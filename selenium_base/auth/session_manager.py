#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
會話管理模組

提供以下功能：
1. 會話狀態管理
2. 會話驗證
3. 會話信息持久化
4. 會話過期處理
5. 會話加密存儲
"""

import json
import os
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, Union, Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .auth_exceptions import SessionError
from ..core.logger import setup_logger
from ..core.utils import Utils

logger = setup_logger(__name__)

class SessionManager:
    """會話管理類"""
    
    def __init__(self, session_file: Optional[str] = None, 
                 encryption_key: Optional[str] = None):
        """
        初始化會話管理器
        
        Args:
            session_file: 會話信息文件路徑，默認為 ~/.datascout/session.json
            encryption_key: 加密密鑰，默認為 None（不加密）
        """
        self.session_file = session_file or os.path.expanduser("~/.datascout/session.json")
        self.sessions: Dict[str, Dict] = {}
        self.encryption_key = encryption_key
        self._fernet = None
        if encryption_key:
            self._setup_encryption(encryption_key)
        self._load_sessions()
        
    def _setup_encryption(self, key: str) -> None:
        """
        設置加密
        
        Args:
            key: 加密密鑰
        """
        try:
            # 使用 PBKDF2 生成密鑰
            salt = b'datascout_session_salt'  # 固定鹽值
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key_bytes = kdf.derive(key.encode())
            self._fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
        except Exception as e:
            logger.error(f"設置加密失敗: {str(e)}")
            self._fernet = None
            
    def _encrypt_data(self, data: str) -> str:
        """
        加密數據
        
        Args:
            data: 待加密的數據
            
        Returns:
            加密後的數據
        """
        if not self._fernet:
            return data
        try:
            return self._fernet.encrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"加密數據失敗: {str(e)}")
            return data
            
    def _decrypt_data(self, data: str) -> str:
        """
        解密數據
        
        Args:
            data: 待解密的數據
            
        Returns:
            解密後的數據
        """
        if not self._fernet:
            return data
        try:
            return self._fernet.decrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"解密數據失敗: {str(e)}")
            return data
        
    def _load_sessions(self) -> None:
        """從文件加載會話信息"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, "r", encoding="utf-8") as f:
                    data = f.read()
                    if self._fernet:
                        data = self._decrypt_data(data)
                    self.sessions = json.loads(data)
                    
                # 清理過期會話
                self._cleanup_expired_sessions()
        except Exception as e:
            raise SessionError(f"加載會話信息失敗: {str(e)}")
            
    def _save_sessions(self) -> None:
        """保存會話信息到文件"""
        try:
            Utils.ensure_dir(os.path.dirname(self.session_file))
            data = json.dumps(self.sessions, indent=2, ensure_ascii=False)
            if self._fernet:
                data = self._encrypt_data(data)
            with open(self.session_file, "w", encoding="utf-8") as f:
                f.write(data)
        except Exception as e:
            raise SessionError(f"保存會話信息失敗: {str(e)}")
            
    def _cleanup_expired_sessions(self) -> None:
        """清理過期會話"""
        now = datetime.now()
        expired_domains = []
        
        for domain, session in self.sessions.items():
            if "expire_time" in session:
                expire_time = datetime.fromisoformat(session["expire_time"])
                if now > expire_time:
                    expired_domains.append(domain)
                    
        for domain in expired_domains:
            logger.info(f"清理過期會話: {domain}")
            del self.sessions[domain]
            
        if expired_domains:
            self._save_sessions()
            
    def create_session(self, domain: str, session_data: Dict[str, Any]) -> None:
        """
        創建新會話
        
        Args:
            domain: 域名
            session_data: 會話數據
        """
        if domain not in self.sessions:
            self.sessions[domain] = {}
            
        # 設置默認過期時間（7天）
        if "expire_time" not in session_data:
            session_data["expire_time"] = (datetime.now() + timedelta(days=7)).isoformat()
            
        self.sessions[domain].update({
            **session_data,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        })
        self._save_sessions()
        logger.info(f"創建會話: {domain}")
        
    def get_session(self, domain: str) -> Dict[str, Any]:
        """
        獲取會話信息
        
        Args:
            domain: 域名
            
        Returns:
            會話信息字典
        """
        if domain not in self.sessions:
            return {}
            
        # 檢查會話是否過期
        session = self.sessions[domain]
        if "expire_time" in session:
            expire_time = datetime.fromisoformat(session["expire_time"])
            if datetime.now() > expire_time:
                logger.info(f"會話已過期: {domain}")
                del self.sessions[domain]
                self._save_sessions()
                return {}
                
        # 更新最後活動時間
        self.refresh_session(domain)
        return session
        
    def update_session(self, domain: str, session_data: Dict[str, Any]) -> None:
        """
        更新會話信息
        
        Args:
            domain: 域名
            session_data: 新的會話數據
        """
        if domain not in self.sessions:
            raise SessionError(f"域名 {domain} 的會話不存在")
            
        # 如果提供了新的過期時間，則更新
        if "expire_time" in session_data:
            try:
                # 驗證日期格式
                datetime.fromisoformat(session_data["expire_time"])
            except ValueError:
                raise SessionError(f"無效的過期時間格式: {session_data['expire_time']}")
                
        self.sessions[domain].update({
            **session_data,
            "last_activity": datetime.now().isoformat()
        })
        self._save_sessions()
        logger.info(f"更新會話: {domain}")
        
    def delete_session(self, domain: str) -> None:
        """
        刪除會話
        
        Args:
            domain: 域名
        """
        if domain in self.sessions:
            del self.sessions[domain]
            self._save_sessions()
            logger.info(f"刪除會話: {domain}")
            
    def clear_sessions(self) -> None:
        """清空所有會話"""
        self.sessions.clear()
        self._save_sessions()
        logger.info("清空所有會話")
        
    def is_session_valid(self, domain: str, max_age: Optional[int] = None) -> bool:
        """
        檢查會話是否有效
        
        Args:
            domain: 域名
            max_age: 最大會話年齡（秒），默認為None（永不過期）
            
        Returns:
            會話是否有效
        """
        if domain not in self.sessions:
            return False
            
        session = self.sessions[domain]
        
        # 檢查過期時間
        if "expire_time" in session:
            expire_time = datetime.fromisoformat(session["expire_time"])
            if datetime.now() > expire_time:
                logger.info(f"會話已過期: {domain}")
                del self.sessions[domain]
                self._save_sessions()
                return False
                
        # 檢查最大年齡
        if max_age is not None:
            last_activity = datetime.fromisoformat(session["last_activity"])
            age = (datetime.now() - last_activity).total_seconds()
            if age > max_age:
                logger.info(f"會話超過最大年齡: {domain}")
                return False
                
        return True
        
    def refresh_session(self, domain: str) -> None:
        """
        刷新會話活動時間
        
        Args:
            domain: 域名
        """
        if domain not in self.sessions:
            raise SessionError(f"域名 {domain} 的會話不存在")
            
        self.sessions[domain]["last_activity"] = datetime.now().isoformat()
        self._save_sessions()
        
    def extend_session(self, domain: str, days: int = 7) -> None:
        """
        延長會話有效期
        
        Args:
            domain: 域名
            days: 延長的天數
        """
        if domain not in self.sessions:
            raise SessionError(f"域名 {domain} 的會話不存在")
            
        if "expire_time" in self.sessions[domain]:
            current_expire = datetime.fromisoformat(self.sessions[domain]["expire_time"])
            new_expire = current_expire + timedelta(days=days)
            self.sessions[domain]["expire_time"] = new_expire.isoformat()
            self._save_sessions()
            logger.info(f"延長會話有效期: {domain}, 新過期時間: {new_expire.isoformat()}")
            
    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        獲取所有有效會話
        
        Returns:
            有效會話字典
        """
        active_sessions = {}
        now = datetime.now()
        
        for domain, session in self.sessions.items():
            if "expire_time" in session:
                expire_time = datetime.fromisoformat(session["expire_time"])
                if now <= expire_time:
                    active_sessions[domain] = session
                    
        return active_sessions 
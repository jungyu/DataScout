#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cookie 管理模組

提供以下功能：
1. Cookie 狀態管理
2. Cookie 驗證
3. Cookie 信息持久化
4. Cookie 過期處理
5. Cookie 加密存儲
"""

import json
import os
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, Union, Any, List

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .auth_exceptions import CookieError
from ..core.logger import setup_logger
from ..core.utils import Utils

logger = setup_logger(__name__)

class CookieManager:
    """Cookie 管理類"""
    
    def __init__(self, cookie_file: Optional[str] = None, 
                 encryption_key: Optional[str] = None):
        """
        初始化 Cookie 管理器
        
        Args:
            cookie_file: Cookie 信息文件路徑，默認為 ~/.datascout/cookies.json
            encryption_key: 加密密鑰，默認為 None（不加密）
        """
        self.cookie_file = cookie_file or os.path.expanduser("~/.datascout/cookies.json")
        self.cookies: Dict[str, Dict] = {}
        self.encryption_key = encryption_key
        self._fernet = None
        if encryption_key:
            self._setup_encryption(encryption_key)
        self._load_cookies()
        
    def _setup_encryption(self, key: str) -> None:
        """
        設置加密
        
        Args:
            key: 加密密鑰
        """
        try:
            # 使用 PBKDF2 生成密鑰
            salt = b'datascout_cookie_salt'  # 固定鹽值
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
        
    def _load_cookies(self) -> None:
        """從文件加載 Cookie 信息"""
        try:
            if os.path.exists(self.cookie_file):
                with open(self.cookie_file, "r", encoding="utf-8") as f:
                    data = f.read()
                    if self._fernet:
                        data = self._decrypt_data(data)
                    self.cookies = json.loads(data)
                    
                # 清理過期 Cookie
                self._cleanup_expired_cookies()
        except Exception as e:
            raise CookieError(f"加載 Cookie 信息失敗: {str(e)}")
            
    def _save_cookies(self) -> None:
        """保存 Cookie 信息到文件"""
        try:
            Utils.ensure_dir(os.path.dirname(self.cookie_file))
            data = json.dumps(self.cookies, indent=2, ensure_ascii=False)
            if self._fernet:
                data = self._encrypt_data(data)
            with open(self.cookie_file, "w", encoding="utf-8") as f:
                f.write(data)
        except Exception as e:
            raise CookieError(f"保存 Cookie 信息失敗: {str(e)}")
            
    def _cleanup_expired_cookies(self) -> None:
        """清理過期 Cookie"""
        now = datetime.now()
        expired_domains = []
        
        for domain, cookies in self.cookies.items():
            for cookie in cookies:
                if "expires" in cookie:
                    expire_time = datetime.fromtimestamp(cookie["expires"])
                    if now > expire_time:
                        expired_domains.append(domain)
                        break
                        
        for domain in expired_domains:
            logger.info(f"清理過期 Cookie: {domain}")
            del self.cookies[domain]
            
        if expired_domains:
            self._save_cookies()
            
    def add_cookies(self, domain: str, cookies: List[Dict[str, Any]]) -> None:
        """
        添加 Cookie
        
        Args:
            domain: 域名
            cookies: Cookie 列表
        """
        if domain not in self.cookies:
            self.cookies[domain] = []
            
        # 更新現有 Cookie
        for cookie in cookies:
            found = False
            for i, existing_cookie in enumerate(self.cookies[domain]):
                if existing_cookie.get("name") == cookie.get("name"):
                    self.cookies[domain][i] = cookie
                    found = True
                    break
            if not found:
                self.cookies[domain].append(cookie)
                
        self._save_cookies()
        logger.info(f"添加 Cookie: {domain}, 數量: {len(cookies)}")
        
    def get_cookies(self, domain: str) -> List[Dict[str, Any]]:
        """
        獲取 Cookie
        
        Args:
            domain: 域名
            
        Returns:
            Cookie 列表
        """
        if domain not in self.cookies:
            return []
            
        # 過濾過期 Cookie
        now = datetime.now()
        valid_cookies = []
        
        for cookie in self.cookies[domain]:
            if "expires" in cookie:
                expire_time = datetime.fromtimestamp(cookie["expires"])
                if now <= expire_time:
                    valid_cookies.append(cookie)
            else:
                valid_cookies.append(cookie)
                
        # 更新 Cookie 列表
        if len(valid_cookies) != len(self.cookies[domain]):
            self.cookies[domain] = valid_cookies
            self._save_cookies()
            
        return valid_cookies
        
    def update_cookies(self, domain: str, cookies: List[Dict[str, Any]]) -> None:
        """
        更新 Cookie
        
        Args:
            domain: 域名
            cookies: 新的 Cookie 列表
        """
        if domain not in self.cookies:
            raise CookieError(f"域名 {domain} 的 Cookie 不存在")
            
        self.cookies[domain] = cookies
        self._save_cookies()
        logger.info(f"更新 Cookie: {domain}, 數量: {len(cookies)}")
        
    def delete_cookies(self, domain: str) -> None:
        """
        刪除 Cookie
        
        Args:
            domain: 域名
        """
        if domain in self.cookies:
            del self.cookies[domain]
            self._save_cookies()
            logger.info(f"刪除 Cookie: {domain}")
            
    def clear_cookies(self) -> None:
        """清空所有 Cookie"""
        self.cookies.clear()
        self._save_cookies()
        logger.info("清空所有 Cookie")
        
    def is_cookie_valid(self, domain: str) -> bool:
        """
        檢查 Cookie 是否有效
        
        Args:
            domain: 域名
            
        Returns:
            Cookie 是否有效
        """
        if domain not in self.cookies:
            return False
            
        # 檢查是否有有效 Cookie
        valid_cookies = self.get_cookies(domain)
        return len(valid_cookies) > 0
        
    def refresh_cookies(self, domain: str) -> None:
        """
        刷新 Cookie
        
        Args:
            domain: 域名
        """
        if domain not in self.cookies:
            raise CookieError(f"域名 {domain} 的 Cookie 不存在")
            
        # 更新 Cookie 時間戳
        now = datetime.now()
        for cookie in self.cookies[domain]:
            if "expires" in cookie:
                # 延長有效期（7天）
                cookie["expires"] = (now + timedelta(days=7)).timestamp()
                
        self._save_cookies()
        logger.info(f"刷新 Cookie: {domain}")
        
    def extend_cookies(self, domain: str, days: int = 7) -> None:
        """
        延長 Cookie 有效期
        
        Args:
            domain: 域名
            days: 延長的天數
        """
        if domain not in self.cookies:
            raise CookieError(f"域名 {domain} 的 Cookie 不存在")
            
        now = datetime.now()
        for cookie in self.cookies[domain]:
            if "expires" in cookie:
                current_expire = datetime.fromtimestamp(cookie["expires"])
                new_expire = current_expire + timedelta(days=days)
                cookie["expires"] = new_expire.timestamp()
                
        self._save_cookies()
        logger.info(f"延長 Cookie 有效期: {domain}, 天數: {days}")
        
    def get_active_cookies(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        獲取所有有效 Cookie
        
        Returns:
            有效 Cookie 字典
        """
        active_cookies = {}
        now = datetime.now()
        
        for domain, cookies in self.cookies.items():
            valid_cookies = []
            for cookie in cookies:
                if "expires" in cookie:
                    expire_time = datetime.fromtimestamp(cookie["expires"])
                    if now <= expire_time:
                        valid_cookies.append(cookie)
                else:
                    valid_cookies.append(cookie)
            if valid_cookies:
                active_cookies[domain] = valid_cookies
                
        return active_cookies 
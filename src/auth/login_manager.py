#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
登入管理模組

提供以下功能：
1. 登入狀態管理
2. 登入驗證
3. 登入信息持久化
4. 登入重試機制
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Union

from .auth_exceptions import LoginError
from ..core.utils.cookie_manager import CookieManager
from .session_manager import SessionManager
from ..core.utils.logger import setup_logger

logger = setup_logger(__name__)

class LoginManager:
    """登入管理類"""
    
    def __init__(self, 
                 cookie_manager: Optional[CookieManager] = None,
                 session_manager: Optional[SessionManager] = None,
                 login_file: Optional[str] = None):
        """
        初始化登入管理器
        
        Args:
            cookie_manager: Cookie管理器實例
            session_manager: 會話管理器實例
            login_file: 登入信息文件路徑，默認為 ~/.datascout/login.json
        """
        self.cookie_manager = cookie_manager or CookieManager()
        self.session_manager = session_manager or SessionManager()
        self.login_file = login_file or os.path.expanduser("~/.datascout/login.json")
        self.login_info: Dict[str, Dict] = {}
        self._load_login_info()
        
    def _load_login_info(self) -> None:
        """從文件加載登入信息"""
        try:
            if os.path.exists(self.login_file):
                with open(self.login_file, "r", encoding="utf-8") as f:
                    self.login_info = json.load(f)
        except Exception as e:
            raise LoginError(f"加載登入信息失敗: {str(e)}")
            
    def _save_login_info(self) -> None:
        """保存登入信息到文件"""
        try:
            os.makedirs(os.path.dirname(self.login_file), exist_ok=True)
            with open(self.login_file, "w", encoding="utf-8") as f:
                json.dump(self.login_info, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise LoginError(f"保存登入信息失敗: {str(e)}")
            
    def add_login(self, domain: str, username: str, password: str) -> None:
        """
        添加登入信息
        
        Args:
            domain: 域名
            username: 用戶名
            password: 密碼
        """
        if domain not in self.login_info:
            self.login_info[domain] = {}
        self.login_info[domain].update({
            "username": username,
            "password": password,
            "last_login": datetime.now().isoformat()
        })
        self._save_login_info()
        
    def get_login(self, domain: str) -> Dict:
        """
        獲取登入信息
        
        Args:
            domain: 域名
            
        Returns:
            登入信息字典
        """
        return self.login_info.get(domain, {})
        
    def update_login(self, domain: str, username: Optional[str] = None, 
                    password: Optional[str] = None) -> None:
        """
        更新登入信息
        
        Args:
            domain: 域名
            username: 新的用戶名
            password: 新的密碼
        """
        if domain not in self.login_info:
            raise LoginError(f"域名 {domain} 的登入信息不存在")
            
        if username:
            self.login_info[domain]["username"] = username
        if password:
            self.login_info[domain]["password"] = password
            
        self.login_info[domain]["last_login"] = datetime.now().isoformat()
        self._save_login_info()
        
    def delete_login(self, domain: str) -> None:
        """
        刪除登入信息
        
        Args:
            domain: 域名
        """
        if domain in self.login_info:
            del self.login_info[domain]
            self._save_login_info()
            
    def clear_login(self) -> None:
        """清空所有登入信息"""
        self.login_info.clear()
        self._save_login_info()
        
    def is_logged_in(self, domain: str) -> bool:
        """
        檢查是否已登入
        
        Args:
            domain: 域名
            
        Returns:
            是否已登入
        """
        if domain not in self.login_info:
            return False
            
        # 檢查Cookie是否有效
        if not self.cookie_manager.is_cookie_valid(domain):
            return False
            
        # 檢查會話是否有效
        if not self.session_manager.is_session_valid(domain):
            return False
            
        return True
        
    def login(self, domain: str, username: str, password: str, 
             max_retries: int = 3) -> bool:
        """
        執行登入操作
        
        Args:
            domain: 域名
            username: 用戶名
            password: 密碼
            max_retries: 最大重試次數
            
        Returns:
            登入是否成功
        """
        retries = 0
        while retries < max_retries:
            try:
                # TODO: 實現具體的登入邏輯
                # 1. 發送登入請求
                # 2. 處理登入響應
                # 3. 保存Cookie和會話信息
                
                # 保存登入信息
                self.add_login(domain, username, password)
                return True
                
            except Exception as e:
                retries += 1
                if retries == max_retries:
                    raise LoginError(f"登入失敗: {str(e)}")
                    
        return False
    
    def logout(self, domain: str) -> None:
        """
        執行登出操作
        
        Args:
            domain: 域名
            
        Raises:
            LoginError: 登出失敗
        """
        try:
            # 清除會話
            self.session_manager.delete_session(domain)
            
            # 清除 Cookie
            self.cookie_manager.delete_cookies(domain)
            
            logger.info(f"已登出 {domain}")
            
        except Exception as e:
            raise LoginError(f"登出失敗: {e}")
    
    def check_login_status(self, domain: str) -> bool:
        """
        檢查登入狀態
        
        Args:
            domain: 域名
            
        Returns:
            是否已登入
        """
        # 檢查會話是否存在且有效
        session = self.session_manager.get_session(domain)
        if not session:
            return False
        
        # 檢查 Cookie 是否存在
        cookies = self.cookie_manager.get_cookies(domain)
        if not cookies:
            return False
        
        return True
    
    def get_login_info(self, domain: str) -> Optional[Dict]:
        """
        獲取登入信息
        
        Args:
            domain: 域名
            
        Returns:
            登入信息字典，如果未登入則返回 None
        """
        if not self.check_login_status(domain):
            return None
            
        session = self.session_manager.get_session(domain)
        if not session:
            return None
            
        return {
            "username": session.get("username"),
            "login_time": session.get("login_time"),
            "domain": session.get("domain")
        } 
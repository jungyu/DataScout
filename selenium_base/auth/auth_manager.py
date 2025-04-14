#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
認證管理模組

提供以下功能：
1. 用戶認證
2. 會話管理
3. 令牌管理
4. 權限控制
5. 認證狀態追蹤
"""

import os
from typing import Dict, Optional, Union, List
from datetime import datetime

from .session_manager import SessionManager
from .login_manager import LoginManager
from .token_manager import TokenManager
from .auth_exceptions import (
    AuthError,
    LoginError,
    SessionError,
    TokenError,
    ValidationError
)
from ..base_manager import BaseManager

class AuthManager(BaseManager):
    """認證管理類"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化認證管理器
        
        Args:
            config_dir: 配置目錄路徑，默認為 ~/.datascout
        """
        super().__init__()
        self.config_dir = config_dir or os.path.expanduser("~/.datascout")
        
        # 初始化子管理器
        self.session_manager = SessionManager()
        self.login_manager = LoginManager()
        self.token_manager = TokenManager()
        
        # 當前認證狀態
        self.current_user: Optional[str] = None
        self.current_session: Optional[Dict] = None
        self.current_tokens: Optional[Dict] = None
        
    def register(self, username: str, password: str, email: str) -> Dict:
        """
        註冊新用戶
        
        Args:
            username: 用戶名
            password: 密碼
            email: 電子郵件
            
        Returns:
            註冊信息字典
        """
        try:
            # 註冊用戶
            self.login_manager.register(username, password, email)
            
            # 生成初始令牌
            tokens = self.token_manager.generate_token_pair(username)
            
            # 創建會話
            session = self.session_manager.create_session(username)
            
            return {
                "username": username,
                "email": email,
                "tokens": tokens,
                "session": session
            }
            
        except Exception as e:
            raise AuthError(f"註冊失敗: {str(e)}")
            
    def login(self, username: str, password: str) -> Dict:
        """
        用戶登錄
        
        Args:
            username: 用戶名
            password: 密碼
            
        Returns:
            登錄信息字典
        """
        try:
            # 驗證登錄
            login_info = self.login_manager.login(username, password)
            
            # 生成令牌
            tokens = self.token_manager.generate_token_pair(username)
            
            # 創建會話
            session = self.session_manager.create_session(username)
            
            # 更新當前狀態
            self.current_user = username
            self.current_session = session
            self.current_tokens = tokens
            
            return {
                "username": username,
                "email": login_info["email"],
                "tokens": tokens,
                "session": session
            }
            
        except Exception as e:
            raise AuthError(f"登錄失敗: {str(e)}")
            
    def logout(self) -> None:
        """用戶登出"""
        try:
            if self.current_user:
                # 撤銷所有令牌
                self.token_manager.revoke_all_tokens(self.current_user)
                
                # 刪除會話
                if self.current_session:
                    self.session_manager.delete_session(self.current_session["id"])
                    
                # 清除當前狀態
                self.current_user = None
                self.current_session = None
                self.current_tokens = None
                
        except Exception as e:
            raise AuthError(f"登出失敗: {str(e)}")
            
    def refresh_auth(self, refresh_token: str) -> Dict:
        """
        刷新認證狀態
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的認證信息
        """
        try:
            # 驗證刷新令牌
            token_info = self.token_manager.verify_token(refresh_token)
            username = token_info["sub"]
            
            # 生成新令牌
            tokens = self.token_manager.generate_token_pair(username)
            
            # 更新會話
            session = self.session_manager.refresh_session(username)
            
            # 更新當前狀態
            self.current_user = username
            self.current_session = session
            self.current_tokens = tokens
            
            return {
                "username": username,
                "tokens": tokens,
                "session": session
            }
            
        except Exception as e:
            raise AuthError(f"刷新認證失敗: {str(e)}")
            
    def verify_auth(self, access_token: str) -> Dict:
        """
        驗證認證狀態
        
        Args:
            access_token: 訪問令牌
            
        Returns:
            認證信息
        """
        try:
            # 驗證令牌
            token_info = self.token_manager.verify_token(access_token)
            username = token_info["sub"]
            
            # 驗證會話
            session = self.session_manager.get_session(username)
            if not session:
                raise AuthError("會話不存在")
                
            return {
                "username": username,
                "session": session,
                "token_info": token_info
            }
            
        except Exception as e:
            raise AuthError(f"驗證認證失敗: {str(e)}")
            
    def change_password(self, old_password: str, new_password: str) -> None:
        """
        修改密碼
        
        Args:
            old_password: 舊密碼
            new_password: 新密碼
        """
        try:
            if not self.current_user:
                raise AuthError("未登錄")
                
            self.login_manager.change_password(
                self.current_user,
                old_password,
                new_password
            )
            
        except Exception as e:
            raise AuthError(f"修改密碼失敗: {str(e)}")
            
    def reset_password(self, username: str, email: str) -> str:
        """
        重置密碼
        
        Args:
            username: 用戶名
            email: 電子郵件
            
        Returns:
            新密碼
        """
        try:
            return self.login_manager.reset_password(username, email)
            
        except Exception as e:
            raise AuthError(f"重置密碼失敗: {str(e)}")
            
    def get_auth_status(self) -> Dict:
        """
        獲取當前認證狀態
        
        Returns:
            認證狀態字典
        """
        return {
            "is_authenticated": bool(self.current_user),
            "username": self.current_user,
            "session": self.current_session,
            "tokens": self.current_tokens
        }
        
    def get_login_history(self) -> List[Dict]:
        """
        獲取登錄歷史
        
        Returns:
            登錄歷史列表
        """
        try:
            if not self.current_user:
                raise AuthError("未登錄")
                
            return self.login_manager.get_login_history(self.current_user)
            
        except Exception as e:
            raise AuthError(f"獲取登錄歷史失敗: {str(e)}")
            
    def get_active_sessions(self) -> List[Dict]:
        """
        獲取活動會話列表
        
        Returns:
            活動會話列表
        """
        try:
            if not self.current_user:
                raise AuthError("未登錄")
                
            return self.session_manager.get_active_sessions(self.current_user)
            
        except Exception as e:
            raise AuthError(f"獲取活動會話失敗: {str(e)}")
            
    def get_active_tokens(self) -> List[Dict]:
        """
        獲取活動令牌列表
        
        Returns:
            活動令牌列表
        """
        try:
            if not self.current_user:
                raise AuthError("未登錄")
                
            return self.token_manager.get_active_tokens(self.current_user)
            
        except Exception as e:
            raise AuthError(f"獲取活動令牌失敗: {str(e)}") 
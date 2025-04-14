#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
令牌管理模組

提供以下功能：
1. 訪問令牌生成
2. 令牌驗證
3. 令牌刷新
4. 令牌撤銷
5. 令牌狀態追蹤
"""

import os
import json
import time
import uuid
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, Union, List
from cryptography.fernet import Fernet

from .auth_exceptions import TokenError, ValidationError
from ..base_manager import BaseManager

class TokenManager(BaseManager):
    """令牌管理類"""
    
    def __init__(self, tokens_file: Optional[str] = None):
        """
        初始化令牌管理器
        
        Args:
            tokens_file: 令牌文件路徑，默認為 ~/.datascout/tokens.json
        """
        super().__init__()
        self.tokens_file = tokens_file or os.path.expanduser("~/.datascout/tokens.json")
        self.tokens: Dict[str, Dict] = {}
        self._load_tokens()
        
    def _load_tokens(self) -> None:
        """從文件加載令牌信息"""
        try:
            if os.path.exists(self.tokens_file):
                with open(self.tokens_file, "r", encoding="utf-8") as f:
                    self.tokens = json.load(f)
        except Exception as e:
            raise TokenError(f"加載令牌信息失敗: {str(e)}")
            
    def _save_tokens(self) -> None:
        """保存令牌信息到文件"""
        try:
            os.makedirs(os.path.dirname(self.tokens_file), exist_ok=True)
            with open(self.tokens_file, "w", encoding="utf-8") as f:
                json.dump(self.tokens, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise TokenError(f"保存令牌信息失敗: {str(e)}")
            
    def _generate_token(self, username: str, token_type: str = "access") -> str:
        """
        生成令牌
        
        Args:
            username: 用戶名
            token_type: 令牌類型（access/refresh）
            
        Returns:
            生成的令牌
        """
        token_id = str(uuid.uuid4())
        timestamp = int(time.time())
        payload = {
            "sub": username,
            "type": token_type,
            "iat": timestamp,
            "exp": timestamp + (3600 if token_type == "access" else 604800),  # 1小時/7天
            "jti": token_id
        }
        
        # 使用Fernet進行加密
        key = Fernet.generate_key()
        f = Fernet(key)
        token = f.encrypt(json.dumps(payload).encode())
        
        # 保存令牌信息
        self.tokens[token_id] = {
            "username": username,
            "type": token_type,
            "created_at": datetime.now().isoformat(),
            "expires_at": datetime.fromtimestamp(payload["exp"]).isoformat(),
            "is_revoked": False
        }
        self._save_tokens()
        
        return base64.b64encode(token).decode('utf-8')
        
    def generate_token_pair(self, username: str) -> Dict[str, str]:
        """
        生成訪問令牌和刷新令牌對
        
        Args:
            username: 用戶名
            
        Returns:
            包含access_token和refresh_token的字典
        """
        access_token = self._generate_token(username, "access")
        refresh_token = self._generate_token(username, "refresh")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        
    def verify_token(self, token: str) -> Dict:
        """
        驗證令牌
        
        Args:
            token: 待驗證的令牌
            
        Returns:
            令牌中的信息
        """
        try:
            # 解碼令牌
            token_data = base64.b64decode(token.encode('utf-8'))
            f = Fernet(Fernet.generate_key())  # TODO: 使用實際的密鑰
            payload = json.loads(f.decrypt(token_data))
            
            # 檢查令牌是否存在且未被撤銷
            token_id = payload.get("jti")
            if not token_id or token_id not in self.tokens:
                raise TokenError("無效的令牌")
                
            token_info = self.tokens[token_id]
            if token_info["is_revoked"]:
                raise TokenError("令牌已被撤銷")
                
            # 檢查令牌是否過期
            if time.time() > payload["exp"]:
                raise TokenError("令牌已過期")
                
            return payload
            
        except Exception as e:
            raise TokenError(f"令牌驗證失敗: {str(e)}")
            
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        使用刷新令牌獲取新的訪問令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的訪問令牌
        """
        try:
            # 驗證刷新令牌
            payload = self.verify_token(refresh_token)
            if payload["type"] != "refresh":
                raise TokenError("無效的刷新令牌")
                
            # 生成新的訪問令牌
            return self.generate_token_pair(payload["sub"])
            
        except Exception as e:
            raise TokenError(f"刷新令牌失敗: {str(e)}")
            
    def revoke_token(self, token: str) -> None:
        """
        撤銷令牌
        
        Args:
            token: 待撤銷的令牌
        """
        try:
            payload = self.verify_token(token)
            token_id = payload["jti"]
            
            # 標記令牌為已撤銷
            self.tokens[token_id]["is_revoked"] = True
            self._save_tokens()
            
        except Exception as e:
            raise TokenError(f"撤銷令牌失敗: {str(e)}")
            
    def revoke_all_tokens(self, username: str) -> None:
        """
        撤銷用戶的所有令牌
        
        Args:
            username: 用戶名
        """
        try:
            for token_id, token_info in self.tokens.items():
                if token_info["username"] == username:
                    token_info["is_revoked"] = True
            self._save_tokens()
            
        except Exception as e:
            raise TokenError(f"撤銷所有令牌失敗: {str(e)}")
            
    def get_active_tokens(self, username: str) -> List[Dict]:
        """
        獲取用戶的活動令牌列表
        
        Args:
            username: 用戶名
            
        Returns:
            活動令牌列表
        """
        active_tokens = []
        for token_id, token_info in self.tokens.items():
            if (token_info["username"] == username and 
                not token_info["is_revoked"] and 
                datetime.fromisoformat(token_info["expires_at"]) > datetime.now()):
                active_tokens.append({
                    "token_id": token_id,
                    "type": token_info["type"],
                    "created_at": token_info["created_at"],
                    "expires_at": token_info["expires_at"]
                })
        return active_tokens 
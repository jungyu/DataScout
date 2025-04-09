#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API 配置模組

提供 API 相關的配置類型和配置管理功能。
包括：
1. API 類型定義
2. 認證類型定義
3. API 配置類
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


class APIType(Enum):
    """API 類型"""
    REST = "rest"
    WEBHOOK = "webhook"
    N8N = "n8n"
    MAKE = "make"
    ZAPIER = "zapier"
    IFTTT = "ifttt"
    CUSTOM = "custom"
    AUTOMATION = "automation"


class AuthType(Enum):
    """認證類型"""
    NONE = "none"
    API_KEY = "api_key"
    OAUTH = "oauth"
    BASIC = "basic"
    JWT = "jwt"
    CUSTOM = "custom"


@dataclass
class APIConfig:
    """API 配置"""
    api_type: APIType
    base_url: str
    auth_type: AuthType = AuthType.NONE
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_count: int = 3
    retry_delay: int = 1
    user_agent: str = "Crawler/1.0"
    options: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """驗證配置是否有效"""
        if not self.base_url:
            return False
        
        if self.auth_type == AuthType.API_KEY and not self.api_key:
            return False
        
        if self.auth_type == AuthType.BASIC and (not self.username or not self.password):
            return False
        
        return True

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "api_type": self.api_type.value,
            "base_url": self.base_url,
            "auth_type": self.auth_type.value,
            "api_key": self.api_key,
            "username": self.username,
            "password": self.password,
            "headers": self.headers,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay,
            "user_agent": self.user_agent,
            "options": self.options
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIConfig':
        """從字典創建配置"""
        return cls(
            api_type=APIType(data.get("api_type", "rest")),
            base_url=data.get("base_url", ""),
            auth_type=AuthType(data.get("auth_type", "none")),
            api_key=data.get("api_key"),
            username=data.get("username"),
            password=data.get("password"),
            headers=data.get("headers", {}),
            timeout=int(data.get("timeout", 30)),
            retry_count=int(data.get("retry_count", 3)),
            retry_delay=int(data.get("retry_delay", 1)),
            user_agent=data.get("user_agent", "Crawler/1.0"),
            options=data.get("options", {})
        ) 
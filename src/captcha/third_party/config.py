#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
第三方驗證碼服務配置模組

提供第三方驗證碼服務的配置管理。
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class ThirdPartyServiceConfig:
    """第三方驗證服務配置"""
    type: str  # 服務類型，如 "2captcha"
    api_key: str  # API金鑰
    site_key: Optional[str] = None  # 網站金鑰（用於reCAPTCHA/hCaptcha）
    url: Optional[str] = None  # 目標網頁URL
    options: Optional[Dict[str, Any]] = None  # 其他選項
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ThirdPartyServiceConfig":
        """從字典創建配置"""
        return cls(
            type=data.get("type", ""),
            api_key=data.get("api_key", ""),
            site_key=data.get("site_key"),
            url=data.get("url"),
            options=data.get("options", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "type": self.type,
            "api_key": self.api_key,
            "site_key": self.site_key,
            "url": self.url,
            "options": self.options or {}
        }
    
    def validate(self) -> bool:
        """驗證配置是否有效"""
        if not self.type or not self.api_key:
            return False
        
        # 驗證特定類型的配置
        if self.type == "2captcha":
            return bool(self.api_key)
        elif self.type == "anti_captcha":
            return bool(self.api_key)
        elif self.type == "death_by_captcha":
            return bool(self.api_key)
        
        return True 
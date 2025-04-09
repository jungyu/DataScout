#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用戶代理配置類

此模組提供用戶代理配置的定義和管理，包括：
1. 用戶代理配置驗證
2. 用戶代理狀態管理
3. 用戶代理性能統計
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ..base_config import BaseConfig

@dataclass
class UserAgentConfig(BaseConfig):
    """用戶代理配置類"""
    
    # 用戶代理設置
    browser: str
    version: str
    platform: str
    device: str
    language: str = "en-US"
    
    # 性能指標
    success_rate: float = 0.0
    last_check: Optional[datetime] = None
    
    def validate(self) -> bool:
        """驗證用戶代理配置"""
        try:
            # 檢查必要字段
            if not all([self.browser, self.version, self.platform, self.device]):
                return False
            
            # 檢查瀏覽器類型
            if self.browser not in ["Chrome", "Firefox", "Safari", "Edge"]:
                return False
            
            # 檢查平台
            if self.platform not in ["Windows", "MacOS", "Linux", "Android", "iOS"]:
                return False
            
            return True
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        data = super().to_dict()
        data.update({
            'browser': self.browser,
            'version': self.version,
            'platform': self.platform,
            'device': self.device,
            'language': self.language,
            'success_rate': self.success_rate,
            'last_check': self.last_check.isoformat() if self.last_check else None
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserAgentConfig':
        """從字典創建配置"""
        config = super().from_dict(data)
        return cls(
            id=config.id,
            browser=data['browser'],
            version=data['version'],
            platform=data['platform'],
            device=data['device'],
            language=data.get('language', 'en-US'),
            success_rate=data.get('success_rate', 0.0),
            last_check=datetime.fromisoformat(data['last_check']) if data.get('last_check') else None,
            created_at=config.created_at,
            updated_at=config.updated_at,
            total_uses=config.total_uses,
            success_count=config.success_count,
            failure_count=config.failure_count,
            last_used=config.last_used,
            last_success=config.last_success,
            last_failure=config.last_failure,
            metadata=config.metadata
        )
    
    @property
    def user_agent_string(self) -> str:
        """獲取用戶代理字符串"""
        if self.browser == "Chrome":
            return f"Mozilla/5.0 ({self.platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.version} Safari/537.36"
        elif self.browser == "Firefox":
            return f"Mozilla/5.0 ({self.platform}; rv:{self.version}) Gecko/20100101 Firefox/{self.version}"
        elif self.browser == "Safari":
            return f"Mozilla/5.0 ({self.platform}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{self.version} Safari/605.1.15"
        elif self.browser == "Edge":
            return f"Mozilla/5.0 ({self.platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.version} Safari/537.36 Edg/{self.version}"
        else:
            return f"Mozilla/5.0 ({self.platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.version} Safari/537.36"
    
    def update_performance(self, success: bool):
        """更新性能指標"""
        self.last_check = datetime.now()
        self.update_stats(success) 
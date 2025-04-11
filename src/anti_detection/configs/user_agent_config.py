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
class UserAgentConfig:
    """用戶代理配置類"""
    
    # 基本屬性（必需參數）
    id: str
    browser: str
    version: str
    platform: str
    device: str
    
    # 基本屬性（可選參數）
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 統計信息
    total_uses: int = 0
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    
    # 用戶代理設置（可選參數）
    language: str = "en-US"
    success_rate: float = 0.0
    last_check: Optional[datetime] = None
    
    # 元數據
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化後的處理"""
        self.base_config = BaseConfig(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            total_uses=self.total_uses,
            success_count=self.success_count,
            failure_count=self.failure_count,
            last_used=self.last_used,
            last_success=self.last_success,
            last_failure=self.last_failure,
            metadata=self.metadata
        )
    
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
        data = self.base_config.to_dict()
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
        base_config = BaseConfig.from_dict(data)
        return cls(
            id=base_config.id,
            browser=data['browser'],
            version=data['version'],
            platform=data['platform'],
            device=data['device'],
            language=data.get('language', 'en-US'),
            success_rate=data.get('success_rate', 0.0),
            last_check=datetime.fromisoformat(data['last_check']) if data.get('last_check') else None,
            created_at=base_config.created_at,
            updated_at=base_config.updated_at,
            total_uses=base_config.total_uses,
            success_count=base_config.success_count,
            failure_count=base_config.failure_count,
            last_used=base_config.last_used,
            last_success=base_config.last_success,
            last_failure=base_config.last_failure,
            metadata=base_config.metadata
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
        self.base_config.update_stats(success)
        self.total_uses = self.base_config.total_uses
        self.success_count = self.base_config.success_count
        self.failure_count = self.base_config.failure_count
        self.last_used = self.base_config.last_used
        self.last_success = self.base_config.last_success
        self.last_failure = self.base_config.last_failure 
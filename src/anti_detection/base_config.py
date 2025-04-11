#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
反爬蟲基礎配置模組

提供反爬蟲相關的基礎配置類，繼承自 core.config_loader.BaseConfig
"""

from typing import Dict, Any, Optional
from src.core.config_loader import BaseConfig


class AntiDetectionConfig(BaseConfig):
    """反爬蟲基礎配置類"""
    
    def __init__(self, id: str, **kwargs):
        """
        初始化反爬蟲配置
        
        Args:
            id: 配置ID
            **kwargs: 其他配置參數
        """
        super().__init__(id=id)
        
        # 基本設置
        self.enabled: bool = kwargs.get('enabled', True)
        self.max_retries: int = kwargs.get('max_retries', 3)
        self.retry_delay: float = kwargs.get('retry_delay', 1.0)
        
        # 瀏覽器指紋設置
        self.browser_fingerprint: Dict[str, Any] = kwargs.get('browser_fingerprint', {})
        self.user_agent: Optional[str] = kwargs.get('user_agent')
        self.platform: Optional[str] = kwargs.get('platform')
        self.language: Optional[str] = kwargs.get('language')
        
        # 行為模擬設置
        self.human_behavior: Dict[str, Any] = kwargs.get('human_behavior', {})
        self.mouse_movement: bool = kwargs.get('mouse_movement', True)
        self.keyboard_input: bool = kwargs.get('keyboard_input', True)
        self.scroll_behavior: bool = kwargs.get('scroll_behavior', True)
        
        # 代理設置
        self.proxy: Dict[str, Any] = kwargs.get('proxy', {})
        self.proxy_enabled: bool = kwargs.get('proxy_enabled', False)
        self.proxy_rotation: bool = kwargs.get('proxy_rotation', False)
        
        # 請求設置
        self.request_headers: Dict[str, str] = kwargs.get('request_headers', {})
        self.request_cookies: Dict[str, str] = kwargs.get('request_cookies', {})
        self.request_timeout: float = kwargs.get('request_timeout', 30.0)
        
        # 更新元數據
        self.metadata.update({
            'type': 'anti_detection',
            'version': '1.0.0'
        })
    
    def validate(self) -> bool:
        """
        驗證配置是否有效
        
        Returns:
            bool: 配置是否有效
        """
        try:
            # 基本參數驗證
            if not isinstance(self.max_retries, int) or self.max_retries < 0:
                return False
            if not isinstance(self.retry_delay, (int, float)) or self.retry_delay < 0:
                return False
            if not isinstance(self.request_timeout, (int, float)) or self.request_timeout < 0:
                return False
            
            # 代理設置驗證
            if self.proxy_enabled:
                if not isinstance(self.proxy, dict):
                    return False
                required_keys = ['host', 'port']
                if not all(key in self.proxy for key in required_keys):
                    return False
            
            # 請求頭驗證
            if not isinstance(self.request_headers, dict):
                return False
            if not isinstance(self.request_cookies, dict):
                return False
            
            return True
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        轉換為字典格式
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        config_dict = super().to_dict()
        config_dict.update({
            'enabled': self.enabled,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'browser_fingerprint': self.browser_fingerprint,
            'user_agent': self.user_agent,
            'platform': self.platform,
            'language': self.language,
            'human_behavior': self.human_behavior,
            'mouse_movement': self.mouse_movement,
            'keyboard_input': self.keyboard_input,
            'scroll_behavior': self.scroll_behavior,
            'proxy': self.proxy,
            'proxy_enabled': self.proxy_enabled,
            'proxy_rotation': self.proxy_rotation,
            'request_headers': self.request_headers,
            'request_cookies': self.request_cookies,
            'request_timeout': self.request_timeout
        })
        return config_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AntiDetectionConfig':
        """
        從字典創建配置
        
        Args:
            data: 配置字典
            
        Returns:
            AntiDetectionConfig: 配置實例
        """
        base_config = super().from_dict(data)
        config = cls(id=base_config.id)
        
        # 更新基本屬性
        config.created_at = base_config.created_at
        config.updated_at = base_config.updated_at
        config.total_uses = base_config.total_uses
        config.success_count = base_config.success_count
        config.failure_count = base_config.failure_count
        config.last_used = base_config.last_used
        config.last_success = base_config.last_success
        config.last_failure = base_config.last_failure
        config.metadata = base_config.metadata
        
        # 更新配置屬性
        config.enabled = data.get('enabled', True)
        config.max_retries = data.get('max_retries', 3)
        config.retry_delay = data.get('retry_delay', 1.0)
        config.browser_fingerprint = data.get('browser_fingerprint', {})
        config.user_agent = data.get('user_agent')
        config.platform = data.get('platform')
        config.language = data.get('language')
        config.human_behavior = data.get('human_behavior', {})
        config.mouse_movement = data.get('mouse_movement', True)
        config.keyboard_input = data.get('keyboard_input', True)
        config.scroll_behavior = data.get('scroll_behavior', True)
        config.proxy = data.get('proxy', {})
        config.proxy_enabled = data.get('proxy_enabled', False)
        config.proxy_rotation = data.get('proxy_rotation', False)
        config.request_headers = data.get('request_headers', {})
        config.request_cookies = data.get('request_cookies', {})
        config.request_timeout = data.get('request_timeout', 30.0)
        
        return config 
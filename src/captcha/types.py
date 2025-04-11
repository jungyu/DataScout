#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼類型定義模組

提供驗證碼相關的類型定義。
包括：
1. 驗證碼類型枚舉
2. 驗證碼配置類
3. 驗證碼結果類
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

# 從 src.core.utils 導入工具類
from src.core.utils import (
    ConfigUtils,
    Logger,
    PathUtils,
    DataProcessor
)

from src.core.config_loader import BaseConfig


class CaptchaType(Enum):
    """驗證碼類型枚舉"""
    SLIDER = "slider"      # 滑塊驗證碼
    IMAGE = "image"        # 圖片驗證碼
    CLICK = "click"        # 點擊驗證碼
    AUDIO = "audio"        # 音頻驗證碼
    TEXT = "text"          # 文本驗證碼
    RECAPTCHA = "recaptcha"  # Google reCAPTCHA
    HCAPTCHA = "hcaptcha"    # hCaptcha
    MANUAL = "manual"        # 人工手動驗證
    CUSTOM = "custom"        # 自定義驗證函式
    UNKNOWN = "unknown"      # 未知類型


@dataclass
class CaptchaConfig(BaseConfig):
    """驗證碼配置類"""
    
    def __init__(self, id: str, **kwargs):
        """
        初始化驗證碼配置
        
        Args:
            id: 配置ID
            **kwargs: 其他配置參數
        """
        super().__init__(id=id)
        
        # 基本設置
        self.enabled: bool = kwargs.get('enabled', True)
        self.max_retries: int = kwargs.get('max_retries', 3)
        self.retry_delay: float = kwargs.get('retry_delay', 1.0)
        self.timeout: float = kwargs.get('timeout', 30.0)
        
        # 驗證碼類型設置
        self.captcha_type: CaptchaType = kwargs.get('captcha_type', CaptchaType.IMAGE)
        self.captcha_source: str = kwargs.get('captcha_source', 'local')
        
        # 圖像驗證碼設置
        self.image_config: Dict[str, Any] = kwargs.get('image_config', {})
        self.image_preprocessing: bool = kwargs.get('image_preprocessing', True)
        self.image_threshold: int = kwargs.get('image_threshold', 127)
        
        # 音頻驗證碼設置
        self.audio_config: Dict[str, Any] = kwargs.get('audio_config', {})
        self.audio_preprocessing: bool = kwargs.get('audio_preprocessing', True)
        self.audio_sample_rate: int = kwargs.get('audio_sample_rate', 16000)
        
        # 文本驗證碼設置
        self.text_config: Dict[str, Any] = kwargs.get('text_config', {})
        self.text_preprocessing: bool = kwargs.get('text_preprocessing', True)
        self.text_min_length: int = kwargs.get('text_min_length', 4)
        
        # 滑塊驗證碼設置
        self.slider_config: Dict[str, Any] = kwargs.get('slider_config', {})
        self.slider_move_delay: float = kwargs.get('slider_move_delay', 0.1)
        self.slider_move_offset: int = kwargs.get('slider_move_offset', 5)
        
        # API設置
        self.api_config: Dict[str, Any] = kwargs.get('api_config', {})
        self.api_key: Optional[str] = kwargs.get('api_key')
        self.api_endpoint: Optional[str] = kwargs.get('api_endpoint')
        self.api_timeout: float = kwargs.get('api_timeout', 30.0)
        
        # 更新元數據
        self.metadata.update({
            'type': 'captcha',
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
            
            # 驗證碼類型驗證
            if self.captcha_type not in ['image', 'audio', 'text']:
                return False
            if self.captcha_source not in ['local', 'api']:
                return False
            
            # API設置驗證
            if self.captcha_source == 'api':
                if not self.api_key or not self.api_endpoint:
                    return False
                if not isinstance(self.api_timeout, (int, float)) or self.api_timeout < 0:
                    return False
            
            # 圖像設置驗證
            if self.captcha_type == 'image':
                if not isinstance(self.image_threshold, int) or self.image_threshold < 0:
                    return False
            
            # 音頻設置驗證
            if self.captcha_type == 'audio':
                if not isinstance(self.audio_sample_rate, int) or self.audio_sample_rate < 0:
                    return False
            
            # 文本設置驗證
            if self.captcha_type == 'text':
                if not isinstance(self.text_min_length, int) or self.text_min_length < 0:
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
            'timeout': self.timeout,
            'captcha_type': self.captcha_type,
            'captcha_source': self.captcha_source,
            'image_config': self.image_config,
            'image_preprocessing': self.image_preprocessing,
            'image_threshold': self.image_threshold,
            'audio_config': self.audio_config,
            'audio_preprocessing': self.audio_preprocessing,
            'audio_sample_rate': self.audio_sample_rate,
            'text_config': self.text_config,
            'text_preprocessing': self.text_preprocessing,
            'text_min_length': self.text_min_length,
            'slider_config': self.slider_config,
            'slider_move_delay': self.slider_move_delay,
            'slider_move_offset': self.slider_move_offset,
            'api_config': self.api_config,
            'api_key': self.api_key,
            'api_endpoint': self.api_endpoint,
            'api_timeout': self.api_timeout
        })
        return config_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CaptchaConfig':
        """
        從字典創建配置
        
        Args:
            data: 配置字典
            
        Returns:
            CaptchaConfig: 配置實例
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
        config.timeout = data.get('timeout', 30.0)
        config.captcha_type = data.get('captcha_type', CaptchaType.IMAGE)
        config.captcha_type = data.get('captcha_type', 'image')
        config.captcha_source = data.get('captcha_source', 'local')
        config.image_config = data.get('image_config', {})
        config.image_preprocessing = data.get('image_preprocessing', True)
        config.image_threshold = data.get('image_threshold', 127)
        config.audio_config = data.get('audio_config', {})
        config.audio_preprocessing = data.get('audio_preprocessing', True)
        config.audio_sample_rate = data.get('audio_sample_rate', 16000)
        config.text_config = data.get('text_config', {})
        config.text_preprocessing = data.get('text_preprocessing', True)
        config.text_min_length = data.get('text_min_length', 4)
        config.api_config = data.get('api_config', {})
        config.api_key = data.get('api_key')
        config.api_endpoint = data.get('api_endpoint')
        config.api_timeout = data.get('api_timeout', 30.0)
        
        return config


@dataclass
class CaptchaResult:
    """驗證碼結果類"""
    success: bool                                  # 是否成功
    captcha_type: CaptchaType                     # 驗證碼類型
    solution: Optional[str] = None                 # 解決方案
    confidence: float = 0.0                        # 可信度
    error: Optional[str] = None                    # 錯誤信息
    details: Dict[str, Any] = field(default_factory=dict)  # 詳細信息 
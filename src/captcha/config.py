#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼配置模組

提供驗證碼處理的配置類和相關設置。
包括：
1. 驗證碼類型配置
2. 第三方服務配置
3. 處理器配置
4. 通用設置
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum, auto


class CaptchaType(Enum):
    """驗證碼類型枚舉"""
    NONE = auto()
    IMAGE = auto()
    AUDIO = auto()
    RECAPTCHA = auto()
    HCAPTCHA = auto()
    SLIDER = auto()
    ROTATE = auto()
    CLICK = auto()
    TEXT = auto()
    MANUAL = auto()
    UNKNOWN = auto()


@dataclass
class ThirdPartyServiceConfig:
    """第三方服務配置"""
    name: str
    api_key: str
    api_url: str
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImageCaptchaConfig:
    """圖像驗證碼配置"""
    enabled: bool = True
    min_confidence: float = 0.8
    max_attempts: int = 3
    timeout: int = 10
    preprocess: bool = True
    ocr_enabled: bool = True
    ocr_language: str = "eng"
    ocr_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AudioCaptchaConfig:
    """音頻驗證碼配置"""
    enabled: bool = True
    min_confidence: float = 0.8
    max_attempts: int = 3
    timeout: int = 10
    preprocess: bool = True
    speech_recognition_enabled: bool = True
    speech_recognition_language: str = "en-US"
    speech_recognition_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecaptchaConfig:
    """reCAPTCHA 配置"""
    enabled: bool = True
    site_key: Optional[str] = None
    secret_key: Optional[str] = None
    proxy: Optional[str] = None
    timeout: int = 30
    max_attempts: int = 3


@dataclass
class HCaptchaConfig:
    """hCaptcha 配置"""
    enabled: bool = True
    site_key: Optional[str] = None
    secret_key: Optional[str] = None
    proxy: Optional[str] = None
    timeout: int = 30
    max_attempts: int = 3


@dataclass
class SliderCaptchaConfig:
    """滑塊驗證碼配置"""
    enabled: bool = True
    min_distance: int = 10
    max_distance: int = 300
    move_duration: float = 0.5
    move_steps: int = 10
    max_attempts: int = 3
    timeout: int = 10


@dataclass
class RotateCaptchaConfig:
    """旋轉驗證碼配置"""
    enabled: bool = True
    min_angle: int = -180
    max_angle: int = 180
    angle_step: int = 5
    max_attempts: int = 3
    timeout: int = 10


@dataclass
class ClickCaptchaConfig:
    """點擊驗證碼配置"""
    enabled: bool = True
    max_attempts: int = 3
    timeout: int = 10
    click_delay: float = 0.5


@dataclass
class TextCaptchaConfig:
    """文字驗證碼配置"""
    enabled: bool = True
    min_length: int = 4
    max_length: int = 8
    allowed_chars: str = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    max_attempts: int = 3
    timeout: int = 10


@dataclass
class ManualCaptchaConfig:
    """手動驗證碼配置"""
    enabled: bool = True
    timeout: int = 300
    max_attempts: int = 3
    notification_enabled: bool = True
    notification_method: str = "console"  # console, email, webhook
    notification_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CaptchaConfig:
    """驗證碼配置"""
    # 基本設置
    debug: bool = False
    log_level: str = "INFO"
    log_file: Optional[str] = None
    screenshot_dir: str = "captcha_screenshots"
    max_retries: int = 3
    retry_delay: int = 1
    
    # 驗證碼類型配置
    captcha_types: List[CaptchaType] = field(default_factory=lambda: [
        CaptchaType.IMAGE,
        CaptchaType.AUDIO,
        CaptchaType.RECAPTCHA,
        CaptchaType.HCAPTCHA,
        CaptchaType.SLIDER,
        CaptchaType.ROTATE,
        CaptchaType.CLICK,
        CaptchaType.TEXT,
        CaptchaType.MANUAL
    ])
    
    # 第三方服務配置
    third_party_service: Optional[ThirdPartyServiceConfig] = None
    
    # 各類型驗證碼配置
    image_config: ImageCaptchaConfig = field(default_factory=ImageCaptchaConfig)
    audio_config: AudioCaptchaConfig = field(default_factory=AudioCaptchaConfig)
    recaptcha_config: RecaptchaConfig = field(default_factory=RecaptchaConfig)
    hcaptcha_config: HCaptchaConfig = field(default_factory=HCaptchaConfig)
    slider_config: SliderCaptchaConfig = field(default_factory=SliderCaptchaConfig)
    rotate_config: RotateCaptchaConfig = field(default_factory=RotateCaptchaConfig)
    click_config: ClickCaptchaConfig = field(default_factory=ClickCaptchaConfig)
    text_config: TextCaptchaConfig = field(default_factory=TextCaptchaConfig)
    manual_config: ManualCaptchaConfig = field(default_factory=ManualCaptchaConfig)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'CaptchaConfig':
        """
        從字典創建配置
        
        Args:
            config_dict: 配置字典
            
        Returns:
            配置對象
        """
        # 處理第三方服務配置
        if "third_party_service" in config_dict:
            service_config = config_dict.pop("third_party_service")
            config_dict["third_party_service"] = ThirdPartyServiceConfig(**service_config)
        
        # 處理各類型驗證碼配置
        for config_name in [
            "image_config", "audio_config", "recaptcha_config",
            "hcaptcha_config", "slider_config", "rotate_config",
            "click_config", "text_config", "manual_config"
        ]:
            if config_name in config_dict:
                config_class = globals()[config_name.replace("_config", "Config")]
                config_dict[config_name] = config_class(**config_dict[config_name])
        
        # 處理驗證碼類型
        if "captcha_types" in config_dict:
            config_dict["captcha_types"] = [
                CaptchaType[type_name.upper()]
                for type_name in config_dict["captcha_types"]
            ]
        
        return cls(**config_dict)
    
    @classmethod
    def from_file(cls, config_file: Union[str, Path]) -> 'CaptchaConfig':
        """
        從文件加載配置
        
        Args:
            config_file: 配置文件路徑
            
        Returns:
            配置對象
        """
        config_file = Path(config_file)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        with open(config_file, "r", encoding="utf-8") as f:
            config_dict = json.load(f)
        
        return cls.from_dict(config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        轉換為字典
        
        Returns:
            配置字典
        """
        config_dict = {
            "debug": self.debug,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "screenshot_dir": self.screenshot_dir,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "captcha_types": [t.name.lower() for t in self.captcha_types]
        }
        
        # 添加第三方服務配置
        if self.third_party_service:
            config_dict["third_party_service"] = {
                "name": self.third_party_service.name,
                "api_key": self.third_party_service.api_key,
                "api_url": self.third_party_service.api_url,
                "timeout": self.third_party_service.timeout,
                "max_retries": self.third_party_service.max_retries,
                "retry_delay": self.third_party_service.retry_delay,
                "additional_params": self.third_party_service.additional_params
            }
        
        # 添加各類型驗證碼配置
        for config_name in [
            "image_config", "audio_config", "recaptcha_config",
            "hcaptcha_config", "slider_config", "rotate_config",
            "click_config", "text_config", "manual_config"
        ]:
            config_dict[config_name] = getattr(self, config_name).__dict__
        
        return config_dict
    
    def save_to_file(self, config_file: Union[str, Path]) -> None:
        """
        保存配置到文件
        
        Args:
            config_file: 配置文件路徑
        """
        config_file = Path(config_file)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
    
    def validate(self) -> bool:
        """
        驗證配置是否有效
        
        Returns:
            是否有效
        """
        try:
            # 驗證基本設置
            if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                return False
            
            if self.log_file and not Path(self.log_file).parent.exists():
                return False
            
            if not Path(self.screenshot_dir).parent.exists():
                return False
            
            # 驗證第三方服務配置
            if self.third_party_service:
                if not self.third_party_service.name:
                    return False
                if not self.third_party_service.api_key:
                    return False
                if not self.third_party_service.api_url:
                    return False
            
            # 驗證各類型驗證碼配置
            for config_name in [
                "image_config", "audio_config", "recaptcha_config",
                "hcaptcha_config", "slider_config", "rotate_config",
                "click_config", "text_config", "manual_config"
            ]:
                config = getattr(self, config_name)
                if not isinstance(config, (ImageCaptchaConfig, AudioCaptchaConfig,
                                        RecaptchaConfig, HCaptchaConfig,
                                        SliderCaptchaConfig, RotateCaptchaConfig,
                                        ClickCaptchaConfig, TextCaptchaConfig,
                                        ManualCaptchaConfig)):
                    return False
            
            return True
        
        except Exception:
            return False 
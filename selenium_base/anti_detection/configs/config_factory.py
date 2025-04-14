"""
反檢測配置工廠模組

此模組提供反檢測配置的工廠類，用於生成不同類型的配置：
- 默認配置
- 高性能配置
- 高隱私配置
- 自定義配置
"""

import os
import json
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

from .anti_detection_config import AntiDetectionConfig


class ConfigFactory:
    """反檢測配置工廠
    
    用於生成不同類型的反檢測配置。
    
    Attributes:
        config_dir (str): 配置文件目錄
        default_config_path (str): 默認配置文件路徑
    """
    
    def __init__(self, config_dir: str = "configs"):
        """初始化配置工廠
        
        Args:
            config_dir: 配置文件目錄
        """
        self.config_dir = config_dir
        self.default_config_path = os.path.join(config_dir, "default_config.json")
    
    def create_default_config(self) -> AntiDetectionConfig:
        """創建默認配置
        
        Returns:
            AntiDetectionConfig: 默認配置對象
        """
        return AntiDetectionConfig(
            id="default",
            version="1.0.0",
            description="默認反檢測配置",
            enabled=True,
            headless=False,
            window_size={"width": 1920, "height": 1080},
            page_load_timeout=30,
            script_timeout=30,
            use_proxy=False,
            proxies=[],
            use_random_user_agent=True,
            user_agents=[
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15"
            ],
            browser_fingerprint={
                "platform": "Win32",
                "webgl_vendor": "Google Inc. (NVIDIA)",
                "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)",
                "language": "zh-CN",
                "timezone": "Asia/Shanghai",
                "screen_resolution": "1920x1080",
                "color_depth": 24,
                "pixel_ratio": 1
            },
            anti_fingerprint={
                "enable_webgl_noise": True,
                "enable_canvas_noise": True,
                "enable_audio_noise": True,
                "enable_font_noise": True,
                "enable_webgl_vendor_spoof": True,
                "enable_webgl_renderer_spoof": True,
                "enable_platform_spoof": True,
                "enable_language_spoof": True,
                "enable_timezone_spoof": True,
                "enable_screen_spoof": True,
                "enable_color_depth_spoof": True,
                "enable_pixel_ratio_spoof": True
            },
            delay_config={
                "min_delay": 1,
                "max_delay": 5,
                "random_delay": True,
                "mouse_movement_delay": True,
                "typing_delay": True,
                "scroll_delay": True,
                "click_delay": True
            },
            max_retries=3,
            retry_delay=5,
            detection_threshold=0.8,
            block_threshold=0.9,
            use_cache=True,
            cache_duration=3600,
            max_cache_size=1000
        )
    
    def create_high_performance_config(self) -> AntiDetectionConfig:
        """創建高性能配置
        
        Returns:
            AntiDetectionConfig: 高性能配置對象
        """
        config = self.create_default_config()
        config.id = "high_performance"
        config.description = "高性能反檢測配置"
        config.headless = True
        config.page_load_timeout = 15
        config.script_timeout = 15
        config.delay_config["min_delay"] = 0.5
        config.delay_config["max_delay"] = 2
        config.max_retries = 2
        config.retry_delay = 3
        config.detection_threshold = 0.7
        config.block_threshold = 0.8
        return config
    
    def create_high_privacy_config(self) -> AntiDetectionConfig:
        """創建高隱私配置
        
        Returns:
            AntiDetectionConfig: 高隱私配置對象
        """
        config = self.create_default_config()
        config.id = "high_privacy"
        config.description = "高隱私反檢測配置"
        config.use_proxy = True
        config.proxies = [
            {"type": "http", "host": "proxy1.example.com", "port": 8080},
            {"type": "socks5", "host": "proxy2.example.com", "port": 1080}
        ]
        config.use_random_user_agent = True
        config.user_agents.extend([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ])
        config.anti_fingerprint.update({
            "enable_webgl_noise": True,
            "enable_canvas_noise": True,
            "enable_audio_noise": True,
            "enable_font_noise": True,
            "enable_webgl_vendor_spoof": True,
            "enable_webgl_renderer_spoof": True,
            "enable_platform_spoof": True,
            "enable_language_spoof": True,
            "enable_timezone_spoof": True,
            "enable_screen_spoof": True,
            "enable_color_depth_spoof": True,
            "enable_pixel_ratio_spoof": True,
            "enable_webgl_parameter_noise": True,
            "enable_canvas_parameter_noise": True,
            "enable_audio_parameter_noise": True,
            "enable_font_parameter_noise": True
        })
        config.delay_config.update({
            "min_delay": 2,
            "max_delay": 8,
            "random_delay": True,
            "mouse_movement_delay": True,
            "typing_delay": True,
            "scroll_delay": True,
            "click_delay": True,
            "mouse_movement_pattern": "random",
            "typing_pattern": "random",
            "scroll_pattern": "random"
        })
        config.max_retries = 5
        config.retry_delay = 10
        config.detection_threshold = 0.9
        config.block_threshold = 0.95
        return config
    
    def create_custom_config(
        self,
        config_id: str,
        description: str,
        **kwargs
    ) -> AntiDetectionConfig:
        """創建自定義配置
        
        Args:
            config_id: 配置ID
            description: 配置描述
            **kwargs: 自定義參數
            
        Returns:
            AntiDetectionConfig: 自定義配置對象
        """
        config = self.create_default_config()
        config.id = config_id
        config.description = description
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def load_config_from_file(self, file_path: str) -> AntiDetectionConfig:
        """從文件加載配置
        
        Args:
            file_path: 配置文件路徑
            
        Returns:
            AntiDetectionConfig: 配置對象
        """
        return AntiDetectionConfig.from_file(file_path)
    
    def save_config_to_file(
        self,
        config: AntiDetectionConfig,
        file_path: Optional[str] = None
    ) -> None:
        """保存配置到文件
        
        Args:
            config: 配置對象
            file_path: 配置文件路徑，如果為None則使用默認路徑
        """
        if file_path is None:
            file_path = os.path.join(self.config_dir, f"{config.id}.json")
        
        config.save_to_file(file_path)
    
    def create_config_from_template(
        self,
        template_id: str,
        config_id: str,
        description: str,
        **kwargs
    ) -> AntiDetectionConfig:
        """從模板創建配置
        
        Args:
            template_id: 模板ID（default、high_performance、high_privacy）
            config_id: 配置ID
            description: 配置描述
            **kwargs: 自定義參數
            
        Returns:
            AntiDetectionConfig: 配置對象
        """
        if template_id == "default":
            config = self.create_default_config()
        elif template_id == "high_performance":
            config = self.create_high_performance_config()
        elif template_id == "high_privacy":
            config = self.create_high_privacy_config()
        else:
            raise ValueError(f"未知的模板ID: {template_id}")
        
        config.id = config_id
        config.description = description
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config 
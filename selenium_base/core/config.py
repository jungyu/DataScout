#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Selenium 基礎配置
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from selenium_base.core.exceptions import ConfigError

@dataclass
class Config:
    """Selenium 基礎配置類"""
    
    # 瀏覽器配置
    browser_type: str = "chrome"  # 瀏覽器類型：chrome, firefox, safari
    headless: bool = False  # 是否使用無頭模式
    remote_url: Optional[str] = None  # 遠程 WebDriver 地址
    
    # 窗口配置
    window_size: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    maximize: bool = True  # 是否最大化窗口
    
    # 超時配置
    page_load_timeout: int = 30  # 頁面加載超時時間（秒）
    implicit_wait: int = 10  # 隱式等待時間（秒）
    script_timeout: int = 30  # 腳本執行超時時間（秒）
    
    # 重試配置
    max_retries: int = 3  # 最大重試次數
    retry_interval: int = 1  # 重試間隔（秒）
    
    # 路徑配置
    base_dir: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir: str = os.path.join(base_dir, "data")
    cookies_dir: str = os.path.join(data_dir, "cookies")
    logs_dir: str = os.path.join(data_dir, "logs")
    errors_dir: str = os.path.join(data_dir, "errors")
    screenshots_dir: str = os.path.join(data_dir, "screenshots")
    temp_dir: str = os.path.join(data_dir, "temp")
    search_dir: str = os.path.join(data_dir, "search")
    
    # 日誌配置
    log_level: str = "INFO"  # 日誌級別：DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = os.path.join(logs_dir, "selenium.log")
    
    # 截圖配置
    screenshot_on_error: bool = True  # 錯誤時是否自動截圖
    screenshot_format: str = "png"  # 截圖格式：png, jpg
    
    def __post_init__(self):
        """初始化後處理"""
        self._validate_config()
        self._create_directories()
    
    def _validate_config(self):
        """驗證配置"""
        # 驗證瀏覽器類型
        if self.browser_type not in ["chrome", "firefox", "safari"]:
            raise ConfigError(f"Unsupported browser type: {self.browser_type}")
        
        # 驗證超時設置
        if self.page_load_timeout < 0:
            raise ConfigError("Page load timeout must be non-negative")
        if self.implicit_wait < 0:
            raise ConfigError("Implicit wait must be non-negative")
        if self.script_timeout < 0:
            raise ConfigError("Script timeout must be non-negative")
        
        # 驗證重試設置
        if self.max_retries < 0:
            raise ConfigError("Max retries must be non-negative")
        if self.retry_interval < 0:
            raise ConfigError("Retry interval must be non-negative")
        
        # 驗證日誌級別
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ConfigError(f"Invalid log level: {self.log_level}")
        
        # 驗證截圖格式
        if self.screenshot_format not in ["png", "jpg"]:
            raise ConfigError(f"Unsupported screenshot format: {self.screenshot_format}")
    
    def _create_directories(self):
        """創建必要的目錄"""
        directories = [
            self.data_dir,
            self.cookies_dir,
            self.logs_dir,
            self.errors_dir,
            self.screenshots_dir,
            self.temp_dir,
            self.search_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """將配置轉換為字典
        
        Returns:
            配置字典
        """
        return {
            "browser_type": self.browser_type,
            "headless": self.headless,
            "remote_url": self.remote_url,
            "window_size": self.window_size,
            "maximize": self.maximize,
            "page_load_timeout": self.page_load_timeout,
            "implicit_wait": self.implicit_wait,
            "script_timeout": self.script_timeout,
            "max_retries": self.max_retries,
            "retry_interval": self.retry_interval,
            "base_dir": self.base_dir,
            "data_dir": self.data_dir,
            "cookies_dir": self.cookies_dir,
            "logs_dir": self.logs_dir,
            "errors_dir": self.errors_dir,
            "screenshots_dir": self.screenshots_dir,
            "temp_dir": self.temp_dir,
            "search_dir": self.search_dir,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "log_file": self.log_file,
            "screenshot_on_error": self.screenshot_on_error,
            "screenshot_format": self.screenshot_format
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """從字典創建配置
        
        Args:
            config_dict: 配置字典
            
        Returns:
            配置實例
        """
        return cls(**config_dict) 
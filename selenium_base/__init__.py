#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Selenium 基礎工具包

提供基於 Selenium 的自動化測試和爬蟲功能。
主要功能：
- 瀏覽器自動化
- 反檢測機制
- 認證管理
- 配置管理
- 日誌記錄
"""

from selenium_base.core.browser import Browser
from selenium_base.core.config import BrowserConfig
from selenium_base.core.exceptions import (
    BrowserError,
    ValidationError,
    ConfigurationError
)
from selenium_base.utils.logger import setup_logger
from selenium_base.utils.config import load_config

__version__ = "0.1.0"
__author__ = "DataScout Team"

__all__ = [
    # 核心類
    "Browser",
    "BrowserConfig",
    
    # 異常類
    "BrowserError",
    "ValidationError",
    "ConfigurationError",
    
    # 工具函數
    "setup_logger",
    "load_config"
] 
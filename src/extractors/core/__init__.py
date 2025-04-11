#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬蟲核心模組

提供爬蟲的核心功能，包括：
1. 基礎提取器
2. 數據提取器
3. 工具函數
"""

from .base import BaseExtractor
from .data_extractor import DataExtractor

# 從 src.core.utils 導入工具類
from src.core.utils import (
    # 瀏覽器工具
    BrowserUtils,
    
    # 配置工具
    ConfigUtils,
    
    # 路徑工具
    PathUtils,
    
    # 日誌工具
    Logger,
    
    # URL 工具
    URLUtils,
    
    # 數據處理工具
    DataProcessor,
    
    # 錯誤處理工具
    ErrorHandler,
    
    # Cookie 管理工具
    CookieManager
)

__all__ = [
    # 提取器
    'BaseExtractor',
    'DataExtractor',
    
    # 工具類
    'BrowserUtils',
    'ConfigUtils',
    'PathUtils',
    'Logger',
    'URLUtils',
    'DataProcessor',
    'ErrorHandler',
    'CookieManager'
]

__version__ = '1.0.0'
__author__ = 'Your Name'
__license__ = 'MIT'
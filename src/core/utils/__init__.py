#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
核心工具模組

提供爬蟲系統的通用工具功能，包括：
- 瀏覽器操作
- URL 處理
- 配置管理
- 錯誤處理
- 日誌記錄
- 路徑處理
- 數據處理
"""

from .browser_utils import (
    BrowserUtils,
    BrowserAction,
    BrowserState
)
from .url_utils import (
    URLUtils,
    URLValidator,
    URLNormalizer
)
from .config_utils import (
    ConfigUtils,
    ConfigValidator,
    ConfigLoader
)
from .error_handler import (
    ErrorHandler,
    ErrorLevel,
    ErrorType
)
from .logger import (
    Logger,
    LogLevel,
    LogFormatter
)
from .path_utils import (
    PathUtils,
    PathValidator,
    PathNormalizer
)
from .data_processor import (
    DataProcessor,
    DataValidator,
    DataNormalizer
)

__version__ = '1.0.0'
__author__ = 'Aaron Yu (https://github.com/jungyu), Claude AI, Cursor AI'
__license__ = 'MIT'

__all__ = [
    # 瀏覽器工具
    'BrowserUtils',
    'BrowserAction',
    'BrowserState',
    
    # URL 工具
    'URLUtils',
    'URLValidator',
    'URLNormalizer',
    
    # 配置工具
    'ConfigUtils',
    'ConfigValidator',
    'ConfigLoader',
    
    # 錯誤處理
    'ErrorHandler',
    'ErrorLevel',
    'ErrorType',
    
    # 日誌工具
    'Logger',
    'LogLevel',
    'LogFormatter',
    
    # 路徑工具
    'PathUtils',
    'PathValidator',
    'PathNormalizer',
    
    # 數據處理
    'DataProcessor',
    'DataValidator',
    'DataNormalizer'
] 
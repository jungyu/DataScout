#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數據持久化模組

提供數據存儲相關功能，包括：
- 本地存儲
- 數據庫存儲
- API 存儲
- 雲存儲
- 存儲特定工具
"""

from src.core.utils import (
    ConfigUtils,
    Logger,
    PathUtils,
    DataProcessor,
    ErrorHandler
)

from .config import StorageConfig
from .manager import StorageManager
from .handlers import (
    StorageHandler,
    LocalStorageHandler,
    MongoDBHandler,
    NotionHandler,
    CaptchaHandler,
    CaptchaDetectionResult
)

__all__ = [
    # 核心工具類
    'ConfigUtils',
    'Logger',
    'PathUtils',
    'DataProcessor',
    'ErrorHandler',
    
    # 配置類
    'StorageConfig',
    
    # 管理器
    'StorageManager',
    
    # 處理器
    'StorageHandler',
    'LocalStorageHandler',
    'MongoDBHandler',
    'NotionHandler',
    'CaptchaHandler',
    'CaptchaDetectionResult'
]

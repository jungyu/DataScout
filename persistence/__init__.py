#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
持久化模組 (Persistence Module)

提供通用的數據持久化功能，支援多種存儲後端和數據格式。

主要功能：
- 數據存儲：支援本地文件、MongoDB、Notion等多種存儲後端
- 數據備份：自動備份和版本控制
- 數據恢復：從備份中恢復數據
- 數據驗證：確保數據完整性和一致性
- 錯誤處理：統一的錯誤處理機制
- 日誌記錄：詳細的操作日誌

擴展性：
- 支援自定義存儲後端
- 支援自定義數據格式
- 支援自定義驗證規則
- 支援與其他基礎模組(selenium_base, api_base等)的整合

使用方式：
```python
from persistence import StorageHandler
from persistence.handlers import LocalStorageHandler

# 創建存儲處理器
handler = LocalStorageHandler(config={
    'base_dir': './data',
    'format': 'json'
})

# 存儲數據
handler.save(data={'key': 'value'}, path='example.json')

# 讀取數據
data = handler.load(path='example.json')
```
"""

from persistence.core.base import StorageHandler
from persistence.handlers.local_handler import LocalStorageHandler
from persistence.handlers.mongodb_handler import MongoDBHandler
from persistence.handlers.notion_handler import NotionHandler
from persistence.handlers.supabase_handler import SupabaseHandler, SupabaseConfig
from persistence.core.exceptions import (
    PersistenceError,
    StorageError,
    ValidationError,
    ConfigError
)
from persistence.core.config import StorageConfig

__version__ = '2.0.0'
__author__ = 'Aaron Yu (https://github.com/jungyu), Claude AI, Cursor AI'
__license__ = 'MIT'

__all__ = [
    # 核心類
    'StorageHandler',
    'StorageConfig',
    
    # 存儲處理器
    'LocalStorageHandler',
    'MongoDBHandler',
    'NotionHandler',
    'SupabaseHandler',
    'SupabaseConfig',
    
    # 異常類
    'PersistenceError',
    'StorageError',
    'ValidationError',
    'ConfigError'
] 
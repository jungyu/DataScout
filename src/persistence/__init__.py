#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存儲管理包
提供統一的存儲管理功能
"""

from .config.storage_config import StorageConfig
from .manager.storage_manager import StorageManager
from .handlers.local_storage import LocalStorageHandler
from .handlers.mongodb_handler import MongoDBHandler
from .handlers.notion_handler import NotionHandler

__all__ = [
    "StorageConfig",
    "StorageManager",
    "LocalStorageHandler",
    "MongoDBHandler",
    "NotionHandler"
]

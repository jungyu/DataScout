#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存儲處理器測試
測試各種存儲處理器的功能
"""

import os
import sys
import pytest
from pathlib import Path
from datetime import datetime

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.persistence.config.storage_config import StorageConfig
from src.persistence.handlers.base_handler import StorageHandler
from src.persistence.handlers.local_handler import LocalStorageHandler
from src.persistence.handlers.mongodb_handler import MongoDBHandler
from src.persistence.handlers.notion_handler import NotionHandler

class TestBaseHandler:
    """基礎存儲處理器測試"""
    
    @pytest.fixture
    def config(self):
        """配置測試"""
        return StorageConfig(
            mode="local",
            local_path="test_data",
            backup_path="test_backups"
        )
    
    @pytest.fixture
    def handler(self, config):
        """處理器測試"""
        return StorageHandler(config)
    
    def test_init(self, handler):
        """測試初始化"""
        assert handler.config is not None
        assert handler.status is not None
    
    def test_update_status(self, handler):
        """測試更新狀態"""
        handler._update_status("test", True)
        assert handler.status["last_operation"] == "test"
        assert handler.status["success_count"] == 1

class TestLocalHandler:
    """本地存儲處理器測試"""
    
    @pytest.fixture
    def config(self):
        """配置測試"""
        return StorageConfig(
            mode="local",
            local_path="test_data",
            backup_path="test_backups"
        )
    
    @pytest.fixture
    def handler(self, config):
        """處理器測試"""
        return LocalStorageHandler(config)
    
    def test_save_data(self, handler):
        """測試保存數據"""
        test_data = {"key": "value"}
        success = handler.save_data(test_data)
        assert success is True
    
    def test_load_data(self, handler):
        """測試加載數據"""
        data = handler.load_data()
        assert isinstance(data, list)
    
    def test_delete_data(self, handler):
        """測試刪除數據"""
        test_query = {"key": "value"}
        success = handler.delete_data(test_query)
        assert success is True
    
    def test_clear_data(self, handler):
        """測試清空數據"""
        success = handler.clear_data()
        assert success is True
    
    def test_create_backup(self, handler):
        """測試創建備份"""
        success = handler.create_backup()
        assert success is True
    
    def test_restore_backup(self, handler):
        """測試恢復備份"""
        backups = handler.list_backups()
        if backups:
            success = handler.restore_backup(backups[0])
            assert success is True

class TestMongoDBHandler:
    """MongoDB存儲處理器測試"""
    
    @pytest.fixture
    def config(self):
        """配置測試"""
        return StorageConfig(
            mode="mongodb",
            mongodb_uri="mongodb://localhost:27017",
            mongodb_database="test_db",
            mongodb_collection="test_collection"
        )
    
    @pytest.fixture
    def handler(self, config):
        """處理器測試"""
        return MongoDBHandler(config)
    
    def test_connect(self, handler):
        """測試連接"""
        assert handler.status["connected"] is True
    
    def test_save_data(self, handler):
        """測試保存數據"""
        test_data = {"key": "value"}
        success = handler.save_data(test_data)
        assert success is True
    
    def test_load_data(self, handler):
        """測試加載數據"""
        data = handler.load_data()
        assert isinstance(data, list)
    
    def test_delete_data(self, handler):
        """測試刪除數據"""
        test_query = {"key": "value"}
        success = handler.delete_data(test_query)
        assert success is True
    
    def test_clear_data(self, handler):
        """測試清空數據"""
        success = handler.clear_data()
        assert success is True

class TestNotionHandler:
    """Notion存儲處理器測試"""
    
    @pytest.fixture
    def config(self):
        """配置測試"""
        return StorageConfig(
            mode="notion",
            notion_token="test_token",
            notion_database_id="test_database_id",
            notion_parent_page_id="test_parent_page_id"
        )
    
    @pytest.fixture
    def handler(self, config):
        """處理器測試"""
        return NotionHandler(config)
    
    def test_connect(self, handler):
        """測試連接"""
        assert handler.status["connected"] is True
    
    def test_save_data(self, handler):
        """測試保存數據"""
        test_data = {"key": "value"}
        success = handler.save_data(test_data)
        assert success is True
    
    def test_load_data(self, handler):
        """測試加載數據"""
        data = handler.load_data()
        assert isinstance(data, list)
    
    def test_delete_data(self, handler):
        """測試刪除數據"""
        test_query = {"key": "value"}
        success = handler.delete_data(test_query)
        assert success is True
    
    def test_clear_data(self, handler):
        """測試清空數據"""
        success = handler.clear_data()
        assert success is True 
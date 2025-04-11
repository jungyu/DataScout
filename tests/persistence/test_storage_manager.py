#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存儲管理器單元測試模組
"""

import os
import json
import pytest
from datetime import datetime
from typing import Dict, Any

from src.persistence.config.storage_config import StorageConfig
from src.persistence.manager.storage_manager import StorageManager


@pytest.fixture
def local_config() -> StorageConfig:
    """本地存儲配置"""
    return StorageConfig(
        storage_mode="local",
        local_storage_path="tests/data",
        backup_enabled=True,
        max_backups=3
    )


@pytest.fixture
def mongodb_config() -> StorageConfig:
    """MongoDB存儲配置"""
    return StorageConfig(
        storage_mode="mongodb",
        mongodb_host="localhost",
        mongodb_port=27017,
        mongodb_database="test_db",
        mongodb_collection="test_collection",
        backup_enabled=True,
        max_backups=3
    )


@pytest.fixture
def notion_config() -> StorageConfig:
    """Notion存儲配置"""
    return StorageConfig(
        storage_mode="notion",
        notion_token="test_token",
        notion_database_id="test_database_id",
        backup_enabled=True,
        max_backups=3
    )


@pytest.fixture
def test_data() -> Dict[str, Any]:
    """測試數據"""
    return {
        "id": "test_id",
        "name": "test_name",
        "value": 123,
        "timestamp": datetime.now().isoformat()
    }


class TestStorageManager:
    """存儲管理器測試類"""
    
    def test_init_local_handler(self, local_config):
        """測試初始化本地存儲處理器"""
        manager = StorageManager(local_config)
        assert manager.config.storage_mode == "local"
        assert manager.handler is not None
        assert manager.status["last_operation"] == "init_handler"
    
    def test_init_mongodb_handler(self, mongodb_config):
        """測試初始化MongoDB存儲處理器"""
        manager = StorageManager(mongodb_config)
        assert manager.config.storage_mode == "mongodb"
        assert manager.handler is not None
        assert manager.status["last_operation"] == "init_handler"
    
    def test_init_notion_handler(self, notion_config):
        """測試初始化Notion存儲處理器"""
        manager = StorageManager(notion_config)
        assert manager.config.storage_mode == "notion"
        assert manager.handler is not None
        assert manager.status["last_operation"] == "init_handler"
    
    def test_invalid_storage_mode(self):
        """測試無效的存儲模式"""
        config = StorageConfig(storage_mode="invalid")
        with pytest.raises(ValueError):
            StorageManager(config)
    
    def test_save_and_load_data(self, local_config, test_data):
        """測試保存和加載數據"""
        manager = StorageManager(local_config)
        
        # 保存數據
        assert manager.save_data(test_data)
        assert manager.status["last_operation"] == "save_data"
        
        # 加載數據
        loaded_data = manager.load_data({"id": test_data["id"]})
        assert len(loaded_data) == 1
        assert loaded_data[0]["id"] == test_data["id"]
        assert manager.status["last_operation"] == "load_data"
    
    def test_save_and_load_batch(self, local_config):
        """測試批量保存和加載數據"""
        manager = StorageManager(local_config)
        data_list = [
            {"id": f"test_id_{i}", "value": i}
            for i in range(3)
        ]
        
        # 批量保存
        assert manager.save_batch(data_list)
        assert manager.status["last_operation"] == "save_batch"
        
        # 加載數據
        loaded_data = manager.load_data()
        assert len(loaded_data) == 3
        assert manager.status["last_operation"] == "load_data"
    
    def test_delete_data(self, local_config, test_data):
        """測試刪除數據"""
        manager = StorageManager(local_config)
        
        # 保存數據
        manager.save_data(test_data)
        
        # 刪除數據
        assert manager.delete_data({"id": test_data["id"]})
        assert manager.status["last_operation"] == "delete_data"
        
        # 確認數據已刪除
        loaded_data = manager.load_data({"id": test_data["id"]})
        assert len(loaded_data) == 0
    
    def test_clear_data(self, local_config):
        """測試清空數據"""
        manager = StorageManager(local_config)
        
        # 保存一些數據
        for i in range(3):
            manager.save_data({"id": f"test_id_{i}", "value": i})
        
        # 清空數據
        assert manager.clear_data()
        assert manager.status["last_operation"] == "clear_data"
        
        # 確認數據已清空
        loaded_data = manager.load_data()
        assert len(loaded_data) == 0
    
    def test_get_data_count(self, local_config):
        """測試獲取數據數量"""
        manager = StorageManager(local_config)
        
        # 保存一些數據
        for i in range(3):
            manager.save_data({"id": f"test_id_{i}", "value": i})
        
        # 獲取數量
        count = manager.get_data_count()
        assert count == 3
        assert manager.status["last_operation"] == "get_data_count"
    
    def test_backup_operations(self, local_config, test_data):
        """測試備份操作"""
        manager = StorageManager(local_config)
        
        # 保存數據
        manager.save_data(test_data)
        
        # 創建備份
        assert manager.create_backup()
        assert manager.status["last_operation"] == "create_backup"
        
        # 列出備份
        backups = manager.list_backups()
        assert len(backups) > 0
        assert manager.status["last_operation"] == "list_backups"
        
        # 清空數據
        manager.clear_data()
        
        # 恢復備份
        assert manager.restore_backup(backups[0])
        assert manager.status["last_operation"] == "restore_backup"
        
        # 確認數據已恢復
        loaded_data = manager.load_data({"id": test_data["id"]})
        assert len(loaded_data) == 1
        
        # 刪除備份
        assert manager.delete_backup(backups[0])
        assert manager.status["last_operation"] == "delete_backup"
    
    def test_backup_disabled(self, local_config):
        """測試備份功能禁用"""
        local_config.backup_enabled = False
        manager = StorageManager(local_config)
        
        # 嘗試創建備份
        assert not manager.create_backup()
        assert manager.status["last_operation"] == "create_backup"
        
        # 嘗試列出備份
        backups = manager.list_backups()
        assert len(backups) == 0
        assert manager.status["last_operation"] == "list_backups"
    
    def test_error_handling(self, local_config):
        """測試錯誤處理"""
        manager = StorageManager(local_config)
        
        # 測試無效數據
        assert not manager.save_data(None)
        assert manager.status["last_error"] is not None
        
        # 測試無效查詢
        loaded_data = manager.load_data({"invalid_field": "value"})
        assert len(loaded_data) == 0
        assert manager.status["last_operation"] == "load_data"
    
    def test_context_manager(self, local_config):
        """測試上下文管理器"""
        with StorageManager(local_config) as manager:
            assert manager.config.storage_mode == "local"
            assert manager.handler is not None
        
        # 確認上下文退出狀態
        assert manager.status["last_operation"] == "context_exit"
    
    def test_status_tracking(self, local_config):
        """測試狀態追蹤"""
        manager = StorageManager(local_config)
        
        # 執行一些操作
        manager.save_data({"id": "test_id", "value": 123})
        manager.load_data()
        manager.get_data_count()
        
        # 檢查狀態
        status = manager.get_status()
        assert status["last_operation"] == "get_data_count"
        assert "save_data" in status["operation_counts"]
        assert "load_data" in status["operation_counts"]
        assert "get_data_count" in status["operation_counts"]
        assert status["handler_status"] is not None 
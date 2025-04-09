#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存儲管理器模組
提供統一的存儲管理接口
"""

from typing import Dict, List, Optional, Any
from ..config.storage_config import StorageConfig
from ..handlers.local_storage import LocalStorageHandler
from ..handlers.mongodb_handler import MongoDBHandler
from ..handlers.notion_handler import NotionHandler


class StorageManager:
    """存儲管理器"""
    
    def __init__(self, config: StorageConfig):
        """初始化存儲管理器"""
        self.config = config
        self.handler = self._create_handler()
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """保存單條數據"""
        return self.handler.save_data(data)
    
    def save_batch(self, data_list: List[Dict[str, Any]]) -> bool:
        """批量保存數據"""
        return self.handler.save_batch(data_list)
    
    def load_data(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """加載數據"""
        return self.handler.load_data(query)
    
    def delete_data(self, query: Dict[str, Any]) -> bool:
        """刪除數據"""
        return self.handler.delete_data(query)
    
    def clear_data(self) -> bool:
        """清空數據"""
        return self.handler.clear_data()
    
    def get_data_count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """獲取數據數量"""
        return self.handler.get_data_count(query)
    
    def create_backup(self) -> bool:
        """創建備份"""
        return self.handler.create_backup()
    
    def restore_backup(self, backup_id: str) -> bool:
        """恢復備份"""
        return self.handler.restore_backup(backup_id)
    
    def list_backups(self) -> List[str]:
        """列出所有備份"""
        return self.handler.list_backups()
    
    def delete_backup(self, backup_id: str) -> bool:
        """刪除備份"""
        return self.handler.delete_backup(backup_id)
    
    def _create_handler(self):
        """創建存儲處理器"""
        if self.config.storage_mode == "local":
            return LocalStorageHandler(self.config)
        elif self.config.storage_mode == "mongodb":
            return MongoDBHandler(self.config)
        elif self.config.storage_mode == "notion":
            return NotionHandler(self.config)
        else:
            raise ValueError(f"不支持的存儲模式: {self.config.storage_mode}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if hasattr(self.handler, "__exit__"):
            self.handler.__exit__(exc_type, exc_val, exc_tb) 
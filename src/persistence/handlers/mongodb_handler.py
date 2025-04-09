#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MongoDB 存儲處理器模組
實現 MongoDB 數據庫存儲功能
"""

import time
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from ..config.storage_config import StorageConfig
from .base_handler import StorageHandler


class MongoDBHandler(StorageHandler):
    """MongoDB 存儲處理器"""
    
    def __init__(self, config: StorageConfig):
        """初始化 MongoDB 存儲處理器"""
        super().__init__(config)
        self.client = self._connect()
        self.db = self._get_database()
        self.collection = self._get_collection()
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """保存單條數據"""
        try:
            # 添加時間戳
            if self.config.timestamp_field not in data:
                data[self.config.timestamp_field] = time.time()
            
            # 保存到 MongoDB
            result = self.collection.insert_one(data)
            return bool(result.inserted_id)
            
        except Exception as e:
            print(f"保存數據失敗: {str(e)}")
            return False
    
    def save_batch(self, data_list: List[Dict[str, Any]]) -> bool:
        """批量保存數據"""
        try:
            # 添加時間戳
            for data in data_list:
                if self.config.timestamp_field not in data:
                    data[self.config.timestamp_field] = time.time()
            
            # 保存到 MongoDB
            result = self.collection.insert_many(data_list)
            return bool(result.inserted_ids)
            
        except Exception as e:
            print(f"批量保存數據失敗: {str(e)}")
            return False
    
    def load_data(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """加載數據"""
        try:
            # 查詢數據
            cursor = self.collection.find(query or {})
            return list(cursor)
            
        except Exception as e:
            print(f"加載數據失敗: {str(e)}")
            return []
    
    def delete_data(self, query: Dict[str, Any]) -> bool:
        """刪除數據"""
        try:
            # 刪除數據
            result = self.collection.delete_many(query)
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"刪除數據失敗: {str(e)}")
            return False
    
    def clear_data(self) -> bool:
        """清空數據"""
        try:
            # 刪除所有數據
            result = self.collection.delete_many({})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"清空數據失敗: {str(e)}")
            return False
    
    def get_data_count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """獲取數據數量"""
        try:
            return self.collection.count_documents(query or {})
        except Exception as e:
            print(f"獲取數據數量失敗: {str(e)}")
            return 0
    
    def create_backup(self) -> bool:
        """創建備份"""
        try:
            # 獲取所有數據
            data = self.load_data()
            
            # 創建備份集合
            backup_collection = self._get_backup_collection()
            
            # 保存到備份集合
            if data:
                backup_collection.insert_many(data)
            
            return True
            
        except Exception as e:
            print(f"創建備份失敗: {str(e)}")
            return False
    
    def restore_backup(self, backup_id: str) -> bool:
        """恢復備份"""
        try:
            # 獲取備份集合
            backup_collection = self._get_backup_collection(backup_id)
            
            # 獲取備份數據
            data = list(backup_collection.find())
            
            # 清空當前集合
            self.clear_data()
            
            # 恢復數據
            if data:
                self.collection.insert_many(data)
            
            return True
            
        except Exception as e:
            print(f"恢復備份失敗: {str(e)}")
            return False
    
    def list_backups(self) -> List[str]:
        """列出所有備份"""
        try:
            # 獲取所有集合
            collections = self.db.list_collection_names()
            
            # 過濾備份集合
            return [name for name in collections if name.startswith("backup_")]
            
        except Exception as e:
            print(f"列出備份失敗: {str(e)}")
            return []
    
    def delete_backup(self, backup_id: str) -> bool:
        """刪除備份"""
        try:
            # 獲取備份集合
            backup_collection = self._get_backup_collection(backup_id)
            
            # 刪除備份集合
            backup_collection.drop()
            
            return True
            
        except Exception as e:
            print(f"刪除備份失敗: {str(e)}")
            return False
    
    def _connect(self) -> MongoClient:
        """連接 MongoDB"""
        try:
            return MongoClient(
                self.config.get_mongodb_uri(),
                serverSelectionTimeoutMS=self.config.mongodb_timeout,
                maxPoolSize=self.config.mongodb_max_pool_size
            )
        except Exception as e:
            raise ConnectionError(f"連接 MongoDB 失敗: {str(e)}")
    
    def _get_database(self) -> Database:
        """獲取數據庫"""
        return self.client[self.config.mongodb_db]
    
    def _get_collection(self) -> Collection:
        """獲取集合"""
        return self.db["data"]
    
    def _get_backup_collection(self, backup_id: Optional[str] = None) -> Collection:
        """獲取備份集合"""
        if backup_id is None:
            backup_id = time.strftime("%Y%m%d_%H%M%S")
        return self.db[f"backup_{backup_id}"]
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.client.close() 
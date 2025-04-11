#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MongoDB存儲處理器模組
實現基於MongoDB的數據存儲功能
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId

from .base_handler import StorageHandler
from ..config.storage_config import StorageConfig
from ..utils.storage_utils import StorageUtils


class MongoDBHandler(StorageHandler):
    """MongoDB存儲處理器"""
    
    def __init__(self, config: StorageConfig):
        """
        初始化MongoDB存儲處理器
        
        Args:
            config: 存儲配置
        """
        super().__init__(config)
        self.storage_utils = StorageUtils()
        
        # 初始化連接
        self.client = None
        self.db = None
        self.collection = None
        
        # 連接數據庫
        self._connect()
    
    def _connect(self) -> None:
        """連接MongoDB數據庫"""
        try:
            # 獲取連接 URI
            uri = self.config.get_mongodb_uri()
            
            # 創建客戶端
            self.client = MongoClient(
                uri,
                serverSelectionTimeoutMS=self.config.mongodb_timeout,
                maxPoolSize=self.config.mongodb_max_pool_size
            )
            
            # 獲取數據庫
            self.db = self.client[self.config.mongodb_database]
            
            # 獲取集合
            self.collection = self.db[self.config.mongodb_collection]
            
            # 更新狀態
            self.status['connected'] = True
            self._update_status("connect", True)
            
        except Exception as e:
            self.status['connected'] = False
            self._update_status("connect", False, e)
            raise
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """
        保存單條數據
        
        Args:
            data: 要保存的數據
            
        Returns:
            bool: 是否成功
        """
        try:
            # 添加時間戳
            if self.config.timestamp_field not in data:
                data[self.config.timestamp_field] = self.get_timestamp()
            
            # 保存數據
            result = self.collection.insert_one(data)
            
            # 更新狀態
            success = result.inserted_id is not None
            self._update_status("save_data", success)
            return success
            
        except Exception as e:
            self._update_status("save_data", False, e)
            return False
    
    def save_batch(self, data_list: List[Dict[str, Any]]) -> bool:
        """
        批量保存數據
        
        Args:
            data_list: 要保存的數據列表
            
        Returns:
            bool: 是否成功
        """
        try:
            # 添加時間戳
            for data in data_list:
                if self.config.timestamp_field not in data:
                    data[self.config.timestamp_field] = self.get_timestamp()
            
            # 保存數據
            result = self.collection.insert_many(data_list)
            
            # 更新狀態
            success = len(result.inserted_ids) == len(data_list)
            self._update_status("save_batch", success)
            return success
            
        except Exception as e:
            self._update_status("save_batch", False, e)
            return False
    
    def load_data(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        加載數據
        
        Args:
            query: 查詢條件
            
        Returns:
            List[Dict[str, Any]]: 加載的數據列表
        """
        try:
            # 轉換查詢條件
            if query:
                query = self._convert_query(query)
            
            # 查詢數據
            cursor = self.collection.find(query or {})
            data = list(cursor)
            
            # 更新狀態
            self._update_status("load_data", True)
            return data
            
        except Exception as e:
            self._update_status("load_data", False, e)
            return []
    
    def delete_data(self, query: Dict[str, Any]) -> bool:
        """
        刪除數據
        
        Args:
            query: 刪除條件
            
        Returns:
            bool: 是否成功
        """
        try:
            # 轉換查詢條件
            query = self._convert_query(query)
            
            # 刪除數據
            result = self.collection.delete_many(query)
            
            # 更新狀態
            success = result.deleted_count > 0
            self._update_status("delete_data", success)
            return success
            
        except Exception as e:
            self._update_status("delete_data", False, e)
            return False
    
    def clear_data(self) -> bool:
        """
        清空數據
        
        Returns:
            bool: 是否成功
        """
        try:
            # 刪除所有數據
            result = self.collection.delete_many({})
            
            # 更新狀態
            success = result.deleted_count >= 0
            self._update_status("clear_data", success)
            return success
            
        except Exception as e:
            self._update_status("clear_data", False, e)
            return False
    
    def get_data_count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """
        獲取數據數量
        
        Args:
            query: 查詢條件
            
        Returns:
            int: 數據數量
        """
        try:
            # 轉換查詢條件
            if query:
                query = self._convert_query(query)
            
            # 獲取數量
            count = self.collection.count_documents(query or {})
            
            # 更新狀態
            self._update_status("get_data_count", True)
            return count
            
        except Exception as e:
            self._update_status("get_data_count", False, e)
            return 0
    
    def create_backup(self) -> bool:
        """
        創建備份
        
        Returns:
            bool: 是否成功
        """
        try:
            if not self.config.backup_enabled:
                return False
            
            # 創建備份集合
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_collection = self.db[backup_name]
            
            # 複製數據
            self.collection.aggregate([
                {"$match": {}},
                {"$out": backup_name}
            ])
            
            # 清理舊備份
            self._cleanup_old_backups()
            
            # 更新狀態
            self._update_status("create_backup", True)
            return True
            
        except Exception as e:
            self._update_status("create_backup", False, e)
            return False
    
    def restore_backup(self, backup_id: str) -> bool:
        """
        恢復備份
        
        Args:
            backup_id: 備份ID
            
        Returns:
            bool: 是否成功
        """
        try:
            # 獲取備份集合
            backup_collection = self.db[backup_id]
            if not backup_collection:
                return False
            
            # 清空當前集合
            self.collection.delete_many({})
            
            # 複製數據
            backup_collection.aggregate([
                {"$match": {}},
                {"$out": self.config.mongodb_collection}
            ])
            
            # 更新狀態
            self._update_status("restore_backup", True)
            return True
            
        except Exception as e:
            self._update_status("restore_backup", False, e)
            return False
    
    def list_backups(self) -> List[str]:
        """
        列出所有備份
        
        Returns:
            List[str]: 備份ID列表
        """
        try:
            # 獲取所有集合
            collections = self.db.list_collection_names()
            
            # 過濾備份集合
            backups = [name for name in collections if name.startswith("backup_")]
            backups.sort(reverse=True)
            
            # 更新狀態
            self._update_status("list_backups", True)
            return backups
            
        except Exception as e:
            self._update_status("list_backups", False, e)
            return []
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        刪除備份
        
        Args:
            backup_id: 備份ID
            
        Returns:
            bool: 是否成功
        """
        try:
            # 獲取備份集合
            backup_collection = self.db[backup_id]
            if not backup_collection:
                return False
            
            # 刪除集合
            backup_collection.drop()
            
            # 更新狀態
            self._update_status("delete_backup", True)
            return True
            
        except Exception as e:
            self._update_status("delete_backup", False, e)
            return False
    
    def _convert_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        轉換查詢條件為MongoDB格式
        
        Args:
            query: 查詢條件
            
        Returns:
            Dict[str, Any]: MongoDB查詢條件
        """
        result = {}
        for key, value in query.items():
            # 處理ObjectId
            if key == "_id":
                try:
                    value = ObjectId(value)
                except:
                    continue
            result[key] = value
        return result
    
    def _cleanup_old_backups(self) -> None:
        """清理舊備份"""
        try:
            # 列出備份
            backups = self.list_backups()
            
            # 如果超過最大備份數，刪除舊備份
            if len(backups) > self.config.max_backups:
                for backup_id in backups[self.config.max_backups:]:
                    self.delete_backup(backup_id)
        except Exception as e:
            self.log_error(f"清理舊備份失敗: {str(e)}")
    
    def __del__(self):
        """析構函數"""
        if self.client:
            self.client.close() 
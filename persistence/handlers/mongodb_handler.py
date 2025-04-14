#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MongoDB存儲處理器

提供基於MongoDB的數據存儲功能，支持文檔的增刪改查操作
"""

import time
from typing import Dict, Any, List, Optional, Union
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId
from ..core.base import StorageHandler
from ..core.config import MongoDBConfig
from ..core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

class MongoDBHandler(StorageHandler):
    """MongoDB存儲處理器"""
    
    def __init__(self, config: Union[Dict[str, Any], MongoDBConfig]):
        """
        初始化MongoDB存儲處理器
        
        Args:
            config: 配置對象或配置字典
        """
        super().__init__(config)
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.collection: Optional[Collection] = None
    
    def _setup_storage(self) -> None:
        """設置存儲環境"""
        try:
            # 構建連接URI
            uri = self._build_connection_uri()
            
            # 創建MongoDB客戶端
            self.client = MongoClient(
                uri,
                maxPoolSize=self.config.max_pool_size,
                minPoolSize=self.config.min_pool_size,
                maxIdleTimeMS=self.config.max_idle_time_ms,
                serverSelectionTimeoutMS=int(self.config.timeout * 1000)
            )
            
            # 測試連接
            self.client.server_info()
            
            # 獲取數據庫和集合
            self.db = self.client[self.config.database]
            self.collection = self.db[self.config.collection]
            
            self.logger.info(
                f"MongoDB存儲環境已初始化: "
                f"{self.config.host}:{self.config.port}/"
                f"{self.config.database}/{self.config.collection}"
            )
        except Exception as e:
            raise ConnectionError(f"連接MongoDB失敗: {str(e)}")
    
    def _build_connection_uri(self) -> str:
        """
        構建MongoDB連接URI
        
        Returns:
            str: 連接URI
        """
        # 構建認證部分
        auth = ""
        if self.config.username and self.config.password:
            auth = f"{self.config.username}:{self.config.password}@"
        
        # 構建URI
        return f"mongodb://{auth}{self.config.host}:{self.config.port}"
    
    def save(self, data: Any, path: str) -> None:
        """
        保存數據到MongoDB
        
        Args:
            data: 要保存的數據
            path: 文檔路徑（作為_id）
        """
        try:
            # 驗證數據
            self._validate_data(data)
            
            # 構建文檔
            document = {
                '_id': path,
                'data': data,
                'created_at': time.time(),
                'updated_at': time.time()
            }
            
            # 保存文檔
            self.collection.update_one(
                {'_id': path},
                {'$set': document},
                upsert=True
            )
            
            # 備份數據
            self._backup_data(data, path)
            
            self.logger.info(f"數據已保存到MongoDB: {path}")
        except Exception as e:
            raise StorageError(f"保存數據到MongoDB失敗: {str(e)}")
    
    def load(self, path: str) -> Any:
        """
        從MongoDB加載數據
        
        Args:
            path: 文檔路徑（作為_id）
            
        Returns:
            Any: 加載的數據
        """
        try:
            # 查詢文檔
            document = self.collection.find_one({'_id': path})
            
            # 檢查文檔是否存在
            if not document:
                raise NotFoundError(f"文檔不存在: {path}")
            
            self.logger.info(f"數據已從MongoDB加載: {path}")
            return document['data']
        except Exception as e:
            raise StorageError(f"從MongoDB加載數據失敗: {str(e)}")
    
    def delete(self, path: str) -> None:
        """
        從MongoDB刪除數據
        
        Args:
            path: 文檔路徑（作為_id）
        """
        try:
            # 刪除文檔
            result = self.collection.delete_one({'_id': path})
            
            # 檢查是否刪除成功
            if result.deleted_count == 0:
                raise NotFoundError(f"文檔不存在: {path}")
            
            self.logger.info(f"數據已從MongoDB刪除: {path}")
        except Exception as e:
            raise StorageError(f"從MongoDB刪除數據失敗: {str(e)}")
    
    def exists(self, path: str) -> bool:
        """
        檢查MongoDB文檔是否存在
        
        Args:
            path: 文檔路徑（作為_id）
            
        Returns:
            bool: 是否存在
        """
        try:
            # 查詢文檔
            document = self.collection.find_one(
                {'_id': path},
                {'_id': 1}
            )
            
            return document is not None
        except Exception as e:
            raise StorageError(f"檢查MongoDB文檔是否存在失敗: {str(e)}")
    
    def list(self, path: str = None) -> List[str]:
        """
        列出MongoDB文檔
        
        Args:
            path: 文檔路徑前綴，None表示所有文檔
            
        Returns:
            List[str]: 文檔路徑列表
        """
        try:
            # 構建查詢條件
            query = {}
            if path:
                query['_id'] = {'$regex': f'^{path}'}
            
            # 查詢文檔
            documents = self.collection.find(
                query,
                {'_id': 1}
            )
            
            # 提取文檔路徑
            paths = [doc['_id'] for doc in documents]
            
            return paths
        except Exception as e:
            raise StorageError(f"列出MongoDB文檔失敗: {str(e)}")
    
    def find(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        查詢MongoDB文檔
        
        Args:
            query: 查詢條件
            
        Returns:
            List[Dict[str, Any]]: 文檔列表
        """
        try:
            # 查詢文檔
            documents = self.collection.find(query)
            
            # 轉換為列表
            return list(documents)
        except Exception as e:
            raise StorageError(f"查詢MongoDB文檔失敗: {str(e)}")
    
    def update(self, path: str, update: Dict[str, Any]) -> None:
        """
        更新MongoDB文檔
        
        Args:
            path: 文檔路徑（作為_id）
            update: 更新操作
        """
        try:
            # 更新文檔
            result = self.collection.update_one(
                {'_id': path},
                update
            )
            
            # 檢查是否更新成功
            if result.matched_count == 0:
                raise NotFoundError(f"文檔不存在: {path}")
            
            self.logger.info(f"MongoDB文檔已更新: {path}")
        except Exception as e:
            raise StorageError(f"更新MongoDB文檔失敗: {str(e)}")
    
    def count(self, query: Dict[str, Any] = None) -> int:
        """
        統計MongoDB文檔數量
        
        Args:
            query: 查詢條件，None表示所有文檔
            
        Returns:
            int: 文檔數量
        """
        try:
            # 統計文檔數量
            return self.collection.count_documents(query or {})
        except Exception as e:
            raise StorageError(f"統計MongoDB文檔數量失敗: {str(e)}")
    
    def create_index(self, keys: List[tuple], **kwargs) -> None:
        """
        創建MongoDB索引
        
        Args:
            keys: 索引鍵列表
            **kwargs: 索引選項
        """
        try:
            # 創建索引
            self.collection.create_index(keys, **kwargs)
            
            self.logger.info(f"MongoDB索引已創建: {keys}")
        except Exception as e:
            raise StorageError(f"創建MongoDB索引失敗: {str(e)}")
    
    def drop_index(self, name: str) -> None:
        """
        刪除MongoDB索引
        
        Args:
            name: 索引名稱
        """
        try:
            # 刪除索引
            self.collection.drop_index(name)
            
            self.logger.info(f"MongoDB索引已刪除: {name}")
        except Exception as e:
            raise StorageError(f"刪除MongoDB索引失敗: {str(e)}")
    
    def __del__(self):
        """清理資源"""
        if self.client:
            self.client.close() 
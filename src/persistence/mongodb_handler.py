#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MongoDB 存儲模組

此模組提供 MongoDB 數據庫的存儲功能，支持文檔的增刪改查操作。
"""

import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, OperationFailure

@dataclass
class MongoDBConfig:
    """MongoDB 配置類"""
    host: str = "localhost"
    port: int = 27017
    username: Optional[str] = None
    password: Optional[str] = None
    database: str = "crawler"
    auth_source: str = "admin"
    timeout_ms: int = 5000
    max_pool_size: int = 100
    retry_count: int = 3
    retry_delay: int = 1
    timestamp_field: str = "timestamp"
    id_field: str = "_id"

class MongoDBHandler:
    """MongoDB 處理類"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化 MongoDB 處理器
        
        Args:
            config: 配置字典
        """
        self.logger = logging.getLogger(__name__)
        
        # 加載配置
        self.config = MongoDBConfig(**(config or {}))
        
        # 初始化連接
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
        
        # 連接數據庫
        self._connect()
        
        self.logger.info("MongoDB 處理器初始化完成")
    
    def _connect(self) -> None:
        """建立數據庫連接"""
        try:
            # 構建連接字符串
            if self.config.username and self.config.password:
                uri = f"mongodb://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}?authSource={self.config.auth_source}"
            else:
                uri = f"mongodb://{self.config.host}:{self.config.port}/{self.config.database}"
            
            # 創建客戶端
            self._client = MongoClient(
                uri,
                serverSelectionTimeoutMS=self.config.timeout_ms,
                maxPoolSize=self.config.max_pool_size
            )
            
            # 測試連接
            self._client.admin.command('ping')
            
            # 獲取數據庫
            self._db = self._client[self.config.database]
            
            self.logger.info(f"已連接到 MongoDB: {self.config.host}:{self.config.port}")
        
        except ConnectionFailure as e:
            self.logger.error(f"MongoDB 連接失敗: {str(e)}")
            raise
    
    def _get_collection(self, collection: str) -> Collection:
        """
        獲取集合
        
        Args:
            collection: 集合名稱
            
        Returns:
            MongoDB 集合對象
        """
        if not self._db:
            raise ConnectionFailure("MongoDB 未連接")
        
        return self._db[collection]
    
    def save_document(self, data: Dict, collection: str) -> bool:
        """
        保存文檔
        
        Args:
            data: 文檔數據
            collection: 集合名稱
            
        Returns:
            是否成功保存
        """
        try:
            # 添加時間戳
            if self.config.timestamp_field not in data:
                data[self.config.timestamp_field] = datetime.now()
            
            # 獲取集合
            coll = self._get_collection(collection)
            
            # 插入文檔
            result = coll.insert_one(data)
            
            self.logger.debug(f"已保存文檔到集合 {collection}: {result.inserted_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"保存文檔失敗: {str(e)}")
            return False
    
    def save_documents(self, data_list: List[Dict], collection: str) -> bool:
        """
        批量保存文檔
        
        Args:
            data_list: 文檔數據列表
            collection: 集合名稱
            
        Returns:
            是否成功保存
        """
        try:
            if not data_list:
                self.logger.warning("沒有數據需要保存")
                return False
            
            # 添加時間戳
            now = datetime.now()
            for data in data_list:
                if self.config.timestamp_field not in data:
                    data[self.config.timestamp_field] = now
            
            # 獲取集合
            coll = self._get_collection(collection)
            
            # 插入文檔
            result = coll.insert_many(data_list)
            
            self.logger.debug(f"已批量保存 {len(result.inserted_ids)} 個文檔到集合 {collection}")
            return True
        
        except Exception as e:
            self.logger.error(f"批量保存文檔失敗: {str(e)}")
            return False
    
    def update_document(self, query: Dict, update: Dict, collection: str, upsert: bool = False) -> bool:
        """
        更新文檔
        
        Args:
            query: 查詢條件
            update: 更新內容
            collection: 集合名稱
            upsert: 不存在時是否插入
            
        Returns:
            是否成功更新
        """
        try:
            # 獲取集合
            coll = self._get_collection(collection)
            
            # 更新文檔
            result = coll.update_one(query, {"$set": update}, upsert=upsert)
            
            self.logger.debug(f"已更新文檔: 匹配 {result.matched_count} 個，修改 {result.modified_count} 個")
            return True
        
        except Exception as e:
            self.logger.error(f"更新文檔失敗: {str(e)}")
            return False
    
    def delete_document(self, query: Dict, collection: str) -> bool:
        """
        刪除文檔
        
        Args:
            query: 查詢條件
            collection: 集合名稱
            
        Returns:
            是否成功刪除
        """
        try:
            # 獲取集合
            coll = self._get_collection(collection)
            
            # 刪除文檔
            result = coll.delete_many(query)
            
            self.logger.debug(f"已刪除 {result.deleted_count} 個文檔")
            return True
        
        except Exception as e:
            self.logger.error(f"刪除文檔失敗: {str(e)}")
            return False
    
    def find_documents(self, query: Dict, collection: str, projection: Optional[Dict] = None, 
                      sort: Optional[List[tuple]] = None, limit: Optional[int] = None) -> List[Dict]:
        """
        查詢文檔
        
        Args:
            query: 查詢條件
            collection: 集合名稱
            projection: 投影條件
            sort: 排序條件
            limit: 限制數量
            
        Returns:
            文檔列表
        """
        try:
            # 獲取集合
            coll = self._get_collection(collection)
            
            # 構建查詢
            cursor = coll.find(query, projection)
            
            # 添加排序
            if sort:
                cursor = cursor.sort(sort)
            
            # 添加限制
            if limit:
                cursor = cursor.limit(limit)
            
            # 執行查詢
            documents = list(cursor)
            
            self.logger.debug(f"已查詢到 {len(documents)} 個文檔")
            return documents
        
        except Exception as e:
            self.logger.error(f"查詢文檔失敗: {str(e)}")
            return []
    
    def count_documents(self, query: Dict, collection: str) -> int:
        """
        統計文檔數量
        
        Args:
            query: 查詢條件
            collection: 集合名稱
            
        Returns:
            文檔數量
        """
        try:
            # 獲取集合
            coll = self._get_collection(collection)
            
            # 統計數量
            count = coll.count_documents(query)
            
            self.logger.debug(f"集合 {collection} 中符合條件的文檔數量: {count}")
            return count
        
        except Exception as e:
            self.logger.error(f"統計文檔數量失敗: {str(e)}")
            return 0
    
    def create_index(self, collection: str, keys: List[tuple], unique: bool = False) -> bool:
        """
        創建索引
        
        Args:
            collection: 集合名稱
            keys: 索引鍵列表
            unique: 是否唯一索引
            
        Returns:
            是否成功創建
        """
        try:
            # 獲取集合
            coll = self._get_collection(collection)
            
            # 創建索引
            coll.create_index(keys, unique=unique)
            
            self.logger.debug(f"已在集合 {collection} 上創建索引: {keys}")
            return True
        
        except Exception as e:
            self.logger.error(f"創建索引失敗: {str(e)}")
            return False
    
    def get_collections(self) -> List[str]:
        """
        獲取所有集合名稱
        
        Returns:
            集合名稱列表
        """
        try:
            if not self._db:
                raise ConnectionFailure("MongoDB 未連接")
            
            # 獲取集合列表
            collections = self._db.list_collection_names()
            
            self.logger.debug(f"已獲取集合列表: {len(collections)} 個")
            return collections
        
        except Exception as e:
            self.logger.error(f"獲取集合列表失敗: {str(e)}")
            return []
    
    def drop_collection(self, collection: str) -> bool:
        """
        刪除集合
        
        Args:
            collection: 集合名稱
            
        Returns:
            是否成功刪除
        """
        try:
            if not self._db:
                raise ConnectionFailure("MongoDB 未連接")
            
            # 刪除集合
            self._db.drop_collection(collection)
            
            self.logger.debug(f"已刪除集合: {collection}")
            return True
        
        except Exception as e:
            self.logger.error(f"刪除集合失敗: {str(e)}")
            return False
    
    def get_collection_info(self, collection: str) -> Optional[Dict]:
        """
        獲取集合信息
        
        Args:
            collection: 集合名稱
            
        Returns:
            集合信息字典，失敗時返回None
        """
        try:
            if not self._db:
                raise ConnectionFailure("MongoDB 未連接")
            
            # 獲取集合信息
            info = self._db.command("collstats", collection)
            
            self.logger.debug(f"已獲取集合信息: {collection}")
            return info
        
        except Exception as e:
            self.logger.error(f"獲取集合信息失敗: {str(e)}")
            return None
    
    def close(self) -> None:
        """關閉數據庫連接"""
        try:
            if self._client:
                self._client.close()
                self._client = None
                self._db = None
                
                self.logger.info("已關閉 MongoDB 連接")
        
        except Exception as e:
            self.logger.error(f"關閉 MongoDB 連接失敗: {str(e)}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
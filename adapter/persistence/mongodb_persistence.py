#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MongoDB 持久化實現
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError
from .base import BasePersistence
from ..core.exceptions import (
    ConnectionError, 
    AuthenticationError,
    DatabaseError,
    ValidationError
)

T = TypeVar('T')

class MongoDBPersistence(BasePersistence[T]):
    """MongoDB 持久化實現"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化持久化
        
        Args:
            config: 配置資訊
        """
        self.config = config
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.collection: Optional[Collection] = None
        
    async def connect(self) -> None:
        """
        建立資料庫連接
        
        Raises:
            ConnectionError: 連接錯誤
            AuthenticationError: 認證錯誤
        """
        try:
            # 建立連接
            self.client = MongoClient(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", 27017),
                username=self.config.get("username"),
                password=self.config.get("password"),
                authSource=self.config.get("auth_source", "admin"),
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=10
            )
            
            # 測試連接
            self.client.server_info()
            
            # 選擇資料庫
            self.db = self.client[self.config.get("database", "momoshop")]
            
            # 選擇集合
            self.collection = self.db[self.config.get("collection", "products")]
            
            # 創建預設索引
            await self._create_default_indexes()
            
        except PyMongoError as e:
            if "Authentication failed" in str(e):
                raise AuthenticationError("MongoDB 認證失敗")
            raise ConnectionError(f"連接 MongoDB 失敗: {str(e)}")
            
    async def disconnect(self) -> None:
        """關閉資料庫連接"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self.collection = None
            
    async def _create_default_indexes(self) -> None:
        """創建預設索引"""
        if not self.collection:
            return
            
        try:
            # 創建時間戳索引
            await self.create_index([("created_at", -1)])
            await self.create_index([("updated_at", -1)])
            
            # 創建產品相關索引
            await self.create_index([("product_id", 1)], unique=True)
            await self.create_index([("category", 1)])
            await self.create_index([("brand", 1)])
            await self.create_index([("price", 1)])
            
        except PyMongoError as e:
            raise DatabaseError(f"創建預設索引失敗: {str(e)}")
            
    async def save(self, data: T) -> str:
        """
        保存單筆資料
        
        Args:
            data: 要保存的資料
            
        Returns:
            str: 資料 ID
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            # 添加時間戳
            if isinstance(data, dict):
                data["created_at"] = datetime.now()
                data["updated_at"] = datetime.now()
                
            # 插入資料
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
            
        except PyMongoError as e:
            raise DatabaseError(f"保存資料失敗: {str(e)}")
            
    async def save_many(self, data_list: List[T]) -> List[str]:
        """
        保存多筆資料
        
        Args:
            data_list: 要保存的資料列表
            
        Returns:
            List[str]: 資料 ID 列表
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            # 添加時間戳
            now = datetime.now()
            for data in data_list:
                if isinstance(data, dict):
                    data["created_at"] = now
                    data["updated_at"] = now
                
            # 插入資料
            result = self.collection.insert_many(data_list)
            return [str(id) for id in result.inserted_ids]
            
        except PyMongoError as e:
            raise DatabaseError(f"批量保存資料失敗: {str(e)}")
            
    async def update(self, id: str, data: T) -> bool:
        """
        更新資料
        
        Args:
            id: 資料 ID
            data: 要更新的資料
            
        Returns:
            bool: 是否更新成功
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            # 添加更新時間
            if isinstance(data, dict):
                data["updated_at"] = datetime.now()
                
            # 更新資料
            result = self.collection.update_one(
                {"_id": id},
                {"$set": data}
            )
            return result.modified_count > 0
            
        except PyMongoError as e:
            raise DatabaseError(f"更新資料失敗: {str(e)}")
            
    async def update_many(self, query: Dict[str, Any], data: Dict[str, Any]) -> int:
        """
        批量更新資料
        
        Args:
            query: 查詢條件
            data: 要更新的資料
            
        Returns:
            int: 更新的資料數量
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            # 添加更新時間
            data["updated_at"] = datetime.now()
            
            # 更新資料
            result = self.collection.update_many(
                query,
                {"$set": data}
            )
            return result.modified_count
            
        except PyMongoError as e:
            raise DatabaseError(f"批量更新資料失敗: {str(e)}")
            
    async def delete(self, id: str) -> bool:
        """
        刪除資料
        
        Args:
            id: 資料 ID
            
        Returns:
            bool: 是否刪除成功
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            # 刪除資料
            result = self.collection.delete_one({"_id": id})
            return result.deleted_count > 0
            
        except PyMongoError as e:
            raise DatabaseError(f"刪除資料失敗: {str(e)}")
            
    async def delete_many(self, query: Dict[str, Any]) -> int:
        """
        批量刪除資料
        
        Args:
            query: 查詢條件
            
        Returns:
            int: 刪除的資料數量
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            # 刪除資料
            result = self.collection.delete_many(query)
            return result.deleted_count
            
        except PyMongoError as e:
            raise DatabaseError(f"批量刪除資料失敗: {str(e)}")
            
    async def find_by_id(self, id: str) -> Optional[T]:
        """
        根據 ID 查詢資料
        
        Args:
            id: 資料 ID
            
        Returns:
            Optional[T]: 查詢結果
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            # 查詢資料
            return self.collection.find_one({"_id": id})
            
        except PyMongoError as e:
            raise DatabaseError(f"查詢資料失敗: {str(e)}")
            
    async def find_one(self, query: Dict[str, Any]) -> Optional[T]:
        """
        查詢單筆資料
        
        Args:
            query: 查詢條件
            
        Returns:
            Optional[T]: 查詢結果
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            # 查詢資料
            return self.collection.find_one(query)
            
        except PyMongoError as e:
            raise DatabaseError(f"查詢資料失敗: {str(e)}")
            
    async def find_many(self, query: Dict[str, Any], limit: int = 0, skip: int = 0) -> List[T]:
        """
        查詢多筆資料
        
        Args:
            query: 查詢條件
            limit: 限制數量
            skip: 跳過數量
            
        Returns:
            List[T]: 查詢結果列表
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            # 查詢資料
            cursor = self.collection.find(query)
            if skip > 0:
                cursor = cursor.skip(skip)
            if limit > 0:
                cursor = cursor.limit(limit)
            return list(cursor)
            
        except PyMongoError as e:
            raise DatabaseError(f"批量查詢資料失敗: {str(e)}")
            
    async def count(self, query: Dict[str, Any] = None) -> int:
        """
        計算資料數量
        
        Args:
            query: 查詢條件
            
        Returns:
            int: 資料數量
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            # 計算數量
            return self.collection.count_documents(query or {})
            
        except PyMongoError as e:
            raise DatabaseError(f"計算資料數量失敗: {str(e)}")
            
    async def create_index(self, keys: List[tuple], unique: bool = False) -> str:
        """
        創建索引
        
        Args:
            keys: 索引欄位列表
            unique: 是否為唯一索引
            
        Returns:
            str: 索引名稱
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            # 創建索引
            return self.collection.create_index(keys, unique=unique)
            
        except PyMongoError as e:
            raise DatabaseError(f"創建索引失敗: {str(e)}")
            
    async def drop_index(self, name: str) -> None:
        """
        刪除索引
        
        Args:
            name: 索引名稱
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            # 刪除索引
            self.collection.drop_index(name)
            
        except PyMongoError as e:
            raise DatabaseError(f"刪除索引失敗: {str(e)}")
            
    async def get_indexes(self) -> List[Dict[str, Any]]:
        """
        獲取所有索引
        
        Returns:
            List[Dict[str, Any]]: 索引列表
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            return list(self.collection.list_indexes())
            
        except PyMongoError as e:
            raise DatabaseError(f"獲取索引失敗: {str(e)}")
            
    async def drop_all_indexes(self) -> None:
        """
        刪除所有索引
        
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            self.collection.drop_indexes()
            
        except PyMongoError as e:
            raise DatabaseError(f"刪除所有索引失敗: {str(e)}")
            
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        執行聚合操作
        
        Args:
            pipeline: 聚合管道
            
        Returns:
            List[Dict[str, Any]]: 聚合結果
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            return list(self.collection.aggregate(pipeline))
            
        except PyMongoError as e:
            raise DatabaseError(f"執行聚合操作失敗: {str(e)}")
            
    async def bulk_write(self, operations: List[Any]) -> Dict[str, int]:
        """
        執行批量寫入操作
        
        Args:
            operations: 寫入操作列表
            
        Returns:
            Dict[str, int]: 操作結果統計
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        try:
            if not self.collection:
                raise DatabaseError("資料庫未連接")
                
            result = self.collection.bulk_write(operations)
            return {
                "inserted": result.inserted_count,
                "matched": result.matched_count,
                "modified": result.modified_count,
                "deleted": result.deleted_count,
                "upserted": result.upserted_count
            }
            
        except PyMongoError as e:
            raise DatabaseError(f"執行批量寫入操作失敗: {str(e)}") 
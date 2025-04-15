#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MongoDB 適配器
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic
from ..persistence.mongodb_persistence import MongoDBPersistence
from ..core.exceptions import (
    ConnectionError,
    AuthenticationError,
    DatabaseError,
    ValidationError
)

T = TypeVar('T')

class MongoDBAdapter(Generic[T]):
    """MongoDB 適配器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化適配器
        
        Args:
            config: 配置資訊
        """
        self.config = config
        self.persistence = MongoDBPersistence[T](config)
        
    async def connect(self) -> None:
        """
        建立資料庫連接
        
        Raises:
            ConnectionError: 連接錯誤
            AuthenticationError: 認證錯誤
        """
        await self.persistence.connect()
        
    async def disconnect(self) -> None:
        """關閉資料庫連接"""
        await self.persistence.disconnect()
        
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
        return await self.persistence.save(data)
        
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
        return await self.persistence.save_many(data_list)
        
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
        return await self.persistence.update(id, data)
        
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
        return await self.persistence.update_many(query, data)
        
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
        return await self.persistence.delete(id)
        
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
        return await self.persistence.delete_many(query)
        
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
        return await self.persistence.find_by_id(id)
        
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
        return await self.persistence.find_one(query)
        
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
        return await self.persistence.find_many(query, limit, skip)
        
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
        return await self.persistence.count(query)
        
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
        return await self.persistence.create_index(keys, unique)
        
    async def drop_index(self, name: str) -> None:
        """
        刪除索引
        
        Args:
            name: 索引名稱
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        await self.persistence.drop_index(name) 
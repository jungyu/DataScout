#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
持久化基礎介面
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic

T = TypeVar('T')

class BasePersistence(ABC, Generic[T]):
    """持久化基礎介面"""
    
    @abstractmethod
    async def connect(self) -> None:
        """
        建立資料庫連接
        
        Raises:
            ConnectionError: 連接錯誤
            AuthenticationError: 認證錯誤
        """
        pass
        
    @abstractmethod
    async def disconnect(self) -> None:
        """關閉資料庫連接"""
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
    async def drop_index(self, name: str) -> None:
        """
        刪除索引
        
        Args:
            name: 索引名稱
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        pass
        
    @abstractmethod
    async def get_indexes(self) -> List[Dict[str, Any]]:
        """
        獲取所有索引
        
        Returns:
            List[Dict[str, Any]]: 索引列表
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        pass
        
    @abstractmethod
    async def drop_all_indexes(self) -> None:
        """
        刪除所有索引
        
        Raises:
            DatabaseError: 資料庫錯誤
        """
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
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
        pass 
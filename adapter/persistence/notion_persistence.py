#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notion 持久化實現
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic
from datetime import datetime
import asyncio
from notion_client import AsyncClient
from notion_client.errors import APIResponseError
from .base import BasePersistence
from ..core.exceptions import (
    ConnectionError,
    AuthenticationError,
    DatabaseError,
    ValidationError
)

T = TypeVar('T')

class NotionPersistence(BasePersistence[T]):
    """Notion 持久化實現"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化持久化
        
        Args:
            config: 配置資訊
        """
        self.config = config
        self.client: Optional[AsyncClient] = None
        self.database_id = config.get("database_id")
        if not self.database_id:
            raise ValidationError("必須提供 database_id")
            
    async def connect(self) -> None:
        """
        建立 Notion API 連接
        
        Raises:
            ConnectionError: 連接錯誤
            AuthenticationError: 認證錯誤
        """
        try:
            api_key = self.config.get("api_key")
            if not api_key:
                raise ValidationError("必須提供 api_key")
                
            self.client = AsyncClient(auth=api_key)
            
            # 測試連接
            await self.client.databases.retrieve(database_id=self.database_id)
            
        except APIResponseError as e:
            if e.code == "unauthorized":
                raise AuthenticationError("Notion API 認證失敗")
            raise ConnectionError(f"連接 Notion API 失敗: {str(e)}")
            
    async def disconnect(self) -> None:
        """關閉 Notion API 連接"""
        if self.client:
            await self.client.aclose()
            self.client = None
            
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
            if not self.client:
                raise DatabaseError("Notion API 未連接")
                
            # 轉換資料格式
            notion_data = self._convert_to_notion_format(data)
            
            # 創建頁面
            response = await self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=notion_data
            )
            return response["id"]
            
        except APIResponseError as e:
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
            if not self.client:
                raise DatabaseError("Notion API 未連接")
                
            # 並行處理所有保存操作
            tasks = [self.save(data) for data in data_list]
            return await asyncio.gather(*tasks)
            
        except APIResponseError as e:
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
            if not self.client:
                raise DatabaseError("Notion API 未連接")
                
            # 轉換資料格式
            notion_data = self._convert_to_notion_format(data)
            
            # 更新頁面
            await self.client.pages.update(
                page_id=id,
                properties=notion_data
            )
            return True
            
        except APIResponseError as e:
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
            if not self.client:
                raise DatabaseError("Notion API 未連接")
                
            # 查詢符合條件的頁面
            pages = await self.find_many(query)
            
            # 並行更新所有頁面
            tasks = [self.update(page["id"], data) for page in pages]
            results = await asyncio.gather(*tasks)
            
            return sum(1 for result in results if result)
            
        except APIResponseError as e:
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
            if not self.client:
                raise DatabaseError("Notion API 未連接")
                
            # 將頁面標記為已存檔（Notion 不支援直接刪除）
            await self.client.pages.update(
                page_id=id,
                archived=True
            )
            return True
            
        except APIResponseError as e:
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
            if not self.client:
                raise DatabaseError("Notion API 未連接")
                
            # 查詢符合條件的頁面
            pages = await self.find_many(query)
            
            # 並行刪除所有頁面
            tasks = [self.delete(page["id"]) for page in pages]
            results = await asyncio.gather(*tasks)
            
            return sum(1 for result in results if result)
            
        except APIResponseError as e:
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
            if not self.client:
                raise DatabaseError("Notion API 未連接")
                
            # 查詢頁面
            response = await self.client.pages.retrieve(page_id=id)
            return self._convert_from_notion_format(response)
            
        except APIResponseError as e:
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
            if not self.client:
                raise DatabaseError("Notion API 未連接")
                
            # 查詢資料庫
            response = await self.client.databases.query(
                database_id=self.database_id,
                filter=self._convert_query_to_notion(query),
                page_size=1
            )
            
            if not response["results"]:
                return None
                
            return self._convert_from_notion_format(response["results"][0])
            
        except APIResponseError as e:
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
            if not self.client:
                raise DatabaseError("Notion API 未連接")
                
            # 查詢資料庫
            response = await self.client.databases.query(
                database_id=self.database_id,
                filter=self._convert_query_to_notion(query),
                page_size=limit if limit > 0 else 100,
                start_cursor=skip if skip > 0 else None
            )
            
            return [
                self._convert_from_notion_format(page)
                for page in response["results"]
            ]
            
        except APIResponseError as e:
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
            if not self.client:
                raise DatabaseError("Notion API 未連接")
                
            # 查詢資料庫
            response = await self.client.databases.query(
                database_id=self.database_id,
                filter=self._convert_query_to_notion(query) if query else None,
                page_size=1
            )
            
            return response["total"]
            
        except APIResponseError as e:
            raise DatabaseError(f"計算資料數量失敗: {str(e)}")
            
    async def create_index(self, keys: List[tuple], unique: bool = False) -> str:
        """
        創建索引（Notion 不支援自定義索引）
        
        Args:
            keys: 索引欄位列表
            unique: 是否為唯一索引
            
        Returns:
            str: 索引名稱
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        raise DatabaseError("Notion 不支援自定義索引")
        
    async def drop_index(self, name: str) -> None:
        """
        刪除索引（Notion 不支援自定義索引）
        
        Args:
            name: 索引名稱
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        raise DatabaseError("Notion 不支援自定義索引")
        
    async def get_indexes(self) -> List[Dict[str, Any]]:
        """
        獲取所有索引（Notion 不支援自定義索引）
        
        Returns:
            List[Dict[str, Any]]: 索引列表
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        raise DatabaseError("Notion 不支援自定義索引")
        
    async def drop_all_indexes(self) -> None:
        """
        刪除所有索引（Notion 不支援自定義索引）
        
        Raises:
            DatabaseError: 資料庫錯誤
        """
        raise DatabaseError("Notion 不支援自定義索引")
        
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        執行聚合操作（Notion 不支援聚合操作）
        
        Args:
            pipeline: 聚合管道
            
        Returns:
            List[Dict[str, Any]]: 聚合結果
            
        Raises:
            DatabaseError: 資料庫錯誤
        """
        raise DatabaseError("Notion 不支援聚合操作")
        
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
            if not self.client:
                raise DatabaseError("Notion API 未連接")
                
            results = {
                "inserted": 0,
                "matched": 0,
                "modified": 0,
                "deleted": 0,
                "upserted": 0
            }
            
            for operation in operations:
                if operation["type"] == "insert":
                    await self.save(operation["data"])
                    results["inserted"] += 1
                elif operation["type"] == "update":
                    await self.update(operation["id"], operation["data"])
                    results["modified"] += 1
                elif operation["type"] == "delete":
                    await self.delete(operation["id"])
                    results["deleted"] += 1
                    
            return results
            
        except APIResponseError as e:
            raise DatabaseError(f"執行批量寫入操作失敗: {str(e)}")
            
    def _convert_to_notion_format(self, data: T) -> Dict[str, Any]:
        """
        將資料轉換為 Notion 格式
        
        Args:
            data: 要轉換的資料
            
        Returns:
            Dict[str, Any]: Notion 格式的資料
        """
        if not isinstance(data, dict):
            raise ValidationError("資料必須是字典類型")
            
        notion_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                notion_data[key] = {"title": [{"text": {"content": value}}]}
            elif isinstance(value, int):
                notion_data[key] = {"number": value}
            elif isinstance(value, float):
                notion_data[key] = {"number": value}
            elif isinstance(value, bool):
                notion_data[key] = {"checkbox": value}
            elif isinstance(value, datetime):
                notion_data[key] = {"date": {"start": value.isoformat()}}
            elif isinstance(value, list):
                notion_data[key] = {"multi_select": [{"name": str(item)} for item in value]}
            else:
                notion_data[key] = {"rich_text": [{"text": {"content": str(value)}}]}
                
        return notion_data
        
    def _convert_from_notion_format(self, data: Dict[str, Any]) -> T:
        """
        將 Notion 格式轉換為資料
        
        Args:
            data: Notion 格式的資料
            
        Returns:
            T: 轉換後的資料
        """
        result = {}
        for key, value in data["properties"].items():
            prop_type = value["type"]
            if prop_type == "title":
                result[key] = value["title"][0]["text"]["content"] if value["title"] else ""
            elif prop_type == "rich_text":
                result[key] = value["rich_text"][0]["text"]["content"] if value["rich_text"] else ""
            elif prop_type == "number":
                result[key] = value["number"]
            elif prop_type == "checkbox":
                result[key] = value["checkbox"]
            elif prop_type == "date":
                result[key] = datetime.fromisoformat(value["date"]["start"]) if value["date"] else None
            elif prop_type == "multi_select":
                result[key] = [item["name"] for item in value["multi_select"]]
            else:
                result[key] = str(value)
                
        return result
        
    def _convert_query_to_notion(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        將查詢條件轉換為 Notion 格式
        
        Args:
            query: 查詢條件
            
        Returns:
            Dict[str, Any]: Notion 格式的查詢條件
        """
        notion_query = {"and": []}
        
        for key, value in query.items():
            if isinstance(value, (str, int, float, bool)):
                notion_query["and"].append({
                    "property": key,
                    "rich_text": {
                        "equals": str(value)
                    }
                })
            elif isinstance(value, list):
                notion_query["and"].append({
                    "property": key,
                    "multi_select": {
                        "contains": value[0]
                    }
                })
            elif isinstance(value, dict):
                operator = value.get("operator", "equals")
                if operator == "contains":
                    notion_query["and"].append({
                        "property": key,
                        "rich_text": {
                            "contains": str(value["value"])
                        }
                    })
                elif operator == "starts_with":
                    notion_query["and"].append({
                        "property": key,
                        "rich_text": {
                            "starts_with": str(value["value"])
                        }
                    })
                elif operator == "ends_with":
                    notion_query["and"].append({
                        "property": key,
                        "rich_text": {
                            "ends_with": str(value["value"])
                        }
                    })
                    
        return notion_query 
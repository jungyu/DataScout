#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notion 存儲處理器模組
實現基於 Notion API 的數據存儲功能
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from notion_client import Client
from notion_client.errors import APIResponseError

from .base_handler import StorageHandler
from ..config.storage_config import StorageConfig
from ..utils.storage_utils import StorageUtils


class NotionHandler(StorageHandler):
    """Notion 存儲處理器"""
    
    def __init__(self, config: StorageConfig):
        """
        初始化 Notion 存儲處理器
        
        Args:
            config: 存儲配置
        """
        super().__init__(config)
        self.storage_utils = StorageUtils()
        self.client = None
        self.database_id = None
        self._connect()
    
    def _connect(self) -> None:
        """連接 Notion API"""
        try:
            # 獲取 API 令牌
            token = self.config.get_notion_token()
            
            # 創建客戶端
            self.client = Client(auth=token)
            
            # 獲取數據庫 ID
            self.database_id = self.config.notion_database_id
            
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
            
            # 轉換數據格式
            notion_data = self._convert_to_notion(data)
            
            # 創建頁面
            result = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=notion_data
            )
            
            # 更新狀態
            success = result is not None
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
            
            # 轉換數據格式
            notion_data_list = [self._convert_to_notion(data) for data in data_list]
            
            # 批量創建頁面
            results = []
            for notion_data in notion_data_list:
                result = self.client.pages.create(
                    parent={"database_id": self.database_id},
                    properties=notion_data
                )
                results.append(result)
            
            # 更新狀態
            success = len(results) == len(data_list)
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
            notion_query = self._convert_query_to_notion(query) if query else {}
            
            # 查詢頁面
            response = self.client.databases.query(
                database_id=self.database_id,
                filter=notion_query
            )
            
            # 轉換數據格式
            data = [self._convert_from_notion(page) for page in response.get("results", [])]
            
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
            notion_query = self._convert_query_to_notion(query)
            
            # 查詢頁面
            response = self.client.databases.query(
                database_id=self.database_id,
                filter=notion_query
            )
            
            # 刪除頁面
            success = True
            for page in response.get("results", []):
                try:
                    self.client.pages.update(
                        page_id=page["id"],
                        archived=True
                    )
                except:
                    success = False
            
            # 更新狀態
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
            # 查詢所有頁面
            response = self.client.databases.query(
                database_id=self.database_id
            )
            
            # 刪除頁面
            success = True
            for page in response.get("results", []):
                try:
                    self.client.pages.update(
                        page_id=page["id"],
                        archived=True
                    )
                except:
                    success = False
            
            # 更新狀態
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
            notion_query = self._convert_query_to_notion(query) if query else {}
            
            # 查詢頁面
            response = self.client.databases.query(
                database_id=self.database_id,
                filter=notion_query
            )
            
            # 更新狀態
            self._update_status("get_data_count", True)
            return len(response.get("results", []))
            
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
            
            # 創建備份數據庫
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_database = self.client.databases.create(
                parent={"type": "page_id", "page_id": self.config.notion_parent_page_id},
                title=[{"type": "text", "text": {"content": backup_name}}],
                properties=self._get_database_properties()
            )
            
            # 複製數據
            data = self.load_data()
            success = self.save_batch(data)
            
            # 清理舊備份
            self._cleanup_old_backups()
            
            # 更新狀態
            self._update_status("create_backup", success)
            return success
            
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
            # 清空當前數據
            self.clear_data()
            
            # 加載備份數據
            backup_database = self.client.databases.retrieve(database_id=backup_id)
            if not backup_database:
                return False
            
            # 查詢備份頁面
            response = self.client.databases.query(
                database_id=backup_id
            )
            
            # 轉換數據格式
            data = [self._convert_from_notion(page) for page in response.get("results", [])]
            
            # 保存數據
            success = self.save_batch(data)
            
            # 更新狀態
            self._update_status("restore_backup", success)
            return success
            
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
            # 查詢備份數據庫
            response = self.client.search(
                query="backup_",
                filter={"property": "object", "value": "database"}
            )
            
            # 過濾備份數據庫
            backups = []
            for result in response.get("results", []):
                if result["object"] == "database":
                    backups.append(result["id"])
            
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
            # 刪除備份數據庫
            self.client.databases.update(
                database_id=backup_id,
                archived=True
            )
            
            # 更新狀態
            self._update_status("delete_backup", True)
            return True
            
        except Exception as e:
            self._update_status("delete_backup", False, e)
            return False
    
    def _convert_to_notion(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        轉換數據為 Notion 格式
        
        Args:
            data: 原始數據
            
        Returns:
            Dict[str, Any]: Notion 格式的數據
        """
        notion_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                notion_data[key] = {"title": [{"text": {"content": value}}]}
            elif isinstance(value, (int, float)):
                notion_data[key] = {"number": value}
            elif isinstance(value, bool):
                notion_data[key] = {"checkbox": value}
            elif isinstance(value, datetime):
                notion_data[key] = {"date": {"start": value.isoformat()}}
            else:
                notion_data[key] = {"rich_text": [{"text": {"content": str(value)}}]}
        return notion_data
    
    def _convert_from_notion(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """
        從 Notion 格式轉換數據
        
        Args:
            page: Notion 頁面
            
        Returns:
            Dict[str, Any]: 轉換後的數據
        """
        data = {}
        for key, value in page["properties"].items():
            prop_type = value["type"]
            if prop_type == "title":
                data[key] = value["title"][0]["text"]["content"] if value["title"] else ""
            elif prop_type == "rich_text":
                data[key] = value["rich_text"][0]["text"]["content"] if value["rich_text"] else ""
            elif prop_type == "number":
                data[key] = value["number"]
            elif prop_type == "checkbox":
                data[key] = value["checkbox"]
            elif prop_type == "date":
                data[key] = datetime.fromisoformat(value["date"]["start"]) if value["date"] else None
        return data
    
    def _convert_query_to_notion(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        轉換查詢條件為 Notion 格式
        
        Args:
            query: 原始查詢條件
            
        Returns:
            Dict[str, Any]: Notion 格式的查詢條件
        """
        notion_query = {"and": []}
        for key, value in query.items():
            if isinstance(value, str):
                notion_query["and"].append({
                    "property": key,
                    "title": {"equals": value}
                })
            elif isinstance(value, (int, float)):
                notion_query["and"].append({
                    "property": key,
                    "number": {"equals": value}
                })
            elif isinstance(value, bool):
                notion_query["and"].append({
                    "property": key,
                    "checkbox": {"equals": value}
                })
            elif isinstance(value, datetime):
                notion_query["and"].append({
                    "property": key,
                    "date": {"equals": value.isoformat()}
                })
        return notion_query
    
    def _get_database_properties(self) -> Dict[str, Any]:
        """
        獲取數據庫屬性
        
        Returns:
            Dict[str, Any]: 數據庫屬性
        """
        return {
            "Name": {"title": {}},
            "Content": {"rich_text": {}},
            "Created": {"date": {}},
            "Updated": {"date": {}}
        }
    
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
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        pass 
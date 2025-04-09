#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notion 存儲處理器模組
實現 Notion 數據庫存儲功能
"""

import time
from typing import Dict, List, Optional, Any
from notion_client import Client
from ..config.storage_config import StorageConfig
from .base_handler import StorageHandler


class NotionHandler(StorageHandler):
    """Notion 存儲處理器"""
    
    def __init__(self, config: StorageConfig):
        """初始化 Notion 存儲處理器"""
        super().__init__(config)
        self.client = self._connect()
        self.database_id = config.notion_database_id
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """保存單條數據"""
        try:
            # 添加時間戳
            if self.config.timestamp_field not in data:
                data[self.config.timestamp_field] = time.time()
            
            # 轉換為 Notion 屬性
            properties = self._convert_to_notion_properties(data)
            
            # 創建頁面
            self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            return True
            
        except Exception as e:
            print(f"保存數據失敗: {str(e)}")
            return False
    
    def save_batch(self, data_list: List[Dict[str, Any]]) -> bool:
        """批量保存數據"""
        try:
            for data in data_list:
                if not self.save_data(data):
                    return False
            return True
            
        except Exception as e:
            print(f"批量保存數據失敗: {str(e)}")
            return False
    
    def load_data(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """加載數據"""
        try:
            # 構建過濾條件
            filter_params = self._build_filter_params(query)
            
            # 查詢數據
            response = self.client.databases.query(
                database_id=self.database_id,
                filter=filter_params,
                page_size=self.config.notion_page_size
            )
            
            # 轉換結果
            return [self._convert_from_notion_page(page) for page in response["results"]]
            
        except Exception as e:
            print(f"加載數據失敗: {str(e)}")
            return []
    
    def delete_data(self, query: Dict[str, Any]) -> bool:
        """刪除數據"""
        try:
            # 查詢要刪除的頁面
            pages = self.load_data(query)
            
            # 刪除頁面
            for page in pages:
                self.client.pages.update(
                    page_id=page["id"],
                    archived=True
                )
            
            return True
            
        except Exception as e:
            print(f"刪除數據失敗: {str(e)}")
            return False
    
    def clear_data(self) -> bool:
        """清空數據"""
        try:
            # 查詢所有頁面
            pages = self.load_data()
            
            # 刪除所有頁面
            for page in pages:
                self.client.pages.update(
                    page_id=page["id"],
                    archived=True
                )
            
            return True
            
        except Exception as e:
            print(f"清空數據失敗: {str(e)}")
            return False
    
    def get_data_count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """獲取數據數量"""
        return len(self.load_data(query))
    
    def create_backup(self) -> bool:
        """創建備份"""
        try:
            # 獲取所有數據
            data = self.load_data()
            
            # 創建備份數據庫
            backup_database = self.client.databases.create(
                parent={"type": "page_id", "page_id": self.database_id},
                title=[{"type": "text", "text": {"content": f"Backup_{time.strftime('%Y%m%d_%H%M%S')}"}}],
                properties=self._get_database_properties()
            )
            
            # 保存到備份數據庫
            for item in data:
                properties = self._convert_to_notion_properties(item)
                self.client.pages.create(
                    parent={"database_id": backup_database["id"]},
                    properties=properties
                )
            
            return True
            
        except Exception as e:
            print(f"創建備份失敗: {str(e)}")
            return False
    
    def restore_backup(self, backup_id: str) -> bool:
        """恢復備份"""
        try:
            # 清空當前數據庫
            self.clear_data()
            
            # 從備份數據庫加載數據
            backup_data = self.load_data({"database_id": backup_id})
            
            # 恢復數據
            for item in backup_data:
                self.save_data(item)
            
            return True
            
        except Exception as e:
            print(f"恢復備份失敗: {str(e)}")
            return False
    
    def list_backups(self) -> List[str]:
        """列出所有備份"""
        try:
            # 查詢備份數據庫
            response = self.client.search(
                query="Backup_",
                filter={"property": "object", "value": "database"}
            )
            
            # 提取備份 ID
            return [page["id"] for page in response["results"]]
            
        except Exception as e:
            print(f"列出備份失敗: {str(e)}")
            return []
    
    def delete_backup(self, backup_id: str) -> bool:
        """刪除備份"""
        try:
            # 刪除備份數據庫
            self.client.databases.update(
                database_id=backup_id,
                archived=True
            )
            
            return True
            
        except Exception as e:
            print(f"刪除備份失敗: {str(e)}")
            return False
    
    def _connect(self) -> Client:
        """連接 Notion"""
        try:
            return Client(auth=self.config.notion_token)
        except Exception as e:
            raise ConnectionError(f"連接 Notion 失敗: {str(e)}")
    
    def _convert_to_notion_properties(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """轉換為 Notion 屬性"""
        properties = {}
        for key, value in data.items():
            if isinstance(value, str):
                properties[key] = {"rich_text": [{"text": {"content": value}}]}
            elif isinstance(value, (int, float)):
                properties[key] = {"number": value}
            elif isinstance(value, bool):
                properties[key] = {"checkbox": value}
            elif isinstance(value, list):
                properties[key] = {"multi_select": [{"name": str(item)} for item in value]}
            else:
                properties[key] = {"rich_text": [{"text": {"content": str(value)}}]}
        return properties
    
    def _convert_from_notion_page(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """從 Notion 頁面轉換"""
        data = {}
        for key, value in page["properties"].items():
            if value["type"] == "rich_text":
                data[key] = value["rich_text"][0]["text"]["content"] if value["rich_text"] else ""
            elif value["type"] == "number":
                data[key] = value["number"]
            elif value["type"] == "checkbox":
                data[key] = value["checkbox"]
            elif value["type"] == "multi_select":
                data[key] = [item["name"] for item in value["multi_select"]]
        data["id"] = page["id"]
        return data
    
    def _build_filter_params(self, query: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """構建過濾參數"""
        if query is None:
            return {}
        
        filter_params = {"and": []}
        for key, value in query.items():
            if isinstance(value, str):
                filter_params["and"].append({
                    "property": key,
                    "rich_text": {"equals": value}
                })
            elif isinstance(value, (int, float)):
                filter_params["and"].append({
                    "property": key,
                    "number": {"equals": value}
                })
            elif isinstance(value, bool):
                filter_params["and"].append({
                    "property": key,
                    "checkbox": {"equals": value}
                })
            elif isinstance(value, list):
                filter_params["and"].append({
                    "property": key,
                    "multi_select": {"contains": str(value[0])}
                })
        
        return filter_params
    
    def _get_database_properties(self) -> Dict[str, Any]:
        """獲取數據庫屬性"""
        return {
            "Name": {"title": {}},
            "Content": {"rich_text": {}},
            "Number": {"number": {}},
            "Checkbox": {"checkbox": {}},
            "MultiSelect": {"multi_select": {}}
        }
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        pass 
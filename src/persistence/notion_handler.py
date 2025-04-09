#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notion 存儲模組

此模組提供 Notion 數據庫的存儲功能，支持頁面的增刪改查操作。
"""

import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
from notion_client import Client
from notion_client.errors import APIResponseError

@dataclass
class NotionConfig:
    """Notion 配置類"""
    token: str
    database_id: Optional[str] = None
    default_page_id: Optional[str] = None
    timeout: int = 30
    retry_count: int = 3
    retry_delay: int = 1
    timestamp_field: str = "timestamp"
    id_field: str = "id"
    title_field: str = "title"
    content_field: str = "content"
    url_field: str = "url"
    tags_field: str = "tags"
    status_field: str = "status"

class NotionHandler:
    """Notion 處理類"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化 Notion 處理器
        
        Args:
            config: 配置字典
        """
        self.logger = logging.getLogger(__name__)
        
        # 加載配置
        self.config = NotionConfig(**(config or {}))
        
        # 初始化客戶端
        self._client: Optional[Client] = None
        
        # 連接 Notion
        self._connect()
        
        self.logger.info("Notion 處理器初始化完成")
    
    def _connect(self) -> None:
        """建立 Notion 連接"""
        try:
            # 創建客戶端
            self._client = Client(auth=self.config.token)
            
            # 測試連接
            self._client.users.me()
            
            self.logger.info("已連接到 Notion")
        
        except Exception as e:
            self.logger.error(f"Notion 連接失敗: {str(e)}")
            raise
    
    def _convert_to_notion_properties(self, data: Dict) -> Dict:
        """
        將數據轉換為 Notion 屬性格式
        
        Args:
            data: 數據字典
            
        Returns:
            Notion 屬性字典
        """
        properties = {}
        
        for key, value in data.items():
            if value is None:
                continue
            
            if isinstance(value, str):
                properties[key] = {"rich_text": [{"text": {"content": value}}]}
            
            elif isinstance(value, bool):
                properties[key] = {"checkbox": value}
            
            elif isinstance(value, int):
                properties[key] = {"number": value}
            
            elif isinstance(value, float):
                properties[key] = {"number": value}
            
            elif isinstance(value, datetime):
                properties[key] = {"date": {"start": value.isoformat()}}
            
            elif isinstance(value, list):
                if all(isinstance(item, str) for item in value):
                    properties[key] = {"multi_select": [{"name": item} for item in value]}
                else:
                    properties[key] = {"rich_text": [{"text": {"content": str(value)}}]}
            
            elif isinstance(value, dict):
                properties[key] = {"rich_text": [{"text": {"content": str(value)}}]}
            
            else:
                properties[key] = {"rich_text": [{"text": {"content": str(value)}}]}
        
        return properties
    
    def _convert_from_notion_properties(self, properties: Dict) -> Dict:
        """
        將 Notion 屬性轉換為數據格式
        
        Args:
            properties: Notion 屬性字典
            
        Returns:
            數據字典
        """
        data = {}
        
        for key, value in properties.items():
            if not value:
                continue
            
            if "rich_text" in value:
                text = "".join(item["text"]["content"] for item in value["rich_text"])
                data[key] = text
            
            elif "checkbox" in value:
                data[key] = value["checkbox"]
            
            elif "number" in value:
                data[key] = value["number"]
            
            elif "date" in value:
                data[key] = datetime.fromisoformat(value["date"]["start"])
            
            elif "multi_select" in value:
                data[key] = [item["name"] for item in value["multi_select"]]
            
            elif "select" in value:
                data[key] = value["select"]["name"]
            
            else:
                data[key] = str(value)
        
        return data
    
    def create_page(self, data: Dict, parent_id: Optional[str] = None) -> Optional[str]:
        """
        創建頁面
        
        Args:
            data: 頁面數據
            parent_id: 父頁面ID，為None時使用默認數據庫
            
        Returns:
            頁面ID，失敗時返回None
        """
        try:
            # 添加時間戳
            if self.config.timestamp_field not in data:
                data[self.config.timestamp_field] = datetime.now()
            
            # 轉換屬性
            properties = self._convert_to_notion_properties(data)
            
            # 確定父頁面
            if parent_id is None:
                if self.config.database_id:
                    parent = {"database_id": self.config.database_id}
                else:
                    raise ValueError("未指定父頁面或數據庫")
            else:
                parent = {"page_id": parent_id}
            
            # 創建頁面
            page = self._client.pages.create(
                parent=parent,
                properties=properties
            )
            
            self.logger.debug(f"已創建頁面: {page['id']}")
            return page["id"]
        
        except Exception as e:
            self.logger.error(f"創建頁面失敗: {str(e)}")
            return None
    
    def update_page(self, page_id: str, data: Dict) -> bool:
        """
        更新頁面
        
        Args:
            page_id: 頁面ID
            data: 更新數據
            
        Returns:
            是否成功更新
        """
        try:
            # 轉換屬性
            properties = self._convert_to_notion_properties(data)
            
            # 更新頁面
            self._client.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            self.logger.debug(f"已更新頁面: {page_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"更新頁面失敗: {str(e)}")
            return False
    
    def delete_page(self, page_id: str) -> bool:
        """
        刪除頁面
        
        Args:
            page_id: 頁面ID
            
        Returns:
            是否成功刪除
        """
        try:
            # 刪除頁面
            self._client.pages.update(
                page_id=page_id,
                archived=True
            )
            
            self.logger.debug(f"已刪除頁面: {page_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"刪除頁面失敗: {str(e)}")
            return False
    
    def get_page(self, page_id: str) -> Optional[Dict]:
        """
        獲取頁面
        
        Args:
            page_id: 頁面ID
            
        Returns:
            頁面數據，失敗時返回None
        """
        try:
            # 獲取頁面
            page = self._client.pages.retrieve(page_id=page_id)
            
            # 轉換屬性
            data = self._convert_from_notion_properties(page["properties"])
            
            # 添加頁面ID
            data["id"] = page["id"]
            
            self.logger.debug(f"已獲取頁面: {page_id}")
            return data
        
        except Exception as e:
            self.logger.error(f"獲取頁面失敗: {str(e)}")
            return None
    
    def query_database(self, database_id: str, filter_query: Optional[Dict] = None, 
                      sorts: Optional[List[Dict]] = None, page_size: int = 100) -> List[Dict]:
        """
        查詢數據庫
        
        Args:
            database_id: 數據庫ID
            filter_query: 過濾條件
            sorts: 排序條件
            page_size: 每頁數量
            
        Returns:
            頁面數據列表
        """
        try:
            # 構建查詢
            query = {
                "page_size": page_size
            }
            
            if filter_query:
                query["filter"] = filter_query
            
            if sorts:
                query["sorts"] = sorts
            
            # 執行查詢
            results = self._client.databases.query(**query)
            
            # 轉換結果
            pages = []
            for page in results["results"]:
                # 轉換屬性
                data = self._convert_from_notion_properties(page["properties"])
                
                # 添加頁面ID
                data["id"] = page["id"]
                
                pages.append(data)
            
            self.logger.debug(f"已查詢數據庫 {database_id}: {len(pages)} 個頁面")
            return pages
        
        except Exception as e:
            self.logger.error(f"查詢數據庫失敗: {str(e)}")
            return []
    
    def append_block(self, page_id: str, block_type: str, content: Union[str, List[str]]) -> bool:
        """
        添加區塊
        
        Args:
            page_id: 頁面ID
            block_type: 區塊類型
            content: 區塊內容
            
        Returns:
            是否成功添加
        """
        try:
            # 構建區塊
            if block_type == "paragraph":
                block = {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            
            elif block_type == "heading_1":
                block = {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            
            elif block_type == "heading_2":
                block = {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            
            elif block_type == "heading_3":
                block = {
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            
            elif block_type == "bulleted_list_item":
                block = {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            
            elif block_type == "numbered_list_item":
                block = {
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            
            elif block_type == "code":
                block = {
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            
            elif block_type == "quote":
                block = {
                    "object": "block",
                    "type": "quote",
                    "quote": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            
            elif block_type == "callout":
                block = {
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            
            else:
                raise ValueError(f"不支持的區塊類型: {block_type}")
            
            # 添加區塊
            self._client.blocks.children.append(
                block_id=page_id,
                children=[block]
            )
            
            self.logger.debug(f"已在頁面 {page_id} 添加區塊: {block_type}")
            return True
        
        except Exception as e:
            self.logger.error(f"添加區塊失敗: {str(e)}")
            return False
    
    def get_blocks(self, page_id: str, block_type: Optional[str] = None) -> List[Dict]:
        """
        獲取區塊
        
        Args:
            page_id: 頁面ID
            block_type: 區塊類型，為None時獲取所有類型
            
        Returns:
            區塊列表
        """
        try:
            # 獲取區塊
            blocks = self._client.blocks.children.list(block_id=page_id)
            
            # 過濾區塊類型
            if block_type:
                blocks = [block for block in blocks["results"] if block["type"] == block_type]
            
            self.logger.debug(f"已獲取頁面 {page_id} 的區塊: {len(blocks)} 個")
            return blocks
        
        except Exception as e:
            self.logger.error(f"獲取區塊失敗: {str(e)}")
            return []
    
    def create_database(self, parent_id: str, title: str, properties: Dict) -> Optional[str]:
        """
        創建數據庫
        
        Args:
            parent_id: 父頁面ID
            title: 數據庫標題
            properties: 數據庫屬性
            
        Returns:
            數據庫ID，失敗時返回None
        """
        try:
            # 創建數據庫
            database = self._client.databases.create(
                parent={"page_id": parent_id},
                title=[{"type": "text", "text": {"content": title}}],
                properties=properties
            )
            
            self.logger.debug(f"已創建數據庫: {database['id']}")
            return database["id"]
        
        except Exception as e:
            self.logger.error(f"創建數據庫失敗: {str(e)}")
            return None
    
    def update_database(self, database_id: str, title: Optional[str] = None, 
                       properties: Optional[Dict] = None) -> bool:
        """
        更新數據庫
        
        Args:
            database_id: 數據庫ID
            title: 數據庫標題
            properties: 數據庫屬性
            
        Returns:
            是否成功更新
        """
        try:
            # 構建更新內容
            update = {}
            
            if title:
                update["title"] = [{"type": "text", "text": {"content": title}}]
            
            if properties:
                update["properties"] = properties
            
            # 更新數據庫
            self._client.databases.update(
                database_id=database_id,
                **update
            )
            
            self.logger.debug(f"已更新數據庫: {database_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"更新數據庫失敗: {str(e)}")
            return False
    
    def get_database(self, database_id: str) -> Optional[Dict]:
        """
        獲取數據庫
        
        Args:
            database_id: 數據庫ID
            
        Returns:
            數據庫信息，失敗時返回None
        """
        try:
            # 獲取數據庫
            database = self._client.databases.retrieve(database_id=database_id)
            
            self.logger.debug(f"已獲取數據庫: {database_id}")
            return database
        
        except Exception as e:
            self.logger.error(f"獲取數據庫失敗: {str(e)}")
            return None
    
    def list_databases(self) -> List[Dict]:
        """
        列出數據庫
        
        Returns:
            數據庫列表
        """
        try:
            # 搜索數據庫
            results = self._client.search(
                filter={"property": "object", "value": "database"}
            )
            
            self.logger.debug(f"已列出數據庫: {len(results['results'])} 個")
            return results["results"]
        
        except Exception as e:
            self.logger.error(f"列出數據庫失敗: {str(e)}")
            return []
    
    def close(self) -> None:
        """關閉 Notion 連接"""
        try:
            if self._client:
                self._client = None
                
                self.logger.info("已關閉 Notion 連接")
        
        except Exception as e:
            self.logger.error(f"關閉 Notion 連接失敗: {str(e)}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
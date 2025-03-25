# 獲取數據庫標題
                    title = result.get("title", [])
                    db_title = "".join([t.get("plain_text", "") for t in title])
                    
                    # 比較標題是否匹配
                    if db_title.lower() == database_name.lower():
                        database_id = result.get("id")
                        
                        # 更新緩存
                        self.database_map[database_name] = database_id
                        
                        return database_id
            
            self.logger.warning(f"未找到Notion數據庫: {database_name}")
            return ""
        
        except Exception as e:
            self.logger.error(f"搜索Notion數據庫失敗: {str(e)}")
            return ""
    
    def create_database(self, database_name: str, properties: Dict) -> str:
        """
        創建Notion數據庫
        
        Args:
            database_name: 數據庫名稱
            properties: 屬性定義
            
        Returns:
            數據庫ID
        """
        try:
            if not self.client:
                self.logger.error("Notion客戶端未初始化")
                return ""
            
            if not self.parent_page_id:
                self.logger.error("未設置Notion父頁面ID")
                return ""
            
            # 檢查是否已存在
            database_id = self._get_database_id(database_name)
            if database_id:
                self.logger.info(f"Notion數據庫已存在: {database_name}, ID: {database_id}")
                return database_id
            
            # 創建數據庫
            response = self.client.databases.create(
                parent={"page_id": self.parent_page_id},
                title=[{"type": "text", "text": {"content": database_name}}],
                properties=properties
            )
            
            database_id = response.get("id", "")
            
            if database_id:
                # 更新緩存
                self.database_map[database_name] = database_id
                self.logger.info(f"已創建Notion數據庫: {database_name}, ID: {database_id}")
            else:
                self.logger.warning(f"創建Notion數據庫失敗: {database_name}")
            
            return database_id
        
        except Exception as e:
            self.logger.error(f"創建Notion數據庫失敗: {str(e)}")
            return ""
    
    def get_database(self, database_name: str) -> Dict:
        """
        獲取數據庫信息
        
        Args:
            database_name: 數據庫名稱
            
        Returns:
            數據庫信息
        """
        try:
            if not self.client:
                self.logger.error("Notion客戶端未初始化")
                return {}
            
            # 獲取數據庫ID
            database_id = self._get_database_id(database_name)
            
            if not database_id:
                self.logger.warning(f"未找到Notion數據庫: {database_name}")
                return {}
            
            # 獲取數據庫
            response = self.client.databases.retrieve(database_id=database_id)
            
            return response
        
        except Exception as e:
            self.logger.error(f"獲取Notion數據庫失敗: {str(e)}")
            return {}
    
    def update_database(self, database_name: str, properties: Dict) -> bool:
        """
        更新數據庫
        
        Args:
            database_name: 數據庫名稱
            properties: 新的屬性定義
            
        Returns:
            是否成功更新
        """
        try:
            if not self.client:
                self.logger.error("Notion客戶端未初始化")
                return False
            
            # 獲取數據庫ID
            database_id = self._get_database_id(database_name)
            
            if not database_id:
                self.logger.warning(f"未找到Notion數據庫: {database_name}")
                return False
            
            # 更新數據庫
            self.client.databases.update(
                database_id=database_id,
                properties=properties
            )
            
            self.logger.info(f"已更新Notion數據庫: {database_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"更新Notion數據庫失敗: {str(e)}")
            return False
    
    @retry_on_exception(retries=3, delay=1)
    def query_database(
        self,
        database_name: str,
        filter_obj: Dict = None,
        sorts: List[Dict] = None,
        page_size: int = 100,
        start_cursor: str = None
    ) -> Dict:
        """
        查詢數據庫
        
        Args:
            database_name: 數據庫名稱
            filter_obj: 過濾條件
            sorts: 排序條件
            page_size: 每頁大小
            start_cursor: 起始游標
            
        Returns:
            查詢結果
        """
        try:
            if not self.client:
                self.logger.error("Notion客戶端未初始化")
                return {"results": []}
            
            # 獲取數據庫ID
            database_id = self._get_database_id(database_name)
            
            if not database_id:
                self.logger.warning(f"未找到Notion數據庫: {database_name}")
                return {"results": []}
            
            # 構建查詢參數
            query_params = {
                "database_id": database_id,
                "page_size": page_size
            }
            
            if filter_obj:
                query_params["filter"] = filter_obj
            
            if sorts:
                query_params["sorts"] = sorts
            
            if start_cursor:
                query_params["start_cursor"] = start_cursor
            
            # 執行查詢
            response = self.client.databases.query(**query_params)
            
            return response
        
        except Exception as e:
            self.logger.error(f"查詢Notion數據庫失敗: {str(e)}")
            raise
    
    def query_all_pages(self, database_name: str, filter_obj: Dict = None, sorts: List[Dict] = None) -> List[Dict]:
        """
        查詢數據庫中的所有頁面
        
        Args:
            database_name: 數據庫名稱
            filter_obj: 過濾條件
            sorts: 排序條件
            
        Returns:
            所有頁面
        """
        try:
            all_pages = []
            has_more = True
            next_cursor = None
            
            while has_more:
                response = self.query_database(
                    database_name=database_name,
                    filter_obj=filter_obj,
                    sorts=sorts,
                    start_cursor=next_cursor
                )
                
                pages = response.get("results", [])
                all_pages.extend(pages)
                
                has_more = response.get("has_more", False)
                next_cursor = response.get("next_cursor")
                
                if not has_more or not next_cursor:
                    break
            
            self.logger.info(f"已查詢 {len(all_pages)} 個頁面，數據庫: {database_name}")
            return all_pages
        
        except Exception as e:
            self.logger.error(f"查詢所有頁面失敗: {str(e)}")
            return []
    
    @retry_on_exception(retries=3, delay=1)
    def create_page(self, database_name: str, properties: Dict, content: List[Dict] = None) -> str:
        """
        創建頁面
        
        Args:
            database_name: 數據庫名稱
            properties: 頁面屬性
            content: 頁面內容
            
        Returns:
            頁面ID
        """
        try:
            if not self.client:
                self.logger.error("Notion客戶端未初始化")
                return ""
            
            # 獲取數據庫ID
            database_id = self._get_database_id(database_name)
            
            if not database_id:
                self.logger.warning(f"未找到Notion數據庫: {database_name}")
                return ""
            
            # 構建頁面數據
            page_data = {
                "parent": {"database_id": database_id},
                "properties": properties
            }
            
            if content:
                page_data["children"] = content
            
            # 創建頁面
            response = self.client.pages.create(**page_data)
            
            page_id = response.get("id", "")
            
            if page_id:
                self.logger.info(f"已創建Notion頁面，ID: {page_id}")
            else:
                self.logger.warning("創建Notion頁面失敗")
            
            return page_id
        
        except Exception as e:
            self.logger.error(f"創建Notion頁面失敗: {str(e)}")
            raise
    
    @retry_on_exception(retries=3, delay=1)
    def update_page(self, page_id: str, properties: Dict = None, archived: bool = None) -> bool:
        """
        更新頁面
        
        Args:
            page_id: 頁面ID
            properties: 新的屬性
            archived: 是否歸檔
            
        Returns:
            是否成功更新
        """
        try:
            if not self.client:
                self.logger.error("Notion客戶端未初始化")
                return False
            
            # 構建更新數據
            update_data = {}
            
            if properties:
                update_data["properties"] = properties
            
            if archived is not None:
                update_data["archived"] = archived
            
            if not update_data:
                self.logger.warning("沒有提供更新數據")
                return False
            
            # 更新頁面
            self.client.pages.update(page_id=page_id, **update_data)
            
            self.logger.info(f"已更新Notion頁面，ID: {page_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"更新Notion頁面失敗，ID: {page_id}, 錯誤: {str(e)}")
            raise
    
    def get_page(self, page_id: str) -> Dict:
        """
        獲取頁面
        
        Args:
            page_id: 頁面ID
            
        Returns:
            頁面數據
        """
        try:
            if not self.client:
                self.logger.error("Notion客戶端未初始化")
                return {}
            
            response = self.client.pages.retrieve(page_id=page_id)
            return response
        
        except Exception as e:
            self.logger.error(f"獲取Notion頁面失敗，ID: {page_id}, 錯誤: {str(e)}")
            return {}
    
    def delete_page(self, page_id: str) -> bool:
        """
        刪除頁面（實際為歸檔）
        
        Args:
            page_id: 頁面ID
            
        Returns:
            是否成功刪除
        """
        return self.update_page(page_id, archived=True)
    
    def create_block(self, page_id: str, block_content: List[Dict]) -> bool:
        """
        創建區塊
        
        Args:
            page_id: 頁面ID
            block_content: 區塊內容
            
        Returns:
            是否成功創建
        """
        try:
            if not self.client:
                self.logger.error("Notion客戶端未初始化")
                return False
            
            # 創建區塊
            self.client.blocks.children.append(
                block_id=page_id,
                children=block_content
            )
            
            self.logger.info(f"已創建Notion區塊，頁面ID: {page_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"創建Notion區塊失敗，頁面ID: {page_id}, 錯誤: {str(e)}")
            return False
    
    def get_blocks(self, page_id: str) -> List[Dict]:
        """
        獲取頁面下的所有區塊
        
        Args:
            page_id: 頁面ID
            
        Returns:
            區塊列表
        """
        try:
            if not self.client:
                self.logger.error("Notion客戶端未初始化")
                return []
            
            response = self.client.blocks.children.list(block_id=page_id)
            return response.get("results", [])
        
        except Exception as e:
            self.logger.error(f"獲取Notion區塊失敗，頁面ID: {page_id}, 錯誤: {str(e)}")
            return []
    
    def convert_to_notion_properties(self, data: Dict) -> Dict:
        """
        將普通數據轉換為Notion屬性格式
        
        Args:
            data: 數據字典
            
        Returns:
            Notion屬性格式
        """
        properties = {}
        
        for key, value in data.items():
            if key in ["notion_page_id", "parent", "id", "created_time", "last_edited_time", "url", "archived"]:
                continue
            
            # 根據值類型設置屬性
            if isinstance(value, str):
                # 檢查是否應該作為標題
                if key == "title" or key == "name":
                    properties[key] = {"title": [{"text": {"content": value}}]}
                else:
                    properties[key] = {"rich_text": [{"text": {"content": value}}]}
            
            elif isinstance(value, int):
                properties[key] = {"number": value}
            
            elif isinstance(value, float):
                properties[key] = {"number": value}
            
            elif isinstance(value, bool):
                properties[key] = {"checkbox": value}
            
            elif isinstance(value, list):
                # 處理多選項或關聯
                if all(isinstance(item, str) for item in value):
                    properties[key] = {"multi_select": [{"name": item} for item in value]}
                else:
                    # 如果不是字符串列表，轉為JSON字符串
                    json_value = json.dumps(value)
                    properties[key] = {"rich_text": [{"text": {"content#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union

from ..utils.logger import setup_logger
from ..utils.error_handler import retry_on_exception, handle_exception


class NotionHandler:
    """
    Notion處理器，提供Notion數據庫的連接和操作功能。
    """
    
    def __init__(
        self,
        config: Dict = None,
        log_level: int = logging.INFO
    ):
        """
        初始化Notion處理器
        
        Args:
            config: 配置字典
            log_level: 日誌級別
        """
        self.logger = setup_logger(__name__, log_level)
        self.config = config or {}
        
        # Notion設置
        self.token = self.config.get("token", "")
        self.database_map = self.config.get("database_map", {})
        self.parent_page_id = self.config.get("parent_page_id", "")
        
        # 初始化客戶端
        self.client = None
        
        # 初始化連接
        self._init_connection()
        
        self.logger.info("Notion處理器初始化完成")
    
    def _init_connection(self):
        """初始化Notion連接"""
        try:
            from notion_client import Client
            
            if not self.token:
                self.logger.error("未提供Notion API令牌，請先設置token")
                return
            
            # 創建客戶端
            self.client = Client(auth=self.token)
            
            # 測試連接
            self.client.users.me()
            
            self.logger.info("已連接Notion API")
        
        except ImportError:
            self.logger.error("未安裝notion_client庫，請先安裝: pip install notion-client")
            return
        
        except Exception as e:
            self.logger.error(f"連接Notion API失敗: {str(e)}")
            self.client = None
    
    def _get_database_id(self, database_name: str) -> str:
        """
        獲取數據庫ID
        
        Args:
            database_name: 數據庫名稱
            
        Returns:
            數據庫ID
        """
        # 如果有緩存，直接返回
        if database_name in self.database_map:
            return self.database_map[database_name]
        
        # 否則搜索數據庫
        try:
            if not self.client:
                self.logger.error("Notion客戶端未初始化")
                return ""
            
            response = self.client.search(
                query=database_name,
                filter={"property": "object", "value": "database"}
            )
            
            for result in response.get("results", []):
                if result.get("object") == "database":
                    # 獲取數據庫標題
                    title = result.get("title", [])
                    db_title = "".join([t.get("plain_text", "") for t in title])
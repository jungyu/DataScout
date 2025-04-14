#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notion存儲處理器

提供基於Notion API的數據存儲功能
"""

import time
from typing import Dict, Any, List, Optional
from notion_client import Client
from ..core.base import StorageHandler
from ..core.config import NotionConfig
from ..core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError,
    AuthenticationError
)

class NotionHandler(StorageHandler):
    """Notion存儲處理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Notion存儲處理器
        
        Args:
            config: 配置字典
        """
        super().__init__(NotionConfig(**config))
        self.client: Optional[Client] = None
    
    def _setup_storage(self) -> None:
        """設置存儲環境"""
        try:
            # 創建Notion客戶端
            self.client = Client(auth=self.config.token)
            
            # 測試連接
            self.client.databases.retrieve(self.config.database_id)
            
            self.logger.info(
                f"Notion存儲環境已初始化: "
                f"database_id={self.config.database_id}"
            )
        except Exception as e:
            raise ConnectionError(f"連接Notion失敗: {str(e)}")
    
    def save(self, data: Any, path: str) -> None:
        """
        保存數據到Notion
        
        Args:
            data: 要保存的數據
            path: 頁面標題
        """
        try:
            # 驗證數據
            self._validate_data(data)
            
            # 構建頁面屬性
            properties = self._build_properties(data)
            
            # 創建頁面
            self.client.pages.create(
                parent={'database_id': self.config.database_id},
                properties=properties
            )
            
            # 備份數據
            self._backup_data(data, path)
            
            self.logger.info(f"數據已保存到Notion: {path}")
        except Exception as e:
            raise StorageError(f"保存數據到Notion失敗: {str(e)}")
    
    def load(self, path: str) -> Any:
        """
        從Notion加載數據
        
        Args:
            path: 頁面標題
            
        Returns:
            Any: 加載的數據
        """
        try:
            # 查詢頁面
            pages = self.client.databases.query(
                database_id=self.config.database_id,
                filter={
                    'property': 'Name',
                    'title': {
                        'equals': path
                    }
                }
            ).get('results', [])
            
            # 檢查頁面是否存在
            if not pages:
                raise NotFoundError(f"頁面不存在: {path}")
            
            # 提取數據
            data = self._extract_data(pages[0]['properties'])
            
            self.logger.info(f"數據已從Notion加載: {path}")
            return data
        except Exception as e:
            raise StorageError(f"從Notion加載數據失敗: {str(e)}")
    
    def delete(self, path: str) -> None:
        """
        從Notion刪除數據
        
        Args:
            path: 頁面標題
        """
        try:
            # 查詢頁面
            pages = self.client.databases.query(
                database_id=self.config.database_id,
                filter={
                    'property': 'Name',
                    'title': {
                        'equals': path
                    }
                }
            ).get('results', [])
            
            # 檢查頁面是否存在
            if not pages:
                raise NotFoundError(f"頁面不存在: {path}")
            
            # 刪除頁面
            self.client.pages.update(
                page_id=pages[0]['id'],
                archived=True
            )
            
            self.logger.info(f"數據已從Notion刪除: {path}")
        except Exception as e:
            raise StorageError(f"從Notion刪除數據失敗: {str(e)}")
    
    def exists(self, path: str) -> bool:
        """
        檢查Notion頁面是否存在
        
        Args:
            path: 頁面標題
            
        Returns:
            bool: 是否存在
        """
        try:
            # 查詢頁面
            pages = self.client.databases.query(
                database_id=self.config.database_id,
                filter={
                    'property': 'Name',
                    'title': {
                        'equals': path
                    }
                }
            ).get('results', [])
            
            return len(pages) > 0
        except Exception as e:
            raise StorageError(f"檢查Notion頁面是否存在失敗: {str(e)}")
    
    def list(self, path: str = None) -> List[str]:
        """
        列出Notion頁面
        
        Args:
            path: 頁面標題前綴，None表示所有頁面
            
        Returns:
            List[str]: 頁面標題列表
        """
        try:
            # 構建查詢條件
            filter_params = {}
            if path:
                filter_params = {
                    'property': 'Name',
                    'title': {
                        'starts_with': path
                    }
                }
            
            # 查詢頁面
            pages = self.client.databases.query(
                database_id=self.config.database_id,
                filter=filter_params
            ).get('results', [])
            
            # 提取頁面標題
            titles = []
            for page in pages:
                title = page['properties']['Name']['title'][0]['text']['content']
                titles.append(title)
            
            return titles
        except Exception as e:
            raise StorageError(f"列出Notion頁面失敗: {str(e)}")
    
    def _build_properties(self, data: Any) -> Dict[str, Any]:
        """
        構建Notion頁面屬性
        
        Args:
            data: 數據
            
        Returns:
            Dict[str, Any]: 頁面屬性
        """
        properties = {
            'Name': {
                'title': [
                    {
                        'text': {
                            'content': str(data.get('title', ''))
                        }
                    }
                ]
            }
        }
        
        # 添加其他屬性
        for key, value in data.items():
            if key == 'title':
                continue
            
            if isinstance(value, str):
                properties[key] = {
                    'rich_text': [
                        {
                            'text': {
                                'content': value
                            }
                        }
                    ]
                }
            elif isinstance(value, (int, float)):
                properties[key] = {
                    'number': value
                }
            elif isinstance(value, bool):
                properties[key] = {
                    'checkbox': value
                }
            elif isinstance(value, list):
                properties[key] = {
                    'multi_select': [
                        {'name': str(item)} for item in value
                    ]
                }
            else:
                properties[key] = {
                    'rich_text': [
                        {
                            'text': {
                                'content': str(value)
                            }
                        }
                    ]
                }
        
        return properties
    
    def _extract_data(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        從Notion頁面屬性提取數據
        
        Args:
            properties: 頁面屬性
            
        Returns:
            Dict[str, Any]: 數據
        """
        data = {}
        
        for key, value in properties.items():
            if key == 'Name':
                data['title'] = value['title'][0]['text']['content']
            elif 'rich_text' in value:
                data[key] = value['rich_text'][0]['text']['content']
            elif 'number' in value:
                data[key] = value['number']
            elif 'checkbox' in value:
                data[key] = value['checkbox']
            elif 'multi_select' in value:
                data[key] = [item['name'] for item in value['multi_select']]
        
        return data 
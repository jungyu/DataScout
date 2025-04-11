#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
處理器包

此包提供了一系列數據提取處理器，包括：
1. 網頁處理器 - 用於提取網頁內容
2. API處理器 - 用於處理API請求
3. 分頁處理器 - 用於處理分頁內容

主要組件：
- WebHandler: 網頁處理器，提供網頁內容提取功能
- APIHandler: API處理器，提供API請求處理功能
- PaginationHandler: 分頁處理器，提供分頁內容處理功能

使用示例：
```python
from selenium import webdriver
from src.extractors.handlers import (
    WebHandler,
    APIHandler,
    PaginationHandler
)
from src.core.data_processor import DataProcessor, DataProcessorConfig

# 創建網頁處理器
web_config = {
    "url": "https://example.com",
    "extract_rules": {
        "title": {
            "selector": "h1",
            "type": "text"
        }
    }
}
web_handler = WebHandler(web_config, driver=webdriver.Chrome())

# 創建API處理器
api_config = {
    "base_url": "https://api.example.com",
    "endpoints": {
        "users": "/users"
    }
}
api_handler = APIHandler(api_config)

# 創建分頁處理器
pagination_config = {
    "type": "button_click",
    "next_button_selector": ".next-page"
}
pagination_handler = PaginationHandler(pagination_config, driver=webdriver.Chrome())

# 創建數據處理器
data_processor = DataProcessor({
    "remove_html": True,
    "remove_extra_spaces": True,
    "normalize_whitespace": True
})
```
"""

from .web import (
    WebHandler,
    WebConfig,
    WebLoadStrategy
)

from .api import (
    APIHandler,
    APIConfig,
    APIMethod,
    APIAuthType
)

from .pagination_handler import (
    PaginationHandler,
    PaginationConfig,
    PaginationType
)

# 從核心模組導入數據處理器
from src.core.data_processor import (
    DataProcessor,
    DataProcessorConfig
)

__all__ = [
    # 網頁處理器
    "WebHandler",
    "WebConfig",
    "WebLoadStrategy",
    
    # API處理器
    "APIHandler",
    "APIConfig",
    "APIMethod",
    "APIAuthType",
    
    # 分頁處理器
    "PaginationHandler",
    "PaginationConfig",
    "PaginationType",
    
    # 數據處理器（從核心模組導入）
    "DataProcessor",
    "DataProcessorConfig"
]

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

# 處理器工廠函數
def create_handler(handler_type: str, **kwargs):
    """
    創建處理器實例
    
    Args:
        handler_type: 處理器類型
        **kwargs: 處理器參數
        
    Returns:
        處理器實例
    """
    handlers = {
        'captcha': CaptchaHandler,
        'pagination': PaginationHandler,
        'api': ApiHandler,
        'storage': StorageHandler
    }
    
    if handler_type not in handlers:
        raise ValueError(f"不支持的處理器類型: {handler_type}")
        
    return handlers[handler_type](**kwargs)

# 便捷函數
def create_captcha_handler(**kwargs) -> CaptchaHandler:
    """
    創建驗證碼處理器
    
    Args:
        **kwargs: 處理器參數
        
    Returns:
        CaptchaHandler: 驗證碼處理器實例
    """
    return CaptchaHandler(**kwargs)

def create_pagination_handler(**kwargs) -> PaginationHandler:
    """
    創建分頁處理器
    
    Args:
        **kwargs: 處理器參數
        
    Returns:
        PaginationHandler: 分頁處理器實例
    """
    return PaginationHandler(**kwargs)

def create_api_handler(**kwargs) -> ApiHandler:
    """
    創建 API 處理器
    
    Args:
        **kwargs: 處理器參數
        
    Returns:
        ApiHandler: API 處理器實例
    """
    return ApiHandler(**kwargs)

def create_storage_handler(**kwargs) -> StorageHandler:
    """
    創建存儲處理器
    
    Args:
        **kwargs: 處理器參數
        
    Returns:
        StorageHandler: 存儲處理器實例
    """
    return StorageHandler(**kwargs)

# Notion API 便捷函數
def create_notion_page(database_id: str, properties: dict, **kwargs) -> dict:
    """
    在 Notion 數據庫中創建新頁面
    
    Args:
        database_id: 數據庫 ID
        properties: 頁面屬性
        **kwargs: API 處理器參數
        
    Returns:
        dict: 創建的頁面信息
    """
    handler = create_api_handler(**kwargs)
    return handler.create_notion_page(database_id, properties)

def query_notion_database(database_id: str, filter_params: dict = None, page_size: int = 100, **kwargs) -> dict:
    """
    查詢 Notion 數據庫
    
    Args:
        database_id: 數據庫 ID
        filter_params: 過濾參數
        page_size: 每頁結果數量
        **kwargs: API 處理器參數
        
    Returns:
        dict: 查詢結果
    """
    handler = create_api_handler(**kwargs)
    return handler.query_notion_database(database_id, filter_params, page_size)

def update_notion_page(page_id: str, properties: dict, **kwargs) -> dict:
    """
    更新 Notion 頁面
    
    Args:
        page_id: 頁面 ID
        properties: 更新的屬性
        **kwargs: API 處理器參數
        
    Returns:
        dict: 更新後的頁面信息
    """
    handler = create_api_handler(**kwargs)
    return handler.update_notion_page(page_id, properties)

def append_notion_block(block_id: str, children: list, **kwargs) -> dict:
    """
    向 Notion 區塊添加子區塊
    
    Args:
        block_id: 區塊 ID
        children: 子區塊列表
        **kwargs: API 處理器參數
        
    Returns:
        dict: 操作結果
    """
    handler = create_api_handler(**kwargs)
    return handler.append_notion_block(block_id, children)

def search_notion(query: str, filter_params: dict = None, sort_params: dict = None, page_size: int = 100, **kwargs) -> dict:
    """
    搜索 Notion 內容
    
    Args:
        query: 搜索關鍵詞
        filter_params: 過濾參數
        sort_params: 排序參數
        page_size: 每頁結果數量
        **kwargs: API 處理器參數
        
    Returns:
        dict: 搜索結果
    """
    handler = create_api_handler(**kwargs)
    return handler.search_notion(query, filter_params, sort_params, page_size)
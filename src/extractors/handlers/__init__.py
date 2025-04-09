#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
處理器模組

此模組提供各種數據提取和處理的處理器，包括：
- 驗證碼處理
- 分頁處理
- API 處理
- 存儲處理
"""

from .captcha_handler import CaptchaHandler, CaptchaType, CaptchaDetectionResult
from .pagination_handler import PaginationHandler, PaginationType, PaginationConfig
from .api_handler import ApiHandler, ApiType, ApiConfig
from .storage_handler import StorageHandler, StorageType, StorageConfig

# 導出所有處理器類和相關類型
__all__ = [
    # 驗證碼處理
    'CaptchaHandler',
    'CaptchaType',
    'CaptchaDetectionResult',
    
    # 分頁處理
    'PaginationHandler',
    'PaginationType',
    'PaginationConfig',
    
    # API 處理
    'ApiHandler',
    'ApiType',
    'ApiConfig',
    
    # 存儲處理
    'StorageHandler',
    'StorageType',
    'StorageConfig'
]

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

# 版本信息
__version__ = '0.1.0'
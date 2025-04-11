#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬蟲提取器模組

提供網頁數據提取的核心功能，包括：
1. 頁面處理
2. API 處理
3. 分頁處理
4. 數據提取
5. 錯誤處理
"""

from .core.base import BaseExtractor
from .core.data_extractor import DataExtractor
from .handlers.web.page_handler import PageHandler, PageConfig, WaitStrategy
from .handlers.api.api_handler import APIHandler, APIConfig, APIMethod, APIAuthType
from .handlers.pagination_handler import PaginationHandler, PaginationConfig, PaginationType
from .exceptions import (
    CrawlerException,
    ConfigError,
    NetworkError,
    ParseError,
    ResourceError,
    StateError,
    DataError,
    handle_exception
)

__all__ = [
    # 核心類
    'BaseExtractor',
    'DataExtractor',
    
    # 頁面處理
    'PageHandler',
    'PageConfig',
    'WaitStrategy',
    
    # API 處理
    'APIHandler',
    'APIConfig',
    'APIMethod',
    'APIAuthType',
    
    # 分頁處理
    'PaginationHandler',
    'PaginationConfig',
    'PaginationType',
    
    # 異常處理
    'CrawlerException',
    'ConfigError',
    'NetworkError',
    'ParseError',
    'ResourceError',
    'StateError',
    'DataError',
    'handle_exception'
]

__version__ = '1.0.0'
__author__ = 'Your Name'
__license__ = 'MIT'

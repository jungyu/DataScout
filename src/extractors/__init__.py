#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提取器包 - 包含用於從網頁中提取數據的各種提取器

主要組件：
- 核心提取器：
  - BaseExtractor: 基礎提取器，提供基本的提取功能
  - DataExtractor: 數據提取器，用於提取單一數據
  - ListExtractor: 列表提取器，用於提取列表數據
  - DetailExtractor: 詳情提取器，用於提取詳情頁數據
  - CompoundExtractor: 複合提取器，用於提取複雜數據結構

- 處理器：
  - CaptchaHandler: 驗證碼處理器，處理驗證碼相關操作
  - PaginationHandler: 分頁處理器，處理分頁相關操作
  - StorageHandler: 存儲處理器，處理數據存儲相關操作

使用示例：
    from src.extractors import ListExtractor, DetailExtractor
    
    # 創建列表提取器
    list_extractor = ListExtractor(config)
    
    # 創建詳情提取器
    detail_extractor = DetailExtractor(config)
    
    # 提取數據
    list_data = list_extractor.extract()
    detail_data = detail_extractor.extract()
"""

__version__ = '1.0.0'
__author__ = 'Aaron'
__license__ = 'MIT'

__all__ = [
    # 核心提取器
    'BaseExtractor',
    'DataExtractor',
    'ListExtractor',
    'DetailExtractor',
    'CompoundExtractor',
    
    # 處理器
    'CaptchaHandler',
    'PaginationHandler',
    'StorageHandler'
]

# 導入核心提取器
from .core import (
    BaseExtractor,
    DataExtractor,
    ListExtractor,
    DetailExtractor,
    CompoundExtractor
)

# 導入處理器
from .handlers import (
    CaptchaHandler,
    PaginationHandler,
    StorageHandler
)

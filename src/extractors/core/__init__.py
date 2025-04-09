#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提取器核心模組 (core/__init__.py)

提供網頁數據提取的核心功能，包含各種專門的提取器類。

主要組件：
- BaseExtractor: 基礎提取器，提供共享功能和抽象接口
- DataExtractor: 通用數據提取器，處理各種類型的數據提取
- ListExtractor: 列表提取器，專門處理列表頁面的數據提取
- DetailExtractor: 詳情提取器，專門處理詳情頁面的數據提取
- CompoundExtractor: 複合提取器，處理複雜的嵌套數據結構

使用示例：
    from src.extractors.core import DataExtractor, ListExtractor, DetailExtractor
    
    # 創建提取器
    data_extractor = DataExtractor(driver, base_url="https://example.com")
    list_extractor = ListExtractor(driver, base_url="https://example.com")
    detail_extractor = DetailExtractor(driver, base_url="https://example.com")
    
    # 提取數據
    list_data = list_extractor.extract(list_config)
    for item in list_data:
        detail_data = detail_extractor.extract(item['url'], detail_config)
        # 處理提取的數據
"""

# 導出核心提取器類
from .base_extractor import BaseExtractor
from .data_extractor import DataExtractor
from .list_extractor import ListExtractor
from .detail_extractor import DetailExtractor
from .compound_extractor import CompoundExtractor

# 定義可以直接從包中導入的類
__all__ = [
    'BaseExtractor',
    'DataExtractor',
    'ListExtractor',
    'DetailExtractor',
    'CompoundExtractor'
]

# 版本信息
__version__ = '0.1.0'
__author__ = 'Crawler Team'
__license__ = 'MIT'
__copyright__ = 'Copyright 2023 Crawler Team'
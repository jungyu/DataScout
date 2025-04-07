#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提取器核心模組

包含所有核心提取器類的實現
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
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提取器模組

提供爬蟲系統的數據提取功能，包括：
- 數據提取
- 數據解析
- 數據驗證
"""

from .extractor import Extractor
from .parser import Parser
from .validator import Validator

__version__ = '1.0.0'
__author__ = 'Aaron Yu (https://github.com/jungyu), Claude AI, Cursor AI'
__license__ = 'MIT'

__all__ = [
    'Extractor',
    'Parser',
    'Validator'
]

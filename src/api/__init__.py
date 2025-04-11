#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API 模組

提供爬蟲系統的 API 功能，包括：
- API 處理
- API 配置
- API 錯誤處理
"""

from .api_handler import APIHandler
from .api_config import APIConfig
from .api_error import APIError

__version__ = '1.0.0'
__author__ = 'Aaron Yu (https://github.com/jungyu), Claude AI, Cursor AI'
__license__ = 'MIT'

__all__ = [
    'APIHandler',
    'APIConfig',
    'APIError'
] 
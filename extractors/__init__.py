#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提取器模組

提供數據提取功能，包括：
1. 基礎提取器
2. 提取器管理器
3. 錯誤處理
4. 日誌記錄
"""

from .core.error import (
    ExtractorError,
    ExtractorNotFoundError,
    ExtractorConfigError,
    ExtractorValidationError,
    ExtractorExecutionError,
    ExtractorTimeoutError,
    ExtractorStateError,
    handle_extractor_error
)
from .core.base import BaseExtractor
from .core.manager import BaseExtractorManager
from .handlers.web import WebExtractor
from .handlers.content import ContentExtractor
from .handlers.form import FormExtractor

__version__ = '1.0.0'
__author__ = 'Aaron Yu (https://github.com/jungyu), Claude AI, Cursor AI'
__license__ = 'MIT'

__all__ = [
    # 錯誤類別
    'ExtractorError',
    'ExtractorNotFoundError',
    'ExtractorConfigError',
    'ExtractorValidationError',
    'ExtractorExecutionError',
    'ExtractorTimeoutError',
    'ExtractorStateError',
    'handle_extractor_error',
    
    # 基礎類別
    'BaseExtractor',
    'BaseExtractorManager',
    
    # 具體提取器
    'WebExtractor',
    'ContentExtractor',
    'FormExtractor'
] 
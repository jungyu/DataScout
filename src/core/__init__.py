#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
核心模組

提供爬蟲系統的基礎功能，包括：
- 配置管理
- 異常處理
- 基礎爬蟲類
- 通用工具
- 狀態管理
"""

from .config_loader import ConfigLoader, BaseConfig
from .crawler_state_manager import CrawlerStateManager
from .crawler_engine import CrawlerEngine
from .exceptions import (
    CrawlerException,
    ConfigError,
    BrowserError,
    NavigationError,
    ExtractionError,
    StateError
)
from .data_processor import DataProcessor
from .webdriver_manager import WebDriverManager
from .template_crawler import TemplateCrawler

__all__ = [
    'ConfigLoader',
    'BaseConfig',
    'CrawlerStateManager',
    'CrawlerEngine',
    'CrawlerException',
    'ConfigError',
    'BrowserError',
    'NavigationError',
    'ExtractionError',
    'StateError',
    'DataProcessor',
    'WebDriverManager',
    'TemplateCrawler'
]
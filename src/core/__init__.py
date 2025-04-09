#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬蟲系統核心模組
提供配置載入、WebDriver管理、模板爬蟲和爬蟲引擎功能

主要組件：
- ConfigLoader: 配置載入器，負責讀取和驗證配置文件
- WebDriverManager: WebDriver管理器，處理瀏覽器實例的創建和管理
- TemplateCrawler: 模板爬蟲，基於配置模板執行爬蟲任務
- CrawlerEngine: 爬蟲引擎，協調和管理爬蟲任務的執行

使用示例：
    from src.core import ConfigLoader, WebDriverManager, TemplateCrawler
    
    # 載入配置
    config = ConfigLoader().load_config('config.json')
    
    # 初始化WebDriver
    driver_manager = WebDriverManager(config)
    driver = driver_manager.create_driver()
    
    # 創建爬蟲實例
    crawler = TemplateCrawler(config, driver)
    
    # 執行爬蟲
    results = crawler.start()
"""

__version__ = '1.0.0'
__author__ = 'Aaron'
__license__ = 'MIT'

__all__ = [
    'ConfigLoader',
    'WebDriverManager',
    'TemplateCrawler',
    'CrawlerEngine'
]

from .config_loader import ConfigLoader
from .webdriver_manager import WebDriverManager
from .template_crawler import TemplateCrawler
from .crawler_engine import CrawlerEngine

from .crawler_state_manager import (
    CrawlerStateManager,
    CrawlerState,
    CrawlerStateConfig,
    StorageFormat
)

__all__ = [
    'CrawlerStateManager',
    'CrawlerState',
    'CrawlerStateConfig',
    'StorageFormat'
]
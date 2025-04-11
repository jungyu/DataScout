#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
網頁處理模組

此模組提供了一套完整的網頁內容提取工具，包括：
1. 網頁處理器 - 用於提取網頁內容
2. 配置管理 - 提供靈活的配置選項
3. 加載策略 - 支持不同的頁面加載方式
4. 工具函數 - 提供常用的輔助功能

主要組件：
- WebHandler: 網頁處理器類，提供網頁內容提取功能
- WebConfig: 網頁配置類，用於配置網頁處理器
- WebLoadStrategy: 網頁加載策略枚舉，定義不同的加載方式

使用示例：
```python
from selenium import webdriver
from src.extractors.handlers.web import WebHandler, WebConfig, WebLoadStrategy

# 創建配置
config = WebConfig(
    url="https://example.com",
    load_strategy=WebLoadStrategy.NORMAL,
    extract_rules={
        "title": {
            "selector": "h1",
            "type": "text"
        }
    }
)

# 創建瀏覽器實例
driver = webdriver.Chrome()

# 創建處理器
handler = WebHandler(config, driver)

# 提取數據
items = handler.extract("https://example.com")
```
"""

from .web_handler import (
    WebHandler,
    WebConfig,
    WebLoadStrategy
)

__all__ = [
    "WebHandler",
    "WebConfig",
    "WebLoadStrategy"
]

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT" 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
反檢測基礎模組

提供以下功能：
1. 基礎管理器
2. 基礎錯誤處理
3. 基礎配置
4. 基礎爬蟲
"""

from .base_manager import BaseManager
from .base_error import AntiDetectionError
from .base_config import BaseConfig
from .base_scraper import BaseScraper

__all__ = ['BaseManager', 'AntiDetectionError', 'BaseConfig', 'BaseScraper'] 
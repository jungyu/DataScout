#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
反檢測模組

提供爬蟲系統的反檢測功能，包括：
- 瀏覽器指紋偽裝
- 代理IP管理
- 請求頭偽裝
- 行為模擬
"""

from .fingerprint import FingerprintManager
from .proxy import ProxyManager
from .headers import HeadersManager
from .behavior import BehaviorSimulator

__version__ = '1.0.0'
__author__ = 'Aaron Yu (https://github.com/jungyu), Claude AI, Cursor AI'
__license__ = 'MIT'

__all__ = [
    'FingerprintManager',
    'ProxyManager',
    'HeadersManager',
    'BehaviorSimulator'
]

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

from .utils.browser_fingerprint import BrowserFingerprint
from .utils.human_behavior import HumanBehavior
from .proxy_manager import ProxyManager
from .user_agent_manager import UserAgentManager
from src.core.utils.cookie_manager import CookieManager
from .configs.anti_detection_config import AntiDetectionConfig
from .configs.proxy_config import ProxyConfig, ProxyPoolConfig
from .configs.user_agent_config import UserAgentConfig
from .configs.delay_config import DelayConfig
from .base_scraper import BaseScraper
from .anti_detection_manager import AntiDetectionManager

__version__ = '1.0.0'
__author__ = 'Aaron Yu (https://github.com/jungyu), Claude AI, Cursor AI'
__license__ = 'MIT'

__all__ = [
    'BrowserFingerprint',
    'HumanBehavior',
    'ProxyManager',
    'UserAgentManager',
    'CookieManager',
    'AntiDetectionConfig',
    'ProxyConfig',
    'ProxyPoolConfig',
    'UserAgentConfig',
    'DelayConfig',
    'BaseScraper',
    'AntiDetectionManager'
]

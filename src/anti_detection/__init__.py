#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
反檢測模組

提供防止被網站偵測為爬蟲的功能，包括：
- 瀏覽器指紋
- 代理管理
- Cookie 管理
- 用戶代理管理
- 反檢測特定工具
"""

from .base_config import AntiDetectionConfig
from .user_agent_manager import UserAgentManager
from .anti_detection_manager import AntiDetectionManager
from .browser_fingerprint_manager import BrowserFingerprintManager
from .proxy_manager import ProxyManager
from .base_error import AntiDetectionError
from .base_manager import BaseManager
from .detection_handler import DetectionHandler
from .honeypot_detector import HoneypotDetector

__all__ = [
    'AntiDetectionConfig',
    'UserAgentManager',
    'AntiDetectionManager',
    'BrowserFingerprintManager',
    'ProxyManager',
    'AntiDetectionError',
    'BaseManager',
    'DetectionHandler',
    'HoneypotDetector'
]

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
反檢測模組

提供以下功能：
1. 基礎功能
2. 管理器功能
3. 規避功能
4. 檢測功能
5. 隱藏功能
6. 行為模擬
7. 指紋管理
"""

from .base import BaseManager, AntiDetectionError, BaseConfig, BaseScraper
from .managers import (
    AntiDetectionManager,
    ProxyManager,
    CookieManager,
    UserAgentManager
)
from .evasion import EvasionManager, EvasionCleanup, EvasionScripts
from .detection import DetectionHandler, HoneypotDetector
from .stealth import StealthManager, StealthStrategy, StealthScripts
from .behavior import (
    BehaviorManager,
    MouseBehavior,
    KeyboardBehavior,
    ScrollBehavior,
    FormBehavior
)
from .fingerprint import (
    FingerprintManager,
    FingerprintGenerator,
    FingerprintInjector,
    FingerprintValidator,
    FingerprintUpdater
)

__all__ = [
    # 基礎類
    'BaseManager',
    'AntiDetectionError',
    'BaseConfig',
    'BaseScraper',
    
    # 管理器類
    'AntiDetectionManager',
    'ProxyManager',
    'CookieManager',
    'UserAgentManager',
    
    # 規避類
    'EvasionManager',
    'EvasionCleanup',
    'EvasionScripts',
    
    # 檢測類
    'DetectionHandler',
    'HoneypotDetector',
    
    # 隱藏類
    'StealthManager',
    'StealthStrategy',
    'StealthScripts',
    
    # 行為類
    'BehaviorManager',
    'MouseBehavior',
    'KeyboardBehavior',
    'ScrollBehavior',
    'FormBehavior',
    
    # 指紋類
    'FingerprintManager',
    'FingerprintGenerator',
    'FingerprintInjector',
    'FingerprintValidator',
    'FingerprintUpdater'
] 
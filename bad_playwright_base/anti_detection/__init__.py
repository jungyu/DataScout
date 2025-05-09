#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
反檢測模組

提供以下功能：
1. WebGL 指紋偽裝
2. Canvas 指紋偽裝
3. 音頻指紋偽裝
4. 字體指紋偽裝
5. 屏幕指紋偽裝
6. 平台指紋偽裝
7. 代理管理
8. 人性化行為
9. 用戶代理管理
"""

from .webgl_spoofer import WebGLSpoofer
from .canvas_spoofer import CanvasSpoofer
from .audio_spoofer import AudioSpoofer
from .fingerprint import FingerprintManager
from .proxy_manager import ProxyManager
from .human_like import HumanLikeBehavior
from .user_agent import UserAgentManager

__all__ = [
    # 指紋偽裝
    'WebGLSpoofer',
    'CanvasSpoofer',
    'AudioSpoofer',
    'FingerprintManager',
    
    # 代理管理
    'ProxyManager',
    
    # 人性化行為
    'HumanLikeBehavior',
    
    # 用戶代理管理
    'UserAgentManager'
] 
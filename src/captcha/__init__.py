#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼模組

提供驗證碼處理相關功能，包括：
- 驗證碼檢測
- 驗證碼處理
- 驗證碼識別
- 驗證碼特定工具
- 特定網站驗證碼求解器
"""

from .base_config import CaptchaConfig
from .detection import CaptchaDetector
from .captcha_manager import CaptchaManager
from .types import CaptchaType, CaptchaSource, CaptchaResult
from .solvers.shopee_solver import ShopeeSolver

__all__ = [
    'CaptchaConfig',
    'CaptchaDetector',
    'CaptchaManager',
    'CaptchaType',
    'CaptchaSource',
    'CaptchaResult',
    'ShopeeSolver'
]

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼模組

提供爬蟲系統的驗證碼處理功能，包括：
- 驗證碼服務
- 圖像驗證碼處理
- 音頻驗證碼處理
"""

from .handlers import CaptchaService, CaptchaResult
from .types import CaptchaConfig, CaptchaType

__version__ = '1.0.0'
__author__ = 'Aaron Yu (https://github.com/jungyu), Claude AI, Cursor AI'
__license__ = 'MIT'

__all__ = [
    'CaptchaService',
    'CaptchaResult',
    'CaptchaConfig',
    'CaptchaType'
]

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼處理器模組

提供各種驗證碼處理器，包括：
1. 圖像驗證碼處理器
2. 音頻驗證碼處理器
3. 驗證碼服務
"""

from .service import CaptchaService, CaptchaResult

__all__ = [
    'CaptchaService',
    'CaptchaResult'
] 
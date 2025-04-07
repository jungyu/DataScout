#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提取器處理器模組

包含用於處理各種提取任務的專門處理器
"""

# 導出處理器類
from .captcha_handler import CaptchaHandler
from .pagination_handler import PaginationHandler
from .storage_handler import StorageHandler

# 定義可以直接從包中導入的類
__all__ = [
    'CaptchaHandler',
    'PaginationHandler',
    'StorageHandler'
]

# 版本信息
__version__ = '0.1.0'
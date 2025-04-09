#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼工具模組

提供各種驗證碼處理工具，包括：
1. 圖像處理工具
2. 音頻處理工具
3. 文本處理工具
4. 錯誤處理工具
5. 日誌工具
"""

from .image import ImageProcessor
from .audio import AudioProcessor
from .text import TextProcessor, TextProcessResult
from .error import (
    CaptchaError,
    ImageProcessError,
    AudioProcessError,
    TextProcessError,
    ValidationError,
    RetryError,
    handle_error,
    setup_error_logging
)
from .logger import (
    Logger,
    LogConfig,
    LogFilter,
    LogFormatter
)

__all__ = [
    # 圖像處理
    'ImageProcessor',
    
    # 音頻處理
    'AudioProcessor',
    
    # 文本處理
    'TextProcessor',
    'TextProcessResult',
    
    # 錯誤處理
    'CaptchaError',
    'ImageProcessError',
    'AudioProcessError',
    'TextProcessError',
    'ValidationError',
    'RetryError',
    'handle_error',
    'setup_error_logging',
    
    # 日誌處理
    'Logger',
    'LogConfig',
    'LogFilter',
    'LogFormatter'
] 
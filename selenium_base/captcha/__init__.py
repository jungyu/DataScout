#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼模組

此模組提供驗證碼相關的功能，包括：
1. 基礎功能
2. 管理器功能
3. 檢測功能
4. 識別功能
5. 求解功能
6. 驗證功能
"""

from .base.base_error import (
    CaptchaError,
    ConfigError,
    DetectionError,
    RecognitionError,
    SolverError,
    ValidationError,
    StateError,
    handle_error,
    log_error,
    format_error
)

from .base.base_config import (
    DetectionConfig,
    RecognitionConfig,
    SolverConfig,
    ValidationConfig,
    CaptchaConfig
)

from .base.base_scraper import BaseScraper
from .base.base_manager import BaseManager

__all__ = [
    # 錯誤類
    'CaptchaError',
    'ConfigError',
    'DetectionError',
    'RecognitionError',
    'SolverError',
    'ValidationError',
    'StateError',
    
    # 錯誤處理函數
    'handle_error',
    'log_error',
    'format_error',
    
    # 配置類
    'DetectionConfig',
    'RecognitionConfig',
    'SolverConfig',
    'ValidationConfig',
    'CaptchaConfig',
    
    # 基礎類
    'BaseScraper',
    'BaseManager'
] 
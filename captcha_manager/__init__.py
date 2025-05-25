#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼管理器

提供多種驗證碼解決方案，支持圖片驗證碼、滑動驗證碼等。
主要功能：
- 多種驗證碼類型支持
- 異步操作支持
- 錯誤處理和重試機制
- 日誌記錄
- 配置管理
"""

from captcha_manager.solver import CaptchaSolver
from captcha_manager.config import SolverConfig
from captcha_manager.exceptions import (
    CaptchaError,
    SolverError,
    ValidationError
)
from captcha_manager.utils.logger import setup_logger
from captcha_manager.utils.config import load_config

__version__ = "0.1.0"
__author__ = "DataScout Team"

__all__ = [
    # 核心類
    "CaptchaSolver",
    "SolverConfig",
    
    # 異常類
    "CaptchaError",
    "SolverError",
    "ValidationError",
    
    # 工具函數
    "setup_logger",
    "load_config"
] 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數據提取器

提供多種數據提取方案，支持網頁、文件等多種數據源。
主要功能：
- 多種數據源支持
- 異步操作支持
- 錯誤處理和重試機制
- 日誌記錄
- 配置管理
"""

from extractors.core.extractor import BaseExtractor
from extractors.core.config import ExtractorConfig
from extractors.core.exceptions import (
    ExtractorError,
    ValidationError,
    ConfigurationError
)
from extractors.utils.logger import setup_logger
from extractors.utils.config import load_config

__version__ = "0.1.0"
__author__ = "DataScout Team"

__all__ = [
    # 核心類
    "BaseExtractor",
    "ExtractorConfig",
    
    # 異常類
    "ExtractorError",
    "ValidationError",
    "ConfigurationError",
    
    # 工具函數
    "setup_logger",
    "load_config"
] 
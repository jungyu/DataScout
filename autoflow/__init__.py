#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AutoFlow 工作流自動化框架

提供一個完整的解決方案，用於創建和管理自動化工作流程。
主要功能：
- 工作流程定義和管理
- 異步操作支持
- 錯誤處理和重試機制
- 日誌記錄
- 配置管理
"""

from autoflow.core.flow import Flow
from autoflow.core.config import Config
from autoflow.core.exceptions import (
    FlowError,
    ConfigError,
    ValidationError
)
from autoflow.utils.logger import setup_logger
from autoflow.utils.config import load_config

__version__ = "0.1.0"
__author__ = "DataScout Team"

__all__ = [
    # 核心類
    "Flow",
    "Config",
    
    # 異常類
    "FlowError",
    "ConfigError",
    "ValidationError",
    
    # 工具函數
    "setup_logger",
    "load_config"
] 
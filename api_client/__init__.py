#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API 客戶端包

提供統一的 API 調用接口，支持異步操作和錯誤處理。
主要功能：
- 統一的 API 調用接口
- 異步請求支持
- 錯誤處理和重試機制
- 請求限流和緩存
- 日誌記錄
"""

from api_client.core.client import APIClient
from api_client.core.config import APIConfig
from api_client.core.exceptions import (
    APIError,
    RequestError,
    ResponseError,
    RateLimitError
)
from api_client.handlers.retry import RetryHandler
from api_client.handlers.rate_limit import RateLimitHandler
from api_client.handlers.cache import CacheHandler

__version__ = "0.1.0"
__author__ = "DataScout Team"

__all__ = [
    # 核心類
    "APIClient",
    "APIConfig",
    
    # 異常類
    "APIError",
    "RequestError",
    "ResponseError",
    "RateLimitError",
    
    # 處理器
    "RetryHandler",
    "RateLimitHandler",
    "CacheHandler"
] 
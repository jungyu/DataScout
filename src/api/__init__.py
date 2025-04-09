#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API 模組

提供 API 相關的功能和組件。
包括：
1. API 配置
2. API 類型
3. 認證類型
4. API 處理器
"""

from .config import (
    APIConfig,
    APIType,
    AuthType
)

from .handlers import (
    BaseAPIHandler,
    APIRequest,
    APIResponse,
    APIError,
    RESTAPIHandler,
    WebhookAPIHandler,
    N8NAPIHandler,
    MakeAPIHandler,
    ZapierAPIHandler,
    IFTTTAPIHandler,
    CustomAPIHandler,
    AutomationAPIHandler
)

__all__ = [
    # 配置相關
    'APIConfig',
    'APIType',
    'AuthType',
    
    # 基礎組件
    'BaseAPIHandler',
    'APIRequest',
    'APIResponse',
    'APIError',
    
    # API 處理器
    'RESTAPIHandler',
    'WebhookAPIHandler',
    'N8NAPIHandler',
    'MakeAPIHandler',
    'ZapierAPIHandler',
    'IFTTTAPIHandler',
    'CustomAPIHandler',
    'AutomationAPIHandler'
] 
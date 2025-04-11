#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API 模組

提供 API 相關的功能。
包括：
1. API 處理器
2. API 配置
3. API 錯誤處理
"""

from .handlers import (
    BaseAPIHandler,
    APIRequest,
    APIResponse,
    APIError,
    RESTAPIHandler,
    WebhookHandler,
    N8NHandler,
    MakeHandler,
    ZapierHandler,
    IFTTTHandler,
    CustomHandler,
    AutomationHandler
)

from src.extractors.handlers.api.api_handler import APIConfig, APIMethod, APIAuthType

__all__ = [
    'BaseAPIHandler',
    'APIRequest',
    'APIResponse',
    'APIError',
    'RESTAPIHandler',
    'WebhookHandler',
    'N8NHandler',
    'MakeHandler',
    'ZapierHandler',
    'IFTTTHandler',
    'CustomHandler',
    'AutomationHandler',
    'APIConfig',
    'APIMethod',
    'APIAuthType'
] 
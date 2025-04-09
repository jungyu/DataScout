#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API 處理器模組

提供各種 API 處理器的實現。
包括：
1. REST API 處理器
2. Webhook API 處理器
3. N8N API 處理器
4. Make API 處理器
5. Zapier API 處理器
6. IFTTT API 處理器
7. 自定義 API 處理器
8. 自動化 API 處理器
"""

from .base import (
    BaseAPIHandler,
    APIRequest,
    APIResponse,
    APIError
)

from .rest import RESTAPIHandler
from .webhook import WebhookAPIHandler
from .n8n import N8NAPIHandler
from .make import MakeAPIHandler
from .zapier import ZapierAPIHandler
from .ifttt import IFTTTAPIHandler
from .custom import CustomAPIHandler
from .automation import AutomationAPIHandler

__all__ = [
    'BaseAPIHandler',
    'APIRequest',
    'APIResponse',
    'APIError',
    'RESTAPIHandler',
    'WebhookAPIHandler',
    'N8NAPIHandler',
    'MakeAPIHandler',
    'ZapierAPIHandler',
    'IFTTTAPIHandler',
    'CustomAPIHandler',
    'AutomationAPIHandler'
] 
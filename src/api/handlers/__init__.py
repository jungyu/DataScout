#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API 處理器模組

提供各種 API 處理器的實現。
包括：
1. REST API 處理器
2. Webhook 處理器
3. 自動化平台處理器
"""

from .base import BaseAPIHandler, APIRequest, APIResponse, APIError
from .rest import RESTAPIHandler
from .webhook import WebhookHandler
from .n8n import N8NHandler
from .make import MakeHandler
from .zapier import ZapierHandler
from .ifttt import IFTTTHandler
from .custom import CustomHandler
from .automation import AutomationHandler

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
    'AutomationHandler'
] 
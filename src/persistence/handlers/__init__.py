#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存儲處理器包
提供各種存儲處理器的實現
"""

from .base_handler import StorageHandler
from .local_storage import LocalStorageHandler
from .mongodb_handler import MongoDBHandler
from .notion_handler import NotionHandler
from .captcha_handler import CaptchaHandler, CaptchaDetectionResult
from src.captcha.types import CaptchaType

__all__ = [
    "StorageHandler",
    "LocalStorageHandler",
    "MongoDBHandler",
    "NotionHandler",
    "CaptchaHandler",
    "CaptchaDetectionResult"
] 
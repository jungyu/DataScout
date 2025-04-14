#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
異常處理模塊
提供各種自定義異常類
"""

class APIError(Exception):
    """API 錯誤基礎類"""
    pass

class ConfigurationError(APIError):
    """配置錯誤"""
    pass

class AuthenticationError(APIError):
    """認證錯誤"""
    pass

class RequestError(APIError):
    """請求錯誤"""
    pass

class ResponseError(APIError):
    """響應錯誤"""
    pass

class ValidationError(APIError):
    """驗證錯誤"""
    pass

class TimeoutError(APIError):
    """超時錯誤"""
    pass

class RetryError(APIError):
    """重試錯誤"""
    pass 
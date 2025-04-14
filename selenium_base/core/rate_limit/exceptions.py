#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
速率限制異常模組

提供以下異常類：
1. RateLimitError: 基礎速率限制異常
2. RateLimitExceededError: 超出速率限制異常
3. RateLimitConfigError: 速率限制配置異常
4. RateLimitStateError: 速率限制狀態異常
5. RateLimitTimeoutError: 速率限制超時異常
6. RateLimitInvalidConfigError: 無效的速率限制配置異常
"""

class RateLimitError(Exception):
    """基礎速率限制異常"""
    def __init__(self, message: str, code: int = 1000):
        self.message = message
        self.code = code
        super().__init__(message)

class RateLimitExceededError(RateLimitError):
    """超出速率限制異常"""
    def __init__(self, message: str = "超出速率限制", code: int = 1001):
        super().__init__(message, code)

class RateLimitConfigError(RateLimitError):
    """速率限制配置異常"""
    def __init__(self, message: str = "配置錯誤", code: int = 1002):
        super().__init__(message, code)

class RateLimitStateError(RateLimitError):
    """速率限制狀態異常"""
    def __init__(self, message: str = "狀態錯誤", code: int = 1003):
        super().__init__(message, code)

class RateLimitTimeoutError(RateLimitError):
    """速率限制超時異常"""
    def __init__(self, message: str = "操作超時", code: int = 1004):
        super().__init__(message, code)

class RateLimitInvalidConfigError(RateLimitConfigError):
    """無效的速率限制配置異常"""
    def __init__(self, message: str = "無效的配置", code: int = 1005):
        super().__init__(message, code) 
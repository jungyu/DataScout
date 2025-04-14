#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
認證異常模組

提供以下異常類：
1. AuthError: 認證基礎異常類
2. LoginError: 登入相關異常
3. SessionError: 會話相關異常
4. CookieError: Cookie相關異常
5. ValidationError: 驗證相關異常
"""

from ..core.exceptions import DataScoutError

class AuthError(DataScoutError):
    """認證基礎異常類"""
    def __init__(self, message: str, code: int = 3000):
        self.message = message
        self.code = code
        super().__init__(message)

class LoginError(AuthError):
    """登入相關異常"""
    def __init__(self, message: str = "登入失敗", code: int = 3001):
        super().__init__(message, code)

class SessionError(AuthError):
    """會話相關異常"""
    def __init__(self, message: str = "會話錯誤", code: int = 3002):
        super().__init__(message, code)

class CookieError(AuthError):
    """Cookie相關異常"""
    def __init__(self, message: str = "Cookie錯誤", code: int = 3003):
        super().__init__(message, code)

class ValidationError(AuthError):
    """驗證相關異常"""
    def __init__(self, message: str = "驗證失敗", code: int = 3004):
        super().__init__(message, code) 
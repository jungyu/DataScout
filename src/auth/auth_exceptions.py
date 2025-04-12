#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
認證異常模組

提供以下異常類：
1. AuthError: 認證基礎異常類
2. LoginError: 登入相關異常
3. SessionError: 會話相關異常
4. CookieError: Cookie相關異常
"""

class AuthError(Exception):
    """認證基礎異常類"""
    pass

class LoginError(AuthError):
    """登入相關異常"""
    pass

class SessionError(AuthError):
    """會話相關異常"""
    pass

class CookieError(AuthError):
    """Cookie相關異常"""
    pass 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
認證模組

提供以下功能：
1. 登入管理
2. 會話管理
3. Cookie 管理
4. 認證異常處理
"""

from .login_manager import LoginManager
from .session_manager import SessionManager
from .cookie_manager import CookieManager
from .auth_exceptions import (
    AuthError,
    LoginError,
    SessionError,
    CookieError,
    ValidationError
)

__all__ = [
    'LoginManager',
    'SessionManager',
    'CookieManager',
    'AuthError',
    'LoginError',
    'SessionError',
    'CookieError',
    'ValidationError'
] 
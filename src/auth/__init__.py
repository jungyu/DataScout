#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
認證模組

提供以下功能：
1. 登入管理
2. 會話管理
3. Cookie管理
4. 認證異常處理
"""

from .auth_exceptions import (
    AuthError,
    LoginError,
    SessionError,
    CookieError
)
from .login_manager import LoginManager
from .session_manager import SessionManager
from ..core.utils.cookie_manager import CookieManager

__version__ = "1.0.0"
__author__ = "DataScout Team"
__license__ = "MIT"

__all__ = [
    "AuthError",
    "LoginError",
    "SessionError",
    "CookieError",
    "LoginManager",
    "SessionManager",
    "CookieManager"
] 
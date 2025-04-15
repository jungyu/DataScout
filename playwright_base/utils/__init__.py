#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具模組

提供 Playwright 基礎框架的工具函數和異常類
"""

from .exceptions import (
    PlaywrightBaseException,
    BrowserException,
    PageException,
    ElementException,
    CaptchaException,
    StorageException,
    ProxyException,
    AuthenticationException,
    ConfigException,
    NavigationException,
    RequestException,
    AntiDetectionException,
)

try:
    from .logger import setup_logger
    __all__ = [
        'PlaywrightBaseException',
        'BrowserException',
        'PageException',
        'ElementException',
        'CaptchaException',
        'StorageException',
        'ProxyException',
        'AuthenticationException',
        'ConfigException',
        'NavigationException',
        'RequestException',
        'AntiDetectionException',
        'setup_logger',
    ]
except ImportError:
    __all__ = [
        'PlaywrightBaseException',
        'BrowserException',
        'PageException',
        'ElementException',
        'CaptchaException',
        'StorageException',
        'ProxyException',
        'AuthenticationException',
        'ConfigException',
        'NavigationException',
        'RequestException',
        'AntiDetectionException',
    ] 
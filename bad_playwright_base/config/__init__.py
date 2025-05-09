#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模組

提供 Playwright 基礎框架的配置常量和函數
"""

from .settings import (
    BROWSER_CONFIG,
    PROXY_CONFIG,
    ANTI_DETECTION_CONFIG,
    REQUEST_INTERCEPT_CONFIG,
    TIMEOUT_CONFIG,
    RETRY_CONFIG,
)

__all__ = [
    'BROWSER_CONFIG',
    'PROXY_CONFIG',
    'ANTI_DETECTION_CONFIG',
    'REQUEST_INTERCEPT_CONFIG',
    'TIMEOUT_CONFIG',
    'RETRY_CONFIG',
] 
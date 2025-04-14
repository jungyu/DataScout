#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
速率限制異常模組

提供以下異常類：
1. RateLimitError: 基礎速率限制異常
2. RateLimitExceededError: 超出速率限制異常
3. RateLimitConfigError: 速率限制配置異常
4. RateLimitStateError: 速率限制狀態異常
"""

class RateLimitError(Exception):
    """基礎速率限制異常"""
    pass

class RateLimitExceededError(RateLimitError):
    """超出速率限制異常"""
    pass

class RateLimitConfigError(RateLimitError):
    """速率限制配置異常"""
    pass

class RateLimitStateError(RateLimitError):
    """速率限制狀態異常"""
    pass 
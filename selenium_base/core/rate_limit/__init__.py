#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
速率限制模組

提供以下功能：
1. 全局速率限制
2. 域名速率限制
3. IP 速率限制
4. 會話速率限制
5. 延遲控制
6. 限流策略
7. 熔斷器
"""

from .exceptions import (
    RateLimitError,
    RateLimitExceededError,
    RateLimitConfigError,
    RateLimitStateError
)
from .manager import RateLimitManager

__all__ = [
    'RateLimitError',
    'RateLimitExceededError',
    'RateLimitConfigError',
    'RateLimitStateError',
    'RateLimitManager'
] 
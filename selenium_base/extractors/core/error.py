#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提取器錯誤處理模組

提供提取器相關的錯誤處理功能，包括：
1. 提取器錯誤類別
2. 錯誤處理裝飾器
3. 錯誤日誌記錄
"""

import functools
import logging
from typing import Any, Callable, Dict, Optional, Type, Union

from ...core.error import BaseError, handle_error

class ExtractorError(BaseError):
    """提取器基礎錯誤類別"""
    pass

class ExtractorNotFoundError(ExtractorError):
    """提取器未找到錯誤"""
    pass

class ExtractorConfigError(ExtractorError):
    """提取器配置錯誤"""
    pass

class ExtractorValidationError(ExtractorError):
    """提取器驗證錯誤"""
    pass

class ExtractorExecutionError(ExtractorError):
    """提取器執行錯誤"""
    pass

class ExtractorTimeoutError(ExtractorError):
    """提取器超時錯誤"""
    pass

class ExtractorStateError(ExtractorError):
    """提取器狀態錯誤"""
    pass

def handle_extractor_error(
    error_types: Optional[Union[Type[Exception], tuple[Type[Exception], ...]]] = None,
    default_return: Any = None,
    logger: Optional[logging.Logger] = None
) -> Callable:
    """
    提取器錯誤處理裝飾器
    
    Args:
        error_types: 要處理的錯誤類型
        default_return: 發生錯誤時的默認返回值
        logger: 日誌記錄器
        
    Returns:
        裝飾器函數
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except error_types or (ExtractorError,) as e:
                if logger:
                    logger.error(f"提取器錯誤：{str(e)}", exc_info=True)
                return default_return
            except Exception as e:
                if logger:
                    logger.error(f"未預期的錯誤：{str(e)}", exc_info=True)
                return default_return
        return wrapper
    return decorator

# 導出所有錯誤類別和函數
__all__ = [
    'ExtractorError',
    'ExtractorNotFoundError',
    'ExtractorConfigError',
    'ExtractorValidationError',
    'ExtractorExecutionError',
    'ExtractorTimeoutError',
    'ExtractorStateError',
    'handle_extractor_error'
] 
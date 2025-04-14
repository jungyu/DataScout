#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基礎錯誤處理模組

此模組提供基礎錯誤處理功能，包括：
1. 自定義錯誤類
2. 錯誤處理裝飾器
3. 錯誤日誌記錄
"""

import functools
import logging
from typing import Any, Callable, Optional, Type, Union

from ...core.exceptions import DataScoutError
from ...core.logger import setup_logger

logger = setup_logger(__name__)

class AntiDetectionError(DataScoutError):
    """反檢測基礎錯誤類"""
    
    def __init__(self, message: str, code: Optional[int] = None):
        """
        初始化錯誤
        
        Args:
            message: 錯誤信息
            code: 錯誤代碼
        """
        self.message = message
        self.code = code or 4000  # 反檢測錯誤代碼從 4000 開始
        super().__init__(message)

class ConfigError(AntiDetectionError):
    """配置錯誤類"""
    def __init__(self, message: str, code: int = 4001):
        super().__init__(message, code)
    
class ProxyError(AntiDetectionError):
    """代理錯誤類"""
    def __init__(self, message: str, code: int = 4002):
        super().__init__(message, code)
    
class UserAgentError(AntiDetectionError):
    """用戶代理錯誤類"""
    def __init__(self, message: str, code: int = 4003):
        super().__init__(message, code)
    
class CookieError(AntiDetectionError):
    """Cookie 錯誤類"""
    def __init__(self, message: str, code: int = 4004):
        super().__init__(message, code)
    
class EvasionError(AntiDetectionError):
    """規避錯誤類"""
    def __init__(self, message: str, code: int = 4005):
        super().__init__(message, code)
    
class ValidationError(AntiDetectionError):
    """驗證錯誤類"""
    def __init__(self, message: str, code: int = 4006):
        super().__init__(message, code)
    
class StateError(AntiDetectionError):
    """狀態錯誤類"""
    def __init__(self, message: str, code: int = 4007):
        super().__init__(message, code)
    
def handle_error(
    error_types: Optional[Union[Type[Exception], tuple[Type[Exception], ...]]] = None,
    default_return: Any = None,
    log_level: int = logging.ERROR
) -> Callable:
    """
    錯誤處理裝飾器
    
    Args:
        error_types: 要處理的錯誤類型
        default_return: 發生錯誤時的默認返回值
        log_level: 日誌級別
        
    Returns:
        裝飾器函數
    """
    if error_types is None:
        error_types = (AntiDetectionError,)
        
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except error_types as e:
                logger.log(
                    log_level,
                    f"函數 {func.__name__} 執行出錯：{str(e)}",
                    exc_info=True
                )
                return default_return
            except Exception as e:
                logger.log(
                    log_level,
                    f"函數 {func.__name__} 發生未預期的錯誤：{str(e)}",
                    exc_info=True
                )
                raise
        return wrapper
    return decorator
    
def log_error(
    error: Exception,
    message: Optional[str] = None,
    level: int = logging.ERROR
) -> None:
    """
    記錄錯誤
    
    Args:
        error: 錯誤對象
        message: 自定義錯誤信息
        level: 日誌級別
    """
    error_message = message or str(error)
    logger.log(level, error_message, exc_info=True)
    
def format_error(error: Exception) -> str:
    """
    格式化錯誤信息
    
    Args:
        error: 錯誤對象
        
    Returns:
        格式化後的錯誤信息
    """
    if isinstance(error, AntiDetectionError):
        return f"[{error.__class__.__name__}] {error.message} (代碼：{error.code})"
    return f"[{error.__class__.__name__}] {str(error)}" 
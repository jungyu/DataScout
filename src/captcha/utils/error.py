#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
錯誤處理工具模組

提供錯誤處理相關的工具類和函數，包括：
1. 自定義異常類
2. 錯誤處理裝飾器
3. 錯誤日誌記錄
4. 錯誤重試機制
"""

import logging
import functools
import traceback
from typing import Optional, Callable, Type, Union, List, Dict, Any
from dataclasses import dataclass
from enum import Enum, auto

class ErrorLevel(Enum):
    """錯誤等級枚舉"""
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

@dataclass
class ErrorContext:
    """錯誤上下文數據類"""
    error_type: Type[Exception]
    error_message: str
    error_level: ErrorLevel
    stack_trace: str
    metadata: Dict[str, Any]

class CaptchaError(Exception):
    """驗證碼處理基礎異常類"""
    
    def __init__(self, message: str, error_level: ErrorLevel = ErrorLevel.ERROR):
        """
        初始化異常
        
        Args:
            message: 錯誤信息
            error_level: 錯誤等級
        """
        super().__init__(message)
        self.error_level = error_level
        self.context = self._create_context()
        
    def _create_context(self) -> ErrorContext:
        """
        創建錯誤上下文
        
        Returns:
            錯誤上下文對象
        """
        return ErrorContext(
            error_type=type(self),
            error_message=str(self),
            error_level=self.error_level,
            stack_trace=traceback.format_exc(),
            metadata={}
        )

class ImageProcessError(CaptchaError):
    """圖像處理異常"""
    pass

class AudioProcessError(CaptchaError):
    """音頻處理異常"""
    pass

class TextProcessError(CaptchaError):
    """文本處理異常"""
    pass

class ValidationError(CaptchaError):
    """驗證異常"""
    pass

class RetryError(CaptchaError):
    """重試異常"""
    pass

def handle_error(
    error_types: Union[Type[Exception], List[Type[Exception]]] = Exception,
    error_level: ErrorLevel = ErrorLevel.ERROR,
    retry_count: int = 0,
    retry_delay: float = 1.0,
    logger: Optional[logging.Logger] = None
) -> Callable:
    """
    錯誤處理裝飾器
    
    Args:
        error_types: 需要處理的異常類型
        error_level: 錯誤等級
        retry_count: 重試次數
        retry_delay: 重試延遲（秒）
        logger: 日誌記錄器
        
    Returns:
        裝飾器函數
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger_instance = logger or logging.getLogger(func.__module__)
            last_error = None
            
            for attempt in range(retry_count + 1):
                try:
                    return func(*args, **kwargs)
                except error_types as e:
                    last_error = e
                    error_context = ErrorContext(
                        error_type=type(e),
                        error_message=str(e),
                        error_level=error_level,
                        stack_trace=traceback.format_exc(),
                        metadata={
                            'function': func.__name__,
                            'attempt': attempt + 1,
                            'max_attempts': retry_count + 1
                        }
                    )
                    
                    # 記錄錯誤
                    log_message = (
                        f"錯誤發生在 {func.__name__}: {str(e)}\n"
                        f"嘗試次數: {attempt + 1}/{retry_count + 1}\n"
                        f"堆疊追蹤:\n{error_context.stack_trace}"
                    )
                    
                    if error_level == ErrorLevel.DEBUG:
                        logger_instance.debug(log_message)
                    elif error_level == ErrorLevel.INFO:
                        logger_instance.info(log_message)
                    elif error_level == ErrorLevel.WARNING:
                        logger_instance.warning(log_message)
                    elif error_level == ErrorLevel.ERROR:
                        logger_instance.error(log_message)
                    else:
                        logger_instance.critical(log_message)
                    
                    # 如果還有重試機會，等待後繼續
                    if attempt < retry_count:
                        import time
                        time.sleep(retry_delay)
                    else:
                        raise RetryError(
                            f"在 {retry_count + 1} 次嘗試後仍然失敗: {str(e)}",
                            error_level=error_level
                        )
                        
            raise last_error
            
        return wrapper
    return decorator

def setup_error_logging(
    logger: Optional[logging.Logger] = None,
    level: int = logging.ERROR,
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
) -> logging.Logger:
    """
    設置錯誤日誌記錄
    
    Args:
        logger: 日誌記錄器
        level: 日誌等級
        format: 日誌格式
        
    Returns:
        配置好的日誌記錄器
    """
    logger_instance = logger or logging.getLogger(__name__)
    
    if not logger_instance.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(format)
        handler.setFormatter(formatter)
        logger_instance.addHandler(handler)
        
    logger_instance.setLevel(level)
    return logger_instance 
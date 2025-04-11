#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基礎錯誤處理類

此模組提供所有錯誤類的基礎功能，包括：
1. 錯誤碼管理
2. 錯誤信息格式化
3. 錯誤追蹤
4. 錯誤恢復
5. 錯誤處理裝飾器
"""

import logging
import functools
from typing import Dict, Any, Optional, Callable, TypeVar, ParamSpec
from datetime import datetime

T = TypeVar('T')
P = ParamSpec('P')

class BaseError(Exception):
    """基礎錯誤類"""
    
    def __init__(
        self,
        code: int,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化錯誤
        
        Args:
            code: 錯誤碼
            message: 錯誤信息
            details: 詳細信息
        """
        self.code = code
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        super().__init__(self.format_message())
        self._log_error()
    
    def format_message(self) -> str:
        """格式化錯誤信息"""
        return f"[{self.code}] {self.message}"
    
    def _log_error(self):
        """記錄錯誤"""
        self.logger.error(
            f"{self.format_message()}\n"
            f"Details: {self.details}\n"
            f"Timestamp: {self.timestamp}"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'code': self.code,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseError':
        """從字典創建錯誤"""
        return cls(
            code=data['code'],
            message=data['message'],
            details=data.get('details')
        )
    
    def recover(self) -> bool:
        """嘗試恢復錯誤"""
        try:
            # 子類實現具體的恢復邏輯
            return True
        except Exception as e:
            self.logger.error(f"恢復失敗: {e}")
            return False

def handle_error(func: Callable[P, T]) -> Callable[P, T]:
    """
    錯誤處理裝飾器
    
    Args:
        func: 要處理的函數
        
    Returns:
        包裝後的函數
    """
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except BaseError as e:
            logging.error(f"處理錯誤: {e}")
            raise
        except Exception as e:
            logging.error(f"未知錯誤: {e}")
            raise BaseError(500, str(e))
    return wrapper

def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (BaseError,)
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    錯誤重試裝飾器
    
    Args:
        max_retries: 最大重試次數
        delay: 重試延遲時間
        exceptions: 需要重試的異常類型
        
    Returns:
        包裝後的函數
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            import time
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries == max_retries:
                        raise
                    logging.warning(f"重試 {retries}/{max_retries}: {e}")
                    time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基礎 API 處理器模組

提供 API 處理的基礎類和接口定義。
包括：
1. 基礎 API 處理器類
2. 請求/響應數據結構
3. 錯誤處理
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import logging
import time
from ..config import APIConfig, APIType, AuthType


@dataclass
class APIRequest:
    """API 請求數據結構"""
    method: str
    url: str
    headers: Dict[str, str]
    params: Dict[str, Any]
    data: Any
    timeout: int


@dataclass
class APIResponse:
    """API 響應數據結構"""
    status_code: int
    headers: Dict[str, str]
    data: Any
    error: Optional[str] = None


class APIError(Exception):
    """API 錯誤基類"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class BaseAPIHandler(ABC):
    """基礎 API 處理器"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if not config.validate():
            raise ValueError("無效的 API 配置")
    
    @abstractmethod
    def _prepare_request(self, method: str, endpoint: str, **kwargs) -> APIRequest:
        """準備請求"""
        pass
    
    @abstractmethod
    def _handle_response(self, response: Any) -> APIResponse:
        """處理響應"""
        pass
    
    @abstractmethod
    def _handle_error(self, error: Exception) -> APIError:
        """處理錯誤"""
        pass
    
    def _retry_on_error(self, func):
        """錯誤重試裝飾器"""
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(self.config.retry_count):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < self.config.retry_count - 1:
                        self.logger.warning(f"請求失敗，正在重試 ({attempt + 1}/{self.config.retry_count})")
                        time.sleep(self.config.retry_delay)
            raise self._handle_error(last_error)
        return wrapper
    
    @abstractmethod
    def request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """發送請求"""
        pass
    
    def get(self, endpoint: str, **kwargs) -> APIResponse:
        """GET 請求"""
        return this.request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> APIResponse:
        """POST 請求"""
        return this.request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> APIResponse:
        """PUT 請求"""
        return this.request("PUT", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> APIResponse:
        """DELETE 請求"""
        return this.request("DELETE", endpoint, **kwargs) 
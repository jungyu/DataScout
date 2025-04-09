#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自定義 API 處理器模組

提供自定義 API 的具體實現。
包括：
1. 自定義 API 處理器類
2. 請求處理
3. 響應處理
"""

import json
from typing import Dict, Any, Optional, List, Callable
from .base import BaseAPIHandler, APIRequest, APIResponse, APIError
from ..config import APIConfig, APIType, AuthType


class CustomAPIHandler(BaseAPIHandler):
    """自定義 API 處理器"""
    
    def __init__(self, config: APIConfig):
        if config.api_type != APIType.CUSTOM:
            raise ValueError("配置類型必須為 CUSTOM")
        super().__init__(config)
        self._request_interceptors: List[Callable] = []
        self._response_interceptors: List[Callable] = []
        self._error_interceptors: List[Callable] = []
    
    def _prepare_request(self, method: str, endpoint: str, **kwargs) -> APIRequest:
        """準備請求"""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = kwargs.get('headers', {}).copy()
        data = kwargs.get('data')
        timeout = kwargs.get('timeout', self.config.timeout)
        
        # 添加認證信息
        if self.config.auth_type == AuthType.API_KEY:
            headers['Authorization'] = f"Bearer {self.config.api_key}"
        elif self.config.auth_type == AuthType.BASIC:
            headers['Authorization'] = f"Basic {self.config.username}:{self.config.password}"
        elif self.config.auth_type == AuthType.JWT:
            headers['Authorization'] = f"Bearer {self.config.api_key}"
        
        # 添加通用請求頭
        headers.update({
            'Content-Type': 'application/json',
            'User-Agent': self.config.user_agent
        })
        
        # 添加自定義請求頭
        headers.update(self.config.headers)
        
        request = APIRequest(
            method=method,
            url=url,
            headers=headers,
            data=data,
            timeout=timeout
        )
        
        # 執行請求攔截器
        for interceptor in self._request_interceptors:
            request = interceptor(request)
        
        return request
    
    def _handle_response(self, response: Dict[str, Any]) -> APIResponse:
        """處理響應"""
        if not isinstance(response, dict):
            raise APIError("無效的響應格式")
        
        api_response = APIResponse(
            status_code=200,
            headers={},
            data=response
        )
        
        # 執行響應攔截器
        for interceptor in self._response_interceptors:
            api_response = interceptor(api_response)
        
        return api_response
    
    def _handle_error(self, error: Exception) -> APIError:
        """處理錯誤"""
        api_error = APIError(str(error))
        
        # 執行錯誤攔截器
        for interceptor in self._error_interceptors:
            api_error = interceptor(api_error)
        
        return api_error
    
    def add_request_interceptor(self, interceptor: Callable[[APIRequest], APIRequest]) -> None:
        """添加請求攔截器"""
        self._request_interceptors.append(interceptor)
    
    def add_response_interceptor(self, interceptor: Callable[[APIResponse], APIResponse]) -> None:
        """添加響應攔截器"""
        self._response_interceptors.append(interceptor)
    
    def add_error_interceptor(self, interceptor: Callable[[APIError], APIError]) -> None:
        """添加錯誤攔截器"""
        self._error_interceptors.append(interceptor)
    
    def remove_request_interceptor(self, interceptor: Callable[[APIRequest], APIRequest]) -> None:
        """移除請求攔截器"""
        if interceptor in self._request_interceptors:
            self._request_interceptors.remove(interceptor)
    
    def remove_response_interceptor(self, interceptor: Callable[[APIResponse], APIResponse]) -> None:
        """移除響應攔截器"""
        if interceptor in self._response_interceptors:
            self._response_interceptors.remove(interceptor)
    
    def remove_error_interceptor(self, interceptor: Callable[[APIError], APIError]) -> None:
        """移除錯誤攔截器"""
        if interceptor in self._error_interceptors:
            self._error_interceptors.remove(interceptor)
    
    def clear_interceptors(self) -> None:
        """清除所有攔截器"""
        self._request_interceptors.clear()
        self._response_interceptors.clear()
        self._error_interceptors.clear()
    
    @BaseAPIHandler._retry_on_error
    def request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """發送請求"""
        request = self._prepare_request(method, endpoint, **kwargs)
        
        try:
            # 這裡可以根據需要實現自定義的請求邏輯
            # 例如使用不同的 HTTP 客戶端庫
            response = self._make_request(request)
            return self._handle_response(response)
        except Exception as e:
            raise self._handle_error(e)
    
    def _make_request(self, request: APIRequest) -> Dict[str, Any]:
        """發送 HTTP 請求"""
        # 這裡可以根據配置選擇不同的 HTTP 客戶端
        # 例如 requests, aiohttp, httpx 等
        import requests
        
        response = requests.request(
            method=request.method,
            url=request.url,
            headers=request.headers,
            json=request.data,
            timeout=request.timeout
        )
        
        response.raise_for_status()
        return response.json() 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
REST API 處理器模組

提供 REST API 的具體實現。
包括：
1. REST API 處理器類
2. 請求認證
3. 響應處理
"""

import requests
from typing import Dict, Any, Optional
from .base import BaseAPIHandler, APIRequest, APIResponse, APIError
from src.extractors.handlers.api.api_handler import APIConfig, APIType, APIAuthType


class RESTAPIHandler(BaseAPIHandler):
    """REST API 處理器"""
    
    def __init__(self, config: APIConfig):
        if config.api_type != APIType.REST:
            raise ValueError("配置類型必須為 REST")
        super().__init__(config)
        self.session = requests.Session()
    
    def _prepare_request(self, method: str, endpoint: str, **kwargs) -> APIRequest:
        """準備請求"""
        # 使用 URLUtils 處理 URL
        url = self.url_utils.normalize_url(f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}")
        
        headers = kwargs.get('headers', {}).copy()
        params = kwargs.get('params', {}).copy()
        data = kwargs.get('data')
        timeout = kwargs.get('timeout', self.config.timeout)
        
        # 添加認證信息
        if self.config.auth_type == APIAuthType.API_KEY:
            headers['Authorization'] = f"Bearer {self.config.api_key}"
        elif self.config.auth_type == APIAuthType.BASIC:
            headers['Authorization'] = f"Basic {self.config.username}:{self.config.password}"
        
        # 添加通用請求頭
        headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': self.config.user_agent
        })
        
        return APIRequest(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout
        )
    
    def _handle_response(self, response: requests.Response) -> APIResponse:
        """處理響應"""
        try:
            # 使用 DataProcessor 處理響應數據
            data = self.data_processor.format_for_json(response.json())
        except ValueError:
            data = response.text
        
        return APIResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=data
        )
    
    def _handle_error(self, error: Exception) -> APIError:
        """處理錯誤"""
        if isinstance(error, requests.RequestException):
            return APIError(
                message=str(error),
                status_code=getattr(error.response, 'status_code', None)
            )
        return APIError(str(error))
    
    @BaseAPIHandler._retry_on_error
    def request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """發送請求"""
        request = self._prepare_request(method, endpoint, **kwargs)
        
        try:
            response = self.session.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                params=request.params,
                json=request.data,
                timeout=request.timeout
            )
            response.raise_for_status()
            return self._handle_response(response)
        except Exception as e:
            raise self._handle_error(e)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close() 
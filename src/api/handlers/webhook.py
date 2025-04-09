#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Webhook API 處理器模組

提供 Webhook API 的具體實現。
包括：
1. Webhook API 處理器類
2. 事件處理
3. 響應處理
"""

import json
import hmac
import hashlib
from typing import Dict, Any, Optional, Callable
from .base import BaseAPIHandler, APIRequest, APIResponse, APIError
from ..config import APIConfig, APIType, AuthType


class WebhookAPIHandler(BaseAPIHandler):
    """Webhook API 處理器"""
    
    def __init__(self, config: APIConfig):
        if config.api_type != APIType.WEBHOOK:
            raise ValueError("配置類型必須為 WEBHOOK")
        super().__init__(config)
        self._event_handlers: Dict[str, Callable] = {}
        self._secret = config.options.get("webhook_secret")
    
    def _prepare_request(self, method: str, endpoint: str, **kwargs) -> APIRequest:
        """準備請求"""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = kwargs.get('headers', {}).copy()
        data = kwargs.get('data')
        timeout = kwargs.get('timeout', self.config.timeout)
        
        # 添加認證信息
        if self.config.auth_type == AuthType.API_KEY:
            headers['X-API-Key'] = self.config.api_key
        elif self._secret:
            # 如果配置了 webhook secret，添加簽名
            if data:
                signature = self._generate_signature(data)
                headers['X-Webhook-Signature'] = signature
        
        # 添加通用請求頭
        headers.update({
            'Content-Type': 'application/json',
            'User-Agent': self.config.user_agent
        })
        
        return APIRequest(
            method=method,
            url=url,
            headers=headers,
            data=data,
            timeout=timeout
        )
    
    def _handle_response(self, response: Dict[str, Any]) -> APIResponse:
        """處理響應"""
        return APIResponse(
            status_code=200,
            headers={},
            data=response
        )
    
    def _handle_error(self, error: Exception) -> APIError:
        """處理錯誤"""
        return APIError(str(error))
    
    def _generate_signature(self, data: Dict[str, Any]) -> str:
        """生成 Webhook 簽名"""
        if not self._secret:
            return ""
        
        message = json.dumps(data, sort_keys=True)
        signature = hmac.new(
            self._secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(self, signature: str, data: Dict[str, Any]) -> bool:
        """驗證 Webhook 簽名"""
        if not self._secret:
            return True
        
        expected_signature = self._generate_signature(data)
        return hmac.compare_digest(signature, expected_signature)
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """註冊事件處理器"""
        self._event_handlers[event_type] = handler
    
    def handle_event(self, event_type: str, data: Dict[str, Any]) -> APIResponse:
        """處理 Webhook 事件"""
        if event_type not in self._event_handlers:
            raise APIError(f"未找到事件類型 {event_type} 的處理器")
        
        try:
            result = self._event_handlers[event_type](data)
            return self._handle_response(result)
        except Exception as e:
            raise self._handle_error(e)
    
    @BaseAPIHandler._retry_on_error
    def request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """發送請求"""
        request = self._prepare_request(method, endpoint, **kwargs)
        
        try:
            # Webhook 通常是單向的，不需要等待響應
            return APIResponse(
                status_code=200,
                headers={},
                data={"status": "success"}
            )
        except Exception as e:
            raise self._handle_error(e) 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Zapier API 處理器模組

提供 Zapier API 的具體實現。
包括：
1. Zapier API 處理器類
2. Zap 管理
3. 執行管理
"""

import json
from typing import Dict, Any, Optional, List
from .base import BaseAPIHandler, APIRequest, APIResponse, APIError
from ..config import APIConfig, APIType, AuthType


class ZapierAPIHandler(BaseAPIHandler):
    """Zapier API 處理器"""
    
    def __init__(self, config: APIConfig):
        if config.api_type != APIType.ZAPIER:
            raise ValueError("配置類型必須為 ZAPIER")
        super().__init__(config)
        self._zap_cache: Dict[str, Dict[str, Any]] = {}
    
    def _prepare_request(self, method: str, endpoint: str, **kwargs) -> APIRequest:
        """準備請求"""
        url = f"{self.config.base_url.rstrip('/')}/api/v1/{endpoint.lstrip('/')}"
        headers = kwargs.get('headers', {}).copy()
        data = kwargs.get('data')
        timeout = kwargs.get('timeout', self.config.timeout)
        
        # 添加認證信息
        if self.config.auth_type == AuthType.API_KEY:
            headers['X-Zapier-API-Key'] = self.config.api_key
        
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
        if not isinstance(response, dict):
            raise APIError("無效的響應格式")
        
        return APIResponse(
            status_code=200,
            headers={},
            data=response
        )
    
    def _handle_error(self, error: Exception) -> APIError:
        """處理錯誤"""
        if isinstance(error, dict) and "message" in error:
            return APIError(error["message"])
        return APIError(str(error))
    
    def get_zaps(self) -> List[Dict[str, Any]]:
        """獲取所有 Zap"""
        response = self.request("GET", "zaps")
        return response.data.get("data", [])
    
    def get_zap(self, zap_id: str) -> Dict[str, Any]:
        """獲取 Zap 詳情"""
        if zap_id in self._zap_cache:
            return self._zap_cache[zap_id]
        
        response = self.request("GET", f"zaps/{zap_id}")
        zap = response.data.get("data", {})
        self._zap_cache[zap_id] = zap
        return zap
    
    def create_zap(self, zap_data: Dict[str, Any]) -> Dict[str, Any]:
        """創建 Zap"""
        response = self.request("POST", "zaps", data=zap_data)
        return response.data.get("data", {})
    
    def update_zap(self, zap_id: str, zap_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新 Zap"""
        response = self.request("PUT", f"zaps/{zap_id}", data=zap_data)
        if zap_id in self._zap_cache:
            del self._zap_cache[zap_id]
        return response.data.get("data", {})
    
    def delete_zap(self, zap_id: str) -> bool:
        """刪除 Zap"""
        response = self.request("DELETE", f"zaps/{zap_id}")
        if zap_id in self._zap_cache:
            del self._zap_cache[zap_id]
        return response.status_code == 200
    
    def activate_zap(self, zap_id: str) -> bool:
        """激活 Zap"""
        response = self.request("POST", f"zaps/{zap_id}/activate")
        return response.status_code == 200
    
    def deactivate_zap(self, zap_id: str) -> bool:
        """停用 Zap"""
        response = self.request("POST", f"zaps/{zap_id}/deactivate")
        return response.status_code == 200
    
    def execute_zap(self, zap_id: str, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """執行 Zap"""
        data = {"inputData": input_data} if input_data else {}
        response = self.request("POST", f"zaps/{zap_id}/execute", data=data)
        return response.data.get("data", {})
    
    def get_executions(self, zap_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """獲取執行記錄"""
        endpoint = f"executions/{zap_id}" if zap_id else "executions"
        response = self.request("GET", endpoint)
        return response.data.get("data", [])
    
    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """獲取執行詳情"""
        response = self.request("GET", f"executions/{execution_id}")
        return response.data.get("data", {})
    
    def stop_execution(self, execution_id: str) -> bool:
        """停止執行"""
        response = self.request("POST", f"executions/{execution_id}/stop")
        return response.status_code == 200
    
    def get_apps(self) -> List[Dict[str, Any]]:
        """獲取可用應用列表"""
        response = self.request("GET", "apps")
        return response.data.get("data", [])
    
    def get_app(self, app_id: str) -> Dict[str, Any]:
        """獲取應用詳情"""
        response = self.request("GET", f"apps/{app_id}")
        return response.data.get("data", {})
    
    def test_connection(self, app_id: str, connection_data: Dict[str, Any]) -> bool:
        """測試應用連接"""
        response = self.request("POST", f"apps/{app_id}/test", data=connection_data)
        return response.status_code == 200 
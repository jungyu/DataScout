#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
IFTTT API 處理器模組

提供 IFTTT API 的具體實現。
包括：
1. IFTTT API 處理器類
2. Applet 管理
3. 執行管理
"""

import json
from typing import Dict, Any, Optional, List
from .base import BaseAPIHandler, APIRequest, APIResponse, APIError
from ..config import APIConfig, APIType, AuthType


class IFTTTAPIHandler(BaseAPIHandler):
    """IFTTT API 處理器"""
    
    def __init__(self, config: APIConfig):
        if config.api_type != APIType.IFTTT:
            raise ValueError("配置類型必須為 IFTTT")
        super().__init__(config)
        self._applet_cache: Dict[str, Dict[str, Any]] = {}
    
    def _prepare_request(self, method: str, endpoint: str, **kwargs) -> APIRequest:
        """準備請求"""
        url = f"{self.config.base_url.rstrip('/')}/api/v1/{endpoint.lstrip('/')}"
        headers = kwargs.get('headers', {}).copy()
        data = kwargs.get('data')
        timeout = kwargs.get('timeout', self.config.timeout)
        
        # 添加認證信息
        if self.config.auth_type == AuthType.API_KEY:
            headers['X-IFTTT-API-Key'] = self.config.api_key
        
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
    
    def get_applets(self) -> List[Dict[str, Any]]:
        """獲取所有 Applet"""
        response = self.request("GET", "applets")
        return response.data.get("data", [])
    
    def get_applet(self, applet_id: str) -> Dict[str, Any]:
        """獲取 Applet 詳情"""
        if applet_id in self._applet_cache:
            return self._applet_cache[applet_id]
        
        response = self.request("GET", f"applets/{applet_id}")
        applet = response.data.get("data", {})
        self._applet_cache[applet_id] = applet
        return applet
    
    def create_applet(self, applet_data: Dict[str, Any]) -> Dict[str, Any]:
        """創建 Applet"""
        response = self.request("POST", "applets", data=applet_data)
        return response.data.get("data", {})
    
    def update_applet(self, applet_id: str, applet_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新 Applet"""
        response = self.request("PUT", f"applets/{applet_id}", data=applet_data)
        if applet_id in self._applet_cache:
            del self._applet_cache[applet_id]
        return response.data.get("data", {})
    
    def delete_applet(self, applet_id: str) -> bool:
        """刪除 Applet"""
        response = self.request("DELETE", f"applets/{applet_id}")
        if applet_id in self._applet_cache:
            del self._applet_cache[applet_id]
        return response.status_code == 200
    
    def activate_applet(self, applet_id: str) -> bool:
        """激活 Applet"""
        response = self.request("POST", f"applets/{applet_id}/activate")
        return response.status_code == 200
    
    def deactivate_applet(self, applet_id: str) -> bool:
        """停用 Applet"""
        response = self.request("POST", f"applets/{applet_id}/deactivate")
        return response.status_code == 200
    
    def execute_applet(self, applet_id: str, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """執行 Applet"""
        data = {"inputData": input_data} if input_data else {}
        response = self.request("POST", f"applets/{applet_id}/execute", data=data)
        return response.data.get("data", {})
    
    def get_executions(self, applet_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """獲取執行記錄"""
        endpoint = f"executions/{applet_id}" if applet_id else "executions"
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
    
    def get_services(self) -> List[Dict[str, Any]]:
        """獲取可用服務列表"""
        response = self.request("GET", "services")
        return response.data.get("data", [])
    
    def get_service(self, service_id: str) -> Dict[str, Any]:
        """獲取服務詳情"""
        response = self.request("GET", f"services/{service_id}")
        return response.data.get("data", {})
    
    def test_connection(self, service_id: str, connection_data: Dict[str, Any]) -> bool:
        """測試服務連接"""
        response = self.request("POST", f"services/{service_id}/test", data=connection_data)
        return response.status_code == 200 
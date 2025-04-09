#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
N8N API 處理器模組

提供 N8N API 的具體實現。
包括：
1. N8N API 處理器類
2. 工作流管理
3. 執行管理
"""

import json
from typing import Dict, Any, Optional, List
from .base import BaseAPIHandler, APIRequest, APIResponse, APIError
from ..config import APIConfig, APIType, AuthType


class N8nAPIHandler(BaseAPIHandler):
    """N8N API 處理器"""
    
    def __init__(self, config: APIConfig):
        if config.api_type != APIType.N8N:
            raise ValueError("配置類型必須為 N8N")
        super().__init__(config)
        self._workflow_cache: Dict[str, Dict[str, Any]] = {}
    
    def _prepare_request(self, method: str, endpoint: str, **kwargs) -> APIRequest:
        """準備請求"""
        url = f"{self.config.base_url.rstrip('/')}/api/v1/{endpoint.lstrip('/')}"
        headers = kwargs.get('headers', {}).copy()
        data = kwargs.get('data')
        timeout = kwargs.get('timeout', self.config.timeout)
        
        # 添加認證信息
        if self.config.auth_type == AuthType.API_KEY:
            headers['X-N8N-API-KEY'] = self.config.api_key
        
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
    
    def get_workflows(self) -> List[Dict[str, Any]]:
        """獲取所有工作流"""
        response = self.request("GET", "workflows")
        return response.data.get("data", [])
    
    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """獲取工作流詳情"""
        if workflow_id in self._workflow_cache:
            return self._workflow_cache[workflow_id]
        
        response = self.request("GET", f"workflows/{workflow_id}")
        workflow = response.data.get("data", {})
        self._workflow_cache[workflow_id] = workflow
        return workflow
    
    def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """創建工作流"""
        response = self.request("POST", "workflows", data=workflow_data)
        return response.data.get("data", {})
    
    def update_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新工作流"""
        response = self.request("PUT", f"workflows/{workflow_id}", data=workflow_data)
        if workflow_id in self._workflow_cache:
            del self._workflow_cache[workflow_id]
        return response.data.get("data", {})
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """刪除工作流"""
        response = self.request("DELETE", f"workflows/{workflow_id}")
        if workflow_id in self._workflow_cache:
            del self._workflow_cache[workflow_id]
        return response.status_code == 200
    
    def activate_workflow(self, workflow_id: str) -> bool:
        """激活工作流"""
        response = self.request("POST", f"workflows/{workflow_id}/activate")
        return response.status_code == 200
    
    def deactivate_workflow(self, workflow_id: str) -> bool:
        """停用工作流"""
        response = self.request("POST", f"workflows/{workflow_id}/deactivate")
        return response.status_code == 200
    
    def execute_workflow(self, workflow_id: str, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """執行工作流"""
        data = {"inputData": input_data} if input_data else {}
        response = self.request("POST", f"workflows/{workflow_id}/execute", data=data)
        return response.data.get("data", {})
    
    def get_executions(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """獲取執行記錄"""
        endpoint = f"executions/{workflow_id}" if workflow_id else "executions"
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
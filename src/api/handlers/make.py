#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Make API 處理器模組

提供 Make（原 Integromat）API 的具體實現。
包括：
1. Make API 處理器類
2. 場景管理
3. 執行管理
"""

import json
from typing import Dict, Any, Optional, List
from .base import BaseAPIHandler, APIRequest, APIResponse, APIError
from ..config import APIConfig, APIType, AuthType


class MakeAPIHandler(BaseAPIHandler):
    """Make API 處理器"""
    
    def __init__(self, config: APIConfig):
        if config.api_type != APIType.MAKE:
            raise ValueError("配置類型必須為 MAKE")
        super().__init__(config)
        self._scenario_cache: Dict[str, Dict[str, Any]] = {}
    
    def _prepare_request(self, method: str, endpoint: str, **kwargs) -> APIRequest:
        """準備請求"""
        url = f"{self.config.base_url.rstrip('/')}/api/v1/{endpoint.lstrip('/')}"
        headers = kwargs.get('headers', {}).copy()
        data = kwargs.get('data')
        timeout = kwargs.get('timeout', self.config.timeout)
        
        # 添加認證信息
        if self.config.auth_type == AuthType.API_KEY:
            headers['Authorization'] = f"Bearer {self.config.api_key}"
        
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
    
    def get_scenarios(self) -> List[Dict[str, Any]]:
        """獲取所有場景"""
        response = self.request("GET", "scenarios")
        return response.data.get("data", [])
    
    def get_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """獲取場景詳情"""
        if scenario_id in self._scenario_cache:
            return self._scenario_cache[scenario_id]
        
        response = self.request("GET", f"scenarios/{scenario_id}")
        scenario = response.data.get("data", {})
        self._scenario_cache[scenario_id] = scenario
        return scenario
    
    def create_scenario(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """創建場景"""
        response = self.request("POST", "scenarios", data=scenario_data)
        return response.data.get("data", {})
    
    def update_scenario(self, scenario_id: str, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新場景"""
        response = self.request("PUT", f"scenarios/{scenario_id}", data=scenario_data)
        if scenario_id in self._scenario_cache:
            del self._scenario_cache[scenario_id]
        return response.data.get("data", {})
    
    def delete_scenario(self, scenario_id: str) -> bool:
        """刪除場景"""
        response = self.request("DELETE", f"scenarios/{scenario_id}")
        if scenario_id in self._scenario_cache:
            del self._scenario_cache[scenario_id]
        return response.status_code == 200
    
    def activate_scenario(self, scenario_id: str) -> bool:
        """激活場景"""
        response = self.request("POST", f"scenarios/{scenario_id}/activate")
        return response.status_code == 200
    
    def deactivate_scenario(self, scenario_id: str) -> bool:
        """停用場景"""
        response = self.request("POST", f"scenarios/{scenario_id}/deactivate")
        return response.status_code == 200
    
    def execute_scenario(self, scenario_id: str, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """執行場景"""
        data = {"inputData": input_data} if input_data else {}
        response = self.request("POST", f"scenarios/{scenario_id}/execute", data=data)
        return response.data.get("data", {})
    
    def get_executions(self, scenario_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """獲取執行記錄"""
        endpoint = f"executions/{scenario_id}" if scenario_id else "executions"
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
    
    def get_modules(self) -> List[Dict[str, Any]]:
        """獲取可用模組列表"""
        response = self.request("GET", "modules")
        return response.data.get("data", [])
    
    def get_module(self, module_id: str) -> Dict[str, Any]:
        """獲取模組詳情"""
        response = self.request("GET", f"modules/{module_id}")
        return response.data.get("data", {})
    
    def test_connection(self, module_id: str, connection_data: Dict[str, Any]) -> bool:
        """測試模組連接"""
        response = self.request("POST", f"modules/{module_id}/test", data=connection_data)
        return response.status_code == 200 
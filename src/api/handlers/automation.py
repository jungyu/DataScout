#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自動化 API 處理器模組

提供自動化 API 的具體實現。
包括：
1. 自動化 API 處理器類
2. 任務管理
3. 執行管理
"""

import json
import time
from typing import Dict, Any, Optional, List, Callable
from .base import BaseAPIHandler, APIRequest, APIResponse, APIError
from ..config import APIConfig, APIType, AuthType


class AutomationAPIHandler(BaseAPIHandler):
    """自動化 API 處理器"""
    
    def __init__(self, config: APIConfig):
        if config.api_type != APIType.AUTOMATION:
            raise ValueError("配置類型必須為 AUTOMATION")
        super().__init__(config)
        self._task_cache: Dict[str, Dict[str, Any]] = {}
        self._task_handlers: Dict[str, Callable] = {}
    
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
    
    def get_tasks(self) -> List[Dict[str, Any]]:
        """獲取所有任務"""
        response = self.request("GET", "tasks")
        return response.data.get("data", [])
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """獲取任務詳情"""
        if task_id in self._task_cache:
            return self._task_cache[task_id]
        
        response = self.request("GET", f"tasks/{task_id}")
        task = response.data.get("data", {})
        self._task_cache[task_id] = task
        return task
    
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """創建任務"""
        response = self.request("POST", "tasks", data=task_data)
        return response.data.get("data", {})
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新任務"""
        response = self.request("PUT", f"tasks/{task_id}", data=task_data)
        if task_id in self._task_cache:
            del self._task_cache[task_id]
        return response.data.get("data", {})
    
    def delete_task(self, task_id: str) -> bool:
        """刪除任務"""
        response = self.request("DELETE", f"tasks/{task_id}")
        if task_id in self._task_cache:
            del self._task_cache[task_id]
        return response.status_code == 200
    
    def activate_task(self, task_id: str) -> bool:
        """激活任務"""
        response = self.request("POST", f"tasks/{task_id}/activate")
        return response.status_code == 200
    
    def deactivate_task(self, task_id: str) -> bool:
        """停用任務"""
        response = self.request("POST", f"tasks/{task_id}/deactivate")
        return response.status_code == 200
    
    def execute_task(self, task_id: str, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """執行任務"""
        data = {"inputData": input_data} if input_data else {}
        response = self.request("POST", f"tasks/{task_id}/execute", data=data)
        return response.data.get("data", {})
    
    def get_executions(self, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """獲取執行記錄"""
        endpoint = f"executions/{task_id}" if task_id else "executions"
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
    
    def register_task_handler(self, task_type: str, handler: Callable) -> None:
        """註冊任務處理器"""
        self._task_handlers[task_type] = handler
    
    def unregister_task_handler(self, task_type: str) -> None:
        """註銷任務處理器"""
        if task_type in self._task_handlers:
            del self._task_handlers[task_type]
    
    def handle_task(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理任務"""
        if task_type not in self._task_handlers:
            raise APIError(f"未找到任務類型 {task_type} 的處理器")
        
        try:
            result = self._task_handlers[task_type](task_data)
            return result
        except Exception as e:
            raise self._handle_error(e)
    
    def schedule_task(self, task_id: str, schedule: Dict[str, Any]) -> bool:
        """調度任務"""
        response = self.request("POST", f"tasks/{task_id}/schedule", data=schedule)
        return response.status_code == 200
    
    def cancel_schedule(self, task_id: str) -> bool:
        """取消調度"""
        response = self.request("POST", f"tasks/{task_id}/cancel-schedule")
        return response.status_code == 200
    
    def get_schedules(self, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """獲取調度列表"""
        endpoint = f"schedules/{task_id}" if task_id else "schedules"
        response = self.request("GET", endpoint)
        return response.data.get("data", [])
    
    def get_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """獲取調度詳情"""
        response = self.request("GET", f"schedules/{schedule_id}")
        return response.data.get("data", {})
    
    def update_schedule(self, schedule_id: str, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新調度"""
        response = self.request("PUT", f"schedules/{schedule_id}", data=schedule_data)
        return response.data.get("data", {})
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """刪除調度"""
        response = self.request("DELETE", f"schedules/{schedule_id}")
        return response.status_code == 200 
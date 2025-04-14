#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Make.com 處理器
提供與 Make.com 平台的整合功能
"""

import json
import logging
import requests
from typing import Dict, List, Optional, Union, Any
from api_client.core.base_client import BaseClient
from api_client.core.exceptions import APIError, AuthenticationError, RequestError

class MakeHandler(BaseClient):
    """Make.com 處理器類"""
    
    def __init__(self, config: Union[Dict, Any]):
        """初始化 Make.com 處理器
        
        Args:
            config: 配置參數，可以是字典或配置對象
                  必須包含 api_key 和 base_url
        """
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # 設置 API 相關參數
        self.api_key = self.config.get("api_key")
        self.base_url = self.config.get("base_url", "https://api.make.com/v1")
        self.timeout = self.config.get("timeout", 30)
        self.retry_count = self.config.get("retry_count", 3)
        self.retry_delay = self.config.get("retry_delay", 1)
        
        # 驗證必要參數
        if not self.api_key:
            raise AuthenticationError("Make.com API key is required")
    
    def _get_headers(self) -> Dict[str, str]:
        """獲取請求頭
        
        Returns:
            Dict[str, str]: 請求頭字典
        """
        return {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
    
    def trigger_scenario(self, data: Dict) -> Dict:
        """觸發場景
        
        Args:
            data: 要發送的數據
            
        Returns:
            Dict: 響應結果
            
        Raises:
            RequestError: 請求錯誤
        """
        try:
            response = self._make_request(
                "POST",
                f"{self.base_url}/scenarios/trigger",
                json=data
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to trigger scenario: {str(e)}")
            raise RequestError(f"Failed to trigger scenario: {str(e)}")
    
    def trigger_scenario_with_json(self, data: Dict) -> Dict:
        """使用 JSON 數據觸發場景
        
        Args:
            data: JSON 格式的數據
            
        Returns:
            Dict: 響應結果
        """
        return self.trigger_scenario(data)
    
    def trigger_scenario_with_form(self, data: Dict) -> Dict:
        """使用表單數據觸發場景
        
        Args:
            data: 表單格式的數據
            
        Returns:
            Dict: 響應結果
        """
        headers = self._get_headers()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        return self.trigger_scenario(data)
    
    def trigger_scenario_with_xml(self, data: str) -> Dict:
        """使用 XML 數據觸發場景
        
        Args:
            data: XML 格式的數據
            
        Returns:
            Dict: 響應結果
        """
        headers = self._get_headers()
        headers["Content-Type"] = "application/xml"
        return self.trigger_scenario({"xml": data})
    
    def trigger_scenario_with_text(self, data: str) -> Dict:
        """使用純文本數據觸發場景
        
        Args:
            data: 純文本數據
            
        Returns:
            Dict: 響應結果
        """
        headers = self._get_headers()
        headers["Content-Type"] = "text/plain"
        return self.trigger_scenario({"text": data})
    
    def trigger_scenario_with_binary(self, data: bytes) -> Dict:
        """使用二進制數據觸發場景
        
        Args:
            data: 二進制數據
            
        Returns:
            Dict: 響應結果
        """
        headers = self._get_headers()
        headers["Content-Type"] = "application/octet-stream"
        return self.trigger_scenario({"binary": data})
    
    def trigger_scenario_with_file(self, file_path: str) -> Dict:
        """使用文件觸發場景
        
        Args:
            file_path: 文件路徑
            
        Returns:
            Dict: 響應結果
        """
        try:
            with open(file_path, "rb") as f:
                file_data = f.read()
            return self.trigger_scenario_with_binary(file_data)
        except Exception as e:
            self.logger.error(f"Failed to read file: {str(e)}")
            raise RequestError(f"Failed to read file: {str(e)}")
    
    def get_scenario_info(self, scenario_id: str) -> Dict:
        """獲取場景信息
        
        Args:
            scenario_id: 場景 ID
            
        Returns:
            Dict: 場景信息
            
        Raises:
            RequestError: 請求錯誤
        """
        try:
            response = self._make_request(
                "GET",
                f"{self.base_url}/scenarios/{scenario_id}"
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to get scenario info: {str(e)}")
            raise RequestError(f"Failed to get scenario info: {str(e)}")
    
    def list_scenarios(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """獲取場景列表
        
        Args:
            limit: 每頁數量
            offset: 偏移量
            
        Returns:
            List[Dict]: 場景列表
            
        Raises:
            RequestError: 請求錯誤
        """
        try:
            response = self._make_request(
                "GET",
                f"{self.base_url}/scenarios",
                params={"limit": limit, "offset": offset}
            )
            return response.get("data", [])
        except Exception as e:
            self.logger.error(f"Failed to list scenarios: {str(e)}")
            raise RequestError(f"Failed to list scenarios: {str(e)}")
    
    def execute_scenario(self, scenario_id: str, data: Optional[Dict] = None) -> Dict:
        """執行場景
        
        Args:
            scenario_id: 場景 ID
            data: 執行數據
            
        Returns:
            Dict: 執行結果
            
        Raises:
            RequestError: 請求錯誤
        """
        try:
            response = self._make_request(
                "POST",
                f"{self.base_url}/scenarios/{scenario_id}/execute",
                json=data or {}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to execute scenario: {str(e)}")
            raise RequestError(f"Failed to execute scenario: {str(e)}")
    
    def get_execution_status(self, execution_id: str) -> Dict:
        """獲取執行狀態
        
        Args:
            execution_id: 執行 ID
            
        Returns:
            Dict: 執行狀態
            
        Raises:
            RequestError: 請求錯誤
        """
        try:
            response = self._make_request(
                "GET",
                f"{self.base_url}/executions/{execution_id}"
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to get execution status: {str(e)}")
            raise RequestError(f"Failed to get execution status: {str(e)}")
    
    def list_executions(self, scenario_id: Optional[str] = None, 
                       limit: int = 100, offset: int = 0) -> List[Dict]:
        """獲取執行列表
        
        Args:
            scenario_id: 場景 ID（可選）
            limit: 每頁數量
            offset: 偏移量
            
        Returns:
            List[Dict]: 執行列表
            
        Raises:
            RequestError: 請求錯誤
        """
        try:
            params = {"limit": limit, "offset": offset}
            if scenario_id:
                params["scenarioId"] = scenario_id
            
            response = self._make_request(
                "GET",
                f"{self.base_url}/executions",
                params=params
            )
            return response.get("data", [])
        except Exception as e:
            self.logger.error(f"Failed to list executions: {str(e)}")
            raise RequestError(f"Failed to list executions: {str(e)}")
    
    def _make_request(self, method: str, url: str, **kwargs) -> Dict:
        """發送 HTTP 請求
        
        Args:
            method: 請求方法
            url: 請求 URL
            **kwargs: 請求參數
            
        Returns:
            Dict: 響應結果
            
        Raises:
            APIError: API 錯誤
            AuthenticationError: 認證錯誤
            RequestError: 請求錯誤
        """
        headers = self._get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        
        for attempt in range(self.retry_count):
            try:
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    **kwargs
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status_code == 403:
                    raise AuthenticationError("Insufficient permissions")
                elif response.status_code == 404:
                    raise RequestError("Resource not found")
                elif response.status_code == 429:
                    if attempt < self.retry_count - 1:
                        time.sleep(self.retry_delay)
                        continue
                    raise RequestError("Rate limit exceeded")
                else:
                    raise APIError(f"API error: {response.text}")
            except requests.exceptions.RequestException as e:
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise RequestError(f"Request failed: {str(e)}")
        
        raise RequestError("Max retries exceeded") 
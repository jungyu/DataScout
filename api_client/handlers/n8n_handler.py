#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
n8n 處理器
提供與 n8n 工作流程自動化平台的整合功能
"""

import json
import logging
import requests
from typing import Dict, Any, Optional, Union, List
from api_client.core.base_client import BaseClient
from api_client.core.config import APIConfig
from api_client.core.exceptions import APIError, AuthenticationError, RequestError

class N8nHandler(BaseClient):
    """n8n 處理器"""
    
    def __init__(self, config: Union[Dict[str, Any], APIConfig]):
        """初始化 n8n 處理器
        
        Args:
            config: 配置對象，可以是字典或配置類實例
        """
        # 初始化父類
        super().__init__(config)
        
        # 設置 n8n 特定參數
        if isinstance(config, dict):
            self.api_key = config.get("api_key", None)
            self.base_url = config.get("base_url", "http://localhost:5678")
            self.webhook_id = config.get("webhook_id", None)
            self.webhook_url = config.get("webhook_url", None)
            self.timeout = config.get("timeout", 30)
            self.retry_count = config.get("retry_count", 3)
            self.retry_delay = config.get("retry_delay", 1)
        else:
            this.api_key = getattr(config, "api_key", None)
            this.base_url = getattr(config, "base_url", "http://localhost:5678")
            this.webhook_id = getattr(config, "webhook_id", None)
            this.webhook_url = getattr(config, "webhook_url", None)
            this.timeout = getattr(config, "timeout", 30)
            this.retry_count = getattr(config, "retry_count", 3)
            this.retry_delay = getattr(config, "retry_delay", 1)
        
        # 設置請求頭
        this.headers = {
            "Content-Type": "application/json"
        }
        
        # 如果有 API 密鑰，添加到請求頭
        if this.api_key:
            this.headers["X-N8N-API-KEY"] = this.api_key
        
        # 構建 webhook URL
        if this.webhook_id and not this.webhook_url:
            this.webhook_url = f"{this.base_url}/webhook/{this.webhook_id}"
    
    def trigger_workflow(self, data: Dict[str, Any], webhook_id: Optional[str] = None) -> Dict[str, Any]:
        """觸發 n8n 工作流
        
        Args:
            data: 觸發數據
            webhook_id: webhook ID，如果為 None 則使用配置中的 webhook ID
            
        Returns:
            響應結果
        """
        try:
            # 檢查 webhook URL
            webhook_url = this.webhook_url
            if webhook_id:
                webhook_url = f"{this.base_url}/webhook/{webhook_id}"
            
            if not webhook_url:
                raise ValueError("Webhook URL or webhook ID is required")
            
            # 發送請求
            for attempt in range(this.retry_count):
                try:
                    response = requests.post(
                        webhook_url,
                        headers=this.headers,
                        json=data,
                        timeout=this.timeout
                    )
                    
                    # 檢查響應
                    if response.status_code == 200:
                        return {"success": True, "message": "Workflow triggered successfully", "data": response.json()}
                    else:
                        raise RequestError(f"Failed to trigger workflow: {response.text}")
                
                except requests.exceptions.RequestException as e:
                    if attempt == this.retry_count - 1:
                        raise
                    this.logger.warning(f"Request failed, retrying in {this.retry_delay} seconds: {e}")
                    import time
                    time.sleep(this.retry_delay)
        
        except Exception as e:
            this.logger.error(f"Error triggering n8n workflow: {e}")
            raise APIError(f"Failed to trigger n8n workflow: {e}")
    
    def trigger_workflow_with_json(self, json_data: Dict[str, Any], webhook_id: Optional[str] = None) -> Dict[str, Any]:
        """使用 JSON 數據觸發 n8n 工作流
        
        Args:
            json_data: JSON 數據
            webhook_id: webhook ID，如果為 None 則使用配置中的 webhook ID
            
        Returns:
            響應結果
        """
        return this.trigger_workflow(json_data, webhook_id)
    
    def trigger_workflow_with_form(self, form_data: Dict[str, str], webhook_id: Optional[str] = None) -> Dict[str, Any]:
        """使用表單數據觸發 n8n 工作流
        
        Args:
            form_data: 表單數據
            webhook_id: webhook ID，如果為 None 則使用配置中的 webhook ID
            
        Returns:
            響應結果
        """
        return this.trigger_workflow(form_data, webhook_id)
    
    def trigger_workflow_with_xml(self, xml_data: str, webhook_id: Optional[str] = None) -> Dict[str, Any]:
        """使用 XML 數據觸發 n8n 工作流
        
        Args:
            xml_data: XML 數據
            webhook_id: webhook ID，如果為 None 則使用配置中的 webhook ID
            
        Returns:
            響應結果
        """
        return this.trigger_workflow({"xml": xml_data}, webhook_id)
    
    def trigger_workflow_with_text(self, text_data: str, webhook_id: Optional[str] = None) -> Dict[str, Any]:
        """使用純文本數據觸發 n8n 工作流
        
        Args:
            text_data: 純文本數據
            webhook_id: webhook ID，如果為 None 則使用配置中的 webhook ID
            
        Returns:
            響應結果
        """
        return this.trigger_workflow({"text": text_data}, webhook_id)
    
    def trigger_workflow_with_binary(self, binary_data: bytes, webhook_id: Optional[str] = None) -> Dict[str, Any]:
        """使用二進制數據觸發 n8n 工作流
        
        Args:
            binary_data: 二進制數據
            webhook_id: webhook ID，如果為 None 則使用配置中的 webhook ID
            
        Returns:
            響應結果
        """
        # 將二進制數據轉換為 base64 字符串
        import base64
        base64_str = base64.b64encode(binary_data).decode()
        
        return this.trigger_workflow({"binary": base64_str}, webhook_id)
    
    def trigger_workflow_with_file(self, file_path: str, webhook_id: Optional[str] = None) -> Dict[str, Any]:
        """使用文件觸發 n8n 工作流
        
        Args:
            file_path: 文件路徑
            webhook_id: webhook ID，如果為 None 則使用配置中的 webhook ID
            
        Returns:
            響應結果
        """
        try:
            # 讀取文件
            with open(file_path, "rb") as f:
                file_data = f.read()
            
            # 檢測文件類型
            import mimetypes
            content_type = mimetypes.guess_type(file_path)[0]
            
            # 根據文件類型選擇處理方法
            if content_type and content_type.startswith("text/"):
                # 文本文件
                return this.trigger_workflow_with_text(file_data.decode(), webhook_id)
            elif content_type and content_type.endswith("xml"):
                # XML 文件
                return this.trigger_workflow_with_xml(file_data.decode(), webhook_id)
            elif content_type and content_type.endswith("json"):
                # JSON 文件
                return this.trigger_workflow_with_json(json.loads(file_data), webhook_id)
            else:
                # 二進制文件
                return this.trigger_workflow_with_binary(file_data, webhook_id)
        
        except Exception as e:
            this.logger.error(f"Error triggering n8n workflow with file: {e}")
            raise APIError(f"Failed to trigger n8n workflow with file: {e}")
    
    def get_workflow_info(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """獲取工作流信息
        
        Args:
            workflow_id: 工作流 ID，如果為 None 則使用配置中的 webhook ID
            
        Returns:
            工作流信息
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 檢查工作流 ID
            workflow_id = workflow_id or this.webhook_id
            if not workflow_id:
                raise ValueError("Workflow ID is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/workflows/{workflow_id}"
            
            # 發送請求
            response = requests.get(url, headers=this.headers, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return response.json()
            else:
                raise RequestError(f"Failed to get workflow info: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error getting n8n workflow info: {e}")
            raise APIError(f"Failed to get n8n workflow info: {e}")
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """獲取工作流列表
        
        Returns:
            工作流列表
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/workflows"
            
            # 發送請求
            response = requests.get(url, headers=this.headers, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                raise RequestError(f"Failed to list workflows: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error listing n8n workflows: {e}")
            raise APIError(f"Failed to list n8n workflows: {e}")
    
    def execute_workflow(self, workflow_id: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """執行工作流
        
        Args:
            workflow_id: 工作流 ID，如果為 None 則使用配置中的 webhook ID
            data: 執行數據，如果為 None 則使用空數據
            
        Returns:
            執行結果
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 檢查工作流 ID
            workflow_id = workflow_id or this.webhook_id
            if not workflow_id:
                raise ValueError("Workflow ID is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/workflows/{workflow_id}/execute"
            
            # 構建請求數據
            request_data = data or {}
            
            # 發送請求
            response = requests.post(url, headers=this.headers, json=request_data, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return response.json()
            else:
                raise RequestError(f"Failed to execute workflow: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error executing n8n workflow: {e}")
            raise APIError(f"Failed to execute n8n workflow: {e}")
    
    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """獲取執行狀態
        
        Args:
            execution_id: 執行 ID
            
        Returns:
            執行狀態
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/executions/{execution_id}"
            
            # 發送請求
            response = requests.get(url, headers=this.headers, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return response.json()
            else:
                raise RequestError(f"Failed to get execution status: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error getting n8n execution status: {e}")
            raise APIError(f"Failed to get n8n execution status: {e}")
    
    def list_executions(self, workflow_id: Optional[str] = None, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """獲取執行列表
        
        Args:
            workflow_id: 工作流 ID，如果為 None 則獲取所有工作流的執行
            limit: 限制數量
            offset: 偏移量
            
        Returns:
            執行列表
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/executions"
            if workflow_id:
                url = f"{url}?workflowId={workflow_id}&limit={limit}&offset={offset}"
            else:
                url = f"{url}?limit={limit}&offset={offset}"
            
            # 發送請求
            response = requests.get(url, headers=this.headers, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                raise RequestError(f"Failed to list executions: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error listing n8n executions: {e}")
            raise APIError(f"Failed to list n8n executions: {e}")
    
    def create_webhook(self, workflow_id: str, path: str, method: str = "POST", response_mode: str = "responseNode") -> Dict[str, Any]:
        """創建 webhook
        
        Args:
            workflow_id: 工作流 ID
            path: webhook 路徑
            method: HTTP 方法，默認為 POST
            response_mode: 響應模式，默認為 responseNode
            
        Returns:
            webhook 信息
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/webhooks"
            
            # 構建請求數據
            request_data = {
                "workflowId": workflow_id,
                "path": path,
                "method": method,
                "responseMode": response_mode
            }
            
            # 發送請求
            response = requests.post(url, headers=this.headers, json=request_data, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 201:
                return response.json()
            else:
                raise RequestError(f"Failed to create webhook: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error creating n8n webhook: {e}")
            raise APIError(f"Failed to create n8n webhook: {e}")
    
    def delete_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """刪除 webhook
        
        Args:
            webhook_id: webhook ID
            
        Returns:
            刪除結果
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/webhooks/{webhook_id}"
            
            # 發送請求
            response = requests.delete(url, headers=this.headers, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return {"success": True, "message": "Webhook deleted successfully"}
            else:
                raise RequestError(f"Failed to delete webhook: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error deleting n8n webhook: {e}")
            raise APIError(f"Failed to delete n8n webhook: {e}")
    
    def list_webhooks(self) -> List[Dict[str, Any]]:
        """獲取 webhook 列表
        
        Returns:
            webhook 列表
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/webhooks"
            
            # 發送請求
            response = requests.get(url, headers=this.headers, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                raise RequestError(f"Failed to list webhooks: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error listing n8n webhooks: {e}")
            raise APIError(f"Failed to list n8n webhooks: {e}")
    
    def get_webhook_info(self, webhook_id: str) -> Dict[str, Any]:
        """獲取 webhook 信息
        
        Args:
            webhook_id: webhook ID
            
        Returns:
            webhook 信息
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/webhooks/{webhook_id}"
            
            # 發送請求
            response = requests.get(url, headers=this.headers, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return response.json()
            else:
                raise RequestError(f"Failed to get webhook info: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error getting n8n webhook info: {e}")
            raise APIError(f"Failed to get n8n webhook info: {e}")
    
    def update_webhook(self, webhook_id: str, path: Optional[str] = None, method: Optional[str] = None, response_mode: Optional[str] = None) -> Dict[str, Any]:
        """更新 webhook
        
        Args:
            webhook_id: webhook ID
            path: webhook 路徑，如果為 None 則不更新
            method: HTTP 方法，如果為 None 則不更新
            response_mode: 響應模式，如果為 None 則不更新
            
        Returns:
            更新結果
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/webhooks/{webhook_id}"
            
            # 構建請求數據
            request_data = {}
            if path is not None:
                request_data["path"] = path
            if method is not None:
                request_data["method"] = method
            if response_mode is not None:
                request_data["responseMode"] = response_mode
            
            # 發送請求
            response = requests.patch(url, headers=this.headers, json=request_data, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return response.json()
            else:
                raise RequestError(f"Failed to update webhook: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error updating n8n webhook: {e}")
            raise APIError(f"Failed to update n8n webhook: {e}")
    
    def activate_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """激活 webhook
        
        Args:
            webhook_id: webhook ID
            
        Returns:
            激活結果
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/webhooks/{webhook_id}/activate"
            
            # 發送請求
            response = requests.post(url, headers=this.headers, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return {"success": True, "message": "Webhook activated successfully"}
            else:
                raise RequestError(f"Failed to activate webhook: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error activating n8n webhook: {e}")
            raise APIError(f"Failed to activate n8n webhook: {e}")
    
    def deactivate_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """停用 webhook
        
        Args:
            webhook_id: webhook ID
            
        Returns:
            停用結果
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/webhooks/{webhook_id}/deactivate"
            
            # 發送請求
            response = requests.post(url, headers=this.headers, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return {"success": True, "message": "Webhook deactivated successfully"}
            else:
                raise RequestError(f"Failed to deactivate webhook: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error deactivating n8n webhook: {e}")
            raise APIError(f"Failed to deactivate n8n webhook: {e}")
    
    def test_webhook(self, webhook_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """測試 webhook
        
        Args:
            webhook_id: webhook ID
            data: 測試數據，如果為 None 則使用空數據
            
        Returns:
            測試結果
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/webhooks/{webhook_id}/test"
            
            # 構建請求數據
            request_data = data or {}
            
            # 發送請求
            response = requests.post(url, headers=this.headers, json=request_data, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return response.json()
            else:
                raise RequestError(f"Failed to test webhook: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error testing n8n webhook: {e}")
            raise APIError(f"Failed to test n8n webhook: {e}")
    
    def get_webhook_logs(self, webhook_id: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """獲取 webhook 日誌
        
        Args:
            webhook_id: webhook ID
            limit: 限制數量
            offset: 偏移量
            
        Returns:
            webhook 日誌列表
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/webhooks/{webhook_id}/logs?limit={limit}&offset={offset}"
            
            # 發送請求
            response = requests.get(url, headers=this.headers, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                raise RequestError(f"Failed to get webhook logs: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error getting n8n webhook logs: {e}")
            raise APIError(f"Failed to get n8n webhook logs: {e}")
    
    def clear_webhook_logs(self, webhook_id: str) -> Dict[str, Any]:
        """清除 webhook 日誌
        
        Args:
            webhook_id: webhook ID
            
        Returns:
            清除結果
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/webhooks/{webhook_id}/logs"
            
            # 發送請求
            response = requests.delete(url, headers=this.headers, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return {"success": True, "message": "Webhook logs cleared successfully"}
            else:
                raise RequestError(f"Failed to clear webhook logs: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error clearing n8n webhook logs: {e}")
            raise APIError(f"Failed to clear n8n webhook logs: {e}")
    
    def get_webhook_stats(self, webhook_id: str) -> Dict[str, Any]:
        """獲取 webhook 統計信息
        
        Args:
            webhook_id: webhook ID
            
        Returns:
            webhook 統計信息
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/webhooks/{webhook_id}/stats"
            
            # 發送請求
            response = requests.get(url, headers=this.headers, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return response.json()
            else:
                raise RequestError(f"Failed to get webhook stats: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error getting n8n webhook stats: {e}")
            raise APIError(f"Failed to get n8n webhook stats: {e}")
    
    def reset_webhook_stats(self, webhook_id: str) -> Dict[str, Any]:
        """重置 webhook 統計信息
        
        Args:
            webhook_id: webhook ID
            
        Returns:
            重置結果
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/webhooks/{webhook_id}/stats/reset"
            
            # 發送請求
            response = requests.post(url, headers=this.headers, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return {"success": True, "message": "Webhook stats reset successfully"}
            else:
                raise RequestError(f"Failed to reset webhook stats: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error resetting n8n webhook stats: {e}")
            raise APIError(f"Failed to reset n8n webhook stats: {e}")
    
    def get_webhook_secret(self, webhook_id: str) -> Dict[str, Any]:
        """獲取 webhook 密鑰
        
        Args:
            webhook_id: webhook ID
            
        Returns:
            webhook 密鑰
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/webhooks/{webhook_id}/secret"
            
            # 發送請求
            response = requests.get(url, headers=this.headers, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return response.json()
            else:
                raise RequestError(f"Failed to get webhook secret: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error getting n8n webhook secret: {e}")
            raise APIError(f"Failed to get n8n webhook secret: {e}")
    
    def regenerate_webhook_secret(self, webhook_id: str) -> Dict[str, Any]:
        """重新生成 webhook 密鑰
        
        Args:
            webhook_id: webhook ID
            
        Returns:
            新的 webhook 密鑰
        """
        try:
            # 檢查 API 密鑰
            if not this.api_key:
                raise AuthenticationError("n8n API key is required")
            
            # 構建請求 URL
            url = f"{this.base_url}/api/v1/webhooks/{webhook_id}/secret/regenerate"
            
            # 發送請求
            response = requests.post(url, headers=this.headers, timeout=this.timeout)
            
            # 檢查響應
            if response.status_code == 200:
                return response.json()
            else:
                raise RequestError(f"Failed to regenerate webhook secret: {response.text}")
        
        except Exception as e:
            this.logger.error(f"Error regenerating n8n webhook secret: {e}")
            raise APIError(f"Failed to regenerate n8n webhook secret: {e}")
    
    def verify_webhook_signature(self, webhook_id: str, signature: str, payload: str) -> bool:
        """驗證 webhook 簽名
        
        Args:
            webhook_id: webhook ID
            signature: 簽名
            payload: 負載
            
        Returns:
            驗證結果
        """
        try:
            # 獲取 webhook 密鑰
            secret = this.get_webhook_secret(webhook_id).get("secret")
            
            if not secret:
                return False
            
            # 使用 HMAC-SHA256 驗證簽名
            import hmac
            import hashlib
            
            expected_signature = hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        
        except Exception as e:
            this.logger.error(f"Error verifying n8n webhook signature: {e}")
            return False 
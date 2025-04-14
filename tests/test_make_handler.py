#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Make.com 處理器單元測試
"""

import json
import unittest
from unittest.mock import patch, MagicMock
from api_client.handlers.make_handler import MakeHandler
from api_client.core.config import APIConfig
from api_client.core.exceptions import APIError, AuthenticationError, RequestError

class TestMakeHandler(unittest.TestCase):
    """Make.com 處理器測試類"""
    
    def setUp(self):
        """測試前準備"""
        # 創建測試配置
        self.config_dict = {
            "api_key": "test_api_key",
            "base_url": "https://hook.make.com",
            "scenario_id": "test_scenario_id",
            "webhook_url": "https://hook.make.com/test_scenario_id",
            "timeout": 30,
            "retry_count": 3,
            "retry_delay": 1
        }
        
        self.config = APIConfig(**self.config_dict)
        
        # 創建處理器實例
        self.handler_dict = MakeHandler(self.config_dict)
        self.handler_config = MakeHandler(self.config)
    
    def test_init_with_dict(self):
        """測試使用字典初始化"""
        self.assertEqual(self.handler_dict.api_key, "test_api_key")
        self.assertEqual(self.handler_dict.base_url, "https://hook.make.com")
        self.assertEqual(self.handler_dict.scenario_id, "test_scenario_id")
        self.assertEqual(self.handler_dict.webhook_url, "https://hook.make.com/test_scenario_id")
        self.assertEqual(self.handler_dict.timeout, 30)
        self.assertEqual(self.handler_dict.retry_count, 3)
        self.assertEqual(self.handler_dict.retry_delay, 1)
        self.assertEqual(self.handler_dict.headers["Authorization"], "Bearer test_api_key")
    
    def test_init_with_config(self):
        """測試使用配置對象初始化"""
        self.assertEqual(self.handler_config.api_key, "test_api_key")
        self.assertEqual(self.handler_config.base_url, "https://hook.make.com")
        self.assertEqual(self.handler_config.scenario_id, "test_scenario_id")
        self.assertEqual(self.handler_config.webhook_url, "https://hook.make.com/test_scenario_id")
        self.assertEqual(self.handler_config.timeout, 30)
        self.assertEqual(self.handler_config.retry_count, 3)
        self.assertEqual(self.handler_config.retry_delay, 1)
        self.assertEqual(self.handler_config.headers["Authorization"], "Bearer test_api_key")
    
    @patch("requests.post")
    def test_trigger_scenario(self, mock_post):
        """測試觸發場景"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        # 測試觸發場景
        result = self.handler_dict.trigger_scenario({"test": "data"})
        
        # 驗證結果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Scenario triggered successfully")
        self.assertEqual(result["data"], {"success": True})
        
        # 驗證請求
        mock_post.assert_called_once_with(
            "https://hook.make.com/test_scenario_id",
            headers={"Content-Type": "application/json", "Authorization": "Bearer test_api_key"},
            json={"test": "data"},
            timeout=30
        )
    
    @patch("requests.post")
    def test_trigger_scenario_error(self, mock_post):
        """測試觸發場景錯誤"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        # 測試觸發場景錯誤
        with self.assertRaises(RequestError):
            self.handler_dict.trigger_scenario({"test": "data"})
    
    @patch("requests.post")
    def test_trigger_scenario_retry(self, mock_post):
        """測試觸發場景重試"""
        # 設置模擬響應
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"success": True}
        
        mock_response_error = MagicMock()
        mock_response_error.status_code = 500
        mock_response_error.text = "Internal Server Error"
        
        mock_post.side_effect = [RequestError("Connection error"), mock_response_success]
        
        # 測試觸發場景重試
        result = self.handler_dict.trigger_scenario({"test": "data"})
        
        # 驗證結果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Scenario triggered successfully")
        self.assertEqual(result["data"], {"success": True})
        
        # 驗證請求
        self.assertEqual(mock_post.call_count, 2)
    
    @patch("requests.post")
    def test_trigger_scenario_with_json(self, mock_post):
        """測試使用 JSON 數據觸發場景"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        # 測試觸發場景
        result = self.handler_dict.trigger_scenario_with_json({"test": "data"})
        
        # 驗證結果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Scenario triggered successfully")
        self.assertEqual(result["data"], {"success": True})
    
    @patch("requests.post")
    def test_trigger_scenario_with_form(self, mock_post):
        """測試使用表單數據觸發場景"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        # 測試觸發場景
        result = self.handler_dict.trigger_scenario_with_form({"field1": "value1", "field2": "value2"})
        
        # 驗證結果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Scenario triggered successfully")
        self.assertEqual(result["data"], {"success": True})
    
    @patch("requests.post")
    def test_trigger_scenario_with_xml(self, mock_post):
        """測試使用 XML 數據觸發場景"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        # 測試觸發場景
        result = self.handler_dict.trigger_scenario_with_xml("<test>data</test>")
        
        # 驗證結果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Scenario triggered successfully")
        self.assertEqual(result["data"], {"success": True})
    
    @patch("requests.post")
    def test_trigger_scenario_with_text(self, mock_post):
        """測試使用純文本數據觸發場景"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        # 測試觸發場景
        result = self.handler_dict.trigger_scenario_with_text("test data")
        
        # 驗證結果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Scenario triggered successfully")
        self.assertEqual(result["data"], {"success": True})
    
    @patch("requests.post")
    def test_trigger_scenario_with_binary(self, mock_post):
        """測試使用二進制數據觸發場景"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        # 測試觸發場景
        result = self.handler_dict.trigger_scenario_with_binary(b"test data")
        
        # 驗證結果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Scenario triggered successfully")
        self.assertEqual(result["data"], {"success": True})
    
    @patch("requests.post")
    def test_trigger_scenario_with_file(self, mock_post):
        """測試使用文件觸發場景"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        # 創建臨時文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test data")
            file_path = f.name
        
        try:
            # 測試觸發場景
            result = self.handler_dict.trigger_scenario_with_file(file_path)
            
            # 驗證結果
            self.assertTrue(result["success"])
            self.assertEqual(result["message"], "Scenario triggered successfully")
            self.assertEqual(result["data"], {"success": True})
        
        finally:
            # 清理臨時文件
            import os
            os.unlink(file_path)
    
    @patch("requests.get")
    def test_get_scenario_info(self, mock_get):
        """測試獲取場景信息"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_scenario_id", "name": "Test Scenario"}
        mock_get.return_value = mock_response
        
        # 測試獲取場景信息
        result = self.handler_dict.get_scenario_info()
        
        # 驗證結果
        self.assertEqual(result["id"], "test_scenario_id")
        self.assertEqual(result["name"], "Test Scenario")
        
        # 驗證請求
        mock_get.assert_called_once_with(
            "https://api.make.com/v1/scenarios/test_scenario_id",
            headers={"Content-Type": "application/json", "Authorization": "Bearer test_api_key"},
            timeout=30
        )
    
    @patch("requests.get")
    def test_get_scenario_info_error(self, mock_get):
        """測試獲取場景信息錯誤"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response
        
        # 測試獲取場景信息錯誤
        with self.assertRaises(RequestError):
            self.handler_dict.get_scenario_info()
    
    @patch("requests.get")
    def test_list_scenarios(self, mock_get):
        """測試獲取場景列表"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "test_scenario_id", "name": "Test Scenario"}]}
        mock_get.return_value = mock_response
        
        # 測試獲取場景列表
        result = self.handler_dict.list_scenarios()
        
        # 驗證結果
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "test_scenario_id")
        self.assertEqual(result[0]["name"], "Test Scenario")
        
        # 驗證請求
        mock_get.assert_called_once_with(
            "https://api.make.com/v1/scenarios",
            headers={"Content-Type": "application/json", "Authorization": "Bearer test_api_key"},
            timeout=30
        )
    
    @patch("requests.get")
    def test_list_scenarios_error(self, mock_get):
        """測試獲取場景列表錯誤"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        # 測試獲取場景列表錯誤
        with self.assertRaises(RequestError):
            self.handler_dict.list_scenarios()
    
    @patch("requests.post")
    def test_execute_scenario(self, mock_post):
        """測試執行場景"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "test_execution_id", "status": "running"}
        mock_post.return_value = mock_response
        
        # 測試執行場景
        result = self.handler_dict.execute_scenario(data={"test": "data"})
        
        # 驗證結果
        self.assertEqual(result["id"], "test_execution_id")
        self.assertEqual(result["status"], "running")
        
        # 驗證請求
        mock_post.assert_called_once_with(
            "https://api.make.com/v1/scenarios/test_scenario_id/executions",
            headers={"Content-Type": "application/json", "Authorization": "Bearer test_api_key"},
            json={"test": "data"},
            timeout=30
        )
    
    @patch("requests.post")
    def test_execute_scenario_error(self, mock_post):
        """測試執行場景錯誤"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        # 測試執行場景錯誤
        with self.assertRaises(RequestError):
            self.handler_dict.execute_scenario(data={"test": "data"})
    
    @patch("requests.get")
    def test_get_execution_status(self, mock_get):
        """測試獲取執行狀態"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_execution_id", "status": "completed"}
        mock_get.return_value = mock_response
        
        # 測試獲取執行狀態
        result = self.handler_dict.get_execution_status("test_execution_id")
        
        # 驗證結果
        self.assertEqual(result["id"], "test_execution_id")
        self.assertEqual(result["status"], "completed")
        
        # 驗證請求
        mock_get.assert_called_once_with(
            "https://api.make.com/v1/executions/test_execution_id",
            headers={"Content-Type": "application/json", "Authorization": "Bearer test_api_key"},
            timeout=30
        )
    
    @patch("requests.get")
    def test_get_execution_status_error(self, mock_get):
        """測試獲取執行狀態錯誤"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response
        
        # 測試獲取執行狀態錯誤
        with self.assertRaises(RequestError):
            self.handler_dict.get_execution_status("test_execution_id")
    
    @patch("requests.get")
    def test_list_executions(self, mock_get):
        """測試獲取執行列表"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "test_execution_id", "status": "completed"}]}
        mock_get.return_value = mock_response
        
        # 測試獲取執行列表
        result = self.handler_dict.list_executions(limit=10, offset=0)
        
        # 驗證結果
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "test_execution_id")
        self.assertEqual(result[0]["status"], "completed")
        
        # 驗證請求
        mock_get.assert_called_once_with(
            "https://api.make.com/v1/executions?limit=10&offset=0",
            headers={"Content-Type": "application/json", "Authorization": "Bearer test_api_key"},
            timeout=30
        )
    
    @patch("requests.get")
    def test_list_executions_with_scenario(self, mock_get):
        """測試獲取場景執行列表"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "test_execution_id", "status": "completed"}]}
        mock_get.return_value = mock_response
        
        # 測試獲取場景執行列表
        result = self.handler_dict.list_executions(scenario_id="test_scenario_id", limit=10, offset=0)
        
        # 驗證結果
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "test_execution_id")
        self.assertEqual(result[0]["status"], "completed")
        
        # 驗證請求
        mock_get.assert_called_once_with(
            "https://api.make.com/v1/executions?scenarioId=test_scenario_id&limit=10&offset=0",
            headers={"Content-Type": "application/json", "Authorization": "Bearer test_api_key"},
            timeout=30
        )
    
    @patch("requests.get")
    def test_list_executions_error(self, mock_get):
        """測試獲取執行列表錯誤"""
        # 設置模擬響應
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        # 測試獲取執行列表錯誤
        with self.assertRaises(RequestError):
            self.handler_dict.list_executions()

if __name__ == "__main__":
    unittest.main() 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
IFTTT 處理器單元測試
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from api_client.handlers.ifttt_handler import IFTTTHandler
from api_client.core.config import APIConfig
from api_client.core.exceptions import APIError, AuthenticationError, RequestError

class TestIFTTTHandler(unittest.TestCase):
    """IFTTT 處理器測試類"""
    
    def setUp(self):
        """測試前準備"""
        # 創建配置對象
        self.config = APIConfig(
            api_type="rest",
            base_url="https://maker.ifttt.com/trigger",
            auth_type="api_key",
            webhook_key="test_webhook_key"
        )
        
        # 創建處理器實例
        self.handler = IFTTTHandler(self.config)
        
        # 模擬請求方法
        self.handler.post = Mock()
    
    def test_init_with_dict(self):
        """測試使用字典初始化"""
        config_dict = {
            "api_type": "rest",
            "base_url": "https://maker.ifttt.com/trigger",
            "auth_type": "api_key",
            "webhook_key": "test_webhook_key"
        }
        
        handler = IFTTTHandler(config_dict)
        self.assertEqual(handler.webhook_key, "test_webhook_key")
    
    def test_init_with_config(self):
        """測試使用配置對象初始化"""
        self.assertEqual(self.handler.webhook_key, "test_webhook_key")
    
    def test_trigger_event(self):
        """測試基本事件觸發"""
        # 設置模擬返回值
        self.handler.post.return_value = {"status": "success"}
        
        # 調用方法
        result = self.handler.trigger_event("test_event", "value1", "value2", "value3")
        
        # 驗證結果
        self.handler.post.assert_called_once_with(
            "/test_event/with/key/test_webhook_key",
            json={"value1": "value1", "value2": "value2", "value3": "value3"}
        )
        self.assertEqual(result, {"status": "success"})
    
    def test_trigger_event_with_json(self):
        """測試使用 JSON 數據觸發事件"""
        # 設置模擬返回值
        self.handler.post.return_value = {"status": "success"}
        
        # 準備測試數據
        json_data = {"key": "value", "number": 123}
        
        # 調用方法
        result = self.handler.trigger_event_with_json("test_event", json_data)
        
        # 驗證結果
        self.handler.post.assert_called_once_with(
            "/test_event/with/key/test_webhook_key",
            json=json_data
        )
        self.assertEqual(result, {"status": "success"})
    
    def test_trigger_event_with_form(self):
        """測試使用表單數據觸發事件"""
        # 設置模擬返回值
        self.handler.post.return_value = {"status": "success"}
        
        # 準備測試數據
        form_data = {"field1": "value1", "field2": "value2"}
        
        # 調用方法
        result = self.handler.trigger_event_with_form("test_event", form_data)
        
        # 驗證結果
        self.handler.post.assert_called_once_with(
            "/test_event/with/key/test_webhook_key",
            data=form_data
        )
        self.assertEqual(result, {"status": "success"})
    
    def test_trigger_event_with_xml(self):
        """測試使用 XML 數據觸發事件"""
        # 設置模擬返回值
        self.handler.post.return_value = {"status": "success"}
        
        # 準備測試數據
        xml_data = "<root><item>value</item></root>"
        
        # 調用方法
        result = self.handler.trigger_event_with_xml("test_event", xml_data)
        
        # 驗證結果
        self.handler.post.assert_called_once_with(
            "/test_event/with/key/test_webhook_key",
            data=xml_data,
            headers={"Content-Type": "application/xml"}
        )
        self.assertEqual(result, {"status": "success"})
    
    def test_trigger_event_with_text(self):
        """測試使用純文本數據觸發事件"""
        # 設置模擬返回值
        self.handler.post.return_value = {"status": "success"}
        
        # 準備測試數據
        text_data = "Hello, World!"
        
        # 調用方法
        result = self.handler.trigger_event_with_text("test_event", text_data)
        
        # 驗證結果
        self.handler.post.assert_called_once_with(
            "/test_event/with/key/test_webhook_key",
            data=text_data,
            headers={"Content-Type": "text/plain"}
        )
        self.assertEqual(result, {"status": "success"})
    
    def test_trigger_event_with_binary(self):
        """測試使用二進制數據觸發事件"""
        # 設置模擬返回值
        self.handler.post.return_value = {"status": "success"}
        
        # 準備測試數據
        binary_data = b"binary data"
        content_type = "application/octet-stream"
        
        # 調用方法
        result = self.handler.trigger_event_with_binary("test_event", binary_data, content_type)
        
        # 驗證結果
        self.handler.post.assert_called_once_with(
            "/test_event/with/key/test_webhook_key",
            data=binary_data,
            headers={"Content-Type": content_type}
        )
        self.assertEqual(result, {"status": "success"})
    
    @patch("builtins.open", create=True)
    def test_trigger_event_with_file(self, mock_open):
        """測試使用文件觸發事件"""
        # 設置模擬返回值
        self.handler.post.return_value = {"status": "success"}
        
        # 模擬文件讀取
        mock_file = MagicMock()
        mock_file.read.return_value = b"file content"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # 準備測試數據
        file_path = "test.txt"
        content_type = "text/plain"
        
        # 調用方法
        result = self.handler.trigger_event_with_file("test_event", file_path, content_type)
        
        # 驗證結果
        mock_open.assert_called_once_with(file_path, "rb")
        self.handler.post.assert_called_once_with(
            "/test_event/with/key/test_webhook_key",
            data=b"file content",
            headers={"Content-Type": content_type}
        )
        self.assertEqual(result, {"status": "success"})
    
    def test_trigger_event_error(self):
        """測試事件觸發錯誤處理"""
        # 設置模擬錯誤
        self.handler.post.side_effect = APIError("API Error")
        
        # 驗證異常拋出
        with self.assertRaises(APIError):
            self.handler.trigger_event("test_event")
    
    def test_trigger_event_auth_error(self):
        """測試認證錯誤處理"""
        # 設置模擬錯誤
        self.handler.post.side_effect = AuthenticationError("Auth Error")
        
        # 驗證異常拋出
        with self.assertRaises(AuthenticationError):
            self.handler.trigger_event("test_event")
    
    def test_trigger_event_request_error(self):
        """測試請求錯誤處理"""
        # 設置模擬錯誤
        self.handler.post.side_effect = RequestError("Request Error")
        
        # 驗證異常拋出
        with self.assertRaises(RequestError):
            self.handler.trigger_event("test_event") 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MQTT 處理器單元測試
"""

import unittest
from unittest.mock import MagicMock, patch
import json
import time
from api_client.handlers.mqtt_handler import MQTTHandler
from api_client.core.config import MQTTConfig
from api_client.core.exceptions import APIError, AuthenticationError, RequestError, ConnectionError

class TestMQTTHandler(unittest.TestCase):
    """MQTT 處理器測試類"""
    
    def setUp(self):
        """測試前準備"""
        # 創建配置
        self.config = MQTTConfig(
            broker="localhost",
            port=1883,
            username="test_user",
            password="test_pass",
            client_id="test_client",
            keepalive=60,
            use_tls=False,
            clean_session=True
        )
        
        # 創建處理器
        self.handler = MQTTHandler(self.config)
        
        # 創建 MQTT 客戶端模擬對象
        self.mock_client = MagicMock()
        self.handler.client = self.mock_client
    
    def test_init_with_dict(self):
        """測試使用字典初始化"""
        config_dict = {
            "broker": "test.broker.com",
            "port": 8883,
            "username": "test_user",
            "password": "test_pass",
            "client_id": "test_client",
            "keepalive": 30,
            "use_tls": True,
            "clean_session": False
        }
        
        handler = MQTTHandler(config_dict)
        
        self.assertEqual(handler.broker, "test.broker.com")
        self.assertEqual(handler.port, 8883)
        self.assertEqual(handler.username, "test_user")
        self.assertEqual(handler.password, "test_pass")
        self.assertEqual(handler.client_id, "test_client")
        self.assertEqual(handler.keepalive, 30)
        self.assertTrue(handler.use_tls)
        self.assertFalse(handler.clean_session)
    
    def test_init_with_config(self):
        """測試使用配置對象初始化"""
        config = MQTTConfig(
            broker="test.broker.com",
            port=8883,
            username="test_user",
            password="test_pass",
            client_id="test_client",
            keepalive=30,
            use_tls=True,
            clean_session=False
        )
        
        handler = MQTTHandler(config)
        
        self.assertEqual(handler.broker, "test.broker.com")
        self.assertEqual(handler.port, 8883)
        self.assertEqual(handler.username, "test_user")
        self.assertEqual(handler.password, "test_pass")
        self.assertEqual(handler.client_id, "test_client")
        self.assertEqual(handler.keepalive, 30)
        self.assertTrue(handler.use_tls)
        self.assertFalse(handler.clean_session)
    
    def test_connect(self):
        """測試連接"""
        # 設置模擬對象
        self.mock_client.connect.return_value = None
        self.mock_client.loop_start.return_value = None
        
        # 模擬連接成功
        with patch.object(self.handler, '_on_connect') as mock_on_connect:
            mock_on_connect.return_value = None
            self.handler.connected = True
            
            # 執行連接
            result = self.handler.connect()
            
            # 驗證結果
            self.assertTrue(result)
            self.mock_client.connect.assert_called_once_with(
                self.handler.broker,
                self.handler.port,
                self.handler.keepalive
            )
            self.mock_client.loop_start.assert_called_once()
    
    def test_connect_error(self):
        """測試連接錯誤"""
        # 設置模擬對象
        self.mock_client.connect.side_effect = Exception("Connection failed")
        
        # 執行連接
        with self.assertRaises(ConnectionError):
            self.handler.connect()
        
        # 驗證結果
        self.mock_client.connect.assert_called_once()
        self.assertFalse(self.handler.connected)
    
    def test_disconnect(self):
        """測試斷開連接"""
        # 設置模擬對象
        self.mock_client.loop_stop.return_value = None
        self.mock_client.disconnect.return_value = None
        
        # 設置連接狀態
        this.handler.connected = True
        
        # 模擬斷開連接成功
        with patch.object(this.handler, '_on_disconnect') as mock_on_disconnect:
            mock_on_disconnect.return_value = None
            this.handler.connected = False
            
            # 執行斷開連接
            result = this.handler.disconnect()
            
            # 驗證結果
            this.assertTrue(result)
            this.mock_client.loop_stop.assert_called_once()
            this.mock_client.disconnect.assert_called_once()
    
    def test_disconnect_error(self):
        """測試斷開連接錯誤"""
        # 設置模擬對象
        this.mock_client.loop_stop.return_value = None
        this.mock_client.disconnect.side_effect = Exception("Disconnection failed")
        
        # 設置連接狀態
        this.handler.connected = True
        
        # 執行斷開連接
        with this.assertRaises(ConnectionError):
            this.handler.disconnect()
        
        # 驗證結果
        this.mock_client.loop_stop.assert_called_once()
        this.mock_client.disconnect.assert_called_once()
    
    def test_publish(self):
        """測試發布消息"""
        # 設置模擬對象
        mock_result = MagicMock()
        mock_result.rc = 0
        mock_result.wait_for_publish.return_value = None
        this.mock_client.publish.return_value = mock_result
        
        # 設置連接狀態
        this.handler.connected = True
        
        # 執行發布
        result = this.handler.publish("test/topic", {"key": "value"})
        
        # 驗證結果
        this.assertTrue(result)
        this.mock_client.publish.assert_called_once()
        mock_result.wait_for_publish.assert_called_once()
    
    def test_publish_error(self):
        """測試發布消息錯誤"""
        # 設置模擬對象
        this.mock_client.publish.side_effect = Exception("Publish failed")
        
        # 設置連接狀態
        this.handler.connected = True
        
        # 執行發布
        with this.assertRaises(APIError):
            this.handler.publish("test/topic", {"key": "value"})
        
        # 驗證結果
        this.mock_client.publish.assert_called_once()
    
    def test_subscribe(self):
        """測試訂閱主題"""
        # 設置模擬對象
        this.mock_client.subscribe.return_value = (0, 1)
        
        # 設置連接狀態
        this.handler.connected = True
        
        # 定義回調函數
        def callback(topic, payload):
            pass
        
        # 執行訂閱
        result = this.handler.subscribe("test/topic", callback)
        
        # 驗證結果
        this.assertTrue(result)
        this.mock_client.subscribe.assert_called_once_with("test/topic", 0)
        this.assertIn("test/topic", this.handler.subscriptions)
    
    def test_subscribe_error(self):
        """測試訂閱主題錯誤"""
        # 設置模擬對象
        this.mock_client.subscribe.side_effect = Exception("Subscribe failed")
        
        # 設置連接狀態
        this.handler.connected = True
        
        # 定義回調函數
        def callback(topic, payload):
            pass
        
        # 執行訂閱
        with this.assertRaises(APIError):
            this.handler.subscribe("test/topic", callback)
        
        # 驗證結果
        this.mock_client.subscribe.assert_called_once()
    
    def test_unsubscribe(self):
        """測試取消訂閱主題"""
        # 設置模擬對象
        this.mock_client.unsubscribe.return_value = (0,)
        
        # 設置連接狀態
        this.handler.connected = True
        this.handler.subscriptions["test/topic"] = 0
        
        # 執行取消訂閱
        result = this.handler.unsubscribe("test/topic")
        
        # 驗證結果
        this.assertTrue(result)
        this.mock_client.unsubscribe.assert_called_once_with("test/topic")
        this.assertNotIn("test/topic", this.handler.subscriptions)
    
    def test_unsubscribe_error(self):
        """測試取消訂閱主題錯誤"""
        # 設置模擬對象
        this.mock_client.unsubscribe.side_effect = Exception("Unsubscribe failed")
        
        # 設置連接狀態
        this.handler.connected = True
        this.handler.subscriptions["test/topic"] = 0
        
        # 執行取消訂閱
        with this.assertRaises(APIError):
            this.handler.unsubscribe("test/topic")
        
        # 驗證結果
        this.mock_client.unsubscribe.assert_called_once()
    
    def test_on_connect(self):
        """測試連接回調"""
        # 設置初始狀態
        this.handler.connected = False
        this.handler.connecting = True
        this.handler.reconnect_attempts = 5
        
        # 執行連接回調（成功）
        this.handler._on_connect(None, None, None, 0)
        
        # 驗證結果
        this.assertTrue(this.handler.connected)
        this.assertFalse(this.handler.connecting)
        this.assertEqual(this.handler.reconnect_attempts, 0)
        
        # 執行連接回調（失敗）
        this.handler._on_connect(None, None, None, 1)
        
        # 驗證結果
        this.assertFalse(this.handler.connected)
        this.assertFalse(this.handler.connecting)
    
    def test_on_disconnect(self):
        """測試斷開連接回調"""
        # 設置初始狀態
        this.handler.connected = True
        this.handler.disconnecting = True
        this.handler.reconnect_attempts = 0
        
        # 執行斷開連接回調
        this.handler._on_disconnect(None, None, 0)
        
        # 驗證結果
        this.assertFalse(this.handler.connected)
        this.assertFalse(this.handler.disconnecting)
    
    def test_on_message(self):
        """測試消息回調"""
        # 創建模擬消息
        mock_msg = MagicMock()
        mock_msg.topic = "test/topic"
        mock_msg.payload = json.dumps({"key": "value"}).encode()
        
        # 設置回調函數
        callback_called = False
        callback_topic = None
        callback_payload = None
        
        def callback(topic, payload):
            nonlocal callback_called, callback_topic, callback_payload
            callback_called = True
            callback_topic = topic
            callback_payload = payload
        
        # 註冊回調
        this.handler.register_message_callback("test/topic", callback)
        
        # 執行消息回調
        this.handler._on_message(None, None, mock_msg)
        
        # 驗證結果
        this.assertTrue(callback_called)
        this.assertEqual(callback_topic, "test/topic")
        this.assertEqual(callback_payload, {"key": "value"})
    
    def test_worker_loop(self):
        """測試工作線程循環"""
        # 設置初始狀態
        this.handler.connected = False
        this.handler.connecting = False
        this.handler.should_stop = False
        
        # 模擬連接成功
        with patch.object(this.handler, 'connect') as mock_connect:
            mock_connect.return_value = True
            
            # 執行工作線程循環
            this.handler._worker_loop()
            
            # 驗證結果
            mock_connect.assert_called_once()
    
    def test_worker_loop_stop(self):
        """測試工作線程停止"""
        # 設置初始狀態
        this.handler.should_stop = True
        
        # 執行工作線程循環
        this.handler._worker_loop()
        
        # 驗證結果
        this.assertTrue(this.handler.should_stop)

if __name__ == "__main__":
    unittest.main() 
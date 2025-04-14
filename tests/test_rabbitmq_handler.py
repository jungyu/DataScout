#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RabbitMQ 處理器單元測試
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import time
from persistence.handlers.rabbitmq_handler import RabbitMQHandler
from persistence.core.config import RabbitMQConfig
from persistence.core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

class TestRabbitMQHandler(unittest.TestCase):
    """RabbitMQ 處理器測試類"""
    
    def setUp(self):
        """測試前準備"""
        # 創建配置
        self.config = RabbitMQConfig(
            host="localhost",
            port=5672,
            username="guest",
            password="guest",
            virtual_host="/",
            exchange_name="test_exchange",
            queue_name="test_queue",
            routing_key="test"
        )
        
        # 創建處理器
        self.handler = RabbitMQHandler(self.config)
        
        # 模擬 channel
        self.channel_mock = MagicMock()
        self.handler.channel = self.channel_mock
        
        # 模擬 connection
        self.connection_mock = MagicMock()
        self.handler.connection = self.connection_mock
    
    def test_init(self):
        """測試初始化"""
        # 使用字典配置
        config_dict = {
            "host": "localhost",
            "port": 5672,
            "username": "guest",
            "password": "guest",
            "virtual_host": "/",
            "exchange_name": "test_exchange",
            "queue_name": "test_queue",
            "routing_key": "test"
        }
        handler = RabbitMQHandler(config_dict)
        self.assertIsInstance(handler.config, RabbitMQConfig)
        
        # 使用配置對象
        handler = RabbitMQHandler(self.config)
        self.assertEqual(handler.config, self.config)
    
    def test_setup_storage(self):
        """測試設置存儲環境"""
        with patch("pika.BlockingConnection") as mock_connection:
            with patch("pika.PlainCredentials") as mock_credentials:
                with patch("pika.ConnectionParameters") as mock_parameters:
                    # 設置模擬對象
                    mock_connection.return_value = self.connection_mock
                    mock_credentials.return_value = MagicMock()
                    mock_parameters.return_value = MagicMock()
                    
                    # 創建處理器
                    handler = RabbitMQHandler(self.config)
                    
                    # 驗證連接創建
                    mock_credentials.assert_called_once_with(
                        self.config.username,
                        self.config.password
                    )
                    mock_parameters.assert_called_once()
                    mock_connection.assert_called_once()
    
    def test_create_exchange(self):
        """測試創建交換機"""
        # 調用方法
        self.handler._create_exchange()
        
        # 驗證交換機創建
        self.channel_mock.exchange_declare.assert_called_once_with(
            exchange=self.config.exchange_name,
            exchange_type=self.config.exchange_type,
            durable=self.config.exchange_durable,
            auto_delete=self.config.exchange_auto_delete,
            internal=self.config.exchange_internal
        )
    
    def test_create_queue(self):
        """測試創建隊列"""
        # 調用方法
        self.handler._create_queue()
        
        # 驗證隊列創建
        self.channel_mock.queue_declare.assert_called_once_with(
            queue=self.config.queue_name,
            durable=self.config.queue_durable,
            exclusive=self.config.queue_exclusive,
            auto_delete=self.config.queue_auto_delete,
            arguments={
                "x-message-ttl": self.config.message_ttl,
                "x-max-length": self.config.queue_max_length,
                "x-overflow": self.config.queue_overflow
            }
        )
    
    def test_bind_queue(self):
        """測試綁定隊列"""
        # 調用方法
        self.handler._bind_queue()
        
        # 驗證隊列綁定
        self.channel_mock.queue_bind.assert_called_once_with(
            exchange=self.config.exchange_name,
            queue=self.config.queue_name,
            routing_key=self.config.routing_key
        )
    
    def test_save(self):
        """測試保存數據"""
        # 準備測試數據
        data = {"key": "value"}
        path = "test/path"
        
        # 調用方法
        self.handler.save(data, path)
        
        # 驗證消息發布
        self.channel_mock.basic_publish.assert_called_once()
        call_args = self.channel_mock.basic_publish.call_args[1]
        self.assertEqual(call_args["exchange"], self.config.exchange_name)
        self.assertEqual(call_args["routing_key"], path)
        self.assertEqual(
            json.loads(call_args["body"])["data"],
            data
        )
    
    def test_load(self):
        """測試加載數據"""
        # 準備測試數據
        path = "test/path"
        data = {"key": "value"}
        
        # 設置模擬返回值
        self.channel_mock.queue_declare.return_value.method.queue = "temp_queue"
        self.channel_mock.consume.return_value = [
            (MagicMock(), MagicMock(), json.dumps({
                "data": data,
                "path": path,
                "timestamp": time.time()
            }).encode())
        ]
        
        # 調用方法
        result = self.handler.load(path)
        
        # 驗證結果
        self.assertEqual(result, data)
        self.channel_mock.queue_bind.assert_called_once_with(
            exchange=self.config.exchange_name,
            queue="temp_queue",
            routing_key=path
        )
    
    def test_load_not_found(self):
        """測試加載不存在的數據"""
        # 準備測試數據
        path = "test/path"
        
        # 設置模擬返回值
        self.channel_mock.queue_declare.return_value.method.queue = "temp_queue"
        self.channel_mock.consume.return_value = []
        
        # 驗證異常
        with self.assertRaises(NotFoundError):
            self.handler.load(path)
    
    def test_delete(self):
        """測試刪除數據"""
        # 準備測試數據
        path = "test/path"
        
        # 調用方法
        self.handler.delete(path)
        
        # 驗證消息發布
        self.channel_mock.basic_publish.assert_called_once()
        call_args = self.channel_mock.basic_publish.call_args[1]
        self.assertEqual(call_args["exchange"], self.config.exchange_name)
        self.assertEqual(call_args["routing_key"], path)
        self.assertTrue(
            json.loads(call_args["body"])["deleted"]
        )
    
    def test_exists(self):
        """測試檢查數據是否存在"""
        # 準備測試數據
        path = "test/path"
        
        # 設置模擬返回值
        self.channel_mock.queue_declare.return_value.method.queue = "temp_queue"
        self.channel_mock.consume.return_value = [
            (MagicMock(), MagicMock(), json.dumps({
                "data": {"key": "value"},
                "path": path,
                "timestamp": time.time()
            }).encode())
        ]
        
        # 調用方法
        result = self.handler.exists(path)
        
        # 驗證結果
        self.assertTrue(result)
    
    def test_list(self):
        """測試列出數據路徑"""
        # 準備測試數據
        prefix = "test/"
        paths = ["test/path1", "test/path2", "other/path"]
        
        # 設置模擬返回值
        self.channel_mock.queue_declare.return_value.method.queue = "temp_queue"
        self.channel_mock.consume.return_value = [
            (MagicMock(), MagicMock(), json.dumps({
                "data": {"key": "value"},
                "path": path,
                "timestamp": time.time()
            }).encode())
            for path in paths
        ]
        
        # 調用方法
        result = self.handler.list(prefix)
        
        # 驗證結果
        self.assertEqual(
            set(result),
            {"test/path1", "test/path2"}
        )
    
    def test_find(self):
        """測試查詢數據"""
        # 準備測試數據
        query = {"key": "value"}
        data_list = [
            {"key": "value", "other": "data1"},
            {"key": "other", "other": "data2"},
            {"key": "value", "other": "data3"}
        ]
        
        # 設置模擬返回值
        self.channel_mock.queue_declare.return_value.method.queue = "temp_queue"
        self.channel_mock.consume.return_value = [
            (MagicMock(), MagicMock(), json.dumps({
                "data": data,
                "path": f"test/path{i}",
                "timestamp": time.time()
            }).encode())
            for i, data in enumerate(data_list)
        ]
        
        # 調用方法
        result = self.handler.find(query)
        
        # 驗證結果
        self.assertEqual(
            result,
            [{"key": "value", "other": "data1"}, {"key": "value", "other": "data3"}]
        )
    
    def test_count(self):
        """測試統計數據數量"""
        # 準備測試數據
        query = {"key": "value"}
        data_list = [
            {"key": "value", "other": "data1"},
            {"key": "other", "other": "data2"},
            {"key": "value", "other": "data3"}
        ]
        
        # 設置模擬返回值
        self.channel_mock.queue_declare.return_value.method.queue = "temp_queue"
        self.channel_mock.consume.return_value = [
            (MagicMock(), MagicMock(), json.dumps({
                "data": data,
                "path": f"test/path{i}",
                "timestamp": time.time()
            }).encode())
            for i, data in enumerate(data_list)
        ]
        
        # 調用方法
        result = self.handler.count(query)
        
        # 驗證結果
        self.assertEqual(result, 2)
    
    def test_batch_save(self):
        """測試批量保存數據"""
        # 準備測試數據
        data_list = [
            {"path": "test/path1", "data": {"key": "value1"}},
            {"path": "test/path2", "data": {"key": "value2"}}
        ]
        
        # 調用方法
        self.handler.batch_save(data_list)
        
        # 驗證消息發布
        self.assertEqual(
            self.channel_mock.basic_publish.call_count,
            len(data_list)
        )
    
    def test_batch_load(self):
        """測試批量加載數據"""
        # 準備測試數據
        paths = ["test/path1", "test/path2"]
        data_dict = {
            "test/path1": {"key": "value1"},
            "test/path2": {"key": "value2"}
        }
        
        # 設置模擬返回值
        self.channel_mock.queue_declare.return_value.method.queue = "temp_queue"
        self.channel_mock.consume.return_value = [
            (MagicMock(), MagicMock(), json.dumps({
                "data": data,
                "path": path,
                "timestamp": time.time()
            }).encode())
            for path, data in data_dict.items()
        ]
        
        # 調用方法
        result = self.handler.batch_load(paths)
        
        # 驗證結果
        self.assertEqual(
            {item["path"]: item["data"] for item in result},
            data_dict
        )
    
    def test_batch_delete(self):
        """測試批量刪除數據"""
        # 準備測試數據
        paths = ["test/path1", "test/path2"]
        
        # 調用方法
        self.handler.batch_delete(paths)
        
        # 驗證消息發布
        self.assertEqual(
            self.channel_mock.basic_publish.call_count,
            len(paths)
        )
    
    def test_batch_exists(self):
        """測試批量檢查數據是否存在"""
        # 準備測試數據
        paths = ["test/path1", "test/path2", "test/path3"]
        existing_paths = ["test/path1", "test/path2"]
        
        # 設置模擬返回值
        self.channel_mock.queue_declare.return_value.method.queue = "temp_queue"
        self.channel_mock.consume.return_value = [
            (MagicMock(), MagicMock(), json.dumps({
                "data": {"key": "value"},
                "path": path,
                "timestamp": time.time()
            }).encode())
            for path in existing_paths
        ]
        
        # 調用方法
        result = self.handler.batch_exists(paths)
        
        # 驗證結果
        self.assertEqual(
            result,
            {
                "test/path1": True,
                "test/path2": True,
                "test/path3": False
            }
        )
    
    def test_subscribe(self):
        """測試訂閱數據變更"""
        # 準備測試數據
        callback = Mock()
        data = {"key": "value"}
        path = "test/path"
        
        # 設置模擬返回值
        self.channel_mock.consume.return_value = [
            (MagicMock(), MagicMock(), json.dumps({
                "data": data,
                "path": path,
                "timestamp": time.time()
            }).encode())
        ]
        
        # 調用方法
        self.handler.subscribe(callback)
        
        # 驗證回調
        callback.assert_called_once_with(data, path)
    
    def test_subscribe_with_filter(self):
        """測試訂閱數據變更（帶過濾）"""
        # 準備測試數據
        callback = Mock()
        filter_func = Mock(return_value=True)
        data = {"key": "value"}
        path = "test/path"
        
        # 設置模擬返回值
        self.channel_mock.consume.return_value = [
            (MagicMock(), MagicMock(), json.dumps({
                "data": data,
                "path": path,
                "timestamp": time.time()
            }).encode())
        ]
        
        # 調用方法
        self.handler.subscribe_with_filter(callback, filter_func)
        
        # 驗證回調
        filter_func.assert_called_once_with(data, path)
        callback.assert_called_once_with(data, path)
    
    def test_stream(self):
        """測試流式獲取數據"""
        # 準備測試數據
        data_list = [
            {"key": "value1", "path": "test/path1"},
            {"key": "value2", "path": "test/path2"}
        ]
        
        # 設置模擬返回值
        self.channel_mock.consume.return_value = [
            (MagicMock(), MagicMock(), json.dumps({
                "data": data,
                "path": path,
                "timestamp": time.time()
            }).encode())
            for data, path in data_list
        ]
        
        # 調用方法
        result = list(self.handler.stream())
        
        # 驗證結果
        self.assertEqual(
            len(result),
            len(data_list)
        )
        for item, (data, path) in zip(result, data_list):
            self.assertEqual(item["data"], data)
            self.assertEqual(item["path"], path)
    
    def test_stream_with_filter(self):
        """測試流式獲取數據（帶過濾）"""
        # 準備測試數據
        filter_func = Mock(return_value=True)
        data_list = [
            {"key": "value1", "path": "test/path1"},
            {"key": "value2", "path": "test/path2"}
        ]
        
        # 設置模擬返回值
        self.channel_mock.consume.return_value = [
            (MagicMock(), MagicMock(), json.dumps({
                "data": data,
                "path": path,
                "timestamp": time.time()
            }).encode())
            for data, path in data_list
        ]
        
        # 調用方法
        result = list(self.handler.stream_with_filter(filter_func))
        
        # 驗證結果
        self.assertEqual(
            len(result),
            len(data_list)
        )
        for item, (data, path) in zip(result, data_list):
            self.assertEqual(item["data"], data)
            self.assertEqual(item["path"], path)
            filter_func.assert_called_with(data, path)
    
    def test_cleanup(self):
        """測試清理資源"""
        # 調用方法
        self.handler.cleanup()
        
        # 驗證資源清理
        self.channel_mock.close.assert_called_once()
        self.connection_mock.close.assert_called_once()

if __name__ == "__main__":
    unittest.main() 
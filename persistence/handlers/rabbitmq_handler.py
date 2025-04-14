#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RabbitMQ 存儲處理器
提供基於 RabbitMQ 的數據存儲功能，支持生產者和消費者操作
"""

import json
import time
from typing import Dict, Any, List, Optional, Union, Callable, Iterator
import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError
from persistence.core.config import RabbitMQConfig
from persistence.core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)
from persistence.core.storage_interface import StorageInterface

class RabbitMQHandler(StorageInterface):
    """RabbitMQ 存儲處理器類"""
    
    def __init__(self, config: Union[Dict[str, Any], RabbitMQConfig]):
        """初始化 RabbitMQ 存儲處理器
        
        Args:
            config: 配置對象，可以是字典或 RabbitMQConfig 實例
        """
        if isinstance(config, dict):
            self.config = RabbitMQConfig(**config)
        else:
            self.config = config
        
        self.connection = None
        self.channel = None
        self._setup_storage()
    
    def _setup_storage(self):
        """設置存儲環境"""
        try:
            # 創建連接
            credentials = pika.PlainCredentials(
                self.config.username,
                self.config.password
            )
            
            parameters = pika.ConnectionParameters(
                host=self.config.host,
                port=self.config.port,
                virtual_host=self.config.virtual_host,
                credentials=credentials,
                ssl_options=pika.SSLOptions(
                    ca_certs=self.config.ssl_ca_certs,
                    certfile=self.config.ssl_certfile,
                    keyfile=self.config.ssl_keyfile,
                    cert_reqs=self.config.ssl_cert_reqs
                ) if self.config.ssl_enabled else None,
                connection_attempts=self.config.connection_attempts,
                retry_delay=self.config.retry_delay,
                socket_timeout=self.config.socket_timeout,
                heartbeat=self.config.heartbeat
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # 創建交換機
            self._create_exchange()
            
            # 創建隊列
            self._create_queue()
            
            # 綁定隊列和交換機
            self._bind_queue()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to RabbitMQ: {str(e)}")
    
    def _create_exchange(self):
        """創建交換機"""
        try:
            self.channel.exchange_declare(
                exchange=self.config.exchange_name,
                exchange_type=self.config.exchange_type,
                durable=self.config.exchange_durable,
                auto_delete=self.config.exchange_auto_delete,
                internal=self.config.exchange_internal
            )
        except Exception as e:
            raise StorageError(f"Failed to create exchange: {str(e)}")
    
    def _create_queue(self):
        """創建隊列"""
        try:
            self.channel.queue_declare(
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
        except Exception as e:
            raise StorageError(f"Failed to create queue: {str(e)}")
    
    def _bind_queue(self):
        """綁定隊列和交換機"""
        try:
            self.channel.queue_bind(
                exchange=self.config.exchange_name,
                queue=self.config.queue_name,
                routing_key=self.config.routing_key
            )
        except Exception as e:
            raise StorageError(f"Failed to bind queue: {str(e)}")
    
    def save(self, data: Dict[str, Any], path: str) -> None:
        """保存數據
        
        Args:
            data: 要保存的數據
            path: 數據路徑
        """
        try:
            # 添加時間戳
            data_with_timestamp = {
                "data": data,
                "path": path,
                "timestamp": time.time()
            }
            
            # 發送消息
            self.channel.basic_publish(
                exchange=self.config.exchange_name,
                routing_key=path,
                body=json.dumps(data_with_timestamp),
                properties=pika.BasicProperties(
                    delivery_mode=2 if self.config.message_persistent else 1,
                    content_type="application/json",
                    content_encoding="utf-8",
                    headers={"path": path},
                    priority=self.config.message_priority,
                    timestamp=int(time.time())
                )
            )
        except Exception as e:
            raise StorageError(f"Failed to save data: {str(e)}")
    
    def load(self, path: str) -> Dict[str, Any]:
        """加載數據
        
        Args:
            path: 數據路徑
            
        Returns:
            加載的數據
        """
        try:
            # 創建臨時隊列
            result = self.channel.queue_declare(queue="", exclusive=True)
            temp_queue = result.method.queue
            
            # 綁定臨時隊列
            self.channel.queue_bind(
                exchange=self.config.exchange_name,
                queue=temp_queue,
                routing_key=path
            )
            
            # 消費消息
            for method, properties, body in self.channel.consume(
                temp_queue,
                auto_ack=True,
                inactivity_timeout=10
            ):
                if method:
                    data = json.loads(body)
                    if data["path"] == path:
                        return data["data"]
            
            raise NotFoundError(f"Data not found: {path}")
        except NotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to load data: {str(e)}")
    
    def delete(self, path: str) -> None:
        """刪除數據
        
        Args:
            path: 數據路徑
        """
        try:
            # 發送刪除標記
            delete_marker = {
                "data": None,
                "path": path,
                "timestamp": time.time(),
                "deleted": True
            }
            
            # 發送消息
            self.channel.basic_publish(
                exchange=self.config.exchange_name,
                routing_key=path,
                body=json.dumps(delete_marker),
                properties=pika.BasicProperties(
                    delivery_mode=2 if self.config.message_persistent else 1,
                    content_type="application/json",
                    content_encoding="utf-8",
                    headers={"path": path, "deleted": True},
                    priority=self.config.message_priority,
                    timestamp=int(time.time())
                )
            )
        except Exception as e:
            raise StorageError(f"Failed to delete data: {str(e)}")
    
    def exists(self, path: str) -> bool:
        """檢查數據是否存在
        
        Args:
            path: 數據路徑
            
        Returns:
            數據是否存在
        """
        try:
            # 創建臨時隊列
            result = self.channel.queue_declare(queue="", exclusive=True)
            temp_queue = result.method.queue
            
            # 綁定臨時隊列
            self.channel.queue_bind(
                exchange=self.config.exchange_name,
                queue=temp_queue,
                routing_key=path
            )
            
            # 消費消息
            for method, properties, body in self.channel.consume(
                temp_queue,
                auto_ack=True,
                inactivity_timeout=10
            ):
                if method:
                    data = json.loads(body)
                    if data["path"] == path and not data.get("deleted", False):
                        return True
            
            return False
        except Exception as e:
            raise StorageError(f"Failed to check data existence: {str(e)}")
    
    def list(self, prefix: Optional[str] = None) -> List[str]:
        """列出數據路徑
        
        Args:
            prefix: 路徑前綴
            
        Returns:
            數據路徑列表
        """
        try:
            # 創建臨時隊列
            result = self.channel.queue_declare(queue="", exclusive=True)
            temp_queue = result.method.queue
            
            # 綁定臨時隊列
            self.channel.queue_bind(
                exchange=self.config.exchange_name,
                queue=temp_queue,
                routing_key="#" if prefix is None else f"{prefix}#"
            )
            
            # 收集路徑
            paths = set()
            for method, properties, body in self.channel.consume(
                temp_queue,
                auto_ack=True,
                inactivity_timeout=10
            ):
                if method:
                    data = json.loads(body)
                    path = data["path"]
                    if not data.get("deleted", False):
                        if prefix is None or path.startswith(prefix):
                            paths.add(path)
            
            return list(paths)
        except Exception as e:
            raise StorageError(f"Failed to list data: {str(e)}")
    
    def find(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """查詢數據
        
        Args:
            query: 查詢條件
            
        Returns:
            查詢結果列表
        """
        try:
            # 創建臨時隊列
            result = self.channel.queue_declare(queue="", exclusive=True)
            temp_queue = result.method.queue
            
            # 綁定臨時隊列
            self.channel.queue_bind(
                exchange=self.config.exchange_name,
                queue=temp_queue,
                routing_key="#"
            )
            
            # 收集結果
            results = []
            for method, properties, body in self.channel.consume(
                temp_queue,
                auto_ack=True,
                inactivity_timeout=10
            ):
                if method:
                    data = json.loads(body)
                    if not data.get("deleted", False):
                        # 檢查是否匹配查詢條件
                        match = True
                        for key, value in query.items():
                            if key not in data["data"] or data["data"][key] != value:
                                match = False
                                break
                        if match:
                            results.append(data["data"])
            
            return results
        except Exception as e:
            raise StorageError(f"Failed to find data: {str(e)}")
    
    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """統計數據數量
        
        Args:
            query: 查詢條件
            
        Returns:
            數據數量
        """
        try:
            # 創建臨時隊列
            result = self.channel.queue_declare(queue="", exclusive=True)
            temp_queue = result.method.queue
            
            # 綁定臨時隊列
            self.channel.queue_bind(
                exchange=self.config.exchange_name,
                queue=temp_queue,
                routing_key="#"
            )
            
            # 計數
            count = 0
            for method, properties, body in self.channel.consume(
                temp_queue,
                auto_ack=True,
                inactivity_timeout=10
            ):
                if method:
                    data = json.loads(body)
                    if not data.get("deleted", False):
                        if query is None:
                            count += 1
                        else:
                            # 檢查是否匹配查詢條件
                            match = True
                            for key, value in query.items():
                                if key not in data["data"] or data["data"][key] != value:
                                    match = False
                                    break
                            if match:
                                count += 1
            
            return count
        except Exception as e:
            raise StorageError(f"Failed to count data: {str(e)}")
    
    def batch_save(self, data_list: List[Dict[str, Any]]) -> None:
        """批量保存數據
        
        Args:
            data_list: 數據列表，每個元素包含 path 和 data
        """
        try:
            # 批量發送消息
            for item in data_list:
                path = item["path"]
                data = item["data"]
                
                # 添加時間戳
                data_with_timestamp = {
                    "data": data,
                    "path": path,
                    "timestamp": time.time()
                }
                
                # 發送消息
                self.channel.basic_publish(
                    exchange=self.config.exchange_name,
                    routing_key=path,
                    body=json.dumps(data_with_timestamp),
                    properties=pika.BasicProperties(
                        delivery_mode=2 if self.config.message_persistent else 1,
                        content_type="application/json",
                        content_encoding="utf-8",
                        headers={"path": path},
                        priority=self.config.message_priority,
                        timestamp=int(time.time())
                    )
                )
        except Exception as e:
            raise StorageError(f"Failed to batch save data: {str(e)}")
    
    def batch_load(self, paths: List[str]) -> List[Dict[str, Any]]:
        """批量加載數據
        
        Args:
            paths: 數據路徑列表
            
        Returns:
            數據列表，每個元素包含 path 和 data
        """
        try:
            # 創建臨時隊列
            result = self.channel.queue_declare(queue="", exclusive=True)
            temp_queue = result.method.queue
            
            # 綁定臨時隊列
            for path in paths:
                self.channel.queue_bind(
                    exchange=self.config.exchange_name,
                    queue=temp_queue,
                    routing_key=path
                )
            
            # 收集數據
            data_dict = {}
            for method, properties, body in self.channel.consume(
                temp_queue,
                auto_ack=True,
                inactivity_timeout=10
            ):
                if method:
                    data = json.loads(body)
                    path = data["path"]
                    if path in paths and not data.get("deleted", False):
                        data_dict[path] = data["data"]
            
            # 構建結果
            return [
                {"path": path, "data": data_dict.get(path)}
                for path in paths
            ]
        except Exception as e:
            raise StorageError(f"Failed to batch load data: {str(e)}")
    
    def batch_delete(self, paths: List[str]) -> None:
        """批量刪除數據
        
        Args:
            paths: 數據路徑列表
        """
        try:
            # 批量發送刪除標記
            for path in paths:
                delete_marker = {
                    "data": None,
                    "path": path,
                    "timestamp": time.time(),
                    "deleted": True
                }
                
                # 發送消息
                self.channel.basic_publish(
                    exchange=self.config.exchange_name,
                    routing_key=path,
                    body=json.dumps(delete_marker),
                    properties=pika.BasicProperties(
                        delivery_mode=2 if self.config.message_persistent else 1,
                        content_type="application/json",
                        content_encoding="utf-8",
                        headers={"path": path, "deleted": True},
                        priority=self.config.message_priority,
                        timestamp=int(time.time())
                    )
                )
        except Exception as e:
            raise StorageError(f"Failed to batch delete data: {str(e)}")
    
    def batch_exists(self, paths: List[str]) -> Dict[str, bool]:
        """批量檢查數據是否存在
        
        Args:
            paths: 數據路徑列表
            
        Returns:
            數據存在狀態字典
        """
        try:
            # 創建臨時隊列
            result = self.channel.queue_declare(queue="", exclusive=True)
            temp_queue = result.method.queue
            
            # 綁定臨時隊列
            for path in paths:
                self.channel.queue_bind(
                    exchange=self.config.exchange_name,
                    queue=temp_queue,
                    routing_key=path
                )
            
            # 收集存在狀態
            exists_dict = {path: False for path in paths}
            for method, properties, body in self.channel.consume(
                temp_queue,
                auto_ack=True,
                inactivity_timeout=10
            ):
                if method:
                    data = json.loads(body)
                    path = data["path"]
                    if path in paths and not data.get("deleted", False):
                        exists_dict[path] = True
            
            return exists_dict
        except Exception as e:
            raise StorageError(f"Failed to batch check data existence: {str(e)}")
    
    def subscribe(self, callback: Callable[[Dict[str, Any], str], None]) -> None:
        """訂閱數據變更
        
        Args:
            callback: 回調函數，接收數據和路徑
        """
        try:
            # 消費消息
            for method, properties, body in self.channel.consume(
                self.config.queue_name,
                auto_ack=True
            ):
                if method:
                    data = json.loads(body)
                    callback(data["data"], data["path"])
        except Exception as e:
            raise StorageError(f"Failed to subscribe: {str(e)}")
    
    def subscribe_with_filter(self, callback: Callable[[Dict[str, Any], str], None], filter_func: Callable[[Dict[str, Any], str], bool]) -> None:
        """訂閱數據變更（帶過濾）
        
        Args:
            callback: 回調函數，接收數據和路徑
            filter_func: 過濾函數，接收數據和路徑，返回是否處理
        """
        try:
            # 消費消息
            for method, properties, body in self.channel.consume(
                self.config.queue_name,
                auto_ack=True
            ):
                if method:
                    data = json.loads(body)
                    if filter_func(data["data"], data["path"]):
                        callback(data["data"], data["path"])
        except Exception as e:
            raise StorageError(f"Failed to subscribe with filter: {str(e)}")
    
    def stream(self, timeout: int = 10) -> Iterator[Dict[str, Any]]:
        """流式獲取數據
        
        Args:
            timeout: 超時時間（秒）
            
        Returns:
            數據迭代器
        """
        try:
            # 消費消息
            for method, properties, body in self.channel.consume(
                self.config.queue_name,
                auto_ack=True,
                inactivity_timeout=timeout
            ):
                if method:
                    data = json.loads(body)
                    if not data.get("deleted", False):
                        yield {
                            "path": data["path"],
                            "data": data["data"],
                            "timestamp": data["timestamp"]
                        }
        except Exception as e:
            raise StorageError(f"Failed to stream data: {str(e)}")
    
    def stream_with_filter(self, filter_func: Callable[[Dict[str, Any], str], bool], timeout: int = 10) -> Iterator[Dict[str, Any]]:
        """流式獲取數據（帶過濾）
        
        Args:
            filter_func: 過濾函數，接收數據和路徑，返回是否處理
            timeout: 超時時間（秒）
            
        Returns:
            數據迭代器
        """
        try:
            # 消費消息
            for method, properties, body in self.channel.consume(
                self.config.queue_name,
                auto_ack=True,
                inactivity_timeout=timeout
            ):
                if method:
                    data = json.loads(body)
                    if not data.get("deleted", False):
                        if filter_func(data["data"], data["path"]):
                            yield {
                                "path": data["path"],
                                "data": data["data"],
                                "timestamp": data["timestamp"]
                            }
        except Exception as e:
            raise StorageError(f"Failed to stream data with filter: {str(e)}")
    
    def cleanup(self) -> None:
        """清理資源"""
        try:
            if self.channel:
                self.channel.close()
            if self.connection:
                self.connection.close()
        except Exception as e:
            raise StorageError(f"Failed to cleanup: {str(e)}") 
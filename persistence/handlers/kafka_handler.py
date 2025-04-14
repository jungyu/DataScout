#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Kafka 存儲處理器
提供基於 Kafka 的數據存儲功能，支持生產者和消費者操作
"""

import json
import time
from typing import Dict, Any, List, Optional, Union, Callable, Iterator
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError, TopicAlreadyExistsError
from persistence.core.config import KafkaConfig
from persistence.core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

class KafkaHandler:
    """Kafka 存儲處理器類"""
    
    def __init__(self, config: Union[Dict[str, Any], KafkaConfig]):
        """初始化 Kafka 存儲處理器
        
        Args:
            config: 配置對象，可以是字典或 KafkaConfig 實例
        """
        if isinstance(config, dict):
            self.config = KafkaConfig(**config)
        else:
            self.config = config
        
        self.producer = None
        self.consumer = None
        self.admin_client = None
        self._setup_storage()
    
    def _setup_storage(self):
        """設置存儲環境"""
        try:
            # 創建管理客戶端
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=self.config.bootstrap_servers,
                client_id=f"{self.config.client_id}_admin",
                security_protocol=self.config.security_protocol,
                sasl_mechanism=self.config.sasl_mechanism,
                sasl_plain_username=self.config.sasl_plain_username,
                sasl_plain_password=self.config.sasl_plain_password,
                ssl_cafile=self.config.ssl_cafile,
                ssl_certfile=self.config.ssl_certfile,
                ssl_keyfile=self.config.ssl_keyfile
            )
            
            # 創建主題
            self._create_topic()
            
            # 創建生產者
            self._create_producer()
            
            # 創建消費者
            self._create_consumer()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Kafka: {str(e)}")
    
    def _create_topic(self):
        """創建主題"""
        try:
            # 檢查主題是否存在
            topics = self.admin_client.list_topics()
            if self.config.topic_name not in topics:
                # 創建主題
                topic = NewTopic(
                    name=self.config.topic_name,
                    num_partitions=self.config.partition_count,
                    replication_factor=self.config.replication_factor
                )
                self.admin_client.create_topics([topic])
        except TopicAlreadyExistsError:
            # 主題已存在，忽略錯誤
            pass
        except Exception as e:
            raise StorageError(f"Failed to create topic: {str(e)}")
    
    def _create_producer(self):
        """創建生產者"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.config.bootstrap_servers,
                client_id=f"{self.config.client_id}_producer",
                security_protocol=self.config.security_protocol,
                sasl_mechanism=self.config.sasl_mechanism,
                sasl_plain_username=self.config.sasl_plain_username,
                sasl_plain_password=self.config.sasl_plain_password,
                ssl_cafile=self.config.ssl_cafile,
                ssl_certfile=self.config.ssl_certfile,
                ssl_keyfile=self.config.ssl_keyfile,
                acks=self.config.acks,
                retries=self.config.retries,
                batch_size=self.config.batch_size,
                linger_ms=self.config.linger_ms,
                compression_type=self.config.compression_type,
                key_serializer=lambda k: json.dumps(k).encode('utf-8') if k else None,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except Exception as e:
            raise ConnectionError(f"Failed to create producer: {str(e)}")
    
    def _create_consumer(self):
        """創建消費者"""
        try:
            self.consumer = KafkaConsumer(
                bootstrap_servers=self.config.bootstrap_servers,
                client_id=f"{self.config.client_id}_consumer",
                group_id=self.config.group_id,
                security_protocol=self.config.security_protocol,
                sasl_mechanism=self.config.sasl_mechanism,
                sasl_plain_username=self.config.sasl_plain_username,
                sasl_plain_password=self.config.sasl_plain_password,
                ssl_cafile=self.config.ssl_cafile,
                ssl_certfile=self.config.ssl_certfile,
                ssl_keyfile=self.config.ssl_keyfile,
                auto_offset_reset=self.config.auto_offset_reset,
                enable_auto_commit=self.config.enable_auto_commit,
                auto_commit_interval_ms=self.config.auto_commit_interval_ms,
                max_poll_records=self.config.max_poll_records,
                key_deserializer=lambda k: json.loads(k.decode('utf-8')) if k else None,
                value_deserializer=lambda v: json.loads(v.decode('utf-8'))
            )
            
            # 訂閱主題
            self.consumer.subscribe([self.config.topic_name])
        except Exception as e:
            raise ConnectionError(f"Failed to create consumer: {str(e)}")
    
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
            future = self.producer.send(
                self.config.topic_name,
                key=path,
                value=data_with_timestamp
            )
            
            # 等待發送完成
            future.get(timeout=10)
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
            # 重置消費者偏移量
            self.consumer.seek_to_beginning()
            
            # 查找指定路徑的數據
            for message in self.consumer:
                if message.key == path:
                    return message.value["data"]
            
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
            future = self.producer.send(
                self.config.topic_name,
                key=path,
                value=delete_marker
            )
            
            # 等待發送完成
            future.get(timeout=10)
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
            # 重置消費者偏移量
            self.consumer.seek_to_beginning()
            
            # 查找指定路徑的數據
            for message in self.consumer:
                if message.key == path and not message.value.get("deleted", False):
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
            # 重置消費者偏移量
            self.consumer.seek_to_beginning()
            
            # 收集路徑
            paths = set()
            for message in self.consumer:
                path = message.key
                if not message.value.get("deleted", False):
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
            # 重置消費者偏移量
            self.consumer.seek_to_beginning()
            
            # 收集結果
            results = []
            for message in self.consumer:
                if not message.value.get("deleted", False):
                    data = message.value["data"]
                    # 檢查是否匹配查詢條件
                    match = True
                    for key, value in query.items():
                        if key not in data or data[key] != value:
                            match = False
                            break
                    if match:
                        results.append(data)
            
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
            # 重置消費者偏移量
            self.consumer.seek_to_beginning()
            
            # 計數
            count = 0
            for message in self.consumer:
                if not message.value.get("deleted", False):
                    if query is None:
                        count += 1
                    else:
                        data = message.value["data"]
                        # 檢查是否匹配查詢條件
                        match = True
                        for key, value in query.items():
                            if key not in data or data[key] != value:
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
            futures = []
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
                future = self.producer.send(
                    self.config.topic_name,
                    key=path,
                    value=data_with_timestamp
                )
                futures.append(future)
            
            # 等待所有消息發送完成
            for future in futures:
                future.get(timeout=10)
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
            # 重置消費者偏移量
            self.consumer.seek_to_beginning()
            
            # 收集數據
            data_dict = {}
            for message in self.consumer:
                path = message.key
                if path in paths and not message.value.get("deleted", False):
                    data_dict[path] = message.value["data"]
            
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
            futures = []
            for path in paths:
                delete_marker = {
                    "data": None,
                    "path": path,
                    "timestamp": time.time(),
                    "deleted": True
                }
                
                # 發送消息
                future = self.producer.send(
                    self.config.topic_name,
                    key=path,
                    value=delete_marker
                )
                futures.append(future)
            
            # 等待所有消息發送完成
            for future in futures:
                future.get(timeout=10)
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
            # 重置消費者偏移量
            self.consumer.seek_to_beginning()
            
            # 收集存在狀態
            exists_dict = {path: False for path in paths}
            for message in self.consumer:
                path = message.key
                if path in paths and not message.value.get("deleted", False):
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
            # 重置消費者偏移量
            self.consumer.seek_to_beginning()
            
            # 消費消息
            for message in self.consumer:
                data = message.value["data"]
                path = message.key
                callback(data, path)
        except Exception as e:
            raise StorageError(f"Failed to subscribe: {str(e)}")
    
    def subscribe_with_filter(self, callback: Callable[[Dict[str, Any], str], None], filter_func: Callable[[Dict[str, Any], str], bool]) -> None:
        """訂閱數據變更（帶過濾）
        
        Args:
            callback: 回調函數，接收數據和路徑
            filter_func: 過濾函數，接收數據和路徑，返回是否處理
        """
        try:
            # 重置消費者偏移量
            self.consumer.seek_to_beginning()
            
            # 消費消息
            for message in self.consumer:
                data = message.value["data"]
                path = message.key
                if filter_func(data, path):
                    callback(data, path)
        except Exception as e:
            raise StorageError(f"Failed to subscribe with filter: {str(e)}")
    
    def stream(self, timeout_ms: int = 1000) -> Iterator[Dict[str, Any]]:
        """流式獲取數據
        
        Args:
            timeout_ms: 超時時間（毫秒）
            
        Returns:
            數據迭代器
        """
        try:
            # 消費消息
            for message in self.consumer:
                if not message.value.get("deleted", False):
                    yield {
                        "path": message.key,
                        "data": message.value["data"],
                        "timestamp": message.value["timestamp"]
                    }
        except Exception as e:
            raise StorageError(f"Failed to stream data: {str(e)}")
    
    def stream_with_filter(self, filter_func: Callable[[Dict[str, Any], str], bool], timeout_ms: int = 1000) -> Iterator[Dict[str, Any]]:
        """流式獲取數據（帶過濾）
        
        Args:
            filter_func: 過濾函數，接收數據和路徑，返回是否處理
            timeout_ms: 超時時間（毫秒）
            
        Returns:
            數據迭代器
        """
        try:
            # 消費消息
            for message in self.consumer:
                if not message.value.get("deleted", False):
                    data = message.value["data"]
                    path = message.key
                    if filter_func(data, path):
                        yield {
                            "path": path,
                            "data": data,
                            "timestamp": message.value["timestamp"]
                        }
        except Exception as e:
            raise StorageError(f"Failed to stream data with filter: {str(e)}")
    
    def cleanup(self) -> None:
        """清理資源"""
        try:
            if self.producer:
                self.producer.close()
            if self.consumer:
                self.consumer.close()
            if self.admin_client:
                self.admin_client.close()
        except Exception as e:
            raise StorageError(f"Failed to cleanup: {str(e)}") 
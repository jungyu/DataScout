#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCP 客戶端基礎類
提供 MCP 協議的基礎功能
"""

import json
import time
import logging
import threading
import requests
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
from abc import ABC, abstractmethod
from api_client.core.config import APIConfig
from api_client.core.exceptions import APIError, AuthenticationError, RequestError, ConnectionError

class MCPClient(ABC):
    """MCP 客戶端基類"""
    
    def __init__(self, config: Union[Dict[str, Any], APIConfig]):
        """初始化 MCP 客戶端
        
        Args:
            config: 配置對象，可以是字典或配置類實例
        """
        # 設置日誌
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 初始化配置
        self.config = self._init_config(config)
        
        # 初始化連接狀態
        self.connected = False
        self.connecting = False
        self.disconnecting = False
        
        # 初始化回調函數
        self.message_callbacks = {}
        self.connection_callbacks = {}
        
        # 初始化線程
        self.worker_thread = None
        self.should_stop = False
    
    def _init_config(self, config: Union[Dict[str, Any], APIConfig]) -> APIConfig:
        """初始化配置
        
        Args:
            config: 配置對象，可以是字典或配置類實例
            
        Returns:
            配置對象
        """
        if isinstance(config, dict):
            return APIConfig(**config)
        return config
    
    @abstractmethod
    def connect(self) -> bool:
        """連接到服務器
        
        Returns:
            連接是否成功
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """斷開與服務器的連接
        
        Returns:
            斷開連接是否成功
        """
        pass
    
    @abstractmethod
    def publish(self, topic: str, message: Union[str, Dict[str, Any], bytes], qos: int = 0) -> bool:
        """發布消息
        
        Args:
            topic: 主題
            message: 消息內容
            qos: 服務質量等級
            
        Returns:
            發布是否成功
        """
        pass
    
    @abstractmethod
    def subscribe(self, topic: str, callback: Callable[[str, Dict[str, Any]], None], qos: int = 0) -> bool:
        """訂閱主題
        
        Args:
            topic: 主題
            callback: 回調函數
            qos: 服務質量等級
            
        Returns:
            訂閱是否成功
        """
        pass
    
    @abstractmethod
    def unsubscribe(self, topic: str) -> bool:
        """取消訂閱主題
        
        Args:
            topic: 主題
            
        Returns:
            取消訂閱是否成功
        """
        pass
    
    def register_message_callback(self, topic: str, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """註冊消息回調函數
        
        Args:
            topic: 主題
            callback: 回調函數
        """
        if topic not in self.message_callbacks:
            self.message_callbacks[topic] = []
        self.message_callbacks[topic].append(callback)
    
    def unregister_message_callback(self, topic: str, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """註銷消息回調函數
        
        Args:
            topic: 主題
            callback: 回調函數
        """
        if topic in self.message_callbacks and callback in self.message_callbacks[topic]:
            self.message_callbacks[topic].remove(callback)
    
    def register_connection_callback(self, event: str, callback: Callable[[], None]) -> None:
        """註冊連接事件回調函數
        
        Args:
            event: 事件名稱（connect, disconnect, reconnect）
            callback: 回調函數
        """
        if event not in self.connection_callbacks:
            self.connection_callbacks[event] = []
        self.connection_callbacks[event].append(callback)
    
    def unregister_connection_callback(self, event: str, callback: Callable[[], None]) -> None:
        """註銷連接事件回調函數
        
        Args:
            event: 事件名稱（connect, disconnect, reconnect）
            callback: 回調函數
        """
        if event in self.connection_callbacks and callback in self.connection_callbacks[event]:
            self.connection_callbacks[event].remove(callback)
    
    def _notify_connection_event(self, event: str) -> None:
        """通知連接事件
        
        Args:
            event: 事件名稱（connect, disconnect, reconnect）
        """
        if event in self.connection_callbacks:
            for callback in self.connection_callbacks[event]:
                try:
                    callback()
                except Exception as e:
                    self.logger.error(f"Error in connection callback: {e}")
    
    def _notify_message(self, topic: str, message: Dict[str, Any]) -> None:
        """通知消息
        
        Args:
            topic: 主題
            message: 消息內容
        """
        # 通知特定主題的回調
        if topic in self.message_callbacks:
            for callback in self.message_callbacks[topic]:
                try:
                    callback(topic, message)
                except Exception as e:
                    self.logger.error(f"Error in message callback: {e}")
        
        # 通知通配符主題的回調
        for wildcard_topic, callbacks in self.message_callbacks.items():
            if self._match_topic(topic, wildcard_topic):
                for callback in callbacks:
                    try:
                        callback(topic, message)
                    except Exception as e:
                        self.logger.error(f"Error in message callback: {e}")
    
    def _match_topic(self, topic: str, pattern: str) -> bool:
        """匹配主題
        
        Args:
            topic: 主題
            pattern: 模式
            
        Returns:
            是否匹配
        """
        # 將主題和模式分割為層級
        topic_parts = topic.split('/')
        pattern_parts = pattern.split('/')
        
        # 如果模式比主題長，則不匹配
        if len(pattern_parts) > len(topic_parts):
            return False
        
        # 逐層比較
        for i in range(len(pattern_parts)):
            # 如果模式部分為 #，則匹配所有後續層級
            if pattern_parts[i] == '#':
                return True
            
            # 如果模式部分為 +，則匹配任何一個層級
            if pattern_parts[i] == '+':
                continue
            
            # 如果模式部分與主題部分不匹配，則不匹配
            if pattern_parts[i] != topic_parts[i]:
                return False
        
        # 如果模式比主題短，則不匹配
        return len(pattern_parts) == len(topic_parts)
    
    def start_worker(self) -> None:
        """啟動工作線程"""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.should_stop = False
            self.worker_thread = threading.Thread(target=self._worker_loop)
            self.worker_thread.daemon = True
            self.worker_thread.start()
    
    def stop_worker(self) -> None:
        """停止工作線程"""
        self.should_stop = True
        if self.worker_thread is not None and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)
    
    @abstractmethod
    def _worker_loop(self) -> None:
        """工作線程循環"""
        pass
    
    def _serialize_message(self, message: Union[str, Dict[str, Any], bytes]) -> bytes:
        """序列化消息
        
        Args:
            message: 消息內容
            
        Returns:
            序列化後的消息
        """
        if isinstance(message, str):
            return message.encode('utf-8')
        elif isinstance(message, dict):
            return json.dumps(message).encode('utf-8')
        elif isinstance(message, bytes):
            return message
        else:
            raise ValueError(f"Unsupported message type: {type(message)}")
    
    def _deserialize_message(self, message: bytes) -> Dict[str, Any]:
        """反序列化消息
        
        Args:
            message: 消息內容
            
        Returns:
            反序列化後的消息
        """
        try:
            return json.loads(message.decode('utf-8'))
        except json.JSONDecodeError:
            return {"raw": message.decode('utf-8')}
        except UnicodeDecodeError:
            return {"raw": message} 
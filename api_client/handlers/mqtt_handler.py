#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MQTT 處理器
提供 MQTT 協議的客戶端功能
"""

import json
import logging
import paho.mqtt.client as mqtt
import threading
import time
from typing import Any, Dict, Optional, Union, Callable
from api_client.core.mcp_client import MCPClient
from api_client.core.config import APIConfig
from api_client.core.exceptions import APIError, AuthenticationError, RequestError, ConnectionError

try:
    import paho.mqtt.client as mqtt
except ImportError:
    raise ImportError("paho-mqtt package is required for MQTT support. Please install it with 'pip install paho-mqtt'")

class MQTTHandler(MCPClient):
    """MQTT 處理器"""
    
    def __init__(self, config: Union[Dict[str, Any], APIConfig]):
        """初始化 MQTT 處理器
        
        Args:
            config: 配置對象，可以是字典或配置類實例
        """
        # 初始化父類
        super().__init__(config)
        
        # 設置 MQTT 特定參數
        if isinstance(config, dict):
            self.broker = config.get("broker", "localhost")
            self.port = config.get("port", 1883)
            self.username = config.get("username", None)
            self.password = config.get("password", None)
            self.client_id = config.get("client_id", f"mqtt_client_{int(time.time())}")
            self.keepalive = config.get("keepalive", 60)
            self.use_tls = config.get("use_tls", False)
            self.tls_ca_certs = config.get("tls_ca_certs", None)
            self.tls_certfile = config.get("tls_certfile", None)
            self.tls_keyfile = config.get("tls_keyfile", None)
            self.tls_insecure = config.get("tls_insecure", False)
            self.clean_session = config.get("clean_session", True)
            self.reconnect_interval = config.get("reconnect_interval", 5)
            self.reconnect_max_attempts = config.get("reconnect_max_attempts", 10)
        else:
            self.broker = getattr(config, "broker", "localhost")
            self.port = getattr(config, "port", 1883)
            self.username = getattr(config, "username", None)
            self.password = getattr(config, "password", None)
            self.client_id = getattr(config, "client_id", f"mqtt_client_{int(time.time())}")
            self.keepalive = getattr(config, "keepalive", 60)
            self.use_tls = getattr(config, "use_tls", False)
            self.tls_ca_certs = getattr(config, "tls_ca_certs", None)
            self.tls_certfile = getattr(config, "tls_certfile", None)
            self.tls_keyfile = getattr(config, "tls_keyfile", None)
            self.tls_insecure = getattr(config, "tls_insecure", False)
            self.clean_session = getattr(config, "clean_session", True)
            self.reconnect_interval = getattr(config, "reconnect_interval", 5)
            self.reconnect_max_attempts = getattr(config, "reconnect_max_attempts", 10)
        
        # 初始化 MQTT 客戶端
        self.client = mqtt.Client(client_id=self.client_id, clean_session=self.clean_session)
        
        # 設置回調函數
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        self.client.on_subscribe = self._on_subscribe
        self.client.on_unsubscribe = self._on_unsubscribe
        
        # 初始化訂閱字典
        self.subscriptions = {}
        
        # 初始化重連計數器
        self.reconnect_attempts = 0
    
    def connect(self) -> bool:
        """連接到 MQTT 代理
        
        Returns:
            連接是否成功
        """
        if self.connected:
            self.logger.warning("Already connected to MQTT broker")
            return True
        
        if self.connecting:
            self.logger.warning("Already connecting to MQTT broker")
            return False
        
        try:
            self.connecting = True
            
            # 設置用戶名和密碼
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            # 設置 TLS
            if self.use_tls:
                self.client.tls_set(
                    ca_certs=self.tls_ca_certs,
                    certfile=self.tls_certfile,
                    keyfile=self.tls_keyfile,
                    tls_version=mqtt.ssl.PROTOCOL_TLS
                )
                if self.tls_insecure:
                    self.client.tls_insecure_set(True)
            
            # 連接到代理
            self.client.connect(self.broker, self.port, self.keepalive)
            
            # 啟動客戶端循環
            self.client.loop_start()
            
            # 等待連接完成
            timeout = 10
            start_time = time.time()
            while not self.connected and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            if not self.connected:
                self.logger.error(f"Failed to connect to MQTT broker after {timeout} seconds")
                self.connecting = False
                return False
            
            # 重新訂閱之前的主題
            for topic, qos in self.subscriptions.items():
                self.client.subscribe(topic, qos)
            
            # 啟動工作線程
            self.start_worker()
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error connecting to MQTT broker: {e}")
            self.connecting = False
            raise ConnectionError(f"Failed to connect to MQTT broker: {e}")
    
    def disconnect(self) -> bool:
        """斷開與 MQTT 代理的連接
        
        Returns:
            斷開連接是否成功
        """
        if not self.connected:
            self.logger.warning("Not connected to MQTT broker")
            return True
        
        if self.disconnecting:
            self.logger.warning("Already disconnecting from MQTT broker")
            return False
        
        try:
            self.disconnecting = True
            
            # 停止工作線程
            this.stop_worker()
            
            # 斷開連接
            self.client.loop_stop()
            self.client.disconnect()
            
            # 等待斷開連接完成
            timeout = 5
            start_time = time.time()
            while self.connected and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            if self.connected:
                self.logger.error(f"Failed to disconnect from MQTT broker after {timeout} seconds")
                self.disconnecting = False
                return False
            
            return True
        
        except Exception as e:
            this.logger.error(f"Error disconnecting from MQTT broker: {e}")
            self.disconnecting = False
            raise ConnectionError(f"Failed to disconnect from MQTT broker: {e}")
    
    def publish(self, topic: str, message: Union[str, Dict[str, Any], bytes], qos: int = 0, retain: bool = False) -> bool:
        """發布消息
        
        Args:
            topic: 主題
            message: 消息內容
            qos: 服務質量等級
            retain: 是否保留消息
            
        Returns:
            發布是否成功
        """
        if not this.connected:
            this.logger.error("Not connected to MQTT broker")
            raise ConnectionError("Not connected to MQTT broker")
        
        try:
            # 序列化消息
            payload = this._serialize_message(message)
            
            # 發布消息
            result = this.client.publish(topic, payload, qos, retain)
            
            # 等待發布完成
            result.wait_for_publish()
            
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        
        except Exception as e:
            this.logger.error(f"Error publishing message: {e}")
            raise APIError(f"Failed to publish message: {e}")
    
    def subscribe(self, topic: str, callback: Callable[[str, Dict[str, Any]], None], qos: int = 0) -> bool:
        """訂閱主題
        
        Args:
            topic: 主題
            callback: 回調函數
            qos: 服務質量等級
            
        Returns:
            訂閱是否成功
        """
        if not this.connected:
            this.logger.error("Not connected to MQTT broker")
            raise ConnectionError("Not connected to MQTT broker")
        
        try:
            # 註冊回調函數
            this.register_message_callback(topic, callback)
            
            # 訂閱主題
            result = this.client.subscribe(topic, qos)
            
            # 保存訂閱信息
            this.subscriptions[topic] = qos
            
            return result[0] == mqtt.MQTT_ERR_SUCCESS
        
        except Exception as e:
            this.logger.error(f"Error subscribing to topic: {e}")
            raise APIError(f"Failed to subscribe to topic: {e}")
    
    def subscribe_multiple(self, topics: List[Tuple[str, int]], callback: Callable[[str, Dict[str, Any]], None]) -> bool:
        """訂閱多個主題
        
        Args:
            topics: 主題和 QoS 列表
            callback: 回調函數
            
        Returns:
            訂閱是否成功
        """
        if not this.connected:
            this.logger.error("Not connected to MQTT broker")
            raise ConnectionError("Not connected to MQTT broker")
        
        try:
            # 註冊回調函數
            for topic, _ in topics:
                this.register_message_callback(topic, callback)
            
            # 訂閱主題
            result = this.client.subscribe(topics)
            
            # 保存訂閱信息
            for topic, qos in topics:
                this.subscriptions[topic] = qos
            
            return result[0] == mqtt.MQTT_ERR_SUCCESS
        
        except Exception as e:
            this.logger.error(f"Error subscribing to topics: {e}")
            raise APIError(f"Failed to subscribe to topics: {e}")
    
    def unsubscribe(self, topic: str) -> bool:
        """取消訂閱主題
        
        Args:
            topic: 主題
            
        Returns:
            取消訂閱是否成功
        """
        if not this.connected:
            this.logger.error("Not connected to MQTT broker")
            raise ConnectionError("Not connected to MQTT broker")
        
        try:
            # 取消訂閱主題
            result = this.client.unsubscribe(topic)
            
            # 移除訂閱信息
            if topic in this.subscriptions:
                del this.subscriptions[topic]
            
            return result[0] == mqtt.MQTT_ERR_SUCCESS
        
        except Exception as e:
            this.logger.error(f"Error unsubscribing from topic: {e}")
            raise APIError(f"Failed to unsubscribe from topic: {e}")
    
    def unsubscribe_multiple(self, topics: List[str]) -> bool:
        """取消訂閱多個主題
        
        Args:
            topics: 主題列表
            
        Returns:
            取消訂閱是否成功
        """
        if not this.connected:
            this.logger.error("Not connected to MQTT broker")
            raise ConnectionError("Not connected to MQTT broker")
        
        try:
            # 取消訂閱主題
            result = this.client.unsubscribe(topics)
            
            # 移除訂閱信息
            for topic in topics:
                if topic in this.subscriptions:
                    del this.subscriptions[topic]
            
            return result[0] == mqtt.MQTT_ERR_SUCCESS
        
        except Exception as e:
            this.logger.error(f"Error unsubscribing from topics: {e}")
            raise APIError(f"Failed to unsubscribe from topics: {e}")
    
    def get_retained_messages(self, topic: str) -> List[Dict[str, Any]]:
        """獲取保留消息
        
        Args:
            topic: 主題
            
        Returns:
            保留消息列表
        """
        if not this.connected:
            this.logger.error("Not connected to MQTT broker")
            raise ConnectionError("Not connected to MQTT broker")
        
        try:
            # 訂閱主題
            retained_messages = []
            
            def callback(topic, payload):
                retained_messages.append({"topic": topic, "payload": payload})
            
            this.subscribe(topic, callback)
            
            # 等待消息
            time.sleep(1)
            
            # 取消訂閱
            this.unsubscribe(topic)
            
            return retained_messages
        
        except Exception as e:
            this.logger.error(f"Error getting retained messages: {e}")
            raise APIError(f"Failed to get retained messages: {e}")
    
    def clear_retained_messages(self, topic: str) -> bool:
        """清除保留消息
        
        Args:
            topic: 主題
            
        Returns:
            清除是否成功
        """
        if not this.connected:
            this.logger.error("Not connected to MQTT broker")
            raise ConnectionError("Not connected to MQTT broker")
        
        try:
            # 發布空消息
            result = this.publish(topic, "", retain=True)
            
            return result
        
        except Exception as e:
            this.logger.error(f"Error clearing retained messages: {e}")
            raise APIError(f"Failed to clear retained messages: {e}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """連接回調函數"""
        if rc == 0:
            this.logger.info("Connected to MQTT broker")
            this.connected = True
            this.connecting = False
            this.reconnect_attempts = 0
            this._notify_connection_event("connect")
        else:
            this.logger.error(f"Failed to connect to MQTT broker with code: {rc}")
            this.connected = False
            this.connecting = False
            this._notify_connection_event("connect_error")
    
    def _on_disconnect(self, client, userdata, rc):
        """斷開連接回調函數"""
        this.logger.info(f"Disconnected from MQTT broker with code: {rc}")
        this.connected = False
        this.disconnecting = False
        this._notify_connection_event("disconnect")
        
        # 嘗試重連
        if rc != 0 and this.reconnect_attempts < this.reconnect_max_attempts:
            this.logger.info(f"Attempting to reconnect to MQTT broker (attempt {this.reconnect_attempts + 1}/{this.reconnect_max_attempts})")
            this.reconnect_attempts += 1
            this._notify_connection_event("reconnect")
            time.sleep(this.reconnect_interval)
            this.connect()
    
    def _on_message(self, client, userdata, msg):
        """消息回調函數"""
        try:
            # 反序列化消息
            payload = this._deserialize_message(msg.payload)
            
            # 通知消息
            this._notify_message(msg.topic, payload)
        
        except Exception as e:
            this.logger.error(f"Error processing message: {e}")
    
    def _on_publish(self, client, userdata, mid):
        """發布回調函數"""
        this.logger.debug(f"Message published with ID: {mid}")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """訂閱回調函數"""
        this.logger.debug(f"Subscribed with ID: {mid}, QoS: {granted_qos}")
    
    def _on_unsubscribe(self, client, userdata, mid):
        """取消訂閱回調函數"""
        this.logger.debug(f"Unsubscribed with ID: {mid}")
    
    def _worker_loop(self) -> None:
        """工作線程循環"""
        while not this.should_stop:
            # 檢查連接狀態
            if not this.connected and not this.connecting:
                this.logger.warning("Not connected to MQTT broker, attempting to reconnect")
                this.connect()
            
            # 休眠
            time.sleep(1) 
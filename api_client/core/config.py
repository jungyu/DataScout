#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模塊
提供各種配置類的基礎類和具體實現
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from api_client.core.exceptions import ConfigurationError
import time

@dataclass
class APIConfig:
    """API 基礎配置類"""
    
    # 基本配置
    api_type: str = "rest"  # API 類型：rest, graphql, soap, mqtt, webhook
    base_url: str = ""  # API 基礎 URL
    version: str = "v1"  # API 版本
    timeout: int = 30  # 請求超時時間（秒）
    retry_times: int = 3  # 重試次數
    
    # 認證配置
    auth_type: str = "none"  # 認證類型：none, basic, bearer, oauth2, api_key
    username: Optional[str] = None  # 用戶名
    password: Optional[str] = None  # 密碼
    token: Optional[str] = None  # 認證令牌
    api_key: Optional[str] = None  # API 密鑰
    api_key_header: str = "X-API-Key"  # API 密鑰請求頭
    api_key_param: Optional[str] = None  # API 密鑰參數名
    
    # 請求配置
    headers: Dict[str, str] = field(default_factory=dict)  # 請求頭
    params: Dict[str, Any] = field(default_factory=dict)  # 查詢參數
    verify_ssl: bool = True  # 是否驗證 SSL 證書
    proxy: Optional[str] = None  # 代理服務器
    
    # 響應配置
    response_type: str = "json"  # 響應類型：json, xml, text
    success_codes: List[int] = field(default_factory=lambda: [200, 201, 202, 204])  # 成功狀態碼
    error_codes: List[int] = field(default_factory=lambda: [400, 401, 403, 404, 500])  # 錯誤狀態碼
    
    # 路徑配置
    base_dir: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir: str = os.path.join(base_dir, "data")
    logs_dir: str = os.path.join(data_dir, "logs")
    errors_dir: str = os.path.join(data_dir, "errors")
    temp_dir: str = os.path.join(data_dir, "temp")
    
    # 日誌配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = os.path.join(logs_dir, "api.log")
    
    def __post_init__(self):
        """初始化後處理"""
        self._validate_config()
        self._create_directories()
    
    def _validate_config(self):
        """驗證配置"""
        # 驗證 API 類型
        valid_api_types = ["rest", "graphql", "soap", "mqtt", "webhook"]
        if self.api_type not in valid_api_types:
            raise ConfigurationError(f"不支持的 API 類型: {self.api_type}")
        
        # 驗證認證類型
        valid_auth_types = ["none", "basic", "bearer", "oauth2", "api_key"]
        if self.auth_type not in valid_auth_types:
            raise ConfigurationError(f"不支持的認證類型: {self.auth_type}")
        
        # 驗證響應類型
        valid_response_types = ["json", "xml", "text"]
        if self.response_type not in valid_response_types:
            raise ConfigurationError(f"不支持的響應類型: {self.response_type}")
        
        # 驗證超時設置
        if self.timeout < 0:
            raise ConfigurationError("超時時間不能為負數")
        
        # 驗證重試次數
        if self.retry_times < 0:
            raise ConfigurationError("重試次數不能為負數")
        
        # 驗證認證配置
        if self.auth_type == "basic" and (not self.username or not self.password):
            raise ConfigurationError("基本認證需要提供用戶名和密碼")
        elif self.auth_type == "bearer" and not self.token:
            raise ConfigurationError("Bearer 認證需要提供令牌")
        elif self.auth_type == "api_key" and not self.api_key:
            raise ConfigurationError("API 密鑰認證需要提供密鑰")
    
    def _create_directories(self):
        """創建必要的目錄"""
        directories = [
            self.data_dir,
            self.logs_dir,
            self.errors_dir,
            self.temp_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """將配置轉換為字典
        
        Returns:
            配置字典
        """
        return {
            "api_type": self.api_type,
            "base_url": self.base_url,
            "version": self.version,
            "timeout": self.timeout,
            "retry_times": self.retry_times,
            "auth_type": self.auth_type,
            "username": self.username,
            "password": self.password,
            "token": self.token,
            "api_key": self.api_key,
            "api_key_header": self.api_key_header,
            "api_key_param": self.api_key_param,
            "headers": self.headers,
            "params": self.params,
            "verify_ssl": self.verify_ssl,
            "proxy": self.proxy,
            "response_type": self.response_type,
            "success_codes": self.success_codes,
            "error_codes": self.error_codes,
            "base_dir": self.base_dir,
            "data_dir": self.data_dir,
            "logs_dir": self.logs_dir,
            "errors_dir": self.errors_dir,
            "temp_dir": self.temp_dir,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "log_file": self.log_file
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "APIConfig":
        """從字典創建配置
        
        Args:
            config_dict: 配置字典
            
        Returns:
            配置實例
        """
        return cls(**config_dict)
    
    def validate(self) -> bool:
        """驗證配置
        
        Returns:
            bool: 配置是否有效
        """
        self._validate_config()
        return True

class MQTTConfig(APIConfig):
    """MQTT 配置類"""
    
    def __init__(self, **kwargs):
        """初始化 MQTT 配置
        
        Args:
            **kwargs: 配置參數
                broker: MQTT 代理地址
                port: MQTT 代理端口
                username: 用戶名
                password: 密碼
                client_id: 客戶端 ID
                keepalive: 保活時間
                use_tls: 是否使用 TLS
                tls_ca_certs: TLS CA 證書路徑
                tls_certfile: TLS 證書文件路徑
                tls_keyfile: TLS 密鑰文件路徑
                tls_insecure: 是否允許不安全的 TLS 連接
                clean_session: 是否使用乾淨會話
                reconnect_interval: 重連間隔
                reconnect_max_attempts: 最大重連次數
        """
        super().__init__(**kwargs)
        
        # 設置默認值
        self.broker = kwargs.get("broker", "localhost")
        self.port = kwargs.get("port", 1883)
        self.username = kwargs.get("username", None)
        self.password = kwargs.get("password", None)
        self.client_id = kwargs.get("client_id", f"mqtt_client_{int(time.time())}")
        self.keepalive = kwargs.get("keepalive", 60)
        self.use_tls = kwargs.get("use_tls", False)
        self.tls_ca_certs = kwargs.get("tls_ca_certs", None)
        self.tls_certfile = kwargs.get("tls_certfile", None)
        self.tls_keyfile = kwargs.get("tls_keyfile", None)
        self.tls_insecure = kwargs.get("tls_insecure", False)
        self.clean_session = kwargs.get("clean_session", True)
        self.reconnect_interval = kwargs.get("reconnect_interval", 5)
        self.reconnect_max_attempts = kwargs.get("reconnect_max_attempts", 10)
    
    def validate(self) -> bool:
        """驗證配置是否有效
        
        Returns:
            配置是否有效
        """
        try:
            # 驗證必填參數
            if not self.broker:
                raise ValueError("MQTT broker address is required")
            
            # 驗證端口範圍
            if not isinstance(self.port, int) or not (1 <= self.port <= 65535):
                raise ValueError("MQTT port must be an integer between 1 and 65535")
            
            # 驗證保活時間
            if not isinstance(self.keepalive, int) or self.keepalive < 0:
                raise ValueError("MQTT keepalive must be a non-negative integer")
            
            # 驗證重連參數
            if not isinstance(self.reconnect_interval, (int, float)) or self.reconnect_interval < 0:
                raise ValueError("MQTT reconnect interval must be a non-negative number")
            
            if not isinstance(self.reconnect_max_attempts, int) or self.reconnect_max_attempts < 0:
                raise ValueError("MQTT reconnect max attempts must be a non-negative integer")
            
            # 驗證 TLS 配置
            if self.use_tls:
                if self.tls_ca_certs and not os.path.exists(self.tls_ca_certs):
                    raise ValueError(f"TLS CA certificates file not found: {self.tls_ca_certs}")
                
                if self.tls_certfile and not os.path.exists(self.tls_certfile):
                    raise ValueError(f"TLS certificate file not found: {self.tls_certfile}")
                
                if self.tls_keyfile and not os.path.exists(self.tls_keyfile):
                    raise ValueError(f"TLS key file not found: {self.tls_keyfile}")
            
            return True
        
        except Exception as e:
            raise ValueError(f"Invalid MQTT configuration: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """將配置轉換為字典
        
        Returns:
            配置字典
        """
        return {
            "broker": self.broker,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "client_id": self.client_id,
            "keepalive": self.keepalive,
            "use_tls": self.use_tls,
            "tls_ca_certs": self.tls_ca_certs,
            "tls_certfile": self.tls_certfile,
            "tls_keyfile": self.tls_keyfile,
            "tls_insecure": self.tls_insecure,
            "clean_session": self.clean_session,
            "reconnect_interval": self.reconnect_interval,
            "reconnect_max_attempts": self.reconnect_max_attempts
        }

class IFTTTConfig(APIConfig):
    """IFTTT 配置類"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化 IFTTT 配置
        
        Args:
            config: 配置字典
        """
        super().__init__(config)
        
        # 設置 IFTTT 特定參數
        self.webhook_key = self.config.get("webhook_key", None)
        self.webhook_url = self.config.get("webhook_url", None)
        self.event_name = self.config.get("event_name", None)
        self.value1 = self.config.get("value1", None)
        self.value2 = self.config.get("value2", None)
        self.value3 = self.config.get("value3", None)
        self.timeout = self.config.get("timeout", 30)
        self.retry_count = self.config.get("retry_count", 3)
        self.retry_delay = self.config.get("retry_delay", 1)
    
    def validate(self) -> bool:
        """驗證 IFTTT 配置
        
        Returns:
            驗證結果
        """
        # 檢查 webhook 密鑰
        if not self.webhook_key:
            raise ConfigurationError("IFTTT webhook key is required")
        
        # 檢查事件名稱
        if not self.event_name:
            raise ConfigurationError("IFTTT event name is required")
        
        # 檢查超時時間
        if self.timeout <= 0:
            raise ConfigurationError("IFTTT timeout must be greater than 0")
        
        # 檢查重試次數
        if self.retry_count < 0:
            raise ConfigurationError("IFTTT retry count must be greater than or equal to 0")
        
        # 檢查重試延遲
        if self.retry_delay < 0:
            raise ConfigurationError("IFTTT retry delay must be greater than or equal to 0")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典
        
        Returns:
            配置字典
        """
        return {
            "webhook_key": self.webhook_key,
            "webhook_url": self.webhook_url,
            "event_name": self.event_name,
            "value1": self.value1,
            "value2": self.value2,
            "value3": self.value3,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay
        }

class N8nConfig(APIConfig):
    """n8n 配置類"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化 n8n 配置
        
        Args:
            config: 配置字典
        """
        super().__init__(config)
        
        # 設置 n8n 特定參數
        self.api_key = self.config.get("api_key", None)
        self.base_url = self.config.get("base_url", "http://localhost:5678")
        self.webhook_id = self.config.get("webhook_id", None)
        self.webhook_url = self.config.get("webhook_url", None)
        self.timeout = self.config.get("timeout", 30)
        self.retry_count = self.config.get("retry_count", 3)
        self.retry_delay = self.config.get("retry_delay", 1)
        self.verify_ssl = self.config.get("verify_ssl", True)
        self.proxy = self.config.get("proxy", None)
        self.proxy_auth = self.config.get("proxy_auth", None)
        self.max_retries = self.config.get("max_retries", 3)
        self.backoff_factor = self.config.get("backoff_factor", 0.5)
        self.status_forcelist = self.config.get("status_forcelist", [500, 502, 503, 504])
        self.session = self.config.get("session", None)
    
    def validate(self) -> bool:
        """驗證 n8n 配置
        
        Returns:
            驗證結果
        """
        # 檢查 API 密鑰
        if not self.api_key:
            raise ConfigurationError("n8n API key is required")
        
        # 檢查基礎 URL
        if not self.base_url:
            raise ConfigurationError("n8n base URL is required")
        
        # 檢查超時時間
        if self.timeout <= 0:
            raise ConfigurationError("n8n timeout must be greater than 0")
        
        # 檢查重試次數
        if self.retry_count < 0:
            raise ConfigurationError("n8n retry count must be greater than or equal to 0")
        
        # 檢查重試延遲
        if self.retry_delay < 0:
            raise ConfigurationError("n8n retry delay must be greater than or equal to 0")
        
        # 檢查最大重試次數
        if self.max_retries < 0:
            raise ConfigurationError("n8n max retries must be greater than or equal to 0")
        
        # 檢查退避因子
        if self.backoff_factor < 0:
            raise ConfigurationError("n8n backoff factor must be greater than or equal to 0")
        
        # 檢查代理認證
        if self.proxy_auth and not isinstance(self.proxy_auth, tuple):
            raise ConfigurationError("n8n proxy auth must be a tuple of (username, password)")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典
        
        Returns:
            配置字典
        """
        return {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "webhook_id": self.webhook_id,
            "webhook_url": self.webhook_url,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay,
            "verify_ssl": self.verify_ssl,
            "proxy": self.proxy,
            "proxy_auth": self.proxy_auth,
            "max_retries": self.max_retries,
            "backoff_factor": self.backoff_factor,
            "status_forcelist": self.status_forcelist,
            "session": self.session
        }

class MakeConfig(APIConfig):
    """Make.com 配置類"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化 Make.com 配置
        
        Args:
            config: 配置字典
        """
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.make.com/v1")
        self.scenario_id = config.get("scenario_id")
        self.webhook_url = config.get("webhook_url")
        self.timeout = config.get("timeout", 30)
        self.retry_count = config.get("retry_count", 3)
        self.retry_delay = config.get("retry_delay", 1)
        self.max_retries = config.get("max_retries", 3)
        self.retry_backoff_factor = config.get("retry_backoff_factor", 1.5)
        self.retry_status_forcelist = config.get("retry_status_forcelist", [500, 502, 503, 504])
    
    def validate(self) -> bool:
        """驗證 Make.com 配置
        
        Returns:
            bool: 配置是否有效
            
        Raises:
            ConfigurationError: 配置錯誤
        """
        if not self.api_key:
            raise ConfigurationError("Make.com API key is required")
        
        if not self.base_url:
            raise ConfigurationError("Make.com base URL is required")
        
        if not isinstance(self.timeout, (int, float)) or self.timeout <= 0:
            raise ConfigurationError("Invalid timeout value")
        
        if not isinstance(self.retry_count, int) or self.retry_count < 0:
            raise ConfigurationError("Invalid retry count value")
        
        if not isinstance(self.retry_delay, (int, float)) or self.retry_delay < 0:
            raise ConfigurationError("Invalid retry delay value")
        
        if not isinstance(self.max_retries, int) or self.max_retries < 0:
            raise ConfigurationError("Invalid max retries value")
        
        if not isinstance(self.retry_backoff_factor, (int, float)) or self.retry_backoff_factor <= 0:
            raise ConfigurationError("Invalid retry backoff factor value")
        
        if not isinstance(self.retry_status_forcelist, list):
            raise ConfigurationError("Invalid retry status forcelist value")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        return {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "scenario_id": self.scenario_id,
            "webhook_url": self.webhook_url,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay,
            "max_retries": self.max_retries,
            "retry_backoff_factor": self.retry_backoff_factor,
            "retry_status_forcelist": self.retry_status_forcelist
        } 
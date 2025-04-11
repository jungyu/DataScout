#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API 處理模組

提供與第三方 API 和流程自動化平台（如 n8n、make.com）的介接功能。
包括：
1. REST API 介接
2. Webhook 處理
3. 流程自動化平台介接
4. API 認證和授權
5. 請求重試和錯誤處理
"""

import os
import json
import time
import logging
import requests
import hashlib
import hmac
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from enum import Enum
from dataclasses import dataclass
import threading
import queue
import uuid
from requests.exceptions import RequestException

# 嘗試導入可選依賴
try:
    import aiohttp
    import asyncio
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

try:
    from webhook import WebhookServer
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

from ...core.base import BaseExtractor
from ...core.exceptions import (
    NetworkError,
    AuthenticationError,
    RateLimitError,
    ParseError,
    handle_exception
)

# 從 src.core.utils 導入工具類
from src.core.utils import (
    ConfigUtils,
    Logger,
    URLUtils,
    DataProcessor
)

class APIMethod(Enum):
    """API 方法枚舉"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class APIAuthType(Enum):
    """API 認證類型枚舉"""
    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    HMAC = "hmac"


@dataclass
class APIConfig:
    """API 配置類"""
    # 基本配置
    base_url: str = ""
    endpoints: Dict[str, str] = None
    method: APIMethod = APIMethod.GET
    auth_type: APIAuthType = APIAuthType.NONE
    
    # 認證配置
    auth_config: Dict[str, Any] = None
    
    # 請求配置
    headers: Dict[str, str] = None
    params: Dict[str, Any] = None
    data: Dict[str, Any] = None
    json_data: Dict[str, Any] = None
    files: Dict[str, Any] = None
    timeout: int = 30
    verify_ssl: bool = True
    allow_redirects: bool = True
    proxies: Dict[str, str] = None
    
    # 響應配置
    expected_status: List[int] = None
    response_type: str = "json"
    response_encoding: str = "utf-8"
    
    # 重試配置
    max_retries: int = 3
    retry_delay: int = 1
    retry_codes: List[int] = None
    
    # 限流配置
    rate_limit: int = 0
    rate_limit_period: int = 60
    
    # 日誌配置
    log_requests: bool = True
    log_responses: bool = True
    log_errors: bool = True
    
    def __post_init__(self):
        """初始化後處理"""
        if self.endpoints is None:
            self.endpoints = {}
        if self.auth_config is None:
            self.auth_config = {}
        if self.headers is None:
            self.headers = {}
        if self.params is None:
            self.params = {}
        if self.data is None:
            self.data = {}
        if self.json_data is None:
            self.json_data = {}
        if self.files is None:
            self.files = {}
        if self.expected_status is None:
            self.expected_status = [200]
        if self.retry_codes is None:
            self.retry_codes = [408, 429, 500, 502, 503, 504]


class APIHandler(BaseExtractor):
    """API 處理器類"""
    
    def __init__(self, config: Union[Dict[str, Any], APIConfig]):
        """
        初始化 API 處理器
        
        Args:
            config: 配置字典或 APIConfig 對象
        """
        if isinstance(config, dict):
            config = APIConfig(**config)
        super().__init__(config)
        
        # 初始化工具類
        self.config_utils = ConfigUtils()
        self.logger = Logger.get_logger("APIHandler")
        self.url_utils = URLUtils()
        self.data_processor = DataProcessor()
        
        # 初始化會話
        self.session = requests.Session()
        
        # 設置基本配置
        self._setup_session()
        
        # 初始化限流器
        self._setup_rate_limiter()
        
    def _setup_session(self) -> None:
        """設置會話配置"""
        # 設置基本配置
        self.session.verify = self.config.verify_ssl
        
        # 設置代理
        if self.config.proxies:
            self.session.proxies = self.config.proxies
            
        # 設置認證
        self._setup_auth()
        
        # 設置請求頭
        if self.config.headers:
            self.session.headers.update(self.config.headers)
            
    def _setup_auth(self) -> None:
        """設置認證"""
        auth_type = self.config.auth_type
        auth_config = self.config.auth_config
        
        if auth_type == APIAuthType.BASIC:
            username = auth_config.get("username")
            password = auth_config.get("password")
            if not username or not password:
                raise ConfigError("Basic 認證需要用戶名和密碼")
            self.session.auth = (username, password)
            
        elif auth_type == APIAuthType.BEARER:
            token = auth_config.get("token")
            if not token:
                raise ConfigError("Bearer 認證需要 token")
            self.session.headers["Authorization"] = f"Bearer {token}"
            
        elif auth_type == APIAuthType.API_KEY:
            key = auth_config.get("key")
            value = auth_config.get("value")
            in_header = auth_config.get("in_header", True)
            if not key or not value:
                raise ConfigError("API Key 認證需要 key 和 value")
            if in_header:
                self.session.headers[key] = value
            else:
                self.session.params[key] = value
                
        elif auth_type == APIAuthType.OAUTH2:
            token = auth_config.get("access_token")
            if not token:
                raise ConfigError("OAuth2 認證需要 access_token")
            self.session.headers["Authorization"] = f"Bearer {token}"
            
        elif auth_type == APIAuthType.HMAC:
            key = auth_config.get("key")
            secret = auth_config.get("secret")
            if not key or not secret:
                raise ConfigError("HMAC 認證需要 key 和 secret")
            self._setup_hmac_auth(key, secret)
            
    def _setup_hmac_auth(self, key: str, secret: str) -> None:
        """
        設置 HMAC 認證
        
        Args:
            key: API Key
            secret: API Secret
        """
        def hmac_auth(request):
            # 生成時間戳
            timestamp = str(int(time.time()))
            
            # 生成隨機 nonce
            nonce = str(uuid.uuid4())
            
            # 構建簽名字符串
            string_to_sign = "\n".join([
                request.method,
                request.url,
                timestamp,
                nonce
            ])
            
            # 計算簽名
            signature = hmac.new(
                secret.encode("utf-8"),
                string_to_sign.encode("utf-8"),
                hashlib.sha256
            ).hexdigest()
            
            # 添加認證頭
            request.headers.update({
                "X-API-Key": key,
                "X-Timestamp": timestamp,
                "X-Nonce": nonce,
                "X-Signature": signature
            })
            
            return request
            
        self.session.auth = hmac_auth
        
    def _setup_rate_limiter(self) -> None:
        """設置限流器"""
        if self.config.rate_limit > 0:
            self.rate_limit = self.config.rate_limit
            self.rate_limit_period = self.config.rate_limit_period
            self.request_times = queue.Queue()
            
    def _check_rate_limit(self) -> None:
        """檢查限流"""
        if not hasattr(self, "rate_limit"):
            return
            
        current_time = time.time()
        
        # 清理過期的請求時間
        while (
            not self.request_times.empty() and
            current_time - self.request_times.queue[0] > self.rate_limit_period
        ):
            self.request_times.get()
            
        # 檢查是否超過限流
        if self.request_times.qsize() >= self.rate_limit:
            sleep_time = (
                self.request_times.queue[0] +
                self.rate_limit_period -
                current_time
            )
            if sleep_time > 0:
                time.sleep(sleep_time)
                
        # 記錄請求時間
        self.request_times.put(current_time)
        
    def _build_url(self, endpoint: str) -> str:
        """
        構建完整的 URL
        
        Args:
            endpoint: API 端點
            
        Returns:
            完整的 URL
        """
        # 獲取端點 URL
        if endpoint in self.config.endpoints:
            endpoint = self.config.endpoints[endpoint]
            
        # 構建完整 URL
        url = self.url_utils.join_url(self.config.base_url, endpoint)
        
        return url
        
    def _send_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        發送請求
        
        Args:
            method: 請求方法
            endpoint: API 端點
            **kwargs: 請求參數
            
        Returns:
            響應對象
        """
        # 檢查限流
        self._check_rate_limit()
        
        # 構建 URL
        url = self._build_url(endpoint)
        
        # 合併配置
        kwargs = self._merge_request_config(kwargs)
        
        # 發送請求
        try:
            response = self.session.request(method, url, **kwargs)
            
            # 記錄請求
            if self.config.log_requests:
                self._log_request(method, url, kwargs)
                
            # 記錄響應
            if self.config.log_responses:
                self._log_response(response)
                
            # 檢查響應狀態
            self._check_response(response)
            
            return response
            
        except requests.exceptions.RequestException as e:
            if self.config.log_errors:
                self._log_error(e)
            raise NetworkError(f"請求失敗: {str(e)}")
            
    def _merge_request_config(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        合併請求配置
        
        Args:
            kwargs: 請求參數
            
        Returns:
            合併後的配置
        """
        config = {
            "timeout": self.config.timeout,
            "verify": self.config.verify_ssl,
            "allow_redirects": self.config.allow_redirects
        }
        
        # 合併查詢參數
        params = kwargs.pop("params", {})
        if self.config.params:
            params.update(self.config.params)
        if params:
            config["params"] = params
            
        # 合併表單數據
        data = kwargs.pop("data", {})
        if self.config.data:
            data.update(self.config.data)
        if data:
            config["data"] = data
            
        # 合併 JSON 數據
        json_data = kwargs.pop("json", {})
        if self.config.json_data:
            json_data.update(self.config.json_data)
        if json_data:
            config["json"] = json_data
            
        # 合併文件
        files = kwargs.pop("files", {})
        if self.config.files:
            files.update(self.config.files)
        if files:
            config["files"] = files
            
        # 合併其他參數
        config.update(kwargs)
        
        return config
        
    def _check_response(self, response: requests.Response) -> None:
        """
        檢查響應
        
        Args:
            response: 響應對象
        """
        if response.status_code not in self.config.expected_status:
            if self.config.log_errors:
                self._log_error(response)
            raise NetworkError(
                f"請求失敗: {response.status_code} {response.reason}"
            )
            
    def _log_request(
        self,
        method: str,
        url: str,
        kwargs: Dict[str, Any]
    ) -> None:
        """
        記錄請求
        
        Args:
            method: 請求方法
            url: 請求 URL
            kwargs: 請求參數
        """
        self.logger.info(f"發送請求: {method} {url}")
        self.logger.debug(f"請求參數: {kwargs}")
        
    def _log_response(self, response: requests.Response) -> None:
        """
        記錄響應
        
        Args:
            response: 響應對象
        """
        self.logger.info(
            f"收到響應: {response.status_code} {response.reason}"
        )
        self.logger.debug(f"響應內容: {response.text[:1000]}")
        
    def _log_error(self, error: Union[Exception, requests.Response]) -> None:
        """
        記錄錯誤
        
        Args:
            error: 錯誤對象
        """
        if isinstance(error, requests.Response):
            self.logger.error(
                f"請求失敗: {error.status_code} {error.reason}"
            )
            self.logger.debug(f"錯誤內容: {error.text[:1000]}")
        else:
            self.logger.error(f"請求異常: {str(error)}")
            
    def _parse_response(
        self,
        response: requests.Response
    ) -> Any:
        """
        解析響應
        
        Args:
            response: 響應對象
            
        Returns:
            解析後的數據
        """
        # 設置編碼
        response.encoding = self.config.response_encoding
        
        # 根據響應類型解析
        if self.config.response_type == "json":
            try:
                return response.json()
            except ValueError as e:
                raise ParseError(f"解析 JSON 失敗: {str(e)}")
                
        elif self.config.response_type == "text":
            return response.text
            
        elif self.config.response_type == "binary":
            return response.content
            
        else:
            raise ConfigError(f"不支持的響應類型: {self.config.response_type}")
            
    def request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Any:
        """
        發送請求
        
        Args:
            method: 請求方法
            endpoint: API 端點
            **kwargs: 請求參數
            
        Returns:
            響應數據
        """
        retries = kwargs.pop("retries", self.config.max_retries)
        retry_delay = kwargs.pop("retry_delay", self.config.retry_delay)
        
        for i in range(retries):
            try:
                # 發送請求
                response = self._send_request(method, endpoint, **kwargs)
                
                # 解析響應
                return self._parse_response(response)
                
            except Exception as e:
                # 最後一次重試失敗
                if i == retries - 1:
                    raise
                    
                # 判斷是否需要重試
                if (
                    isinstance(e, NetworkError) and
                    hasattr(e, "response") and
                    e.response.status_code in self.config.retry_codes
                ):
                    # 等待後重試
                    time.sleep(retry_delay * (i + 1))
                    continue
                    
                # 其他錯誤直接拋出
                raise
                
    def get(self, endpoint: str, **kwargs) -> Any:
        """發送 GET 請求"""
        return self.request("GET", endpoint, **kwargs)
        
    def post(self, endpoint: str, **kwargs) -> Any:
        """發送 POST 請求"""
        return self.request("POST", endpoint, **kwargs)
        
    def put(self, endpoint: str, **kwargs) -> Any:
        """發送 PUT 請求"""
        return self.request("PUT", endpoint, **kwargs)
        
    def delete(self, endpoint: str, **kwargs) -> Any:
        """發送 DELETE 請求"""
        return self.request("DELETE", endpoint, **kwargs)
        
    def patch(self, endpoint: str, **kwargs) -> Any:
        """發送 PATCH 請求"""
        return self.request("PATCH", endpoint, **kwargs)
        
    def head(self, endpoint: str, **kwargs) -> Any:
        """發送 HEAD 請求"""
        return self.request("HEAD", endpoint, **kwargs)
        
    def options(self, endpoint: str, **kwargs) -> Any:
        """發送 OPTIONS 請求"""
        return self.request("OPTIONS", endpoint, **kwargs)
        
    def __del__(self):
        """清理資源"""
        if hasattr(self, "session"):
            try:
                self.session.close()
            except:
                pass


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, rate_limit: int, burst: int = 0):
        """
        初始化速率限制器
        
        Args:
            rate_limit: 每秒請求數
            burst: 突發請求數
        """
        self.rate_limit = rate_limit
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
        self.lock = threading.Lock()
        
    def acquire(self):
        """獲取令牌"""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.last_update = now
            
            # 添加新令牌
            self.tokens = min(
                self.burst,
                self.tokens + elapsed * self.rate_limit
            )
            
            # 檢查是否有足夠的令牌
            if self.tokens < 1:
                # 計算等待時間
                wait_time = (1 - self.tokens) / self.rate_limit
                time.sleep(wait_time)
                self.tokens = 0
            else:
                # 消耗令牌
                self.tokens -= 1 
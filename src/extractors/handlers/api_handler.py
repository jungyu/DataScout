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

from src.extractors.exceptions import APIError


class APIType(Enum):
    """API 類型"""
    REST = "rest"
    WEBHOOK = "webhook"
    N8N = "n8n"
    MAKE = "make"
    ZAPIER = "zapier"
    IFTTT = "ifttt"
    CUSTOM = "custom"
    AUTOMATION = "automation"


class AuthType(Enum):
    """認證類型"""
    NONE = "none"
    API_KEY = "api_key"
    OAUTH = "oauth"
    BASIC = "basic"
    JWT = "jwt"
    CUSTOM = "custom"


@dataclass
class APIConfig:
    """API 配置"""
    type: APIType
    url: str
    auth_type: AuthType
    auth_params: Dict[str, Any]
    headers: Dict[str, str]
    timeout: int
    retry_count: int
    retry_delay: int
    options: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIConfig':
        """從字典創建配置"""
        return cls(
            type=APIType(data.get("type", "rest")),
            url=data.get("url", ""),
            auth_type=AuthType(data.get("auth_type", "none")),
            auth_params=data.get("auth_params", {}),
            headers=data.get("headers", {}),
            timeout=int(data.get("timeout", 30)),
            retry_count=int(data.get("retry_count", 3)),
            retry_delay=int(data.get("retry_delay", 1)),
            options=data.get("options", {})
        )


class APIHandler:
    """
    API 處理器，支持多種 API 類型和認證方式
    
    提供與第三方 API 和流程自動化平台的介接功能
    """
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        config_file: Optional[str] = None,
        default_timeout: int = 30,
        default_retry_count: int = 3,
        default_retry_delay: int = 1
    ):
        """
        初始化 API 處理器
        
        Args:
            logger: 日誌記錄器
            config_file: API 配置文件路徑
            default_timeout: 默認超時時間（秒）
            default_retry_count: 默認重試次數
            default_retry_delay: 默認重試延遲（秒）
        """
        self.logger = logger or logging.getLogger(__name__)
        self.default_timeout = default_timeout
        self.default_retry_count = default_retry_count
        self.default_retry_delay = default_retry_delay
        
        # API 配置
        self.api_configs: Dict[str, APIConfig] = {}
        
        # 請求統計
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_response_time = 0
        
        # 請求隊列（用於異步處理）
        self.request_queue = queue.Queue()
        
        # 請求鎖（用於並發控制）
        self.request_locks = {}
        
        # 加載配置
        if config_file:
            self.load_config_from_file(config_file)
        
        self.logger.info("API 處理器初始化完成")
    
    def load_config_from_file(self, config_file: str) -> None:
        """
        從文件加載 API 配置
        
        Args:
            config_file: 配置文件路徑
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 加載 API 配置
            if "apis" in config_data:
                for api_name, api_config in config_data["apis"].items():
                    self.api_configs[api_name] = APIConfig.from_dict(api_config)
                    self.logger.info(f"已加載 API 配置: {api_name}")
            
            self.logger.info(f"已從 {config_file} 加載 {len(self.api_configs)} 個 API 配置")
        
        except Exception as e:
            self.logger.error(f"加載 API 配置失敗: {str(e)}")
            raise APIError(f"加載 API 配置失敗: {str(e)}")
    
    def register_api(self, name: str, config: APIConfig) -> None:
        """
        註冊 API 配置
        
        Args:
            name: API 名稱
            config: API 配置
        """
        self.api_configs[name] = config
        self.logger.info(f"已註冊 API: {name}")
    
    def call_api(
        self,
        api_name: str,
        method: str = "GET",
        endpoint: str = "",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retry_count: Optional[int] = None,
        retry_delay: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        調用 API
        
        Args:
            api_name: API 名稱
            method: HTTP 方法
            endpoint: API 端點
            params: URL 參數
            data: 表單數據
            json_data: JSON 數據
            files: 文件數據
            headers: 請求頭
            timeout: 超時時間
            retry_count: 重試次數
            retry_delay: 重試延遲
            **kwargs: 其他參數
            
        Returns:
            API 響應
            
        Raises:
            APIError: API 調用失敗時拋出
        """
        # 檢查 API 配置是否存在
        if api_name not in self.api_configs:
            error_msg = f"未找到 API 配置: {api_name}"
            self.logger.error(error_msg)
            raise APIError(error_msg)
        
        # 獲取 API 配置
        config = self.api_configs[api_name]
        
        # 設置默認值
        timeout = timeout or config.timeout
        retry_count = retry_count or config.retry_count
        retry_delay = retry_delay or config.retry_delay
        
        # 構建完整 URL
        url = config.url.rstrip('/') + '/' + endpoint.lstrip('/')
        
        # 合併請求頭
        merged_headers = config.headers.copy()
        if headers:
            merged_headers.update(headers)
        
        # 添加認證信息
        self._add_auth_headers(config, merged_headers, params, data, json_data)
        
        # 記錄請求開始時間
        start_time = time.time()
        
        # 執行請求（帶重試）
        last_error = None
        for attempt in range(retry_count + 1):
            try:
                # 獲取請求鎖
                lock_key = f"{api_name}_{method}_{endpoint}"
                if lock_key not in self.request_locks:
                    self.request_locks[lock_key] = threading.Lock()
                
                with self.request_locks[lock_key]:
                    # 發送請求
                    response = requests.request(
                        method=method,
                        url=url,
                        params=params,
                        data=data,
                        json=json_data,
                        files=files,
                        headers=merged_headers,
                        timeout=timeout,
                        **kwargs
                    )
                
                # 檢查響應狀態
                response.raise_for_status()
                
                # 更新統計信息
                self.request_count += 1
                self.success_count += 1
                self.total_response_time += time.time() - start_time
                
                # 返回響應
                return response.json()
            
            except requests.exceptions.RequestException as e:
                last_error = e
                self.logger.warning(f"API 請求失敗 (嘗試 {attempt + 1}/{retry_count + 1}): {str(e)}")
                
                # 如果不是最後一次嘗試，則等待後重試
                if attempt < retry_count:
                    time.sleep(retry_delay)
        
        # 所有重試都失敗了
        self.request_count += 1
        self.error_count += 1
        self.total_response_time += time.time() - start_time
        
        error_msg = f"API 請求失敗 ({api_name}): {str(last_error)}"
        self.logger.error(error_msg)
        raise APIError(error_msg)
    
    def _add_auth_headers(
        self,
        config: APIConfig,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]],
        data: Optional[Dict[str, Any]],
        json_data: Optional[Dict[str, Any]]
    ) -> None:
        """
        添加認證頭
        
        Args:
            config: API 配置
            headers: 請求頭
            params: URL 參數
            data: 表單數據
            json_data: JSON 數據
        """
        auth_type = config.auth_type
        auth_params = config.auth_params
        
        if auth_type == AuthType.NONE:
            return
        
        elif auth_type == AuthType.API_KEY:
            # API 密鑰認證
            key_name = auth_params.get("key_name", "api_key")
            key_value = auth_params.get("key_value", "")
            key_in_header = auth_params.get("key_in_header", True)
            
            if key_in_header:
                headers[key_name] = key_value
            else:
                if params is None:
                    params = {}
                params[key_name] = key_value
        
        elif auth_type == AuthType.OAUTH:
            # OAuth 認證
            token = auth_params.get("token", "")
            token_type = auth_params.get("token_type", "Bearer")
            headers["Authorization"] = f"{token_type} {token}"
        
        elif auth_type == AuthType.BASIC:
            # 基本認證
            username = auth_params.get("username", "")
            password = auth_params.get("password", "")
            auth_str = f"{username}:{password}"
            auth_bytes = auth_str.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            headers["Authorization"] = f"Basic {auth_b64}"
        
        elif auth_type == AuthType.JWT:
            # JWT 認證
            token = auth_params.get("token", "")
            headers["Authorization"] = f"Bearer {token}"
        
        elif auth_type == AuthType.CUSTOM:
            # 自定義認證
            custom_func = auth_params.get("custom_func")
            if custom_func and callable(custom_func):
                custom_func(headers, params, data, json_data)
    
    async def call_api_async(
        self,
        api_name: str,
        method: str = "GET",
        endpoint: str = "",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retry_count: Optional[int] = None,
        retry_delay: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        異步調用 API
        
        Args:
            api_name: API 名稱
            method: HTTP 方法
            endpoint: API 端點
            params: URL 參數
            data: 表單數據
            json_data: JSON 數據
            files: 文件數據
            headers: 請求頭
            timeout: 超時時間
            retry_count: 重試次數
            retry_delay: 重試延遲
            **kwargs: 其他參數
            
        Returns:
            API 響應
            
        Raises:
            APIError: API 調用失敗時拋出
        """
        if not ASYNC_AVAILABLE:
            raise APIError("異步功能不可用，請安裝 aiohttp 庫")
        
        # 檢查 API 配置是否存在
        if api_name not in self.api_configs:
            error_msg = f"未找到 API 配置: {api_name}"
            self.logger.error(error_msg)
            raise APIError(error_msg)
        
        # 獲取 API 配置
        config = self.api_configs[api_name]
        
        # 設置默認值
        timeout = timeout or config.timeout
        retry_count = retry_count or config.retry_count
        retry_delay = retry_delay or config.retry_delay
        
        # 構建完整 URL
        url = config.url.rstrip('/') + '/' + endpoint.lstrip('/')
        
        # 合併請求頭
        merged_headers = config.headers.copy()
        if headers:
            merged_headers.update(headers)
        
        # 添加認證信息
        self._add_auth_headers(config, merged_headers, params, data, json_data)
        
        # 記錄請求開始時間
        start_time = time.time()
        
        # 執行請求（帶重試）
        last_error = None
        for attempt in range(retry_count + 1):
            try:
                # 發送請求
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method=method,
                        url=url,
                        params=params,
                        data=data,
                        json=json_data,
                        headers=merged_headers,
                        timeout=timeout,
                        **kwargs
                    ) as response:
                        # 檢查響應狀態
                        response.raise_for_status()
                        
                        # 更新統計信息
                        self.request_count += 1
                        self.success_count += 1
                        self.total_response_time += time.time() - start_time
                        
                        # 返回響應
                        return await response.json()
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_error = e
                self.logger.warning(f"異步 API 請求失敗 (嘗試 {attempt + 1}/{retry_count + 1}): {str(e)}")
                
                # 如果不是最後一次嘗試，則等待後重試
                if attempt < retry_count:
                    await asyncio.sleep(retry_delay)
        
        # 所有重試都失敗了
        self.request_count += 1
        self.error_count += 1
        self.total_response_time += time.time() - start_time
        
        error_msg = f"異步 API 請求失敗 ({api_name}): {str(last_error)}"
        self.logger.error(error_msg)
        raise APIError(error_msg)
    
    def queue_api_request(
        self,
        api_name: str,
        method: str = "GET",
        endpoint: str = "",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retry_count: Optional[int] = None,
        retry_delay: Optional[int] = None,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        **kwargs
    ) -> str:
        """
        將 API 請求加入隊列
        
        Args:
            api_name: API 名稱
            method: HTTP 方法
            endpoint: API 端點
            params: URL 參數
            data: 表單數據
            json_data: JSON 數據
            files: 文件數據
            headers: 請求頭
            timeout: 超時時間
            retry_count: 重試次數
            retry_delay: 重試延遲
            callback: 回調函數
            **kwargs: 其他參數
            
        Returns:
            請求 ID
        """
        # 生成請求 ID
        request_id = str(uuid.uuid4())
        
        # 構建請求參數
        request_params = {
            "request_id": request_id,
            "api_name": api_name,
            "method": method,
            "endpoint": endpoint,
            "params": params,
            "data": data,
            "json_data": json_data,
            "files": files,
            "headers": headers,
            "timeout": timeout,
            "retry_count": retry_count,
            "retry_delay": retry_delay,
            "callback": callback,
            "kwargs": kwargs
        }
        
        # 加入隊列
        self.request_queue.put(request_params)
        
        self.logger.info(f"API 請求已加入隊列: {request_id}")
        return request_id
    
    def process_request_queue(self, max_requests: int = 10) -> List[Dict[str, Any]]:
        """
        處理請求隊列
        
        Args:
            max_requests: 最大處理請求數
            
        Returns:
            處理結果列表
        """
        results = []
        
        # 處理隊列中的請求
        for _ in range(min(max_requests, self.request_queue.qsize())):
            try:
                # 獲取請求參數
                request_params = self.request_queue.get_nowait()
                
                # 執行請求
                try:
                    result = self.call_api(
                        api_name=request_params["api_name"],
                        method=request_params["method"],
                        endpoint=request_params["endpoint"],
                        params=request_params["params"],
                        data=request_params["data"],
                        json_data=request_params["json_data"],
                        files=request_params["files"],
                        headers=request_params["headers"],
                        timeout=request_params["timeout"],
                        retry_count=request_params["retry_count"],
                        retry_delay=request_params["retry_delay"],
                        **request_params["kwargs"]
                    )
                    
                    # 調用回調函數
                    callback = request_params["callback"]
                    if callback and callable(callback):
                        callback(result)
                    
                    # 添加結果
                    results.append({
                        "request_id": request_params["request_id"],
                        "success": True,
                        "result": result
                    })
                
                except APIError as e:
                    # 添加錯誤結果
                    results.append({
                        "request_id": request_params["request_id"],
                        "success": False,
                        "error": str(e)
                    })
                
                # 標記任務完成
                self.request_queue.task_done()
            
            except queue.Empty:
                break
        
        return results
    
    def start_webhook_server(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        webhook_path: str = "/webhook",
        secret: Optional[str] = None
    ) -> None:
        """
        啟動 Webhook 服務器
        
        Args:
            host: 主機地址
            port: 端口
            webhook_path: Webhook 路徑
            secret: Webhook 密鑰
        """
        if not WEBHOOK_AVAILABLE:
            raise APIError("Webhook 功能不可用，請安裝 webhook 庫")
        
        try:
            # 創建 Webhook 服務器
            server = WebhookServer(host=host, port=port)
            
            # 添加 Webhook 處理器
            @server.route(webhook_path, methods=["POST"])
            def handle_webhook():
                # 獲取請求數據
                data = request.get_json()
                
                # 驗證簽名（如果提供了密鑰）
                if secret:
                    signature = request.headers.get("X-Webhook-Signature")
                    if not signature or not self._verify_signature(data, secret, signature):
                        return jsonify({"error": "無效的簽名"}), 403
                
                # 處理 Webhook 數據
                self._process_webhook_data(data)
                
                return jsonify({"status": "success"})
            
            # 啟動服務器
            server.start()
            self.logger.info(f"Webhook 服務器已啟動: http://{host}:{port}{webhook_path}")
        
        except Exception as e:
            error_msg = f"啟動 Webhook 服務器失敗: {str(e)}"
            self.logger.error(error_msg)
            raise APIError(error_msg)
    
    def _verify_signature(self, data: Dict[str, Any], secret: str, signature: str) -> bool:
        """
        驗證 Webhook 簽名
        
        Args:
            data: 請求數據
            secret: 密鑰
            signature: 簽名
            
        Returns:
            簽名是否有效
        """
        try:
            # 計算簽名
            data_str = json.dumps(data, sort_keys=True)
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                data_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # 比較簽名
            return hmac.compare_digest(expected_signature, signature)
        
        except Exception as e:
            self.logger.error(f"驗證簽名失敗: {str(e)}")
            return False
    
    def _process_webhook_data(self, data: Dict[str, Any]) -> None:
        """
        處理 Webhook 數據
        
        Args:
            data: Webhook 數據
        """
        # 記錄 Webhook 數據
        self.logger.info(f"收到 Webhook 數據: {json.dumps(data)}")
        
        # 這裡可以添加自定義的 Webhook 處理邏輯
        # 例如，根據數據類型調用不同的處理函數
        
        # 更新統計信息
        self.request_count += 1
        self.success_count += 1
    
    def trigger_automation(
        self,
        platform: str,
        workflow_id: str,
        data: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        觸發流程自動化平台的工作流
        
        Args:
            platform: 平台名稱（n8n、make.com 等）
            workflow_id: 工作流 ID
            data: 觸發數據
            **kwargs: 其他參數
            
        Returns:
            觸發結果
        """
        try:
            if platform.lower() == "n8n":
                return self._trigger_n8n(workflow_id, data, **kwargs)
            
            elif platform.lower() == "make":
                return self._trigger_make(workflow_id, data, **kwargs)
            
            elif platform.lower() == "zapier":
                return self._trigger_zapier(workflow_id, data, **kwargs)
            
            elif platform.lower() == "ifttt":
                return self._trigger_ifttt(workflow_id, data, **kwargs)
            
            else:
                error_msg = f"不支持的流程自動化平台: {platform}"
                self.logger.error(error_msg)
                raise APIError(error_msg)
        
        except Exception as e:
            error_msg = f"觸發流程自動化失敗: {str(e)}"
            self.logger.error(error_msg)
            raise APIError(error_msg)
    
    def _trigger_n8n(self, workflow_id: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        觸發 n8n 工作流
        
        Args:
            workflow_id: 工作流 ID
            data: 觸發數據
            **kwargs: 其他參數
            
        Returns:
            觸發結果
        """
        # 檢查 n8n 配置
        if "n8n" not in self.api_configs:
            error_msg = "未找到 n8n 配置"
            self.logger.error(error_msg)
            raise APIError(error_msg)
        
        # 獲取 n8n 配置
        config = self.api_configs["n8n"]
        
        # 構建 Webhook URL
        webhook_url = f"{config.url}/webhook/{workflow_id}"
        
        # 發送請求
        return self.call_api(
            api_name="n8n",
            method="POST",
            endpoint=f"webhook/{workflow_id}",
            json_data=data,
            **kwargs
        )
    
    def _trigger_make(self, workflow_id: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        觸發 make.com 工作流
        
        Args:
            workflow_id: 工作流 ID
            data: 觸發數據
            **kwargs: 其他參數
            
        Returns:
            觸發結果
        """
        # 檢查 make.com 配置
        if "make" not in self.api_configs:
            error_msg = "未找到 make.com 配置"
            self.logger.error(error_msg)
            raise APIError(error_msg)
        
        # 獲取 make.com 配置
        config = self.api_configs["make"]
        
        # 構建 Webhook URL
        webhook_url = f"{config.url}/webhook/{workflow_id}"
        
        # 發送請求
        return self.call_api(
            api_name="make",
            method="POST",
            endpoint=f"webhook/{workflow_id}",
            json_data=data,
            **kwargs
        )
    
    def _trigger_zapier(self, workflow_id: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        觸發 Zapier 工作流
        
        Args:
            workflow_id: 工作流 ID
            data: 觸發數據
            **kwargs: 其他參數
            
        Returns:
            觸發結果
        """
        # 檢查 Zapier 配置
        if "zapier" not in self.api_configs:
            error_msg = "未找到 Zapier 配置"
            self.logger.error(error_msg)
            raise APIError(error_msg)
        
        # 獲取 Zapier 配置
        config = self.api_configs["zapier"]
        
        # 構建 Webhook URL
        webhook_url = f"{config.url}/webhook/{workflow_id}"
        
        # 發送請求
        return self.call_api(
            api_name="zapier",
            method="POST",
            endpoint=f"webhook/{workflow_id}",
            json_data=data,
            **kwargs
        )
    
    def _trigger_ifttt(self, workflow_id: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        觸發 IFTTT 工作流
        
        Args:
            workflow_id: 工作流 ID
            data: 觸發數據
            **kwargs: 其他參數
            
        Returns:
            觸發結果
        """
        # 檢查 IFTTT 配置
        if "ifttt" not in self.api_configs:
            error_msg = "未找到 IFTTT 配置"
            self.logger.error(error_msg)
            raise APIError(error_msg)
        
        # 獲取 IFTTT 配置
        config = self.api_configs["ifttt"]
        
        # 構建 Webhook URL
        webhook_url = f"{config.url}/trigger/{workflow_id}/with/key/{config.auth_params.get('key', '')}"
        
        # 發送請求
        return self.call_api(
            api_name="ifttt",
            method="POST",
            endpoint=f"trigger/{workflow_id}/with/key/{config.auth_params.get('key', '')}",
            json_data=data,
            **kwargs
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        獲取 API 統計數據
        
        Returns:
            包含 API 統計的字典
        """
        return {
            "request_count": self.request_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "average_response_time": self.total_response_time / self.request_count if self.request_count > 0 else 0,
            "registered_apis": list(self.api_configs.keys())
        }
    
    def reset_statistics(self) -> None:
        """重置統計計數"""
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_response_time = 0


# 便捷函數
def call_api(
    api_name: str,
    method: str = "GET",
    endpoint: str = "",
    **kwargs
) -> Dict[str, Any]:
    """
    快速調用 API 的便捷函數
    
    Args:
        api_name: API 名稱
        method: HTTP 方法
        endpoint: API 端點
        **kwargs: 其他參數
        
    Returns:
        API 響應
    """
    handler = APIHandler()
    return handler.call_api(api_name, method, endpoint, **kwargs)


def trigger_automation(
    platform: str,
    workflow_id: str,
    data: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    快速觸發流程自動化的便捷函數
    
    Args:
        platform: 平台名稱
        workflow_id: 工作流 ID
        data: 觸發數據
        **kwargs: 其他參數
        
    Returns:
        觸發結果
    """
    handler = APIHandler()
    return handler.trigger_automation(platform, workflow_id, data, **kwargs)


def create_notion_page(self, database_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    在 Notion 數據庫中創建新頁面
    
    Args:
        database_id: 數據庫 ID
        properties: 頁面屬性
        
    Returns:
        Dict[str, Any]: 創建的頁面信息
    """
    endpoint = "/pages"
    data = {
        "parent": {"database_id": database_id},
        "properties": properties
    }
    return self.call_api("notion", endpoint, method="POST", data=data)
    
def query_notion_database(self, database_id: str, filter_params: Optional[Dict[str, Any]] = None,
                        page_size: int = 100) -> Dict[str, Any]:
    """
    查詢 Notion 數據庫
    
    Args:
        database_id: 數據庫 ID
        filter_params: 過濾參數
        page_size: 每頁結果數量
        
    Returns:
        Dict[str, Any]: 查詢結果
    """
    endpoint = f"/databases/{database_id}/query"
    data = {
        "page_size": page_size
    }
    if filter_params:
        data["filter"] = filter_params
        
    return self.call_api("notion", endpoint, method="POST", data=data)
    
def update_notion_page(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新 Notion 頁面
    
    Args:
        page_id: 頁面 ID
        properties: 更新的屬性
        
    Returns:
        Dict[str, Any]: 更新後的頁面信息
    """
    endpoint = f"/pages/{page_id}"
    data = {"properties": properties}
    return self.call_api("notion", endpoint, method="PATCH", data=data)
    
def append_notion_block(self, block_id: str, children: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    向 Notion 區塊添加子區塊
    
    Args:
        block_id: 區塊 ID
        children: 子區塊列表
        
    Returns:
        Dict[str, Any]: 操作結果
    """
    endpoint = f"/blocks/{block_id}/children"
    data = {"children": children}
    return self.call_api("notion", endpoint, method="PATCH", data=data)
    
def search_notion(self, query: str, filter_params: Optional[Dict[str, Any]] = None,
                 sort_params: Optional[Dict[str, Any]] = None,
                 page_size: int = 100) -> Dict[str, Any]:
    """
    搜索 Notion 內容
    
    Args:
        query: 搜索關鍵詞
        filter_params: 過濾參數
        sort_params: 排序參數
        page_size: 每頁結果數量
        
    Returns:
        Dict[str, Any]: 搜索結果
    """
    endpoint = "/search"
    data = {
        "query": query,
        "page_size": page_size
    }
    if filter_params:
        data["filter"] = filter_params
    if sort_params:
        data["sort"] = sort_params
        
    return self.call_api("notion", endpoint, method="POST", data=data) 
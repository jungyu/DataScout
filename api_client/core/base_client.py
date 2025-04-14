#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基礎客戶端類
提供所有 API 客戶端的基礎功能
"""

import json
import logging
import requests
from typing import Dict, Any, Optional, Union
from api_client.core.config import APIConfig
from api_client.core.exceptions import (
    APIError,
    AuthenticationError,
    RequestError,
    ConfigurationError
)

class BaseClient:
    """基礎客戶端類"""
    
    def __init__(self, config: Union[Dict[str, Any], APIConfig]):
        """初始化基礎客戶端
        
        Args:
            config: 配置對象，可以是字典或配置類實例
        """
        if isinstance(config, dict):
            self.config = config
        else:
            self.config = config.to_dict()
        
        self.logger = logging.getLogger(__name__)
    
    def _make_request(self, method: str, url: str, **kwargs) -> Dict:
        """發送 HTTP 請求
        
        Args:
            method: 請求方法
            url: 請求 URL
            **kwargs: 請求參數
            
        Returns:
            Dict: 響應結果
            
        Raises:
            APIError: API 錯誤
            AuthenticationError: 認證錯誤
            RequestError: 請求錯誤
        """
        try:
            response = requests.request(method, url, **kwargs)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 403:
                raise AuthenticationError("Insufficient permissions")
            elif response.status_code == 404:
                raise RequestError("Resource not found")
            else:
                raise APIError(f"API error: {response.text}")
        except requests.exceptions.RequestException as e:
            raise RequestError(f"Request failed: {str(e)}")
    
    def _validate_config(self) -> bool:
        """驗證配置
        
        Returns:
            bool: 配置是否有效
            
        Raises:
            ConfigurationError: 配置錯誤
        """
        if not isinstance(self.config, dict):
            raise ConfigurationError("Config must be a dictionary")
        return True 
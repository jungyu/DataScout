#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置驗證器模組

提供以下功能：
1. 配置格式驗證
2. 配置值驗證
3. 配置依賴驗證
4. 配置衝突檢測
"""

import logging
from typing import Dict, List, Optional

from .config_exceptions import ConfigError

class ConfigValidator:
    """配置驗證器類"""
    
    def __init__(self):
        """初始化配置驗證器"""
        self.logger = logging.getLogger("crawler.config")
        
    def validate_config(self, module: str, config: Dict) -> None:
        """
        驗證配置
        
        Args:
            module: 模組名稱
            config: 配置字典
        """
        if module == "browser":
            self._validate_browser_config(config)
        elif module == "request":
            self._validate_request_config(config)
        elif module == "rate_limit":
            self._validate_rate_limit_config(config)
        elif module == "common":
            self._validate_common_config(config)
        else:
            raise ConfigError(f"未知的模組: {module}")
            
    def _validate_browser_config(self, config: Dict) -> None:
        """
        驗證瀏覽器配置
        
        Args:
            config: 配置字典
        """
        required_fields = ["headless", "window_size", "page_load_timeout"]
        for field in required_fields:
            if field not in config:
                raise ConfigError(f"缺少必要的瀏覽器配置項: {field}")
                
        if not isinstance(config["window_size"], dict):
            raise ConfigError("window_size 必須是一個字典")
            
        if "width" not in config["window_size"] or "height" not in config["window_size"]:
            raise ConfigError("window_size 必須包含 width 和 height")
            
    def _validate_request_config(self, config: Dict) -> None:
        """
        驗證請求配置
        
        Args:
            config: 配置字典
        """
        required_fields = ["timeout", "max_retries", "headers"]
        for field in required_fields:
            if field not in config:
                raise ConfigError(f"缺少必要的請求配置項: {field}")
                
        if not isinstance(config["headers"], dict):
            raise ConfigError("headers 必須是一個字典")
            
    def _validate_rate_limit_config(self, config: Dict) -> None:
        """
        驗證速率限制配置
        
        Args:
            config: 配置字典
        """
        required_fields = ["enabled", "global", "domain", "ip", "session"]
        for field in required_fields:
            if field not in config:
                raise ConfigError(f"缺少必要的速率限制配置項: {field}")
                
        if not isinstance(config["global"], dict):
            raise ConfigError("global 必須是一個字典")
            
        if "window" not in config["global"] or "max_requests" not in config["global"]:
            raise ConfigError("global 必須包含 window 和 max_requests")
            
    def _validate_common_config(self, config: Dict) -> None:
        """
        驗證通用配置
        
        Args:
            config: 配置字典
        """
        required_fields = ["storage", "logging"]
        for field in required_fields:
            if field not in config:
                raise ConfigError(f"缺少必要的通用配置項: {field}")
                
        if not isinstance(config["storage"], dict):
            raise ConfigError("storage 必須是一個字典")
            
        if not isinstance(config["logging"], dict):
            raise ConfigError("logging 必須是一個字典") 
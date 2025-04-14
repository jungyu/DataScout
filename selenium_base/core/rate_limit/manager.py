#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
速率限制管理模組

提供以下功能：
1. 全局速率限制
2. 域名速率限制
3. IP 速率限制
4. 會話速率限制
5. 延遲控制
6. 限流策略
7. 熔斷器
"""

import os
import json
import time
import random
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from collections import defaultdict

from .exceptions import (
    RateLimitError,
    RateLimitExceededError,
    RateLimitConfigError,
    RateLimitStateError,
    RateLimitTimeoutError,
    RateLimitInvalidConfigError
)

class RateLimitManager:
    """速率限制管理器類"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化速率限制管理器
        
        Args:
            config_path: 配置文件路徑，默認為模組目錄下的 configs/rate_limits.json
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__),
            "configs",
            "rate_limits.json"
        )
        self.config = self._load_config()
        self.logger = logging.getLogger("crawler.rate_limit")
        
        # 初始化狀態
        self._init_state()
        
    def _load_config(self) -> Dict:
        """
        加載配置
        
        Returns:
            配置字典
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise RateLimitConfigError(f"加載配置失敗: {str(e)}")
            
    def _init_state(self) -> None:
        """初始化狀態"""
        # 請求計數器
        self.request_counts = {
            "global": defaultdict(int),
            "domain": defaultdict(lambda: defaultdict(int)),
            "ip": defaultdict(int),
            "session": defaultdict(int)
        }
        
        # 時間窗口
        self.time_windows = {
            "second": time.time(),
            "minute": time.time(),
            "hour": time.time(),
            "day": time.time()
        }
        
        # IP 封禁列表
        self.ip_bans = {}
        
        # 會話狀態
        self.sessions = {}
        
        # 熔斷器狀態
        self.circuit_breaker_state = {
            "status": "closed",
            "failure_count": 0,
            "last_failure": None,
            "last_success": None
        }
        
        # 監控指標
        self.metrics = {
            "requests": 0,
            "blocks": 0,
            "errors": 0,
            "last_reset": time.time()
        }
        
    def validate_config(self) -> None:
        """驗證配置是否有效"""
        required_fields = ["global", "domain", "ip", "session", "delay", "circuit_breaker"]
        for field in required_fields:
            if field not in self.config:
                raise RateLimitInvalidConfigError(f"缺少必要的配置項: {field}")
                
    def reload_config(self) -> None:
        """重新加載配置"""
        self.config = self._load_config()
        self.validate_config()
        
    def check_rate_limit(self, domain: str, ip: str, session_id: str) -> bool:
        """
        檢查速率限制
        
        Args:
            domain: 域名
            ip: IP 地址
            session_id: 會話 ID
            
        Returns:
            是否允許請求
        """
        try:
            # 檢查全局限制
            if not self._check_global_limit():
                self.metrics["blocks"] += 1
                return False
                
            # 檢查域名限制
            if not self._check_domain_limit(domain):
                self.metrics["blocks"] += 1
                return False
                
            # 檢查 IP 限制
            if not self._check_ip_limit(ip):
                self.metrics["blocks"] += 1
                return False
                
            # 檢查會話限制
            if not self._check_session_limit(session_id):
                self.metrics["blocks"] += 1
                return False
                
            # 更新計數器
            self._update_counters(domain, ip, session_id)
            self.metrics["requests"] += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"檢查速率限制失敗: {str(e)}")
            self.metrics["errors"] += 1
            return False
            
    def get_metrics(self) -> Dict:
        """
        獲取指標
        
        Returns:
            指標字典
        """
        return {
            "global": {
                "requests": self.metrics["requests"],
                "blocks": self.metrics["blocks"],
                "errors": self.metrics["errors"],
                "error_rate": self.metrics["errors"] / self.metrics["requests"] if self.metrics["requests"] > 0 else 0
            },
            "domains": {
                domain: {
                    "requests": sum(counts.values()),
                    "blocks": self.domain_blocks.get(domain, 0),
                    "error_rate": self.domain_errors.get(domain, 0) / sum(counts.values()) if sum(counts.values()) > 0 else 0
                }
                for domain, counts in self.request_counts["domain"].items()
            },
            "ips": dict(self.request_counts["ip"]),
            "sessions": len(self.sessions),
            "banned_ips": len(self.ip_bans),
            "circuit_breaker": self.circuit_breaker_state
        }
        
    def reset_metrics(self) -> None:
        """重置監控指標"""
        self.metrics = {
            "requests": 0,
            "blocks": 0,
            "errors": 0,
            "last_reset": time.time()
        }
        self.domain_blocks = defaultdict(int)
        self.domain_errors = defaultdict(int) 
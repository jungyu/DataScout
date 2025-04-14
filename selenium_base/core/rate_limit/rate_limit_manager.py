#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
速率限制管理器模組

提供以下功能：
1. 全局速率限制
2. 域名速率限制
3. IP 速率限制
4. 會話速率限制
5. 延遲控制
6. 限流策略
7. 熔斷器
8. 代理輪換
9. 用戶代理輪換
10. Cookie 管理
11. 錯誤處理
12. 監控
"""

import json
import os
import time
import random
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

from ..base_manager import BaseManager
from .rate_limit_exceptions import (
    RateLimitError,
    RateLimitExceededError,
    RateLimitConfigError,
    RateLimitStateError
)

class RateLimitManager(BaseManager):
    """速率限制管理器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化速率限制管理器
        
        Args:
            config_path: 配置文件路徑
        """
        super().__init__()
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__),
            "configs",
            "rate_limits.json"
        )
        self.config = self._load_config()
        self.state = {
            "global": {},
            "domain": {},
            "ip": {},
            "session": {},
            "circuit_breaker": {}
        }
        self.metrics = {
            "requests": 0,
            "blocks": 0,
            "errors": 0,
            "last_reset": time.time()
        }
    
    def _load_config(self) -> Dict:
        """
        加載配置文件
        
        Returns:
            Dict: 配置數據
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise RateLimitConfigError(f"加載配置文件失敗: {str(e)}")
    
    def _save_state(self) -> None:
        """保存狀態"""
        try:
            state_path = os.path.join(
                os.path.dirname(self.config_path),
                "rate_limit_state.json"
            )
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=4)
        except Exception as e:
            self.logger.error(f"保存狀態失敗: {str(e)}")
    
    def _load_state(self) -> None:
        """加載狀態"""
        try:
            state_path = os.path.join(
                os.path.dirname(self.config_path),
                "rate_limit_state.json"
            )
            if os.path.exists(state_path):
                with open(state_path, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
        except Exception as e:
            self.logger.error(f"加載狀態失敗: {str(e)}")
    
    def check_global_limit(self) -> bool:
        """
        檢查全局限制
        
        Returns:
            bool: 是否允許請求
        """
        now = time.time()
        window = self.config["global"]["window"]
        max_requests = self.config["global"]["max_requests"]
        
        # 清理過期數據
        self.state["global"] = {
            k: v for k, v in self.state["global"].items()
            if now - k < window
        }
        
        # 檢查限制
        if len(self.state["global"]) >= max_requests:
            return False
        
        # 更新狀態
        self.state["global"][now] = True
        self._save_state()
        return True
    
    def check_domain_limit(self, domain: str) -> bool:
        """
        檢查域名限制
        
        Args:
            domain: 域名
            
        Returns:
            bool: 是否允許請求
        """
        now = time.time()
        window = self.config["domain"]["window"]
        max_requests = self.config["domain"]["max_requests"]
        
        if domain not in self.state["domain"]:
            self.state["domain"][domain] = {}
        
        # 清理過期數據
        self.state["domain"][domain] = {
            k: v for k, v in self.state["domain"][domain].items()
            if now - k < window
        }
        
        # 檢查限制
        if len(self.state["domain"][domain]) >= max_requests:
            return False
        
        # 更新狀態
        self.state["domain"][domain][now] = True
        self._save_state()
        return True
    
    def check_ip_limit(self, ip: str) -> bool:
        """
        檢查 IP 限制
        
        Args:
            ip: IP 地址
            
        Returns:
            bool: 是否允許請求
        """
        now = time.time()
        window = self.config["ip"]["window"]
        max_requests = self.config["ip"]["max_requests"]
        
        if ip not in self.state["ip"]:
            self.state["ip"][ip] = {}
        
        # 清理過期數據
        self.state["ip"][ip] = {
            k: v for k, v in self.state["ip"][ip].items()
            if now - k < window
        }
        
        # 檢查限制
        if len(self.state["ip"][ip]) >= max_requests:
            return False
        
        # 更新狀態
        self.state["ip"][ip][now] = True
        self._save_state()
        return True
    
    def check_session_limit(self, session_id: str) -> bool:
        """
        檢查會話限制
        
        Args:
            session_id: 會話 ID
            
        Returns:
            bool: 是否允許請求
        """
        now = time.time()
        window = self.config["session"]["window"]
        max_requests = self.config["session"]["max_requests"]
        
        if session_id not in self.state["session"]:
            self.state["session"][session_id] = {}
        
        # 清理過期數據
        self.state["session"][session_id] = {
            k: v for k, v in self.state["session"][session_id].items()
            if now - k < window
        }
        
        # 檢查限制
        if len(self.state["session"][session_id]) >= max_requests:
            return False
        
        # 更新狀態
        self.state["session"][session_id][now] = True
        self._save_state()
        return True
    
    def get_delay(self) -> float:
        """
        獲取延遲時間
        
        Returns:
            float: 延遲時間（秒）
        """
        min_delay = self.config["delay"]["min"]
        max_delay = self.config["delay"]["max"]
        return random.uniform(min_delay, max_delay)
    
    def check_circuit_breaker(self, key: str) -> bool:
        """
        檢查熔斷器
        
        Args:
            key: 熔斷器鍵值
            
        Returns:
            bool: 是否允許請求
        """
        if key not in self.state["circuit_breaker"]:
            self.state["circuit_breaker"][key] = {
                "failures": 0,
                "last_failure": 0,
                "state": "closed"
            }
        
        cb = self.state["circuit_breaker"][key]
        now = time.time()
        
        # 檢查是否需要重置
        if cb["state"] == "open":
            if now - cb["last_failure"] > self.config["circuit_breaker"]["reset_timeout"]:
                cb["state"] = "half-open"
                cb["failures"] = 0
        
        # 檢查是否熔斷
        if cb["state"] == "open":
            return False
        
        return True
    
    def record_failure(self, key: str) -> None:
        """
        記錄失敗
        
        Args:
            key: 熔斷器鍵值
        """
        if key not in self.state["circuit_breaker"]:
            self.state["circuit_breaker"][key] = {
                "failures": 0,
                "last_failure": 0,
                "state": "closed"
            }
        
        cb = self.state["circuit_breaker"][key]
        cb["failures"] += 1
        cb["last_failure"] = time.time()
        
        # 檢查是否需要熔斷
        if cb["failures"] >= self.config["circuit_breaker"]["threshold"]:
            cb["state"] = "open"
        
        self._save_state()
    
    def record_success(self, key: str) -> None:
        """
        記錄成功
        
        Args:
            key: 熔斷器鍵值
        """
        if key in self.state["circuit_breaker"]:
            cb = self.state["circuit_breaker"][key]
            if cb["state"] == "half-open":
                cb["state"] = "closed"
                cb["failures"] = 0
                self._save_state()
    
    def update_metrics(self, success: bool = True) -> None:
        """
        更新指標
        
        Args:
            success: 是否成功
        """
        self.metrics["requests"] += 1
        if not success:
            self.metrics["blocks"] += 1
        
        # 檢查是否需要重置
        now = time.time()
        if now - self.metrics["last_reset"] > self.config["monitoring"]["reset_interval"]:
            self.metrics = {
                "requests": 0,
                "blocks": 0,
                "errors": 0,
                "last_reset": now
            }
    
    def get_metrics(self) -> Dict:
        """
        獲取指標
        
        Returns:
            Dict: 指標數據
        """
        return self.metrics.copy()
    
    def reset(self) -> None:
        """重置所有狀態"""
        self.state = {
            "global": {},
            "domain": {},
            "ip": {},
            "session": {},
            "circuit_breaker": {}
        }
        self.metrics = {
            "requests": 0,
            "blocks": 0,
            "errors": 0,
            "last_reset": time.time()
        }
        self._save_state() 
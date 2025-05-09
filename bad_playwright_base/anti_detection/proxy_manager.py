#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
代理管理模組

此模組提供代理管理功能，包括：
1. 代理配置管理
2. 代理輪換
3. 代理驗證
4. 代理黑名單管理
"""

from typing import Dict, Any, List, Optional
import random
import time
from datetime import datetime, timedelta
from loguru import logger

from ..utils.exceptions import AntiDetectionException


class ProxyManager:
    """代理管理器"""
    
    def __init__(self):
        """初始化代理管理器"""
        # 代理配置
        self.proxy_config = {
            "enabled": False,
            "proxy_list": [],
            "current_proxy": None,
            "rotation_interval": 300,  # 5分鐘
            "last_rotation": None,
            "blacklist": [],
            "blacklist_duration": 3600,  # 1小時
            "max_retries": 3,
            "retry_delay": 5  # 5秒
        }
    
    def set_proxy_config(self, config: Dict[str, Any]) -> None:
        """
        設置代理配置
        
        Args:
            config: 代理配置字典
        """
        try:
            self.proxy_config.update(config)
            logger.info("已更新代理配置")
        except Exception as e:
            logger.error(f"更新代理配置時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"更新代理配置失敗: {str(e)}")
    
    def add_proxy(self, proxy: Dict[str, Any]) -> None:
        """
        添加代理
        
        Args:
            proxy: 代理配置字典
        """
        try:
            if proxy not in self.proxy_config["proxy_list"]:
                self.proxy_config["proxy_list"].append(proxy)
                logger.info(f"已添加代理: {proxy['host']}:{proxy['port']}")
        except Exception as e:
            logger.error(f"添加代理時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"添加代理失敗: {str(e)}")
    
    def remove_proxy(self, proxy: Dict[str, Any]) -> None:
        """
        移除代理
        
        Args:
            proxy: 代理配置字典
        """
        try:
            if proxy in self.proxy_config["proxy_list"]:
                self.proxy_config["proxy_list"].remove(proxy)
                logger.info(f"已移除代理: {proxy['host']}:{proxy['port']}")
        except Exception as e:
            logger.error(f"移除代理時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"移除代理失敗: {str(e)}")
    
    def get_random_proxy(self) -> Optional[Dict[str, Any]]:
        """
        獲取隨機代理
        
        Returns:
            Optional[Dict[str, Any]]: 代理配置字典
        """
        try:
            if not self.proxy_config["enabled"] or not self.proxy_config["proxy_list"]:
                return None
            
            available_proxies = [
                proxy for proxy in self.proxy_config["proxy_list"]
                if proxy not in self.proxy_config["blacklist"]
            ]
            
            if not available_proxies:
                return None
            
            return random.choice(available_proxies)
        except Exception as e:
            logger.error(f"獲取隨機代理時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"獲取隨機代理失敗: {str(e)}")
    
    def rotate_proxy(self) -> Optional[Dict[str, Any]]:
        """
        輪換代理
        
        Returns:
            Optional[Dict[str, Any]]: 新的代理配置字典
        """
        try:
            if not self.proxy_config["enabled"]:
                return None
            
            current_time = datetime.now()
            
            # 檢查是否需要輪換
            if (self.proxy_config["last_rotation"] and
                (current_time - self.proxy_config["last_rotation"]).total_seconds() < self.proxy_config["rotation_interval"]):
                return self.proxy_config["current_proxy"]
            
            # 獲取新代理
            new_proxy = self.get_random_proxy()
            if new_proxy:
                self.proxy_config["current_proxy"] = new_proxy
                self.proxy_config["last_rotation"] = current_time
                logger.info(f"已輪換到新代理: {new_proxy['host']}:{new_proxy['port']}")
            
            return new_proxy
        except Exception as e:
            logger.error(f"輪換代理時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"輪換代理失敗: {str(e)}")
    
    def add_to_blacklist(self, proxy: Dict[str, Any]) -> None:
        """
        將代理添加到黑名單
        
        Args:
            proxy: 代理配置字典
        """
        try:
            if proxy not in self.proxy_config["blacklist"]:
                self.proxy_config["blacklist"].append({
                    "proxy": proxy,
                    "added_at": datetime.now()
                })
                logger.info(f"已將代理添加到黑名單: {proxy['host']}:{proxy['port']}")
        except Exception as e:
            logger.error(f"添加代理到黑名單時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"添加代理到黑名單失敗: {str(e)}")
    
    def clean_blacklist(self) -> None:
        """清理過期的黑名單代理"""
        try:
            current_time = datetime.now()
            self.proxy_config["blacklist"] = [
                item for item in self.proxy_config["blacklist"]
                if (current_time - item["added_at"]).total_seconds() < self.proxy_config["blacklist_duration"]
            ]
            logger.info("已清理過期的黑名單代理")
        except Exception as e:
            logger.error(f"清理黑名單時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"清理黑名單失敗: {str(e)}")
    
    def apply_proxy(self, page) -> None:
        """
        應用代理到 Playwright 頁面
        
        Args:
            page: Playwright 頁面對象
        """
        try:
            if not self.proxy_config["enabled"]:
                return
            
            proxy = self.rotate_proxy()
            if not proxy:
                return
            
            page.route("**/*", lambda route: route.continue_(
                proxy={
                    "server": f"{proxy['protocol']}://{proxy['host']}:{proxy['port']}",
                    "username": proxy.get("username"),
                    "password": proxy.get("password")
                }
            ))
            
            logger.info(f"已應用代理: {proxy['host']}:{proxy['port']}")
        except Exception as e:
            logger.error(f"應用代理時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"應用代理失敗: {str(e)}") 
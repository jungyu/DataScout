#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用戶代理管理模組

此模組提供用戶代理管理功能，包括：
1. 用戶代理生成
2. 用戶代理驗證
3. 用戶代理輪換
4. 用戶代理黑名單管理
"""

from typing import Dict, Any, List, Optional
import random
import json
import os
from datetime import datetime
from loguru import logger

from ..utils.exceptions import AntiDetectionException


class UserAgentManager:
    """用戶代理管理器"""
    
    def __init__(self):
        """初始化用戶代理管理器"""
        # 用戶代理配置
        self.ua_config = {
            "enabled": True,
            "rotation_interval": 3600,  # 1小時
            "last_rotation": None,
            "blacklist": [],
            "blacklist_duration": 86400,  # 24小時
            "current_ua": None
        }
        
        # 用戶代理模板
        self.ua_templates = {
            "chrome": {
                "windows": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
                "macos": "Mozilla/5.0 (Macintosh; Intel Mac OS X {os_version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
                "linux": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
            },
            "firefox": {
                "windows": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{version}) Gecko/20100101 Firefox/{version}",
                "macos": "Mozilla/5.0 (Macintosh; Intel Mac OS X {os_version}; rv:{version}) Gecko/20100101 Firefox/{version}",
                "linux": "Mozilla/5.0 (X11; Linux i686; rv:{version}) Gecko/20100101 Firefox/{version}"
            },
            "safari": {
                "windows": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15",
                "macos": "Mozilla/5.0 (Macintosh; Intel Mac OS X {os_version}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15"
            }
        }
        
        # 版本範圍
        self.version_ranges = {
            "chrome": {
                "min": "110.0.0.0",
                "max": "120.0.0.0"
            },
            "firefox": {
                "min": "110.0",
                "max": "120.0"
            },
            "safari": {
                "min": "16.0",
                "max": "17.0"
            }
        }
        
        # 操作系統版本
        self.os_versions = {
            "windows": ["10.0", "11.0"],
            "macos": ["10_15", "11_0", "12_0", "13_0"],
            "linux": ["x86_64", "i686"]
        }
    
    def set_ua_config(self, config: Dict[str, Any]) -> None:
        """
        設置用戶代理配置
        
        Args:
            config: 用戶代理配置字典
        """
        try:
            self.ua_config.update(config)
            logger.info("已更新用戶代理配置")
        except Exception as e:
            logger.error(f"更新用戶代理配置時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"更新用戶代理配置失敗: {str(e)}")
    
    def generate_random_ua(self) -> str:
        """
        生成隨機用戶代理
        
        Returns:
            str: 用戶代理字符串
        """
        try:
            # 隨機選擇瀏覽器
            browser = random.choice(list(self.ua_templates.keys()))
            
            # 隨機選擇操作系統
            os_type = random.choice(list(self.ua_templates[browser].keys()))
            
            # 生成版本號
            version_range = self.version_ranges[browser]
            version = f"{random.uniform(float(version_range['min'].split('.')[0]), float(version_range['max'].split('.')[0])):.1f}"
            
            # 選擇操作系統版本
            os_version = random.choice(self.os_versions[os_type])
            
            # 生成用戶代理
            ua = self.ua_templates[browser][os_type].format(
                version=version,
                os_version=os_version
            )
            
            return ua
        except Exception as e:
            logger.error(f"生成隨機用戶代理時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"生成隨機用戶代理失敗: {str(e)}")
    
    def get_consistent_ua(self) -> str:
        """
        獲取一致的用戶代理（每次調用返回相同的用戶代理）
        
        Returns:
            str: 用戶代理字符串
        """
        try:
            if self.ua_config["current_ua"]:
                return self.ua_config["current_ua"]
            
            # 生成新的用戶代理
            ua = self.generate_random_ua()
            self.ua_config["current_ua"] = ua
            
            return ua
        except Exception as e:
            logger.error(f"獲取一致用戶代理時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"獲取一致用戶代理失敗: {str(e)}")
    
    def rotate_ua(self) -> str:
        """
        輪換用戶代理
        
        Returns:
            str: 新的用戶代理字符串
        """
        try:
            if not self.ua_config["enabled"]:
                return None
            
            current_time = datetime.now()
            
            # 檢查是否需要輪換
            if (self.ua_config["last_rotation"] and
                (current_time - self.ua_config["last_rotation"]).total_seconds() < self.ua_config["rotation_interval"]):
                return self.ua_config["current_ua"]
            
            # 生成新用戶代理
            new_ua = self.generate_random_ua()
            while new_ua in self.ua_config["blacklist"]:
                new_ua = self.generate_random_ua()
            
            self.ua_config["current_ua"] = new_ua
            self.ua_config["last_rotation"] = current_time
            
            logger.info(f"已輪換到新用戶代理: {new_ua}")
            return new_ua
        except Exception as e:
            logger.error(f"輪換用戶代理時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"輪換用戶代理失敗: {str(e)}")
    
    def add_to_blacklist(self, ua: str) -> None:
        """
        將用戶代理添加到黑名單
        
        Args:
            ua: 用戶代理字符串
        """
        try:
            if ua not in self.ua_config["blacklist"]:
                self.ua_config["blacklist"].append({
                    "ua": ua,
                    "added_at": datetime.now()
                })
                logger.info(f"已將用戶代理添加到黑名單: {ua}")
        except Exception as e:
            logger.error(f"添加用戶代理到黑名單時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"添加用戶代理到黑名單失敗: {str(e)}")
    
    def clean_blacklist(self) -> None:
        """清理過期的黑名單用戶代理"""
        try:
            current_time = datetime.now()
            self.ua_config["blacklist"] = [
                item for item in self.ua_config["blacklist"]
                if (current_time - item["added_at"]).total_seconds() < self.ua_config["blacklist_duration"]
            ]
            logger.info("已清理過期的黑名單用戶代理")
        except Exception as e:
            logger.error(f"清理黑名單時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"清理黑名單失敗: {str(e)}")
    
    async def apply_ua(self, page) -> None:
        """
        應用用戶代理到 Playwright 頁面
        
        Args:
            page: Playwright 頁面對象
        """
        try:
            if not self.ua_config["enabled"]:
                return
            
            ua = self.rotate_ua()
            if not ua:
                return
            
            # 設置用戶代理
            await page.set_extra_http_headers({
                "User-Agent": ua
            })
            
            # 注入用戶代理到頁面
            await page.add_init_script(f"""
                Object.defineProperty(navigator, 'userAgent', {{
                    get: function() {{
                        return '{ua}';
                    }}
                }});
            """)
            
            logger.info(f"已應用用戶代理: {ua}")
        except Exception as e:
            logger.error(f"應用用戶代理時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"應用用戶代理失敗: {str(e)}") 
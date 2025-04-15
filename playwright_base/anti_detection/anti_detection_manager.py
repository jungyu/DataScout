#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
反檢測管理模組

此模組整合所有反檢測功能，包括：
1. 指紋偽裝
2. 代理管理
3. 人類行為模擬
4. 用戶代理管理
"""

from typing import Dict, Any, Optional
from loguru import logger

from ..utils.exceptions import AntiDetectionException
from .fingerprint import FingerprintManager
from .proxy_manager import ProxyManager
from .behavior_manager import BehaviorManager
from .user_agent_manager import UserAgentManager


class AntiDetectionManager:
    """反檢測管理器"""
    
    def __init__(self):
        """初始化反檢測管理器"""
        # 初始化各個管理器
        self.fingerprint_manager = FingerprintManager()
        self.proxy_manager = ProxyManager()
        self.behavior_manager = BehaviorManager()
        self.ua_manager = UserAgentManager()
        
        # 反檢測配置
        self.config = {
            "enabled": True,
            "fingerprint": {
                "enabled": True,
                "webgl": True,
                "canvas": True,
                "audio": True,
                "font": True,
                "screen": True,
                "platform": True
            },
            "proxy": {
                "enabled": True,
                "rotation_interval": 300,  # 5分鐘
                "blacklist_duration": 3600  # 1小時
            },
            "behavior": {
                "enabled": True,
                "mouse_speed": {
                    "min": 0.5,
                    "max": 2.0
                },
                "typing_speed": {
                    "min": 100,
                    "max": 300
                },
                "scroll_speed": {
                    "min": 100,
                    "max": 500
                },
                "click_delay": {
                    "min": 0.1,
                    "max": 0.5
                },
                "form_delay": {
                    "min": 0.5,
                    "max": 2.0
                }
            },
            "user_agent": {
                "enabled": True,
                "rotation_interval": 3600,  # 1小時
                "blacklist_duration": 86400  # 24小時
            }
        }
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """
        設置反檢測配置
        
        Args:
            config: 反檢測配置字典
        """
        try:
            self.config.update(config)
            
            # 更新各個管理器的配置
            if "fingerprint" in config:
                self.fingerprint_manager.set_fingerprint_config(config["fingerprint"])
            
            if "proxy" in config:
                self.proxy_manager.set_proxy_config(config["proxy"])
            
            if "behavior" in config:
                self.behavior_manager.set_behavior_config(config["behavior"])
            
            if "user_agent" in config:
                self.ua_manager.set_ua_config(config["user_agent"])
            
            logger.info("已更新反檢測配置")
        except Exception as e:
            logger.error(f"更新反檢測配置時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"更新反檢測配置失敗: {str(e)}")
    
    async def apply_anti_detection(self, page) -> None:
        """
        應用所有反檢測功能到 Playwright 頁面
        
        Args:
            page: Playwright 頁面對象
        """
        try:
            if not self.config["enabled"]:
                return
            
            # 應用指紋偽裝
            if self.config["fingerprint"]["enabled"]:
                await self.fingerprint_manager.apply_fingerprint(page)
            
            # 應用代理
            if self.config["proxy"]["enabled"]:
                await self.proxy_manager.apply_proxy(page)
            
            # 應用用戶代理
            if self.config["user_agent"]["enabled"]:
                await self.ua_manager.apply_ua(page)
            
            logger.info("已應用所有反檢測功能")
        except Exception as e:
            logger.error(f"應用反檢測功能時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"應用反檢測功能失敗: {str(e)}")
    
    async def move_mouse(self, page, target: tuple) -> None:
        """
        模擬人類鼠標移動
        
        Args:
            page: Playwright 頁面對象
            target: 目標坐標
        """
        try:
            if not self.config["enabled"] or not self.config["behavior"]["enabled"]:
                await page.mouse.move(target[0], target[1])
                return
            
            await self.behavior_manager.move_mouse(page, target)
        except Exception as e:
            logger.error(f"移動鼠標時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"移動鼠標失敗: {str(e)}")
    
    async def type_text(self, page, selector: str, text: str) -> None:
        """
        模擬人類鍵盤輸入
        
        Args:
            page: Playwright 頁面對象
            selector: 元素選擇器
            text: 要輸入的文本
        """
        try:
            if not self.config["enabled"] or not self.config["behavior"]["enabled"]:
                await page.type(selector, text)
                return
            
            await self.behavior_manager.type_text(page, selector, text)
        except Exception as e:
            logger.error(f"輸入文本時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"輸入文本失敗: {str(e)}")
    
    async def scroll_page(self, page, distance: Optional[int] = None) -> None:
        """
        模擬人類頁面滾動
        
        Args:
            page: Playwright 頁面對象
            distance: 滾動距離（像素）
        """
        try:
            if not self.config["enabled"] or not self.config["behavior"]["enabled"]:
                if distance:
                    await page.evaluate(f"window.scrollBy(0, {distance})")
                else:
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                return
            
            await self.behavior_manager.scroll_page(page, distance)
        except Exception as e:
            logger.error(f"滾動頁面時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"滾動頁面失敗: {str(e)}")
    
    async def click_element(self, page, selector: str) -> None:
        """
        模擬人類點擊行為
        
        Args:
            page: Playwright 頁面對象
            selector: 元素選擇器
        """
        try:
            if not self.config["enabled"] or not self.config["behavior"]["enabled"]:
                await page.click(selector)
                return
            
            await self.behavior_manager.click_element(page, selector)
        except Exception as e:
            logger.error(f"點擊元素時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"點擊元素失敗: {str(e)}")
    
    async def fill_form(self, page, form_data: Dict[str, str]) -> None:
        """
        模擬人類表單填寫行為
        
        Args:
            page: Playwright 頁面對象
            form_data: 表單數據字典
        """
        try:
            if not self.config["enabled"] or not self.config["behavior"]["enabled"]:
                for selector, value in form_data.items():
                    await page.fill(selector, value)
                return
            
            await self.behavior_manager.fill_form(page, form_data)
        except Exception as e:
            logger.error(f"填寫表單時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"填寫表單失敗: {str(e)}")
    
    def add_proxy(self, proxy: Dict[str, Any]) -> None:
        """
        添加代理
        
        Args:
            proxy: 代理配置字典
        """
        try:
            if not self.config["enabled"] or not self.config["proxy"]["enabled"]:
                return
            
            self.proxy_manager.add_proxy(proxy)
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
            if not self.config["enabled"] or not self.config["proxy"]["enabled"]:
                return
            
            self.proxy_manager.remove_proxy(proxy)
        except Exception as e:
            logger.error(f"移除代理時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"移除代理失敗: {str(e)}")
    
    def add_to_blacklist(self, item: Dict[str, Any], blacklist_type: str) -> None:
        """
        將項目添加到黑名單
        
        Args:
            item: 要添加到黑名單的項目
            blacklist_type: 黑名單類型（proxy/ua）
        """
        try:
            if not self.config["enabled"]:
                return
            
            if blacklist_type == "proxy":
                if self.config["proxy"]["enabled"]:
                    self.proxy_manager.add_to_blacklist(item)
            elif blacklist_type == "ua":
                if self.config["user_agent"]["enabled"]:
                    self.ua_manager.add_to_blacklist(item)
            else:
                raise AntiDetectionException(f"不支持的黑名單類型: {blacklist_type}")
        except Exception as e:
            logger.error(f"添加項目到黑名單時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"添加項目到黑名單失敗: {str(e)}")
    
    def clean_blacklists(self) -> None:
        """清理所有黑名單"""
        try:
            if not self.config["enabled"]:
                return
            
            if self.config["proxy"]["enabled"]:
                self.proxy_manager.clean_blacklist()
            
            if self.config["user_agent"]["enabled"]:
                self.ua_manager.clean_blacklist()
            
            logger.info("已清理所有黑名單")
        except Exception as e:
            logger.error(f"清理黑名單時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"清理黑名單失敗: {str(e)}") 
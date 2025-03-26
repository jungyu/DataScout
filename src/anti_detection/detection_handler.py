#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
from typing import Dict

from selenium import webdriver
from selenium.webdriver.common.by import By


class DetectionHandler:
    """處理被反爬機制識別的情況"""
    
    def __init__(self, manager, config: Dict, logger=None, max_retries: int = 3):
        """
        初始化偵測處理器
        
        Args:
            manager: AntiDetectionManager實例
            config: 配置
            logger: 日誌記錄器
            max_retries: 最大重試次數
        """
        self.manager = manager
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.max_retries = max_retries
        self.detection_count = 0
    
    def detect(self, driver: webdriver.Remote) -> bool:
        """
        檢測是否被反爬機制識別
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否被識別
        """
        # 檢測點一：檢查頁面是否包含常見的反爬文本
        anti_crawl_texts = [
            "驗證碼", "captcha", "禁止訪問", "access denied",
            "異常訪問", "unusual traffic", "人機驗證", "robot",
            "拒絕訪問", "請求頻率過高", "請稍後再試", "temporarily blocked",
            "安全檢查", "security check", "滑動驗證", "點擊驗證"
        ]
        
        try:
            page_source = driver.page_source.lower()
            
            for text in anti_crawl_texts:
                if text.lower() in page_source:
                    self.logger.warning(f"檢測到反爬機制: 頁面包含 '{text}'")
                    return True
            
            # 檢測點二：檢查是否有驗證碼元素
            captcha_selectors = [
                "//iframe[contains(@src, 'captcha')]",
                "//iframe[contains(@src, 'recaptcha')]",
                "//div[contains(@class, 'captcha')]",
                "//div[contains(@class, 'recaptcha')]",
                "//div[contains(@id, 'captcha')]",
                "//div[contains(@id, 'recaptcha')]",
                "//img[contains(@src, 'captcha')]",
                "//input[contains(@placeholder, 'captcha')]",
                "//input[contains(@id, 'captcha')]",
                "//div[contains(@class, 'slider')]//div[contains(@class, 'handle')]"
            ]
            
            for selector in captcha_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    self.logger.warning(f"檢測到反爬機制: 存在驗證碼元素 '{selector}'")
                    return True
            
            # 檢測點三：檢查頁面標題或URL是否包含錯誤提示
            error_indicators = [
                "error", "denied", "blocked", "unauthorized",
                "forbidden", "429", "too many requests", "retry"
            ]
            
            page_title = driver.title.lower()
            current_url = driver.current_url.lower()
            
            for indicator in error_indicators:
                if indicator in page_title or indicator in current_url:
                    self.logger.warning(f"檢測到反爬機制: 頁面標題或URL包含 '{indicator}'")
                    return True
            
            # 檢測點四：使用JavaScript檢測是否存在WebDriver
            webdriver_detection_script = """
            return (navigator.webdriver !== undefined && navigator.webdriver === true) ||
                   (window.callPhantom !== undefined) ||
                   (window._phantom !== undefined) ||
                   (window.__nightmare !== undefined) ||
                   (window.Buffer !== undefined);
            """
            
            try:
                is_detected = driver.execute_script(webdriver_detection_script)
                if is_detected:
                    self.logger.warning("檢測到反爬機制: JavaScript檢測到WebDriver特徵")
                    return True
            except Exception as js_error:
                self.logger.debug(f"執行JavaScript檢測失敗: {str(js_error)}")
            
            # 未檢測到反爬機制
            return False
        
        except Exception as e:
            self.logger.error(f"檢測反爬機制失敗: {str(e)}")
            # 為了安全起見，假設可能被檢測到
            return True
    
    def handle(self, driver: webdriver.Remote) -> bool:
        """
        處理被反爬機制識別的情況
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否成功處理
        """
        # 增加檢測計數
        self.detection_count += 1
        
        # 檢查是否超過最大重試次數
        if self.detection_count > self.max_retries:
            self.logger.error(f"已達到最大重試次數 {self.max_retries}，放棄處理")
            return False
        
        self.logger.info(f"嘗試處理反爬機制檢測，第 {self.detection_count}/{self.max_retries} 次")
        
        # 策略一：更換代理
        if self.config.get("change_proxy_on_detection", True) and self.manager.proxies:
            try:
                proxy = self.manager._get_next_proxy()
                if proxy:
                    self.logger.info(f"更換代理: {proxy}")
                    # 由於WebDriver不支持運行時更換代理，需要重新創建
                    return False  # 返回False以觸發上層重新創建WebDriver
            except Exception as e:
                self.logger.error(f"更換代理失敗: {str(e)}")
        
        # 策略二：更換用戶代理
        if self.config.get("change_user_agent_on_detection", True) and self.manager.user_agents:
            try:
                user_agent = self.manager._get_random_user_agent()
                if user_agent:
                    self.logger.info(f"更換用戶代理: {user_agent}")
                    self.manager.webdriver_manager.change_user_agent(user_agent)
            except Exception as e:
                self.logger.error(f"更換用戶代理失敗: {str(e)}")
        
        # 策略三：清除Cookie
        if self.config.get("clear_cookies_on_detection", True):
            try:
                self.logger.info("清除Cookie")
                driver.delete_all_cookies()
            except Exception as e:
                self.logger.error(f"清除Cookie失敗: {str(e)}")
        
        # 策略四：重新應用隱身腳本
        try:
            self.logger.info("重新應用隱身腳本")
            self.manager._apply_stealth_scripts(driver)
        except Exception as e:
            self.logger.error(f"重新應用隱身腳本失敗: {str(e)}")
        
        # 策略五：模擬人類行為
        try:
            self.logger.info("模擬人類行為")
            self.manager.behavior_simulator.simulate_human_scroll(driver)
            self.manager.behavior_simulator.random_delay("between_actions")
            self.manager.behavior_simulator.simulate_human_mouse_movement(driver)
        except Exception as e:
            self.logger.error(f"模擬人類行為失敗: {str(e)}")
        
        # 策略六：等待較長時間
        cooldown_time = self.config.get("detection_cooldown", 30)
        self.logger.info(f"等待冷卻時間: {cooldown_time} 秒")
        time.sleep(cooldown_time)
        
        # 刷新頁面
        try:
            self.logger.info("刷新頁面")
            driver.refresh()
            
            # 等待頁面加載
            self.manager.behavior_simulator.random_delay("page_load")
        except Exception as e:
            self.logger.error(f"刷新頁面失敗: {str(e)}")
        
        # 再次檢測是否被識別
        if not self.detect(driver):
            self.logger.info("成功處理反爬機制")
            self.detection_count = 0  # 重置計數器
            return True
        else:
            self.logger.warning("處理反爬機制失敗，仍被識別")
            return False
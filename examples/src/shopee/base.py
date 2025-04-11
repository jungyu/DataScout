#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
蝦皮爬蟲基礎類
提供基本的爬蟲功能和配置管理
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.anti_detection.base_scraper import BaseScraper
from src.anti_detection.anti_detection_manager import AntiDetectionManager
from src.anti_detection.utils.human_behavior import HumanBehaviorSimulator
from src.anti_detection.cookie_manager import CookieManager
from src.anti_detection.browser_fingerprint import BrowserFingerprint
from src.core.utils.url_utils import URLUtils
from src.core.utils.data_processor import DataProcessor
from src.core.utils import BrowserUtils, ConfigUtils, PathUtils, Logger
from src.core.utils.security_utils import SecurityUtils
from src.persistence.handlers import StorageHandler, LocalStorageHandler, MongoDBHandler, NotionHandler
from src.captcha.types import CaptchaType
from src.captcha import CaptchaManager
from src.persistence.handlers import CaptchaHandler, CaptchaDetectionResult

class ScraperError(Exception):
    """爬蟲錯誤"""
    pass

class ConfigError(Exception):
    """配置錯誤"""
    pass

class ShopeeCrawler:
    """蝦皮爬蟲基礎類"""
    
    def __init__(self):
        """初始化爬蟲"""
        # 初始化工具類
        self.config_utils = ConfigUtils()
        self.path_utils = PathUtils()
        self.logger = Logger()
        self.security_utils = SecurityUtils()
        
        # 加載配置
        self.crawler_config = self.config_utils.get_config('crawler')
        self.storage_config = self.config_utils.get_config('storage')
        self.security_config = self.config_utils.get_config('security')
        self.logging_config = self.config_utils.get_config('logging')
        
        # 初始化存儲處理器
        self.storage = self._init_storage()
        
        # 初始化瀏覽器
        self.driver = None
        self.setup_browser()
        
    def _init_storage(self) -> StorageHandler:
        """
        初始化存儲處理器
        
        Returns:
            StorageHandler: 存儲處理器實例
        """
        storage_type = self.storage_config.get('default_storage', 'local')
        storage_config = self.storage_config['storage_types'][storage_type]
        
        if storage_type == 'local':
            return LocalStorageHandler(
                base_path=storage_config['base_path'],
                file_format=storage_config['file_format']
            )
        elif storage_type == 'mongodb':
            return MongoDBHandler(
                host=storage_config['host'],
                port=storage_config['port'],
                database=storage_config['database'],
                username=storage_config['username'],
                password=storage_config['password']
            )
        elif storage_type == 'notion':
            return NotionHandler(
                token=storage_config['token'],
                database_id=storage_config['database_id']
            )
        else:
            raise ValueError(f"不支持的存儲類型: {storage_type}")
            
    def setup_browser(self):
        """設置瀏覽器"""
        browser_config = self.crawler_config.get('browser', {})
        
        options = Options()
        if browser_config.get('headless', True):
            options.add_argument('--headless')
            
        options.add_argument(f'--window-size={browser_config["window_size"]["width"]},{browser_config["window_size"]["height"]}')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(browser_config.get('page_load_timeout', 30))
        self.driver.implicitly_wait(browser_config.get('implicit_wait', 10))
        
    def setup_proxy(self):
        """設置代理"""
        proxy_config = self.security_config.get('proxy', {})
        if not proxy_config.get('enabled', False):
            return
            
        proxy_type = proxy_config['type']
        proxy_host = proxy_config['host']
        proxy_port = proxy_config['port']
        
        if proxy_config.get('username') and proxy_config.get('password'):
            auth = f"{proxy_config['username']}:{proxy_config['password']}@"
        else:
            auth = ""
            
        proxy_url = f"{proxy_type}://{auth}{proxy_host}:{proxy_port}"
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": self._get_random_user_agent()})
        self.driver.execute_cdp_cmd('Network.enable', {})
        self.driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {'headers': self._get_headers()})
        
    def _get_random_user_agent(self) -> str:
        """
        獲取隨機用戶代理
        
        Returns:
            str: 用戶代理字符串
        """
        headers_config = self.security_config.get('headers', {})
        if not headers_config.get('rotate_user_agent', True):
            return self.driver.execute_script("return navigator.userAgent")
            
        # TODO: 實現用戶代理輪換邏輯
        return self.driver.execute_script("return navigator.userAgent")
        
    def _get_headers(self) -> Dict[str, str]:
        """
        獲取請求頭
        
        Returns:
            Dict[str, str]: 請求頭字典
        """
        return self.security_config.get('headers', {}).get('custom_headers', {})
        
    def wait_for_element(self, by: By, value: str, timeout: Optional[int] = None) -> Any:
        """
        等待元素出現
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間
            
        Returns:
            Any: 元素對象
        """
        if timeout is None:
            timeout = self.crawler_config.get('browser', {}).get('timeout', 30)
            
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        
    def scroll_to_bottom(self):
        """滾動到頁面底部"""
        scroll_config = self.crawler_config.get('shopee', {}).get('scroll', {})
        pause_time = scroll_config.get('pause_time', 2)
        max_attempts = scroll_config.get('max_attempts', 10)
        
        for _ in range(max_attempts):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            
    def close(self):
        """關閉瀏覽器"""
        if self.driver:
            self.driver.quit()
            self.driver = None

class ShopeeBaseScraper(BaseScraper):
    """蝦皮爬蟲基礎類"""
    
    def __init__(self, 
                 config_path: str,
                 data_dir: str = "./examples/data",
                 domain: str = "shopee.tw",
                 debug_mode: bool = False):
        """
        初始化爬蟲
        
        Args:
            config_path: 配置文件路徑
            data_dir: 數據目錄
            domain: 目標網站域名
            debug_mode: 是否啟用調試模式
        """
        super().__init__(config_path, data_dir, domain, debug_mode)
        
        # 初始化各個管理器
        self._init_managers()
        
        # 載入蝦皮特定配置
        self._load_shopee_config()
        
    def _init_managers(self) -> None:
        """初始化各個管理器"""
        try:
            # 初始化反爬蟲管理器
            self.anti_detection = AntiDetectionManager(self.config)
            
            # 初始化人類行為模擬器
            self.human_behavior = self.anti_detection.human_behavior
            
            # 初始化 Cookie 管理器
            self.cookie_manager = self.anti_detection.cookie_manager
            
            # 初始化瀏覽器指紋管理器
            self.browser_fingerprint = self.anti_detection.browser_fingerprint
            
            # 初始化驗證碼管理器
            self.captcha_manager = CaptchaManager()
            
            # 初始化驗證碼處理器
            self.captcha_handler = CaptchaHandler(self.config)
            self.captcha_handler.set_captcha_manager(self.captcha_manager)
            
        except Exception as e:
            raise ScraperError(f"初始化管理器失敗: {str(e)}")
            
    def _load_shopee_config(self) -> None:
        """載入蝦皮特定配置"""
        try:
            # 載入驗證碼相關配置
            self.captcha_config = self.config.get("captcha", {})
            self.captcha_selectors = self.captcha_config.get("selectors", {})
            
            # 載入人類行為模擬配置
            self.human_behavior_config = self.config.get("human_behavior", {})
            self.scroll_config = self.human_behavior_config.get("scroll", {})
            self.click_config = self.human_behavior_config.get("click", {})
            self.type_config = self.human_behavior_config.get("type", {})
            
        except Exception as e:
            raise ConfigError(f"載入蝦皮配置失敗: {str(e)}")
            
    def _check_for_captcha(self) -> bool:
        """
        檢查是否存在驗證碼
        
        Returns:
            是否存在驗證碼
        """
        try:
            for captcha_type, selector in self.captcha_selectors.items():
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        self.logger.info(f"檢測到驗證碼: {captcha_type}")
                        return True
                except NoSuchElementException:
                    continue
            return False
        except Exception as e:
            self.logger.error(f"檢查驗證碼失敗: {str(e)}")
            return False
            
    def _handle_captcha(self) -> bool:
        """
        處理驗證碼
        
        Returns:
            是否處理成功
        """
        try:
            # 截圖保存
            self.take_screenshot("captcha")
            
            # 等待用戶手動處理驗證碼
            self.logger.info("請手動處理驗證碼，等待 30 秒...")
            time.sleep(30)
            
            # 檢查驗證碼是否已解決
            if not self._check_for_captcha():
                self.logger.info("驗證碼已解決")
                return True
                
            self.logger.error("驗證碼未解決")
            return False
            
        except Exception as e:
            self.logger.error(f"處理驗證碼失敗: {str(e)}")
            return False
            
    def save_search_results(self, results: List[Dict[str, Any]], keyword: str) -> bool:
        """
        保存搜索結果
        
        Args:
            results: 搜索結果列表
            keyword: 搜索關鍵詞
            
        Returns:
            是否保存成功
        """
        return self.save_results(results, f"search_results_{keyword}")
        
    def _enhance_browser_stealth(self) -> None:
        """增強反爬蟲能力"""
        try:
            # 應用反爬蟲措施
            self.anti_detection.apply_anti_detection_measures(self.driver)
        except Exception as e:
            self.logger.error(f"增強反爬蟲能力失敗: {str(e)}")
        
    def _simulate_human_browsing(self) -> None:
        """模擬人類瀏覽行為"""
        try:
            # 模擬人類瀏覽行為
            self.anti_detection.simulate_human_browsing(self.driver)
        except Exception as e:
            self.logger.error(f"模擬人類瀏覽行為失敗: {str(e)}")
            
    def start(self) -> bool:
        """
        啟動爬蟲
        
        Returns:
            是否啟動成功
        """
        if not super().start():
            return False
            
        # 增強反爬蟲能力
        self._enhance_browser_stealth()
        
        # 模擬人類瀏覽行為
        self._simulate_human_browsing()
        
        return True
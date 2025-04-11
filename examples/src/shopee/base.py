#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
蝦皮爬蟲基礎類

提供基本的爬蟲功能和配置管理，包括：
- 瀏覽器管理
- 配置管理
- 存儲管理
- 反檢測管理
- 驗證碼處理
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

# 核心模組
from src.core import (
    ConfigLoader,
    CrawlerEngine,
    CrawlerStateManager,
    CrawlerException,
    ConfigError,
    BrowserError,
    NavigationError,
    ExtractionError,
    StateError
)

# 核心工具
from src.core.utils import (
    ConfigUtils,
    Logger,
    PathUtils,
    BrowserUtils,
    URLUtils,
    DataProcessor,
    SecurityUtils
)

# 反檢測
from src.anti_detection import (
    BaseScraper,
    AntiDetectionManager,
    HumanBehaviorSimulator,
    CookieManager,
    BrowserFingerprint
)

# 存儲
from src.persistence import (
    Storage,
    LocalStorageHandler,
    MongoDBHandler,
    NotionHandler
)

# 驗證碼
from src.captcha import (
    CaptchaType,
    CaptchaManager,
    CaptchaHandler,
    CaptchaDetectionResult
)

class ScraperError(CrawlerException):
    """爬蟲錯誤"""
    pass

class ShopeeCrawler:
    """蝦皮爬蟲基礎類"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化爬蟲
        
        Args:
            config_path: 配置文件路徑，如果為 None 則使用默認配置
        """
        # 初始化核心引擎
        self.engine = CrawlerEngine()
        self.state_manager = CrawlerStateManager()
        
        # 初始化工具類
        self.config_utils = ConfigUtils()
        self.path_utils = PathUtils()
        self.logger = Logger()
        self.browser_utils = BrowserUtils()
        self.url_utils = URLUtils()
        self.data_processor = DataProcessor()
        self.security_utils = SecurityUtils()
        
        # 加載配置
        self.config = self._load_config(config_path)
        self.crawler_config = self.config.get('crawler', {})
        self.storage_config = self.config.get('storage', {})
        self.security_config = self.config.get('security', {})
        self.logging_config = self.config.get('logging', {})
        
        # 初始化存儲處理器
        self.storage = self._init_storage()
        
        # 初始化瀏覽器
        self.driver = None
        self.setup_browser()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """
        加載配置文件
        
        Args:
            config_path: 配置文件路徑
            
        Returns:
            Dict: 配置字典
        """
        try:
            if config_path:
                return self.config_utils.load_config(config_path)
            return self.config_utils.get_default_config()
        except Exception as e:
            raise ConfigError(f"加載配置失敗: {str(e)}")
        
    def _init_storage(self) -> Storage:
        """
        初始化存儲處理器
        
        Returns:
            Storage: 存儲處理器實例
        """
        try:
            storage_type = self.storage_config.get('default_storage', 'local')
            storage_config = self.storage_config.get('storage_types', {}).get(storage_type, {})
            
            if storage_type == 'local':
                return LocalStorageHandler(
                    base_path=storage_config.get('base_path', 'data'),
                    file_format=storage_config.get('file_format', 'json')
                )
            elif storage_type == 'mongodb':
                return MongoDBHandler(
                    host=storage_config.get('host', 'localhost'),
                    port=storage_config.get('port', 27017),
                    database=storage_config.get('database', 'crawler'),
                    username=storage_config.get('username'),
                    password=storage_config.get('password')
                )
            elif storage_type == 'notion':
                return NotionHandler(
                    token=storage_config.get('token'),
                    database_id=storage_config.get('database_id')
                )
            else:
                raise ValueError(f"不支持的存儲類型: {storage_type}")
        except Exception as e:
            raise ScraperError(f"初始化存儲失敗: {str(e)}")
            
    def setup_browser(self):
        """設置瀏覽器"""
        try:
            options = self.browser_utils.create_chrome_options(
                headless=self.crawler_config.get('headless', False),
                proxy=self.security_config.get('proxy'),
                user_agent=self.security_config.get('user_agent')
            )
            
            self.driver = self.browser_utils.create_driver(options)
            self.driver.set_window_size(
                self.crawler_config.get('window_width', 1920),
                self.crawler_config.get('window_height', 1080)
            )
        except Exception as e:
            raise BrowserError(f"設置瀏覽器失敗: {str(e)}")
        
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
        try:
            timeout = timeout or self.crawler_config.get('timeout', 10)
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except Exception as e:
            raise NavigationError(f"等待元素失敗: {str(e)}")
        
    def scroll_to_bottom(self):
        """滾動到頁面底部"""
        try:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(self.crawler_config.get('scroll_delay', 1))
        except Exception as e:
            raise NavigationError(f"滾動頁面失敗: {str(e)}")
        
    def close(self):
        """關閉瀏覽器"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except Exception as e:
                self.logger.error(f"關閉瀏覽器失敗: {str(e)}")

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
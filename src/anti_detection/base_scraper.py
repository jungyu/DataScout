#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基礎爬蟲類

提供爬蟲的基礎功能，包括：
- 瀏覽器管理
- 頁面導航
- 元素操作
- 數據提取
- 錯誤處理
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, List, Any, Union
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException,
    StaleElementReferenceException
)

from src.core.utils import (
    BrowserUtils,
    ConfigUtils,
    PathUtils,
    Logger,
    URLUtils,
    DataProcessor,
    setup_logger
)
from src.core.exceptions import CrawlerException, BrowserError, NavigationError
from src.core.webdriver_manager import WebDriverManager
from src.core.config_loader import ConfigLoader

class BaseScraper:
    """基礎爬蟲類"""
    
    def __init__(self, 
                 config_path: str,
                 data_dir: str = "./data",
                 domain: str = None,
                 debug_mode: bool = False):
        """
        初始化爬蟲
        
        Args:
            config_path: 配置文件路徑
            data_dir: 數據目錄
            domain: 目標網站域名
            debug_mode: 是否啟用調試模式
        """
        # 初始化路徑工具
        this_dir = os.path.dirname(os.path.abspath(__file__))
        self.path_utils = PathUtils()
        
        # 初始化日誌工具
        self.logger = setup_logger(
            name=self.__class__.__name__,
            level_name="INFO" if not debug_mode else "DEBUG",
            log_dir=os.path.join(data_dir, "logs"),
            log_file=f"{self.__class__.__name__.lower()}.log",
            console_output=True,
            file_output=True
        )
        
        # 設置基本屬性
        self.config_path = config_path
        self.data_dir = data_dir
        self.domain = domain
        self.debug_mode = debug_mode
        
        # 生成唯一標識符
        self.id = self._generate_id()
        
        # 初始化配置
        self._load_config()
        
        # 初始化 WebDriver 管理器
        browser_config = {
            "headless": self.config.get("crawler", {}).get("headless", False),
            "window_size": (
                self.config.get("crawler", {}).get("window_width", 1920),
                self.config.get("crawler", {}).get("window_height", 1080)
            ),
            "page_load_timeout": self.config.get("crawler", {}).get("timeout", 30),
            "proxy": self.config.get("security", {}).get("proxy"),
            "user_agent": self.config.get("security", {}).get("user_agent")
        }
        self.webdriver_manager = WebDriverManager(browser_config)
        
        # 初始化瀏覽器工具
        self.browser_utils = BrowserUtils()
        
        # 初始化 URL 工具
        self.url_utils = URLUtils()
        
        # 初始化數據處理器
        self.data_processor = DataProcessor()
        
        # 初始化 WebDriver
        self.driver = None
        
    def _generate_id(self) -> str:
        """生成唯一標識符"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.__class__.__name__}_{timestamp}"
        
    def _load_config(self) -> None:
        """載入配置"""
        try:
            # 載入配置
            config_loader = ConfigLoader(self.logger)
            self.config = config_loader.load_config(self.config_path)
            
            # 設置域名
            if not self.domain and "domain" in self.config:
                self.domain = self.config["domain"]
                
        except Exception as e:
            self.logger.error(f"載入配置失敗: {str(e)}")
            raise CrawlerException(f"載入配置失敗: {str(e)}")
            
    def start(self) -> bool:
        """
        啟動爬蟲
        
        Returns:
            是否啟動成功
        """
        try:
            # 創建 WebDriver
            self.driver = self.webdriver_manager.create_driver()
            
            # 設置瀏覽器工具
            self.browser_utils.set_driver(self.driver)
            
            # 設置窗口大小
            window_size = self.config.get("browser", {}).get("window_size", {})
            if window_size:
                width = window_size.get("width", 1920)
                height = window_size.get("height", 1080)
                self.driver.set_window_size(width, height)
                
            # 訪問目標網站
            if self.domain:
                self.driver.get(f"https://{self.domain}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"啟動爬蟲失敗: {str(e)}")
            return False
            
    def stop(self) -> None:
        """停止爬蟲"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception as e:
            self.logger.error(f"停止爬蟲失敗: {str(e)}")
            
    def wait_for_element(self, 
                         by: By, 
                         value: str, 
                         timeout: int = 10, 
                         clickable: bool = False) -> Any:
        """
        等待元素出現
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間
            clickable: 是否等待元素可點擊
            
        Returns:
            元素對象
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            if clickable:
                element = wait.until(EC.element_to_be_clickable((by, value)))
            else:
                element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            self.logger.warning(f"等待元素超時: {by}={value}")
            return None
        except Exception as e:
            self.logger.error(f"等待元素失敗: {str(e)}")
            return None
            
    def safe_click(self, element: Any, retries: int = 3) -> bool:
        """
        安全點擊元素
        
        Args:
            element: 要點擊的元素
            retries: 重試次數
            
        Returns:
            是否點擊成功
        """
        for i in range(retries):
            try:
                # 等待元素可點擊
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(element)
                )
                
                # 點擊元素
                element.click()
                return True
                
            except ElementClickInterceptedException:
                self.logger.warning(f"點擊被攔截，重試 {i+1}/{retries}")
                time.sleep(1)
                
            except StaleElementReferenceException:
                self.logger.warning(f"元素已過期，重試 {i+1}/{retries}")
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"點擊元素失敗: {str(e)}")
                return False
                
        return False
        
    def take_screenshot(self, name: str) -> bool:
        """
        截取屏幕截圖
        
        Args:
            name: 截圖名稱
            
        Returns:
            是否截圖成功
        """
        try:
            if not self.driver:
                self.logger.error("WebDriver 未初始化")
                return False
                
            # 生成截圖路徑
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_dir = self.path_utils.get_screenshot_dir(self.data_dir)
            self.path_utils.ensure_dir(screenshot_dir)
            
            filename = f"{name}_{timestamp}.png"
            filepath = self.path_utils.join_path(screenshot_dir, filename)
            
            # 截圖
            self.driver.save_screenshot(filepath)
            self.logger.info(f"截圖已保存到: {filepath}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"截圖失敗: {str(e)}")
            return False
            
    def save_results(self, results: List[Dict[str, Any]], name: str) -> bool:
        """
        保存結果
        
        Args:
            results: 結果列表
            name: 結果名稱
            
        Returns:
            是否保存成功
        """
        try:
            if not results:
                self.logger.warning("沒有結果可保存")
                return False
                
            # 生成文件路徑
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = self.path_utils.get_output_dir(self.data_dir)
            self.path_utils.ensure_dir(output_dir)
            
            filename = f"{name}_{timestamp}.json"
            filepath = self.path_utils.join_path(output_dir, filename)
            
            # 保存到文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"結果已保存到: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存結果失敗: {str(e)}")
            return False
            
    def run(self, *args, **kwargs) -> bool:
        """
        運行爬蟲
        
        Args:
            *args: 位置參數
            **kwargs: 關鍵字參數
            
        Returns:
            是否運行成功
        """
        try:
            # 啟動爬蟲
            if not self.start():
                return False
                
            # 執行爬蟲邏輯
            result = self._run(*args, **kwargs)
            
            # 停止爬蟲
            self.stop()
            
            return result
            
        except Exception as e:
            self.logger.error(f"運行爬蟲失敗: {str(e)}")
            self.stop()
            return False
            
    def _run(self, *args, **kwargs) -> bool:
        """
        執行爬蟲邏輯
        
        Args:
            *args: 位置參數
            **kwargs: 關鍵字參數
            
        Returns:
            是否執行成功
        """
        # 子類需要實現此方法
        raise NotImplementedError("子類必須實現 _run 方法") 
import os
import time
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from src.core.exceptions import CrawlerException, BrowserException, RequestException
from src.core.config import BaseConfig, BrowserConfig, RequestConfig
from src.core.logger import setup_logger
from src.anti_detection import AntiDetectionManager
from src.captcha import CaptchaService

@dataclass
class CrawlerState:
    """爬蟲狀態數據類"""
    is_running: bool = False
    current_url: Optional[str] = None
    last_request_time: float = 0.0
    request_count: int = 0
    error_count: int = 0

class BaseCrawler:
    """基礎爬蟲類"""
    
    def __init__(
        self,
        config: BaseConfig,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化基礎爬蟲
        
        Args:
            config: 爬蟲配置
            logger: 日誌記錄器
        """
        self.config = config
        self.logger = logger or setup_logger(__name__)
        self.state = CrawlerState()
        self.driver = None
        self.anti_detection = None
        self.captcha_service = None
        
    def initialize(self) -> None:
        """初始化爬蟲環境"""
        try:
            self._setup_browser()
            self._setup_anti_detection()
            self._setup_captcha()
            self.state.is_running = True
            self.logger.info("爬蟲初始化完成")
        except Exception as e:
            self.logger.error(f"爬蟲初始化失敗: {str(e)}")
            raise CrawlerException("爬蟲初始化失敗", details={"error": str(e)})
            
    def _setup_browser(self) -> None:
        """設置瀏覽器"""
        try:
            options = Options()
            if self.config.browser.headless:
                options.add_argument("--headless")
            
            options.add_argument(f"--window-size={self.config.browser.window_size[0]},{self.config.browser.window_size[1]}")
            
            if self.config.browser.proxy:
                options.add_argument(f"--proxy-server={self.config.browser.proxy}")
                
            if self.config.browser.user_agent:
                options.add_argument(f"--user-agent={self.config.browser.user_agent}")
                
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(self.config.browser.timeout)
            
        except Exception as e:
            raise BrowserException("瀏覽器設置失敗", details={"error": str(e)})
            
    def _setup_anti_detection(self) -> None:
        """設置反偵測"""
        try:
            self.anti_detection = AntiDetectionManager(
                driver=self.driver,
                config=self.config.anti_detection
            )
        except Exception as e:
            raise CrawlerException("反偵測設置失敗", details={"error": str(e)})
            
    def _setup_captcha(self) -> None:
        """設置驗證碼服務"""
        try:
            self.captcha_service = CaptchaService(
                driver=self.driver,
                config=self.config.captcha
            )
        except Exception as e:
            raise CrawlerException("驗證碼服務設置失敗", details={"error": str(e)})
            
    def navigate(self, url: str) -> None:
        """
        導航到指定URL
        
        Args:
            url: 目標URL
        """
        try:
            self.driver.get(url)
            self.state.current_url = url
            self.logger.info(f"成功導航到: {url}")
        except Exception as e:
            self.logger.error(f"導航失敗: {str(e)}")
            raise CrawlerException("導航失敗", details={"url": url, "error": str(e)})
            
    def wait_for_element(
        self,
        by: By,
        value: str,
        timeout: Optional[int] = None
    ) -> Any:
        """
        等待元素出現
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間（秒）
            
        Returns:
            找到的元素
        """
        try:
            timeout = timeout or self.config.browser.timeout
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.logger.error(f"等待元素超時: {value}")
            raise CrawlerException("等待元素超時", details={"element": value})
            
    def cleanup(self) -> None:
        """清理資源"""
        try:
            if self.driver:
                self.driver.quit()
            self.state.is_running = False
            self.logger.info("爬蟲資源清理完成")
        except Exception as e:
            self.logger.error(f"資源清理失敗: {str(e)}")
            
    def __enter__(self):
        """上下文管理器入口"""
        self.initialize()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup() 
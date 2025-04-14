"""
瀏覽器配置模組

提供瀏覽器配置和操作功能
"""

import os
from typing import Dict, List, Optional, Union
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium_base.core.exceptions import BrowserError
from selenium_base.core.utils import Utils

class Browser:
    """瀏覽器配置類別"""
    
    def __init__(self, config: Dict):
        """初始化瀏覽器配置類別
        
        Args:
            config: 瀏覽器配置
        """
        self.config = config
        self.driver = None
        self.options = None
        self._setup_browser()
    
    def _setup_browser(self) -> None:
        """設定瀏覽器"""
        try:
            browser_type = self.config.get('type', 'chrome').lower()
            
            if browser_type == 'chrome':
                self.options = ChromeOptions()
            elif browser_type == 'firefox':
                self.options = FirefoxOptions()
            elif browser_type == 'edge':
                self.options = EdgeOptions()
            elif browser_type == 'safari':
                self.options = SafariOptions()
            else:
                raise BrowserError(f'不支援的瀏覽器類型: {browser_type}')
            
            self._configure_options()
            
        except Exception as e:
            raise BrowserError(f'設定瀏覽器失敗: {e}')
    
    def _configure_options(self) -> None:
        """設定瀏覽器選項"""
        try:
            # 設定無頭模式
            if self.config.get('headless', False):
                self.options.add_argument('--headless')
            
            # 設定視窗大小
            window_size = self.config.get('window_size', {'width': 1920, 'height': 1080})
            self.options.add_argument(f'--window-size={window_size["width"]},{window_size["height"]}')
            
            # 設定代理
            proxy = self.config.get('proxy')
            if proxy:
                self.options.add_argument(f'--proxy-server={proxy}')
            
            # 設定使用者代理
            user_agent = self.config.get('user_agent')
            if user_agent:
                self.options.add_argument(f'--user-agent={user_agent}')
            
            # 設定語言
            language = self.config.get('language', 'zh-TW')
            self.options.add_argument(f'--lang={language}')
            
            # 設定時區
            timezone = self.config.get('timezone', 'Asia/Taipei')
            self.options.add_argument(f'--timezone={timezone}')
            
            # 設定地理位置
            geolocation = self.config.get('geolocation')
            if geolocation:
                self.options.add_argument(f'--geolocation={geolocation["latitude"]},{geolocation["longitude"]}')
            
            # 設定其他選項
            for option in self.config.get('options', []):
                self.options.add_argument(option)
            
        except Exception as e:
            raise BrowserError(f'設定瀏覽器選項失敗: {e}')
    
    def start(self) -> None:
        """啟動瀏覽器"""
        try:
            browser_type = self.config.get('type', 'chrome').lower()
            
            if browser_type == 'chrome':
                self.driver = webdriver.Chrome(options=self.options)
            elif browser_type == 'firefox':
                self.driver = webdriver.Firefox(options=self.options)
            elif browser_type == 'edge':
                self.driver = webdriver.Edge(options=self.options)
            elif browser_type == 'safari':
                self.driver = webdriver.Safari(options=self.options)
            
            # 設定頁面載入超時
            self.driver.set_page_load_timeout(self.config.get('page_load_timeout', 30))
            
            # 設定隱式等待
            self.driver.implicitly_wait(self.config.get('implicit_wait', 10))
            
        except Exception as e:
            raise BrowserError(f'啟動瀏覽器失敗: {e}')
    
    def stop(self) -> None:
        """停止瀏覽器"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception as e:
            raise BrowserError(f'停止瀏覽器失敗: {e}')
    
    def get_driver(self) -> webdriver.Remote:
        """取得瀏覽器驅動程式
        
        Returns:
            瀏覽器驅動程式
        """
        if not self.driver:
            raise BrowserError('瀏覽器尚未啟動')
        return self.driver
    
    def add_extension(self, extension_path: str) -> None:
        """添加擴充功能
        
        Args:
            extension_path: 擴充功能路徑
        """
        try:
            if not os.path.exists(extension_path):
                raise BrowserError(f'擴充功能不存在: {extension_path}')
            
            self.options.add_extension(extension_path)
            
        except Exception as e:
            raise BrowserError(f'添加擴充功能失敗: {e}')
    
    def add_argument(self, argument: str) -> None:
        """添加瀏覽器參數
        
        Args:
            argument: 瀏覽器參數
        """
        try:
            self.options.add_argument(argument)
        except Exception as e:
            raise BrowserError(f'添加瀏覽器參數失敗: {e}')
    
    def add_experimental_option(self, name: str, value: Any) -> None:
        """添加實驗性選項
        
        Args:
            name: 選項名稱
            value: 選項值
        """
        try:
            self.options.add_experimental_option(name, value)
        except Exception as e:
            raise BrowserError(f'添加實驗性選項失敗: {e}')
    
    def set_preference(self, name: str, value: Any) -> None:
        """設定偏好設定
        
        Args:
            name: 設定名稱
            value: 設定值
        """
        try:
            self.options.set_preference(name, value)
        except Exception as e:
            raise BrowserError(f'設定偏好設定失敗: {e}')
    
    def __enter__(self):
        """進入上下文管理器"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """離開上下文管理器"""
        self.stop() 
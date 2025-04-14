"""
瀏覽器配置類別

提供瀏覽器配置管理功能
"""

import os
from typing import Dict, List, Optional, Union, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium_base.utils.exceptions import BrowserError
from selenium_base.utils.logger import Logger

class BrowserProfile:
    """瀏覽器配置類別"""
    
    def __init__(self, config: Dict):
        """
        初始化瀏覽器配置
        
        Args:
            config: 配置字典，包含以下欄位：
                - type: 瀏覽器類型（chrome、firefox、edge、safari）
                - headless: 是否使用無頭模式
                - window_size: 視窗大小
                - proxy: 代理設定
                - user_agent: 使用者代理
                - language: 語言設定
                - timezone: 時區設定
                - geolocation: 地理位置設定
                - options: 其他選項
        """
        self.config = config
        self.logger = Logger('browser_profile')
        self.options = self._create_options()
    
    def _create_options(self) -> Union[ChromeOptions, FirefoxOptions, EdgeOptions, SafariOptions]:
        """
        建立瀏覽器選項
        
        Returns:
            Union[ChromeOptions, FirefoxOptions, EdgeOptions, SafariOptions]: 瀏覽器選項物件
            
        Raises:
            BrowserError: 不支援的瀏覽器類型
        """
        browser_type = self.config.get('type', 'chrome').lower()
        
        if browser_type == 'chrome':
            options = ChromeOptions()
        elif browser_type == 'firefox':
            options = FirefoxOptions()
        elif browser_type == 'edge':
            options = EdgeOptions()
        elif browser_type == 'safari':
            options = SafariOptions()
        else:
            raise BrowserError(f'不支援的瀏覽器類型: {browser_type}')
        
        # 設定無頭模式
        if self.config.get('headless', False):
            options.add_argument('--headless')
        
        # 設定視窗大小
        if 'window_size' in self.config:
            width = self.config['window_size'].get('width', 1920)
            height = self.config['window_size'].get('height', 1080)
            options.add_argument(f'--window-size={width},{height}')
        
        # 設定代理
        if 'proxy' in self.config:
            options.add_argument(f'--proxy-server={self.config["proxy"]}')
        
        # 設定使用者代理
        if 'user_agent' in self.config:
            options.add_argument(f'--user-agent={self.config["user_agent"]}')
        
        # 設定語言
        if 'language' in self.config:
            options.add_argument(f'--lang={self.config["language"]}')
        
        # 設定時區
        if 'timezone' in self.config:
            options.add_argument(f'--timezone={self.config["timezone"]}')
        
        # 設定地理位置
        if 'geolocation' in self.config:
            lat = self.config['geolocation'].get('latitude', 0)
            lng = self.config['geolocation'].get('longitude', 0)
            options.add_argument(f'--geolocation={lat},{lng}')
        
        # 設定其他選項
        if 'options' in self.config:
            for option in self.config['options']:
                options.add_argument(option)
        
        return options
    
    def add_extension(self, extension_path: str) -> None:
        """
        添加擴充功能
        
        Args:
            extension_path: 擴充功能路徑
            
        Raises:
            BrowserError: 擴充功能檔案不存在
        """
        if not os.path.exists(extension_path):
            raise BrowserError(f'擴充功能檔案不存在: {extension_path}')
        
        self.options.add_extension(extension_path)
    
    def add_argument(self, argument: str) -> None:
        """
        添加瀏覽器參數
        
        Args:
            argument: 瀏覽器參數
        """
        self.options.add_argument(argument)
    
    def add_experimental_option(self, name: str, value: Any) -> None:
        """
        添加實驗性選項
        
        Args:
            name: 選項名稱
            value: 選項值
        """
        self.options.add_experimental_option(name, value)
    
    def set_preference(self, name: str, value: Any) -> None:
        """
        設定偏好設定
        
        Args:
            name: 偏好設定名稱
            value: 偏好設定值
        """
        self.options.set_preference(name, value)
    
    def get_options(self) -> Union[ChromeOptions, FirefoxOptions, EdgeOptions, SafariOptions]:
        """
        取得瀏覽器選項
        
        Returns:
            Union[ChromeOptions, FirefoxOptions, EdgeOptions, SafariOptions]: 瀏覽器選項物件
        """
        return self.options 
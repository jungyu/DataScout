"""
瀏覽器驅動程式管理類別

提供瀏覽器驅動程式管理功能
"""

from typing import Dict, Optional, Union
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver
from selenium.webdriver.safari.webdriver import WebDriver as SafariDriver
from datascout_core.utils.exceptions import BrowserError
from datascout_core.utils.logger import Logger
from .profile import BrowserProfile

class BrowserDriver:
    """瀏覽器驅動程式管理類別"""
    
    def __init__(self, profile: BrowserProfile):
        """
        初始化瀏覽器驅動程式管理
        
        Args:
            profile: 瀏覽器配置物件
        """
        self.profile = profile
        self.logger = Logger('browser_driver')
        self.driver = None
    
    def start(self) -> Union[ChromeDriver, FirefoxDriver, EdgeDriver, SafariDriver]:
        """
        啟動瀏覽器
        
        Returns:
            Union[ChromeDriver, FirefoxDriver, EdgeDriver, SafariDriver]: 瀏覽器驅動程式物件
            
        Raises:
            BrowserError: 瀏覽器啟動失敗
        """
        try:
            browser_type = self.profile.config.get('type', 'chrome').lower()
            options = self.profile.get_options()
            
            if browser_type == 'chrome':
                self.driver = webdriver.Chrome(options=options)
            elif browser_type == 'firefox':
                self.driver = webdriver.Firefox(options=options)
            elif browser_type == 'edge':
                self.driver = webdriver.Edge(options=options)
            elif browser_type == 'safari':
                self.driver = webdriver.Safari(options=options)
            else:
                raise BrowserError(f'不支援的瀏覽器類型: {browser_type}')
            
            # 設定頁面載入超時
            if 'page_load_timeout' in self.profile.config:
                self.driver.set_page_load_timeout(self.profile.config['page_load_timeout'])
            
            # 設定隱式等待
            if 'implicit_wait' in self.profile.config:
                self.driver.implicitly_wait(self.profile.config['implicit_wait'])
            
            return self.driver
        except Exception as e:
            self.logger.error(f'瀏覽器啟動失敗: {str(e)}')
            raise BrowserError(f'瀏覽器啟動失敗: {str(e)}')
    
    def stop(self) -> None:
        """
        停止瀏覽器
        
        Raises:
            BrowserError: 瀏覽器未啟動
        """
        if self.driver is None:
            raise BrowserError('瀏覽器未啟動')
        
        try:
            self.driver.quit()
            self.driver = None
        except Exception as e:
            self.logger.error(f'瀏覽器停止失敗: {str(e)}')
            raise BrowserError(f'瀏覽器停止失敗: {str(e)}')
    
    def get_driver(self) -> Union[ChromeDriver, FirefoxDriver, EdgeDriver, SafariDriver]:
        """
        取得瀏覽器驅動程式
        
        Returns:
            Union[ChromeDriver, FirefoxDriver, EdgeDriver, SafariDriver]: 瀏覽器驅動程式物件
            
        Raises:
            BrowserError: 瀏覽器未啟動
        """
        if self.driver is None:
            raise BrowserError('瀏覽器未啟動')
        
        return self.driver
    
    def __enter__(self) -> Union[ChromeDriver, FirefoxDriver, EdgeDriver, SafariDriver]:
        """
        上下文管理器進入
        
        Returns:
            Union[ChromeDriver, FirefoxDriver, EdgeDriver, SafariDriver]: 瀏覽器驅動程式物件
        """
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        上下文管理器退出
        """
        self.stop() 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WebDriverManager 模組
實作瀏覽器實例管理和設定
"""

import os
import json
import time
import random
import logging
from typing import Dict, List, Optional, Any, Union, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By

from ..anti_detection.configs.anti_fingerprint_config import AntiFingerprintConfig
from ..anti_detection.stealth.stealth_manager import StealthManager

class WebDriverManager:
    """
    WebDriver管理器，負責創建、配置和管理WebDriver實例
    """
    
    def __init__(self, config: Union[Dict[str, Any], AntiFingerprintConfig], logger=None):
        """
        初始化WebDriver管理器
        
        Args:
            config: WebDriver配置或反指紋檢測配置
            logger: 日誌記錄器，如果為None則創建新的
        """
        self.logger = logger or logging.getLogger(__name__)
        self.config = config
        self.driver = None
        self.stealth_manager = StealthManager(logger=self.logger)
        
        # 判斷配置類型
        if isinstance(config, AntiFingerprintConfig):
            self._init_from_anti_fingerprint_config(config)
        else:
            self._init_from_dict_config(config)
    
    def _init_from_anti_fingerprint_config(self, config: AntiFingerprintConfig):
        """從反指紋檢測配置初始化"""
        self.browser_type = "chrome"
        self.user_agent = config.user_agent
        self.proxy = config.proxy
        self.headless = config.headless
        self.window_size = {"width": config.window_size[0], "height": config.window_size[1]}
        self.enable_stealth = True
        self.timeout = config.timeout
        self.disable_images = False
        self.disable_javascript = False
        self.disable_cookies = False
        self.user_data_dir = None
        self.extensions = []
        self.arguments = []
        self.experimental_options = {}
        self.driver_path = None
        self.binary_path = None
        self.randomize_user_agent = False
        self.user_agents = []
    
    def _init_from_dict_config(self, config: Dict[str, Any]):
        """從字典配置初始化"""
        self.browser_type = config.get("browser_type", "chrome")
        self.user_agent = config.get("user_agent", None)
        self.proxy = config.get("proxy", None)
        self.headless = config.get("headless", False)
        self.disable_images = config.get("disable_images", False)
        self.disable_javascript = config.get("disable_javascript", False)
        self.disable_cookies = config.get("disable_cookies", False)
        self.window_size = config.get("window_size", {"width": 1920, "height": 1080})
        self.user_data_dir = config.get("user_data_dir", None)
        self.extensions = config.get("extensions", [])
        self.arguments = config.get("arguments", [])
        self.experimental_options = config.get("experimental_options", {})
        self.driver_path = config.get("driver_path", None)
        self.binary_path = config.get("binary_path", None)
        self.enable_stealth = config.get("enable_stealth", True)
        self.randomize_user_agent = config.get("randomize_user_agent", False)
        self.user_agents = config.get("user_agents", self._get_default_user_agents())
        self.timeout = config.get("timeout", 30)
    
    def _get_default_user_agents(self) -> List[str]:
        """獲取默認的用戶代理列表"""
        return [
            # Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            # Firefox
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            # Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
            # Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        ]
    
    def _get_random_user_agent(self) -> str:
        """獲取隨機用戶代理"""
        if self.user_agents:
            return random.choice(self.user_agents)
        return None
    
    def _configure_chrome_options(self) -> ChromeOptions:
        """配置Chrome選項"""
        options = ChromeOptions()
        
        # 設置用戶代理
        user_agent = self.user_agent
        if self.randomize_user_agent:
            user_agent = self._get_random_user_agent()
        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")
        
        # 設置代理
        if self.proxy:
            if isinstance(self.proxy, str):
                options.add_argument(f"--proxy-server={self.proxy}")
            elif isinstance(self.proxy, dict):
                proxy_type = self.proxy.get("type", "http")
                proxy_host = self.proxy.get("host", "")
                proxy_port = self.proxy.get("port", "")
                proxy_url = f"{proxy_type}://{proxy_host}:{proxy_port}"
                options.add_argument(f"--proxy-server={proxy_url}")
        
        # 設置無頭模式
        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        
        # 禁用圖片
        if self.disable_images:
            options.add_argument("--blink-settings=imagesEnabled=false")
        
        # 禁用JavaScript
        if self.disable_javascript:
            options.add_argument("--disable-javascript")
        
        # 禁用Cookie
        if self.disable_cookies:
            options.add_argument("--disable-cookies")
        
        # 設置窗口大小
        width = self.window_size.get("width", 1920)
        height = self.window_size.get("height", 1080)
        options.add_argument(f"--window-size={width},{height}")
        
        # 設置用戶數據目錄
        if self.user_data_dir:
            options.add_argument(f"--user-data-dir={self.user_data_dir}")
        
        # 添加擴展
        for extension in self.extensions:
            options.add_extension(extension)
        
        # 添加其他參數
        for arg in self.arguments:
            options.add_argument(arg)
        
        # 添加實驗性選項
        for key, value in self.experimental_options.items():
            options.add_experimental_option(key, value)
        
        # 應用隱身選項
        if self.enable_stealth:
            stealth_config = {
                "disable_webgl": self.config.get("disable_webgl", False),
                "disable_canvas": self.config.get("disable_canvas", False)
            }
            self.stealth_manager.apply_stealth_options(options, stealth_config)
        
        return options
    
    def _configure_firefox_options(self) -> FirefoxOptions:
        """配置Firefox選項"""
        options = FirefoxOptions()
        
        # 設置用戶代理
        user_agent = self.user_agent
        if self.randomize_user_agent:
            user_agent = self._get_random_user_agent()
        if user_agent:
            options.set_preference("general.useragent.override", user_agent)
        
        # 設置代理
        if self.proxy:
            if isinstance(self.proxy, str):
                proxy_parts = self.proxy.split(":")
                if len(proxy_parts) >= 2:
                    host = proxy_parts[0]
                    port = int(proxy_parts[1])
                    options.set_preference("network.proxy.type", 1)
                    options.set_preference("network.proxy.http", host)
                    options.set_preference("network.proxy.http_port", port)
                    options.set_preference("network.proxy.ssl", host)
                    options.set_preference("network.proxy.ssl_port", port)
            elif isinstance(self.proxy, dict):
                proxy_type = self.proxy.get("type", "http")
                proxy_host = self.proxy.get("host", "")
                proxy_port = self.proxy.get("port", 0)
                
                options.set_preference("network.proxy.type", 1)
                if proxy_type == "http":
                    options.set_preference("network.proxy.http", proxy_host)
                    options.set_preference("network.proxy.http_port", proxy_port)
                    options.set_preference("network.proxy.ssl", proxy_host)
                    options.set_preference("network.proxy.ssl_port", proxy_port)
                elif proxy_type == "socks":
                    options.set_preference("network.proxy.socks", proxy_host)
                    options.set_preference("network.proxy.socks_port", proxy_port)
                    options.set_preference("network.proxy.socks_version", 5)
        
        # 設置無頭模式
        if self.headless:
            options.add_argument("--headless")
        
        # 禁用圖片
        if self.disable_images:
            options.set_preference("permissions.default.image", 2)
        
        # 禁用JavaScript
        if self.disable_javascript:
            options.set_preference("javascript.enabled", False)
        
        # 禁用Cookie
        if self.disable_cookies:
            options.set_preference("network.cookie.cookieBehavior", 2)
        
        # 設置窗口大小
        if self.window_size:
            width = self.window_size.get("width", 1920)
            height = self.window_size.get("height", 1080)
            options.add_argument(f"--width={width}")
            options.add_argument(f"--height={height}")
        
        # 設置二進制路徑
        if self.binary_path:
            options.binary_location = self.binary_path
        
        # 添加其他參數
        for arg in self.arguments:
            options.add_argument(arg)
        
        # 應用隱身選項
        if self.enable_stealth:
            stealth_config = {
                "disable_webgl": self.config.get("disable_webgl", False),
                "disable_canvas": self.config.get("disable_canvas", False)
            }
            self.stealth_manager.apply_stealth_options(options, stealth_config)
        
        return options
    
    def _configure_edge_options(self) -> EdgeOptions:
        """配置Edge選項"""
        options = EdgeOptions()
        
        # 設置用戶代理
        user_agent = self.user_agent
        if self.randomize_user_agent:
            user_agent = self._get_random_user_agent()
        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")
        
        # 設置代理
        if self.proxy:
            if isinstance(self.proxy, str):
                options.add_argument(f"--proxy-server={self.proxy}")
            elif isinstance(self.proxy, dict):
                proxy_type = self.proxy.get("type", "http")
                proxy_host = self.proxy.get("host", "")
                proxy_port = self.proxy.get("port", "")
                proxy_url = f"{proxy_type}://{proxy_host}:{proxy_port}"
                options.add_argument(f"--proxy-server={proxy_url}")
        
        # 設置無頭模式
        if self.headless:
            options.add_argument("--headless")
        
        # 禁用圖片
        if self.disable_images:
            options.add_argument("--blink-settings=imagesEnabled=false")
        
        # 設置窗口大小
        width = self.window_size.get("width", 1920)
        height = self.window_size.get("height", 1080)
        options.add_argument(f"--window-size={width},{height}")
        
        # 設置用戶數據目錄
        if self.user_data_dir:
            options.add_argument(f"--user-data-dir={self.user_data_dir}")
        
        # 添加其他參數
        for arg in self.arguments:
            options.add_argument(arg)
        
        # 添加實驗性選項
        for key, value in self.experimental_options.items():
            options.add_experimental_option(key, value)
        
        # 應用隱身選項
        if self.enable_stealth:
            stealth_config = {
                "disable_webgl": self.config.get("disable_webgl", False),
                "disable_canvas": self.config.get("disable_canvas", False)
            }
            self.stealth_manager.apply_stealth_options(options, stealth_config)
        
        return options
    
    def create_driver(self) -> Union[webdriver.Chrome, webdriver.Firefox, webdriver.Edge]:
        """
        創建並配置WebDriver
        
        Returns:
            配置好的WebDriver實例
        """
        try:
            if self.browser_type.lower() == "chrome":
                options = self._configure_chrome_options()
                service = ChromeService(executable_path=self.driver_path) if self.driver_path else ChromeService()
                self.driver = webdriver.Chrome(service=service, options=options)
            elif self.browser_type.lower() == "firefox":
                options = self._configure_firefox_options()
                service = FirefoxService(executable_path=self.driver_path) if self.driver_path else FirefoxService()
                self.driver = webdriver.Firefox(service=service, options=options)
            elif self.browser_type.lower() == "edge":
                options = self._configure_edge_options()
                service = EdgeService(executable_path=self.driver_path) if self.driver_path else EdgeService()
                self.driver = webdriver.Edge(service=service, options=options)
            else:
                raise ValueError(f"不支持的瀏覽器類型: {self.browser_type}")
            
            # 設置頁面加載超時
            self.driver.set_page_load_timeout(self.timeout)
            
            # 應用隱身腳本
            if self.enable_stealth:
                self.stealth_manager.apply_stealth_scripts(self.driver)
            
            return self.driver
            
        except Exception as e:
            self.logger.error(f"創建WebDriver失敗: {str(e)}")
            raise
    
    def close_driver(self):
        """安全關閉 WebDriver"""
        if self.driver:
            try:
                self.logger.info("關閉 WebDriver")
                self.driver.quit()
                self.driver = None
            except Exception as e:
                self.logger.error(f"關閉 WebDriver 失敗: {str(e)}")
    
    def save_cookies(self, filepath: str = None):
        """保存 cookies 到文件"""
        if not self.driver:
            self.logger.warning("WebDriver未初始化，無法保存cookies")
            return False
        
        try:
            if not filepath:
                # 設置默認路徑
                cookies_dir = self.config.get("cookies_dir", "cookies")
                os.makedirs(cookies_dir, exist_ok=True)
                filepath = os.path.join(cookies_dir, f"{self.browser_type}_cookies.json")
            
            # 確保目錄存在
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            
            cookies = self.driver.get_cookies()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2)
            
            self.logger.info(f"已保存 {len(cookies)} 個cookies到 {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"保存cookies失敗: {str(e)}")
            return False
    
    def load_cookies(self, filepath: str = None):
        """從文件加載 cookies"""
        if not self.driver:
            self.logger.warning("WebDriver未初始化，無法加載cookies")
            return False
        
        try:
            if not filepath:
                # 設置默認路徑
                cookies_dir = self.config.get("cookies_dir", "cookies")
                filepath = os.path.join(cookies_dir, f"{self.browser_type}_cookies.json")
            
            if not os.path.exists(filepath):
                self.logger.warning(f"Cookies文件不存在: {filepath}")
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            # 加載前先清除現有cookies
            self.driver.delete_all_cookies()
            
            for cookie in cookies:
                try:
                    # 修正 expiry 類型
                    if 'expiry' in cookie:
                        cookie['expiry'] = int(cookie['expiry'])
                    
                    # 移除非標準屬性
                    for key in list(cookie.keys()):
                        if key not in ['name', 'value', 'domain', 'path', 'expiry', 'secure', 'httpOnly']:
                            del cookie[key]
                    
                    # 添加cookie
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    self.logger.warning(f"添加cookie {cookie.get('name')} 失敗: {str(e)}")
            
            self.logger.info(f"已加載 {len(cookies)} 個cookies")
            return True
        except Exception as e:
            self.logger.error(f"加載cookies失敗: {str(e)}")
            return False
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10) -> Optional[Any]:
        """
        等待元素出現
        
        Args:
            by: 定位方式，如 By.XPATH, By.ID 等
            value: 定位值
            timeout: 超時時間（秒）
            
        Returns:
            元素物件，如果超時則返回None
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化，無法等待元素")
            return None
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            self.logger.warning(f"等待元素超時: {by}={value}")
            return None
        except Exception as e:
            self.logger.error(f"等待元素出錯: {str(e)}")
            return None
    
    def wait_for_clickable(self, by: By, value: str, timeout: int = 10) -> Optional[Any]:
        """
        等待元素可點擊
        
        Args:
            by: 定位方式，如 By.XPATH, By.ID 等
            value: 定位值
            timeout: 超時時間（秒）
            
        Returns:
            元素物件，如果超時則返回None
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化，無法等待元素")
            return None
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable((by, value)))
            return element
        except TimeoutException:
            self.logger.warning(f"等待元素可點擊超時: {by}={value}")
            return None
        except Exception as e:
            self.logger.error(f"等待元素可點擊出錯: {str(e)}")
            return None
    
    def safe_click(self, element, retries: int = 3) -> bool:
        """
        安全點擊元素，嘗試多種點擊方式
        
        Args:
            element: 要點擊的元素
            retries: 重試次數
            
        Returns:
            是否點擊成功
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化，無法點擊元素")
            return False
        
        for i in range(retries):
            try:
                # 嘗試直接點擊
                element.click()
                return True
            except Exception as e:
                self.logger.warning(f"直接點擊失敗 (嘗試 {i+1}/{retries}): {str(e)}")
                
                try:
                    # 嘗試滾動到元素
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.5)
                    
                    # 使用 JavaScript 點擊
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except Exception as js_e:
                    self.logger.warning(f"JavaScript點擊失敗 (嘗試 {i+1}/{retries}): {str(js_e)}")
                    
                    if i == retries - 1:
                        self.logger.error("所有點擊嘗試均失敗")
                        return False
                    
                    # 短暫延遲後重試
                    time.sleep(1)
        
        return False
    
    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
        """
        隨機延遲一段時間
        
        Args:
            min_seconds: 最小延遲時間（秒）
            max_seconds: 最大延遲時間（秒）
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def scroll_page(self, direction: str = "down", amount: int = 500):
        """
        滾動頁面
        
        Args:
            direction: 滾動方向，可選值: "up", "down", "top", "bottom"
            amount: 滾動距離 (僅對於 up/down 有效)
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化，無法滾動頁面")
            return
        
        try:
            if direction == "down":
                self.driver.execute_script(f"window.scrollBy(0, {amount});")
            elif direction == "up":
                self.driver.execute_script(f"window.scrollBy(0, -{amount});")
            elif direction == "top":
                self.driver.execute_script("window.scrollTo(0, 0);")
            elif direction == "bottom":
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception as e:
            self.logger.error(f"滾動頁面失敗: {str(e)}")
    
    def take_screenshot(self, filepath: str = None) -> Optional[str]:
        """
        截取螢幕截圖
        
        Args:
            filepath: 檔案路徑，如果為None則使用時間戳自動生成
            
        Returns:
            保存的檔案路徑，如果失敗則返回None
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化，無法截圖")
            return None
        
        try:
            if not filepath:
                screenshot_dir = self.config.get("screenshot_dir", "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(screenshot_dir, f"{timestamp}.png")
            
            # 確保目錄存在
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            
            self.driver.save_screenshot(filepath)
            self.logger.info(f"截圖已保存: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"截圖失敗: {str(e)}")
            return None
    
    def navigate_to(self, url: str, timeout: int = 30) -> bool:
        """
        導航到指定 URL
        
        Args:
            url: 目標 URL
            timeout: 頁面加載超時時間（秒）
            
        Returns:
            是否成功導航
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化，無法導航")
            return False
        
        try:
            self.logger.info(f"導航到: {url}")
            self.driver.set_page_load_timeout(timeout)
            self.driver.get(url)
            return True
        except TimeoutException:
            self.logger.error(f"頁面加載超時: {url}")
            return False
        except Exception as e:
            self.logger.error(f"導航失敗: {str(e)}")
            return False
    
    def refresh_page(self) -> bool:
        """
        刷新當前頁面
        
        Returns:
            是否成功刷新
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化，無法刷新頁面")
            return False
        
        try:
            self.logger.info("刷新頁面")
            self.driver.refresh()
            return True
        except Exception as e:
            self.logger.error(f"刷新頁面失敗: {str(e)}")
            return False
    
    def get_page_source(self) -> Optional[str]:
        """
        獲取頁面源碼
        
        Returns:
            頁面源碼，如果失敗則返回None
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化，無法獲取頁面源碼")
            return None
        
        try:
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"獲取頁面源碼失敗: {str(e)}")
            return None
    
    def execute_script(self, script: str, *args) -> Any:
        """
        執行JavaScript腳本
        
        Args:
            script: JavaScript腳本
            *args: 腳本參數
            
        Returns:
            腳本執行結果
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化，無法執行腳本")
            return None
        
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self.logger.error(f"執行腳本失敗: {str(e)}")
            return None
    
    def detect_captcha(self, selectors: List[str] = None) -> bool:
        """
        檢測頁面上是否有驗證碼
        
        Args:
            selectors: 驗證碼元素的選擇器列表
            
        Returns:
            是否檢測到驗證碼
        """
        if not self.driver:
            return False
        
        if not selectors:
            # 默認驗證碼選擇器
            selectors = [
                "//iframe[contains(@src, 'recaptcha')]",
                "//div[contains(@class, 'g-recaptcha')]",
                "//div[contains(@class, 'captcha')]",
                "//img[contains(@src, 'captcha')]",
                "//input[contains(@id, 'captcha')]"
            ]
        
        try:
            for selector in selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements and elements[0].is_displayed():
                    self.logger.info(f"檢測到驗證碼: {selector}")
                    return True
            
            # 檢查頁面文本
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            captcha_texts = ["captcha", "驗證碼", "安全驗證", "人機驗證", "機器人驗證"]
            
            for text in captcha_texts:
                if text in page_text:
                    self.logger.info(f"檢測到驗證碼文本: {text}")
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"檢測驗證碼出錯: {str(e)}")
            return False
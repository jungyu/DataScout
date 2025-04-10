"""
瀏覽器反指紋檢測模組
"""

import logging
from typing import Dict, Any, Optional, List, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from .configs.anti_fingerprint_config import AntiFingerprintConfig
from .stealth.stealth_manager import StealthManager

class BrowserAntiFingerprint:
    """瀏覽器反指紋檢測類"""
    
    def __init__(self, config: Union[Dict[str, Any], AntiFingerprintConfig], logger=None):
        """
        初始化瀏覽器反指紋檢測
        
        Args:
            config: 反指紋檢測配置
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.config = config
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
                driver = webdriver.Chrome(service=service, options=options)
            elif self.browser_type.lower() == "firefox":
                options = self._configure_firefox_options()
                service = FirefoxService(executable_path=self.driver_path) if self.driver_path else FirefoxService()
                driver = webdriver.Firefox(service=service, options=options)
            elif self.browser_type.lower() == "edge":
                options = self._configure_edge_options()
                service = EdgeService(executable_path=self.driver_path) if self.driver_path else EdgeService()
                driver = webdriver.Edge(service=service, options=options)
            else:
                raise ValueError(f"不支持的瀏覽器類型: {self.browser_type}")
            
            # 設置頁面加載超時
            driver.set_page_load_timeout(self.timeout)
            
            # 應用隱身腳本
            if self.enable_stealth:
                self.stealth_manager.apply_stealth_scripts(driver)
            
            return driver
            
        except Exception as e:
            self.logger.error(f"創建WebDriver失敗: {str(e)}")
            raise 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import random
import logging
import platform
from typing import Dict, List, Optional, Any, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.common.exceptions import WebDriverException

from ..utils.logger import setup_logger
from ..utils.error_handler import retry_on_exception, handle_exception


class WebDriverManager:
    """
    WebDriver管理器，負責創建、配置和管理WebDriver實例。
    支持Chrome、Firefox和Edge瀏覽器，並提供多種配置選項，包括用戶代理、代理伺服器、禁用特徵等。
    """
    
    def __init__(self, config: Dict = None, log_level: int = logging.INFO):
        """
        初始化WebDriver管理器
        
        Args:
            config: WebDriver配置
            log_level: 日誌級別
        """
        self.logger = setup_logger(__name__, log_level)
        self.logger.info("初始化WebDriver管理器")
        
        self.config = config or {}
        self.driver = None
        
        # 默認配置
        self.browser_type = self.config.get("browser_type", "chrome")
        self.user_agent = self.config.get("user_agent", None)
        self.proxy = self.config.get("proxy", None)
        self.headless = self.config.get("headless", False)
        self.disable_images = self.config.get("disable_images", True)
        self.disable_javascript = self.config.get("disable_javascript", False)
        self.disable_cookies = self.config.get("disable_cookies", False)
        self.user_data_dir = self.config.get("user_data_dir", None)
        self.extensions = self.config.get("extensions", [])
        self.arguments = self.config.get("arguments", [])
        self.experimental_options = self.config.get("experimental_options", {})
        self.driver_path = self.config.get("driver_path", None)
        self.binary_path = self.config.get("binary_path", None)
        
        # 用戶代理列表
        self.user_agents = self.config.get("user_agents", self._get_default_user_agents())
        
        # 代理列表
        self.proxies = self.config.get("proxies", [])
        
        # 隨機化設置
        self.randomize_user_agent = self.config.get("randomize_user_agent", True)
        self.randomize_proxy = self.config.get("randomize_proxy", False)
    
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
    
    def _get_random_proxy(self) -> Dict:
        """獲取隨機代理"""
        if self.proxies:
            return random.choice(self.proxies)
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
        proxy = self.proxy
        if self.randomize_proxy:
            proxy = self._get_random_proxy()
        if proxy:
            if isinstance(proxy, str):
                options.add_argument(f"--proxy-server={proxy}")
            elif isinstance(proxy, dict):
                proxy_type = proxy.get("type", "http")
                proxy_host = proxy.get("host", "")
                proxy_port = proxy.get("port", "")
                proxy_auth = proxy.get("auth", None)
                
                proxy_url = f"{proxy_type}://{proxy_host}:{proxy_port}"
                options.add_argument(f"--proxy-server={proxy_url}")
                
                if proxy_auth:
                    options.add_extension(self._create_proxy_auth_extension(
                        proxy_auth.get("username", ""),
                        proxy_auth.get("password", "")
                    ))
        
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
        
        # 添加防止WebDriver檢測的選項
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
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
        proxy = self.proxy
        if self.randomize_proxy:
            proxy = self._get_random_proxy()
        if proxy:
            if isinstance(proxy, str):
                proxy_parts = proxy.split(":")
                if len(proxy_parts) >= 2:
                    host = proxy_parts[0]
                    port = int(proxy_parts[1])
                    options.set_preference("network.proxy.type", 1)
                    options.set_preference("network.proxy.http", host)
                    options.set_preference("network.proxy.http_port", port)
                    options.set_preference("network.proxy.ssl", host)
                    options.set_preference("network.proxy.ssl_port", port)
            elif isinstance(proxy, dict):
                proxy_type = proxy.get("type", "http")
                proxy_host = proxy.get("host", "")
                proxy_port = proxy.get("port", 0)
                
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
        
        # 設置二進制路徑
        if self.binary_path:
            options.binary_location = self.binary_path
        
        # 添加其他參數
        for arg in self.arguments:
            options.add_argument(arg)
        
        # 防止WebDriver指紋識別
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        
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
        proxy = self.proxy
        if self.randomize_proxy:
            proxy = self._get_random_proxy()
        if proxy:
            if isinstance(proxy, str):
                options.add_argument(f"--proxy-server={proxy}")
            elif isinstance(proxy, dict):
                proxy_type = proxy.get("type", "http")
                proxy_host = proxy.get("host", "")
                proxy_port = proxy.get("port", "")
                
                proxy_url = f"{proxy_type}://{proxy_host}:{proxy_port}"
                options.add_argument(f"--proxy-server={proxy_url}")
        
        # 設置無頭模式
        if self.headless:
            options.add_argument("--headless")
        
        # 禁用圖片
        if self.disable_images:
            options.add_argument("--blink-settings=imagesEnabled=false")
        
        # 設置用戶數據目錄
        if self.user_data_dir:
            options.add_argument(f"--user-data-dir={self.user_data_dir}")
        
        # 添加其他參數
        for arg in self.arguments:
            options.add_argument(arg)
        
        # 添加實驗性選項
        for key, value in self.experimental_options.items():
            options.add_experimental_option(key, value)
        
        # 添加防止WebDriver檢測的選項
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        return options
    
    def _create_proxy_auth_extension(self, username: str, password: str, path: str = None) -> str:
        """創建代理認證擴展"""
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """
        
        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (self.proxy_host, self.proxy_port, username, password)
        
        if not path:
            path = os.path.join(os.getcwd(), "proxy_auth_extension")
        
        os.makedirs(path, exist_ok=True)
        
        with open(os.path.join(path, "manifest.json"), "w") as f:
            f.write(manifest_json)
        
        with open(os.path.join(path, "background.js"), "w") as f:
            f.write(background_js)
        
        return path
    
    @retry_on_exception(retries=3, delay=2)
    def create_driver(self) -> Union[webdriver.Chrome, webdriver.Firefox, webdriver.Edge]:
        """創建並配置WebDriver實例"""
        try:
            self.logger.info(f"創建 {self.browser_type} WebDriver")
            
            if self.browser_type.lower() == "chrome":
                options = self._configure_chrome_options()
                service = None
                if self.driver_path:
                    service = ChromeService(executable_path=self.driver_path)
                
                self.driver = webdriver.Chrome(service=service, options=options)
            
            elif self.browser_type.lower() == "firefox":
                options = self._configure_firefox_options()
                service = None
                if self.driver_path:
                    service = FirefoxService(executable_path=self.driver_path)
                
                self.driver = webdriver.Firefox(service=service, options=options)
            
            elif self.browser_type.lower() == "edge":
                options = self._configure_edge_options()
                service = None
                if self.driver_path:
                    service = EdgeService(executable_path=self.driver_path)
                
                self.driver = webdriver.Edge(service=service, options=options)
            
            else:
                raise ValueError(f"不支持的瀏覽器類型: {self.browser_type}")
            
            # 設置窗口大小
            if not self.headless:
                self.driver.maximize_window()
            else:
                self.driver.set_window_size(1920, 1080)
            
            # 設置頁面加載超時
            self.driver.set_page_load_timeout(self.config.get("page_load_timeout", 30))
            
            # 設置腳本超時
            self.driver.set_script_timeout(self.config.get("script_timeout", 30))
            
            # 執行隱藏 WebDriver 的 JavaScript
            self._hide_webdriver()
            
            self.logger.info(f"{self.browser_type} WebDriver 創建成功")
            return self.driver
        
        except Exception as e:
            self.logger.error(f"創建 {self.browser_type} WebDriver 失敗: {str(e)}")
            if self.driver:
                self.driver.quit()
                self.driver = None
            raise
    
    def _hide_webdriver(self):
        """執行隱藏 WebDriver 的 JavaScript"""
        if not self.driver:
            return
        
        try:
            # 通用的 WebDriver 隱藏腳本
            script = """
            // 覆蓋 WebDriver 屬性
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
            
            // 移除 'cdc_' 屬性
            for (const key of Object.keys(navigator)) {
                if (key.includes('cdc_')) {
                    delete navigator[key];
                }
            }
            
            // 修改 User-Agent
            if (navigator.userAgent.includes('HeadlessChrome')) {
                Object.defineProperty(navigator, 'userAgent', {
                    get: () => navigator.userAgent.replace('HeadlessChrome', 'Chrome'),
                });
            }
            
            // 模擬 Chrome 的插件
            if (!window.chrome) {
                window.chrome = {};
            }
            if (!window.chrome.runtime) {
                window.chrome.runtime = {};
            }
            """
            
            self.driver.execute_script(script)
            self.logger.debug("WebDriver 隱藏腳本執行成功")
        
        except Exception as e:
            self.logger.warning(f"執行 WebDriver 隱藏腳本失敗: {str(e)}")
    
    def close_driver(self):
        """安全關閉 WebDriver"""
        if self.driver:
            try:
                self.logger.info("關閉 WebDriver")
                self.driver.quit()
                self.driver = None
            except Exception as e:
                self.logger.error(f"關閉 WebDriver 失敗: {str(e)}")
    
    def refresh_page(self):
        """刷新當前頁面"""
        if self.driver:
            try:
                self.logger.info("刷新頁面")
                self.driver.refresh()
                return True
            except Exception as e:
                self.logger.error(f"刷新頁面失敗: {str(e)}")
                return False
        return False
    
    def delete_all_cookies(self):
        """刪除所有Cookie"""
        if self.driver:
            try:
                self.logger.info("刪除所有Cookie")
                self.driver.delete_all_cookies()
                return True
            except Exception as e:
                self.logger.error(f"刪除所有Cookie失敗: {str(e)}")
                return False
        return False
    
    def save_cookies(self, cookie_path: str):
        """保存Cookie到文件"""
        if not self.driver:
            self.logger.warning("WebDriver未初始化，無法保存Cookie")
            return False
        
        try:
            self.logger.info(f"保存Cookie到: {cookie_path}")
            cookies = self.driver.get_cookies()
            
            # 確保目錄存在
            os.makedirs(os.path.dirname(cookie_path), exist_ok=True)
            
            with open(cookie_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f)
            
            self.logger.info(f"成功保存 {len(cookies)} 個Cookie")
            return True
        except Exception as e:
            self.logger.error(f"保存Cookie失敗: {str(e)}")
            return False
    
    def load_cookies(self, cookie_path: str):
        """從文件加載Cookie"""
        if not self.driver:
            self.logger.warning("WebDriver未初始化，無法加載Cookie")
            return False
        
        try:
            self.logger.info(f"從 {cookie_path} 加載Cookie")
            
            if not os.path.exists(cookie_path):
                self.logger.warning(f"Cookie文件不存在: {cookie_path}")
                return False
            
            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            # 先刪除所有現有Cookie
            self.driver.delete_all_cookies()
            
            # 添加讀取的Cookie
            for cookie in cookies:
                # Selenium有時對Domain和Secure有特殊要求
                if 'expiry' in cookie:
                    cookie['expiry'] = int(cookie['expiry'])
                
                # 某些Cookie可能有額外的不允許的屬性
                for key in list(cookie.keys()):
                    if key not in ['name', 'value', 'domain', 'path', 'expiry', 'secure', 'httpOnly']:
                        del cookie[key]
                
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    self.logger.warning(f"添加Cookie失敗: {str(e)}，跳過該Cookie")
            
            self.logger.info(f"成功加載 {len(cookies)} 個Cookie")
            return True
        except Exception as e:
            self.logger.error(f"加載Cookie失敗: {str(e)}")
            return False
    
    def change_user_agent(self, user_agent: str = None):
        """更改用戶代理"""
        if not self.driver:
            self.logger.warning("WebDriver未初始化，無法更改用戶代理")
            return False
        
        try:
            if user_agent is None and self.randomize_user_agent:
                user_agent = self._get_random_user_agent()
            
            if not user_agent:
                self.logger.warning("未提供用戶代理且沒有可用的隨機用戶代理")
                return False
            
            self.logger.info(f"更改用戶代理為: {user_agent}")
            
            # 使用JavaScript更改用戶代理
            script = f"""
            Object.defineProperty(navigator, 'userAgent', {{
                get: function() {{ return '{user_agent}'; }}
            }});
            """
            
            self.driver.execute_script(script)
            return True
        except Exception as e:
            self.logger.error(f"更改用戶代理失敗: {str(e)}")
            return False
    
    def change_proxy(self, proxy: Union[str, Dict] = None):
        """更改代理設置"""
        self.logger.warning("更改代理需要重新創建WebDriver，不支持運行時更改")
        return False
    
    def execute_stealth_js(self, script_path: str = None):
        """執行隱身JavaScript腳本"""
        if not self.driver:
            self.logger.warning("WebDriver未初始化，無法執行隱身腳本")
            return False
        
        try:
            # 默認腳本
            if script_path is None:
                script_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "anti_detection", "stealth_scripts", "browser_fp.js"
                )
            
            if not os.path.exists(script_path):
                self.logger.warning(f"隱身腳本不存在: {script_path}")
                return False
            
            self.logger.info(f"執行隱身腳本: {script_path}")
            
            with open(script_path, 'r', encoding='utf-8') as f:
                script = f.read()
            
            self.driver.execute_script(script)
            self.logger.info("隱身腳本執行成功")
            return True
        except Exception as e:
            self.logger.error(f"執行隱身腳本失敗: {str(e)}")
            return False
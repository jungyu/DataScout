import os
import time
import logging
import json
import random
import platform
import gzip
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

from selenium_base.core.exceptions import (
    CrawlerException, BrowserException, RequestException,
    CrawlerTimeoutError, NetworkError, ValidationError
)
from selenium_base.core.config import BaseConfig, BrowserConfig, RequestConfig
from selenium_base.core.logger import setup_logger
from selenium_base.anti_detection import AntiDetectionManager
from captcha_manager import CaptchaManagerFactory, CaptchaConfig

@dataclass
class CacheConfig:
    """快取配置"""
    expire_days: int = 7  # 快取過期天數
    compress: bool = True  # 是否壓縮快取
    max_size: int = 100 * 1024 * 1024  # 最大快取大小（字節）

@dataclass
class CrawlerState:
    """爬蟲狀態數據類"""
    is_running: bool = False
    current_url: Optional[str] = None
    last_request_time: float = 0.0
    request_count: int = 0
    error_count: int = 0
    retry_count: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[float] = None
    cookie_file: Optional[str] = None
    last_cookie_update: Optional[float] = None
    cookie_update_count: int = 0
    cache_dir: Optional[str] = None
    last_cache_cleanup: Optional[float] = None
    cache_size: int = 0

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
        self.captcha_manager = None
        self.cache_config = CacheConfig()
        
    def initialize(self) -> None:
        """初始化爬蟲環境"""
        try:
            self._setup_browser()
            self._setup_anti_detection()
            self._setup_captcha_manager()
            self._setup_cache()
            self._load_cookies()
            self.state.is_running = True
            self.logger.info("爬蟲初始化完成")
        except Exception as e:
            self.state.last_error = str(e)
            self.state.last_error_time = time.time()
            self.state.error_count += 1
            self.logger.error(f"爬蟲初始化失敗: {str(e)}")
            raise CrawlerException("爬蟲初始化失敗", details={"error": str(e)})
            
    def _setup_browser(self) -> None:
        """設置瀏覽器"""
        try:
            options = Options()
            
            # 基本設置
            if self.config.browser.headless:
                options.add_argument("--headless")
            
            # 窗口設置
            window_size = self.config.browser.window_size
            options.add_argument(f"--window-size={window_size['width']},{window_size['height']}")
            
            # 代理設置
            if self.config.browser.proxy:
                options.add_argument(f"--proxy-server={self.config.browser.proxy}")
                
            # 用戶代理設置
            if self.config.browser.user_agent:
                options.add_argument(f"--user-agent={self.config.browser.user_agent}")
            
            # 反檢測設置
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # 其他瀏覽器設置
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-save-password-bubble")
            options.add_argument("--disable-translate")
            options.add_argument("--disable-web-security")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--ignore-ssl-errors")
            
            # 性能優化設置
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-setuid-sandbox")
            options.add_argument("--disable-accelerated-2d-canvas")
            options.add_argument("--disable-accelerated-jpeg-decoding")
            options.add_argument("--disable-accelerated-mjpeg-decode")
            options.add_argument("--disable-accelerated-video-decode")
            
            # 內存優化設置
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-breakpad")
            options.add_argument("--disable-component-extensions-with-background-pages")
            options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
            options.add_argument("--disable-ipc-flooding-protection")
            options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
            
            # 創建瀏覽器實例
            self.driver = webdriver.Chrome(options=options)
            
            # 設置超時
            self.driver.set_page_load_timeout(self.config.browser.timeout)
            self.driver.implicitly_wait(self.config.browser.timeout)
            
            # 最大化窗口
            if self.config.browser.maximize:
                self.driver.maximize_window()
            
            # 注入反檢測 JavaScript
            self._inject_anti_detection_js()
                
        except Exception as e:
            raise BrowserException("瀏覽器設置失敗", details={"error": str(e)})
            
    def _setup_anti_detection(self) -> None:
        """設置反偵測"""
        try:
            self.anti_detection = AntiDetectionManager(
                driver=self.driver,
                config=self.config.anti_detection
            )
            self.logger.info("反偵測設置完成")
        except Exception as e:
            raise CrawlerException("反偵測設置失敗", details={"error": str(e)})
            
    def _setup_captcha_manager(self) -> None:
        """設置驗證碼管理器"""
        try:
            captcha_config = CaptchaConfig(**self.config.captcha)
            self.captcha_manager = CaptchaManagerFactory.create_manager(
                driver=self.driver,
                config=captcha_config
            )
            self.logger.info("驗證碼管理器設置完成")
        except Exception as e:
            raise CrawlerException("驗證碼管理器設置失敗", details={"error": str(e)})

    def _setup_cache(self) -> None:
        """設置快取目錄"""
        try:
            cache_dir = os.path.join(
                self.config.data_dir,
                "cache",
                self.__class__.__name__
            )
            os.makedirs(cache_dir, exist_ok=True)
            self.state.cache_dir = cache_dir
            self._cleanup_expired_cache()
            self.logger.info(f"快取目錄設置完成: {cache_dir}")
        except Exception as e:
            self.logger.error(f"設置快取目錄失敗: {str(e)}")

    def _cleanup_expired_cache(self) -> None:
        """清理過期快取"""
        try:
            if not self.state.cache_dir:
                return
            
            expire_time = time.time() - (self.cache_config.expire_days * 24 * 60 * 60)
            total_size = 0
            
            for file in os.listdir(self.state.cache_dir):
                file_path = os.path.join(self.state.cache_dir, file)
                if os.path.isfile(file_path):
                    # 檢查文件修改時間
                    if os.path.getmtime(file_path) < expire_time:
                        os.remove(file_path)
                        self.logger.info(f"已刪除過期快取: {file_path}")
                    else:
                        total_size += os.path.getsize(file_path)
            
            self.state.cache_size = total_size
            self.state.last_cache_cleanup = time.time()
            
            # 如果快取大小超過限制，刪除最舊的文件
            while total_size > self.cache_config.max_size:
                oldest_file = min(
                    (f for f in os.listdir(self.state.cache_dir) if os.path.isfile(os.path.join(self.state.cache_dir, f))),
                    key=lambda f: os.path.getmtime(os.path.join(self.state.cache_dir, f))
                )
                file_path = os.path.join(self.state.cache_dir, oldest_file)
                total_size -= os.path.getsize(file_path)
                os.remove(file_path)
                self.logger.info(f"已刪除超出大小限制的快取: {file_path}")
            
            self.state.cache_size = total_size
        except Exception as e:
            self.logger.error(f"清理過期快取失敗: {str(e)}")

    def _inject_anti_detection_js(self) -> None:
        """注入反檢測 JavaScript"""
        try:
            # 修改 navigator.webdriver
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            # 修改 window.chrome
            self.driver.execute_script("""
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
            """)
            
            # 添加隨機的插件數量
            plugins_count = random.randint(3, 10)
            self.driver.execute_script(f"""
                Object.defineProperty(navigator, 'plugins', {{
                    get: () => Array({plugins_count}).fill().map(() => ({{
                        name: ['Chrome PDF Plugin', 'Chrome PDF Viewer', 'Native Client'][Math.floor(Math.random() * 3)],
                        description: 'Portable Document Format',
                        filename: 'internal-pdf-viewer'
                    }}))
                }});
            """)
            
            # 修改 navigator.languages
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en']
                });
            """)
            
            # 修改 navigator.platform
            self.driver.execute_script(f"""
                Object.defineProperty(navigator, 'platform', {{
                    get: () => '{platform.system()}'
                }});
            """)
            
            # 修改 navigator.hardwareConcurrency
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8
                });
            """)
            
            # 修改 navigator.deviceMemory
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8
                });
            """)
            
            # 修改 navigator.permissions
            self.driver.execute_script("""
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            # 修改 navigator.connection
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 50,
                        downlink: 10,
                        saveData: false
                    })
                });
            """)
            
            # 修改 navigator.getBattery
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'getBattery', {
                    get: () => () => Promise.resolve({
                        charging: true,
                        chargingTime: 0,
                        dischargingTime: Infinity,
                        level: 1
                    })
                });
            """)
            
            # 修改 navigator.maxTouchPoints
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'maxTouchPoints', {
                    get: () => 10
                });
            """)
            
            # 修改 navigator.vendor
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'vendor', {
                    get: () => 'Google Inc.'
                });
            """)
            
            # 修改 navigator.oscpu
            self.driver.execute_script(f"""
                Object.defineProperty(navigator, 'oscpu', {{
                    get: () => '{platform.system()} {platform.release()}'
                }});
            """)
            
            # 修改 navigator.buildID
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'buildID', {
                    get: () => '20240215000000'
                });
            """)
            
            # 模擬本機儲存
            self.driver.execute_script("""
                // 模擬常見的本機儲存鍵值
                const mockLocalStorage = {
                    'theme': 'light',
                    'language': 'zh-TW',
                    'timezone': 'Asia/Taipei',
                    'notifications': 'enabled',
                    'lastVisit': new Date().toISOString(),
                    'userPreferences': JSON.stringify({
                        fontSize: 14,
                        fontFamily: 'Arial',
                        colorScheme: 'default'
                    }),
                    'sessionId': Math.random().toString(36).substring(2),
                    'lastLogin': new Date().toISOString(),
                    'deviceId': 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                        const r = Math.random() * 16 | 0;
                        const v = c === 'x' ? r : (r & 0x3 | 0x8);
                        return v.toString(16);
                    })
                };
                
                // 注入模擬的本機儲存
                Object.keys(mockLocalStorage).forEach(key => {
                    localStorage.setItem(key, mockLocalStorage[key]);
                });
                
                // 模擬會話儲存
                const mockSessionStorage = {
                    'currentPage': window.location.pathname,
                    'sessionStartTime': new Date().toISOString(),
                    'pageVisits': '1',
                    'lastAction': 'pageLoad',
                    'userSession': JSON.stringify({
                        startTime: new Date().toISOString(),
                        isActive: true,
                        lastActivity: new Date().toISOString()
                    })
                };
                
                // 注入模擬的會話儲存
                Object.keys(mockSessionStorage).forEach(key => {
                    sessionStorage.setItem(key, mockSessionStorage[key]);
                });
                
                // 模擬 IndexedDB
                const mockIndexedDB = {
                    'userSettings': {
                        theme: 'light',
                        notifications: true,
                        language: 'zh-TW'
                    },
                    'browserHistory': [
                        {
                            url: window.location.href,
                            title: document.title,
                            timestamp: new Date().toISOString()
                        }
                    ]
                };
                
                // 注入模擬的 IndexedDB 數據
                if (window.indexedDB) {
                    const request = indexedDB.open('browserData', 1);
                    request.onupgradeneeded = function(event) {
                        const db = event.target.result;
                        if (!db.objectStoreNames.contains('userData')) {
                            const store = db.createObjectStore('userData', { keyPath: 'id' });
                            store.add({ id: 'settings', data: mockIndexedDB.userSettings });
                            store.add({ id: 'history', data: mockIndexedDB.browserHistory });
                        }
                    };
                }
                
                // 模擬更多的瀏覽器 API
                // 模擬 Canvas 指紋
                const originalGetContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(type, attributes) {
                    const context = originalGetContext.call(this, type, attributes);
                    if (type === '2d') {
                        const originalGetImageData = context.getImageData;
                        context.getImageData = function() {
                            const imageData = originalGetImageData.apply(this, arguments);
                            // 添加隨機噪點
                            for (let i = 0; i < imageData.data.length; i += 4) {
                                imageData.data[i] += Math.floor(Math.random() * 10) - 5;
                                imageData.data[i + 1] += Math.floor(Math.random() * 10) - 5;
                                imageData.data[i + 2] += Math.floor(Math.random() * 10) - 5;
                            }
                            return imageData;
                        };
                    }
                    return context;
                };
                
                // 模擬 WebGL 指紋
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    // 模擬不同的顯卡
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter.apply(this, arguments);
                };
                
                // 模擬音頻指紋
                const originalGetChannelData = AudioBuffer.prototype.getChannelData;
                AudioBuffer.prototype.getChannelData = function() {
                    const channelData = originalGetChannelData.apply(this, arguments);
                    // 添加隨機噪點
                    for (let i = 0; i < channelData.length; i += 100) {
                        channelData[i] += Math.random() * 0.0001;
                    }
                    return channelData;
                };
                
                // 模擬用戶行為
                const mockUserBehavior = {
                    mouseMovements: [],
                    keyStrokes: [],
                    scrollEvents: [],
                    clickEvents: []
                };
                
                // 記錄滑鼠移動
                document.addEventListener('mousemove', function(e) {
                    mockUserBehavior.mouseMovements.push({
                        x: e.clientX,
                        y: e.clientY,
                        timestamp: new Date().toISOString()
                    });
                });
                
                // 記錄鍵盤輸入
                document.addEventListener('keydown', function(e) {
                    mockUserBehavior.keyStrokes.push({
                        key: e.key,
                        timestamp: new Date().toISOString()
                    });
                });
                
                // 記錄滾動事件
                document.addEventListener('scroll', function(e) {
                    mockUserBehavior.scrollEvents.push({
                        scrollY: window.scrollY,
                        timestamp: new Date().toISOString()
                    });
                });
                
                // 記錄點擊事件
                document.addEventListener('click', function(e) {
                    mockUserBehavior.clickEvents.push({
                        x: e.clientX,
                        y: e.clientY,
                        target: e.target.tagName,
                        timestamp: new Date().toISOString()
                    });
                });
                
                // 將用戶行為數據保存到 IndexedDB
                if (window.indexedDB) {
                    const request = indexedDB.open('userBehavior', 1);
                    request.onupgradeneeded = function(event) {
                        const db = event.target.result;
                        if (!db.objectStoreNames.contains('behavior')) {
                            const store = db.createObjectStore('behavior', { keyPath: 'id' });
                            store.add({ id: 'current', data: mockUserBehavior });
                        }
                    };
                }
            """)
            
            self.logger.info("反檢測 JavaScript 注入完成")
        except Exception as e:
            self.logger.error(f"注入反檢測 JavaScript 失敗: {str(e)}")

    def _load_cookies(self) -> None:
        """載入 Cookie"""
        try:
            if self.config.request.cookies:
                for cookie in self.config.request.cookies:
                    self.driver.add_cookie(cookie)
                self.logger.info("Cookie 載入完成")
        except Exception as e:
            self.logger.error(f"載入 Cookie 失敗: {str(e)}")

    def save_cookies(self, file_path: Optional[str] = None) -> None:
        """
        保存 Cookie
        
        Args:
            file_path: Cookie 文件路徑
        """
        try:
            if not file_path:
                file_path = os.path.join(
                    self.config.data_dir,
                    "cookies",
                    f"{self.__class__.__name__}_{int(time.time())}.json"
                )
            
            cookies = self.driver.get_cookies()
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            
            self.state.cookie_file = file_path
            self.state.last_cookie_update = time.time()
            self.state.cookie_update_count += 1
            self.logger.info(f"Cookie 已保存到: {file_path}")
        except Exception as e:
            self.logger.error(f"保存 Cookie 失敗: {str(e)}")

    def load_cookies_from_file(self, file_path: str) -> None:
        """
        從文件載入 Cookie
        
        Args:
            file_path: Cookie 文件路徑
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Cookie 文件不存在: {file_path}")
            
            with open(file_path, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            
            self.state.cookie_file = file_path
            self.state.last_cookie_update = time.time()
            self.state.cookie_update_count += 1
            self.logger.info(f"已從文件載入 Cookie: {file_path}")
        except Exception as e:
            self.logger.error(f"從文件載入 Cookie 失敗: {str(e)}")

    def clear_cookies(self) -> None:
        """清除所有 Cookie"""
        try:
            self.driver.delete_all_cookies()
            self.state.cookie_file = None
            self.state.last_cookie_update = time.time()
            self.logger.info("已清除所有 Cookie")
        except Exception as e:
            self.logger.error(f"清除 Cookie 失敗: {str(e)}")

    def rotate_cookies(self, cookie_files: List[str]) -> None:
        """
        輪換使用多個 Cookie 文件
        
        Args:
            cookie_files: Cookie 文件路徑列表
        """
        try:
            if not cookie_files:
                raise ValueError("Cookie 文件列表為空")
            
            # 清除當前 Cookie
            self.clear_cookies()
            
            # 選擇下一個 Cookie 文件
            next_file = cookie_files[self.state.cookie_update_count % len(cookie_files)]
            
            # 載入新的 Cookie
            self.load_cookies_from_file(next_file)
            
            self.logger.info(f"已輪換到新的 Cookie 文件: {next_file}")
        except Exception as e:
            self.logger.error(f"輪換 Cookie 失敗: {str(e)}")

    def save_cache(self, key: str, data: Any) -> None:
        """
        保存數據到快取
        
        Args:
            key: 快取鍵值
            data: 要保存的數據
        """
        try:
            if not self.state.cache_dir:
                raise ValueError("快取目錄未設置")
            
            # 生成快取文件名
            cache_key = hashlib.md5(key.encode()).hexdigest()
            cache_file = os.path.join(self.state.cache_dir, f"{cache_key}.json")
            
            # 準備快取數據
            cache_data = {
                "key": key,
                "data": data,
                "timestamp": time.time(),
                "expire_time": time.time() + (self.cache_config.expire_days * 24 * 60 * 60)
            }
            
            # 保存快取
            if self.cache_config.compress:
                cache_file += ".gz"
                with gzip.open(cache_file, "wt", encoding="utf-8") as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
            else:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            # 更新快取大小
            self.state.cache_size += os.path.getsize(cache_file)
            
            self.logger.info(f"數據已保存到快取: {cache_file}")
        except Exception as e:
            self.logger.error(f"保存快取失敗: {str(e)}")

    def load_cache(self, key: str) -> Optional[Any]:
        """
        從快取載入數據
        
        Args:
            key: 快取鍵值
            
        Returns:
            快取數據，如果不存在或已過期則返回 None
        """
        try:
            if not self.state.cache_dir:
                raise ValueError("快取目錄未設置")
            
            # 生成快取文件名
            cache_key = hashlib.md5(key.encode()).hexdigest()
            cache_file = os.path.join(self.state.cache_dir, f"{cache_key}.json")
            cache_file_gz = cache_file + ".gz"
            
            # 檢查快取文件是否存在
            if not os.path.exists(cache_file) and not os.path.exists(cache_file_gz):
                return None
            
            # 讀取快取數據
            if os.path.exists(cache_file_gz):
                with gzip.open(cache_file_gz, "rt", encoding="utf-8") as f:
                    cache_data = json.load(f)
            else:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
            
            # 檢查快取是否過期
            if time.time() > cache_data["expire_time"]:
                os.remove(cache_file if os.path.exists(cache_file) else cache_file_gz)
                self.state.cache_size -= os.path.getsize(cache_file if os.path.exists(cache_file) else cache_file_gz)
                return None
            
            self.logger.info(f"已從快取載入數據: {cache_file}")
            return cache_data["data"]
        except Exception as e:
            self.logger.error(f"載入快取失敗: {str(e)}")
            return None

    def clear_cache(self) -> None:
        """清除所有快取"""
        try:
            if not self.state.cache_dir:
                raise ValueError("快取目錄未設置")
            
            for file in os.listdir(self.state.cache_dir):
                file_path = os.path.join(self.state.cache_dir, file)
                if os.path.isfile(file_path):
                    self.state.cache_size -= os.path.getsize(file_path)
                    os.remove(file_path)
            
            self.state.last_cache_cleanup = time.time()
            self.logger.info("已清除所有快取")
        except Exception as e:
            self.logger.error(f"清除快取失敗: {str(e)}")

    def navigate(self, url: str, retry: bool = True) -> None:
        """
        導航到指定URL
        
        Args:
            url: 目標URL
            retry: 是否在失敗時重試
        """
        try:
            self.driver.get(url)
            self.state.current_url = url
            self.state.request_count += 1
            self.state.last_request_time = time.time()
            self.logger.info(f"成功導航到: {url}")
        except TimeoutException as e:
            self.state.error_count += 1
            self.logger.error(f"導航超時: {url}")
            if retry and self.state.retry_count < self.config.request.max_retries:
                self.state.retry_count += 1
                time.sleep(self.config.request.retry_interval)
                return self.navigate(url, retry)
            raise CrawlerTimeoutError(f"導航超時: {url}")
        except Exception as e:
            self.state.error_count += 1
            self.state.last_error = str(e)
            self.state.last_error_time = time.time()
            self.logger.error(f"導航失敗: {str(e)}")
            raise CrawlerException("導航失敗", details={"url": url, "error": str(e)})
            
    def wait_for_element(
        self,
        by: By,
        value: str,
        timeout: Optional[int] = None,
        retry: bool = True
    ) -> Any:
        """
        等待元素出現
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間（秒）
            retry: 是否在失敗時重試
            
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
            self.state.error_count += 1
            self.logger.error(f"等待元素超時: {value}")
            if retry and self.state.retry_count < self.config.request.max_retries:
                self.state.retry_count += 1
                time.sleep(self.config.request.retry_interval)
                return self.wait_for_element(by, value, timeout, retry)
            raise CrawlerTimeoutError(f"等待元素超時: {value}")
        except NoSuchElementException:
            self.state.error_count += 1
            self.logger.error(f"元素不存在: {value}")
            raise ValidationError(f"元素不存在: {value}")
        except Exception as e:
            self.state.error_count += 1
            self.state.last_error = str(e)
            self.state.last_error_time = time.time()
            self.logger.error(f"等待元素時發生錯誤: {str(e)}")
            raise CrawlerException("等待元素失敗", details={"element": value, "error": str(e)})
            
    def wait_for_elements(
        self,
        by: By,
        value: str,
        timeout: Optional[int] = None,
        retry: bool = True
    ) -> List[Any]:
        """
        等待多個元素出現
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間（秒）
            retry: 是否在失敗時重試
            
        Returns:
            找到的元素列表
        """
        try:
            timeout = timeout or self.config.browser.timeout
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
            return elements
        except TimeoutException:
            self.state.error_count += 1
            self.logger.error(f"等待元素超時: {value}")
            if retry and self.state.retry_count < self.config.request.max_retries:
                self.state.retry_count += 1
                time.sleep(self.config.request.retry_interval)
                return self.wait_for_elements(by, value, timeout, retry)
            raise CrawlerTimeoutError(f"等待元素超時: {value}")
        except Exception as e:
            self.state.error_count += 1
            self.state.last_error = str(e)
            self.state.last_error_time = time.time()
            self.logger.error(f"等待元素時發生錯誤: {str(e)}")
            raise CrawlerException("等待元素失敗", details={"element": value, "error": str(e)})

    def wait_for_element_clickable(
        self,
        by: By,
        value: str,
        timeout: Optional[int] = None,
        retry: bool = True
    ) -> Any:
        """
        等待元素可點擊
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間（秒）
            retry: 是否在失敗時重試
            
        Returns:
            可點擊的元素
        """
        try:
            timeout = timeout or self.config.browser.timeout
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            self.state.error_count += 1
            self.logger.error(f"等待元素可點擊超時: {value}")
            if retry and self.state.retry_count < self.config.request.max_retries:
                self.state.retry_count += 1
                time.sleep(self.config.request.retry_interval)
                return self.wait_for_element_clickable(by, value, timeout, retry)
            raise CrawlerTimeoutError(f"等待元素可點擊超時: {value}")
        except Exception as e:
            self.state.error_count += 1
            self.state.last_error = str(e)
            self.state.last_error_time = time.time()
            self.logger.error(f"等待元素可點擊時發生錯誤: {str(e)}")
            raise CrawlerException("等待元素可點擊失敗", details={"element": value, "error": str(e)})

    def wait_for_page_load(
        self,
        timeout: Optional[int] = None,
        retry: bool = True
    ) -> None:
        """
        等待頁面加載完成
        
        Args:
            timeout: 超時時間（秒）
            retry: 是否在失敗時重試
        """
        try:
            timeout = timeout or self.config.browser.timeout
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            self.logger.info("頁面加載完成")
        except TimeoutException:
            self.state.error_count += 1
            self.logger.error("頁面加載超時")
            if retry and self.state.retry_count < self.config.request.max_retries:
                self.state.retry_count += 1
                time.sleep(self.config.request.retry_interval)
                return self.wait_for_page_load(timeout, retry)
            raise CrawlerTimeoutError("頁面加載超時")
        except Exception as e:
            self.state.error_count += 1
            self.state.last_error = str(e)
            self.state.last_error_time = time.time()
            self.logger.error(f"等待頁面加載時發生錯誤: {str(e)}")
            raise CrawlerException("等待頁面加載失敗", details={"error": str(e)})

    def execute_script(
        self,
        script: str,
        *args,
        timeout: Optional[int] = None
    ) -> Any:
        """
        執行 JavaScript 代碼
        
        Args:
            script: JavaScript 代碼
            args: 傳遞給 JavaScript 的參數
            timeout: 超時時間（秒）
            
        Returns:
            JavaScript 執行結果
        """
        try:
            timeout = timeout or self.config.browser.timeout
            self.driver.set_script_timeout(timeout)
            result = self.driver.execute_script(script, *args)
            return result
        except Exception as e:
            self.state.error_count += 1
            self.state.last_error = str(e)
            self.state.last_error_time = time.time()
            self.logger.error(f"執行 JavaScript 時發生錯誤: {str(e)}")
            raise CrawlerException("執行 JavaScript 失敗", details={"script": script, "error": str(e)})

    def wait_for_ajax(
        self,
        timeout: Optional[int] = None,
        retry: bool = True
    ) -> None:
        """
        等待 AJAX 請求完成
        
        Args:
            timeout: 超時時間（秒）
            retry: 是否在失敗時重試
        """
        try:
            timeout = timeout or self.config.browser.timeout
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return jQuery.active == 0")
            )
            self.logger.info("AJAX 請求完成")
        except TimeoutException:
            self.state.error_count += 1
            self.logger.error("等待 AJAX 請求超時")
            if retry and self.state.retry_count < self.config.request.max_retries:
                self.state.retry_count += 1
                time.sleep(self.config.request.retry_interval)
                return self.wait_for_ajax(timeout, retry)
            raise CrawlerTimeoutError("等待 AJAX 請求超時")
        except Exception as e:
            self.state.error_count += 1
            self.state.last_error = str(e)
            self.state.last_error_time = time.time()
            self.logger.error(f"等待 AJAX 請求時發生錯誤: {str(e)}")
            raise CrawlerException("等待 AJAX 請求失敗", details={"error": str(e)})

    def wait_for_dynamic_content(
        self,
        by: By,
        value: str,
        timeout: Optional[int] = None,
        retry: bool = True
    ) -> Any:
        """
        等待動態加載的內容
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間（秒）
            retry: 是否在失敗時重試
            
        Returns:
            動態加載的元素
        """
        try:
            # 等待頁面加載完成
            self.wait_for_page_load(timeout, retry)
            
            # 等待 AJAX 請求完成
            self.wait_for_ajax(timeout, retry)
            
            # 等待元素出現
            element = self.wait_for_element(by, value, timeout, retry)
            
            return element
        except Exception as e:
            self.state.error_count += 1
            self.state.last_error = str(e)
            self.state.last_error_time = time.time()
            self.logger.error(f"等待動態內容時發生錯誤: {str(e)}")
            raise CrawlerException("等待動態內容失敗", details={"element": value, "error": str(e)})
            
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
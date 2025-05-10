"""
Playwright Base 核心基礎類

提供瀏覽器啟動、頁面管理等基本功能。
"""

import os
import json
import time
import random
import threading
from typing import Dict, Any, List, Optional, Union, Callable

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Response, TimeoutError

from playwright_base.utils.logger import setup_logger
from playwright_base.utils.exceptions import BrowserException, NavigationException, TimeoutException

# 設置日誌
logger = setup_logger(name=__name__)

class PlaywrightBase:
    """
    Playwright Base 核心基礎類，提供瀏覽器自動化的基礎功能。
    """
    
    def __init__(
        self,
        headless: bool = False,
        browser_type: str = "chromium",
        storage_state: str = None,
        user_agent: str = None,
        proxy: Dict[str, str] = None,
        viewport: Dict[str, int] = None,
        args: List[str] = None,
        ignore_https_errors: bool = True,
        slow_mo: int = 0
    ):
        """
        初始化 PlaywrightBase 實例。

        參數:
            headless (bool): 是否以無頭模式運行瀏覽器。
            browser_type (str): 瀏覽器類型，可選值: 'chromium', 'firefox', 'webkit'。
            storage_state (str): 存儲狀態檔案路徑，包含 cookies 和 localStorage。
            user_agent (str): 自定義 User-Agent。
            proxy (Dict[str, str]): 代理設置，例如 {'server': 'http://proxy.com:8080'}。
            viewport (Dict[str, int]): 視窗大小，例如 {'width': 1920, 'height': 1080}。
            args (List[str]): 瀏覽器啟動參數。
            ignore_https_errors (bool): 是否忽略 HTTPS 錯誤。
            slow_mo (int): 減慢操作的毫秒數，用於調試。
        """
        # 初始化參數
        self.headless = headless
        self.browser_type = browser_type
        self.storage_state = storage_state
        self.user_agent = user_agent
        self.proxy = proxy
        self.viewport = viewport or {'width': 1920, 'height': 1080}
        self.args = args or ['--start-maximized']
        self.ignore_https_errors = ignore_https_errors
        self.slow_mo = slow_mo
        
        # 初始化 Playwright 相關屬性
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._pages = []
        self._timers = []  # 用於存儲定時器引用
        
        # 初始化標記
        self._is_stealth_mode_enabled = False
        
    @property
    def playwright(self):
        """獲取 playwright 實例"""
        return self._playwright
    
    @property
    def browser(self):
        """獲取瀏覽器實例"""
        return self._browser
    
    @property
    def context(self):
        """獲取瀏覽器上下文"""
        return self._context
    
    @property
    def page(self):
        """獲取主頁面實例"""
        return self._page
    
    @property
    def pages(self):
        """獲取所有頁面實例"""
        return self._pages
    
    def start(self) -> 'PlaywrightBase':
        """
        啟動瀏覽器和創建上下文。

        返回:
            PlaywrightBase: 返回自身實例以支持鏈式調用。
        
        異常:
            BrowserException: 瀏覽器啟動失敗時拋出。
        """
        try:
            # 啟動 playwright
            logger.info(f"啟動 {self.browser_type} 瀏覽器 (headless={self.headless})...")
            self._playwright = sync_playwright().start()
            
            # 選擇瀏覽器類型
            if self.browser_type == "chromium":
                browser_class = self._playwright.chromium
            elif self.browser_type == "firefox":
                browser_class = self._playwright.firefox
            elif self.browser_type == "webkit":
                browser_class = self._playwright.webkit
            else:
                browser_class = self._playwright.chromium
                logger.warning(f"未知瀏覽器類型: {self.browser_type}，使用默認 chromium")
            
            # 啟動瀏覽器
            self._browser = browser_class.launch(
                headless=self.headless,
                args=self.args,
                slow_mo=self.slow_mo
            )
            
            # 處理上下文選項
            context_options = {
                'viewport': self.viewport,
                'ignore_https_errors': self.ignore_https_errors
            }
            
            # 處理 storage_state（支持字符串路徑或直接的狀態對象）
            if self.storage_state:
                if isinstance(self.storage_state, str):
                    # 檢查檔案是否存在且有效
                    if os.path.exists(self.storage_state):
                        try:
                            # 嘗試載入並驗證 JSON
                            with open(self.storage_state, 'r', encoding='utf-8') as f:
                                import json
                                content = f.read().strip()
                                if content:
                                    json.loads(content)  # 僅驗證格式
                                    context_options['storage_state'] = self.storage_state
                                else:
                                    logger.warning(f"儲存狀態檔案 {self.storage_state} 是空的")
                        except json.JSONDecodeError as e:
                            logger.warning(f"儲存狀態檔案 {self.storage_state} 格式錯誤: {str(e)}")
                        except Exception as e:
                            logger.warning(f"讀取儲存狀態檔案 {self.storage_state} 時發生錯誤: {str(e)}")
                    else:
                        logger.warning(f"存儲狀態檔案 {self.storage_state} 不存在")
                elif isinstance(self.storage_state, dict):
                    # 直接使用提供的狀態對象
                    context_options['storage_state'] = self.storage_state
            
            if self.user_agent:
                context_options['user_agent'] = self.user_agent
                
            if self.proxy:
                context_options['proxy'] = self.proxy
            
            # 創建瀏覽器上下文
            self._context = self._browser.new_context(**context_options)
            
            # 創建頁面
            self._page = self._context.new_page()
            self._pages = [self._page]
            
            logger.info("瀏覽器啟動成功！")
            return self
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON 解析錯誤: {str(e)}"
            details = {"file": self.storage_state if isinstance(self.storage_state, str) else "直接傳入的狀態對象"}
            logger.error(error_msg)
            self.close()  # 確保資源被釋放
            raise BrowserException(error_msg, e, details)
        except Exception as e:
            logger.error(f"啟動瀏覽器時發生錯誤: {str(e)}")
            self.close()  # 確保資源被釋放
            raise BrowserException(f"啟動瀏覽器失敗: {str(e)}")
    
    def close(self) -> None:
        """
        關閉瀏覽器和釋放資源。
        """
        # 關閉所有定時器
        for timer in self._timers:
            if timer and timer.is_alive():
                timer.cancel()
        self._timers = []
        
        # 關閉上下文
        if self._context and not self._context.is_closed():
            logger.info("關閉瀏覽器上下文...")
            try:
                self._context.close()
            except Exception as e:
                logger.error(f"關閉上下文時發生錯誤: {str(e)}")
        
        # 關閉瀏覽器
        if self._browser:
            logger.info("關閉瀏覽器...")
            try:
                self._browser.close()
            except Exception as e:
                logger.error(f"關閉瀏覽器時發生錯誤: {str(e)}")
        
        # 關閉 playwright
        if self._playwright:
            logger.info("關閉 Playwright...")
            try:
                self._playwright.stop()
            except Exception as e:
                logger.error(f"關閉 Playwright 時發生錯誤: {str(e)}")
        
        # 重置變數
        self._page = None
        self._pages = []
        self._context = None
        self._browser = None
        self._playwright = None
        
        logger.info("所有資源已釋放")
    
    def goto(self, url: str, timeout: int = 30000, wait_until: str = "domcontentloaded") -> Optional[Response]:
        """
        導航到指定 URL。

        參數:
            url (str): 要訪問的 URL。
            timeout (int): 導航超時時間（毫秒）。
            wait_until (str): 導航完成的條件，可選值: 'load', 'domcontentloaded', 'networkidle', 'commit'。
        
        返回:
            Optional[Response]: 返回響應對象，若導航失敗則返回 None。
        
        異常:
            NavigationException: 導航失敗時拋出。
        """
        if not self._page:
            raise NavigationException("頁面未初始化，請先調用 start() 方法")
        
        logger.info(f"正在訪問: {url}")
        try:
            response = self._page.goto(url, timeout=timeout, wait_until=wait_until)
            if response:
                logger.info(f"頁面狀態碼: {response.status}")
                if response.status >= 400:
                    logger.warning(f"頁面返回錯誤狀態碼: {response.status}")
            return response
        except TimeoutError as e:
            logger.warning(f"導航超時 ({timeout}ms): {str(e)}")
            return None
        except Exception as e:
            logger.error(f"導航到 {url} 時發生錯誤: {str(e)}")
            raise NavigationException(f"導航失敗: {str(e)}")
    
    def wait_for_load_state(self, state: str = "networkidle", timeout: int = 30000) -> None:
        """
        等待頁面達到指定加載狀態。

        參數:
            state (str): 加載狀態，可選值: 'load', 'domcontentloaded', 'networkidle'。
            timeout (int): 超時時間（毫秒）。
        
        異常:
            TimeoutException: 等待超時時拋出。
        """
        if not self._page:
            raise NavigationException("頁面未初始化，請先調用 start() 方法")
        
        logger.info(f"等待頁面達到 {state} 狀態...")
        try:
            self._page.wait_for_load_state(state, timeout=timeout)
            logger.info(f"頁面已達到 {state} 狀態")
        except TimeoutError:
            logger.warning(f"等待 {state} 狀態超時 ({timeout}ms)")
            raise TimeoutException(f"等待頁面 {state} 狀態超時")
        except Exception as e:
            logger.error(f"等待頁面狀態時發生錯誤: {str(e)}")
            raise NavigationException(f"等待頁面狀態失敗: {str(e)}")
    
    def screenshot(self, path: str = None, full_page: bool = True) -> bytes:
        """
        截取當前頁面截圖。

        參數:
            path (str): 保存截圖的路徑，若為 None，則只返回圖像數據不保存。
            full_page (bool): 是否截取整個頁面，而非僅可見區域。
        
        返回:
            bytes: 截圖的二進制數據。
        """
        if not self._page:
            raise NavigationException("頁面未初始化，請先調用 start() 方法")
            
        if path:
            directory = os.path.dirname(path)
            if (directory and not os.path.exists(directory)):
                os.makedirs(directory)
            logger.info(f"截取頁面截圖並保存到: {path}")
        else:
            logger.info("截取頁面截圖但不保存")
        
        return self._page.screenshot(path=path, full_page=full_page)
    
    def enable_stealth_mode(self) -> None:
        """
        啟用隱身模式，減少特徵指紋。
        此方法通過注入腳本模擬常規瀏覽器行為，
        隱藏自動化特徵。
        """
        if not self._page or self._is_stealth_mode_enabled:
            return
            
        logger.info("啟用隱身模式...")
        try:
            # 注入基礎反檢測腳本
            self._page.add_init_script("""
                // 修補 navigator
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
                
                // 修補 plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => {
                        return [
                            {
                                0: {
                                    type: "application/pdf",
                                    suffixes: "pdf",
                                    description: "Portable Document Format"
                                },
                                name: "PDF Viewer",
                                filename: "internal-pdf-viewer",
                                description: "Portable Document Format"
                            }
                        ];
                    }
                });
                
                // 修補 languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-TW', 'zh', 'en-US', 'en'],
                });
                
                // 隱藏自動化特徵
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
                );
                
                // 模擬正常的歷史記錄長度
                Object.defineProperty(history, 'length', {
                    get: () => 2 + Math.floor(Math.random() * 3)
                });
            """)
            
            self._is_stealth_mode_enabled = True
            logger.info("隱身模式已啟用")
        except Exception as e:
            logger.error(f"啟用隱身模式時發生錯誤: {str(e)}")
    
    def save_storage(self, path: str = "storage.json") -> None:
        """
        保存當前瀏覽器會話狀態（cookies 和存儲）。

        參數:
            path (str): 保存狀態的檔案路徑。
        """
        if not self._context:
            logger.warning("無法保存存儲狀態：瀏覽器上下文未初始化")
            return
            
        try:
            logger.info(f"正在保存存儲狀態到: {path}")
            self._context.storage_state(path=path)
            logger.info(f"存儲狀態已保存到: {path}")
        except Exception as e:
            logger.error(f"保存存儲狀態時發生錯誤: {str(e)}")
    
    def load_storage(self, path: str = "storage.json") -> bool:
        """
        從檔案載入瀏覽器會話狀態（cookies 和存儲）。

        參數:
            path (str): 存儲狀態檔案路徑。
            
        返回:
            bool: 載入是否成功。
        """
        if not os.path.exists(path):
            logger.warning(f"存儲狀態檔案不存在: {path}")
            return False
            
        if not self._context:
            logger.warning("無法載入存儲狀態：瀏覽器上下文未初始化")
            return False
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                storage_state = json.load(f)
            
            logger.info(f"正在從 {path} 載入存儲狀態...")
            self._context.add_cookies(storage_state.get('cookies', []))
            logger.info(f"已載入 {len(storage_state.get('cookies', []))} 個 cookies")
            return True
        except Exception as e:
            logger.error(f"載入存儲狀態時發生錯誤: {str(e)}")
            return False
    
    def random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0) -> float:
        """
        隨機延遲一段時間，用於模擬人類行為。

        參數:
            min_delay (float): 最小延遲時間（秒）。
            max_delay (float): 最大延遲時間（秒）。
            
        返回:
            float: 實際延遲時間（秒）。
        """
        delay = random.uniform(min_delay, max_delay)
        logger.debug(f"隨機延遲 {delay:.2f} 秒")
        time.sleep(delay)
        return delay
    
    def register_page_event_handlers(self) -> None:
        """
        註冊頁面事件處理器，監控頁面創建和關閉。
        """
        if not self._context:
            logger.warning("無法註冊頁面事件處理器：瀏覽器上下文未初始化")
            return
            
        try:
            # 監聽頁面創建事件
            self._context.on("page", lambda page: self._on_page_created(page))
            
            # 定期檢查並管理頁面
            def check_pages():
                try:
                    pages_count = len(self._context.pages) if self._context else 0
                    logger.info(f"定期檢查: 目前有 {pages_count} 個頁面開啟")
                    if pages_count > 3:  # 如果超過閾值，執行清理
                        self.manage_pages()
                    
                    # 重新設置定時器，實現循環檢查
                    if self._context and not self._context.is_closed():
                        threading_timer = threading.Timer(30.0, check_pages)
                        threading_timer.daemon = True
                        threading_timer.start()
                        self._timers.append(threading_timer)
                except Exception as e:
                    logger.error(f"定期檢查頁面時發生錯誤: {str(e)}")
            
            # 啟動第一次檢查
            threading_timer = threading.Timer(30.0, check_pages)
            threading_timer.daemon = True
            threading_timer.start()
            self._timers.append(threading_timer)
            
            logger.info("已註冊頁面事件處理器")
            
        except Exception as e:
            logger.error(f"註冊頁面事件處理器時發生錯誤: {str(e)}")
    
    def _on_page_created(self, page: Page) -> None:
        """
        頁面創建時的回調函數。
        
        參數:
            page (Page): 新創建的頁面對象。
        """
        url = page.url
        logger.info(f"檢測到新頁面創建: {url}")
        self._pages.append(page)
    
    def manage_pages(self) -> None:
        """
        管理頁面數量，防止頁面無限增長。
        如果有太多頁面，關閉除了主頁面外的所有頁面。
        """
        if not self._context:
            return
            
        try:
            pages = self._context.pages
            # 若有多個頁面，保留主頁面和最近創建的兩個頁面
            if len(pages) > 3:
                logger.warning(f"檢測到過多頁面 ({len(pages)})，進行清理...")
                keep_pages = pages[:1] + pages[-2:] if len(pages) > 3 else pages
                for p in pages:
                    if p not in keep_pages and not p.is_closed():
                        try:
                            url = p.url
                            p.close()
                            logger.info(f"已關閉多餘頁面: {url}")
                        except Exception as e:
                            logger.warning(f"關閉頁面時發生錯誤: {str(e)}")
                
                # 更新內部頁面列表
                self._pages = [p for p in self._context.pages if not p.is_closed()]
                logger.info(f"頁面清理完成，當前共有 {len(self._pages)} 個頁面")
        except Exception as e:
            logger.error(f"管理頁面時發生錯誤: {str(e)}")
    
    def close_pages(self, keep_main: bool = True) -> None:
        """
        關閉所有分頁，可選保留主分頁。

        參數:
            keep_main (bool): 是否保留主分頁。
        """
        if not self._context:
            return
            
        try:
            pages = self._context.pages
            for i, p in enumerate(pages):
                if i == 0 and keep_main:
                    continue
                if not p.is_closed():
                    try:
                        url = p.url
                        p.close()
                        logger.info(f"已關閉頁面: {url}")
                    except Exception as e:
                        logger.warning(f"關閉頁面時發生錯誤: {str(e)}")
            
            # 更新內部頁面列表
            self._pages = [p for p in self._context.pages if not p.is_closed()]
            logger.info(f"頁面清理完成，當前共有 {len(self._pages)} 個頁面")
        except Exception as e:
            logger.error(f"關閉頁面時發生錯誤: {str(e)}")
            
    def __enter__(self):
        """
        支持上下文管理器協議，進入時啟動瀏覽器。
        """
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        支持上下文管理器協議，退出時關閉瀏覽器。
        """
        self.close()
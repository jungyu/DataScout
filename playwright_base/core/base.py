from typing import Optional, Dict, Any, Callable, Union, List
import asyncio
import random
import time
from pathlib import Path
import logging
import json
import os
from datetime import datetime

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Response,
    Request,
    Route,
    ElementHandle,
)
from loguru import logger
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import Playwright, sync_playwright

from ..config.settings import (
    BROWSER_CONFIG,
    PROXY_CONFIG,
    ANTI_DETECTION_CONFIG,
    REQUEST_INTERCEPT_CONFIG,
    TIMEOUT_CONFIG,
    RETRY_CONFIG,
)
from ..utils.exceptions import PlaywrightBaseException, BrowserException, PageException, ElementException, CaptchaException, StorageException
from ..anti_detection.user_agent import UserAgentManager
from ..anti_detection.human_like import HumanLikeBehavior
from ..anti_detection.proxy_manager import ProxyManager
from ..storage.storage_manager import StorageManager
from ..utils.logger import setup_logger
from .stealth import inject_stealth_js
from .cookie_utils import add_initial_cookies
from ..anti_detection.human_like import human_scroll
from .popup_handler import check_and_handle_popup

logger = logging.getLogger(__name__)

class PlaywrightBase:
    """
    Playwright 基礎類，提供瀏覽器自動化的基本功能
    """
    
    def __init__(
        self,
        headless: bool = True,
        proxy: Optional[Dict[str, str]] = None,
        browser_type: str = "chromium",
        **kwargs
    ):
        """
        初始化 PlaywrightBase 實例
        
        Args:
            headless: 是否以無頭模式運行瀏覽器
            proxy: 代理設置，格式為 {"server": "http://proxy:port"}
            browser_type: 瀏覽器類型，支持 "chromium"、"firefox"、"webkit"
            **kwargs: 其他瀏覽器啟動參數
        """
        self.headless = headless
        self.proxy = proxy
        self.browser_type = browser_type.lower()
        self.browser_kwargs = kwargs
        
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        
        # 存儲所有打開的頁面，用於資源管理和防止頁面洩漏
        self._pages: List[Page] = []
        self._max_pages_allowed = kwargs.get("max_pages", 3)  # 設置允許的最大頁面數
        
        self.user_agent_manager = UserAgentManager()
        self.human_like = HumanLikeBehavior()
        self.request_handlers: list[Callable] = []
        self.proxy_manager = ProxyManager()
        self.captcha_manager = None
        self.storage = StorageManager(base_dir="data")

    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def start(self) -> None:
        """
        啟動瀏覽器實例
        """
        try:
            self._playwright = sync_playwright().start()
            browser_types = {
                "chromium": self._playwright.chromium,
                "firefox": self._playwright.firefox,
                "webkit": self._playwright.webkit
            }
            
            if self.browser_type not in browser_types:
                raise BrowserException(f"不支持的瀏覽器類型: {self.browser_type}")
                
            launch_kwargs = {
                "headless": self.headless,
                **self.browser_kwargs
            }
            
            # 如果瀏覽器已經啟動，先關閉它
            if self._browser:
                try:
                    self._browser.close()
                    logger.info("關閉已存在的瀏覽器實例")
                except Exception as e:
                    logger.warning(f"關閉舊瀏覽器實例時出錯: {str(e)}")
            
            # 啟動瀏覽器
            self._browser = browser_types[self.browser_type].launch(**launch_kwargs)
            context_kwargs = {}
            if self.proxy:
                context_kwargs["proxy"] = self.proxy
            
            # 管理上下文
            if self._context:
                try:
                    self._context.close()
                    logger.info("關閉已存在的瀏覽器上下文")
                except Exception as e:
                    logger.warning(f"關閉舊上下文時出錯: {str(e)}")
                finally:
                    self._context = None
                    self._page = None
                    self._pages = []
            
            # 檢查 storage.json 是否存在，不存在則不使用 storage_state
            if os.path.exists("storage.json"):
                try:
                    with open("storage.json", "r") as f:
                        storage = json.load(f)
                        self._context = self._browser.new_context(storage_state=storage, **context_kwargs)
                except Exception as e:
                    logger.warning(f"讀取儲存狀態失敗: {str(e)}，將創建新的上下文")
                    self._context = self._browser.new_context(**context_kwargs)
            else:
                # 沒有 storage.json 時，創建一個新的 context
                logger.info("未找到 storage.json，使用默認配置創建瀏覽器上下文")
                self._context = self._browser.new_context(**context_kwargs)
            
            # 創建頁面並添加到頁面列表
            self._page = self._context.new_page()
            self._pages = [self._page]
            
            # 設置事件監聽器來追蹤新開的頁面
            self._context.on("page", self._handle_new_page)
            
            # 注入頁面關閉監聽器，確保頁面列表同步更新
            self._setup_page_close_listener()
            
            # 設置請求攔截
            self._setup_request_interception()
            self._setup_auto_save_storage()

            logger.info("瀏覽器實例已啟動")
        except Exception as e:
            logger.error(f"啟動瀍覽器失敗: {str(e)}")
            raise BrowserException(f"啟動瀍覽器失敗: {str(e)}")

    def close(self) -> None:
        """
        關閉瀏覽器實例
        """
        try:
            if self._page:
                self._page.close()
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
            logger.info("瀏覽器實例已關閉")
        except Exception as e:
            logger.error(f"關閉瀏覽器時發生錯誤: {str(e)}")
            raise BrowserException(f"關閉瀏覽器失敗: {str(e)}")

    @property
    def page(self) -> Page:
        """
        獲取當前頁面實例
        
        Returns:
            Page: Playwright 頁面實例
        """
        if not self._page:
            raise PageException("頁面未初始化")
        return self._page
        
    def navigate(self, url: str, timeout: int = 30000) -> None:
        """
        導航到指定URL
        
        Args:
            url: 目標URL
            timeout: 超時時間（毫秒）
        """
        if not self._page or self._page.is_closed():
            logger.warning("頁面已關閉或未初始化，將重新創建頁面")
            try:
                if self._context:
                    # 如果上下文存在但頁面被關閉，創建新頁面
                    self._page = self._context.new_page()
                    logger.info("已重新創建頁面實例")
                else:
                    # 如果連上下文都不存在，拋出異常
                    raise BrowserException("瀏覽器上下文未初始化，請重新啟動瀏覽器")
            except Exception as e:
                logger.error(f"重新創建頁面時發生錯誤: {str(e)}")
                raise BrowserException(f"重新創建頁面失敗: {str(e)}")
        
        # 驗證 URL 格式
        if not url or not isinstance(url, str) or not (url.startswith('http://') or url.startswith('https://')):
            raise PageException(f"無效的 URL 格式: {url}")
        
        # 延遲
        if ANTI_DETECTION_CONFIG["random_delay"]:
            self.random_delay()

        # 嘗試導航
        try:
            response = self.page.goto(
                url,
                timeout=timeout,
                wait_until=BROWSER_CONFIG.get("wait_until", "load")
            )

            # 檢查響應
            if not response:
                logger.warning(f"導航到 {url} 沒有收到響應")
                # 不拋出異常，而是繼續執行，因為有些頁面可能不返回響應但實際上已加載
            elif response.status >= 400:
                # 記錄HTTP錯誤但不立即失敗
                logger.warning(f"導航到 {url} 收到錯誤狀態碼: {response.status}")
                
            logger.info(f"成功導航到 {url}")
            return
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"導航到 {url} 時發生錯誤: {error_msg}")
            
            # 特殊處理超時錯誤
            if "timeout" in error_msg.lower():
                logger.warning("導航超時，嘗試等待頁面加載完成")
                try:
                    # 即使超時也嘗試等待頁面加載
                    self.wait_for_load_state("domcontentloaded", timeout=10000)
                    logger.info("成功獲取基本頁面內容")
                    return  # 繼續執行流程
                except Exception as wait_error:
                    logger.error(f"等待頁面加載失敗: {str(wait_error)}")
                    # 這裡不拋出異常，而是跳到下面拋出原始異常
            
            raise PageException(f"導航失敗: {error_msg}", url=url)

    def get_current_url(self) -> str:
        """
        獲取當前頁面URL
        
        Returns:
            str: 當前頁面URL
        """
        return self.page.url
        
    def wait_for_load_state(self, state: str = "load", timeout: int = 30000) -> None:
        """
        等待頁面加載狀態
        
        Args:
            state: 加載狀態，可選 "load"、"domcontentloaded"、"networkidle"
            timeout: 超時時間（毫秒）
        """
        try:
            self.page.wait_for_load_state(state, timeout=timeout)
            logger.debug(f"頁面已達到 {state} 狀態")
        except Exception as e:
            logger.error(f"等待頁面加載狀態 {state} 失敗: {str(e)}")
            raise PageException(f"等待頁面加載失敗: {str(e)}")

    def add_request_handler(self, handler: Callable[[Route, Request], Any]):
        """
        添加請求處理器

        Args:
            handler: 請求處理函數
        """
        self.request_handlers.append(handler)

    def _setup_request_interception(self):
        """設置請求攔截"""
        self.page.route("**/*", self._handle_request)

    def _handle_request(self, route: Route, request: Request):
        """
        處理請求攔截
        
        Args:
            route: 路由對象
            request: 請求對象
        """
        for handler in self.request_handlers:
            try:
                handler(route, request)
                return
            except Exception as e:
                logger.error(f"請求處理失敗: {str(e)}")
        
        route.continue_()

    def random_delay(self, delay_type: str = None, min_delay: float = None, max_delay: float = None) -> None:
        """
        統一隨機延遲，支援多種延遲型態
        Args:
            delay_type: 延遲類型（如 'page', 'keyword', 'action'）
            min_delay: 覆蓋預設的最小延遲（秒）
            max_delay: 覆蓋預設的最大延遲（秒）
        """
        # 預設延遲參數
        config = {
            None: (ANTI_DETECTION_CONFIG.get("delay_min", 1), ANTI_DETECTION_CONFIG.get("delay_max", 3)),
            "page": (ANTI_DETECTION_CONFIG.get("page_delay_min", 5), ANTI_DETECTION_CONFIG.get("page_delay_max", 15)),
            "keyword": (ANTI_DETECTION_CONFIG.get("keyword_delay_min", 15), ANTI_DETECTION_CONFIG.get("keyword_delay_max", 30)),
            "action": (ANTI_DETECTION_CONFIG.get("action_delay_min", 1), ANTI_DETECTION_CONFIG.get("action_delay_max", 3)),
        }
        min_d, max_d = config.get(delay_type, config[None])
        if min_delay is not None:
            min_d = min_delay
        if max_delay is not None:
            max_d = max_delay
        delay = random.uniform(min_d, max_d)
        logger.info(f"隨機延遲 {delay:.2f} 秒 (type={delay_type or 'default'})")
        time.sleep(delay)

    def _random_delay(self):
        """
        已廢棄，請改用 random_delay
        """
        self.random_delay()

    def screenshot(
        self,
        path: Optional[str] = None,
        full_page: bool = True,
    ) -> Optional[bytes]:
        """
        截取頁面截圖
        
        Args:
            path: 保存路徑
            full_page: 是否截取整個頁面
            
        Returns:
            bytes: 如果未指定保存路徑，則返回圖片數據
        """
        try:
            return self.page.screenshot(
                path=path,
                full_page=full_page,
            )
        except Exception as e:
            logger.error(f"截圖失敗: {str(e)}")
            raise PageException(f"截圖失敗: {str(e)}")

    def evaluate(self, expression: str) -> Any:
        """
        執行 JavaScript 代碼
        
        Args:
            expression: JavaScript 表達式
            
        Returns:
            Any: JavaScript 執行結果
        """
        try:
            return self.page.evaluate(expression)
        except Exception as e:
            logger.error(f"執行 JavaScript 失敗: {str(e)}")
            raise PageException(f"執行 JavaScript 失敗: {str(e)}")

    def new_page(self) -> Page:
        """
        創建新頁面，並管理頁面計數，防止過多頁面導致資源洩漏
        
        Returns:
            Page: 新創建的頁面
        """
        if not self._context:
            raise BrowserException("瀏覽器上下文未初始化")
            
        # 檢查是否已達到最大頁面限制
        if len(self._pages) >= self._max_pages_allowed:
            logger.warning(f"已達到最大頁面數量限制 ({self._max_pages_allowed})，將關閉最舊的頁面")
            try:
                # 關閉最早創建的頁面（排除主頁面）
                for old_page in self._pages[1:]:
                    if not old_page.is_closed():
                        old_page.close()
                        logger.info(f"已關閉舊頁面: {old_page.url}")
                        break
                # 清理已關閉的頁面
                self._pages = [p for p in self._pages if not p.is_closed()]
            except Exception as e:
                logger.error(f"關閉舊頁面時發生錯誤: {str(e)}")
        
        try:
            # 創建新頁面
            page = self._context.new_page()
            # 將新頁面添加到頁面列表
            self._pages.append(page)
            logger.info(f"已創建新頁面 (當前共 {len(self._pages)} 個頁面)")
            return page
        except Exception as e:
            logger.error(f"創建新頁面失敗: {str(e)}")
            raise PageException(f"創建新頁面失敗: {str(e)}")
    
    def manage_pages(self) -> None:
        """
        管理所有打開的頁面，關閉多餘頁面並更新頁面列表
        """
        if not self._context:
            return
            
        try:
            # 獲取所有當前頁面
            all_pages = self._context.pages
            
            # 更新內部頁面列表，確保與實際頁面同步
            self._pages = [p for p in self._pages if not p.is_closed()]
            
            # 如果頁面數超過限制，關閉多餘頁面
            if len(all_pages) > self._max_pages_allowed:
                logger.warning(f"檢測到 {len(all_pages)} 個頁面，超過限制 {self._max_pages_allowed}，將關閉多餘頁面")
                
                # 保留主頁面和最新的頁面
                pages_to_keep = [self._page] + all_pages[-(self._max_pages_allowed-1):] if len(all_pages) > 1 else [self._page]
                pages_to_keep = [p for p in pages_to_keep if p and not p.is_closed()]
                
                # 關閉不需要保留的頁面
                for page in all_pages:
                    if page not in pages_to_keep and not page.is_closed():
                        try:
                            page.close()
                            logger.info(f"已關閉多餘頁面: {page.url}")
                        except Exception as e:
                            logger.error(f"關閉頁面時發生錯誤: {str(e)}")
                
                # 更新頁面列表
                self._pages = [p for p in self._context.pages if not p.is_closed()]
                logger.info(f"頁面管理完成，當前共 {len(self._pages)} 個頁面")
        except Exception as e:
            logger.error(f"管理頁面時發生錯誤: {str(e)}")
    
    def close_pages(self, keep_main: bool = True) -> None:
        """
        關閉所有頁面，可選保留主頁面
        
        Args:
            keep_main: 是否保留主頁面
        """
        if not self._context:
            return
            
        try:
            # 獲取所有當前頁面
            pages = self._context.pages
            
            for page in pages:
                # 如果是主頁面且需要保留，則跳過
                if keep_main and page == self._page:
                    continue
                    
                try:
                    if not page.is_closed():
                        url = page.url
                        page.close()
                        logger.info(f"已關閉頁面: {url}")
                except Exception as e:
                    logger.warning(f"關閉頁面時發生錯誤: {str(e)}")
            
            # 更新頁面列表
            self._pages = [self._page] if keep_main and self._page and not self._page.is_closed() else []
            logger.info(f"已關閉所有頁面" + (" (已保留主頁面)" if keep_main else ""))
            
        except Exception as e:
            logger.error(f"關閉頁面時發生錯誤: {str(e)}")
            
    def pdf(
        self,
        path: str,
        format: str = "A4",
        landscape: bool = False,
    ) -> None:
        """
        生成頁面 PDF
        
        Args:
            path: PDF 保存路徑
            format: 紙張格式
            landscape: 是否橫向
        """
        try:
            self.page.pdf(
                path=path,
                format=format,
                landscape=landscape,
            )
            logger.info(f"PDF 已保存至: {path}")
        except Exception as e:
            logger.error(f"生成 PDF 失敗: {str(e)}")
            raise PageException(f"生成 PDF 失敗: {str(e)}")

    def solve_recaptcha(
        self,
        frame_selector: str = "iframe[title*='reCAPTCHA']",
        timeout: int = 30000,
    ) -> bool:
        """
        解決 reCAPTCHA 驗證碼
        
        Args:
            frame_selector: iframe 選擇器
            timeout: 超時時間（毫秒）
            
        Returns:
            bool: 是否成功
        """
        try:
            frame = self.page.frame(frame_selector)
            if not frame:
                logger.error("未找到 reCAPTCHA iframe")
                return False
                
            checkbox = frame.locator(".recaptcha-checkbox-border")
            checkbox.click()
            
            # 等待驗證完成
            frame.wait_for_selector(
                ".recaptcha-checkbox-checked",
                timeout=timeout
            )
            
            return True
        except Exception as e:
            logger.error(f"解決 reCAPTCHA 失敗: {str(e)}")
            return False
            
    def solve_hcaptcha(
        self,
        frame_selector: str = "iframe[title*='hCaptcha']",
        timeout: int = 30000,
    ) -> bool:
        """
        解決 hCaptcha 驗證碼
        
        Args:
            frame_selector: iframe 選擇器
            timeout: 超時時間（毫秒）
            
        Returns:
            bool: 是否成功
        """
        try:
            frame = self.page.frame(frame_selector)
            if not frame:
                logger.error("未找到 hCaptcha iframe")
                return False
                
            checkbox = frame.locator(".checkbox")
            checkbox.click()
            
            # 等待驗證完成
            frame.wait_for_selector(
                ".checkbox.checked",
                timeout=timeout
            )
            
            return True
        except Exception as e:
            logger.error(f"解決 hCaptcha 失敗: {str(e)}")
            return False
            
    def solve_slider_captcha(
        self,
        slider_selector: str,
        background_selector: str,
        timeout: int = 30000,
    ) -> bool:
        """
        解決滑塊驗證碼
        
        Args:
            slider_selector: 滑塊選擇器
            background_selector: 背景圖選擇器
            timeout: 超時時間（毫秒）
            
        Returns:
            bool: 是否成功
        """
        try:
            slider = self.page.locator(slider_selector)
            background = self.page.locator(background_selector)
            
            # 獲取滑塊和背景圖的位置信息
            slider_box = slider.bounding_box()
            background_box = background.bounding_box()
            
            if not slider_box or not background_box:
                logger.error("無法獲取滑塊或背景圖位置信息")
                return False
            
            # 模擬人工滑動
            self.page.mouse.move(
                slider_box["x"] + slider_box["width"] / 2,
                slider_box["y"] + slider_box["height"] / 2
            )
            self.page.mouse.down()
            
            # 隨機速度移動到目標位置
            current_x = slider_box["x"]
            target_x = background_box["x"] + background_box["width"]
            
            while current_x < target_x:
                move_x = min(
                    random.randint(5, 20),
                    target_x - current_x
                )
                current_x += move_x
                
                self.page.mouse.move(
                    current_x,
                    slider_box["y"] + random.randint(-2, 2)
                )
                time.sleep(random.uniform(0.01, 0.05))
            
            self.page.mouse.up()
            return True
            
        except Exception as e:
            logger.error(f"解決滑塊驗證碼失敗: {str(e)}")
            return False

    def save_data(
        self,
        data: Any,
        filename: str,
        format: str = "json",
        **kwargs,
    ) -> str:
        """
        保存數據

        Args:
            data: 要保存的數據
            filename: 文件名
            format: 保存格式 (json/csv/excel/raw)
            **kwargs: 其他參數

        Returns:
            str: 保存的文件路徑
        """
        try:
            if format == "json":
                return self.storage.save_json(data, filename, **kwargs)
            elif format == "csv":
                return self.storage.save_csv(data, filename, **kwargs)
            elif format == "excel":
                return self.storage.save_excel(data, filename, **kwargs)
            elif format == "raw":
                return self.storage.save_raw(data, filename, **kwargs)
            else:
                raise StorageException(f"不支持的保存格式: {format}")
        except Exception as e:
            raise CaptchaException(f"解決 hCaptcha 失敗: {str(e)}")

    def save_storage(self, file_path: str) -> None:
        """
        保存儲存狀態
        
        Args:
            file_path: 文件路徑
        """
        if not self.page:
            raise PageException("頁面未創建")
            
        try:
            # 儲存狀態
            storage = self._context.storage_state()
            with open("storage.json", "w") as f:
                json.dump(storage, f)
                
            self.storage_state = storage
            logger.info(f"儲存狀態已保存到: {file_path}")
        except Exception as e:
            logger.error(f"保存儲存狀態失敗: {str(e)}")
            raise StorageException(f"保存儲存狀態失敗: {str(e)}")
            
    def load_storage(self, file_path: str) -> None:
        """
        載入儲存狀態
        
        Args:
            file_path: 文件路徑
        """
        try:
            # 檢查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"儲存狀態文件不存在: {file_path}")
                
            # 讀取文件
            with open(file_path, "r", encoding="utf-8") as f:
                storage = json.load(f)
                
            # 設置儲存狀態
            if self.page:
                self.page.context.add_cookies(storage.get("cookies", []))
                
            self.storage_state = storage
            logger.info(f"已載入儲存狀態: {file_path}")
        except Exception as e:
            logger.error(f"載入儲存狀態失敗: {str(e)}")
            raise StorageException(f"載入儲存狀態失敗: {str(e)}")
            
    def clear_storage(self) -> None:
        """清除儲存狀態"""
        try:
            if self.page:
                self.page.context.clear_cookies()
            self.storage_state = None
            logger.info("已清除儲存狀態")
        except Exception as e:
            logger.error(f"清除儲存狀態失敗: {str(e)}")
            raise StorageException(f"清除儲存狀態失敗: {str(e)}")

    def _setup_auto_save_storage(self) -> None:
        """
        自動儲存 cookie 與 session 狀態，當有變動時即時保存
        """
        if not self._context:
            return
        def on_storage_change(event=None):
            try:
                storage = self._context.storage_state()
                with open("storage.json", "w", encoding="utf-8") as f:
                    json.dump(storage, f, ensure_ascii=False, indent=2)
                logger.info("自動儲存 storage 狀態完成")
            except Exception as e:
                logger.error(f"自動儲存 storage 狀態失敗: {str(e)}")
        # 綁定事件
        self._context.on("request", on_storage_change)
        self._context.on("response", on_storage_change)
        self._context.on("close", on_storage_change)

    def enable_stealth_mode(self) -> None:
        """
        啟用隱身模式，注入反自動化與指紋偽裝腳本
        """
        if self._context:
            inject_stealth_js(self._context)

    def add_initial_cookies(self, cookies: list[dict]) -> None:
        """
        批量設置初始 Cookie
        Args:
            cookies: Cookie 字典列表
        """
        if self._context:
            add_initial_cookies(self._context, cookies)

    def human_scroll(self, min_times: int = 3, max_times: int = 8, min_dist: int = 300, max_dist: int = 700, sleep_min: float = 0.5, sleep_max: float = 2.0) -> None:
        """
        模擬人類隨機平滑滾動頁面
        Args:
            min_times: 最少滾動次數
            max_times: 最多滾動次數
            min_dist: 每次最小滾動距離
            max_dist: 每次最大滾動距離
            sleep_min: 每次滾動後最小等待秒數
            sleep_max: 每次滾動後最大等待秒數
        """
        if self.page:
            human_scroll(self.page, min_times, max_times, min_dist, max_dist, sleep_min, sleep_max)

    def check_and_handle_popup(self, selectors: dict) -> bool:
        """
        檢查並處理常見付費牆、cookie banner、彈窗
        Args:
            selectors: dict，格式如 {'cookie': [...], 'popup': [...], 'paywall': [...]}
        Returns:
            bool: 是否有成功自動處理
        """
        if self.page:
            return check_and_handle_popup(self.page, selectors)
        return False

    def _handle_new_page(self, page: Page) -> None:
        """
        處理新頁面創建事件
        
        Args:
            page: 新創建的頁面
        """
        try:
            logger.info(f"檢測到新頁面被創建: {page.url}")
            
            # 添加到頁面列表
            self._pages.append(page)
            
            # 設置頁面關閉監聽器
            page.on("close", lambda: self._handle_page_close(page))
            
            # 如果超過最大頁面限制，關閉最舊的頁面
            if len(self._pages) > self._max_pages_allowed:
                logger.warning(f"頁面數量 ({len(self._pages)}) 超過限制 ({self._max_pages_allowed})，將關閉最舊頁面")
                oldest_pages = [p for p in self._pages[1:] if p != page and not p.is_closed()]
                if oldest_pages:
                    oldest_page = oldest_pages[0]
                    try:
                        url = oldest_page.url
                        oldest_page.close()
                        logger.info(f"已關閉最舊頁面: {url}")
                    except Exception as e:
                        logger.error(f"關閉舊頁面時發生錯誤: {str(e)}")
        except Exception as e:
            logger.error(f"處理新頁面事件時發生錯誤: {str(e)}")
            
    def _handle_page_close(self, page: Page) -> None:
        """
        處理頁面關閉事件
        
        Args:
            page: 被關閉的頁面
        """
        try:
            # 從頁面列表移除
            if page in self._pages:
                self._pages.remove(page)
                logger.info(f"頁面已關閉並從列表中移除，當前剩餘 {len(self._pages)} 個頁面")
        except Exception as e:
            logger.error(f"處理頁面關閉事件時發生錯誤: {str(e)}")
            
    def _setup_page_close_listener(self) -> None:
        """
        設置所有頁面的關閉事件監聽器
        """
        try:
            for page in self._pages:
                if not page.is_closed():
                    page.on("close", lambda: self._handle_page_close(page))
        except Exception as e:
            logger.error(f"設置頁面關閉監聽器時發生錯誤: {str(e)}")
            
    def get_page_count(self) -> int:
        """
        獲取當前打開的頁面數量
        
        Returns:
            int: 頁面數量
        """
        if not self._context:
            return 0
            
        try:
            # 更新頁面列表，確保與實際頁面同步
            self._pages = [p for p in self._pages if not p.is_closed()]
            
            # 獲取上下文中的所有頁面
            context_pages = self._context.pages
            
            # 確保內部列表與上下文頁面同步
            if len(context_pages) != len(self._pages):
                logger.warning(f"頁面列表與上下文不同步: 內部={len(self._pages)}, 上下文={len(context_pages)}")
                self._pages = [p for p in context_pages if not p.is_closed()]
            
            return len(self._pages)
        except Exception as e:
            logger.error(f"獲取頁面數量時發生錯誤: {str(e)}")
            return len(self._pages) if self._pages else 0
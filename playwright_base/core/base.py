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
            
            self._browser = browser_types[self.browser_type].launch(**launch_kwargs)
            context_kwargs = {}
            if self.proxy:
                context_kwargs["proxy"] = self.proxy
                
            self._context = self._browser.new_context(**context_kwargs)
            self._page = self._context.new_page()
            
            # 設置請求攔截
            self._setup_request_interception()

            logger.info("瀏覽器實例已啟動")
        except Exception as e:
            logger.error(f"啟動瀏覽器時發生錯誤: {str(e)}")
            raise BrowserException(f"啟動瀏覽器失敗: {str(e)}")

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
        try:
            if ANTI_DETECTION_CONFIG["random_delay"]:
                self._random_delay()

            response = self.page.goto(
                url,
                timeout=timeout,
            )

            if not response:
                raise PlaywrightBaseException(f"導航到 {url} 失敗")

            if response.status >= 400:
                raise PlaywrightBaseException(
                    f"導航到 {url} 失敗，狀態碼: {response.status}"
                )

            logger.info(f"成功導航到 {url}")
        except Exception as e:
            logger.error(f"導航到 {url} 時發生錯誤: {str(e)}")
            raise PageException(f"導航失敗: {str(e)}")

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

    def _random_delay(self):
        """
        實現隨機延遲以模擬人類行為
        
        延遲時間範圍由配置的 delay_min 和 delay_max 決定
        只有在 random_delay 配置為 True 時才執行延遲
        """
        if not ANTI_DETECTION_CONFIG.get("random_delay", False):
            return
            
        delay = random.uniform(
            ANTI_DETECTION_CONFIG.get("delay_min", 1),
            ANTI_DETECTION_CONFIG.get("delay_max", 3),
        )
        logger.debug(f"隨機延遲 {delay:.2f} 秒")
        time.sleep(delay)



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
        創建新頁面
        
        Returns:
            Page: 新創建的頁面
        """
        if not self._context:
            raise BrowserException("瀏覽器上下文未初始化")
        try:
            page = self._context.new_page()
            logger.info("已創建新頁面")
            return page
        except Exception as e:
            logger.error(f"創建新頁面失敗: {str(e)}")
            raise PageException(f"創建新頁面失敗: {str(e)}")

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
            # 獲取儲存狀態
            storage = self.page.context.storage_state()
            
            # 創建目錄
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 保存到文件
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(storage, f, ensure_ascii=False, indent=2)
                
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
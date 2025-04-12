#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
瀏覽器工具模組

提供瀏覽器操作相關的工具函數，包括元素等待、點擊、滾動、截圖、頁面源碼保存等功能。
"""

import os
import time
import random
import logging
import psutil
from datetime import datetime
from typing import Optional, Union, List, Dict, Any, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    StaleElementReferenceException, ElementClickInterceptedException,
    WebDriverException
)

from .data_processor import SimpleDataProcessor
from .path_utils import PathUtils

class BrowserUtils:
    """瀏覽器工具類，提供常用的瀏覽器操作功能"""
    
    def __init__(
        self,
        driver: Optional[webdriver.Remote] = None,
        config: Optional[Dict] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化瀏覽器工具類
        
        Args:
            driver: WebDriver實例
            config: 配置字典
            logger: 日誌記錄器
        """
        self.driver = driver
        self.config = config or {}
        
        # 初始化日誌記錄器
        if logger:
            self.logger = logger
        else:
            from src.core.utils.logger import setup_logger
            self.logger = setup_logger(
                name=__name__,
                level_name="INFO",
                log_dir="logs",
                log_file="browser.log",
                console_output=True,
                file_output=True
            )
        
        # 初始化其他工具類
        self.data_processor = SimpleDataProcessor(self.logger)
        self.path_utils = PathUtils(self.logger)
        
        # 性能監控相關
        self.performance_stats = {
            'start_time': datetime.now(),
            'page_loads': 0,
            'total_load_time': 0,
            'errors': 0
        }
        
    def set_driver(self, driver: webdriver.Remote) -> None:
        """
        設置WebDriver實例
        
        Args:
            driver: WebDriver實例
        """
        self.driver = driver
        self.logger.info("WebDriver已更新")
        
    def wait_for_element(
        self,
        by: By,
        selector: str,
        timeout: int = 10,
        parent: Optional[WebElement] = None,
        clickable: bool = False
    ) -> Optional[WebElement]:
        """
        等待元素出現
        
        Args:
            by: 定位方式
            selector: 選擇器
            timeout: 超時時間(秒)
            parent: 父元素
            clickable: 是否等待元素可點擊
            
        Returns:
            找到的元素，如果超時則返回None
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化")
            return None
            
        try:
            wait = WebDriverWait(self.driver, timeout)
            if parent:
                if clickable:
                    return wait.until(EC.element_to_be_clickable((by, selector)), parent)
                return wait.until(EC.presence_of_element_located((by, selector)), parent)
            else:
                if clickable:
                    return wait.until(EC.element_to_be_clickable((by, selector)))
                return wait.until(EC.presence_of_element_located((by, selector)))
        except TimeoutException:
            self.logger.warning(f"等待元素超時: {by}={selector}")
            return None
        except Exception as e:
            self.logger.error(f"等待元素出錯: {str(e)}")
            return None
            
    def wait_for_elements(
        self,
        by: By,
        selector: str,
        timeout: int = 10,
        parent: Optional[WebElement] = None
    ) -> List[WebElement]:
        """
        等待多個元素出現
        
        Args:
            by: 定位方式
            selector: 選擇器
            timeout: 超時時間(秒)
            parent: 父元素
            
        Returns:
            找到的元素列表
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化")
            return []
            
        try:
            wait = WebDriverWait(self.driver, timeout)
            if parent:
                return wait.until(EC.presence_of_all_elements_located((by, selector)), parent)
            return wait.until(EC.presence_of_all_elements_located((by, selector)))
        except TimeoutException:
            self.logger.warning(f"等待元素超時: {by}={selector}")
            return []
        except Exception as e:
            self.logger.error(f"等待元素出錯: {str(e)}")
            return []
            
    def safe_click(self, element: WebElement, retries: int = 3) -> bool:
        """
        安全點擊元素
        
        Args:
            element: 要點擊的元素
            retries: 重試次數
            
        Returns:
            是否點擊成功
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化")
            return False
            
        for attempt in range(retries):
            try:
                # 檢查元素是否可見
                if not element.is_displayed():
                    self.logger.warning("元素不可見，無法點擊")
                    return False
                    
                # 捲動到元素位置
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.3)
                
                # 等待元素可點擊
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(element))
                
                # 嘗試普通點擊
                try:
                    element.click()
                    return True
                except ElementClickInterceptedException:
                    self.logger.debug("元素點擊被攔截，嘗試JavaScript點擊")
                except Exception as e:
                    self.logger.debug(f"常規點擊失敗: {str(e)}，嘗試JavaScript點擊")
                    
                # 使用JavaScript點擊
                self.driver.execute_script("arguments[0].click();", element)
                return True
                
            except Exception as e:
                self.logger.warning(f"點擊元素失敗 (嘗試 {attempt + 1}/{retries}): {str(e)}")
                if attempt < retries - 1:
                    time.sleep(0.5)
                    
        return False
        
    def is_element_enabled(self, element: WebElement) -> bool:
        """
        檢查元素是否啟用
        
        Args:
            element: 要檢查的元素
            
        Returns:
            元素是否啟用
        """
        try:
            return element.is_enabled()
        except Exception as e:
            self.logger.error(f"檢查元素狀態失敗: {str(e)}")
            return False
            
    def get_element_text(self, element: WebElement) -> str:
        """
        獲取元素文本
        
        Args:
            element: 要獲取文本的元素
            
        Returns:
            元素文本
        """
        try:
            return element.text.strip()
        except Exception as e:
            self.logger.error(f"獲取元素文本失敗: {str(e)}")
            return ""
            
    def get_element_attribute(self, element: WebElement, attribute: str) -> str:
        """
        獲取元素屬性
        
        Args:
            element: 要獲取屬性的元素
            attribute: 屬性名稱
            
        Returns:
            屬性值
        """
        try:
            return element.get_attribute(attribute)
        except Exception as e:
            self.logger.error(f"獲取元素屬性失敗: {str(e)}")
            return ""
            
    def scroll_to_element(self, element: WebElement, offset: int = 0) -> bool:
        """
        捲動到元素位置
        
        Args:
            element: 要捲動到的元素
            offset: 偏移量
            
        Returns:
            是否捲動成功
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化")
            return False
            
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                element
            )
            if offset:
                self.driver.execute_script(f"window.scrollBy(0, {offset});")
            return True
        except Exception as e:
            self.logger.error(f"捲動到元素失敗: {str(e)}")
            return False
            
    def take_screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        """
        截取頁面截圖
        
        Args:
            filename: 截圖文件名
            
        Returns:
            截圖文件路徑
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化")
            return None
            
        try:
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"screenshot_{timestamp}.png"
                
            screenshot_dir = self.path_utils.get_screenshot_dir()
            filepath = os.path.join(screenshot_dir, filename)
            
            self.driver.save_screenshot(filepath)
            self.logger.info(f"已保存截圖: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"截圖失敗: {str(e)}")
            return None
            
    def save_page_source(self, filename: Optional[str] = None) -> Optional[str]:
        """
        保存頁面源碼
        
        Args:
            filename: 文件名
            
        Returns:
            文件路徑
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化")
            return None
            
        try:
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"page_source_{timestamp}.html"
                
            debug_dir = self.path_utils.get_debug_dir()
            filepath = os.path.join(debug_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
                
            self.logger.info(f"已保存頁面源碼: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"保存頁面源碼失敗: {str(e)}")
            return None
            
    def get_browser_info(self) -> Dict[str, Any]:
        """
        獲取瀏覽器信息
        
        Returns:
            瀏覽器信息
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化")
            return {}
            
        try:
            return {
                'browser_name': self.driver.name,
                'browser_version': self.driver.capabilities.get('browserVersion'),
                'platform': self.driver.capabilities.get('platformName'),
                'window_size': self.driver.get_window_size(),
                'user_agent': self.driver.execute_script("return navigator.userAgent")
            }
        except Exception as e:
            self.logger.error(f"獲取瀏覽器信息失敗: {str(e)}")
            return {}
            
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        獲取性能統計信息
        
        Returns:
            性能統計信息
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化")
            return {}
            
        try:
            # 獲取瀏覽器進程信息
            process = psutil.Process(self.driver.service.process.pid)
            memory_info = process.memory_info()
            
            # 計算運行時間
            runtime = (datetime.now() - self.performance_stats['start_time']).total_seconds()
            
            # 計算平均頁面加載時間
            avg_load_time = (
                self.performance_stats['total_load_time'] / 
                self.performance_stats['page_loads']
                if self.performance_stats['page_loads'] > 0 else 0
            )
            
            return {
                'runtime': runtime,
                'page_loads': self.performance_stats['page_loads'],
                'avg_load_time': avg_load_time,
                'errors': self.performance_stats['errors'],
                'memory_usage': memory_info.rss / 1024 / 1024,  # MB
                'cpu_percent': process.cpu_percent()
            }
        except Exception as e:
            self.logger.error(f"獲取性能統計信息失敗: {str(e)}")
            return {}
            
    def check_page_state(self) -> Tuple[bool, str]:
        """
        檢查頁面狀態
        
        Returns:
            (是否正常, 狀態描述)
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化")
            return False, "WebDriver未初始化"
            
        try:
            # 檢查頁面標題
            title = self.driver.title
            if not title:
                return False, "頁面標題為空"
                
            # 檢查頁面源碼
            source = self.driver.page_source
            if not source or len(source) < 100:
                return False, "頁面源碼異常"
                
            # 檢查JavaScript錯誤
            js_errors = self.driver.get_log('browser')
            if js_errors:
                return False, f"JavaScript錯誤: {len(js_errors)}個"
                
            # 檢查網絡請求
            performance = self.driver.execute_script("return window.performance.getEntries()")
            failed_requests = [p for p in performance if p.get('responseStatus', 200) >= 400]
            if failed_requests:
                return False, f"網絡請求失敗: {len(failed_requests)}個"
                
            return True, "頁面狀態正常"
            
        except Exception as e:
            self.logger.error(f"檢查頁面狀態失敗: {str(e)}")
            return False, f"檢查失敗: {str(e)}"
            
    def clear_browser_data(self) -> bool:
        """
        清理瀏覽器數據
        
        Returns:
            是否清理成功
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化")
            return False
            
        try:
            # 清理cookies
            self.driver.delete_all_cookies()
            
            # 清理localStorage
            self.driver.execute_script("window.localStorage.clear();")
            
            # 清理sessionStorage
            self.driver.execute_script("window.sessionStorage.clear();")
            
            # 清理緩存
            self.driver.execute_script("window.performance.clearResourceTimings();")
            
            self.logger.info("已清理瀏覽器數據")
            return True
            
        except Exception as e:
            self.logger.error(f"清理瀏覽器數據失敗: {str(e)}")
            return False
            
    def simulate_human_behavior(self) -> None:
        """
        模擬人類行為
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化")
            return
            
        try:
            # 隨機滾動
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            current_position = 0
            
            while current_position < scroll_height:
                # 隨機滾動距離
                scroll_step = random.randint(100, 300)
                current_position += scroll_step
                
                # 平滑滾動
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                
                # 隨機暫停
                time.sleep(random.uniform(0.5, 2.0))
                
            # 隨機移動鼠標
            elements = self.driver.find_elements(By.TAG_NAME, "a")
            if elements:
                for _ in range(random.randint(2, 5)):
                    element = random.choice(elements)
                    try:
                        ActionChains(self.driver).move_to_element(element).perform()
                        time.sleep(random.uniform(0.3, 1.0))
                    except:
                        continue
                        
        except Exception as e:
            self.logger.error(f"模擬人類行為失敗: {str(e)}")
            
    def wait_for_page_load(self, timeout: int = 30) -> bool:
        """
        等待頁面加載完成
        
        Args:
            timeout: 超時時間(秒)
            
        Returns:
            是否加載完成
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化")
            return False
            
        try:
            start_time = time.time()
            
            # 等待document.readyState
            while time.time() - start_time < timeout:
                ready_state = self.driver.execute_script("return document.readyState")
                if ready_state == "complete":
                    # 更新性能統計
                    load_time = time.time() - start_time
                    self.performance_stats['page_loads'] += 1
                    self.performance_stats['total_load_time'] += load_time
                    return True
                time.sleep(0.5)
                
            self.logger.warning("頁面加載超時")
            return False
            
        except Exception as e:
            self.logger.error(f"等待頁面加載失敗: {str(e)}")
            return False
            
    def check_element_visibility(self, element: WebElement) -> Tuple[bool, str]:
        """
        檢查元素可見性
        
        Args:
            element: 要檢查的元素
            
        Returns:
            (是否可見, 原因)
        """
        try:
            # 檢查元素是否存在
            if not element:
                return False, "元素不存在"
                
            # 檢查元素是否顯示
            if not element.is_displayed():
                return False, "元素未顯示"
                
            # 檢查元素尺寸
            size = element.size
            if size['width'] == 0 or size['height'] == 0:
                return False, "元素尺寸為0"
                
            # 檢查元素位置
            location = element.location
            if location['x'] < 0 or location['y'] < 0:
                return False, "元素位置異常"
                
            # 檢查元素是否在視口內
            viewport_height = self.driver.execute_script("return window.innerHeight")
            viewport_width = self.driver.execute_script("return window.innerWidth")
            
            if (location['y'] > viewport_height or 
                location['x'] > viewport_width):
                return False, "元素在視口外"
                
            return True, "元素可見"
            
        except Exception as e:
            self.logger.error(f"檢查元素可見性失敗: {str(e)}")
            return False, f"檢查失敗: {str(e)}"
            
    def get_element_center(self, element: WebElement) -> Tuple[int, int]:
        """
        獲取元素中心點坐標
        
        Args:
            element: 要計算的元素
            
        Returns:
            (x, y)坐標
        """
        try:
            location = element.location
            size = element.size
            
            center_x = location['x'] + size['width'] // 2
            center_y = location['y'] + size['height'] // 2
            
            return center_x, center_y
            
        except Exception as e:
            self.logger.error(f"計算元素中心點失敗: {str(e)}")
            return 0, 0
            
    def highlight_element(self, element: WebElement, duration: float = 1.0) -> None:
        """
        高亮顯示元素
        
        Args:
            element: 要高亮的元素
            duration: 高亮持續時間(秒)
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化")
            return
            
        try:
            # 保存原始樣式
            original_style = element.get_attribute('style')
            
            # 設置高亮樣式
            self.driver.execute_script("""
                arguments[0].style.border = '2px solid red';
                arguments[0].style.backgroundColor = 'yellow';
            """, element)
            
            # 等待指定時間
            time.sleep(duration)
            
            # 恢復原始樣式
            self.driver.execute_script(
                "arguments[0].style = arguments[1];",
                element, original_style
            )
            
        except Exception as e:
            self.logger.error(f"高亮元素失敗: {str(e)}")
            
    def get_element_screenshot(self, element: WebElement) -> Optional[str]:
        """
        獲取元素的截圖
        
        Args:
            element: 要截圖的元素
            
        Returns:
            截圖文件路徑，如果失敗則返回None
        """
        try:
            # 檢查元素是否可見
            if not element.is_displayed():
                self.logger.warning("元素不可見，無法截圖")
                return None
                
            # 捲動到元素位置
            self.scroll_to_element(element)
            time.sleep(0.3)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"element_screenshot_{timestamp}.png"
            filepath = self.path_utils.join_path("screenshots", filename)
            
            # 確保目錄存在
            self.path_utils.ensure_dir("screenshots")
            
            # 截取元素圖片
            element.screenshot(filepath)
            self.logger.info(f"已保存元素截圖: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"獲取元素截圖失敗: {str(e)}")
            return None
            
    @staticmethod
    def create_chrome_options(
        headless: bool = False,
        window_size: Tuple[int, int] = (1920, 1080),
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None,
        disable_gpu: bool = True,
        no_sandbox: bool = True,
        disable_dev_shm: bool = True,
        disable_images: bool = False,
        disable_javascript: bool = False,
        incognito: bool = True,
        start_maximized: bool = True
    ) -> webdriver.ChromeOptions:
        """
        創建Chrome瀏覽器選項
        
        Args:
            headless: 是否使用無頭模式
            window_size: 窗口大小
            proxy: 代理服務器
            user_agent: 用戶代理
            disable_gpu: 是否禁用GPU
            no_sandbox: 是否禁用沙箱
            disable_dev_shm: 是否禁用/dev/shm
            disable_images: 是否禁用圖片
            disable_javascript: 是否禁用JavaScript
            incognito: 是否使用隱身模式
            start_maximized: 是否最大化窗口
            
        Returns:
            Chrome瀏覽器選項
        """
        options = webdriver.ChromeOptions()
        
        # 基本設置
        if headless:
            options.add_argument('--headless')
        if disable_gpu:
            options.add_argument('--disable-gpu')
        if no_sandbox:
            options.add_argument('--no-sandbox')
        if disable_dev_shm:
            options.add_argument('--disable-dev-shm-usage')
        if incognito:
            options.add_argument('--incognito')
        if start_maximized:
            options.add_argument('--start-maximized')
            
        # 設置窗口大小
        options.add_argument(f'--window-size={window_size[0]},{window_size[1]}')
        
        # 設置代理
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
            
        # 設置用戶代理
        if user_agent:
            options.add_argument(f'--user-agent={user_agent}')
            
        # 禁用圖片
        if disable_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
            
        # 禁用JavaScript
        if disable_javascript:
            prefs = {"profile.managed_default_content_settings.javascript": 2}
            options.add_experimental_option("prefs", prefs)
            
        # 其他常用設置
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        return options 
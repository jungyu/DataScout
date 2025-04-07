#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基礎提取器模組

定義基本的提取器接口和共用功能
"""

import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Set

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..config import ExtractionConfig
from ..utils.text_cleaner import TextCleaner
from ..utils.url_normalizer import URLNormalizer
from ..utils.html_cleaner import HTMLCleaner
from ..utils.date_parser import DateParser
from ..utils.number_parser import NumberParser


class BaseExtractor(ABC):
    """基礎提取器抽象類，定義共用方法和抽象接口"""
    
    def __init__(
        self, 
        driver: Optional[webdriver.Remote] = None, 
        base_url: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        timeout: int = 10
    ):
        """
        初始化基礎提取器
        
        Args:
            driver: Selenium WebDriver實例
            base_url: 基礎URL，用於URL標準化
            logger: 日誌記錄器
            timeout: 默認等待超時時間(秒)
        """
        self.driver = driver
        self.base_url = base_url
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.default_timeout = timeout
        
        # 用於追蹤訪問過的URL
        self.visited_urls: Set[str] = set()
        
        # 初始化工具類
        self.text_cleaner = TextCleaner()
        self.url_normalizer = URLNormalizer()
        self.html_cleaner = HTMLCleaner(base_url)
        self.date_parser = DateParser()
        self.number_parser = NumberParser()
        
        # 統計計數
        self.extracted_items_count = 0
        self.extracted_fields_count = 0
        self.extraction_errors_count = 0
    
    def set_driver(self, driver: webdriver.Remote) -> None:
        """
        設置WebDriver實例
        
        Args:
            driver: Selenium WebDriver實例
        """
        self.driver = driver
        self.logger.info("WebDriver已更新")
    
    def set_base_url(self, base_url: str) -> None:
        """
        設置基礎URL
        
        Args:
            base_url: 基礎URL
        """
        self.base_url = base_url
        self.html_cleaner.set_base_url(base_url)
        self.logger.info(f"基礎URL已更新: {base_url}")
    
    def reset_statistics(self) -> None:
        """重置統計計數"""
        self.extracted_items_count = 0
        self.extracted_fields_count = 0
        self.extraction_errors_count = 0
        self.visited_urls.clear()
        self.logger.debug("提取統計已重置")
    
    def get_statistics(self) -> Dict[str, int]:
        """
        獲取提取統計信息
        
        Returns:
            包含提取統計的字典
        """
        return {
            "extracted_items": self.extracted_items_count,
            "extracted_fields": self.extracted_fields_count,
            "extraction_errors": self.extraction_errors_count,
            "visited_urls": len(self.visited_urls)
        }
    
    def wait_for_element(
        self, 
        by: By, 
        selector: str, 
        timeout: Optional[int] = None,
        parent: Optional[WebElement] = None
    ) -> Optional[WebElement]:
        """
        等待元素出現
        
        Args:
            by: 定位方式
            selector: 選擇器
            timeout: 超時時間(秒)
            parent: 父元素，用於限制搜索範圍
            
        Returns:
            找到的元素，超時則返回None
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return None
            
        timeout = timeout or self.default_timeout
        context = parent or self.driver
            
        try:
            if parent:
                # 如果有父元素，直接查找
                element = context.find_element(by, selector)
                return element
            else:
                # 使用WebDriverWait等待元素
                wait = WebDriverWait(self.driver, timeout)
                element = wait.until(EC.presence_of_element_located((by, selector)))
                return element
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
        timeout: Optional[int] = None,
        parent: Optional[WebElement] = None
    ) -> List[WebElement]:
        """
        等待多個元素出現
        
        Args:
            by: 定位方式
            selector: 選擇器
            timeout: 超時時間(秒)
            parent: 父元素，用於限制搜索範圍
            
        Returns:
            找到的元素列表
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return []
            
        timeout = timeout or self.default_timeout
        context = parent or self.driver
            
        try:
            if parent:
                # 如果有父元素，直接查找
                elements = context.find_elements(by, selector)
                return elements
            else:
                # 使用WebDriverWait等待元素
                wait = WebDriverWait(self.driver, timeout)
                wait.until(EC.presence_of_element_located((by, selector)))
                elements = self.driver.find_elements(by, selector)
                return elements
        except TimeoutException:
            self.logger.warning(f"等待元素超時: {by}={selector}")
            return []
        except Exception as e:
            self.logger.error(f"等待元素出錯: {str(e)}")
            return []
    
    def wait_for_clickable(
        self, 
        by: By, 
        selector: str, 
        timeout: Optional[int] = None
    ) -> Optional[WebElement]:
        """
        等待元素可點擊
        
        Args:
            by: 定位方式
            selector: 選擇器
            timeout: 超時時間(秒)
            
        Returns:
            可點擊的元素，超時則返回None
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return None
            
        timeout = timeout or self.default_timeout
            
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable((by, selector)))
            return element
        except TimeoutException:
            self.logger.warning(f"等待元素可點擊超時: {by}={selector}")
            return None
        except Exception as e:
            self.logger.error(f"等待元素可點擊出錯: {str(e)}")
            return None
    
    def safe_click(self, element: WebElement, retries: int = 3) -> bool:
        """
        安全點擊元素，處理常見的點擊問題
        
        Args:
            element: 要點擊的元素
            retries: 重試次數
            
        Returns:
            是否成功點擊
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return False
            
        for i in range(retries):
            try:
                # 嘗試滾動到元素位置
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(0.5)
                
                # 直接點擊
                element.click()
                return True
                
            except Exception as e:
                self.logger.debug(f"直接點擊失敗 (嘗試 {i+1}/{retries}): {str(e)}")
                
                try:
                    # 使用JavaScript點擊
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except Exception as js_e:
                    self.logger.debug(f"JavaScript點擊失敗 (嘗試 {i+1}/{retries}): {str(js_e)}")
                    
                    if i == retries - 1:
                        self.logger.warning("所有點擊嘗試均失敗")
                    else:
                        # 短暫延遲後重試
                        time.sleep(1)
        
        return False
    
    def navigate_to_url(self, url: str, timeout: Optional[int] = None) -> bool:
        """
        導航到指定URL
        
        Args:
            url: 目標URL
            timeout: 頁面加載超時時間(秒)
            
        Returns:
            是否成功導航
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return False
            
        timeout = timeout or self.default_timeout
            
        try:
            self.logger.info(f"導航到: {url}")
            self.driver.set_page_load_timeout(timeout)
            self.driver.get(url)
            
            # 記錄訪問
            self.visited_urls.add(url)
            
            # 等待頁面加載完成
            self._wait_for_page_load(timeout)
            
            return True
        except TimeoutException:
            self.logger.warning(f"頁面載入超時: {url}")
            return False
        except Exception as e:
            self.logger.error(f"導航到URL出錯: {str(e)}")
            return False
    
    def _wait_for_page_load(self, timeout: Optional[int] = None) -> None:
        """
        等待頁面加載完成
        
        Args:
            timeout: 超時時間(秒)
        """
        if not self.driver:
            return
            
        if timeout is None:
            timeout = self.default_timeout
            
        try:
            # 等待頁面完成加載
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # 短暫等待
            time.sleep(random.uniform(0.5, 1.5))
                
        except TimeoutException:
            self.logger.warning(f"頁面加載超時，繼續處理")
        except Exception as e:
            self.logger.warning(f"等待頁面加載出錯: {str(e)}")
    
    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
        """
        隨機延遲一段時間
        
        Args:
            min_seconds: 最小延遲時間(秒)
            max_seconds: 最大延遲時間(秒)
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def scroll_page(self, direction: str = "down", amount: int = 300) -> None:
        """
        滾動頁面
        
        Args:
            direction: 滾動方向 (up/down/top/bottom)
            amount: 滾動距離
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
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
    
    def take_screenshot(self, filepath: Optional[str] = None) -> Optional[str]:
        """
        截取當前頁面截圖
        
        Args:
            filepath: 保存路徑，如果為None則自動生成
            
        Returns:
            截圖保存路徑
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return None
            
        try:
            import os
            
            if not filepath:
                os.makedirs("screenshots", exist_ok=True)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join("screenshots", f"screenshot_{timestamp}.png")
            else:
                # 確保目錄存在
                os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
                
            self.driver.save_screenshot(filepath)
            self.logger.info(f"截圖已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"截圖失敗: {str(e)}")
            return None
    
    def save_page_source(self, filepath: Optional[str] = None) -> Optional[str]:
        """
        保存當前頁面源碼
        
        Args:
            filepath: 保存路徑，如果為None則自動生成
            
        Returns:
            頁面源碼保存路徑
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return None
            
        try:
            import os
            
            if not filepath:
                os.makedirs("page_sources", exist_ok=True)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join("page_sources", f"page_{timestamp}.html")
            else:
                # 確保目錄存在
                os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
                
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
                
            self.logger.info(f"頁面源碼已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"保存頁面源碼失敗: {str(e)}")
            return None
    
    def execute_script(self, script: str, *args) -> Any:
        """
        執行JavaScript腳本
        
        Args:
            script: JavaScript腳本
            *args: 腳本參數
            
        Returns:
            腳本返回結果
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return None
            
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self.logger.error(f"執行腳本失敗: {str(e)}")
            return None
    
    def is_page_valid(self) -> bool:
        """
        檢查當前頁面是否有效
        
        Returns:
            頁面是否有效
        """
        if not self.driver:
            return False
            
        try:
            # 檢查頁面標題
            title = self.driver.title.lower()
            invalid_patterns = ["404", "not found", "error", "無法連接", "不存在", "服務暫停"]
            
            for pattern in invalid_patterns:
                if pattern in title:
                    self.logger.warning(f"頁面標題包含無效關鍵字: {pattern}")
                    return False
            
            # 檢查頁面內容
            body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            error_patterns = ["404", "not found", "page not found", "無法連接"]
            
            for pattern in error_patterns:
                if pattern in body_text:
                    self.logger.warning(f"頁面內容包含錯誤文本: {pattern}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"檢查頁面有效性出錯: {str(e)}")
            return False
    
    @abstractmethod
    def extract(self, config: Any) -> Any:
        """
        提取數據的抽象方法，需要由子類實現
        
        Args:
            config: 提取配置
            
        Returns:
            提取的數據
        """
        pass
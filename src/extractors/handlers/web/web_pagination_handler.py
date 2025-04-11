"""
網頁分頁處理器模組

提供通用的網頁分頁處理功能，支持多種分頁模式：
- 按鈕點擊分頁
- URL參數分頁
- 頁碼點擊分頁
- 無限滾動分頁
- 表單提交分頁
- AJAX加載分頁
"""

from typing import Dict, Any, Optional, List, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
import time
import re
import urllib.parse

from ..pagination_handler import PaginationHandler, PaginationType
from ...config import ExtractionConfig
from ...core.exceptions import (
    WebDriverError,
    ParseError,
    TimeoutError,
    handle_exception
)

class WebPaginationHandler(PaginationHandler):
    """網頁分頁處理器類"""
    
    def __init__(self, config: Union[Dict[str, Any], ExtractionConfig], driver: Optional[webdriver.Chrome] = None):
        """
        初始化網頁分頁處理器
        
        Args:
            config: 配置字典或ExtractionConfig對象
            driver: WebDriver實例
        """
        super().__init__(config)
        self.driver = driver
        
        # 初始化分頁類型
        if isinstance(config, dict) and "pagination_type" in config:
            self.pagination_type = PaginationType(config["pagination_type"])
        else:
            self.pagination_type = PaginationType.BUTTON_CLICK
        
        # 初始化選擇器
        self.next_button_xpath = config.get("next_button_xpath", "//a[contains(@class, 'next') or contains(text(), '下一頁')]")
        self.page_number_xpath = config.get("page_number_xpath", "//div[contains(@class, 'pagination')]//a[contains(@class, 'page-num')]")
        self.page_input_xpath = config.get("page_input_xpath", "//input[contains(@class, 'page') or @name='page']")
        self.go_button_xpath = config.get("go_button_xpath", "//button[contains(@class, 'go') or contains(text(), '確定')]")
        self.has_next_xpath = config.get("has_next_xpath", "")
        
        # 初始化URL參數
        self.url_template = config.get("url_template", "")
        self.parameter_name = config.get("parameter_name", "page")
        
        # 初始化滾動配置
        self.scroll_element_xpath = config.get("scroll_element_xpath", "//div[contains(@class, 'list')]")
        self.scroll_threshold = config.get("scroll_threshold", 0.8)
        self.new_content_xpath = config.get("new_content_xpath", "//div[contains(@class, 'item')]")
        self.max_scroll_attempts = config.get("max_scroll_attempts", 10)
        
        # 初始化表單配置
        self.form_xpath = config.get("form_xpath", "//form[contains(@class, 'pagination')]")
        self.form_data = config.get("form_data", {})
        
        # 初始化延遲配置
        self.page_load_delay = config.get("page_load_delay", 2)
        self.between_pages_delay = config.get("between_pages_delay", 1.0)
        self.wait_for_element_timeout = config.get("wait_for_element_timeout", 10)
        
        # 初始化進階選項
        self.retry_count = config.get("retry_count", 3)
        self.javascript_click = config.get("javascript_click", True)
        self.wait_for_staleness = config.get("wait_for_staleness", True)
        self.use_ajax_detection = config.get("use_ajax_detection", False)
        self.ajax_complete_check = config.get("ajax_complete_check", "return (typeof jQuery !== 'undefined') ? jQuery.active === 0 : true")
        
        # 初始化檢測和跟蹤
        self.page_change_detection = config.get("page_change_detection", "url")
        self.element_to_track_xpath = config.get("element_to_track_xpath", "")
        
        # 初始化狀態追蹤
        self.last_page_content_hash = None
        self._previous_element_content = None
    
    def set_driver(self, driver: webdriver.Chrome):
        """
        設置WebDriver
        
        Args:
            driver: WebDriver實例
        """
        self.driver = driver
    
    def _extract_page(self, url: str, **kwargs) -> List[Dict[str, Any]]:
        """
        提取單頁數據
        
        Args:
            url: 頁面URL
            **kwargs: 額外參數
            
        Returns:
            頁面數據列表
        """
        if not self.driver:
            raise WebDriverError("WebDriver未設置")
        
        try:
            # 加載頁面
            self.driver.get(url)
            
            # 等待頁面加載
            self._wait_for_page_load()
            
            # 根據分頁類型提取數據
            if self.pagination_type == PaginationType.INFINITE_SCROLL:
                return self._extract_infinite_scroll_items()
            else:
                return self._extract_regular_items()
            
        except Exception as e:
            handle_exception(e, self.logger)
            return []
    
    def _extract_regular_items(self) -> List[Dict[str, Any]]:
        """
        提取常規頁面數據
        
        Returns:
            數據項列表
        """
        # 子類必須實現此方法
        raise NotImplementedError("子類必須實現_extract_regular_items方法")
    
    def _extract_infinite_scroll_items(self) -> List[Dict[str, Any]]:
        """
        提取無限滾動頁面數據
        
        Returns:
            數據項列表
        """
        items = []
        scroll_attempts = 0
        
        try:
            # 獲取滾動容器
            scroll_container = self._wait_for_element(By.XPATH, self.scroll_element_xpath)
            if not scroll_container:
                self.logger.warning("未找到滾動容器")
                return items
            
            # 記錄當前內容數量
            current_items = len(self.driver.find_elements(By.XPATH, self.new_content_xpath))
            
            # 執行滾動
            self.driver.execute_script(
                "arguments[0].scrollTo(0, arguments[0].scrollHeight * arguments[1]);",
                scroll_container,
                self.scroll_threshold
            )
            
            # 等待新內容加載
            time.sleep(self.page_load_delay)
            
            # 檢查是否有新內容加載
            new_items = len(self.driver.find_elements(By.XPATH, self.new_content_xpath))
            
            if new_items > current_items:
                # 提取新加載的項目
                new_elements = self.driver.find_elements(By.XPATH, self.new_content_xpath)[current_items:]
                for element in new_elements:
                    item = self._extract_item_from_element(element)
                    if item:
                        items.append(item)
            
            return items
            
        except Exception as e:
            self.logger.error(f"提取無限滾動數據失敗: {str(e)}")
            return items
    
    def _extract_item_from_element(self, element) -> Optional[Dict[str, Any]]:
        """
        從元素中提取數據項
        
        Args:
            element: 元素對象
            
        Returns:
            數據項
        """
        # 子類必須實現此方法
        raise NotImplementedError("子類必須實現_extract_item_from_element方法")
    
    def _get_next_page_url(self) -> Optional[str]:
        """
        獲取下一頁URL
        
        Returns:
            下一頁URL
        """
        try:
            if self.pagination_type == PaginationType.URL_PARAMETER:
                # 構建URL參數
                if self.url_template:
                    return self.url_template.format(page=self.current_page + 1)
                else:
                    # 修改當前URL的查詢參數
                    current_url = self.driver.current_url
                    parsed_url = urllib.parse.urlparse(current_url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    query_params[self.parameter_name] = [str(self.current_page + 1)]
                    new_query = urllib.parse.urlencode(query_params, doseq=True)
                    
                    # 構建新URL
                    return urllib.parse.urlunparse((
                        parsed_url.scheme,
                        parsed_url.netloc,
                        parsed_url.path,
                        parsed_url.params,
                        new_query,
                        parsed_url.fragment
                    ))
            
            elif self.pagination_type == PaginationType.BUTTON_CLICK:
                # 獲取下一頁按鈕的href屬性
                next_button = self._wait_for_element(By.XPATH, self.next_button_xpath)
                if next_button:
                    return next_button.get_attribute("href")
            
            elif self.pagination_type == PaginationType.PAGE_NUMBER:
                # 獲取下一頁按鈕的href屬性
                next_page_button = self._wait_for_element(
                    By.XPATH, 
                    f"{this.page_number_xpath}[text()='{this.current_page + 1}' or @data-page='{this.current_page + 1}']"
                )
                if next_page_button:
                    return next_page_button.get_attribute("href")
            
            return None
            
        except Exception as e:
            this.logger.error(f"獲取下一頁URL失敗: {str(e)}")
            return None
    
    def _check_has_next_page(self) -> bool:
        """
        檢查是否有下一頁
        
        Returns:
            是否有下一頁
        """
        try:
            # 使用配置的檢查方法
            if self.has_next_xpath:
                # 使用XPath檢查
                elements = self.driver.find_elements(By.XPATH, self.has_next_xpath)
                return bool(elements and elements[0].is_displayed())
            
            # 根據分頁類型進行檢查
            if this.pagination_type == PaginationType.BUTTON_CLICK:
                # 檢查下一頁按鈕
                elements = this.driver.find_elements(By.XPATH, this.next_button_xpath)
                return bool(elements and elements[0].is_displayed() and not this._is_element_disabled(elements[0]))
            
            elif this.pagination_type == PaginationType.URL_PARAMETER:
                # URL參數方式始終可以嘗試下一頁
                return True
            
            elif this.pagination_type == PaginationType.PAGE_NUMBER:
                # 檢查是否有更多頁碼
                next_page_num = this.current_page + 1
                page_buttons = this.driver.find_elements(
                    By.XPATH, 
                    f"{this.page_number_xpath}[text()='{next_page_num}' or @data-page='{next_page_num}']"
                )
                return bool(page_buttons and page_buttons[0].is_displayed())
            
            elif this.pagination_type == PaginationType.INFINITE_SCROLL:
                # 檢查是否有新內容加載
                scroll_container = this.driver.find_element(By.XPATH, this.scroll_element_xpath)
                if scroll_container:
                    # 執行滾動
                    this.driver.execute_script(
                        "arguments[0].scrollTo(0, arguments[0].scrollHeight * arguments[1]);",
                        scroll_container,
                        this.scroll_threshold
                    )
                    
                    # 等待新內容加載
                    time.sleep(this.page_load_delay)
                    
                    # 檢查是否有新內容
                    current_items = len(this.driver.find_elements(By.XPATH, this.new_content_xpath))
                    return current_items > 0
            
            elif this.pagination_type == PaginationType.FORM_SUBMIT:
                # 表單提交默認可以嘗試
                return True
            
            elif this.pagination_type == PaginationType.AJAX_LOAD:
                # 檢查加載更多按鈕
                elements = this.driver.find_elements(By.XPATH, "//button[contains(text(), '加載更多') or contains(@class, 'load-more')]")
                return bool(elements and elements[0].is_displayed() and not this._is_element_disabled(elements[0]))
            
            # 預設有下一頁
            return True
            
        except Exception as e:
            this.logger.warning(f"檢查是否有下一頁時出錯: {str(e)}")
            # 保守返回False
            return False
    
    def _wait_for_page_load(self):
        """等待頁面加載"""
        try:
            # 等待頁面完成加載
            WebDriverWait(this.driver, this.wait_for_element_timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # 等待AJAX完成
            if this.use_ajax_detection:
                this._wait_for_ajax_complete()
            
            # 額外等待
            time.sleep(this.page_load_delay)
            
        except TimeoutException:
            this.logger.warning(f"頁面加載超時，繼續處理")
        except Exception as e:
            this.logger.warning(f"等待頁面加載出錯: {str(e)}")
    
    def _wait_for_ajax_complete(self, timeout: int = 10) -> None:
        """
        等待AJAX請求完成
        
        Args:
            timeout: 超時時間(秒)
        """
        try:
            WebDriverWait(this.driver, timeout).until(
                lambda driver: driver.execute_script(this.ajax_complete_check)
            )
        except TimeoutException:
            this.logger.warning("等待AJAX完成超時")
    
    def _wait_for_element(self, by: By, selector: str, timeout: Optional[int] = None) -> Optional[Any]:
        """
        等待元素出現
        
        Args:
            by: 定位方式
            selector: 選擇器
            timeout: 超時時間(秒)
            
        Returns:
            找到的元素，超時則返回None
        """
        timeout = timeout or this.wait_for_element_timeout
            
        try:
            wait = WebDriverWait(this.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, selector)))
            return element
        except TimeoutException:
            this.logger.warning(f"等待元素超時: {by}={selector}")
            return None
        except Exception as e:
            this.logger.warning(f"等待元素出錯: {str(e)}")
            return None
    
    def _is_element_disabled(self, element) -> bool:
        """
        檢查元素是否被禁用
        
        Args:
            element: 要檢查的元素
            
        Returns:
            元素是否被禁用
        """
        try:
            # 檢查disabled屬性
            disabled = element.get_attribute("disabled")
            if disabled is not None and disabled.lower() in ["true", "disabled", ""]:
                return True
            
            # 檢查class是否含有表示禁用的關鍵詞
            class_attr = element.get_attribute("class") or ""
            if any(word in class_attr.lower() for word in ["disabled", "inactive", "dimmed"]):
                return True
            
            # 檢查aria-disabled屬性
            aria_disabled = element.get_attribute("aria-disabled")
            if aria_disabled is not None and aria_disabled.lower() == "true":
                return True
            
            return False
            
        except Exception as e:
            this.logger.debug(f"檢查元素禁用狀態時出錯: {str(e)}")
            return False
    
    def _click_element(self, element) -> bool:
        """
        安全點擊元素，處理常見的點擊問題
        
        Args:
            element: 要點擊的元素
            
        Returns:
            是否成功點擊
        """
        if not element:
            return False
            
        try:
            # 檢查元素是否可見
            if not element.is_displayed():
                this.logger.warning("元素不可見，無法點擊")
                return False
            
            # 捲動到元素位置
            this.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            
            # 嘗試普通點擊
            try:
                element.click()
                return True
            except ElementClickInterceptedException:
                this.logger.debug("元素點擊被攔截，嘗試JavaScript點擊")
            except Exception as e:
                this.logger.debug(f"常規點擊失敗: {str(e)}，嘗試JavaScript點擊")
            
            # 使用JavaScript點擊
            if this.javascript_click:
                this.driver.execute_script("arguments[0].click();", element)
                return True
            
            return False
            
        except Exception as e:
            this.logger.warning(f"點擊元素失敗: {str(e)}")
            return False 
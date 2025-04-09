#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分頁處理模組 (pagination_handler.py)

提供多種分頁處理策略，支持按鈕點擊、URL參數、表單提交和無限滾動等分頁方式。
支持從JSON配置文件加載配置，提供靈活的分頁處理方案。

主要功能：
- 支持多種分頁類型（按鈕點擊、URL參數、頁碼點擊、無限滾動等）
- 自動檢測頁面分頁信息
- 提供分頁狀態追蹤和統計
- 支持從JSON配置文件加載配置
- 提供便捷的分頁處理函數
"""

import time
import logging
import re
import json
import importlib
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
import urllib.parse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, 
    StaleElementReferenceException, ElementClickInterceptedException
)

from src.extractors.exceptions import NavigationError, TimeoutError


class PaginationType(Enum):
    """分頁類型枚舉"""
    BUTTON_CLICK = "button_click"     # 點擊下一頁按鈕
    URL_PARAMETER = "url_parameter"   # URL參數調整
    PAGE_NUMBER = "page_number"       # 頁碼直接點擊
    INFINITE_SCROLL = "infinite_scroll"  # 無限滾動加載
    FORM_SUBMIT = "form_submit"       # 表單提交
    AJAX_LOAD = "ajax_load"           # AJAX動態加載
    CUSTOM = "custom"                 # 自定義分頁方式


@dataclass
class PaginationConfig:
    """分頁處理配置"""
    # 基本配置
    pagination_type: PaginationType = PaginationType.BUTTON_CLICK
    max_pages: int = 1  # 最大頁數，設置為-1表示無限制
    start_page: int = 1  # 起始頁碼
    
    # 頁面元素選擇器
    next_button_xpath: str = "//a[contains(@class, 'next') or contains(text(), '下一頁')]"
    page_number_xpath: str = "//div[contains(@class, 'pagination')]//a[contains(@class, 'page-num')]"
    page_input_xpath: str = "//input[contains(@class, 'page') or @name='page']"
    go_button_xpath: str = "//button[contains(@class, 'go') or contains(text(), '確定')]"
    has_next_xpath: str = ""  # 存在下一頁的檢查XPath
    
    # URL參數配置
    url_template: str = ""  # 包含{page}佔位符的URL模板
    parameter_name: str = "page"  # 分頁參數名稱
    
    # 滾動加載配置
    scroll_element_xpath: str = "//div[contains(@class, 'list')]"
    scroll_threshold: int = 0.8  # 滾動閾值，0-1之間，表示滾動到頁面的比例
    new_content_xpath: str = "//div[contains(@class, 'item')]"
    max_scroll_attempts: int = 10  # 最大滾動嘗試次數
    
    # 表單提交配置
    form_xpath: str = "//form[contains(@class, 'pagination')]"
    form_data: Dict[str, str] = field(default_factory=dict)
    
    # 延遲和等待配置
    page_load_delay: int = 2  # 頁面加載後等待時間(秒)
    between_pages_delay: float = 1.0  # 頁面之間的延遲時間(秒)
    wait_for_element_timeout: int = 10  # 等待元素超時時間(秒)
    
    # 自定義函數
    custom_pagination_func: Optional[Callable] = None  # 自定義分頁函數
    
    # 進階選項
    retry_count: int = 3  # 失敗重試次數
    javascript_click: bool = True  # 是否使用JavaScript點擊
    wait_for_staleness: bool = True  # 等待舊元素消失
    use_ajax_detection: bool = False  # 是否使用AJAX檢測
    ajax_complete_check: str = "return (typeof jQuery !== 'undefined') ? jQuery.active === 0 : true"
    
    # 檢測和跟蹤
    page_change_detection: str = "url"  # url / element / content
    element_to_track_xpath: str = ""  # 用於跟蹤頁面變化的元素XPath


class PaginationHandler:
    """
    分頁處理器，處理各種類型的網頁分頁
    
    支持多種分頁策略，跟蹤分頁狀態，處理分頁錯誤，提供分頁報告
    """
    
    def __init__(
        self, 
        driver: webdriver.Remote,
        config: Optional[PaginationConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化分頁處理器
        
        Args:
            driver: WebDriver實例
            config: 分頁配置
            logger: 日誌記錄器
        """
        self.driver = driver
        self.config = config or PaginationConfig()
        self.logger = logger or logging.getLogger(__name__)
        
        # 分頁狀態追蹤
        self.current_page = self.config.start_page
        self.total_pages = None  # 總頁數，如果能夠確定的話
        self.page_history = []  # 已訪問頁面的歷史記錄
        self.last_page_content_hash = None  # 用於檢測頁面變化
        
        # 統計數據
        self.stats = {
            "navigation_attempts": 0,
            "navigation_errors": 0,
            "ajax_wait_count": 0,
            "pages_visited": 0,
            "successful_navigations": 0,
            "failed_navigations": 0,
            "scroll_attempts": 0,
            "scroll_successes": 0
        }
        
        self.logger.debug(f"分頁處理器初始化完成，分頁類型: {self.config.pagination_type.value}")
    
    def load_config_from_json(self, config_path: str) -> None:
        """
        從JSON文件加載配置
        
        Args:
            config_path: JSON配置文件路徑
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 加載基本配置
            if "pagination" in config_data:
                pagination_config = config_data["pagination"]
                
                # 更新分頁類型
                if "type" in pagination_config:
                    self.config.pagination_type = PaginationType(pagination_config["type"])
                
                # 更新最大頁數
                if "max_pages" in pagination_config:
                    self.config.max_pages = pagination_config["max_pages"]
                
                # 更新起始頁碼
                if "start_page" in pagination_config:
                    self.config.start_page = pagination_config["start_page"]
                    self.current_page = self.config.start_page
                
                # 更新元素選擇器
                if "selectors" in pagination_config:
                    selectors = pagination_config["selectors"]
                    if "next_button" in selectors:
                        self.config.next_button_xpath = selectors["next_button"]
                    if "page_number" in selectors:
                        self.config.page_number_xpath = selectors["page_number"]
                    if "page_input" in selectors:
                        self.config.page_input_xpath = selectors["page_input"]
                    if "go_button" in selectors:
                        self.config.go_button_xpath = selectors["go_button"]
                    if "has_next" in selectors:
                        self.config.has_next_xpath = selectors["has_next"]
                
                # 更新URL參數配置
                if "url" in pagination_config:
                    url_config = pagination_config["url"]
                    if "template" in url_config:
                        self.config.url_template = url_config["template"]
                    if "parameter_name" in url_config:
                        self.config.parameter_name = url_config["parameter_name"]
                
                # 更新滾動加載配置
                if "scroll" in pagination_config:
                    scroll_config = pagination_config["scroll"]
                    if "element" in scroll_config:
                        self.config.scroll_element_xpath = scroll_config["element"]
                    if "threshold" in scroll_config:
                        self.config.scroll_threshold = scroll_config["threshold"]
                    if "new_content" in scroll_config:
                        self.config.new_content_xpath = scroll_config["new_content"]
                    if "max_attempts" in scroll_config:
                        self.config.max_scroll_attempts = scroll_config["max_attempts"]
                
                # 更新表單提交配置
                if "form" in pagination_config:
                    form_config = pagination_config["form"]
                    if "xpath" in form_config:
                        self.config.form_xpath = form_config["xpath"]
                    if "data" in form_config:
                        self.config.form_data = form_config["data"]
                
                # 更新延遲和等待配置
                if "delays" in pagination_config:
                    delays = pagination_config["delays"]
                    if "page_load" in delays:
                        self.config.page_load_delay = delays["page_load"]
                    if "between_pages" in delays:
                        self.config.between_pages_delay = delays["between_pages"]
                    if "element_timeout" in delays:
                        self.config.wait_for_element_timeout = delays["element_timeout"]
                
                # 更新進階選項
                if "advanced" in pagination_config:
                    advanced = pagination_config["advanced"]
                    if "retry_count" in advanced:
                        self.config.retry_count = advanced["retry_count"]
                    if "javascript_click" in advanced:
                        self.config.javascript_click = advanced["javascript_click"]
                    if "wait_for_staleness" in advanced:
                        self.config.wait_for_staleness = advanced["wait_for_staleness"]
                    if "use_ajax_detection" in advanced:
                        self.config.use_ajax_detection = advanced["use_ajax_detection"]
                    if "ajax_complete_check" in advanced:
                        self.config.ajax_complete_check = advanced["ajax_complete_check"]
                
                # 更新檢測和跟蹤配置
                if "detection" in pagination_config:
                    detection = pagination_config["detection"]
                    if "method" in detection:
                        self.config.page_change_detection = detection["method"]
                    if "element_to_track" in detection:
                        self.config.element_to_track_xpath = detection["element_to_track"]
                
                # 加載自定義處理器
                if "custom_handlers" in pagination_config:
                    for handler in pagination_config["custom_handlers"]:
                        handler_type = handler.get("type", "custom")
                        handler_path = handler.get("path")
                        
                        if handler_path:
                            try:
                                module_path, func_name = handler_path.rsplit('.', 1)
                                module = importlib.import_module(module_path)
                                handler_func = getattr(module, func_name)
                                self.register_custom_handler(PaginationType(handler_type), handler_func)
                            except Exception as e:
                                self.logger.error(f"加載自定義處理器失敗: {str(e)}")
            
            self.logger.info(f"已從 {config_path} 加載分頁配置")
        except Exception as e:
            self.logger.error(f"加載配置文件失敗: {str(e)}")
    
    def navigate_to_next_page(self) -> bool:
        """
        導航到下一頁
        
        Returns:
            是否成功導航到下一頁
        """
        if self.has_reached_max_pages():
            self.logger.info(f"已達到最大頁數 ({self.config.max_pages})")
            return False
            
        # 增加嘗試次數計數
        self.stats["navigation_attempts"] += 1
        
        # 獲取當前頁面快照
        current_url = self.driver.current_url
        
        # 檢查是否存在下一頁
        if not self.has_next_page():
            self.logger.info("沒有下一頁了")
            return False
            
        self.logger.info(f"正在導航到第 {self.current_page + 1} 頁...")
        
        try:
            # 根據分頁類型執行不同的導航策略
            success = False
            
            if self.config.pagination_type == PaginationType.BUTTON_CLICK:
                success = self._navigate_by_button_click()
            elif self.config.pagination_type == PaginationType.URL_PARAMETER:
                success = self._navigate_by_url_parameter()
            elif self.config.pagination_type == PaginationType.PAGE_NUMBER:
                success = self._navigate_by_page_number()
            elif self.config.pagination_type == PaginationType.INFINITE_SCROLL:
                success = self._navigate_by_infinite_scroll()
            elif self.config.pagination_type == PaginationType.FORM_SUBMIT:
                success = self._navigate_by_form_submit()
            elif self.config.pagination_type == PaginationType.AJAX_LOAD:
                success = self._navigate_by_ajax_load()
            elif self.config.pagination_type == PaginationType.CUSTOM:
                success = self._navigate_by_custom_function()
            else:
                self.logger.error(f"不支持的分頁類型: {self.config.pagination_type}")
                return False
                
            if not success:
                self.stats["navigation_errors"] += 1
                self.stats["failed_navigations"] += 1
                self.logger.warning(f"導航到下一頁失敗，嘗試次數: {self.stats['navigation_attempts']}，失敗次數: {self.stats['navigation_errors']}")
                return False
                
            # 等待頁面加載
            self._wait_for_page_load()
            
            # 檢查頁面是否真的變化了
            if not self._verify_page_changed(current_url):
                self.logger.warning("頁面可能未成功變化")
                self.stats["navigation_errors"] += 1
                self.stats["failed_navigations"] += 1
                return False
                
            # 更新頁面狀態
            self.current_page += 1
            self.page_history.append(self.driver.current_url)
            self.stats["pages_visited"] += 1
            self.stats["successful_navigations"] += 1
            
            # 額外延遲
            if self.config.between_pages_delay > 0:
                time.sleep(self.config.between_pages_delay)
                
            self.logger.info(f"成功導航到第 {self.current_page} 頁: {self.driver.current_url}")
            return True
            
        except Exception as e:
            self.stats["navigation_errors"] += 1
            self.stats["failed_navigations"] += 1
            self.logger.error(f"導航到下一頁時出錯: {str(e)}")
            return False
    
    def navigate_to_page(self, page_number: int) -> bool:
        """
        直接導航到指定頁碼
        
        Args:
            page_number: 目標頁碼
            
        Returns:
            是否成功導航
        """
        if page_number < 1:
            self.logger.warning(f"無效的頁碼: {page_number}")
            return False
            
        if self.config.max_pages > 0 and page_number > self.config.max_pages:
            self.logger.warning(f"頁碼 {page_number} 超過了最大頁數 {self.config.max_pages}")
            return False
            
        # 檢查是否已經在目標頁面
        if page_number == self.current_page:
            self.logger.info(f"已經在第 {page_number} 頁")
            return True
            
        self.logger.info(f"正在導航到第 {page_number} 頁...")
        current_url = self.driver.current_url
        
        try:
            success = False
            
            if self.config.pagination_type == PaginationType.URL_PARAMETER:
                # 構建URL
                if self.config.url_template:
                    target_url = self.config.url_template.format(page=page_number)
                    self.driver.get(target_url)
                    success = True
                else:
                    # 修改當前URL的查詢參數
                    parsed_url = urllib.parse.urlparse(current_url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    query_params[self.config.parameter_name] = [str(page_number)]
                    new_query = urllib.parse.urlencode(query_params, doseq=True)
                    
                    # 構建新URL
                    new_url = urllib.parse.urlunparse((
                        parsed_url.scheme,
                        parsed_url.netloc,
                        parsed_url.path,
                        parsed_url.params,
                        new_query,
                        parsed_url.fragment
                    ))
                    
                    self.driver.get(new_url)
                    success = True
                    
            elif self.config.pagination_type == PaginationType.PAGE_NUMBER:
                # 尋找頁碼按鈕
                page_buttons = self.driver.find_elements(
                    By.XPATH, 
                    f"{self.config.page_number_xpath}[text()='{page_number}' or @data-page='{page_number}']"
                )
                
                if page_buttons:
                    self._click_element(page_buttons[0])
                    success = True
                else:
                    # 尋找頁碼輸入框
                    if self.config.page_input_xpath:
                        input_element = self.wait_for_element(By.XPATH, self.config.page_input_xpath)
                        if input_element:
                            input_element.clear()
                            input_element.send_keys(str(page_number))
                            
                            # 點擊確定按鈕
                            go_button = self.wait_for_element(By.XPATH, self.config.go_button_xpath)
                            if go_button:
                                self._click_element(go_button)
                                success = True
                
            elif self.config.pagination_type == PaginationType.FORM_SUBMIT:
                # 查找表單並設置頁碼
                form = self.wait_for_element(By.XPATH, self.config.form_xpath)
                if form:
                    # 查找頁碼輸入框
                    inputs = form.find_elements(By.XPATH, ".//input")
                    for input_el in inputs:
                        name = input_el.get_attribute("name")
                        if name and (name.lower() == "page" or "page" in name.lower()):
                            input_el.clear()
                            input_el.send_keys(str(page_number))
                            break
                            
                    # 提交表單
                    form.submit()
                    success = True
            
            else:
                self.logger.warning(f"當前分頁類型 {self.config.pagination_type.value} 不支持直接跳轉到指定頁碼")
                return False
                
            if not success:
                self.logger.warning(f"無法導航到第 {page_number} 頁")
                return False
                
            # 等待頁面加載
            self._wait_for_page_load()
            
            # 檢查頁面是否真的變化了
            if not self._verify_page_changed(current_url):
                self.logger.warning("頁面可能未成功變化")
                return False
                
            # 更新頁面狀態
            self.current_page = page_number
            self.page_history.append(self.driver.current_url)
            
            self.logger.info(f"成功導航到第 {self.current_page} 頁")
            return True
            
        except Exception as e:
            self.logger.error(f"導航到第 {page_number} 頁時出錯: {str(e)}")
            return False
    
    def has_next_page(self) -> bool:
        """
        檢查是否有下一頁
        
        Returns:
            是否存在下一頁
        """
        if self.has_reached_max_pages():
            return False
            
        try:
            # 使用配置的檢查方法
            if self.config.has_next_xpath:
                # 使用XPath檢查
                elements = self.driver.find_elements(By.XPATH, self.config.has_next_xpath)
                return bool(elements and elements[0].is_displayed())
                
            # 根據分頁類型進行檢查
            if self.config.pagination_type == PaginationType.BUTTON_CLICK:
                # 檢查下一頁按鈕
                elements = self.driver.find_elements(By.XPATH, self.config.next_button_xpath)
                return bool(elements and elements[0].is_displayed() and not self._is_element_disabled(elements[0]))
                
            elif self.config.pagination_type == PaginationType.URL_PARAMETER:
                # URL參數方式始終可以嘗試下一頁
                return True
                
            elif self.config.pagination_type == PaginationType.PAGE_NUMBER:
                # 檢查是否有更多頁碼
                next_page_num = self.current_page + 1
                page_buttons = self.driver.find_elements(
                    By.XPATH, 
                    f"{self.config.page_number_xpath}[text()='{next_page_num}' or @data-page='{next_page_num}']"
                )
                return bool(page_buttons and page_buttons[0].is_displayed())
                
            elif self.config.pagination_type == PaginationType.INFINITE_SCROLL:
                # 無限滾動始終可以嘗試
                return True
                
            elif self.config.pagination_type == PaginationType.FORM_SUBMIT:
                # 表單提交默認可以嘗試
                return True
                
            elif self.config.pagination_type == PaginationType.AJAX_LOAD:
                # 檢查加載更多按鈕
                elements = self.driver.find_elements(By.XPATH, "//button[contains(text(), '加載更多') or contains(@class, 'load-more')]")
                return bool(elements and elements[0].is_displayed() and not self._is_element_disabled(elements[0]))
                
            elif self.config.pagination_type == PaginationType.CUSTOM:
                # 自定義檢查
                if self.config.custom_pagination_func:
                    return self.config.custom_pagination_func(self.driver, "check_next")
                    
            # 預設有下一頁
            return True
            
        except Exception as e:
            self.logger.warning(f"檢查是否有下一頁時出錯: {str(e)}")
            # 保守返回False
            return False
    
    def detect_pagination_info(self) -> Dict[str, Any]:
        """
        檢測頁面的分頁信息
        
        Returns:
            分頁信息字典，包含當前頁碼、總頁數等
        """
        result = {
            "current_page": self.current_page,
            "total_pages": None,
            "has_next": self.has_next_page(),
            "has_prev": self.current_page > 1,
            "pagination_type": self.config.pagination_type.value,
            "page_elements_found": False
        }
        
        try:
            # 嘗試找到頁面上顯示的頁碼信息
            pagination_patterns = [
                # 格式化的頁碼信息：第X頁/共Y頁
                (r"第\s*(\d+)\s*頁\s*/\s*共\s*(\d+)\s*頁", "中文標準格式"),
                (r"Page\s*(\d+)\s*of\s*(\d+)", "英文標準格式"),
                (r"(\d+)\s*/\s*(\d+)\s*頁", "中文簡化格式"),
                (r"(\d+)\s*/\s*(\d+)\s*Page", "英文簡化格式"),
                # 當前頁/總頁數
                (r"當前第\s*(\d+)\s*頁，共\s*(\d+)\s*頁", "中文詳細格式"),
                (r"當前: (\d+) / 共(\d+)", "數字格式"),
                # 一般數字格式
                (r"(\d+)頁, 共(\d+)頁", "另一種中文格式")
            ]
            
            page_text = self.driver.find_element(By.XPATH, "//body").text
            
            for pattern, pattern_name in pagination_patterns:
                match = re.search(pattern, page_text)
                if match:
                    result["current_page_text"] = int(match.group(1))
                    result["total_pages"] = int(match.group(2))
                    result["pattern_matched"] = pattern_name
                    self.logger.debug(f"檢測到分頁信息: 當前第{result['current_page_text']}頁，共{result['total_pages']}頁")
                    
                    # 更新實例變量
                    self.total_pages = result["total_pages"]
                    break
            
            # 檢查是否有分頁元素
            pagination_elements = self.driver.find_elements(
                By.XPATH, 
                "//div[contains(@class, 'pagination') or contains(@class, 'pager')]"
            )
            
            if pagination_elements:
                result["page_elements_found"] = True
                
                # 檢測分頁類型
                next_buttons = self.driver.find_elements(By.XPATH, self.config.next_button_xpath)
                page_numbers = self.driver.find_elements(By.XPATH, self.config.page_number_xpath)
                
                result["has_next_button"] = bool(next_buttons and next_buttons[0].is_displayed())
                result["has_page_numbers"] = bool(page_numbers)
                
                # 嘗試識別頁面上的頁碼按鈕
                if page_numbers:
                    page_nums = []
                    for el in page_numbers:
                        try:
                            text = el.text.strip()
                            if text.isdigit():
                                page_nums.append(int(text))
                        except:
                            continue
                    
                    if page_nums:
                        result["detected_pages"] = sorted(page_nums)
                        result["max_page_number"] = max(page_nums)
                        
                        if not result.get("total_pages"):
                            result["total_pages"] = result["max_page_number"]
                            self.total_pages = result["max_page_number"]
            
            return result
            
        except Exception as e:
            self.logger.warning(f"檢測分頁信息時出錯: {str(e)}")
            return result
    
    def has_reached_max_pages(self) -> bool:
        """
        檢查是否已達到最大頁數
        
        Returns:
            是否已達到最大頁數
        """
        if self.config.max_pages < 0:  # 負數表示無限制
            return False
            
        return self.current_page >= self.config.max_pages
    
    def reset_state(self) -> None:
        """重置分頁狀態"""
        self.current_page = self.config.start_page
        self.page_history = []
        self.last_page_content_hash = None
        self.stats["navigation_attempts"] = 0
        self.stats["navigation_errors"] = 0
        self.stats["ajax_wait_count"] = 0
        self.logger.debug("分頁狀態已重置")
    
    def get_status(self) -> Dict[str, Any]:
        """
        獲取分頁器狀態
        
        Returns:
            包含分頁狀態信息的字典
        """
        return {
            "current_page": self.current_page,
            "total_pages": self.total_pages,
            "pages_visited": self.stats["pages_visited"],
            "has_next": self.has_next_page(),
            "navigation_attempts": self.stats["navigation_attempts"],
            "navigation_errors": self.stats["navigation_errors"],
            "successful_navigations": self.stats["successful_navigations"],
            "failed_navigations": self.stats["failed_navigations"],
            "scroll_attempts": self.stats["scroll_attempts"],
            "scroll_successes": self.stats["scroll_successes"],
            "pagination_type": self.config.pagination_type.value
        }
    
    def wait_for_element(
        self, 
        by: By, 
        selector: str, 
        timeout: Optional[int] = None
    ) -> Optional[WebElement]:
        """
        等待元素出現
        
        Args:
            by: 定位方式
            selector: 選擇器
            timeout: 超時時間(秒)
            
        Returns:
            找到的元素，超時則返回None
        """
        timeout = timeout or self.config.wait_for_element_timeout
            
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, selector)))
            return element
        except TimeoutException:
            self.logger.warning(f"等待元素超時: {by}={selector}")
            return None
        except Exception as e:
            self.logger.warning(f"等待元素出錯: {str(e)}")
            return None
    
    def _navigate_by_button_click(self) -> bool:
        """
        通過點擊按鈕導航到下一頁
        
        Returns:
            是否成功導航
        """
        # 查找下一頁按鈕
        next_button = self.wait_for_element(By.XPATH, self.config.next_button_xpath)
        
        if not next_button:
            self.logger.warning(f"找不到下一頁按鈕: {self.config.next_button_xpath}")
            return False
            
        if self._is_element_disabled(next_button):
            self.logger.info("下一頁按鈕已禁用")
            return False
            
        # 捲動到按鈕位置
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
        time.sleep(0.5)
        
        # 保存舊頁面內容的引用（可能用於等待頁面更新）
        old_page = self.driver.find_element(By.TAG_NAME, "html") if self.config.wait_for_staleness else None
        
        # 點擊按鈕
        click_success = self._click_element(next_button)
        if not click_success:
            return False
            
        # 等待舊頁面消失
        if self.config.wait_for_staleness and old_page:
            try:
                WebDriverWait(self.driver, self.config.wait_for_element_timeout).until(
                    EC.staleness_of(old_page)
                )
            except TimeoutException:
                self.logger.debug("頁面未刷新，可能是AJAX更新")
            except Exception as e:
                self.logger.debug(f"等待頁面刷新時出錯: {str(e)}")
                
        return True
    
    def _navigate_by_url_parameter(self) -> bool:
        """
        通過URL參數導航到下一頁
        
        Returns:
            是否成功導航
        """
        next_page_number = self.current_page + 1
        
        try:
            # 使用URL模板
            if self.config.url_template:
                target_url = self.config.url_template.format(page=next_page_number)
                self.driver.get(target_url)
                return True
                
            # 修改當前URL的查詢參數
            current_url = self.driver.current_url
            parsed_url = urllib.parse.urlparse(current_url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            # 設置或更新頁碼參數
            query_params[self.config.parameter_name] = [str(next_page_number)]
            
            # 重建查詢字符串
            new_query = urllib.parse.urlencode(query_params, doseq=True)
            
            # 構建新URL
            new_url = urllib.parse.urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                new_query,
                parsed_url.fragment
            ))
            
            self.logger.debug(f"導航到URL: {new_url}")
            self.driver.get(new_url)
            return True
            
        except Exception as e:
            self.logger.error(f"URL參數導航失敗: {str(e)}")
            return False
    
    def _navigate_by_page_number(self) -> bool:
        """
        通過點擊頁碼導航
        
        Returns:
            是否成功導航
        """
        next_page_number = self.current_page + 1
        
        # 尋找對應頁碼的按鈕
        page_xpath = f"{self.config.page_number_xpath}[text()='{next_page_number}' or @data-page='{next_page_number}']"
        page_button = self.wait_for_element(By.XPATH, page_xpath)
        
        if not page_button:
            self.logger.warning(f"找不到第 {next_page_number} 頁的頁碼按鈕")
            
            # 嘗試查找省略號後的按鈕（例如當頁碼太多時）
            ellipsis = self.driver.find_elements(By.XPATH, "//span[contains(text(), '...') or contains(@class, 'ellipsis')]")
            if ellipsis:
                # 嘗試點擊省略號後面的按鈕
                after_ellipsis = self.driver.find_elements(By.XPATH, "//span[contains(text(), '...') or contains(@class, 'ellipsis')]/following-sibling::a[1]")
                if after_ellipsis:
                    return self._click_element(after_ellipsis[0])
            
            # 如果有頁碼輸入框，嘗試直接輸入頁碼
            if self.config.page_input_xpath:
                input_element = self.wait_for_element(By.XPATH, self.config.page_input_xpath)
                if input_element:
                    input_element.clear()
                    input_element.send_keys(str(next_page_number))
                    
                    # 點擊確定按鈕
                    go_button = self.wait_for_element(By.XPATH, self.config.go_button_xpath)
                    if go_button:
                        return self._click_element(go_button)
            
            return False
            
        return self._click_element(page_button)
    
    def _navigate_by_infinite_scroll(self) -> bool:
        """
        通過無限滾動加載更多內容
        
        Returns:
            是否成功加載更多內容
        """
        # 獲取當前內容數量作為基準
        if self.config.new_content_xpath:
            current_items = self.driver.find_elements(By.XPATH, self.config.new_content_xpath)
            current_count = len(current_items)
            self.logger.debug(f"當前內容項目數: {current_count}")
        else:
            # 如果沒有提供內容選擇器，使用頁面高度作為指標
            current_height = self.driver.execute_script("return document.body.scrollHeight")
        
        # 確定滾動目標元素
        scroll_element = None
        if self.config.scroll_element_xpath:
            elements = self.driver.find_elements(By.XPATH, self.config.scroll_element_xpath)
            if elements:
                scroll_element = elements[0]
        
        # 計算滾動閾值
        if scroll_element:
            scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", scroll_element)
            scroll_position = scroll_height * self.config.scroll_threshold
        else:
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_position = scroll_height * self.config.scroll_threshold
        
        # 執行滾動
        if scroll_element:
            self.driver.execute_script(
                "arguments[0].scrollTo(0, arguments[1]);", 
                scroll_element, 
                scroll_position
            )
        else:
            self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        
        # 等待新內容加載
        time.sleep(1.5)  # 初始等待
        
        # 檢查是否有新內容加載
        attempts = 0
        self.stats["scroll_attempts"] += 1
        
        while attempts < self.config.max_scroll_attempts:
            attempts += 1
            
            # 等待AJAX完成
            if self.config.use_ajax_detection:
                self._wait_for_ajax_complete()
            
            # 使用內容計數檢查
            if self.config.new_content_xpath:
                new_items = self.driver.find_elements(By.XPATH, self.config.new_content_xpath)
                new_count = len(new_items)
                
                if new_count > current_count:
                    self.logger.info(f"成功加載新內容，項目數從 {current_count} 增加到 {new_count}")
                    self.stats["scroll_successes"] += 1
                    return True
                    
            # 使用頁面高度檢查  
            else:
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height > current_height:
                    self.logger.info(f"成功加載新內容，頁面高度從 {current_height} 增加到 {new_height}")
                    self.stats["scroll_successes"] += 1
                    return True
            
            # 如果沒有新內容，繼續滾動
            if scroll_element:
                self.driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[1]);", 
                    scroll_element, 
                    scroll_position + (attempts * 300)  # 每次多滾動一點
                )
            else:
                self.driver.execute_script(f"window.scrollTo(0, {scroll_position + (attempts * 300)});")
                
            time.sleep(1)
            
        self.logger.warning(f"無法通過滾動加載新內容，嘗試次數: {attempts}")
        return False
    
    def _navigate_by_form_submit(self) -> bool:
        """
        通過表單提交導航到下一頁
        
        Returns:
            是否成功導航
        """
        # 查找表單
        form = self.wait_for_element(By.XPATH, self.config.form_xpath)
        if not form:
            self.logger.warning(f"找不到分頁表單: {self.config.form_xpath}")
            return False
            
        try:
            # 查找頁碼輸入框
            inputs = form.find_elements(By.XPATH, ".//input")
            next_page_number = self.current_page + 1
            
            # 設置表單數據
            for input_el in inputs:
                name = input_el.get_attribute("name")
                if name:
                    # 如果是頁碼輸入框
                    if name.lower() == "page" or "page" in name.lower():
                        input_el.clear()
                        input_el.send_keys(str(next_page_number))
                    # 設置其他配置的表單數據
                    elif name in self.config.form_data:
                        input_el.clear()
                        input_el.send_keys(self.config.form_data[name])
            
            # 提交表單
            form.submit()
            
            # 等待表單處理
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            self.logger.error(f"表單提交失敗: {str(e)}")
            return False
    
    def _navigate_by_ajax_load(self) -> bool:
        """
        通過AJAX加載導航到下一頁
        
        Returns:
            是否成功導航
        """
        # 尋找"加載更多"按鈕
        load_more_button = self.driver.find_elements(By.XPATH, "//button[contains(text(), '加載更多') or contains(@class, 'load-more')]")
        
        if load_more_button and load_more_button[0].is_displayed():
            # 獲取當前內容數量
            if self.config.new_content_xpath:
                current_items = self.driver.find_elements(By.XPATH, self.config.new_content_xpath)
                current_count = len(current_items)
                self.logger.debug(f"當前內容項目數: {current_count}")
            
            # 點擊加載更多
            self._click_element(load_more_button[0])
            
            # 等待AJAX完成
            self._wait_for_ajax_complete()
            
            # 檢查是否加載了新內容
            if self.config.new_content_xpath:
                new_items = self.driver.find_elements(By.XPATH, self.config.new_content_xpath)
                new_count = len(new_items)
                
                if new_count > current_count:
                    self.logger.info(f"成功加載新內容，項目數從 {current_count} 增加到 {new_count}")
                    return True
                else:
                    self.logger.warning("未檢測到新內容加載")
                    return False
            
            # 如果沒有指定內容選擇器，假設成功
            return True
            
        else:
            # 嘗試無限滾動策略
            return self._navigate_by_infinite_scroll()
    
    def _navigate_by_custom_function(self) -> bool:
        """
        通過自定義函數導航
        
        Returns:
            是否成功導航
        """
        if self.config.custom_pagination_func:
            return self.config.custom_pagination_func(self.driver, "navigate_next", current_page=self.current_page)
        
        self.logger.error("未提供自定義分頁函數")
        return False
    
    def _click_element(self, element: WebElement) -> bool:
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
                self.logger.warning("元素不可見，無法點擊")
                return False
                
            # 捲動到元素位置
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            
            # 嘗試普通點擊
            try:
                element.click()
                return True
            except ElementClickInterceptedException:
                self.logger.debug("元素點擊被攔截，嘗試JavaScript點擊")
            except Exception as e:
                self.logger.debug(f"常規點擊失敗: {str(e)}，嘗試JavaScript點擊")
                
            # 使用JavaScript點擊
            if self.config.javascript_click:
                self.driver.execute_script("arguments[0].click();", element)
                return True
                
            return False
            
        except Exception as e:
            self.logger.warning(f"點擊元素失敗: {str(e)}")
            return False
    
    def _wait_for_page_load(self) -> None:
        """等待頁面加載完成"""
        try:
            # 等待頁面完成加載
            WebDriverWait(self.driver, self.config.page_load_delay).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # 等待AJAX完成
            if self.config.use_ajax_detection:
                self._wait_for_ajax_complete()
                
            # 額外等待
            time.sleep(self.config.page_load_delay)
                
        except TimeoutException:
            self.logger.warning(f"頁面加載超時，繼續處理")
        except Exception as e:
            self.logger.warning(f"等待頁面加載出錯: {str(e)}")
    
    def _wait_for_ajax_complete(self) -> None:
        """等待AJAX請求完成"""
        self.stats["ajax_wait_count"] += 1
        
        try:
            WebDriverWait(self.driver, self.config.wait_for_element_timeout / 2).until(
                lambda driver: driver.execute_script(self.config.ajax_complete_check)
            )
        except TimeoutException:
            self.logger.debug("等待AJAX完成超時")
        except Exception as e:
            self.logger.debug(f"檢查AJAX狀態時出錯: {str(e)}")
    
    def _verify_page_changed(self, previous_url: str) -> bool:
        """
        驗證頁面是否真的變化了
        
        Args:
            previous_url: 前一個頁面的URL
            
        Returns:
            頁面是否變化
        """
        # 檢查URL變化
        if self.config.page_change_detection == "url":
            current_url = self.driver.current_url
            return current_url != previous_url
            
        # 檢查元素變化
        elif self.config.page_change_detection == "element" and self.config.element_to_track_xpath:
            try:
                elements = self.driver.find_elements(By.XPATH, self.config.element_to_track_xpath)
                if not elements:
                    return False
                    
                current_content = elements[0].text
                if not hasattr(self, "_previous_element_content"):
                    self._previous_element_content = current_content
                    return True
                    
                result = current_content != self._previous_element_content
                self._previous_element_content = current_content
                return result
                
            except Exception as e:
                self.logger.warning(f"檢查元素變化時出錯: {str(e)}")
                return True
                
        # 檢查頁面內容哈希值變化
        elif self.config.page_change_detection == "content":
            try:
                content = self.driver.find_element(By.TAG_NAME, "body").text[:1000]  # 只使用前1000字符
                import hashlib
                content_hash = hashlib.md5(content.encode()).hexdigest()
                
                if self.last_page_content_hash is None:
                    self.last_page_content_hash = content_hash
                    return True
                    
                result = content_hash != self.last_page_content_hash
                self.last_page_content_hash = content_hash
                return result
                
            except Exception as e:
                self.logger.warning(f"計算頁面內容哈希時出錯: {str(e)}")
                return True
                
        # 默認假設頁面已變化
        return True
    
    def _is_element_disabled(self, element: WebElement) -> bool:
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
            self.logger.debug(f"檢查元素禁用狀態時出錯: {str(e)}")
            return False


# 便捷函數
def create_pagination_handler(
    driver: webdriver.Remote, 
    pagination_type: str = "button_click",
    next_button_xpath: str = None,
    max_pages: int = 10,
    config_path: str = None
) -> PaginationHandler:
    """
    創建分頁處理器的便捷函數
    
    Args:
        driver: WebDriver實例
        pagination_type: 分頁類型
        next_button_xpath: 下一頁按鈕XPath
        max_pages: 最大頁數
        config_path: 配置文件路徑
        
    Returns:
        配置好的分頁處理器
    """
    config = PaginationConfig(
        pagination_type=PaginationType(pagination_type),
        max_pages=max_pages
    )
    
    if next_button_xpath:
        config.next_button_xpath = next_button_xpath
        
    handler = PaginationHandler(driver, config)
    
    # 如果提供了配置文件路徑，則加載配置
    if config_path:
        handler.load_config_from_json(config_path)
        
    return handler


def handle_pagination(
    driver: webdriver.Remote, 
    action: callable, 
    max_pages: int = 5,
    pagination_config: Dict[str, Any] = None,
    config_path: str = None
) -> List[Any]:
    """
    處理分頁並對每頁執行操作的便捷函數
    
    Args:
        driver: WebDriver實例
        action: 每頁執行的操作函數，接受driver參數
        max_pages: 最大頁數
        pagination_config: 分頁配置字典
        config_path: 配置文件路徑
        
    Returns:
        每頁操作結果的列表
    """
    # 創建配置
    config = PaginationConfig(max_pages=max_pages)
    
    # 更新配置
    if pagination_config:
        if "pagination_type" in pagination_config:
            config.pagination_type = PaginationType(pagination_config["pagination_type"])
        if "next_button_xpath" in pagination_config:
            config.next_button_xpath = pagination_config["next_button_xpath"]
        if "page_load_delay" in pagination_config:
            config.page_load_delay = pagination_config["page_load_delay"]
    
    # 創建分頁處理器
    paginator = PaginationHandler(driver, config)
    
    # 如果提供了配置文件路徑，則加載配置
    if config_path:
        paginator.load_config_from_json(config_path)
    
    results = []
    current_page = 1
    
    # 處理當前頁面
    results.append(action(driver))
    
    # 循環處理後續頁面
    while paginator.navigate_to_next_page():
        current_page += 1
        results.append(action(driver))
        
        if current_page >= max_pages:
            break
    
    return results
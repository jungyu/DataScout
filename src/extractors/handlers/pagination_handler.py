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
from abc import ABC, abstractmethod
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, 
    StaleElementReferenceException, ElementClickInterceptedException, WebDriverException
)
from selenium.webdriver.common.keys import Keys

from src.core.utils import BrowserUtils, Logger, URLUtils, DataProcessor
from src.extractors.exceptions import NavigationError, TimeoutError
from ..core.base import BaseExtractor
from ..core.exceptions import (
    ParseError,
    StateError,
    handle_exception
)


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
    
    # 統計和日誌
    log_level: str = "INFO"  # 日誌級別
    save_screenshots: bool = False  # 是否保存截圖
    screenshot_dir: str = "screenshots"  # 截圖保存目錄
    
    # 錯誤處理
    ignore_errors: bool = False  # 是否忽略錯誤
    error_retry_delay: float = 2.0  # 錯誤重試延遲時間(秒)
    
    # 數據處理
    validate_items: bool = True  # 是否驗證提取的項目
    deduplicate_items: bool = True  # 是否去重
    item_id_field: str = "id"  # 用於去重的字段
    
    # 其他配置
    debug_mode: bool = False  # 是否啟用調試模式
    verbose: bool = False  # 是否輸出詳細日誌


class PaginationHandler(BaseExtractor):
    """分頁處理器基類"""
    
    def __init__(self, config: Union[Dict[str, Any], PaginationConfig], driver: Optional[webdriver.Remote] = None):
        """
        初始化分頁處理器
        
        Args:
            config: 配置字典或PaginationConfig對象
            driver: WebDriver實例
        """
        if isinstance(config, dict):
            config = PaginationConfig(**config)
        super().__init__(config)
        
        # 設置 WebDriver
        self.driver = driver
        
        # 初始化等待器
        self.wait = WebDriverWait(self.driver, self.config.wait_for_element_timeout)
        
        # 初始化工具類
        self.browser_utils = BrowserUtils()
        self.logger = Logger.get_logger("PaginationHandler")
        self.url_utils = URLUtils()
        self.data_processor = DataProcessor()
        
        # 初始化分頁狀態
        self._reset_pagination()
        
    def _reset_pagination(self):
        """重置分頁狀態"""
        self.current_page = self.config.start_page
        self.total_pages = 0
        self.total_items = 0
        self.processed_items = 0
        self.duplicate_items = 0
        self.failed_pages = 0
        self.start_time = time.time()
        
    def _update_pagination_info(self, items: List[Dict[str, Any]]):
        """
        更新分頁信息
        
        Args:
            items: 當前頁面提取的項目列表
        """
        self.processed_items += len(items)
        self.total_items = max(self.total_items, self.processed_items)
        
        # 更新進度
        self._update_progress()
        
    def _should_continue(self) -> bool:
        """
        判斷是否應該繼續分頁
        
        Returns:
            是否應該繼續
        """
        # 檢查是否達到最大頁數
        if self.config.max_pages > 0 and self.current_page >= self.config.max_pages:
            self.logger.info(f"已達到最大頁數: {self.config.max_pages}")
            return False
            
        # 檢查是否沒有更多頁面
        if not self._check_has_next_page():
            self.logger.info("沒有更多頁面")
            return False
            
        return True
        
    def _update_progress(self):
        """更新進度信息"""
        elapsed_time = time.time() - self.start_time
        items_per_second = self.processed_items / elapsed_time if elapsed_time > 0 else 0
        
        self.logger.info(
            f"進度: 第 {self.current_page} 頁, "
            f"已處理 {self.processed_items} 項, "
            f"速度: {items_per_second:.2f} 項/秒"
        )
        
    @abstractmethod
    def _extract_page(self, url: str, **kwargs) -> List[Dict[str, Any]]:
        """
        提取當前頁面的數據
        
        Args:
            url: 頁面URL
            **kwargs: 其他參數
            
        Returns:
            提取的數據項目列表
        """
        pass
        
    @abstractmethod
    def _get_next_page_url(self) -> Optional[str]:
        """
        獲取下一頁的URL
        
        Returns:
            下一頁的URL，如果沒有下一頁則返回None
        """
        pass
        
    @abstractmethod
    def _check_has_next_page(self) -> bool:
        """
        檢查是否有下一頁
        
        Returns:
            是否有下一頁
        """
        pass
        
    def validate_item(self, item: Dict[str, Any]) -> bool:
        """
        驗證提取的項目
        
        Args:
            item: 提取的項目
            
        Returns:
            是否有效
        """
        if not self.config.validate_items:
            return True
            
        # 檢查必要字段
        required_fields = ["id", "title"]
        for field in required_fields:
            if field not in item or not item[field]:
                return False
                
        return True


def create_pagination_handler(
    driver: webdriver.Remote, 
    pagination_type: str = "button_click",
    next_button_xpath: str = None,
    max_pages: int = 10,
    config_path: str = None
) -> PaginationHandler:
    """
    創建分頁處理器
    
    Args:
        driver: WebDriver實例
        pagination_type: 分頁類型
        next_button_xpath: 下一頁按鈕的XPath
        max_pages: 最大頁數
        config_path: 配置文件路徑
        
    Returns:
        分頁處理器實例
    """
    # 從配置文件加載配置
    config = {}
    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            
    # 更新配置
    config.update({
        "pagination_type": pagination_type,
        "max_pages": max_pages
    })
    
    if next_button_xpath:
        config["next_button_xpath"] = next_button_xpath
        
    # 創建處理器
    handler = PaginationHandler(config, driver)
    
    return handler


def handle_pagination(
    driver: webdriver.Remote, 
    action: callable, 
    max_pages: int = 5,
    pagination_config: Dict[str, Any] = None,
    config_path: str = None
) -> List[Any]:
    """
    處理分頁
    
    Args:
        driver: WebDriver實例
        action: 每頁執行的操作函數
        max_pages: 最大頁數
        pagination_config: 分頁配置
        config_path: 配置文件路徑
        
    Returns:
        所有頁面的結果列表
    """
    # 創建分頁處理器
    handler = create_pagination_handler(
        driver=driver,
        max_pages=max_pages,
        config_path=config_path
    )
    
    # 更新配置
    if pagination_config:
        handler.config = PaginationConfig(**pagination_config)
        
    # 執行分頁操作
    results = []
    page = 1
    
    while page <= max_pages:
        # 執行操作
        page_results = action(driver)
        results.extend(page_results)
        
        # 檢查是否有下一頁
        if not handler._check_has_next_page():
            break
            
        # 獲取下一頁URL
        next_url = handler._get_next_page_url()
        if not next_url:
            break
            
        # 導航到下一頁
        driver.get(next_url)
        page += 1
        
    return results
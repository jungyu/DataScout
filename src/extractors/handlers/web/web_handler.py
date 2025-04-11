#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
網頁處理模組

提供網頁內容提取功能，包括：
1. 頁面加載和渲染
2. 元素定位和交互
3. 數據提取和處理
4. 分頁處理
5. 錯誤處理和重試
"""

import time
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException
)

from ...core.base import BaseExtractor
from ...core.exceptions import (
    PageLoadError,
    ElementNotFoundError,
    ExtractionError,
    handle_exception
)
from ..pagination_handler import PaginationHandler, PaginationConfig, PaginationType

# 從 src.core.utils 導入工具類
from src.core.utils import (
    BrowserUtils,
    Logger,
    URLUtils,
    DataProcessor
)


class WebLoadStrategy(Enum):
    """網頁加載策略枚舉"""
    NORMAL = "normal"  # 普通加載
    EAGER = "eager"    # 快速加載
    NONE = "none"      # 最小加載


@dataclass
class WebConfig:
    """網頁配置類"""
    # 基本配置
    url: str = ""
    title: str = ""
    description: str = ""
    
    # 加載配置
    load_strategy: WebLoadStrategy = WebLoadStrategy.NORMAL
    load_timeout: int = 30
    wait_timeout: int = 10
    
    # 瀏覽器配置
    user_agent: str = ""
    viewport_width: int = 1920
    viewport_height: int = 1080
    
    # 元素配置
    selectors: Dict[str, str] = None
    xpaths: Dict[str, str] = None
    
    # 提取配置
    extract_rules: Dict[str, Dict[str, Any]] = None
    validate_rules: Dict[str, Dict[str, Any]] = None
    
    # 分頁配置
    pagination: Optional[PaginationConfig] = None
    
    # 其他配置
    debug_mode: bool = False
    verbose: bool = False
    
    def __post_init__(self):
        """初始化後處理"""
        if self.selectors is None:
            self.selectors = {}
        if self.xpaths is None:
            self.xpaths = {}
        if self.extract_rules is None:
            self.extract_rules = {}
        if self.validate_rules is None:
            self.validate_rules = {}


class WebHandler(BaseExtractor):
    """網頁處理器類"""
    
    def __init__(self, config: Union[Dict[str, Any], WebConfig], driver: Optional[webdriver.Remote] = None):
        """
        初始化網頁處理器
        
        Args:
            config: 配置字典或 WebConfig 對象
            driver: WebDriver 實例
        """
        if isinstance(config, dict):
            config = WebConfig(**config)
        super().__init__(config)
        
        # 設置 WebDriver
        self.driver = driver
        
        # 初始化等待器
        self.wait = WebDriverWait(self.driver, self.config.wait_timeout)
        
        # 初始化工具類
        self.browser_utils = BrowserUtils()
        self.logger = Logger.get_logger("WebHandler")
        self.url_utils = URLUtils()
        self.data_processor = DataProcessor()
        
        # 初始化分頁處理器
        self.pagination_handler = None
        if self.config.pagination:
            self.pagination_handler = PaginationHandler(self.config.pagination, self.driver)
        
    def set_driver(self, driver: webdriver.Remote) -> None:
        """
        設置 WebDriver
        
        Args:
            driver: WebDriver 實例
        """
        self.driver = driver
        self.wait = WebDriverWait(self.driver, self.config.wait_timeout)
        if self.pagination_handler:
            self.pagination_handler.driver = driver
        
    def extract(self, url: str, **kwargs) -> List[Dict[str, Any]]:
        """
        提取數據
        
        Args:
            url: 頁面 URL
            **kwargs: 額外參數
            
        Returns:
            提取的數據列表
        """
        try:
            # 加載頁面
            self._load_page(url)
            
            # 等待頁面加載
            self._wait_for_page_load()
            
            # 提取所有頁面的數據
            all_items = []
            
            if self.pagination_handler:
                # 使用分頁處理器提取數據
                while True:
                    # 提取當前頁數據
                    items = self._extract_items()
                    
                    # 處理數據
                    items = self._process_items(items)
                    
                    # 驗證數據
                    if self.config.validate_rules:
                        items = [item for item in items if self._validate_item(item)]
                        
                    # 添加到結果
                    all_items.extend(items)
                    
                    # 檢查是否有下一頁
                    if not self.pagination_handler._check_has_next_page():
                        break
                        
                    # 跳轉到下一頁
                    next_url = self.pagination_handler._get_next_page_url()
                    if not next_url:
                        break
                        
                    # 加載下一頁
                    self._load_page(next_url)
                    self._wait_for_page_load()
                    
            else:
                # 提取單頁數據
                items = self._extract_items()
                
                # 處理數據
                items = self._process_items(items)
                
                # 驗證數據
                if self.config.validate_rules:
                    items = [item for item in items if self._validate_item(item)]
                    
                all_items = items
                
            return all_items
            
        except Exception as e:
            handle_exception(e, self.logger)
            return []
            
    def _load_page(self, url: str) -> None:
        """
        加載頁面
        
        Args:
            url: 頁面 URL
        """
        try:
            # 使用 URLUtils 處理 URL
            normalized_url = self.url_utils.normalize_url(url)
            
            # 設置頁面加載策略
            if self.config.load_strategy != WebLoadStrategy.NORMAL:
                script = f"document.documentElement.setAttribute('data-load', '{self.config.load_strategy.value}')"
                self.driver.execute_script(script)
                
            # 加載頁面
            self.driver.get(normalized_url)
            
        except WebDriverException as e:
            raise PageLoadError(f"加載頁面失敗: {str(e)}")
            
    def _wait_for_page_load(self) -> None:
        """等待頁面加載完成"""
        try:
            # 等待頁面標題
            if self.config.title:
                self.wait.until(EC.title_is(self.config.title))
                
            # 等待頁面描述
            if self.config.description:
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, f"//meta[@name='description' and @content='{self.config.description}']"))
                )
                
            # 等待頁面就緒
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
        except TimeoutException as e:
            raise PageLoadError(f"等待頁面加載超時: {str(e)}")
            
    def _extract_items(self) -> List[Dict[str, Any]]:
        """
        提取數據項目
        
        Returns:
            提取的數據列表
        """
        items = []
        
        # 根據規則提取數據
        for rule_name, rule in self.config.extract_rules.items():
            try:
                # 獲取元素
                element = self._find_element(rule["selector"])
                
                # 提取數據
                value = self._extract_value(element, rule)
                
                # 添加到結果
                items.append({
                    "rule": rule_name,
                    "value": value
                })
                
            except Exception as e:
                self.logger.warning(f"提取規則 {rule_name} 失敗: {str(e)}")
                
        return items
        
    def _find_element(self, selector: str) -> webdriver.remote.webelement.WebElement:
        """
        查找元素
        
        Args:
            selector: 元素選擇器
            
        Returns:
            元素對象
        """
        try:
            # 根據選擇器類型查找元素
            if selector.startswith("//"):
                return self.wait.until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
            elif selector.startswith("#"):
                return self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            else:
                return self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
        except TimeoutException as e:
            raise ElementNotFoundError(f"未找到元素: {selector}")
            
    def _extract_value(self, element: webdriver.remote.webelement.WebElement, rule: Dict[str, Any]) -> Any:
        """
        提取元素值
        
        Args:
            element: 元素對象
            rule: 提取規則
            
        Returns:
            提取的值
        """
        try:
            # 根據規則類型提取值
            if rule["type"] == "text":
                return element.text
            elif rule["type"] == "attribute":
                return element.get_attribute(rule["attribute"])
            elif rule["type"] == "css":
                return element.value_of_css_property(rule["property"])
            else:
                raise ExtractionError(f"不支持的提取類型: {rule['type']}")
                
        except Exception as e:
            raise ExtractionError(f"提取值失敗: {str(e)}")
            
    def _process_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        處理數據項目
        
        Args:
            items: 數據項目列表
            
        Returns:
            處理後的數據列表
        """
        processed_items = []
        
        # 根據規則處理數據
        for item in items:
            try:
                # 獲取處理規則
                rule = self.config.extract_rules.get(item["rule"], {}).get("process")
                
                if rule:
                    # 應用處理規則
                    value = self._apply_process_rule(item["value"], rule)
                    
                    # 更新值
                    item["value"] = value
                    
                # 添加到結果
                processed_items.append(item)
                
            except Exception as e:
                self.logger.warning(f"處理項目 {item['rule']} 失敗: {str(e)}")
                
        return processed_items
        
    def _apply_process_rule(self, value: Any, rule: Dict[str, Any]) -> Any:
        """
        應用處理規則
        
        Args:
            value: 原始值
            rule: 處理規則
            
        Returns:
            處理後的值
        """
        try:
            # 根據規則類型處理值
            if rule["type"] == "strip":
                return value.strip()
            elif rule["type"] == "replace":
                return value.replace(rule["old"], rule["new"])
            elif rule["type"] == "split":
                return value.split(rule["delimiter"])
            elif rule["type"] == "join":
                return rule["delimiter"].join(value)
            elif rule["type"] == "upper":
                return value.upper()
            elif rule["type"] == "lower":
                return value.lower()
            elif rule["type"] == "clean_text":
                return self.data_processor.clean_text(value)
            elif rule["type"] == "normalize_url":
                return self.url_utils.normalize_url(value)
            else:
                raise ExtractionError(f"不支持的處理類型: {rule['type']}")
                
        except Exception as e:
            raise ExtractionError(f"處理值失敗: {str(e)}")
            
    def _validate_item(self, item: Dict[str, Any]) -> bool:
        """
        驗證數據項目
        
        Args:
            item: 數據項目
            
        Returns:
            是否有效
        """
        try:
            # 獲取驗證規則
            rule = self.config.validate_rules.get(item["rule"])
            
            if rule:
                # 應用驗證規則
                return self._apply_validate_rule(item["value"], rule)
                
            return True
            
        except Exception as e:
            self.logger.warning(f"驗證項目 {item['rule']} 失敗: {str(e)}")
            return False
            
    def _apply_validate_rule(self, value: Any, rule: Dict[str, Any]) -> bool:
        """
        應用驗證規則
        
        Args:
            value: 驗證值
            rule: 驗證規則
            
        Returns:
            是否有效
        """
        try:
            # 根據規則類型驗證值
            if rule["type"] == "required":
                return bool(value)
            elif rule["type"] == "min_length":
                return len(value) >= rule["length"]
            elif rule["type"] == "max_length":
                return len(value) <= rule["length"]
            elif rule["type"] == "pattern":
                import re
                return bool(re.match(rule["pattern"], value))
            elif rule["type"] == "range":
                return rule["min"] <= value <= rule["max"]
            elif rule["type"] == "url":
                return self.url_utils.is_valid_url(value)
            else:
                raise ExtractionError(f"不支持的驗證類型: {rule['type']}")
                
        except Exception as e:
            raise ExtractionError(f"驗證值失敗: {str(e)}")
            
    def find_element(self, by: By, value: str, timeout: Optional[int] = None) -> webdriver.remote.webelement.WebElement:
        """
        查找單個元素
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間
            
        Returns:
            元素對象
        """
        try:
            wait = WebDriverWait(self.driver, timeout or self.config.wait_timeout)
            return wait.until(EC.presence_of_element_located((by, value)))
        except TimeoutException as e:
            raise ElementNotFoundError(f"未找到元素: {value}")
            
    def find_elements(self, by: By, value: str, timeout: Optional[int] = None) -> List[webdriver.remote.webelement.WebElement]:
        """
        查找多個元素
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間
            
        Returns:
            元素對象列表
        """
        try:
            wait = WebDriverWait(self.driver, timeout or self.config.wait_timeout)
            return wait.until(EC.presence_of_all_elements_located((by, value)))
        except TimeoutException as e:
            raise ElementNotFoundError(f"未找到元素: {value}")
            
    def get_text(self, element: webdriver.remote.webelement.WebElement) -> str:
        """
        獲取元素文本
        
        Args:
            element: 元素對象
            
        Returns:
            元素文本
        """
        try:
            return element.text
        except StaleElementReferenceException:
            raise ElementNotFoundError("元素已過期")
            
    def get_attribute(self, element: webdriver.remote.webelement.WebElement, name: str) -> str:
        """
        獲取元素屬性
        
        Args:
            element: 元素對象
            name: 屬性名
            
        Returns:
            屬性值
        """
        try:
            return element.get_attribute(name)
        except StaleElementReferenceException:
            raise ElementNotFoundError("元素已過期")
            
    def execute_script(self, script: str, *args) -> Any:
        """
        執行 JavaScript
        
        Args:
            script: JavaScript 代碼
            *args: 參數
            
        Returns:
            執行結果
        """
        try:
            return self.driver.execute_script(script, *args)
        except WebDriverException as e:
            raise ExtractionError(f"執行 JavaScript 失敗: {str(e)}")
            
    def __del__(self):
        """清理資源"""
        if hasattr(self, "driver"):
            try:
                self.driver.quit()
            except:
                pass 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數據提取器核心模組 (data_extractor.py)

提供中心化、可配置的網頁數據提取功能，協調其他提取器處理不同類型的數據提取任務。

主要功能：
- 從網頁中提取結構化數據
- 支持多種數據類型的提取（文本、屬性、HTML、複合字段等）
- 處理驗證碼和頁面有效性檢查
- 提供統計信息追蹤

使用示例：
    from src.extractors.core import DataExtractor
    from src.extractors.config import ExtractionConfig
    
    # 創建提取器
    extractor = DataExtractor(driver, base_url="https://example.com")
    
    # 配置提取
    config = {
        "title": ExtractionConfig(xpath="//h1", type="text"),
        "price": ExtractionConfig(xpath="//span[@class='price']", type="number"),
        "description": ExtractionConfig(xpath="//p[@class='description']", type="text"),
        "images": ExtractionConfig(xpath="//img", type="attribute", attribute="src", multiple=True)
    }
    
    # 提取數據
    data = extractor.extract_from_page(config)
"""

import logging
import time
from typing import Dict, List, Any, Optional, Union, Set

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .base_extractor import BaseExtractor
from ..config import ExtractionConfig
from ..utils.text_cleaner import TextCleaner
from ..utils.url_normalizer import URLNormalizer
from ..handlers.captcha_handler import CaptchaHandler
from ..handlers.pagination_handler import PaginationHandler
from ..handlers.storage_handler import StorageHandler


class DataExtractor(BaseExtractor):
    """
    主數據提取器類，協調其他提取器處理不同類型的數據提取任務
    
    該類提供了一個統一的接口來從網頁中提取各種類型的數據，包括文本、屬性、HTML內容、
    複合字段等。它還處理驗證碼檢測和頁面有效性檢查。
    
    Attributes:
        driver: Selenium WebDriver實例
        base_url: 基礎URL，用於URL標準化
        logger: 日誌記錄器
        timeout: 默認等待超時時間(秒)
        max_workers: 並行提取的最大工作線程數
        extracted_items_count: 已提取項目數
        extracted_fields_count: 已提取字段數
        extraction_errors_count: 提取錯誤數
        visited_urls: 已訪問的URL集合
        captcha_handler: 驗證碼處理器
        pagination_handler: 分頁處理器
        storage_handler: 存儲處理器
    """
    
    def __init__(
        self, 
        driver: Optional[webdriver.Remote] = None, 
        base_url: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        timeout: int = 10,
        max_workers: int = 5
    ):
        """
        初始化數據提取器
        
        Args:
            driver: Selenium WebDriver實例
            base_url: 基礎URL，用於URL標準化
            logger: 日誌記錄器
            timeout: 默認等待超時時間(秒)
            max_workers: 並行提取的最大工作線程數
        """
        super().__init__(driver, base_url, logger, timeout)
        self.max_workers = max_workers
        
        # 統計計數
        self.extracted_items_count = 0
        self.extracted_fields_count = 0
        self.extraction_errors_count = 0
        
        # 追蹤已訪問的URL以避免重複爬取
        self.visited_urls: Set[str] = set()
        
        # 初始化處理器
        self.captcha_handler = CaptchaHandler(driver, logger)
        self.pagination_handler = PaginationHandler(driver, logger, timeout)
        self.storage_handler = StorageHandler(logger)
        
        self.logger.info("數據提取器初始化完成")
    
    def reset_statistics(self) -> None:
        """
        重置統計計數
        
        將所有統計計數器重置為初始值。
        """
        self.extracted_items_count = 0
        self.extracted_fields_count = 0
        self.extraction_errors_count = 0
        self.logger.debug("提取統計已重置")
    
    def get_statistics(self) -> Dict[str, int]:
        """
        獲取提取統計信息
        
        Returns:
            包含提取統計的字典，包括已提取項目數、字段數、錯誤數和已訪問URL數
        """
        return {
            "extracted_items": self.extracted_items_count,
            "extracted_fields": self.extracted_fields_count,
            "extraction_errors": self.extraction_errors_count,
            "visited_urls": len(self.visited_urls)
        }
    
    def extract_from_page(
        self, 
        config: Dict[str, ExtractionConfig], 
        context: Optional[Union[webdriver.Remote, WebElement]] = None
    ) -> Dict[str, Any]:
        """
        從頁面或元素中提取數據
        
        根據提供的配置字典，從指定的上下文（頁面或元素）中提取數據。
        支持多種數據類型的提取，並處理提取過程中的錯誤。
        
        Args:
            config: 字段提取配置字典，鍵為字段名，值為提取配置
            context: 上下文元素，默認為整個頁面
            
        Returns:
            提取的數據字典，鍵為字段名，值為提取的數據
        """
        result = {}
        context = context or self.driver
        
        if not context:
            self.logger.error("提取上下文不存在")
            return result
        
        for field_name, field_config in config.items():
            try:
                # 執行數據提取
                extracted_value = self._extract_field(context, field_config)
                
                # 篩選非None值
                if extracted_value is not None:
                    result[field_name] = extracted_value
                    self.extracted_fields_count += 1
            
            except Exception as e:
                self.logger.warning(
                    f"提取字段 '{field_name}' 失敗: {str(e)}"
                )
                self.extraction_errors_count += 1
                
                # 使用默認值
                if field_config.default is not None:
                    result[field_name] = field_config.default
        
        # 增加提取項計數
        if result:
            self.extracted_items_count += 1
            
        return result
    
    def _extract_field(
        self, 
        context: Union[webdriver.Remote, WebElement], 
        config: ExtractionConfig
    ) -> Optional[Any]:
        """
        根據配置從元素中提取字段數據
        
        根據配置的類型，調用相應的提取方法從元素中提取數據。
        
        Args:
            context: 上下文元素
            config: 提取配置
            
        Returns:
            提取的數據，如果提取失敗則返回默認值
        """
        # 查找元素
        elements = self._find_elements(context, config)
        
        # 如果找不到元素
        if not elements:
            return config.default
        
        # 根據配置提取數據
        if config.type == 'text':
            value = self._extract_text(elements, config)
        elif config.type == 'attribute':
            value = self._extract_attribute(elements, config)
        elif config.type == 'html':
            value = self._extract_html(elements, config)
        elif config.type == 'compound':
            value = self._extract_compound(elements, config)
        elif config.type == 'date':
            value = self._extract_date(elements, config)
        elif config.type == 'number':
            value = self._extract_number(elements, config)
        elif config.type == 'url':
            value = self._extract_url(elements, config)
        else:
            value = config.default
        
        # 應用自定義轉換函數
        if config.transform and value is not None:
            try:
                value = config.transform(value)
            except Exception as e:
                self.logger.warning(f"應用轉換函數失敗: {str(e)}")
        
        return value
    
    def _find_elements(
        self, 
        context: Union[webdriver.Remote, WebElement], 
        config: ExtractionConfig
    ) -> List[WebElement]:
        """
        查找頁面元素
        
        根據配置的XPath查找元素，如果主XPath失敗則嘗試備用XPath。
        
        Args:
            context: 上下文元素
            config: 提取配置
            
        Returns:
            找到的元素列表，如果查找失敗則返回空列表
        """
        try:
            # 先嘗試主XPath
            elements = context.find_elements(By.XPATH, config.xpath)
            
            # 如果找不到，且有備用XPath，則使用備用XPath
            if not elements and config.fallback_xpath:
                elements = context.find_elements(
                    By.XPATH, 
                    config.fallback_xpath
                )
            
            return elements
        except Exception as e:
            self.logger.warning(
                f"查找元素失敗: {str(e)}, XPath: {config.xpath}"
            )
            return []
    
    def _extract_text(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Union[str, List[str]]:
        """
        提取元素文本
        
        從元素中提取文本內容，並應用文本清理和正則提取。
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            提取的文本，可能是單個字符串或字符串列表
        """
        def process_text(el: WebElement) -> str:
            text = el.text.strip()
            
            # 應用文本清理
            text = TextCleaner.clean_text(text, self.default_text_cleaning)
            
            # 截斷長度
            if config.max_length and len(text) > config.max_length:
                text = text[:config.max_length] + "..."
            
            # 應用正則提取
            if config.regex and text:
                import re
                match = re.search(config.regex, text)
                if match:
                    text = match.group(1)
            
            return text
        
        # 根據是否多值提取
        if config.multiple:
            return [process_text(el) for el in elements]
        
        return process_text(elements[0]) if elements else config.default
    
    def _extract_attribute(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Union[str, List[str]]:
        """
        提取元素屬性
        
        從元素中提取指定屬性的值，並應用正則提取和URL標準化。
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            提取的屬性值，可能是單個字符串或字符串列表
        """
        attribute = config.attribute or 'href'  # 默認提取href屬性
        
        def process_attribute(el: WebElement) -> str:
            attr_value = el.get_attribute(attribute) or ""
            
            # 正則提取
            if attr_value and config.regex:
                import re
                match = re.search(config.regex, attr_value)
                if match:
                    attr_value = match.group(1)
                    
            # URL標準化
            if attribute in ('href', 'src', 'data-src'):
                attr_value = URLNormalizer.normalize_url(attr_value, self.base_url)
            
            return attr_value
        
        # 根據是否多值提取
        if config.multiple:
            return [process_attribute(el) for el in elements]
        
        return process_attribute(elements[0]) if elements else config.default
    
    def _extract_html(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Union[str, List[str]]:
        """
        提取元素HTML內容
        
        從元素中提取完整的HTML內容。
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            提取的HTML內容，可能是單個字符串或字符串列表
        """
        def process_html(el: WebElement) -> str:
            return el.get_attribute('outerHTML') or ""
        
        # 根據是否多值提取
        if config.multiple:
            return [process_html(el) for el in elements]
        
        return process_html(elements[0]) if elements else config.default
    
    def _extract_compound(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        提取複合字段（嵌套字段）
        
        從元素中提取複合字段，支持嵌套的數據結構。
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            提取的複合數據，可能是字典或字典列表
        """
        # 檢查是否有嵌套字段配置
        if not config.nested_fields:
            return config.default
        
        def process_compound(el: WebElement) -> Dict[str, Any]:
            # 遞歸提取嵌套字段
            return self.extract_from_page(config.nested_fields, el)
        
        # 根據是否多值提取
        if config.multiple:
            return [process_compound(el) for el in elements]
        
        return process_compound(elements[0]) if elements else config.default
    
    def _extract_date(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Union[str, List[str]]:
        """
        提取並解析日期
        
        從元素中提取日期文本，並解析為指定格式的日期字符串。
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            解析後的日期，可能是單個字符串或字符串列表
        """
        from ..utils.date_parser import DateParser
        
        def process_date(el: WebElement) -> str:
            date_text = el.text.strip()
            return DateParser.parse_date(date_text, config.date_format)
        
        # 根據是否多值提取
        if config.multiple:
            return [process_date(el) for el in elements]
        
        return process_date(elements[0]) if elements else config.default
    
    def _extract_number(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Union[int, float, str, List[Union[int, float, str]]]:
        """
        提取並解析數字
        
        從元素中提取數字文本，並解析為數字類型。
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            解析後的數字，可能是單個數字或數字列表
        """
        from ..utils.number_parser import NumberParser
        
        def process_number(el: WebElement) -> Union[int, float, str]:
            number_text = el.text.strip()
            return NumberParser.parse_number(number_text)
        
        # 根據是否多值提取
        if config.multiple:
            return [process_number(el) for el in elements]
        
        return process_number(elements[0]) if elements else config.default
    
    def _extract_url(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Union[str, List[str]]:
        """
        提取URL
        
        從元素中提取URL，並標準化為絕對URL。
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            提取後的URL，可能是單個字符串或字符串列表
        """
        attribute = config.attribute or 'href'
        
        def process_url(el: WebElement) -> str:
            url = el.get_attribute(attribute) or ""
            return URLNormalizer.normalize_url(url, self.base_url)
        
        # 根據是否多值提取
        if config.multiple:
            return [process_url(el) for el in elements]
        
        return process_url(elements[0]) if elements else config.default
            
    def handle_captcha(self, detection_xpath: str = None) -> bool:
        """
        檢測並嘗試處理驗證碼
        
        使用驗證碼處理器檢測並處理頁面上的驗證碼。
        
        Args:
            detection_xpath: 驗證碼檢測XPath
            
        Returns:
            是否成功處理驗證碼
        """
        return self.captcha_handler.handle_captcha(detection_xpath)
    
    def is_page_valid(self) -> bool:
        """
        檢查當前頁面是否有效
        
        檢查當前頁面是否為有效的內容頁面，而不是錯誤頁面或無效頁面。
        
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
            error_patterns = [
                "404", "not found", "page not found", 
                "無法連接", "無法顯示", "不存在", 
                "伺服器錯誤", "server error",
                "access denied", "訪問被拒絕",
                "拒絕連接", "connection refused"
            ]
            
            for pattern in error_patterns:
                if pattern in body_text:
                    self.logger.warning(f"頁面內容包含錯誤文本: {pattern}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"檢查頁面有效性出錯: {str(e)}")
            return False
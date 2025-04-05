#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數據提取器模組

提供高度可配置、靈活的網頁數據提取功能，支持多種數據類型和複雜的提取邏輯。
"""

import os
import re
import json
import time
import logging
import random
import traceback
from typing import (
    Dict, List, Any, Optional, Union, Tuple, 
    Callable, Type, TypeVar, Generic
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

import dateparser
import html as html_module
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    StaleElementReferenceException
)

# 泛型類型定義
T = TypeVar('T')

@dataclass
class ExtractionConfig:
    """
    數據提取配置類，用於精細控制提取行為
    """
    type: str = 'text'  # 數據類型：text, attribute, html, compound等
    xpath: str = ''  # 主XPath
    fallback_xpath: Optional[str] = None  # 備用XPath
    multiple: bool = False  # 是否提取多個值
    max_length: Optional[int] = None  # 最大長度限制
    default: Any = None  # 默認值
    attribute: Optional[str] = 'href'  # 屬性提取（僅用於attribute類型）
    regex: Optional[str] = None  # 正則表達式
    cleaning_strategy: Optional[Callable[[str], str]] = None  # 自定義清理策略
    date_format: Optional[str] = None  # 日期格式化
    nested_fields: Optional[Dict[str, 'ExtractionConfig']] = None  # 嵌套字段配置

@dataclass
class TextCleaningOptions:
    """
    文本清理選項配置
    """
    remove_whitespace: bool = True
    remove_newlines: bool = True
    trim: bool = True
    lowercase: bool = False
    uppercase: bool = False
    custom_replacements: Dict[str, str] = field(default_factory=dict)

class TextCleaner:
    """
    文本清理工具類
    """
    @staticmethod
    def clean_text(text: str, options: TextCleaningOptions) -> str:
        """
        根據配置清理文本
        
        Args:
            text: 原始文本
            options: 清理選項
        
        Returns:
            清理後的文本
        """
        if not text:
            return ""
        
        # 移除空白和換行
        if options.remove_whitespace:
            text = re.sub(r'\s+', ' ', text)
        
        if options.remove_newlines:
            text = text.replace('\n', ' ')
        
        # 大小寫轉換
        if options.lowercase:
            text = text.lower()
        elif options.uppercase:
            text = text.upper()
        
        # 自定義替換
        for old, new in options.custom_replacements.items():
            text = text.replace(old, new)
        
        # 修剪
        if options.trim:
            text = text.strip()
        
        return text

class URLNormalizer:
    """
    URL標準化工具類
    """
    @staticmethod
    def normalize_url(url: str, base_url: Optional[str] = None) -> str:
        """
        標準化URL
        
        Args:
            url: 原始URL
            base_url: 基礎URL，用於處理相對路徑
        
        Returns:
            標準化後的URL
        """
        if not url:
            return ""
        
        # 處理相對URL
        if not url.startswith(('http://', 'https://')):
            if base_url:
                # 從基礎URL提取域名部分
                from urllib.parse import urljoin
                url = urljoin(base_url, url)
            else:
                url = f"https://{url}"
        
        # 處理雙斜線開頭的URL
        if url.startswith('//'):
            url = f"https:{url}"
        
        return url
    
    @staticmethod
    def clean_url_params(url: str, keep_params: List[str] = None) -> str:
        """
        清理URL中的參數，只保留指定的參數
        
        Args:
            url: 原始URL
            keep_params: 要保留的參數列表
            
        Returns:
            清理後的URL
        """
        if not url or not keep_params:
            return url
            
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # 只保留指定參數
        filtered_params = {k: v for k, v in query_params.items() if k in keep_params}
        
        # 重建URL
        new_query = urlencode(filtered_params, doseq=True)
        cleaned_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        
        return cleaned_url

class HTMLCleaner:
    """
    HTML清理工具類
    """
    @staticmethod
    def remove_scripts(html: str) -> str:
        """
        移除HTML中的腳本
        
        Args:
            html: 原始HTML
        
        Returns:
            清理後的HTML
        """
        if not html:
            return ""
            
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 移除script和style標籤
            for script in soup(["script", "style"]):
                script.decompose()
            
            return str(soup)
        except Exception as e:
            logging.warning(f"移除HTML腳本時出錯: {str(e)}")
            return html
    
    @staticmethod
    def remove_ads(html: str) -> str:
        """
        移除HTML中的廣告元素
        
        Args:
            html: 原始HTML
        
        Returns:
            清理後的HTML
        """
        if not html:
            return ""
            
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 移除常見廣告類或ID
            ad_classes = ['ad', 'ads', 'banner', 'advertisement', 'popup']
            ad_ids = ['ad', 'ads', 'banner', 'advertisement']
            
            for ad_class in ad_classes:
                for el in soup.find_all(class_=re.compile(ad_class, re.IGNORECASE)):
                    el.decompose()
            
            for ad_id in ad_ids:
                for el in soup.find_all(id=re.compile(ad_id, re.IGNORECASE)):
                    el.decompose()
            
            return str(soup)
        except Exception as e:
            logging.warning(f"移除HTML廣告時出錯: {str(e)}")
            return html
    
    @staticmethod
    def html_to_text(html: str) -> str:
        """
        將HTML轉換為純文本
        
        Args:
            html: HTML字符串
        
        Returns:
            純文本內容
        """
        if not html:
            return ""
            
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            logging.warning(f"HTML轉文本時出錯: {str(e)}")
            return html
            
    @staticmethod
    def extract_images(html: str, base_url: str = None) -> List[Dict[str, str]]:
        """
        從HTML中提取圖片信息
        
        Args:
            html: HTML內容
            base_url: 基礎URL用於標準化圖片URL
            
        Returns:
            圖片信息列表，包含url、alt等屬性
        """
        if not html:
            return []
            
        try:
            soup = BeautifulSoup(html, 'html.parser')
            images = []
            
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src:
                    images.append({
                        'url': URLNormalizer.normalize_url(src, base_url),
                        'alt': img.get('alt', ''),
                        'title': img.get('title', ''),
                    })
            
            return images
        except Exception as e:
            logging.warning(f"提取HTML圖片時出錯: {str(e)}")
            return []

class DateParser:
    """
    日期解析工具類
    """
    @staticmethod
    def parse_date(date_str: str, output_format: str = None) -> str:
        """
        解析各種格式的日期字符串
        
        Args:
            date_str: 日期字符串
            output_format: 輸出格式
            
        Returns:
            格式化後的日期字符串
        """
        if not date_str:
            return ""
            
        try:
            # 使用dateparser解析日期
            parsed_date = dateparser.parse(date_str)
            
            if not parsed_date:
                return date_str
                
            # 根據輸出格式返回
            if output_format:
                return parsed_date.strftime(output_format)
            else:
                return parsed_date.isoformat()
                
        except Exception as e:
            logging.warning(f"解析日期 '{date_str}' 時出錯: {str(e)}")
            return date_str
            
class NumberParser:
    """
    數字解析工具類
    """
    @staticmethod
    def parse_number(number_str: str) -> Union[int, float, str]:
        """
        從字符串中解析數字
        
        Args:
            number_str: 數字字符串
            
        Returns:
            解析後的數字，如果無法解析則返回原字符串
        """
        if not number_str:
            return 0
            
        try:
            # 移除貨幣符號、千位分隔符等
            clean_str = re.sub(r'[^\d.,\-+]', '', number_str)
            clean_str = clean_str.replace(',', '')
            
            # 嘗試轉換
            if '.' in clean_str:
                return float(clean_str)
            else:
                return int(clean_str)
                
        except Exception:
            return number_str

class DataExtractor:
    """
    高度可配置的數據提取器
    """
    def __init__(
        self, 
        driver: Optional[WebDriver] = None, 
        base_url: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化數據提取器
        
        Args:
            driver: Selenium WebDriver實例
            base_url: 基礎URL，用於URL標準化
            logger: 日誌記錄器
        """
        self.driver = driver
        self.base_url = base_url
        self.logger = logger or logging.getLogger(__name__)
        
        # 並發控制
        self.max_workers = 5  # 默認並發數
        
        # 統計計數
        self.extracted_items_count = 0
        self.extracted_fields_count = 0
        self.extraction_errors_count = 0
        self.default_timeout = 10  # 默認等待超時時間
        
        # 默認文本清理選項
        self.default_text_cleaning = TextCleaningOptions()
    
    def extract_from_page(
        self, 
        config: Dict[str, ExtractionConfig], 
        context: Optional[WebElement] = None
    ) -> Dict[str, Any]:
        """
        從頁面提取數據
        
        Args:
            config: 提取配置字典
            context: 上下文元素，默認為整個頁面
        
        Returns:
            提取的數據字典
        """
        result = {}
        context = context or self.driver
        
        if not context:
            self.logger.error("提取上下文不存在")
            return result
        
        for field_name, field_config in config.items():
            try:
                # 執行數據提取
                extracted_value = self._extract_field(
                    context, 
                    field_config
                )
                
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
    
    def parallel_extract(
        self, 
        configs: Dict[str, ExtractionConfig], 
        contexts: List[WebElement]
    ) -> List[Dict[str, Any]]:
        """
        並行提取數據
        
        Args:
            configs: 提取配置字典
            contexts: 上下文元素列表
        
        Returns:
            並行提取的數據列表
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任務
            futures = {
                executor.submit(
                    self.extract_from_page,
                    configs,
                    context
                ): i for i, context in enumerate(contexts)
            }
            
            # 收集結果
            for future in as_completed(futures):
                index = futures[future]
                try:
                    data = future.result()
                    # 添加索引信息
                    data['_metadata'] = data.get('_metadata', {})
                    data['_metadata']['index'] = index
                    results.append(data)
                except Exception as e:
                    self.logger.error(f"並行提取任務 #{index} 失敗: {str(e)}")
                    self.extraction_errors_count += 1
        
        # 按原始順序排序結果
        results.sort(key=lambda x: x['_metadata']['index'])
        
        return results
    
    def extract_list_items(
        self, 
        list_config: Dict[str, Any], 
        container_element: Optional[WebElement] = None
    ) -> List[Dict[str, Any]]:
        """
        提取列表頁面的項目
        
        Args:
            list_config: 列表配置
            container_element: 容器元素
            
        Returns:
            列表項目數據
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return []
            
        try:
            # 確定容器元素
            if container_element is None:
                container_xpath = list_config.get('container_xpath', '//body')
                container_element = self.wait_for_element(By.XPATH, container_xpath)
                
                if not container_element:
                    self.logger.error(f"找不到列表容器: {container_xpath}")
                    return []
            
            # 定位列表項目
            item_xpath = list_config.get('item_xpath')
            if not item_xpath:
                self.logger.error("未指定列表項目選擇器")
                return []
                
            items = container_element.find_elements(By.XPATH, item_xpath)
            self.logger.info(f"找到 {len(items)} 個列表項目")
            
            # 項目字段配置
            fields_config = list_config.get('fields', {})
            
            # 使用並行提取處理列表數據
            extraction_configs = {}
            for field_name, field_config in fields_config.items():
                extraction_configs[field_name] = ExtractionConfig(
                    type=field_config.get('type', 'text'),
                    xpath=field_config.get('xpath', ''),
                    fallback_xpath=field_config.get('fallback_xpath'),
                    multiple=field_config.get('multiple', False),
                    attribute=field_config.get('attribute'),
                    regex=field_config.get('regex'),
                    max_length=field_config.get('max_length'),
                    default=field_config.get('default')
                )
            
            # 決定是否使用並行提取
            if len(items) > 5 and self.max_workers > 1:
                results = self.parallel_extract(extraction_configs, items)
            else:
                # 串行提取
                results = []
                for i, item in enumerate(items):
                    data = self.extract_from_page(extraction_configs, item)
                    data['_metadata'] = {'index': i}
                    results.append(data)
            
            # 添加元數據
            for i, data in enumerate(results):
                data['_metadata'].update({
                    'source': list_config.get('source_name', ''),
                    'extraction_time': int(time.time())
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"提取列表項目時出錯: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return []
    
    def extract_detail_page(self, url: str, detail_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取詳情頁數據
        
        Args:
            url: 頁面URL
            detail_config: 詳情頁配置
            
        Returns:
            詳情頁數據
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return {}
            
        try:
            # 導航到頁面
            self.logger.info(f"提取詳情頁: {url}")
            self.driver.get(url)
            
            # 等待頁面加載
            self._wait_for_page_load(detail_config.get('wait_time', self.default_timeout))
            
            # 展開頁面折疊區域（如果有）
            self._expand_sections(detail_config.get('expand_sections', []))
            
            # 等待主容器
            container_xpath = detail_config.get('container_xpath', '//body')
            container = self.wait_for_element(By.XPATH, container_xpath)
            
            if not container:
                self.logger.error(f"找不到詳情頁容器: {container_xpath}")
                return {}
                
            # 處理字段配置
            fields_config = detail_config.get('fields', {})
            extraction_configs = {}
            
            # 轉換為ExtractionConfig格式
            for field_name, field_config in fields_config.items():
                if field_config.get('type') == 'elements' and 'fields' in field_config:
                    # 嵌套元素
                    nested_fields = {}
                    for nested_name, nested_config in field_config.get('fields', {}).items():
                        nested_fields[nested_name] = ExtractionConfig(
                            type=nested_config.get('type', 'text'),
                            xpath=nested_config.get('xpath', ''),
                            fallback_xpath=nested_config.get('fallback_xpath'),
                            multiple=nested_config.get('multiple', False),
                            attribute=nested_config.get('attribute'),
                            regex=nested_config.get('regex'),
                            max_length=nested_config.get('max_length'),
                            default=nested_config.get('default')
                        )
                        
                    extraction_configs[field_name] = ExtractionConfig(
                        type='compound',
                        xpath=field_config.get('xpath', ''),
                        multiple=True,
                        nested_fields=nested_fields
                    )
                else:
                    # 普通字段
                    extraction_configs[field_name] = ExtractionConfig(
                        type=field_config.get('type', 'text'),
                        xpath=field_config.get('xpath', ''),
                        fallback_xpath=field_config.get('fallback_xpath'),
                        multiple=field_config.get('multiple', False),
                        attribute=field_config.get('attribute'),
                        regex=field_config.get('regex'),
                        max_length=field_config.get('max_length'),
                        default=field_config.get('default')
                    )
            
            # 提取數據
            result = self.extract_from_page(extraction_configs, container)
            
            # 添加元數據
            result['_metadata'] = {
                'url': url,
                'source': detail_config.get('source_name', ''),
                'extraction_time': int(time.time())
            }
            
            # 後處理
            extraction_settings = detail_config.get('extraction_settings', {})
            result = self._post_process_detail_data(result, extraction_settings)
            
            return result
            
        except Exception as e:
            self.logger.error(f"提取詳情頁數據失敗: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return {}
    
    def _extract_field(
        self, 
        context: Union[WebDriver, WebElement], 
        config: ExtractionConfig
    ) -> Optional[Any]:
        """
        核心提取方法
        
        Args:
            context: 上下文元素
            config: 提取配置
        
        Returns:
            提取的數據
        """
        # 查找元素
        elements = self._find_elements(context, config)
        
        # 如果找不到元素
        if not elements:
            return config.default
        
        # 根據配置提取數據
        if config.type == 'text':
            return self._extract_text(elements, config)
        elif config.type == 'attribute':
            return self._extract_attribute(elements, config)
        elif config.type == 'html':
            return self._extract_html(elements, config)
        elif config.type == 'compound':
            return self._extract_compound(elements, config)
        elif config.type == 'date':
            return self._extract_date(elements, config)
        elif config.type == 'number':
            return self._extract_number(elements, config)
        elif config.type == 'url':
            return self._extract_url(elements, config)
        
        return config.default
    
    def _find_elements(
        self, 
        context: Union[WebDriver, WebElement], 
        config: ExtractionConfig
    ) -> List[WebElement]:
        """
        查找頁面元素
        
        Args:
            context: 上下文元素
            config: 提取配置
        
        Returns:
            找到的元素列表
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
        提取文本
        
        Args:
            elements: 元素列表
            config: 提取配置
        
        Returns:
            提取的文本
        """
        def process_text(el: WebElement) -> str:
            text = el.text.strip()
            
            # 應用自定義清理
            if config.cleaning_strategy:
                text = config.cleaning_strategy(text)
            else:
                text = TextCleaner.clean_text(text, self.default_text_cleaning)
            
            # 截斷長度
            if config.max_length and len(text) > config.max_length:
                text = text[:config.max_length] + "..."
            
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
        
        Args:
            elements: 元素列表
            config: 提取配置
        
        Returns:
            提取的屬性值
        """
        def process_attribute(el: WebElement) -> str:
            attr_value = el.get_attribute(config.attribute or 'href') or ""
            
            # 正則提取
            if attr_value and config.regex:
                match = re.search(config.regex, attr_value)
                if match:
                    attr_value = match.group(1)
            
            # URL標準化（如果是URL相關屬性）
            if config.attribute in ('href', 'src'):
                attr_value = URLNormalizer.normalize_url(
                    attr_value, 
                    self.base_url
                )
            
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
        提取HTML
        
        Args:
            elements: 元素列表
            config: 提取配置
        
        Returns:
            提取的HTML
        """
        def process_html(el: WebElement) -> str:
            html_content = el.get_attribute('outerHTML') or ""
            return html_content
        
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
        
        Args:
            elements: 元素列表
            config: 提取配置
        
        Returns:
            提取的複合數據
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
        提取日期
        
        Args:
            elements: 元素列表
            config: 提取配置
        
        Returns:
            提取的日期
        """
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
    ) -> Union[int, float, List[Union[int, float, str]]]:
        """
        提取數字
        
        Args:
            elements: 元素列表
            config: 提取配置
        
        Returns:
            提取的數字
        """
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
        
        Args:
            elements: 元素列表
            config: 提取配置
        
        Returns:
            提取的URL
        """
        # 使用屬性提取並標準化URL
        config.attribute = config.attribute or 'href'
        
        def process_url(el: WebElement) -> str:
            url = el.get_attribute(config.attribute) or ""
            return URLNormalizer.normalize_url(url, self.base_url)
        
        # 根據是否多值提取
        if config.multiple:
            return [process_url(el) for el in elements]
        
        return process_url(elements[0]) if elements else config.default
    
    def _post_process_detail_data(
        self, 
        data: Dict[str, Any], 
        extraction_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        對詳情頁數據進行後處理
        
        Args:
            data: 詳情頁數據
            extraction_settings: 提取設置
            
        Returns:
            處理後的詳情頁數據
        """
        result = data.copy()
        
        # 清理HTML內容
        if extraction_settings.get("clean_html", False):
            for field_name, field_value in list(result.items()):
                if isinstance(field_value, str) and field_value.startswith("<"):
                    # 可能是HTML內容
                    try:
                        # 移除腳本和樣式
                        if extraction_settings.get("remove_scripts", False):
                            field_value = HTMLCleaner.remove_scripts(field_value)
                        
                        # 移除廣告
                        if extraction_settings.get("remove_ads", False):
                            field_value = HTMLCleaner.remove_ads(field_value)
                        
                        result[field_name] = field_value
                        
                        # 額外提取純文本版本
                        if extraction_settings.get("extract_text", True):
                            result[f"{field_name}_text"] = HTMLCleaner.html_to_text(field_value)
                    except Exception as e:
                        self.logger.warning(f"清理HTML字段 '{field_name}' 失敗: {str(e)}")
        
        # 提取圖片
        if extraction_settings.get("extract_images", False):
            images = []
            
            # 從HTML字段中提取圖片
            for field_name, field_value in data.items():
                if isinstance(field_value, str) and field_value.startswith("<"):
                    field_images = HTMLCleaner.extract_images(field_value, self.base_url)
                    for img in field_images:
                        img['source_field'] = field_name
                        images.append(img)
            
            # 去重
            if images:
                unique_images = []
                seen_urls = set()
                
                for img in images:
                    if img["url"] and img["url"] not in seen_urls:
                        seen_urls.add(img["url"])
                        unique_images.append(img)
                
                result["extracted_images"] = unique_images
        
        return result
    
    def _expand_sections(self, expand_sections: List[Dict[str, Any]]) -> None:
        """
        展開頁面中的可折疊區域
        
        Args:
            expand_sections: 展開區域配置
        """
        if not self.driver:
            return
        
        if not expand_sections:
            return
        
        for section in expand_sections:
            try:
                section_name = section.get("name", "unknown")
                button_selector = section.get("button_selector", "")
                target_selector = section.get("target_selector", "")
                wait_time = section.get("wait_time", 1)
                
                if not button_selector:
                    continue
                
                self.logger.debug(f"展開區域: {section_name}")
                
                # 查找展開按鈕
                button = self.wait_for_element(By.XPATH, button_selector)
                
                if button:
                    # 點擊按鈕展開區域
                    try:
                        self.driver.execute_script("arguments[0].click();", button)
                        
                        # 等待區域展開
                        time.sleep(wait_time)
                        
                        # 驗證區域是否已展開
                        if target_selector:
                            target_element = self.wait_for_element(By.XPATH, target_selector, wait_time)
                            if not target_element:
                                self.logger.warning(f"區域 {section_name} 可能未成功展開")
                    except Exception as click_e:
                        self.logger.warning(f"點擊展開按鈕失敗: {str(click_e)}")
                else:
                    self.logger.warning(f"未找到區域 {section_name} 的展開按鈕")
                    
            except Exception as e:
                self.logger.warning(f"展開區域 {section.get('name', '')} 失敗: {str(e)}")
    
    def _wait_for_page_load(self, timeout: int = 10) -> None:
        """
        等待頁面加載完成
        
        Args:
            timeout: 超時時間（秒）
        """
        if not self.driver:
            return
            
        try:
            # 等待頁面加載完成
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # 額外等待一段時間
            time.sleep(random.uniform(0.5, 1.5))
                
        except Exception as e:
            self.logger.warning(f"等待頁面加載出錯: {str(e)}")
    
    def wait_for_element(self, by: By, selector: str, timeout: int = None) -> Optional[WebElement]:
        """
        等待元素出現
        
        Args:
            by: 定位方式
            selector: 選擇器
            timeout: 超時時間（秒）
            
        Returns:
            找到的元素，如果超時則返回None
        """
        if timeout is None:
            timeout = self.default_timeout
            
        if not self.driver:
            return None
            
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, selector)))
            return element
        except TimeoutException:
            self.logger.warning(f"等待元素超時: {by}={selector}")
            return None
        except Exception as e:
            self.logger.error(f"等待元素出錯: {str(e)}")
            return None
    
    def combine_data(self, list_data: Dict[str, Any], detail_data: Dict[str, Any], merge_strategy: str = "nested") -> Dict[str, Any]:
        """
        合併列表數據和詳情頁數據
        
        Args:
            list_data: 列表數據
            detail_data: 詳情頁數據
            merge_strategy: 合併策略（nested/flat/simple）
            
        Returns:
            合併後的數據
        """
        if merge_strategy == "nested":
            # 嵌套模式，將詳情頁數據作為子對象
            result = {
                "list_data": list_data.copy(),
                "detail_data": detail_data.copy(),
                "metadata": {
                    "timestamp": int(time.time())
                }
            }
            
            # 合併元數據
            for data_dict, key in [(list_data, "list_data"), (detail_data, "detail_data")]:
                if "_metadata" in data_dict:
                    metadata = data_dict.pop("_metadata", {})
                    result[key].pop("_metadata", None)
                    result["metadata"].update(metadata)
                
            return result
            
        elif merge_strategy == "flat":
            # 平鋪模式，所有數據放同一層級
            result = list_data.copy()
            
            # 合併元數據
            metadata = {}
            if "_metadata" in list_data:
                metadata.update(list_data.pop("_metadata", {}))
            if "_metadata" in detail_data:
                metadata.update(detail_data.pop("_metadata", {}))
            
            # 合併數據（詳情頁優先）
            result.update(detail_data)
            
            # 添加元數據
            result["metadata"] = {
                **metadata,
                "timestamp": int(time.time())
            }
            
            return result
        else:
            # 簡單合併
            result = list_data.copy()
            
            # 移除元數據，避免衝突
            list_metadata = list_data.pop("_metadata", {})
            detail_metadata = detail_data.pop("_metadata", {})
            
            # 合併數據
            result.update(detail_data)
            
            # 添加元數據
            result["_metadata"] = {
                **list_metadata,
                **detail_metadata,
                "timestamp": int(time.time())
            }
            
            return result
    
    def get_statistics(self) -> Dict[str, int]:
        """
        獲取提取統計信息
        
        Returns:
            統計數據字典
        """
        return {
            "extracted_items": self.extracted_items_count,
            "extracted_fields": self.extracted_fields_count,
            "extraction_errors": self.extraction_errors_count
        }
    
    def set_max_workers(self, num_workers: int) -> None:
        """
        設置並發工作線程數量
        
        Args:
            num_workers: 工作線程數量
        """
        if num_workers > 0:
            self.max_workers = num_workers
    
    def reset_statistics(self) -> None:
        """
        重置統計計數
        """
        self.extracted_items_count = 0
        self.extracted_fields_count = 0
        self.extraction_errors_count = 0
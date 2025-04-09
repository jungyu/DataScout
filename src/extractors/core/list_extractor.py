#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
列表頁提取器模組

專門處理列表頁面的數據提取。

主要功能：
- 列表項目定位和提取
- 並行數據提取
- 自動滾動加載
- 字段數據提取
- 元數據添加

使用示例：
    from src.extractors.core import ListExtractor
    from src.extractors.config import ListExtractionConfig, ExtractionConfig
    
    # 創建提取器
    extractor = ListExtractor(driver, base_url="https://example.com")
    
    # 配置提取
    config = ListExtractionConfig(
        container_xpath="//div[@class='list-container']",
        item_xpath=".//div[@class='item']",
        field_configs={
            "title": ExtractionConfig(type="text", xpath=".//h2"),
            "link": ExtractionConfig(type="url", xpath=".//a")
        }
    )
    
    # 提取數據
    items = extractor.extract(config)
"""

import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Union, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException

from .base_extractor import BaseExtractor
from ..config import ListExtractionConfig, ExtractionConfig
from ..utils.text_cleaner import TextCleaner


class ListExtractor(BaseExtractor):
    """列表頁提取器
    
    專門處理列表頁面的數據提取，支持並行提取和自動滾動加載。
    
    Attributes:
        driver: Selenium WebDriver實例
        base_url: 基礎URL
        logger: 日誌記錄器
        default_timeout: 默認等待超時時間
        max_workers: 並行提取的最大工作線程數
        text_cleaner: 文本清理工具
    """
    
    def __init__(
        self, 
        driver: Optional[webdriver.Remote] = None, 
        base_url: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        timeout: int = 10,
        max_workers: int = 4
    ):
        """
        初始化列表頁提取器
        
        Args:
            driver: Selenium WebDriver實例
            base_url: 基礎URL，用於URL標準化
            logger: 日誌記錄器
            timeout: 默認等待超時時間(秒)
            max_workers: 並行提取的最大工作線程數
        """
        super().__init__(driver, base_url, logger, timeout)
        self.max_workers = max_workers
        self.text_cleaner = TextCleaner()
    
    def extract(self, config: ListExtractionConfig) -> List[Dict[str, Any]]:
        """
        提取列表頁面的項目
        
        Args:
            config: 列表提取配置
            
        Returns:
            列表項目數據
        """
        # 委派給extract_list_items方法
        return self.extract_list_items(config)
    
    def extract_list_items(self, config: ListExtractionConfig) -> List[Dict[str, Any]]:
        """
        提取列表頁面的項目
        
        Args:
            config: 列表提取配置
            
        Returns:
            列表項目數據
        """
        if not self.driver:
            self.logger.warning("WebDriver未初始化")
            return []
            
        try:
            # 等待並獲取容器元素
            container_xpath = config.container_xpath or "//body"
            container = self.wait_for_element(By.XPATH, container_xpath)
            
            if not container:
                self.logger.error(f"找不到列表容器: {container_xpath}")
                return []
            
            # 滾動頁面以確保所有項目加載
            if config.scroll_after_load:
                self._scroll_to_load_items()
            
            # 等待列表項目
            item_xpath = config.item_xpath
            if not item_xpath:
                self.logger.error("未指定列表項目選擇器")
                return []
                
            # 查找所有列表項目
            items = container.find_elements(By.XPATH, item_xpath)
            self.logger.info(f"找到 {len(items)} 個列表項目")
            
            # 如果沒有找到項目，嘗試等待更長時間
            if not items:
                self.logger.warning("未找到列表項目，嘗試等待更長時間")
                time.sleep(2)  # 額外等待
                items = container.find_elements(By.XPATH, item_xpath)
                self.logger.info(f"重試後找到 {len(items)} 個列表項目")
            
            if not items:
                self.logger.warning("仍未找到列表項目，可能頁面結構有變化")
                return []
            
            # 決定是否使用並行提取
            use_parallel = config.use_parallel and len(items) > 5 and self.max_workers > 1
            
            if use_parallel:
                # 並行提取
                results = self._extract_items_parallel(items, config.field_configs)
            else:
                # 串行提取
                results = []
                for i, item in enumerate(items):
                    try:
                        data = self.extract_item(item, config.field_configs)
                        data['_metadata'] = {'index': i}
                        results.append(data)
                        
                        # 添加短暫延遲以減輕服務器負擔
                        if i < len(items) - 1 and config.extraction_delay > 0:
                            time.sleep(config.extraction_delay)
                    except Exception as e:
                        self.logger.warning(f"提取列表項目 #{i} 失敗: {str(e)}")
            
            # 添加元數據
            for i, data in enumerate(results):
                if '_metadata' not in data:
                    data['_metadata'] = {}
                    
                data['_metadata'].update({
                    'source': config.source_name,
                    'extraction_time': int(time.time()),
                    'page_url': self.driver.current_url
                })
            
            # 更新統計信息
            self.extracted_items_count += len(results)
            self.extracted_fields_count += sum(len(item) for item in results)
            
            self.logger.info(f"成功提取 {len(results)} 個列表項目")
            return results
            
        except Exception as e:
            self.logger.error(f"提取列表項目時出錯: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
            self.extraction_errors_count += 1
            return []
    
    def _extract_items_parallel(
        self, 
        items: List[WebElement], 
        field_configs: Dict[str, ExtractionConfig]
    ) -> List[Dict[str, Any]]:
        """
        並行提取列表項目數據
        
        Args:
            items: 列表項目元素
            field_configs: 字段提取配置
            
        Returns:
            提取的數據列表
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交提取任務
            futures = {}
            for i, item in enumerate(items):
                future = executor.submit(self.extract_item, item, field_configs)
                futures[future] = i
            
            # 收集結果
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    data = future.result()
                    data['_metadata'] = {'index': idx}
                    results.append(data)
                except Exception as e:
                    self.logger.error(f"並行提取項目 #{idx} 失敗: {str(e)}")
                    self.extraction_errors_count += 1
        
        # 按原始順序排序
        return sorted(results, key=lambda x: x['_metadata']['index'])
    
    def extract_item(
        self, 
        item_element: WebElement, 
        field_configs: Dict[str, ExtractionConfig]
    ) -> Dict[str, Any]:
        """
        從單個列表項目元素中提取數據
        
        Args:
            item_element: 列表項目元素
            field_configs: 字段提取配置
            
        Returns:
            提取的數據
        """
        result = {}
        
        for field_name, field_config in field_configs.items():
            try:
                # 在項目元素的上下文中查找字段
                elements = self._find_elements(item_element, field_config)
                
                # 根據配置提取數據
                value = self._extract_field_value(elements, field_config)
                
                # 篩選非None值
                if value is not None:
                    result[field_name] = value
                
            except Exception as e:
                self.logger.debug(f"提取字段 '{field_name}' 失敗: {str(e)}")
                
                # 使用默認值
                if field_config.default is not None:
                    result[field_name] = field_config.default
        
        return result
    
    def _find_elements(
        self, 
        parent: WebElement, 
        config: ExtractionConfig
    ) -> List[WebElement]:
        """
        在父元素中查找匹配的元素
        
        Args:
            parent: 父元素
            config: 提取配置
            
        Returns:
            匹配的元素列表
        """
        try:
            if config.xpath:
                return parent.find_elements(By.XPATH, config.xpath)
            elif config.css:
                return parent.find_elements(By.CSS_SELECTOR, config.css)
            elif config.id:
                return parent.find_elements(By.ID, config.id)
            elif config.class_name:
                return parent.find_elements(By.CLASS_NAME, config.class_name)
            elif config.name:
                return parent.find_elements(By.NAME, config.name)
            elif config.tag_name:
                return parent.find_elements(By.TAG_NAME, config.tag_name)
            else:
                self.logger.warning("未指定元素選擇器")
                return []
        except StaleElementReferenceException:
            self.logger.warning("元素已過期，無法查找")
            return []
        except Exception as e:
            self.logger.warning(f"查找元素失敗: {str(e)}")
            return []
    
    def _extract_field_value(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Any:
        """
        根據配置提取字段值
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            提取的值
        """
        if not elements:
            return config.default
        
        try:
            if config.type == 'text':
                return self._extract_text(elements, config)
            elif config.type == 'attribute':
                return self._extract_attribute(elements, config)
            elif config.type == 'url':
                return self._extract_url(elements, config)
            elif config.type == 'html':
                return self._extract_html(elements, config)
            elif config.type == 'number':
                return self._extract_number(elements, config)
            elif config.type == 'date':
                return self._extract_date(elements, config)
            elif config.type == 'compound':
                return self._extract_compound(elements, config)
            else:
                return config.default
        except Exception as e:
            self.logger.debug(f"提取字段值失敗: {str(e)}")
            return config.default
    
    def _extract_text(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Union[str, List[str], None]:
        """
        提取文本內容
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            提取的文本
        """
        if not elements:
            return config.default
        
        try:
            if config.multiple:
                # 提取多個元素的文本
                texts = []
                for element in elements:
                    text = element.text.strip()
                    if text:
                        texts.append(text)
                return texts if texts else config.default
            else:
                # 提取第一個元素的文本
                text = elements[0].text.strip()
                return text if text else config.default
        except Exception as e:
            self.logger.debug(f"提取文本失敗: {str(e)}")
            return config.default
    
    def _extract_attribute(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Union[str, List[str], None]:
        """
        提取屬性值
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            提取的屬性值
        """
        if not elements or not config.attribute:
            return config.default
        
        try:
            if config.multiple:
                # 提取多個元素的屬性
                values = []
                for element in elements:
                    value = element.get_attribute(config.attribute)
                    if value:
                        values.append(value)
                return values if values else config.default
            else:
                # 提取第一個元素的屬性
                value = elements[0].get_attribute(config.attribute)
                return value if value else config.default
        except Exception as e:
            self.logger.debug(f"提取屬性失敗: {str(e)}")
            return config.default
    
    def _extract_url(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Union[str, List[str], None]:
        """
        提取URL
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            提取的URL
        """
        if not elements:
            return config.default
        
        try:
            if config.multiple:
                # 提取多個元素的URL
                urls = []
                for element in elements:
                    url = element.get_attribute('href')
                    if url:
                        # 標準化URL
                        url = self.url_normalizer.normalize(url, self.base_url)
                        urls.append(url)
                return urls if urls else config.default
            else:
                # 提取第一個元素的URL
                url = elements[0].get_attribute('href')
                if url:
                    # 標準化URL
                    return self.url_normalizer.normalize(url, self.base_url)
                return config.default
        except Exception as e:
            self.logger.debug(f"提取URL失敗: {str(e)}")
            return config.default
    
    def _extract_html(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Union[str, List[str], None]:
        """
        提取HTML內容
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            提取的HTML
        """
        if not elements:
            return config.default
        
        try:
            if config.multiple:
                # 提取多個元素的HTML
                htmls = []
                for element in elements:
                    html = element.get_attribute('outerHTML')
                    if html:
                        # 清理HTML
                        html = self.html_cleaner.clean(html)
                        htmls.append(html)
                return htmls if htmls else config.default
            else:
                # 提取第一個元素的HTML
                html = elements[0].get_attribute('outerHTML')
                if html:
                    # 清理HTML
                    return self.html_cleaner.clean(html)
                return config.default
        except Exception as e:
            self.logger.debug(f"提取HTML失敗: {str(e)}")
            return config.default
    
    def _extract_number(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Union[int, float, List[Union[int, float]], None]:
        """
        提取數字
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            提取的數字
        """
        if not elements:
            return config.default
        
        try:
            if config.multiple:
                # 提取多個元素的數字
                numbers = []
                for element in elements:
                    text = element.text.strip()
                    if text:
                        number = self.number_parser.parse(text)
                        if number is not None:
                            numbers.append(number)
                return numbers if numbers else config.default
            else:
                # 提取第一個元素的數字
                text = elements[0].text.strip()
                if text:
                    return self.number_parser.parse(text)
                return config.default
        except Exception as e:
            self.logger.debug(f"提取數字失敗: {str(e)}")
            return config.default
    
    def _extract_date(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Union[str, List[str], None]:
        """
        提取日期
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            提取的日期
        """
        if not elements:
            return config.default
        
        try:
            if config.multiple:
                # 提取多個元素的日期
                dates = []
                for element in elements:
                    text = element.text.strip()
                    if text:
                        date = self.date_parser.parse(text)
                        if date:
                            dates.append(date)
                return dates if dates else config.default
            else:
                # 提取第一個元素的日期
                text = elements[0].text.strip()
                if text:
                    return self.date_parser.parse(text)
                return config.default
        except Exception as e:
            self.logger.debug(f"提取日期失敗: {str(e)}")
            return config.default
    
    def _extract_compound(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """
        提取複合字段
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            提取的複合字段
        """
        if not elements or not config.compound_fields:
            return config.default
        
        try:
            if config.multiple:
                # 提取多個元素的複合字段
                compounds = []
                for element in elements:
                    compound = {}
                    for field_name, field_config in config.compound_fields.items():
                        # 在當前元素中查找子元素
                        sub_elements = self._find_elements(element, field_config)
                        # 提取子字段值
                        value = self._extract_field_value(sub_elements, field_config)
                        if value is not None:
                            compound[field_name] = value
                    if compound:
                        compounds.append(compound)
                return compounds if compounds else config.default
            else:
                # 提取第一個元素的複合字段
                compound = {}
                for field_name, field_config in config.compound_fields.items():
                    # 在當前元素中查找子元素
                    sub_elements = self._find_elements(elements[0], field_config)
                    # 提取子字段值
                    value = self._extract_field_value(sub_elements, field_config)
                    if value is not None:
                        compound[field_name] = value
                return compound if compound else config.default
        except Exception as e:
            self.logger.debug(f"提取複合字段失敗: {str(e)}")
            return config.default
    
    def _scroll_to_load_items(self):
        """
        滾動頁面以加載更多項目
        
        通過滾動頁面到底部並檢查頁面高度變化來加載更多內容。
        """
        if not self.driver:
            return
        
        try:
            # 獲取初始頁面高度
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # 滾動次數
            scroll_attempts = 0
            max_attempts = 5
            
            while scroll_attempts < max_attempts:
                # 滾動至底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # 等待頁面加載
                time.sleep(1.5)
                
                # 獲取新頁面高度
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                # 如果頁面高度未變，則停止滾動
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scroll_attempts += 1
                
            self.logger.debug(f"頁面滾動完成，共滾動 {scroll_attempts} 次")
            
            # 滾動回頁面頂部
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            
        except Exception as e:
            self.logger.warning(f"滾動頁面加載項目時出錯: {str(e)}")
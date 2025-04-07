#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
列表頁提取器模組

專門處理列表頁面的數據提取
"""

import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Union

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from .base_extractor import BaseExtractor
from ..config import ListExtractionConfig, ExtractionConfig
from ..utils.text_cleaner import TextCleaner


class ListExtractor(BaseExtractor):
    """列表頁提取器，專門處理列表頁面的數據提取"""
    
    def __init__(
        self, 
        driver: Optional[webdriver.Remote] = None, 
        base_url: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        timeout: int = 10,
        max_workers: int = 4  # 並行提取的最大工作線程數
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
            self.logger.error("WebDriver未初始化")
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
            
            self.logger.info(f"成功提取 {len(results)} 個列表項目")
            return results
            
        except Exception as e:
            self.logger.error(f"提取列表項目時出錯: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
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
                if field_config.type == 'text':
                    value = self._extract_text(elements, field_config)
                elif field_config.type == 'attribute':
                    value = self._extract_attribute(elements, field_config)
                elif field_config.type == 'url':
                    value = self._extract_url(elements, field_config)
                elif field_config.type == 'html':
                    value = self._extract_html(elements, field_config)
                elif field_config.type == 'number':
                    value = self._extract_number(elements, field_config)
                elif field_config.type == 'date':
                    value = self._extract_date(elements, field_config)
                elif field_config.type == 'compound':
                    value = self._extract_compound(elements, field_config)
                else:
                    value = field_config.default
                
                # 篩選非None值
                if value is not None:
                    result[field_name] = value
                
            except Exception as e:
                self.logger.debug(f"提取字段 '{field_name}' 失敗: {str(e)}")
                
                # 使用默認值
                if field_config.default is not None:
                    result[field_name] = field_config.default
        
        return result
    
    def _scroll_to_load_items(self):
        """滾動頁面以加載更多項目"""
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
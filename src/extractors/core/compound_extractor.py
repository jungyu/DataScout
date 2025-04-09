#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
複合字段提取器模組

專門處理複雜數據結構和嵌套字段的提取，支持多種數據類型和提取策略。

主要功能：
- 複合字段提取
- 嵌套數據結構處理
- JSON數據提取
- 表格數據提取
- 結構化數據提取
- 表單數據提取

使用示例：
    from src.extractors.core import CompoundExtractor
    from src.extractors.config import ExtractionConfig
    
    # 創建提取器
    extractor = CompoundExtractor(driver, base_url="https://example.com")
    
    # 配置提取
    config = ExtractionConfig(
        xpath="//div[@class='product']",
        type="compound",
        multiple=True,
        nested_fields={
            "title": ExtractionConfig(xpath=".//h2", type="text"),
            "price": ExtractionConfig(xpath=".//span[@class='price']", type="number"),
            "description": ExtractionConfig(xpath=".//p", type="text"),
            "specifications": ExtractionConfig(
                xpath=".//table",
                type="table",
                headers_xpath=".//th",
                rows_xpath=".//tr[td]"
            )
        }
    )
    
    # 提取數據
    data = extractor.extract(element, config)
"""

import json
import logging
import re
import time
from typing import Dict, List, Any, Optional, Union, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

from src.extractors.config import ExtractionConfig
from .base_extractor import BaseExtractor


class CompoundExtractor(BaseExtractor):
    """
    複合字段提取器，處理嵌套數據結構和複雜字段的提取
    
    支持從HTML結構、JSON數據或表格數據中提取複雜的嵌套數據結構。
    
    Attributes:
        driver: Selenium WebDriver實例
        logger: 日誌記錄器
        base_url: 基礎URL，用於URL標準化
        default_timeout: 默認等待超時時間
        extracted_fields_count: 已提取字段數
        extraction_errors_count: 提取錯誤數
    """
    
    def __init__(
        self, 
        driver: Optional[webdriver.Remote] = None, 
        base_url: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        timeout: int = 10
    ):
        """
        初始化複合字段提取器
        
        Args:
            driver: Selenium WebDriver實例
            base_url: 基礎URL，用於URL標準化
            logger: 日誌記錄器
            timeout: 默認等待超時時間(秒)
        """
        super().__init__(driver, base_url, logger, timeout)
        self.extracted_fields_count = 0
        self.extraction_errors_count = 0
    
    def extract(
        self, 
        element: WebElement, 
        config: ExtractionConfig
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        從元素中提取複合字段數據
        
        Args:
            element: WebElement元素
            config: 提取配置
            
        Returns:
            提取的複合數據，可能是字典或字典列表
        """
        # 檢查是否有嵌套字段配置
        if not config.nested_fields:
            self.logger.warning("複合字段提取需要嵌套字段配置")
            return {} if not config.multiple else []
        
        return self._extract_compound_data(element, config)
    
    def _extract_compound_data(
        self, 
        element: WebElement, 
        config: ExtractionConfig
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        從元素中提取複合數據
        
        Args:
            element: WebElement元素
            config: 提取配置
            
        Returns:
            提取的複合數據
        """
        # 處理多元素提取
        if config.multiple:
            # 查找所有匹配的子元素
            sub_elements = self._find_elements(element, config)
            
            # 提取所有子元素的數據
            results = []
            for idx, sub_el in enumerate(sub_elements):
                try:
                    data = self._extract_nested_fields(sub_el, config.nested_fields)
                    if data:  # 只添加非空結果
                        # 添加索引信息到元數據
                        if "_metadata" not in data:
                            data["_metadata"] = {}
                        data["_metadata"]["index"] = idx
                        results.append(data)
                        self.extracted_fields_count += 1
                except Exception as e:
                    self.logger.warning(f"提取複合字段組 #{idx} 失敗: {str(e)}")
                    self.extraction_errors_count += 1
            
            return results
        else:
            # 單元素提取
            try:
                result = self._extract_nested_fields(element, config.nested_fields)
                if result:
                    self.extracted_fields_count += 1
                return result
            except Exception as e:
                self.logger.warning(f"提取單一複合字段組失敗: {str(e)}")
                self.extraction_errors_count += 1
                return {}
    
    def _extract_nested_fields(
        self, 
        element: WebElement, 
        nested_fields: Dict[str, ExtractionConfig]
    ) -> Dict[str, Any]:
        """
        從元素中提取嵌套字段
        
        Args:
            element: WebElement元素
            nested_fields: 嵌套字段配置字典
            
        Returns:
            提取的嵌套字段數據
        """
        result = {}
        
        # 遞歸提取所有嵌套字段
        for field_name, field_config in nested_fields.items():
            try:
                # 從當前元素上下文中查找字段元素
                field_elements = self._find_elements(element, field_config)
                
                if not field_elements:
                    # 使用默認值
                    if field_config.default is not None:
                        result[field_name] = field_config.default
                    continue
                
                # 根據字段類型提取數據
                if field_config.type == "text":
                    value = self._extract_text(field_elements, field_config)
                elif field_config.type == "attribute":
                    value = self._extract_attribute(field_elements, field_config)
                elif field_config.type == "html":
                    value = self._extract_html(field_elements, field_config)
                elif field_config.type == "url":
                    value = self._extract_url(field_elements, field_config)
                elif field_config.type == "date":
                    value = self._extract_date(field_elements, field_config)
                elif field_config.type == "number":
                    value = self._extract_number(field_elements, field_config)
                elif field_config.type == "json":
                    value = self._extract_json(field_elements, field_config)
                elif field_config.type == "table":
                    value = self._extract_table(field_elements, field_config)
                elif field_config.type == "compound":
                    # 遞歸提取複合字段
                    if field_config.nested_fields:
                        if field_config.multiple:
                            # 提取多個子複合字段
                            value = []
                            for sub_el in field_elements:
                                sub_value = self._extract_nested_fields(
                                    sub_el, field_config.nested_fields
                                )
                                if sub_value:  # 只添加非空結果
                                    value.append(sub_value)
                        else:
                            # 提取單個子複合字段
                            value = self._extract_nested_fields(
                                field_elements[0], field_config.nested_fields
                            )
                    else:
                        value = None
                else:
                    value = field_config.default
                
                # 應用自定義轉換函數
                if field_config.transform and value is not None:
                    try:
                        value = field_config.transform(value)
                    except Exception as e:
                        self.logger.warning(f"應用轉換函數失敗: {str(e)}")
                
                # 只保存非None值
                if value is not None:
                    result[field_name] = value
                
            except Exception as e:
                self.logger.warning(f"提取嵌套字段 '{field_name}' 失敗: {str(e)}")
                self.extraction_errors_count += 1
                # 使用默認值
                if field_config.default is not None:
                    result[field_name] = field_config.default
        
        return result
    
    def _extract_json(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """
        從元素中提取JSON數據
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            解析後的JSON數據
        """
        if not elements:
            return None
            
        try:
            element = elements[0]
            # 嘗試不同的方式獲取JSON數據
            
            # 1. 從元素文本中提取
            json_str = element.text.strip()
            
            # 2. 如未找到文本，嘗試從屬性中提取
            if not json_str and config.attribute:
                json_str = element.get_attribute(config.attribute)
            
            # 3. 如未找到屬性，嘗試從innerHTML中提取
            if not json_str:
                json_str = element.get_attribute("innerHTML")
                
                # 使用正則從腳本標籤中提取JSON
                match = re.search(r'var\s+(\w+)\s*=\s*({.*?});', json_str, re.DOTALL)
                if match:
                    json_str = match.group(2)
            
            # 清理可能的非JSON字符
            if json_str:
                # 移除JavaScript注釋
                json_str = re.sub(r'//.*?(\n|$)', '', json_str)
                json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
                
                # 嘗試解析JSON
                data = json.loads(json_str)
                
                # 如果有指定選擇器路徑，從解析後的數據中提取子節點
                json_path = config.json_path if hasattr(config, 'json_path') else None
                if json_path and isinstance(data, dict):
                    for key in json_path.split('.'):
                        if key in data:
                            data = data[key]
                        else:
                            self.logger.warning(f"JSON路徑 '{json_path}' 的鍵 '{key}' 不存在")
                            return None
                
                return data
            else:
                return None
                
        except json.JSONDecodeError as e:
            self.logger.warning(f"JSON解析失敗: {str(e)}")
            self.extraction_errors_count += 1
            return None
        except Exception as e:
            self.logger.warning(f"提取JSON數據失敗: {str(e)}")
            self.extraction_errors_count += 1
            return None
    
    def _extract_table(
        self, 
        elements: List[WebElement], 
        config: ExtractionConfig
    ) -> List[Dict[str, Any]]:
        """
        從元素中提取表格數據
        
        Args:
            elements: 元素列表
            config: 提取配置
            
        Returns:
            表格數據列表
        """
        if not elements:
            return []
            
        table_data = []
        try:
            table = elements[0]
            
            # 提取表頭
            headers_xpath = config.headers_xpath if hasattr(config, 'headers_xpath') else ".//th"
            header_cells = table.find_elements(By.XPATH, headers_xpath)
            headers = [cell.text.strip() for cell in header_cells]
            
            # 如果沒有表頭，使用配置的列名或生成默認列名
            if not headers:
                headers = getattr(config, 'column_names', None) or [f"column_{i}" for i in range(10)]
            
            # 提取表格行
            rows_xpath = config.rows_xpath if hasattr(config, 'rows_xpath') else ".//tr[td]"
            rows = table.find_elements(By.XPATH, rows_xpath)
            
            for row in rows:
                # 提取行中的單元格
                cells_xpath = config.cells_xpath if hasattr(config, 'cells_xpath') else ".//td"
                cells = row.find_elements(By.XPATH, cells_xpath)
                
                # 確保有足夠的列名
                while len(headers) < len(cells):
                    headers.append(f"column_{len(headers)}")
                
                # 創建行數據
                row_data = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        # 清理單元格文本
                        cell_text = cell.text.strip()
                        # 跳過空單元格
                        if cell_text:
                            row_data[headers[i]] = cell_text
                
                # 只添加非空行
                if row_data:
                    table_data.append(row_data)
                    self.extracted_fields_count += 1
            
            return table_data
            
        except Exception as e:
            self.logger.warning(f"提取表格數據失敗: {str(e)}")
            self.extraction_errors_count += 1
            return []
    
    def extract_structured_data(
        self, 
        script_type: str = "application/ld+json"
    ) -> List[Dict[str, Any]]:
        """
        提取頁面結構化數據
        
        Args:
            script_type: 腳本類型，默認為JSON-LD
            
        Returns:
            提取的結構化數據列表
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return []
        
        try:
            # 查找所有指定類型的腳本標籤
            scripts = self.driver.find_elements(
                By.XPATH, f"//script[@type='{script_type}']"
            )
            
            results = []
            for script in scripts:
                try:
                    # 獲取腳本內容並解析JSON
                    json_text = script.get_attribute("innerHTML")
                    if json_text:
                        data = json.loads(json_text)
                        results.append(data)
                        self.extracted_fields_count += 1
                except json.JSONDecodeError:
                    self.logger.debug(f"無法解析JSON: {script.get_attribute('innerHTML')[:100]}...")
                    self.extraction_errors_count += 1
                except Exception as e:
                    self.logger.warning(f"提取結構化數據時出錯: {str(e)}")
                    self.extraction_errors_count += 1
            
            return results
            
        except Exception as e:
            self.logger.error(f"提取結構化數據失敗: {str(e)}")
            self.extraction_errors_count += 1
            return []
    
    def extract_form_data(
        self, 
        form_xpath: str
    ) -> Dict[str, Any]:
        """
        提取表單數據
        
        Args:
            form_xpath: 表單元素XPath
            
        Returns:
            表單字段數據字典
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return {}
        
        try:
            # 查找表單元素
            form_element = self.wait_for_element(By.XPATH, form_xpath)
            if not form_element:
                self.logger.warning(f"找不到表單: {form_xpath}")
                return {}
                
            # 查找所有輸入字段
            form_data = {}
            
            # 文本輸入、密碼、隱藏字段等
            input_fields = form_element.find_elements(By.XPATH, ".//input[@name]")
            for field in input_fields:
                name = field.get_attribute("name")
                value = field.get_attribute("value") or ""
                field_type = field.get_attribute("type") or "text"
                
                # 跳過按鈕類型
                if field_type in ["submit", "button", "reset"]:
                    continue
                
                form_data[name] = value
                self.extracted_fields_count += 1
            
            # 文本區域
            textareas = form_element.find_elements(By.XPATH, ".//textarea[@name]")
            for field in textareas:
                name = field.get_attribute("name")
                value = field.get_attribute("value") or field.text or ""
                form_data[name] = value
                self.extracted_fields_count += 1
            
            # 選擇框
            selects = form_element.find_elements(By.XPATH, ".//select[@name]")
            for select in selects:
                name = select.get_attribute("name")
                selected_option = select.find_elements(By.XPATH, "./option[@selected]")
                value = selected_option[0].get_attribute("value") if selected_option else ""
                form_data[name] = value
                self.extracted_fields_count += 1
            
            # 單選和複選框
            radios_and_checkboxes = form_element.find_elements(
                By.XPATH, ".//input[@type='radio' or @type='checkbox'][@name]"
            )
            radio_groups = {}
            checkbox_groups = {}
            
            for field in radios_and_checkboxes:
                name = field.get_attribute("name")
                value = field.get_attribute("value")
                is_checked = field.get_attribute("checked") is not None
                field_type = field.get_attribute("type")
                
                if field_type == "radio":
                    # 單選按鈕分組
                    if name not in radio_groups:
                        radio_groups[name] = None
                    if is_checked:
                        radio_groups[name] = value
                elif field_type == "checkbox":
                    # 複選框分組
                    if name not in checkbox_groups:
                        checkbox_groups[name] = []
                    if is_checked:
                        checkbox_groups[name].append(value)
                
                self.extracted_fields_count += 1
            
            # 合併單選結果
            form_data.update(radio_groups)
            
            # 合併複選結果
            form_data.update(checkbox_groups)
            
            return form_data
            
        except Exception as e:
            self.logger.error(f"提取表單數據失敗: {str(e)}")
            self.extraction_errors_count += 1
            return {}
    
    def get_statistics(self) -> Dict[str, int]:
        """
        獲取提取統計信息
        
        Returns:
            包含提取統計的字典
        """
        return {
            "extracted_fields": self.extracted_fields_count,
            "extraction_errors": self.extraction_errors_count
        }

    def reset_statistics(self) -> None:
        """重置統計計數"""
        self.extracted_fields_count = 0
        self.extraction_errors_count = 0
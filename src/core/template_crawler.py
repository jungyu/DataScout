#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TemplateCrawler 模組
實作基於模板的爬蟲核心邏輯
"""

import os
import time
import logging
import random
import json
from typing import Dict, List, Any, Optional, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    StaleElementReferenceException
)

from .config_loader import ConfigLoader
from .webdriver_manager import WebDriverManager


class TemplateCrawler:
    """模板化爬蟲的核心類"""
    
    def __init__(
        self, 
        template_file: str, 
        config_file: Optional[str] = None,
        logger=None
    ):
        """
        初始化模板爬蟲

        Args:
            template_file: 模板文件路徑
            config_file: 配置文件路徑，如果不提供則使用默認配置
            logger: 日誌記錄器，如果為None則創建新的
        """
        self.logger = logger or logging.getLogger(__name__)
        self.template_file = template_file
        self.config_file = config_file
        
        # 載入模板和配置
        self.config_loader = ConfigLoader(self.logger)
        self.template = self._load_template()
        self.config = self._load_config()
        
        # 初始化WebDriver管理器
        webdriver_config = self.config.get("webdriver_config", {})
        self.webdriver_manager = WebDriverManager(webdriver_config, self.logger)
        
        # 爬蟲狀態
        self.driver = None
        self.current_page = 1
        self.items_collected = 0
        self.running = False
        self.stop_requested = False
        
        # 解析模板設定
        self.site_name = self.template.get("site_name", "")
        self.base_url = self.template.get("base_url", "")
        self.encoding = self.template.get("encoding", "utf-8")
        self.description = self.template.get("description", "")
        self.version = self.template.get("version", "1.0.0")
        
        # 延遲設定
        self.delays = self._parse_delays()
        
        # 高級設定
        self.advanced_settings = self.template.get("advanced_settings", {})
        
        self.logger.info(f"初始化模板爬蟲: {self.site_name}, 版本: {self.version}")
    
    def _load_template(self) -> Dict[str, Any]:
        """載入爬蟲模板文件"""
        try:
            return self.config_loader.load_template(self.template_file)
        except Exception as e:
            self.logger.error(f"載入模板文件失敗: {str(e)}")
            return {}
    
    def _load_config(self) -> Dict[str, Any]:
        """載入配置文件"""
        try:
            # 如果提供了配置文件路徑
            if self.config_file and os.path.exists(self.config_file):
                return self.config_loader.load_config(self.config_file)
            
            # 否則使用默認配置
            default_config = {
                "webdriver_config": {
                    "browser_type": "chrome",
                    "headless": False,
                    "disable_images": True,
                    "enable_stealth": True
                },
                "output_config": {
                    "output_dir": "output",
                    "output_format": "json"
                },
                "request_config": {
                    "retries": 3,
                    "timeout": 30
                }
            }
            
            self.logger.info("使用默認配置")
            return default_config
        except Exception as e:
            self.logger.error(f"載入配置文件失敗: {str(e)}")
            return {}
    
    def _parse_delays(self) -> Dict[str, Dict[str, float]]:
        """解析延遲設定，確保數值有效"""
        delays = self.template.get("delays", {})
        processed_delays = {}
        
        # 解析每個延遲類型
        for delay_type, delay_value in delays.items():
            if isinstance(delay_value, (int, float)):
                # 如果是數字，則使用固定延遲
                processed_delays[delay_type] = {
                    "min": float(delay_value),
                    "max": float(delay_value)
                }
            elif isinstance(delay_value, dict):
                # 如果是字典，則提取min和max值
                min_val = float(delay_value.get("min", 0))
                max_val = float(delay_value.get("max", min_val * 2))
                
                # 確保min不大於max
                if min_val > max_val:
                    min_val, max_val = max_val, min_val
                
                processed_delays[delay_type] = {
                    "min": min_val,
                    "max": max_val
                }
            else:
                # 使用默認值
                processed_delays[delay_type] = {
                    "min": 1.0,
                    "max": 3.0
                }
        
        # 確保主要延遲類型存在
        required_delays = ["page_load", "between_pages", "between_items"]
        for delay_type in required_delays:
            if delay_type not in processed_delays:
                processed_delays[delay_type] = {
                    "min": 1.0,
                    "max": 3.0
                }
        
        return processed_delays
    
    def _random_delay(self, delay_type: str = "page_load") -> None:
        """
        根據配置的延遲範圍，生成隨機延遲時間並等待
        
        Args:
            delay_type: 延遲類型，如 "page_load", "between_pages", "between_items"
        """
        delay_config = self.delays.get(delay_type, {"min": 1.0, "max": 3.0})
        min_delay = delay_config.get("min", 1.0)
        max_delay = delay_config.get("max", 3.0)
        
        delay = random.uniform(min_delay, max_delay)
        self.logger.debug(f"隨機延遲 {delay_type}: {delay:.2f} 秒")
        time.sleep(delay)
    
    def _build_url(self, page: int = 1) -> str:
        """
        構建爬取URL
        
        Args:
            page: 頁碼
            
        Returns:
            完整的URL
        """
        # 檢查是否有分頁配置
        pagination = self.template.get("pagination", {})
        url_pattern = pagination.get("url_pattern", "")
        
        if url_pattern:
            # 使用格式化字符串替換URL模式中的變量
            try:
                # 準備URL參數
                url_params = {
                    "base_url": self.base_url,
                    "page": page,
                    "page_number": page
                }
                
                # 從search_parameters獲取更多參數
                search_params = self.template.get("search_parameters", {})
                for param_name, param_config in search_params.items():
                    url_params[param_name] = param_config.get("default", "")
                
                # 使用高級URL格式設定
                url_format = self.advanced_settings.get("url_format", {})
                
                # 檢查是否需要值映射
                value_mapping = url_format.get("value_mapping", {})
                parameter_mapping = url_format.get("parameter_mapping", {})
                
                # 應用值映射
                for param_name, mapping in value_mapping.items():
                    if param_name in url_params:
                        original_value = url_params[param_name]
                        mapped_value = mapping.get(original_value, original_value)
                        url_params[param_name] = mapped_value
                
                # 應用參數映射
                for old_param, new_param in parameter_mapping.items():
                    if old_param in url_params:
                        url_params[new_param] = url_params[old_param]
                
                # 檢查是否需要編碼參數
                if url_format.get("encode_parameters", False):
                    import urllib.parse
                    for param_name in list(url_params.keys()):
                        if isinstance(url_params[param_name], str):
                            url_params[param_name] = urllib.parse.quote(url_params[param_name])
                
                # 格式化URL
                return url_pattern.format(**url_params)
            except KeyError as e:
                self.logger.error(f"URL格式化失敗，缺少參數: {str(e)}")
                return self.base_url
            except Exception as e:
                self.logger.error(f"構建URL失敗: {str(e)}")
                return self.base_url
        else:
            # 沒有URL模式，則使用基礎URL加上簡單的頁碼參數
            if "?" in self.base_url:
                return f"{self.base_url}&page={page}"
            else:
                return f"{self.base_url}?page={page}"
    
    def start(self, max_pages: Optional[int] = None, max_items: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        開始爬蟲流程
        
        Args:
            max_pages: 最大爬取頁數，如果為None則使用模板中的設定
            max_items: 最大爬取項目數，如果為None則不限制
            
        Returns:
            爬取的資料列表
        """
        self.logger.info(f"開始爬取 {self.site_name}")
        
        # 初始化狀態
        self.running = True
        self.stop_requested = False
        self.current_page = 1
        self.items_collected = 0
        
        # 設置最大頁數
        if max_pages is None:
            pagination = self.template.get("pagination", {})
            max_pages = pagination.get("max_pages", 1)
        
        # 設置最大項目數
        if max_items is None:
            max_items = self.advanced_settings.get("max_results", 1000)
        
        # 初始化WebDriver
        try:
            self.driver = self.webdriver_manager.create_driver()
        except Exception as e:
            self.logger.error(f"初始化WebDriver失敗: {str(e)}")
            self.running = False
            return []
        
        all_data = []
        
        try:
            # 爬取頁面
            while (self.current_page <= max_pages and 
                   self.items_collected < max_items and 
                   not self.stop_requested):
                
                # 爬取當前頁面
                page_data = self._crawl_page(self.current_page)
                
                if not page_data:
                    self.logger.warning(f"頁面 {self.current_page} 未獲取到資料，結束爬取")
                    break
                
                # 添加資料
                all_data.extend(page_data)
                self.items_collected += len(page_data)
                
                self.logger.info(f"已爬取 {self.current_page} 頁，共 {self.items_collected} 項")
                
                # 檢查是否有下一頁
                if not self._has_next_page():
                    self.logger.info("沒有下一頁，結束爬取")
                    break
                
                # 轉到下一頁
                self.current_page += 1
                
                # 頁面間延遲
                self._random_delay("between_pages")
            
            return all_data
            
        except KeyboardInterrupt:
            self.logger.info("收到中斷信號，停止爬取")
            return all_data
        except Exception as e:
            self.logger.error(f"爬取過程中發生錯誤: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return all_data
        finally:
            self.stop()
    
    def stop(self) -> None:
        """停止爬蟲，釋放資源"""
        self.logger.info("停止爬蟲")
        self.stop_requested = True
        self.running = False
        
        # 關閉WebDriver
        if self.driver:
            self.webdriver_manager.close_driver()
            self.driver = None
    
    def _crawl_page(self, page: int) -> List[Dict[str, Any]]:
        """
        爬取單頁資料
        
        Args:
            page: 頁碼
            
        Returns:
            頁面資料列表
        """
        # 構建URL
        url = self._build_url(page)
        self.logger.info(f"爬取頁面 {page}: {url}")
        
        # 導航到頁面
        if not self._navigate_to_page(url):
            self.logger.error(f"導航到頁面 {page} 失敗")
            return []
        
        # 處理搜尋參數（如果有）
        if page == 1 and self.template.get("search_parameters"):
            self._handle_search_parameters()
        
        # 提取列表項目
        list_items = self._extract_list_items()
        self.logger.info(f"從頁面 {page} 中提取了 {len(list_items)} 個項目")
        
        # 收集詳情頁數據
        detailed_items = []
        
        for idx, item in enumerate(list_items):
            # 檢查是否已達到最大項目數或停止請求
            if self.stop_requested:
                break
                
            self.logger.debug(f"處理項目 {idx+1}/{len(list_items)}")
            
            # 檢查是否有詳情頁
            detail_link = item.get("detail_link")
            if detail_link and self.template.get("detail_page"):
                # 提取詳情頁數據
                detail_data = self._extract_detail_page(detail_link)
                
                # 合併列表和詳情頁數據
                combined_item = self._combine_data(item, detail_data)
                detailed_items.append(combined_item)
            else:
                # 沒有詳情頁，僅使用列表數據
                detailed_items.append(item)
            
            # 項目間延遲
            if idx < len(list_items) - 1:
                self._random_delay("between_items")
        
        return detailed_items
    
    def _navigate_to_page(self, url: str) -> bool:
        """
        導航到指定頁面
        
        Args:
            url: 頁面URL
            
        Returns:
            是否成功導航
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return False
        
        try:
            # 導航到頁面
            self.logger.info(f"導航到: {url}")
            self.driver.get(url)
            
            # 等待頁面加載
            self._random_delay("page_load")
            
            # 檢查頁面是否加載成功
            if "捕獲到異常" in self.driver.title or "Error" in self.driver.title:
                self.logger.warning(f"頁面加載異常: {self.driver.title}")
                return False
            
            # 檢查反爬機制
            if self._handle_anti_crawling():
                # 如果檢測到反爬機制，重新加載頁面
                return self._navigate_to_page(url)
            
            return True
        except Exception as e:
            self.logger.error(f"頁面導航失敗: {str(e)}")
            # 保存錯誤截圖和頁面源碼，便於調試
            self._save_debug_info()
            return False
    
    def _handle_anti_crawling(self) -> bool:
        """
        處理反爬機制，如驗證碼、登入等
        
        Returns:
            是否處理了反爬機制
        """
        # 檢查驗證碼
        if self._detect_captcha():
            self.logger.warning("檢測到驗證碼")
            # 儲存截圖供後續人工處理
            self.webdriver_manager.take_screenshot("captcha.png")
            return True
        
        # 其他反爬策略處理
        return False
    
    def _detect_captcha(self) -> bool:
        """
        檢測頁面是否有驗證碼
        
        Returns:
            是否檢測到驗證碼
        """
        if not self.driver:
            return False
        
        # 從模板中獲取驗證碼檢測設定
        advanced_settings = self.template.get("advanced_settings", {})
        detect_captcha = advanced_settings.get("detect_captcha", False)
        
        if not detect_captcha:
            return False
        
        captcha_detection_xpath = advanced_settings.get("captcha_detection_xpath", "")
        if not captcha_detection_xpath:
            return False
        
        try:
            captcha_elements = self.driver.find_elements(By.XPATH, captcha_detection_xpath)
            return len(captcha_elements) > 0
        except Exception as e:
            self.logger.error(f"檢測驗證碼出錯: {str(e)}")
            return False
    
    def _handle_search_parameters(self) -> None:
        """
        處理搜尋參數，如填寫表單、選擇選項等
        """
        if not self.driver:
            return
        
        search_params = self.template.get("search_parameters", {})
        if not search_params:
            return
        
        self.logger.info("處理搜尋參數")
        
        # 處理各種類型的搜尋參數
        for param_name, param_config in search_params.items():
            # 跳過按鈕類型，會最後處理
            if param_config.get("type") == "button":
                continue
                
            try:
                param_type = param_config.get("type", "")
                selector = param_config.get("selector", "")
                default_value = param_config.get("default", "")
                
                self.logger.debug(f"處理參數: {param_name}, 類型: {param_type}, 值: {default_value}")
                
                if not selector or not param_type:
                    continue
                
                # 等待元素可用
                element = self.webdriver_manager.wait_for_element(By.XPATH, selector)
                if not element:
                    self.logger.warning(f"未找到元素: {selector}")
                    continue
                
                # 根據不同類型處理參數
                if param_type == "input":
                    # 清空輸入框
                    element.clear()
                    # 輸入值
                    element.send_keys(default_value)
                    
                elif param_type == "select":
                    # 處理下拉選單
                    from selenium.webdriver.support.ui import Select
                    select = Select(element)
                    
                    # 獲取選項值
                    option_value = None
                    options = param_config.get("options", [])
                    
                    for option in options:
                        if option.get("value") == default_value:
                            option_value = option.get("option_value")
                            break
                    
                    if option_value:
                        select.select_by_value(option_value)
                    else:
                        select.select_by_visible_text(default_value)
                    
                elif param_type == "radio":
                    # 處理單選按鈕
                    options = param_config.get("options", [])
                    option_selector = None
                    
                    for option in options:
                        if option.get("value") == default_value:
                            option_selector = option.get("selector")
                            break
                    
                    if option_selector:
                        option_element = self.webdriver_manager.wait_for_element(By.XPATH, option_selector)
                        if option_element:
                            self.webdriver_manager.safe_click(option_element)
                    
                elif param_type == "checkbox":
                    # 處理複選框
                    current_state = element.is_selected()
                    should_be_checked = default_value in [True, "true", "True", "checked", "selected", "on", "1"]
                    
                    if current_state != should_be_checked:
                        self.webdriver_manager.safe_click(element)
                
                # 短暫延遲
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"處理參數 {param_name} 時出錯: {str(e)}")
        
        # 處理搜尋按鈕
        self._click_search_button()
    
    def _click_search_button(self) -> bool:
        """
        點擊搜尋按鈕
        
        Returns:
            是否成功點擊
        """
        if not self.driver:
            return False
        
        search_params = self.template.get("search_parameters", {})
        for param_name, param_config in search_params.items():
            if param_config.get("type") == "button":
                selector = param_config.get("selector", "")
                description = param_config.get("description", "按鈕")
                
                self.logger.info(f"點擊{description}")
                
                try:
                    button = self.webdriver_manager.wait_for_clickable(By.XPATH, selector)
                    if button:
                        # 點擊按鈕
                        if self.webdriver_manager.safe_click(button):
                            # 等待按鈕點擊後的延遲
                            wait_time = param_config.get("wait_after_click", 3)
                            time.sleep(wait_time)
                            return True
                except Exception as e:
                    self.logger.error(f"點擊{description}失敗: {str(e)}")
        
        return False
    
    def _extract_list_items(self) -> List[Dict[str, Any]]:
        """
        提取列表項數據
        
        Returns:
            列表項數據列表
        """
        if not self.driver:
            return []
        
        list_page_config = self.template.get("list_page", {})
        if not list_page_config:
            return []
        
        # 獲取列表容器和項目選擇器
        container_xpath = list_page_config.get("container_xpath", "//body")
        item_xpath = list_page_config.get("item_xpath", "")
        
        if not item_xpath:
            self.logger.error("未指定列表項選擇器")
            return []
        
        try:
            # 等待容器加載
            container = self.webdriver_manager.wait_for_element(By.XPATH, container_xpath)
            if not container:
                self.logger.error(f"未找到列表容器: {container_xpath}")
                return []
            
            # 查找所有列表項
            items = container.find_elements(By.XPATH, item_xpath)
            self.logger.info(f"找到 {len(items)} 個列表項")
            
            # 提取每個列表項的數據
            result = []
            fields_config = list_page_config.get("fields", {})
            
            for item in items:
                item_data = self._extract_item_fields(item, fields_config)
                if item_data:  # 只添加非空數據
                    result.append(item_data)
            
            return result
        
        except Exception as e:
            self.logger.error(f"提取列表項失敗: {str(e)}")
            return []
    
    def _extract_item_fields(self, item_element, fields_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取單個列表項的字段數據
        
        Args:
            item_element: 列表項元素
            fields_config: 字段配置
            
        Returns:
            字段數據字典
        """
        item_data = {}
        
        for field_name, field_config in fields_config.items():
            try:
                # 獲取字段配置
                xpath = field_config.get("xpath", "")
                field_type = field_config.get("type", "text")
                
                if not xpath:
                    continue
                
                # 查找字段元素
                field_elements = item_element.find_elements(By.XPATH, xpath)
                
                # 如果未找到，嘗試使用備用XPath
                if not field_elements and "fallback_xpath" in field_config:
                    fallback_xpath = field_config.get("fallback_xpath", "")
                    field_elements = item_element.find_elements(By.XPATH, fallback_xpath)
                
                if not field_elements:
                    self.logger.debug(f"未找到字段 {field_name}")
                    item_data[field_name] = ""
                    continue
                
                # 根據字段類型提取數據
                if field_type == "text":
                    # 文本類型
                    text = field_elements[0].text.strip()
                    
                    # 應用最大長度限制
                    max_length = field_config.get("max_length")
                    if max_length and len(text) > max_length:
                        text = text[:max_length] + "..."
                    
                    item_data[field_name] = text
                
                elif field_type == "attribute":
                    # 屬性類型
                    attribute_name = field_config.get("attribute", "href")
                    attribute_value = field_elements[0].get_attribute(attribute_name)
                    
                    # 應用正則表達式提取
                    regex_pattern = field_config.get("regex")
                    if regex_pattern and attribute_value:
                        import re
                        match = re.search(regex_pattern, attribute_value)
                        if match:
                            attribute_value = match.group(1)
                    
                    item_data[field_name] = attribute_value
                
                elif field_type == "html":
                    # HTML類型
                    html_content = field_elements[0].get_attribute("outerHTML")
                    item_data[field_name] = html_content
                
                elif field_type == "compound":
                    # 複合類型，子字段
                    compound_fields = field_config.get("fields", {})
                    is_multiple = field_config.get("multiple", False)
                    
                    if is_multiple:
                        # 多個複合項
                        compound_items = []
                        for element in field_elements:
                            compound_item = self._extract_compound_fields(element, compound_fields)
                            compound_items.append(compound_item)
                        item_data[field_name] = compound_items
                    else:
                        # 單個複合項
                        compound_item = self._extract_compound_fields(field_elements[0], compound_fields)
                        item_data[field_name] = compound_item
            
            except Exception as e:
                self.logger.warning(f"提取字段 {field_name} 失敗: {str(e)}")
                item_data[field_name] = ""
        
        return item_data
    
    def _extract_compound_fields(self, element, fields_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取複合字段數據
        
        Args:
            element: 元素
            fields_config: 字段配置
            
        Returns:
            複合字段數據字典
        """
        compound_data = {}
        
        for field_name, field_config in fields_config.items():
            try:
                # 獲取字段配置
                xpath = field_config.get("xpath", "")
                field_type = field_config.get("type", "text")
                
                if not xpath:
                    continue
                
                # 查找字段元素
                field_elements = element.find_elements(By.XPATH, xpath)
                
                if not field_elements:
                    compound_data[field_name] = ""
                    continue
                
                # 根據字段類型提取數據
                if field_type == "text":
                    compound_data[field_name] = field_elements[0].text.strip()
                elif field_type == "attribute":
                    attribute_name = field_config.get("attribute", "href")
                    compound_data[field_name] = field_elements[0].get_attribute(attribute_name)
                elif field_type == "html":
                    compound_data[field_name] = field_elements[0].get_attribute("outerHTML")
            
            except Exception as e:
                self.logger.warning(f"提取複合字段 {field_name} 失敗: {str(e)}")
                compound_data[field_name] = ""
        
        return compound_data
    
    def _extract_detail_page(self, detail_link: str) -> Dict[str, Any]:
        """
        提取詳情頁數據
        
        Args:
            detail_link: 詳情頁鏈接
            
        Returns:
            詳情頁數據字典
        """
        if not self.driver:
            return {}
        
        detail_page_config = self.template.get("detail_page", {})
        if not detail_page_config:
            return {}
        
        # 構建詳情頁URL
        detail_url = self._build_detail_url(detail_link)
        self.logger.info(f"提取詳情頁: {detail_url}")
        
        try:
            # 導航到詳情頁
            self.driver.get(detail_url)
            self._random_delay("page_load")
            
            # 展開頁面中可能存在的折疊區塊
            self._expand_sections()
            
            # 提取字段數據
            container_xpath = detail_page_config.get("container_xpath", "//body")
            container = self.webdriver_manager.wait_for_element(By.XPATH, container_xpath)
            
            if not container:
                self.logger.error(f"未找到詳情頁容器: {container_xpath}")
                return {}
            
            # 提取字段
            fields_config = detail_page_config.get("fields", {})
            detail_data = {}
            
            for field_name, field_config in fields_config.items():
                try:
                    # 獲取字段配置
                    xpath = field_config.get("xpath", "")
                    field_type = field_config.get("type", "text")
                    is_multiple = field_config.get("multiple", False)
                    
                    if not xpath:
                        continue
                    
                    # 查找字段元素
                    field_elements = self.driver.find_elements(By.XPATH, xpath)
                    
                    # 如果未找到，嘗試使用備用XPath
                    if not field_elements and "fallback_xpath" in field_config:
                        fallback_xpath = field_config.get("fallback_xpath", "")
                        field_elements = self.driver.find_elements(By.XPATH, fallback_xpath)
                    
                    if not field_elements:
                        self.logger.debug(f"未找到詳情頁字段 {field_name}")
                        detail_data[field_name] = "" if not is_multiple else []
                        continue
                    
                    # 根據字段類型和是否多值提取數據
                    if field_type == "text":
                        if is_multiple:
                            # 多值文本
                            detail_data[field_name] = [e.text.strip() for e in field_elements]
                        else:
                            # 單值文本
                            detail_data[field_name] = field_elements[0].text.strip()
                    
                    elif field_type == "attribute":
                        attribute_name = field_config.get("attribute", "href")
                        
                        if is_multiple:
                            # 多值屬性
                            detail_data[field_name] = [e.get_attribute(attribute_name) for e in field_elements]
                        else:
                            # 單值屬性
                            detail_data[field_name] = field_elements[0].get_attribute(attribute_name)
                        
                        # 應用正則表達式提取
                        regex_pattern = field_config.get("regex")
                        if regex_pattern:
                            import re
                            
                            if is_multiple:
                                # 處理多值
                                processed_values = []
                                for value in detail_data[field_name]:
                                    if value:
                                        match = re.search(regex_pattern, value)
                                        if match:
                                            processed_values.append(match.group(1))
                                        else:
                                            processed_values.append(value)
                                    else:
                                        processed_values.append("")
                                detail_data[field_name] = processed_values
                            else:
                                # 處理單值
                                value = detail_data[field_name]
                                if value:
                                    match = re.search(regex_pattern, value)
                                    if match:
                                        detail_data[field_name] = match.group(1)
                    
                    elif field_type == "html":
                        if is_multiple:
                            # 多值HTML
                            detail_data[field_name] = [e.get_attribute("outerHTML") for e in field_elements]
                        else:
                            # 單值HTML
                            detail_data[field_name] = field_elements[0].get_attribute("outerHTML")
                    
                    elif field_type == "elements" and "fields" in field_config:
                        # 元素集合，處理嵌套字段
                        nested_fields = field_config.get("fields", {})
                        nested_items = []
                        
                        for element in field_elements:
                            nested_item = {}
                            for nested_field_name, nested_field_config in nested_fields.items():
                                try:
                                    nested_xpath = nested_field_config.get("xpath", "")
                                    nested_type = nested_field_config.get("type", "text")
                                    
                                    nested_elements = element.find_elements(By.XPATH, nested_xpath)
                                    
                                    if nested_elements:
                                        if nested_type == "text":
                                            nested_item[nested_field_name] = nested_elements[0].text.strip()
                                        elif nested_type == "attribute":
                                            nested_attr = nested_field_config.get("attribute", "href")
                                            nested_value = nested_elements[0].get_attribute(nested_attr)
                                            
                                            # 應用正則表達式提取
                                            nested_regex = nested_field_config.get("regex")
                                            if nested_regex and nested_value:
                                                import re
                                                match = re.search(nested_regex, nested_value)
                                                if match:
                                                    nested_value = match.group(1)
                                            
                                            nested_item[nested_field_name] = nested_value
                                except Exception as ne:
                                    self.logger.warning(f"提取嵌套字段 {nested_field_name} 失敗: {str(ne)}")
                                    nested_item[nested_field_name] = ""
                            
                            nested_items.append(nested_item)
                        
                        detail_data[field_name] = nested_items
                
                except Exception as e:
                    self.logger.warning(f"提取詳情頁字段 {field_name} 失敗: {str(e)}")
                    detail_data[field_name] = "" if not is_multiple else []
            
            return detail_data
        
        except Exception as e:
            self.logger.error(f"提取詳情頁 {detail_url} 失敗: {str(e)}")
            # 保存錯誤截圖和頁面源碼
            self._save_debug_info()
            return {}
        finally:
            # 返回上一頁（可選，取決於需求）
            # self.driver.back()
            # self._random_delay("page_load")
            pass
    
    def _build_detail_url(self, detail_link: str) -> str:
        """
        構建詳情頁URL
        
        Args:
            detail_link: 詳情頁鏈接或ID
            
        Returns:
            完整的詳情頁URL
        """
        detail_page_config = self.template.get("detail_page", {})
        url_pattern = detail_page_config.get("url_pattern", "")
        
        if url_pattern:
            # 檢查detail_link是否已經是完整URL
            if detail_link.startswith(("http://", "https://")):
                return detail_link
            
            # 檢查是否需要從detail_link中提取ID
            pk_param = detail_page_config.get("pk_param", "pk")
            
            # 嘗試構建URL
            try:
                if "{" + pk_param + "}" in url_pattern:
                    # 如果URL模式中有pk參數佔位符
                    return url_pattern.replace("{" + pk_param + "}", detail_link)
                else:
                    # 使用格式化
                    format_params = {pk_param: detail_link, "pk": detail_link, "id": detail_link, "base_url": self.base_url}
                    return url_pattern.format(**format_params)
            except Exception as e:
                self.logger.error(f"構建詳情頁URL失敗: {str(e)}")
                # 回退到簡單拼接
                if not detail_link.startswith(("http://", "https://")):
                    if detail_link.startswith("/"):
                        return self.base_url + detail_link
                    else:
                        return self.base_url + "/" + detail_link
                else:
                    return detail_link
        else:
            # 沒有URL模式，檢查detail_link是否已經是完整URL
            if detail_link.startswith(("http://", "https://")):
                return detail_link
            else:
                # 簡單拼接
                if detail_link.startswith("/"):
                    return self.base_url + detail_link
                else:
                    return self.base_url + "/" + detail_link
    
    def _expand_sections(self) -> None:
        """
        展開頁面中的折疊區塊
        """
        if not self.driver:
            return
        
        detail_page_config = self.template.get("detail_page", {})
        expand_sections = detail_page_config.get("expand_sections", [])
        
        if not expand_sections:
            return
        
        self.logger.info("展開頁面區塊")
        
        for section in expand_sections:
            try:
                section_name = section.get("name", "")
                button_selector = section.get("button_selector", "")
                target_selector = section.get("target_selector", "")
                wait_time = section.get("wait_time", 1)
                
                if not button_selector:
                    continue
                
                self.logger.debug(f"展開區塊: {section_name}")
                
                # 點擊展開按鈕
                button = self.webdriver_manager.wait_for_clickable(By.XPATH, button_selector)
                if button:
                    self.webdriver_manager.safe_click(button)
                    
                    # 等待區塊展開
                    time.sleep(wait_time)
                    
                    # 驗證是否展開成功
                    if target_selector:
                        target = self.webdriver_manager.wait_for_element(By.XPATH, target_selector)
                        if not target:
                            self.logger.warning(f"區塊 {section_name} 似乎未成功展開")
            
            except Exception as e:
                self.logger.warning(f"展開區塊 {section.get('name', '')} 出錯: {str(e)}")
    
    def _combine_data(self, list_item: Dict[str, Any], detail_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        合併列表項和詳情頁數據
        
        Args:
            list_item: 列表項數據
            detail_data: 詳情頁數據
            
        Returns:
            合併後的數據
        """
        # 根據模板配置決定合併方式
        merge_strategy = self.advanced_settings.get("data_merge_strategy", "nested")
        
        if merge_strategy == "nested":
            # 嵌套模式，將詳情頁數據作為子對象
            return {
                "list_data": list_item,
                "detail_data": detail_data,
                "metadata": {
                    "source": self.site_name,
                    "timestamp": int(time.time()),
                    "version": self.version
                }
            }
        elif merge_strategy == "flat":
            # 平鋪模式，將所有數據放在同一層級，詳情頁數據覆蓋列表項數據
            result = list_item.copy()
            result.update(detail_data)
            result["metadata"] = {
                "source": self.site_name,
                "timestamp": int(time.time()),
                "version": self.version
            }
            return result
        else:
            # 默認為嵌套模式
            return {
                "list_data": list_item,
                "detail_data": detail_data,
                "metadata": {
                    "source": self.site_name,
                    "timestamp": int(time.time()),
                    "version": self.version
                }
            }
    
    def _has_next_page(self) -> bool:
        """
        檢查是否有下一頁
        
        Returns:
            是否有下一頁
        """
        if not self.driver:
            return False
        
        pagination = self.template.get("pagination", {})
        has_next_page_check = pagination.get("has_next_page_check", "")
        
        if not has_next_page_check:
            # 無法檢查是否有下一頁，檢查當前頁碼是否小於最大頁數
            max_pages = pagination.get("max_pages", 1)
            return self.current_page < max_pages
        
        try:
            # 使用XPath檢查是否有下一頁
            result = self.driver.execute_script(f"return Boolean(document.evaluate('{has_next_page_check}', document, null, XPathResult.BOOLEAN_TYPE, null).booleanValue);")
            return bool(result)
        except Exception as e:
            self.logger.warning(f"檢查下一頁失敗: {str(e)}")
            return False
    
    def _go_to_next_page(self) -> bool:
        """
        跳轉到下一頁
        
        Returns:
            是否成功跳轉
        """
        if not self.driver:
            return False
        
        pagination = self.template.get("pagination", {})
        next_button_xpath = pagination.get("next_button_xpath", "")
        
        if not next_button_xpath:
            # 沒有下一頁按鈕，使用URL模式翻頁
            url_pattern = pagination.get("url_pattern", "")
            if url_pattern:
                next_url = self._build_url(self.current_page + 1)
                return self._navigate_to_page(next_url)
            else:
                return False
        
        try:
            # 找到下一頁按鈕
            next_button = self.webdriver_manager.wait_for_clickable(By.XPATH, next_button_xpath)
            if not next_button:
                self.logger.warning("未找到下一頁按鈕")
                return False
            
            # 點擊下一頁
            if not self.webdriver_manager.safe_click(next_button):
                self.logger.warning("點擊下一頁按鈕失敗")
                return False
            
            # 等待頁面加載
            self._random_delay("page_load")
            
            return True
        except Exception as e:
            self.logger.error(f"跳轉到下一頁失敗: {str(e)}")
            return False
    
    def _save_debug_info(self) -> None:
        """
        保存錯誤信息，包括截圖和頁面源碼，便於調試
        """
        if not self.driver:
            return
            
        # 檢查是否需要保存錯誤頁面
        if not self.advanced_settings.get("save_error_page", False):
            return
            
        try:
            # 獲取錯誤頁面保存目錄
            error_dir = self.advanced_settings.get("error_page_dir", "debug")
            os.makedirs(error_dir, exist_ok=True)
            
            # 生成檔案名前綴
            timestamp = int(time.time())
            filename_base = os.path.join(
                error_dir, 
                f"error_{os.path.basename(self.template_file).replace('.json', '')}_{timestamp}"
            )
            
            # 保存截圖
            screenshot_path = f"{filename_base}.png"
            self.driver.save_screenshot(screenshot_path)
            
            # 保存頁面源碼
            html_path = f"{filename_base}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
                
            self.logger.info(f"已保存錯誤信息: 截圖={screenshot_path}, HTML={html_path}")
        except Exception as e:
            self.logger.error(f"保存錯誤信息失敗: {str(e)}")
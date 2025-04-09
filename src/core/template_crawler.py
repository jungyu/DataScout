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
from selenium.webdriver.support.ui import Select

from .config_loader import ConfigLoader
from .webdriver_manager import WebDriverManager


class PageNavigator:
    """負責頁面導航和URL構建"""
    
    def __init__(self, driver, webdriver_manager, logger):
        self.driver = driver
        self.webdriver_manager = webdriver_manager
        self.logger = logger
        self.base_url = ""
    
    def navigate_to(self, url: str) -> bool:
        """導航到指定URL"""
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return False
        
        try:
            self.logger.info(f"導航到: {url}")
            self.driver.get(url)
            return True
        except Exception as e:
            self.logger.error(f"頁面導航失敗: {str(e)}")
            return False
    
    def build_url(self, page: int) -> str:
        """構建分頁URL"""
        if "?" in self.base_url:
            return f"{self.base_url}&page={page}"
        else:
            return f"{self.base_url}?page={page}"
    
    def build_detail_url(self, detail_link: str, url_pattern: str = "") -> str:
        """構建詳情頁URL"""
        if url_pattern:
            if detail_link.startswith(("http://", "https://")):
                return detail_link
            
            pk_param = "pk"
            try:
                if "{" + pk_param + "}" in url_pattern:
                    return url_pattern.replace("{" + pk_param + "}", detail_link)
                else:
                    format_params = {pk_param: detail_link, "id": detail_link, "base_url": self.base_url}
                    return url_pattern.format(**format_params)
            except Exception as e:
                self.logger.error(f"構建詳情頁URL失敗: {str(e)}")
                return self._fallback_url_build(detail_link)
        else:
            return self._fallback_url_build(detail_link)
    
    def _fallback_url_build(self, detail_link: str) -> str:
        """URL構建的後備方案"""
        if detail_link.startswith(("http://", "https://")):
            return detail_link
        elif detail_link.startswith("/"):
            return self.base_url + detail_link
        else:
            return self.base_url + "/" + detail_link

class DataExtractor:
    """負責數據提取和處理"""
    
    def __init__(self, driver, webdriver_manager, logger):
        self.driver = driver
        self.webdriver_manager = webdriver_manager
        self.logger = logger
    
    def extract_list_items(self, container_xpath: str, item_xpath: str, fields_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取列表項數據"""
        if not self.driver:
            return []
        
        try:
            container = self.webdriver_manager.wait_for_element(By.XPATH, container_xpath)
            if not container:
                self.logger.error(f"未找到列表容器: {container_xpath}")
                return []
            
            items = container.find_elements(By.XPATH, item_xpath)
            self.logger.info(f"找到 {len(items)} 個列表項")
            
            result = []
            for item in items:
                item_data = self._extract_item_fields(item, fields_config)
                if item_data:
                    result.append(item_data)
            
            return result
        
        except Exception as e:
            self.logger.error(f"提取列表項失敗: {str(e)}")
            return []
    
    def _extract_item_fields(self, item_element, fields_config: Dict[str, Any]) -> Dict[str, Any]:
        """提取單個列表項的字段數據"""
        item_data = {}
        
        for field_name, field_config in fields_config.items():
            try:
                xpath = field_config.get("xpath", "")
                field_type = field_config.get("type", "text")
                
                if not xpath:
                    continue
                
                field_elements = item_element.find_elements(By.XPATH, xpath)
                
                if not field_elements and "fallback_xpath" in field_config:
                    fallback_xpath = field_config.get("fallback_xpath", "")
                    field_elements = item_element.find_elements(By.XPATH, fallback_xpath)
                
                if not field_elements:
                    self.logger.debug(f"未找到字段 {field_name}")
                    item_data[field_name] = ""
                    continue
                
                item_data[field_name] = self._extract_field_value(field_elements[0], field_config)
            
            except Exception as e:
                self.logger.warning(f"提取字段 {field_name} 失敗: {str(e)}")
                item_data[field_name] = ""
        
        return item_data
    
    def _extract_field_value(self, element, field_config: Dict[str, Any]) -> Any:
        """根據字段類型提取值"""
        field_type = field_config.get("type", "text")
        
        if field_type == "text":
            text = element.text.strip()
            max_length = field_config.get("max_length")
            if max_length and len(text) > max_length:
                text = text[:max_length] + "..."
            return text
        
        elif field_type == "attribute":
            attribute_name = field_config.get("attribute", "href")
            value = element.get_attribute(attribute_name)
            
            regex_pattern = field_config.get("regex")
            if regex_pattern and value:
                import re
                match = re.search(regex_pattern, value)
                if match:
                    return match.group(1)
            return value
        
        elif field_type == "html":
            return element.get_attribute("outerHTML")
        
        return ""

class FormHandler:
    """負責表單處理和參數設置"""
    
    def __init__(self, driver, webdriver_manager, logger):
        self.driver = driver
        self.webdriver_manager = webdriver_manager
        self.logger = logger
    
    def handle_search_parameters(self, search_params: Dict[str, Any]) -> None:
        """處理搜尋參數"""
        if not self.driver or not search_params:
            return
        
        self.logger.info("處理搜尋參數")
        
        # 先處理非按鈕類型的參數
        for param_name, param_config in search_params.items():
            if param_config.get("type") == "button":
                continue
            
            self._handle_parameter(param_name, param_config)
        
        # 最後處理按鈕
        self._click_search_button(search_params)
    
    def _handle_parameter(self, param_name: str, param_config: Dict[str, Any]) -> None:
        """處理單個參數"""
        try:
            param_type = param_config.get("type", "")
            selector = param_config.get("selector", "")
            default_value = param_config.get("default", "")
            
            if not selector or not param_type:
                return
            
            element = self.webdriver_manager.wait_for_element(By.XPATH, selector)
            if not element:
                self.logger.warning(f"未找到元素: {selector}")
                return
            
            if param_type == "input":
                element.clear()
                element.send_keys(default_value)
            
            elif param_type == "select":
                self._handle_select(element, param_config)
            
            elif param_type == "radio":
                self._handle_radio(param_config)
            
            elif param_type == "checkbox":
                self._handle_checkbox(element, default_value)
            
            time.sleep(0.5)
        
        except Exception as e:
            self.logger.error(f"處理參數 {param_name} 時出錯: {str(e)}")
    
    def _handle_select(self, element, param_config: Dict[str, Any]) -> None:
        """處理下拉選單"""
        select = Select(element)
        default_value = param_config.get("default", "")
        
        for option in param_config.get("options", []):
            if option.get("value") == default_value:
                select.select_by_value(option.get("option_value"))
                return
        
        select.select_by_visible_text(default_value)
    
    def _handle_radio(self, param_config: Dict[str, Any]) -> None:
        """處理單選按鈕"""
        default_value = param_config.get("default", "")
        
        for option in param_config.get("options", []):
            if option.get("value") == default_value:
                option_selector = option.get("selector")
                if option_selector:
                    option_element = self.webdriver_manager.wait_for_element(By.XPATH, option_selector)
                    if option_element:
                        self.webdriver_manager.safe_click(option_element)
                break
    
    def _handle_checkbox(self, element, default_value: Any) -> None:
        """處理複選框"""
        current_state = element.is_selected()
        should_be_checked = default_value in [True, "true", "True", "checked", "selected", "on", "1"]
        
        if current_state != should_be_checked:
            self.webdriver_manager.safe_click(element)
    
    def _click_search_button(self, search_params: Dict[str, Any]) -> bool:
        """點擊搜尋按鈕"""
        for param_config in search_params.values():
            if param_config.get("type") == "button":
                selector = param_config.get("selector", "")
                description = param_config.get("description", "按鈕")
                
                try:
                    button = self.webdriver_manager.wait_for_clickable(By.XPATH, selector)
                    if button and self.webdriver_manager.safe_click(button):
                        time.sleep(param_config.get("wait_after_click", 3))
                        return True
                except Exception as e:
                    self.logger.error(f"點擊{description}失敗: {str(e)}")
        
        return False

class TemplateCrawler:
    """基於模板的網頁爬蟲"""
    
    def __init__(self, template_file: str, webdriver_manager, logger=None):
        self.template_file = template_file
        self.webdriver_manager = webdriver_manager
        self.logger = logger or logging.getLogger(__name__)
        
        self.driver = None
        self.template = {}
        self.advanced_settings = {}
        self.site_name = ""
        self.version = "1.0.0"
        
        self.running = False
        self.stop_requested = False
        self.current_page = 1
        self.items_collected = 0
        
        # 初始化子組件
        self.navigator = None
        self.extractor = None
        self.form_handler = None
    
    def start(self, max_pages: Optional[int] = None, max_items: Optional[int] = None) -> List[Dict[str, Any]]:
        """開始爬蟲流程"""
        self.logger.info(f"開始爬取 {self.site_name}")
        
        # 初始化狀態
        self.running = True
        self.stop_requested = False
        self.current_page = 1
        self.items_collected = 0
        
        # 設置最大頁數和項目數
        max_pages = max_pages or self.template.get("pagination", {}).get("max_pages", 1)
        max_items = max_items or self.advanced_settings.get("max_results", 1000)
        
        # 初始化WebDriver
        try:
            self.driver = self.webdriver_manager.create_driver()
            self.navigator = PageNavigator(self.driver, self.webdriver_manager, self.logger)
            self.extractor = DataExtractor(self.driver, self.webdriver_manager, self.logger)
            self.form_handler = FormHandler(self.driver, self.webdriver_manager, self.logger)
        except Exception as e:
            self.logger.error(f"初始化WebDriver失敗: {str(e)}")
            self.running = False
            return []
        
        all_data = []
        
        try:
            while (self.current_page <= max_pages and 
                   self.items_collected < max_items and 
                   not self.stop_requested):
                
                page_data = self._crawl_page(self.current_page)
                
                if not page_data:
                    self.logger.warning(f"頁面 {self.current_page} 未獲取到資料，結束爬取")
                    break
                
                all_data.extend(page_data)
                self.items_collected += len(page_data)
                
                self.logger.info(f"已爬取 {self.current_page} 頁，共 {self.items_collected} 項")
                
                if not self._has_next_page():
                    self.logger.info("沒有下一頁，結束爬取")
                    break
                
                self.current_page += 1
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
        
        if self.driver:
            self.webdriver_manager.close_driver()
            self.driver = None
    
    def _crawl_page(self, page: int) -> List[Dict[str, Any]]:
        """爬取單頁資料"""
        url = self.navigator.build_url(page)
        self.logger.info(f"爬取頁面 {page}: {url}")
        
        if not self.navigator.navigate_to(url):
            self.logger.error(f"導航到頁面 {page} 失敗")
            return []
        
        if page == 1 and self.template.get("search_parameters"):
            self.form_handler.handle_search_parameters(self.template["search_parameters"])
        
        list_page_config = self.template.get("list_page", {})
        list_items = self.extractor.extract_list_items(
            list_page_config.get("container_xpath", "//body"),
            list_page_config.get("item_xpath", ""),
            list_page_config.get("fields", {})
        )
        
        self.logger.info(f"從頁面 {page} 中提取了 {len(list_items)} 個項目")
        
        detailed_items = []
        for idx, item in enumerate(list_items):
            if self.stop_requested:
                break
            
            self.logger.debug(f"處理項目 {idx+1}/{len(list_items)}")
            
            detail_link = item.get("detail_link")
            if detail_link and self.template.get("detail_page"):
                detail_data = self._extract_detail_page(detail_link)
                combined_item = self._combine_data(item, detail_data)
                detailed_items.append(combined_item)
            else:
                detailed_items.append(item)
            
            if idx < len(list_items) - 1:
                self._random_delay("between_items")
        
        return detailed_items
    
    def _extract_detail_page(self, detail_link: str) -> Dict[str, Any]:
        """提取詳情頁數據"""
        detail_page_config = self.template.get("detail_page", {})
        detail_url = self.navigator.build_detail_url(
            detail_link,
            detail_page_config.get("url_pattern", "")
        )
        
        self.logger.info(f"提取詳情頁: {detail_url}")
        
        try:
            if not self.navigator.navigate_to(detail_url):
                return {}
            
            self._random_delay("page_load")
            self._expand_sections()
            
            container_xpath = detail_page_config.get("container_xpath", "//body")
            container = self.webdriver_manager.wait_for_element(By.XPATH, container_xpath)
            
            if not container:
                self.logger.error(f"未找到詳情頁容器: {container_xpath}")
                return {}
            
            return self.extractor.extract_list_items(
                container_xpath,
                ".",  # 詳情頁通常只有一個容器
                detail_page_config.get("fields", {})
            )[0] if detail_page_config.get("fields") else {}
        
        except Exception as e:
            self.logger.error(f"提取詳情頁 {detail_url} 失敗: {str(e)}")
            self._save_debug_info()
            return {}
    
    def _expand_sections(self) -> None:
        """展開頁面中的折疊區塊"""
        if not self.driver:
            return
        
        expand_sections = self.template.get("detail_page", {}).get("expand_sections", [])
        if not expand_sections:
            return
        
        self.logger.info("展開頁面區塊")
        
        for section in expand_sections:
            try:
                button_selector = section.get("button_selector", "")
                if not button_selector:
                    continue
                
                button = self.webdriver_manager.wait_for_clickable(By.XPATH, button_selector)
                if button and self.webdriver_manager.safe_click(button):
                    time.sleep(section.get("wait_time", 1))
                    
                    target_selector = section.get("target_selector", "")
                    if target_selector:
                        target = self.webdriver_manager.wait_for_element(By.XPATH, target_selector)
                        if not target:
                            self.logger.warning(f"區塊 {section.get('name', '')} 似乎未成功展開")
            
            except Exception as e:
                self.logger.warning(f"展開區塊 {section.get('name', '')} 出錯: {str(e)}")
    
    def _combine_data(self, list_item: Dict[str, Any], detail_data: Dict[str, Any]) -> Dict[str, Any]:
        """合併列表項和詳情頁數據"""
        merge_strategy = self.advanced_settings.get("data_merge_strategy", "nested")
        
        if merge_strategy == "flat":
            result = list_item.copy()
            result.update(detail_data)
            result["metadata"] = self._get_metadata()
            return result
        else:
            return {
                "list_data": list_item,
                "detail_data": detail_data,
                "metadata": self._get_metadata()
            }
    
    def _get_metadata(self) -> Dict[str, Any]:
        """獲取元數據"""
        return {
            "source": self.site_name,
            "timestamp": int(time.time()),
            "version": self.version
        }
    
    def _has_next_page(self) -> bool:
        """檢查是否有下一頁"""
        if not self.driver:
            return False
        
        pagination = self.template.get("pagination", {})
        has_next_page_check = pagination.get("has_next_page_check", "")
        
        if not has_next_page_check:
            max_pages = pagination.get("max_pages", 1)
            return self.current_page < max_pages
        
        try:
            result = self.driver.execute_script(
                f"return Boolean(document.evaluate('{has_next_page_check}', document, null, XPathResult.BOOLEAN_TYPE, null).booleanValue);"
            )
            return bool(result)
        except Exception as e:
            self.logger.warning(f"檢查下一頁失敗: {str(e)}")
            return False
    
    def _random_delay(self, delay_type: str) -> None:
        """隨機延遲"""
        delay_config = self.advanced_settings.get("delays", {}).get(delay_type, {})
        if not delay_config:
            return
        
        min_delay = delay_config.get("min", 0)
        max_delay = delay_config.get("max", 0)
        
        if min_delay > 0 or max_delay > 0:
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
    
    def _save_debug_info(self) -> None:
        """保存錯誤信息"""
        if not self.driver or not self.advanced_settings.get("save_error_page", False):
            return
            
        try:
            error_dir = self.advanced_settings.get("error_page_dir", "debug")
            os.makedirs(error_dir, exist_ok=True)
            
            timestamp = int(time.time())
            filename_base = os.path.join(
                error_dir, 
                f"error_{os.path.basename(self.template_file).replace('.json', '')}_{timestamp}"
            )
            
            self.driver.save_screenshot(f"{filename_base}.png")
            
            with open(f"{filename_base}.html", 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
                
            self.logger.info(f"已保存錯誤信息: {filename_base}")
        except Exception as e:
            self.logger.error(f"保存錯誤信息失敗: {str(e)}")
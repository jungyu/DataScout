#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import time
import random
import logging
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, 
    TimeoutException, 
    WebDriverException, 
    StaleElementReferenceException,
    ElementClickInterceptedException
)

from ..utils.config_loader import ConfigLoader
from ..utils.logger import setup_logger
from ..utils.error_handler import retry_on_exception, handle_exception
from ..anti_detection.anti_detection_manager import AntiDetectionManager
from ..captcha.captcha_manager import CaptchaManager
from ..state.crawler_state_manager import CrawlerStateManager
from ..persistence.data_persistence_manager import DataPersistenceManager
from ..extractors.detail_page_extractor import DetailPageExtractor

class TemplateCrawler:
    """模板化爬蟲的核心類"""
    
    def __init__(self, template_file: str, config_file: str = "config/config.json", 
                 state_file: Optional[str] = None, log_level: int = logging.INFO):
        """
        初始化模板爬蟲
        
        Args:
            template_file: 模板文件路徑
            state_file: 狀態文件路徑，用於斷點續爬
            log_level: 日誌級別
        """
        self.logger = setup_logger(__name__, log_level)
        self.logger.info(f"初始化模板爬蟲，模板: {template_file}, 配置: {config_file}")
        
        # 載入模板和配置
        self.template = self._load_json(template_file)
        self.config = ConfigLoader.load_config(config_file)
        
        # 初始化模塊
        self.anti_detection = AntiDetectionManager(self.config.get("anti_detection_config", {}))
        self.captcha_manager = CaptchaManager(self.config.get("captcha_config", {}))
        
        # 初始化狀態管理和數據持久化
        state_config = self.config.get("state_config", {})
        persistence_config = self.config.get("persistence_config", {})
        
        state_id = state_file or f"{os.path.basename(template_file).replace('.json', '')}_state"
        self.state_manager = CrawlerStateManager(state_id, state_config)
        self.data_manager = DataPersistenceManager(persistence_config)
        
        # WebDriver相關
        self.driver = None
        self.base_url = self.template.get("base_url", "")
        self.encoding = self.template.get("encoding", "utf-8")
        
        # 爬取設置
        self.delays = self.template.get("delays", {
            "page_load": {"min": 2, "max": 5},
            "between_pages": {"min": 3, "max": 7},
            "between_items": {"min": 1, "max": 3}
        })
        
        self.request_params = self._prepare_request_params()
        self.logger.info("模板爬蟲初始化完成")
        self.crawler_executor = CrawlExecutor(self)
    
    def _load_json(self, file_path: str) -> Dict:
        """加載JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加載JSON文件 {file_path} 失敗: {str(e)}")
            raise
    
    def _prepare_request_params(self) -> Dict:
        """準備請求參數"""
        params = {}
        
        # 獲取請求配置
        request_config = self.template.get("request", {})
        request_params = request_config.get("params", {})
        
        # 添加固定參數
        params.update(request_params.get("fixed", {}))
        
        # 添加變量參數，使用默認值
        for param_name, param_config in request_params.get("variable", {}).items():
            default_value = param_config.get("default", "")
            # 如果配置中有覆蓋，則使用配置中的值
            if param_name in self.config.get("query_params", {}):
                params[param_name] = self.config["query_params"][param_name]
            else:
                params[param_name] = default_value
        
        return params
    
    def _build_url(self, page: int = 1) -> str:
        """構建請求URL，包含分頁參數"""
        url = self.base_url
        
        # 獲取分頁參數配置
        pagination_config = self.template.get("request", {}).get("params", {}).get("pagination", {})
        page_param = pagination_config.get("page_param", "page")
        base_index = pagination_config.get("base_index", 0)
        
        # 構建參數
        params = self.request_params.copy()
        params[page_param] = base_index + page - 1  # 轉換為基於base_index的頁碼
        
        # 構建URL查詢字符串
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        if query_string:
            url = f"{url}?{query_string}"
        
        return url
    
    def _init_webdriver(self):
        """初始化WebDriver，應用反爬蟲設置"""
        try:
            self.logger.info("初始化WebDriver")
            
            # 由AntiDetectionManager創建並配置WebDriver
            self.driver = self.anti_detection.create_webdriver(
                headless=self.config.get("headless", True)
            )
            
            # 設置隱式等待時間
            self.driver.implicitly_wait(self.config.get("implicit_wait", 10))
            
            self.logger.info("WebDriver初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"初始化WebDriver失敗: {str(e)}")
            return False
    
    def _close_webdriver(self):
        """安全關閉WebDriver"""
        if self.driver:
            try:
                self.logger.info("關閉WebDriver")
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"關閉WebDriver失敗: {str(e)}")
            finally:
                self.driver = None
    
    def _random_delay(self, delay_type: str = "page_load"):
        """根據配置的延遲範圍，生成隨機延遲時間並等待"""
        delay_config = self.delays.get(delay_type, {"min": 1, "max": 3})
        min_delay = delay_config.get("min", 1)
        max_delay = delay_config.get("max", 3)
        
        delay = random.uniform(min_delay, max_delay)
        self.logger.debug(f"隨機延遲 {delay_type}: {delay:.2f} 秒")
        time.sleep(delay)
    
    @retry_on_exception(retries=3, delay=2)
    def _navigate_to_url(self, url: str) -> bool:
        """導航到指定URL，包含重試邏輯"""
        try:
            self.logger.info(f"導航到URL: {url}")
            self.driver.get(url)
            self._random_delay("page_load")
            
            # 檢查是否需要處理驗證碼
            if self.captcha_manager.detect_captcha(self.driver):
                self.logger.info("檢測到驗證碼，嘗試解決")
                result = self.captcha_manager.solve_captcha(self.driver)
                if not result:
                    self.logger.warning("無法解決驗證碼")
                    return False
            
            # 檢查是否被反爬機制檢測
            if self.anti_detection.detected_anti_crawling(self.driver):
                self.logger.warning("檢測到反爬機制，嘗試處理")
                result = self.anti_detection.handle_detection(self.driver)
                if not result:
                    self.logger.warning("無法繞過反爬機制")
                    return False
            
            return True
        except WebDriverException as e:
            self.logger.error(f"導航到URL失敗: {str(e)}")
            raise
    
    def _extract_data_from_element(self, element, field_config: Dict) -> Any:
        """從元素中提取數據"""
        extraction_type = field_config.get("type", "text")
        
        try:
            if extraction_type == "text":
                return element.text.strip()
            elif extraction_type == "attribute":
                attribute_name = field_config.get("attribute_name", "href")
                return element.get_attribute(attribute_name)
            elif extraction_type == "html":
                return element.get_attribute("innerHTML")
            else:
                self.logger.warning(f"未知的提取類型: {extraction_type}")
                return None
        except Exception as e:
            self.logger.error(f"提取數據失敗: {str(e)}")
            return None
    
    def _extract_list_item_data(self, item_element) -> Dict:
        """從列表項元素中提取數據"""
        item_data = {}
        list_page_config = self.template.get("list_page", {})
        fields_config = list_page_config.get("fields", {})
        
        for field_name, field_config in fields_config.items():
            try:
                xpath = field_config.get("xpath", "")
                if xpath:
                    field_element = item_element.find_element(By.XPATH, xpath)
                    item_data[field_name] = self._extract_data_from_element(field_element, field_config)
            except NoSuchElementException:
                self.logger.warning(f"未找到字段元素: {field_name}, xpath: {xpath}")
                item_data[field_name] = None
            except Exception as e:
                self.logger.error(f"提取字段 {field_name} 失敗: {str(e)}")
                item_data[field_name] = None
        
        return item_data
    
    def _extract_list_items(self) -> List[Dict]:
        """提取當前頁面的列表項數據"""
        list_items = []
        list_page_config = self.template.get("list_page", {})
        
        try:
            # 等待容器元素加載
            container_xpath = list_page_config.get("container_xpath", "//body")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, container_xpath))
            )
            
            # 找到容器元素
            container = self.driver.find_element(By.XPATH, container_xpath)
            
            # 找到所有列表項
            item_xpath = list_page_config.get("item_xpath", ".//*")
            items = container.find_elements(By.XPATH, item_xpath)
            
            self.logger.info(f"找到 {len(items)} 個列表項")
            
            # 提取每個列表項的數據
            for item in items:
                self._random_delay("between_items")
                item_data = self._extract_list_item_data(item)
                if item_data:
                    list_items.append(item_data)
            
            return list_items
        except TimeoutException:
            self.logger.error(f"等待列表容器超時: {container_xpath}")
            return []
        except Exception as e:
            self.logger.error(f"提取列表項失敗: {str(e)}")
            return []
    
    def _has_next_page(self) -> bool:
        """檢查是否有下一頁"""
        pagination_config = self.template.get("pagination", {})
        
        try:
            # 使用XPath檢查下一頁按鈕是否存在
            has_next_xpath = pagination_config.get("has_next_page_check", "")
            if has_next_xpath:
                elements = self.driver.find_elements(By.XPATH, has_next_xpath)
                return len(elements) > 0
            
            return False
        except Exception as e:
            self.logger.error(f"檢查下一頁失敗: {str(e)}")
            return False
    
    @retry_on_exception(retries=3, delay=2)
    def _go_to_next_page(self) -> bool:
        """點擊下一頁按鈕"""
        pagination_config = self.template.get("pagination", {})
        
        try:
            # 找到下一頁按鈕並點擊
            next_button_xpath = pagination_config.get("next_button_xpath", "")
            if next_button_xpath:
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, next_button_xpath))
                )
                
                # 使用JavaScript點擊，避免元素不可見或被覆蓋
                self.driver.execute_script("arguments[0].click();", next_button)
                
                # 等待頁面加載
                self._random_delay("between_pages")
                return True
            
            return False
        except TimeoutException:
            self.logger.error(f"等待下一頁按鈕超時")
            return False
        except NoSuchElementException as e:
            self.logger.error(f"找不到下一頁按鈕: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"點擊下一頁按鈕失敗: {str(e)}")
            raise
    
    @retry_on_exception(retries=3, delay=5)
    def _extract_detail_data(self, detail_url: str) -> Dict:
        """提取詳情頁數據"""
        detail_data = {}
        detail_page_config = self.template.get("detail_page", {})
        
        try:
            # 導航到詳情頁
            if not self._navigate_to_url(detail_url):
                return detail_data
            
            # 等待容器元素加載
            container_xpath = detail_page_config.get("container_xpath", "//body")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, container_xpath))
            )
            
            # 提取詳情頁數據
            tables_xpath = detail_page_config.get("tables_xpath", "//table")
            tables = self.driver.find_elements(By.XPATH, tables_xpath)
            
            self.logger.info(f"找到 {len(tables)} 個表格")
            
            # 提取每個表格的數據
            for table_index, table in enumerate(tables):
                try:
                    # 提取表格標題
                    table_title_xpath = detail_page_config.get("table_title_xpath", ".//caption")
                    title_elements = table.find_elements(By.XPATH, table_title_xpath)
                    table_title = title_elements[0].text.strip() if title_elements else f"table_{table_index}"
                    
                    # 提取表格行
                    rows = table.find_elements(By.XPATH, ".//tr")
                    table_data = {}
                    
                    for row in rows:
                        try:
                            # 提取行標題和值
                            cols = row.find_elements(By.XPATH, ".//th | .//td")
                            if len(cols) >= 2:
                                key = cols[0].text.strip()
                                value = cols[1].text.strip()
                                if key:
                                    table_data[key] = value
                        except Exception as e:
                            self.logger.warning(f"提取表格行失敗: {str(e)}")
                    
                    detail_data[table_title] = table_data
                except Exception as e:
                    self.logger.warning(f"提取表格 {table_index} 失敗: {str(e)}")
            
            # 提取特定字段
            fields_config = detail_page_config.get("fields", {})
            for field_name, field_config in fields_config.items():
                try:
                    xpath = field_config.get("xpath", "")
                    if xpath:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        if elements:
                            detail_data[field_name] = self._extract_data_from_element(elements[0], field_config)
                except Exception as e:
                    self.logger.warning(f"提取字段 {field_name} 失敗: {str(e)}")
            
            return detail_data
        except Exception as e:
            self.logger.error(f"提取詳情頁數據失敗: {str(e)}", exc_info=True)
            self._save_page_for_analysis()
            return detail_data
    
    def _combine_data(self, list_item: Dict, detail_data: Dict) -> Dict:
        """合併列表項數據和詳情頁數據"""
        combined_data = {
            "list_data": list_item,
            "detail_data": detail_data,
            "metadata": {
                "crawler_name": os.path.basename(self.template.get("site_name", "unknown")),
                "crawl_time": int(time.time()),
                "success": bool(detail_data)
            }
        }
        return combined_data
    
    def crawl(self, max_pages: int = None, max_items: int = None) -> List[Dict]:
        """執行爬蟲"""
        return self.crawler_executor.execute('normal', 
                                          max_pages=max_pages, 
                                          max_items=max_items)
    
    def resume_crawl(self, max_pages: int = None, max_items: int = None) -> List[Dict]:
        """從中斷處恢復爬取"""
        return self.crawler_executor.execute('resume',
                                          max_pages=max_pages,
                                          max_items=max_items)
    
    def _crawl_from_page(self, start_page: int, max_pages: int, max_items: int) -> List[Dict]:
        """從指定頁面開始爬取"""
        # 與crawl方法類似，但從指定頁面開始
        all_data = []
        page = start_page
        
        try:
            # 初始化WebDriver
            if not self._init_webdriver():
                self.logger.error("WebDriver初始化失敗，爬蟲中止")
                return all_data
            
            # 開始爬取
            self.logger.info(f"從第 {page} 頁開始爬取，最大頁數: {max_pages}, 最大項數: {max_items}")
            
            while page <= max_pages and len(all_data) < max_items:
                # 與crawl方法中的爬取邏輯相同
                # ...省略相同代碼...
                
                # 構建並導航到URL
                url = self._build_url(page)
                if not self._navigate_to_url(url):
                    self.logger.warning(f"導航到第 {page} 頁失敗，嘗試下一頁")
                    page += 1
                    continue
                
                # 提取列表項
                list_items = self._extract_list_items()
                self.logger.info(f"第 {page} 頁提取了 {len(list_items)} 個列表項")
                
                # 提取詳情頁數據
                for item in list_items:
                    # 檢查是否達到最大項數
                    if len(all_data) >= max_items:
                        self.logger.info(f"達到最大項數 {max_items}，停止爬取")
                        break
                    
                    # 獲取詳情頁URL
                    detail_link = item.get("detail_link")
                    if detail_link:
                        # 儲存當前狀態
                        self.state_manager.save_state({
                            "current_page": page,
                            "current_item": item,
                            "items_collected": len(all_data)
                        })
                        
                        # 提取詳情頁數據
                        detail_data = self._extract_detail_data(detail_link)
                        
                        # 合併數據
                        combined_data = self._combine_data(item, detail_data)
                        all_data.append(combined_data)
                        
                        # 持久化數據
                        self.data_manager.save_data(combined_data)
                        
                        # 隨機延遲
                        self._random_delay("between_items")
                
                # 檢查是否有下一頁
                if self._has_next_page() and page < max_pages:
                    self.logger.info(f"導航到第 {page + 1} 頁")
                    if not self._go_to_next_page():
                        self.logger.warning("無法導航到下一頁，爬取結束")
                        break
                    page += 1
                else:
                    self.logger.info("沒有更多頁面，爬取結束")
                    break
        
        except Exception as e:
            self.logger.error(f"爬蟲執行過程中發生錯誤: {str(e)}")
            # 保存狀態以便恢復
            self.state_manager.save_state({
                "current_page": page,
                "error": str(e),
                "items_collected": len(all_data)
            })
        
        finally:
            # 關閉WebDriver
            self._close_webdriver()
        
        return all_data
    
    def _crawl_from_position(self, start_page: int, start_item_index: int, max_pages: int, max_items: int) -> List[Dict]:
        """從指定位置開始爬取"""
        all_data = []
        page = start_page
        
        try:
            if not self._init_webdriver():
                self.logger.error("WebDriver初始化失敗，爬蟲中止")
                return all_data
            
            # 記錄起始時間
            start_time = time.time()
            
            self.logger.info(f"從第 {page} 頁第 {start_item_index} 項開始爬取，最大頁數: {max_pages}, 最大項數: {max_items}")
            
            while page <= max_pages and len(all_data) < max_items:
                try:
                    url = self._build_url(page)
                    if not self._navigate_to_url(url):
                        self.logger.warning(f"導航到第 {page} 頁失敗，嘗試下一頁")
                        page += 1
                        continue
                    
                    list_items = self._extract_list_items()
                    self.logger.info(f"第 {page} 頁提取了 {len(list_items)} 個列表項")
                    
                    for item_index, item in enumerate(list_items):
                        if page == start_page and item_index < start_item_index:
                            continue
                        
                        if len(all_data) >= max_items:
                            self.logger.info(f"達到最大項數 {max_items}，停止爬取")
                            break
                        
                        detail_link = item.get("detail_link")
                        if detail_link:
                            self.state_manager.save_state({
                                "current_page": page,
                                "current_item_index": item_index,
                                "items_collected": len(all_data)
                            })
                            
                            detail_data = self._extract_detail_data(detail_link)
                            combined_data = self._combine_data(item, detail_data)
                            all_data.append(combined_data)
                            self.data_manager.save_data(combined_data)
                            self._random_delay("between_items")
                    
                    if self._has_next_page() and page < max_pages:
                        self.logger.info(f"導航到第 {page + 1} 頁")
                        if not self._go_to_next_page():
                            self.logger.warning("無法導航到下一頁，爬取結束")
                            break
                        page += 1
                    else:
                        self.logger.info("沒有更多頁面，爬取結束")
                        break
                
                except Exception as e:
                    self.logger.error(f"處理第 {page} 頁時發生錯誤: {str(e)}")
                    self.state_manager.save_state({
                        "current_page": page,
                        "current_item_index": start_item_index,
                        "error": str(e),
                        "items_collected": len(all_data)
                    })
                    break
        
        except Exception as e:
            self.logger.error(f"恢復爬取過程中發生錯誤: {str(e)}", exc_info=True)
            self.state_manager.save_state({
                "current_page": page,
                "current_item_index": start_item_index,
                "error": str(e),
                "error_traceback": str(e.__traceback__),
                "items_collected": len(all_data),
                "status": "critical_error_resume"
            })
        
        finally:
            self._close_webdriver()
            
            if len(all_data) > 0:
                if len(all_data) >= max_items or not self._has_next_page():
                    self.state_manager.mark_completed()
                    self.logger.info("恢復爬取已完成所有項目")
        
        return all_data
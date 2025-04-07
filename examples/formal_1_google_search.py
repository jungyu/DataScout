#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基於架構的 Google 搜尋爬蟲範例
此範例展示如何使用專案提供的核心組件和提取器模組來實現搜尋結果爬取
"""

import os
import sys
import time
import logging
import json
import re  # 新增 re 模組的導入
from typing import Dict, List, Any, Optional

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 現在可以導入專案模組
from src.core.config_loader import ConfigLoader
from src.core.webdriver_manager import WebDriverManager
from src.core.template_crawler import TemplateCrawler
from src.extractors import (
    ListExtractor,
    CaptchaHandler,
    PaginationHandler,
    StorageHandler
)
from src.extractors.core.detail_extractor import DetailExtractor
from src.extractors.config import ListExtractionConfig, ExtractionConfig

# 在其他導入之後添加
from selenium.webdriver.common.by import By


class GoogleSearchCrawler(TemplateCrawler):
    """Google 搜尋爬蟲，繼承自模板爬蟲"""
    
    def __init__(self, config_path: str):
        # 設置日誌記錄器
        self.logger = self._setup_logger()
        self.logger.info("初始化 Google 搜尋爬蟲")
        
        # 使用 ConfigLoader 載入配置
        self.config_loader = ConfigLoader(logger=self.logger)
        self.config = self.config_loader.load_config(config_path)
        
        # 設置更詳細的日誌層級
        if self.config.get("advanced_settings", {}).get("debug_mode", False):
            self.logger.setLevel(logging.DEBUG)
            self.logger.info("已啟用調試模式")
            
            # 添加 Selenium 的詳細日誌
            selenium_logger = logging.getLogger('selenium')
            selenium_logger.setLevel(logging.INFO)
            if not selenium_logger.handlers:
                # 創建處理器
                handler = logging.StreamHandler()
                formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
                handler.setFormatter(formatter)
                selenium_logger.addHandler(handler)
        
        # 初始化基類 (不使用 super().__init__ 因為我們已經載入了配置)
        # 注意：如果 TemplateCrawler 需要 config_path 而不是 config 對象，則需要調整
        # super().__init__(config_path)  # 舊的方法
        
        # 初始化 WebDriver 管理器
        self.webdriver_manager = None
        self.driver = None
        
        # 結果存儲
        self.all_results = []
        self.detail_results = []
        
        self.logger.info("Google 搜尋爬蟲初始化完成")
    
    def _setup_logger(self) -> logging.Logger:
        """設置日誌記錄器"""
        logger = logging.getLogger("GoogleSearchCrawler")
        logger.setLevel(logging.INFO)
        
        # 創建控制台處理器
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger

    def setup(self) -> bool:
        """
        設置爬蟲環境
        
        Returns:
            設置是否成功
        """
        try:
            self.logger.info("啟動 WebDriver")
            
            # 更新 WebDriverManager 的配置
            # 確保配置中包含所需的瀏覽器選項
            browser_config = self.config.get("browser", {})
            browser_config.update({
                "headless": False,  # 非無頭模式，可以看到驗證碼
                "disable_images": False,  # 確保加載圖片
                "page_load_timeout": 30,  # 增加超時時間
                "implicit_wait": 10  # 設置隱式等待時間
            })
            
            # 更新主配置中的瀏覽器配置
            self.config["browser"] = browser_config
            
            # 初始化 WebDriverManager 與配置
            self.webdriver_manager = WebDriverManager(config=self.config, logger=self.logger)
            
            # 創建 WebDriver
            self.driver = self.webdriver_manager.create_driver()
            
            if not self.driver:
                self.logger.error("無法創建 WebDriver")
                return False
            
            # 初始化提取器
            self.list_extractor = ListExtractor(
                driver=self.driver,
                logger=self.logger
            )
            
            # 初始化詳情頁提取器
            self.detail_extractor = DetailExtractor(
                driver=self.driver,
                logger=self.logger,
                base_url=self.config.get("base_url"),
                timeout=20
            )
            
            # 初始化特定處理器
            self.captcha_handler = CaptchaHandler(
                driver=self.driver, 
                logger=self.logger
            )
            
            # 初始化分頁處理器
            self.pagination_handler = PaginationHandler(
                driver=self.driver,
                logger=self.logger
            )
            
            # 初始化存儲處理器
            self.storage_handler = StorageHandler(logger=self.logger)
            
            return True
            
        except Exception as e:
            self.logger.error(f"設置爬蟲環境失敗: {str(e)}")
            return False

    def run(self) -> bool:
        """
        執行爬蟲任務
        
        Returns:
            爬蟲是否成功執行
        """
        try:
            if not self.setup():
                return False
                
            # 打開搜尋頁面
            base_url = self.config.get("base_url", "https://www.google.com")
            self.logger.info(f"訪問 {self.config.get('site_name', 'Google')} 首頁: {base_url}")
            self.driver.get(base_url)
            
            # 執行搜尋
            search_keyword = self.config.get("search", {}).get("keyword", "Google")
            success = self.perform_search(search_keyword)
            if not success:
                self.logger.error("執行搜尋操作失敗")
                return False
            
            # 爬取多個頁面
            current_page = 1
            max_pages = self.config.get("pagination", {}).get("max_pages", 1)
            
            all_search_results = []  # 收集所有頁面的搜索結果
            
            while current_page <= max_pages:
                self.logger.info(f"處理第 {current_page} 頁")
                
                # 解析當前頁面結果
                page_results = self.extract_search_results()
                
                if not page_results:
                    self.logger.warning(f"第 {current_page} 頁未提取到結果")
                    break
                    
                self.all_results.extend(page_results)
                all_search_results.extend(page_results)  # 添加到總結果
                
                self.logger.info(f"第 {current_page} 頁找到 {len(page_results)} 條結果")
                
                # 檢查是否需要繼續下一頁
                if current_page >= max_pages or not self.has_next_page():
                    break
                
                # 前往下一頁
                self.logger.info(f"前往第 {current_page + 1} 頁...")
                if not self.go_to_next_page():
                    self.logger.warning("無法前往下一頁，結束爬取")
                    break
                
                current_page += 1
                
                # 頁面間延遲
                between_pages_delay = self.config.get("delays", {}).get("between_pages", 2)
                time.sleep(between_pages_delay)
            
            # 檢查是否需要採集詳情頁
            detail_enabled = self.config.get("detail_page", {}).get("enabled", False)
            if detail_enabled and all_search_results:
                self.logger.info("開始提取詳情頁內容...")
                self.extract_detail_pages(all_search_results)
            
            # 保存結果
            self.save_results()
            
            self.logger.info(f"完成爬取 {current_page} 頁，共 {len(self.all_results)} 條結果，{len(self.detail_results)} 個詳情頁")
            return True
            
        except Exception as e:
            self.logger.error(f"爬蟲執行失敗: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            self.handle_error()
            return False
            
        finally:
            self.cleanup()

    def perform_search(self, keyword: str) -> bool:
        """
        執行搜尋操作
        
        Args:
            keyword: 搜尋關鍵字
            
        Returns:
            是否成功執行搜尋
        """
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            
            # 獲取搜尋框配置
            search_box_xpath = self.config.get("search_page", {}).get("search_box_xpath", "//textarea[@name='q']")
            
            # 找到搜尋框並輸入關鍵詞
            self.logger.info(f"搜尋關鍵詞: {keyword}")
            
            # 使用正確的參數順序調用 wait_for_element 方法
            search_box = self.list_extractor.wait_for_element(
                By.XPATH,  # 第一個參數是 by
                search_box_xpath,  # 第二個參數是 selector
                timeout=10
            )
            
            if not search_box:
                self.logger.error(f"找不到搜尋框元素: {search_box_xpath}")
                # 嘗試更多選擇器
                alternative_selectors = [
                    "//input[@name='q']", 
                    "//input[@title='搜尋']",
                    "//textarea[@title='搜尋']"
                ]
                for selector in alternative_selectors:
                    self.logger.info(f"嘗試備用搜尋框選擇器: {selector}")
                    search_box = self.list_extractor.wait_for_element(By.XPATH, selector, timeout=5)
                    if search_box:
                        self.logger.info(f"使用備用選擇器 {selector} 找到搜尋框")
                        break
                        
                if not search_box:
                    self.logger.error("所有選擇器都找不到搜尋框，無法繼續")
                    return False
            
            # 清除並輸入搜尋關鍵詞
            search_box.clear()
            search_box.send_keys(keyword)
            
            # 嘗試提交搜尋
            try:
                search_box.send_keys(Keys.RETURN)
            except:
                try:
                    search_box.submit()
                except:
                    self.logger.warning("無法使用常規方法提交搜尋，嘗試使用JavaScript點擊")
                    self.driver.execute_script("document.querySelector('form[action*=\"search\"]').submit();")
            
            # 等待搜尋結果載入
            result_container_xpath = self.config.get("search_page", {}).get("result_container_xpath", "//div[@id='search']")
            
            # 使用正確的參數順序調用 wait_for_element 方法
            result_container = self.list_extractor.wait_for_element(
                By.XPATH,  # 第一個參數是 by
                result_container_xpath,  # 第二個參數是 selector
                timeout=15
            )
            
            if not result_container:
                self.logger.warning(f"未找到結果容器: {result_container_xpath}")
                # 嘗試更多備用容器選擇器
                alternative_containers = [
                    "//div[@id='rso']",
                    "//div[@id='main']",
                    "//div[@id='center_col']",
                    "//div[contains(@class, 'g')]"
                ]
                
                for selector in alternative_containers:
                    self.logger.info(f"嘗試備用結果容器選擇器: {selector}")
                    result_container = self.list_extractor.wait_for_element(By.XPATH, selector, timeout=5)
                    if result_container:
                        self.logger.info(f"使用備用選擇器 {selector} 找到結果容器")
                        break
            
            # 如果還是找不到，我們等待一段時間然後繼續
            if not result_container:
                self.logger.warning("無法找到任何結果容器，等待頁面完全載入後繼續")
                # 等待頁面載入
                time.sleep(5)
            
            # 頁面載入延遲
            page_load_delay = self.config.get("delays", {}).get("page_load", 1)
            time.sleep(page_load_delay)
            
            return True
            
        except Exception as e:
            self.logger.error(f"執行搜尋操作失敗: {str(e)}")
            return False

    def extract_detail_pages(self, search_results: List[Dict[str, Any]]) -> None:
        """
        提取搜尋結果中的詳情頁面數據
        
        Args:
            search_results: 搜尋結果列表
        """
        # 獲取詳情頁配置
        detail_config = self.config.get("detail_page", {})
        if not detail_config.get("enabled", False):
            self.logger.info("詳情頁提取未啟用，跳過")
            return

        # 獲取最大處理數量
        max_details = detail_config.get("max_details_per_page", 3)
        details_to_process = search_results[:max_details]

        self.logger.info(f"準備提取 {len(details_to_process)} 個詳情頁")

        for index, result in enumerate(details_to_process):
            try:
                # 獲取詳情頁URL
                url = result.get("link")
                if not url:
                    self.logger.warning(f"結果 #{index} 缺少 URL，跳過")
                    continue

                self.logger.info(f"訪問詳情頁 #{index+1}: {url}")

                # 使用 NavigateToPage 函數訪問頁面並處理可能的錯誤
                success = self._navigate_to_detail_page(url, detail_config.get("page_load_delay", 3))
                if not success:
                    self.logger.warning(f"詳情頁 #{index+1} 導航失敗，跳過")
                    continue
                
                # 檢查並處理可能的驗證碼
                if detail_config.get("check_captcha", True):
                    captcha_detected = self._check_and_handle_captcha()
                    if captcha_detected:
                        self.logger.info("已嘗試處理驗證碼")
                
                # 展開需要展開的區塊
                expand_sections = detail_config.get("expand_sections", [])
                if expand_sections:
                    self.detail_extractor.expand_sections(expand_sections)
                    # 展開後等待內容加載
                    time.sleep(1)
                
                # 提取詳情頁數據
                container_xpath = detail_config.get("container_xpath")
                try:
                    self.logger.info(f"正在使用容器: {container_xpath} 提取詳情頁內容")
                    detail_data = self.detail_extractor.extract_detail_page(detail_config, container_xpath)
                    
                    # 確保 detail_data 不為 None
                    if detail_data is None:
                        detail_data = {}
                        
                    # 檢查結果是否為空
                    if not detail_data or (isinstance(detail_data, dict) and len(detail_data) <= 1):  # 只有元數據
                        self.logger.warning(f"詳情頁 #{index+1} 未提取到有效數據")
                        
                        # 嘗試使用備用提取策略
                        fields_config = detail_config.get("fields", {})
                        if fields_config:
                            self.logger.info("嘗試使用直接字段提取方式")
                            alternate_data = self.detail_extractor.extract_fields(fields_config)
                            if alternate_data:
                                detail_data.update(alternate_data)
                                self.logger.info(f"使用備用策略成功提取 {len(alternate_data)} 個字段")
                except Exception as e:
                    self.logger.error(f"提取詳情頁內容出錯: {str(e)}")
                    # 創建空結果
                    detail_data = {"_error": str(e)}
                
                # 提取表格數據（如果需要）
                if detail_config.get("extract_tables", False):
                    try:
                        tables_xpath = detail_config.get("tables_xpath")
                        title_xpath = detail_config.get("table_title_xpath", ".//caption")
                        if tables_xpath:
                            table_data = self.detail_extractor.extract_tables(tables_xpath, title_xpath)
                            if table_data:
                                detail_data["tables"] = table_data
                                self.logger.info(f"提取到 {len(table_data)} 個表格")
                    except Exception as e:
                        self.logger.warning(f"提取表格數據失敗: {str(e)}")
                
                # 提取圖片（如果需要）
                if detail_config.get("extract_images", False):
                    try:
                        images_container = detail_config.get("images_container_xpath")
                        images = self.detail_extractor.extract_images(images_container)
                        if images:
                            detail_data["images"] = images
                            self.logger.info(f"提取到 {len(images)} 張圖片")
                    except Exception as e:
                        self.logger.warning(f"提取圖片失敗: {str(e)}")
                
                # 整合基本搜尋結果和詳情頁數據
                detail_data["_search_result"] = {
                    "title": result.get("title", ""),
                    "description": result.get("description", ""),
                    "position": index
                }
                
                # 添加到詳情結果列表
                self.detail_results.append(detail_data)
                
                self.logger.info(f"完成詳情頁 #{index+1} 提取，字段數: {len(detail_data)}")
                
                # 詳情頁之間等待
                if index < len(details_to_process) - 1:
                    time.sleep(detail_config.get("between_details_delay", 2))
                    
            except Exception as e:
                self.logger.error(f"提取詳情頁 #{index+1} 失敗: {str(e)}")
                import traceback
                self.logger.debug(traceback.format_exc())

        self.logger.info(f"完成 {len(self.detail_results)} 個詳情頁提取")

    def _navigate_to_detail_page(self, url: str, delay: float = 3) -> bool:
        """
        安全地導航到詳情頁面
        
        Args:
            url: 詳情頁URL
            delay: 頁面加載等待時間
            
        Returns:
            是否成功導航
        """
        retry_count = 0
        max_retries = 2
        
        while retry_count <= max_retries:
            try:
                self.driver.get(url)
                
                # 等待頁面載入
                time.sleep(delay)
                
                # 檢查頁面是否成功載入
                if self._is_page_valid():
                    return True
                    
                retry_count += 1
                if retry_count <= max_retries:
                    self.logger.warning(f"頁面載入似乎不完整，重試 ({retry_count}/{max_retries})...")
                    time.sleep(1)  # 短暫等待後重試
                
            except Exception as e:
                self.logger.error(f"導航到詳情頁失敗: {str(e)}")
                retry_count += 1
                if retry_count <= max_retries:
                    self.logger.info(f"嘗試重新訪問 ({retry_count}/{max_retries})...")
                    time.sleep(2)  # 稍長等待後重試
                
        return False

    def _is_page_valid(self) -> bool:
        """
        檢查當前頁面是否有效
        
        Returns:
            頁面是否有效
        """
        try:
            # 檢查頁面標題
            title = self.driver.title.lower()
            body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            invalid_patterns = ["404", "not found", "error", "無法連接", "不存在", "服務暫停"]
            
            # 檢查標題是否含有錯誤關鍵字
            for pattern in invalid_patterns:
                if pattern in title:
                    self.logger.warning(f"頁面標題包含無效關鍵字: '{pattern}'")
                    return False
            
            # 檢查是否有主要內容
            if len(body_text) < 100:  # 太短的內容可能是錯誤頁面
                self.logger.warning("頁面內容過短，可能是錯誤頁面")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"檢查頁面有效性時出錯: {str(e)}")
            return False

    def _check_and_handle_captcha(self) -> bool:
        """
        檢查並處理可能的驗證碼
        
        Returns:
            是否檢測到驗證碼
        """
        try:
            # 檢查頁面是否包含驗證碼線索
            captcha_elements = [
                "//div[contains(@class, 'g-recaptcha')]",
                "//iframe[contains(@src, 'recaptcha')]",
                "//div[contains(@class, 'captcha')]",
                "//*[contains(text(), '驗證') and contains(text(), '人類')]"
            ]
            
            captcha_detected = False
            
            for xpath in captcha_elements:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements:
                    captcha_detected = True
                    self.logger.warning(f"詳情頁可能需要驗證，發現元素: {xpath}")
                    break
                    
            if captcha_detected or "recaptcha" in self.driver.page_source.lower() or "驗證" in self.driver.page_source:
                self.logger.warning("詳情頁需要驗證，請手動解決")
                screenshot_path = f"detail_captcha_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                self.logger.info(f"驗證碼截圖已保存至: {screenshot_path}")
                
                # 給予足夠時間手動解決驗證碼
                time.sleep(30)
                
                self.logger.info("繼續處理詳情頁")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"檢查驗證碼時出錯: {str(e)}")
            return False

    def extract_search_results(self) -> List[Dict[str, Any]]:
        self.logger.info("開始提取搜索結果...")
        
        # 打印頁面標題，幫助調試
        try:
            self.logger.info(f"當前頁面標題: {self.driver.title}")
        except:
            pass
            
        # 手動處理驗證碼
        if "recaptcha" in self.driver.page_source.lower() or "驗證" in self.driver.page_source:
            self.logger.warning("頁面可能需要驗證，請手動解決驗證碼")
            self.driver.save_screenshot("captcha_needed.png")
            # 給予足夠時間進行手動處理
            time.sleep(30)

        # 使用配置中的參數
        container_xpath = self.config.get("list_page", {}).get("container_xpath", "//div[@id='search']")
        item_xpath = self.config.get("list_page", {}).get("item_xpath", "//div[contains(@class, 'N54PNb')]")
        fields = self.config.get("list_page", {}).get("fields", {})
        max_items = self.config.get("advanced_settings", {}).get("max_results_per_page", 10)
        
        # 將原始字段配置轉換為 ExtractionConfig 對象字典
        field_configs = {}
        for field_name, field_config_dict in fields.items():
            field_configs[field_name] = ExtractionConfig(
                xpath=field_config_dict.get("xpath"),
                type=field_config_dict.get("type", "text"),
                attribute=field_config_dict.get("attribute"),
                default=field_config_dict.get("default"),
                fallback_xpath=field_config_dict.get("fallback_xpath"),
                max_length=field_config_dict.get("max_length")
            )
        
        # 創建 ListExtractionConfig 對象（移除不支援的 source_name 參數）
        config = ListExtractionConfig(
            container_xpath=container_xpath,
            item_xpath=item_xpath,
            fields=field_configs,
            max_items=max_items,
            wait_time=5.0,
            scroll_after_load=True
        )
        
        # 添加別名：將 field_configs 設置為 fields 的別名
        setattr(config, 'field_configs', config.fields)
        
        # 設置 extraction_delay 屬性
        setattr(config, 'extraction_delay', 0.5)
        
        # 添加缺少的 source_name 屬性
        setattr(config, 'source_name', self.config.get('site_name', 'Google Search'))
        
        # 添加調試日誌
        self.logger.info(f"開始提取搜尋結果，container_xpath={container_xpath}, item_xpath={item_xpath}")
        
        try:
            # 嘗試提取結果
            results = self.list_extractor.extract(config)
            self.logger.info(f"已提取 {len(results)} 條搜尋結果")
            
            # 為結果添加元數據
            for result in results:
                if '_metadata' not in result:
                    result['_metadata'] = {}
                result['_metadata']['site'] = self.config.get('site_name', 'Google Search')
                result['_metadata']['timestamp'] = int(time.time())
            
            # 如果沒有結果，嘗試更多選擇器
            if not results:
                self.logger.warning("未找到結果，嘗試更多 Google 選擇器...")
                
                # 嘗試更廣泛的 Google 搜尋選擇器
                alternative_selectors = [
                    "//div[@id='rso']/div",  
                    "//div[@id='search']//div[@class='g']", 
                    "//div[@id='search']//div[contains(@class, 'g')]",
                    "//div[contains(@class, 'yuRUbf')]/..",
                    "//div[@id='search']//div[@jscontroller]",  # 更通用選擇器
                    "//div[@id='search']//div[contains(@class, 'v7W49e')]",
                    "//div[@id='search']//div[contains(@class, 'MjjYud')]",
                    "//div[@id='search']//a[h3]/..",  # 包含h3的鏈接父元素
                    "//div[@id='center_col']//div[.//h3]"  # 包含h3的任何div
                ]
                
                for alt_selector in alternative_selectors:
                    self.logger.info(f"嘗試選擇器: {alt_selector}")
                    # 檢查選擇器能找到的元素數量
                    elements = self.driver.find_elements(By.XPATH, alt_selector)
                    self.logger.info(f"選擇器 {alt_selector} 找到 {len(elements)} 個元素")
                    
                    if elements:
                        config.item_xpath = alt_selector
                        # 更新別名
                        setattr(config, 'field_configs', config.fields)
                        results = self.list_extractor.extract(config)
                        if results:
                            self.logger.info(f"使用選擇器 {alt_selector} 找到 {len(results)} 條結果")
                            break
            
            return results or []
            
        except Exception as e:
            self.logger.error(f"提取搜尋結果時發生錯誤: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
            
            # 保存頁面源碼以便調試
            try:
                with open("debug_page_source.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                self.logger.info("已保存頁面源碼到 debug_page_source.html")
            except:
                pass
                
            return []

    def has_next_page(self) -> bool:
        """
        檢查是否有下一頁
        
        Returns:
            是否存在下一頁
        """
        next_button_xpath = self.config.get("pagination", {}).get("next_button_xpath", "//a[@id='pnnext']")
        
        if not next_button_xpath:
            return False
        
        # 直接檢查元素是否存在
        try:
            elements = self.driver.find_elements(By.XPATH, next_button_xpath)
            return len(elements) > 0
        except Exception as e:
            self.logger.error(f"檢查下一頁時出錯: {str(e)}")
            return False

    def go_to_next_page(self) -> bool:
        """前往下一頁"""
        next_button_xpath = self.config.get("pagination", {}).get("next_button_xpath", "//a[@id='pnnext']")
        between_pages_delay = self.config.get("delays", {}).get("between_pages", 2)
        
        self.logger.info(f"嘗試點擊下一頁按鈕: {next_button_xpath}")
        
        try:
            # 使用 JavaScript 點擊
            elements = self.driver.find_elements(By.XPATH, next_button_xpath)
            if elements:
                # 滾動到按鈕位置
                self.driver.execute_script("arguments[0].scrollIntoView(true);", elements[0])
                time.sleep(1)  # 等待滾動完成
                
                # 使用 JavaScript 點擊
                self.driver.execute_script("arguments[0].click();", elements[0])
                self.logger.info("已使用 JavaScript 點擊下一頁按鈕")
                time.sleep(between_pages_delay)
                return True
            else:
                self.logger.warning("找不到下一頁按鈕")
                return False
        except Exception as e:
            self.logger.error(f"前往下一頁時出錯: {str(e)}")
            return False

    def save_results(self) -> None:
        """保存爬取結果到文件"""
        # 創建輸出目錄
        os.makedirs("output", exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        site_name = self.config.get('site_name', 'google_search').replace(' ', '_').lower()
        
        # 保存搜尋結果
        if self.all_results:
            search_output_file = f"output/{site_name}_results_{timestamp}.json"
            try:
                # 確保 JSON 序列化前的數據是可序列化的
                sanitized_results = []
                for item in self.all_results:
                    sanitized_item = {}
                    for k, v in item.items():
                        # 過濾無法序列化的值
                        if isinstance(v, (str, int, float, bool, list, dict, type(None))):
                            sanitized_item[k] = v
                        else:
                            sanitized_item[k] = str(v)
                    sanitized_results.append(sanitized_item)
                
                # 寫入JSON文件
                with open(search_output_file, 'w', encoding='utf-8') as f:
                    json.dump(sanitized_results, f, ensure_ascii=False, indent=2)
                self.logger.info(f"搜尋結果已儲存至: {search_output_file}")
                
                # 同時保存為CSV（可選）
                if self.config.get("advanced_settings", {}).get("save_csv", False):
                    try:
                        import csv
                        import pandas as pd
                        
                        # 嘗試使用pandas存為CSV
                        csv_file = search_output_file.replace('.json', '.csv')
                        df = pd.DataFrame(sanitized_results)
                        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
                        self.logger.info(f"搜尋結果已儲存為CSV: {csv_file}")
                    except Exception as csv_err:
                        self.logger.warning(f"儲存CSV失敗: {str(csv_err)}")
                        
            except Exception as e:
                self.logger.error(f"保存搜尋結果失敗: {str(e)}")
                import traceback
                self.logger.debug(traceback.format_exc())
        else:
            self.logger.warning("沒有搜尋結果可保存")
        
        # 保存詳情頁結果
        if self.detail_results:
            # 確保詳情頁結果是列表
            if not isinstance(self.detail_results, list):
                self.detail_results = [self.detail_results]
                
            detail_output_file = f"output/{site_name}_details_{timestamp}.json"
            try:
                # 確保 JSON 序列化前的數據是可序列化的
                sanitized_details = []
                for item in self.detail_results:
                    if not isinstance(item, dict):
                        self.logger.warning(f"跳過非字典類型的詳情頁結果: {type(item)}")
                        continue
                        
                    sanitized_item = {}
                    for k, v in item.items():
                        # 對複雜對象進行特殊處理
                        if isinstance(v, (str, int, float, bool, type(None))):
                            sanitized_item[k] = v
                        elif isinstance(v, (list, tuple)):
                            sanitized_item[k] = self._sanitize_list(v)
                        elif isinstance(v, dict):
                            sanitized_item[k] = self._sanitize_dict(v)
                        else:
                            sanitized_item[k] = str(v)
                    sanitized_details.append(sanitized_item)
                
                with open(detail_output_file, 'w', encoding='utf-8') as f:
                    json.dump(sanitized_details, f, ensure_ascii=False, indent=2)
                self.logger.info(f"詳情頁結果已儲存至: {detail_output_file}")
                
                # 保存詳情頁到獨立文件（如果配置啟用）
                if self.config.get("advanced_settings", {}).get("save_details_individually", False):
                    details_dir = f"output/{site_name}_details_{timestamp}"
                    os.makedirs(details_dir, exist_ok=True)
                    
                    for idx, detail in enumerate(sanitized_details):
                        # 嘗試從標題或URL獲取合適的文件名
                        title = None
                        if "_search_result" in detail and "title" in detail["_search_result"]:
                            title = detail["_search_result"]["title"]
                        elif "title" in detail:
                            title = detail["title"]
                            
                        if title:
                            # 清理文件名
                            title = re.sub(r'[\\/*?:"<>|]', "", title)
                            title = title[:50]  # 截斷長文件名
                        else:
                            title = f"detail_{idx+1}"
                            
                        detail_file = os.path.join(details_dir, f"{title}.json")
                        with open(detail_file, 'w', encoding='utf-8') as f:
                            json.dump(detail, f, ensure_ascii=False, indent=2)
                            
                    self.logger.info(f"已將 {len(sanitized_details)} 個詳情頁存為獨立文件在 {details_dir} 目錄")
                    
            except Exception as e:
                self.logger.error(f"保存詳情頁結果失敗: {str(e)}")
                import traceback
                self.logger.debug(traceback.format_exc())
        else:
            self.logger.warning("沒有詳情頁結果可保存")
        
        # 輸出統計信息
        if hasattr(self, 'detail_extractor') and self.detail_extractor:
            stats = self.detail_extractor.get_statistics()
            self.logger.info(f"詳情頁提取統計: {stats}")
            
        self.logger.info(f"總共提取了 {len(self.all_results)} 個搜尋結果和 {len(self.detail_results)} 個詳情頁")

    def _sanitize_dict(self, d: Dict) -> Dict:
        """處理字典對象，確保可序列化"""
        result = {}
        for k, v in d.items():
            if isinstance(v, (str, int, float, bool, type(None))):
                result[k] = v
            elif isinstance(v, (list, tuple)):
                result[k] = self._sanitize_list(v)
            elif isinstance(v, dict):
                result[k] = self._sanitize_dict(v)
            else:
                result[k] = str(v)
        return result

    def _sanitize_list(self, lst: List) -> List:
        """處理列表對象，確保可序列化"""
        result = []
        for item in lst:
            if isinstance(item, (str, int, float, bool, type(None))):
                result.append(item)
            elif isinstance(item, (list, tuple)):
                result.append(self._sanitize_list(item))
            elif isinstance(item, dict):
                result.append(self._sanitize_dict(item))
            else:
                result.append(str(item))
        return result

        if hasattr(self, 'detail_extractor') and self.detail_extractor:
            stats = self.detail_extractor.get_statistics()
            self.logger.info(f"詳情頁提取統計: {stats}")

    def handle_error(self) -> None:
        """處理錯誤，保存錯誤頁面截圖和源碼"""
        if not self.driver:
            return
            
        # 檢查是否需要保存錯誤頁面
        if not self.config.get("advanced_settings", {}).get("save_error_page", False):
            return
            
        try:
            # 獲取錯誤頁面保存目錄
            error_dir = self.config.get("advanced_settings", {}).get("error_page_dir", "../debug")
            os.makedirs(error_dir, exist_ok=True)
            
            # 生成檔案名
            timestamp = int(time.time())
            filename_base = f"error_{timestamp}"
            
            # 儲存截圖
            screenshot_path = os.path.join(error_dir, f"{filename_base}.png")
            self.driver.save_screenshot(screenshot_path)
            
            # 儲存頁面源碼
            html_path = os.path.join(error_dir, f"{filename_base}.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
                
            self.logger.info(f"已儲存錯誤頁面: 截圖={screenshot_path}, HTML={html_path}")
        except Exception as e:
            self.logger.error(f"儲存錯誤頁面失敗: {str(e)}")

    def cleanup(self) -> None:
        """清理資源，關閉瀏覽器"""
        if self.driver:
            self.logger.info("關閉瀏覽器...")
            self.driver.quit()
            self.driver = None
        
        self.logger.info("爬蟲程序已完成")

    def handle_captcha(self, xpath: str) -> bool:
        """處理驗證碼，給用戶足夠時間手動解決"""
        try:
            if self.captcha_handler.detect_captcha(xpath):
                self.logger.warning("檢測到驗證碼，請手動解決...")
                
                # 增加足夠的等待時間讓用戶解決驗證碼
                # 用戶有 30 秒的時間來解決驗證碼
                time.sleep(30)
                
                self.logger.info("恢復爬蟲操作...")
                return True
                
            return False
        except Exception as e:
            self.logger.error(f"處理驗證碼時出錯: {str(e)}")
            return False


def main() -> None:
    """主函數：執行 Google 搜尋爬蟲"""
    # 取得配置文件路徑
    config_path = os.path.join(os.path.dirname(__file__), "basic_google_search.json")
    
    # 檢查配置文件是否存在
    if not os.path.exists(config_path):
        print(f"錯誤: 配置文件不存在 - {config_path}")
        sys.exit(1)
    
    # 創建爬蟲實例
    crawler = GoogleSearchCrawler(config_path)
    
    # 執行爬蟲
    success = crawler.run()
    
    # 顯示執行結果
    if success:
        print("爬蟲成功完成!")
    else:
        print("爬蟲執行失敗!")
        sys.exit(1)


if __name__ == "__main__":
    main()
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
from typing import Dict, List, Any

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 現在可以導入專案模組
from src.core import ConfigLoader, WebDriverManager, TemplateCrawler
from src.extractors import (
    ListExtractor,
    CaptchaHandler,
    PaginationHandler,
    StorageHandler
)


class GoogleSearchCrawler(TemplateCrawler):
    """Google 搜尋爬蟲，繼承自模板爬蟲"""
    
    def __init__(self, config_path: str):
        """
        初始化 Google 搜尋爬蟲
        
        Args:
            config_path: JSON 配置文件路徑
        """
        super().__init__(config_path)  # 調用父類的初始化方法
        
        # 設置日誌記錄器
        self.logger = self._setup_logger()
        self.logger.info("初始化 Google 搜尋爬蟲")
        
        # 結果存儲
        self.all_results = []
        
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
            
            # 移除對 super().setup() 的調用，直接初始化 WebDriver
            self.driver = self.webdriver_manager.create_driver()
            if not self.driver:
                self.logger.error("無法創建 WebDriver")
                return False
            
            # 初始化提取器 (新增)
            self.list_extractor = ListExtractor(
                driver=self.driver,
                logger=self.logger
            )
            
            # 初始化特定處理器 - 移除 config 參數
            self.captcha_handler = CaptchaHandler(
                driver=self.driver, 
                logger=self.logger
            )
            
            # 初始化分頁處理器 - 也需移除 config 參數
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
            self.perform_search(search_keyword)
            
            # 爬取多個頁面
            current_page = 1
            max_pages = self.config.get("pagination", {}).get("max_pages", 1)
            
            while current_page <= max_pages:
                self.logger.info(f"處理第 {current_page} 頁")
                
                # 解析當前頁面結果
                page_results = self.extract_search_results()
                self.all_results.extend(page_results)
                
                # 檢查是否需要繼續下一頁
                if current_page >= max_pages or not self.has_next_page():
                    break
                
                # 前往下一頁
                self.logger.info(f"前往第 {current_page + 1} 頁...")
                if not self.go_to_next_page():
                    break
                
                current_page += 1
            
            # 保存結果
            self.save_results()
            
            self.logger.info(f"完成爬取 {current_page} 頁，共 {len(self.all_results)} 條結果")
            return True
            
        except Exception as e:
            self.logger.error(f"爬蟲執行失敗: {str(e)}")
            self.handle_error()
            return False
            
        finally:
            self.cleanup()

    def perform_search(self, keyword: str) -> None:
        """
        執行搜尋操作
        
        Args:
            keyword: 搜尋關鍵字
        """
        try:
            from selenium.webdriver.common.by import By
            
            # 獲取搜尋框配置
            search_box_xpath = self.config.get("search_page", {}).get("search_box_xpath", "//textarea[@name='q']")
            
            # 找到搜尋框並輸入關鍵詞
            self.logger.info(f"搜尋關鍵詞: {keyword}")
            
            # 使用 list_extractor 的等待元素方法，而不是 self.wait_for_element
            search_box = self.list_extractor.wait_for_element(
                selector=search_box_xpath,
                by=By.XPATH,
                timeout=10
            )
            
            if search_box:
                search_box.clear()
                search_box.send_keys(keyword)
                search_box.submit()
                
                # 等待搜尋結果載入
                result_container_xpath = self.config.get("search_page", {}).get("result_container_xpath", "//div[@id='search']")
                
                # 使用 list_extractor 的等待元素方法
                self.list_extractor.wait_for_element(
                    selector=result_container_xpath,
                    by=By.XPATH,
                    timeout=10
                )
                
                # 頁面載入延遲
                page_load_delay = self.config.get("delays", {}).get("page_load", 1)
                time.sleep(page_load_delay)
            else:
                raise Exception("找不到搜尋框")
                
        except Exception as e:
            self.logger.error(f"執行搜尋時出錯: {str(e)}")
            raise

    def extract_search_results(self) -> List[Dict[str, Any]]:
        """
        提取搜尋結果
        
        Returns:
            搜尋結果列表
        """
        # 檢測並處理可能的驗證碼
        if self.config.get("advanced_settings", {}).get("detect_captcha", False):
            captcha_xpath = self.config.get("advanced_settings", {}).get("captcha_detection_xpath")
            if self.captcha_handler.detect_captcha(captcha_xpath):
                self.captcha_handler.handle_captcha()
                self.logger.warning("檢測到驗證碼，已嘗試處理")
        
        # 使用配置中的參數
        container_xpath = self.config.get("list_page", {}).get("container_xpath", "//div[@id='search']")
        item_xpath = self.config.get("list_page", {}).get("item_xpath", "//div[contains(@class, 'N54PNb')]")
        fields = self.config.get("list_page", {}).get("fields", {})
        max_items = self.config.get("advanced_settings", {}).get("max_results_per_page", 10)
        
        # 使用我們已經初始化的提取器
        # 而不是創建新的實例
        extraction_config = {
            "container": container_xpath,
            "items": item_xpath,
            "fields": fields,
            "max_items": max_items
        }
        
        # 設置提取器配置
        self.list_extractor.set_config(extraction_config)
        
        # 調用無參數的 extract 方法
        results = self.list_extractor.extract()
        
        self.logger.info(f"已提取 {len(results)} 條搜尋結果")
        return results

    def has_next_page(self) -> bool:
        """
        檢查是否有下一頁
        
        Returns:
            是否存在下一頁
        """
        has_next_check = self.config.get("pagination", {}).get("has_next_page_check")
        if not has_next_check:
            return False
            
        return self.pagination_handler.check_next_page_exists(has_next_check)

    def go_to_next_page(self) -> bool:
        """
        前往下一頁
        
        Returns:
            是否成功前往下一頁
        """
        next_button_xpath = self.config.get("pagination", {}).get("next_button_xpath")
        between_pages_delay = self.config.get("delays", {}).get("between_pages", 2)
        
        success = self.pagination_handler.go_to_next_page(
            next_button_xpath=next_button_xpath
        )
        
        if success:
            time.sleep(between_pages_delay)
            
        return success

    def save_results(self) -> None:
        """保存爬取結果到文件"""
        if not self.all_results:
            self.logger.warning("沒有結果可保存")
            return
            
        os.makedirs("output", exist_ok=True)
        output_file = f"output/{self.config.get('site_name', 'google_search')}_results.json"
        
        self.storage_handler.save_to_json(
            data=self.all_results,
            file_path=output_file
        )
        
        self.logger.info(f"結果已儲存至: {output_file}")

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


def main() -> None:
    """主函數：執行 Google 搜尋爬蟲"""
    # 取得配置文件路徑
    config_path = os.path.join(os.path.dirname(__file__), "basic_google_search.json")
    
    # 創建爬蟲實例
    crawler = GoogleSearchCrawler(config_path)
    
    # 執行爬蟲
    crawler.run()


if __name__ == "__main__":
    main()
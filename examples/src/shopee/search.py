#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
蝦皮搜索爬蟲
實現蝦皮網站的搜索功能
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base import ShopeeBaseScraper
from src.captcha.types import CaptchaType
from src.captcha import CaptchaManager
from src.persistence.handlers import CaptchaHandler, CaptchaDetectionResult

class ShopeeSearchScraper(ShopeeBaseScraper):
    """蝦皮搜索爬蟲"""
    
    def __init__(self, 
                 config_path: str = "./examples/config/shopee/formal/search.json",
                 data_dir: str = "./examples/data",
                 domain: str = "shopee.tw",
                 debug_mode: bool = False):
        """
        初始化爬蟲
        
        Args:
            config_path: 配置文件路徑
            data_dir: 數據目錄
            domain: 目標網站域名
            debug_mode: 是否開啟調試模式
        """
        super().__init__(config_path, data_dir, domain, debug_mode)
        
        # 加載搜索相關配置
        self._load_search_config()
        
    def _load_search_config(self) -> None:
        """加載搜索相關配置"""
        try:
            # 加載搜索相關配置
            self.search_config = self.config.get("search", {})
            self.search_url = self.search_config.get("url", "https://shopee.tw/search")
            self.search_input_selector = self.search_config.get("input_selector", "input[type='search']")
            self.search_button_selector = self.search_config.get("button_selector", "button[type='submit']")
            self.search_results_selector = self.search_config.get("results_selector", ".shopee-search-item-result__items")
            self.product_item_selector = self.search_config.get("product_item_selector", ".shopee-search-item-result__item")
            
        except Exception as e:
            self.logger.error(f"加載搜索配置失敗: {str(e)}")
            raise
            
    def search(self, keyword: str, max_retries: int = 3) -> bool:
        """
        執行搜索
        
        Args:
            keyword: 搜索關鍵詞
            max_retries: 最大重試次數
            
        Returns:
            是否搜索成功
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                # 訪問搜索頁面
                self.driver.get(self.search_url)
                self.logger.info(f"已訪問搜索頁面: {self.search_url}")
                
                # 等待搜索輸入框出現
                search_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.search_input_selector))
                )
                
                # 模擬人類輸入
                self.human_behavior.human_type(
                    self.driver,
                    search_input,
                    keyword,
                    min_delay=self.type_config.get("min_delay", 0.1),
                    max_delay=self.type_config.get("max_delay", 0.3)
                )
                
                # 等待搜索按鈕出現
                search_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.search_button_selector))
                )
                
                # 模擬人類點擊
                self.human_behavior.human_click(
                    self.driver,
                    search_button,
                    offset_range=self.click_config.get("offset_range", 5)
                )
                
                # 等待搜索結果出現
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.search_results_selector))
                )
                
                # 檢查是否有驗證碼
                if self._check_for_captcha():
                    self.logger.warning("檢測到驗證碼，嘗試處理")
                    if not self._handle_captcha():
                        self.logger.error("驗證碼處理失敗")
                        retry_count += 1
                        continue
                
                # 模擬人類瀏覽行為
                self.anti_detection.simulate_human_browsing(self.driver)
                
                # 截圖保存
                self.take_screenshot("search_results")
                
                self.logger.info(f"搜索成功: {keyword}")
                return True
                
            except TimeoutException:
                self.logger.error(f"等待元素超時 (重試 {retry_count + 1}/{max_retries})")
                retry_count += 1
                
            except Exception as e:
                self.logger.error(f"搜索失敗: {str(e)} (重試 {retry_count + 1}/{max_retries})")
                retry_count += 1
                
        self.logger.error(f"搜索失敗，已達到最大重試次數: {max_retries}")
        return False
        
    def _check_for_captcha(self) -> bool:
        """
        檢查是否存在驗證碼
        
        Returns:
            是否存在驗證碼
        """
        try:
            for captcha_type, selector in self.captcha_selectors.items():
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        self.logger.info(f"檢測到驗證碼: {captcha_type}")
                        return True
                except NoSuchElementException:
                    continue
            return False
        except Exception as e:
            self.logger.error(f"檢查驗證碼失敗: {str(e)}")
            return False
            
    def _handle_captcha(self) -> bool:
        """
        處理驗證碼
        
        Returns:
            是否處理成功
        """
        try:
            # 截圖保存
            self.take_screenshot("captcha")
            
            # 等待用戶手動處理驗證碼
            self.logger.info("請手動處理驗證碼，等待 30 秒...")
            time.sleep(30)
            
            # 檢查驗證碼是否已解決
            if not self._check_for_captcha():
                self.logger.info("驗證碼已解決")
                return True
                
            self.logger.error("驗證碼未解決")
            return False
            
        except Exception as e:
            self.logger.error(f"處理驗證碼失敗: {str(e)}")
            return False
            
    def extract_results(self) -> List[Dict[str, Any]]:
        """
        提取搜索結果
        
        Returns:
            搜索結果列表
        """
        try:
            results = []
            
            # 等待商品項目出現
            product_items = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.product_item_selector))
            )
            
            for item in product_items:
                try:
                    # 提取商品數據
                    product_data = self._extract_product_data(item)
                    
                    # 清理數據
                    cleaned_data = self._clean_product_data(product_data)
                    
                    results.append(cleaned_data)
                    
                except Exception as e:
                    self.logger.error(f"提取商品數據失敗: {str(e)}")
                    continue
                    
            self.logger.info(f"成功提取 {len(results)} 個商品")
            return results
            
        except Exception as e:
            self.logger.error(f"提取搜索結果失敗: {str(e)}")
            return []
            
    def _extract_product_data(self, item) -> Dict[str, Any]:
        """
        提取商品數據
        
        Args:
            item: 商品元素
            
        Returns:
            商品數據字典
        """
        try:
            # 提取商品標題
            title_element = item.find_element(By.CSS_SELECTOR, ".shopee-search-item-result__item-name")
            title = title_element.text.strip()
            
            # 提取商品價格
            price_element = item.find_element(By.CSS_SELECTOR, ".shopee-search-item-result__price")
            price = price_element.text.strip()
            
            # 提取商品鏈接
            link_element = item.find_element(By.CSS_SELECTOR, "a")
            link = link_element.get_attribute("href")
            
            # 提取商品圖片
            image_element = item.find_element(By.CSS_SELECTOR, "img")
            image_url = image_element.get_attribute("src")
            
            # 提取商品評分
            try:
                rating_element = item.find_element(By.CSS_SELECTOR, ".shopee-search-item-result__rating")
                rating = rating_element.text.strip()
            except NoSuchElementException:
                rating = "無評分"
                
            # 提取商品銷量
            try:
                sales_element = item.find_element(By.CSS_SELECTOR, ".shopee-search-item-result__sales")
                sales = sales_element.text.strip()
            except NoSuchElementException:
                sales = "無銷量"
                
            # 提取商品位置
            try:
                location_element = item.find_element(By.CSS_SELECTOR, ".shopee-search-item-result__location")
                location = location_element.text.strip()
            except NoSuchElementException:
                location = "未知位置"
                
            return {
                "title": title,
                "price": price,
                "link": link,
                "image_url": image_url,
                "rating": rating,
                "sales": sales,
                "location": location,
                "extracted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"提取商品數據失敗: {str(e)}")
            return {}
            
    def _clean_product_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理商品數據
        
        Args:
            data: 原始商品數據
            
        Returns:
            清理後的商品數據
        """
        try:
            # 使用數據處理器清理數據
            cleaned_data = self.data_processor.clean_data(data)
            
            # 標準化 URL
            if "link" in cleaned_data:
                cleaned_data["link"] = self.url_utils.normalize_url(cleaned_data["link"])
                
            if "image_url" in cleaned_data:
                cleaned_data["image_url"] = self.url_utils.normalize_url(cleaned_data["image_url"])
                
            return cleaned_data
            
        except Exception as e:
            self.logger.error(f"清理商品數據失敗: {str(e)}")
            return data
            
    def run(self, keyword: str) -> bool:
        """
        運行爬蟲
        
        Args:
            keyword: 搜索關鍵詞
            
        Returns:
            是否運行成功
        """
        try:
            # 執行搜索
            if not self.search(keyword):
                self.logger.error("搜索失敗")
                return False
                
            # 提取結果
            results = self.extract_results()
            
            # 保存結果
            if not self.save_results(results, keyword):
                self.logger.error("保存結果失敗")
                return False
                
            self.logger.info(f"爬蟲運行成功: {keyword}")
            return True
            
        except Exception as e:
            self.logger.error(f"爬蟲運行失敗: {str(e)}")
            return False
            
        finally:
            # 關閉瀏覽器
            self.quit()
            
if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("shopee_search_scraper.log"),
            logging.StreamHandler()
        ]
    )
    
    # 創建爬蟲實例
    scraper = ShopeeSearchScraper(debug_mode=True)
    
    # 執行搜索
    keyword = "手機"
    scraper.run(keyword)
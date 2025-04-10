"""
蝦皮爬蟲整合解決方案
集成了反爬蟲、Cookie管理和數據處理的完整方案
"""

import os
import json
import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from src.anti_detection.base_scraper import BaseScraper

class ShopeeScraper(BaseScraper):
    """蝦皮爬蟲整合類"""
    
    def __init__(self, 
                 config_path: str = "product.json",
                 data_dir: str = "./examples/data",
                 domain: str = "shopee.tw",
                 debug_mode: bool = False):
        """
        初始化爬蟲
        
        Args:
            config_path: 配置文件路徑
            data_dir: 數據目錄
            domain: 目標網站域名
            debug_mode: 是否啟用調試模式
        """
        super().__init__(config_path, data_dir, domain, debug_mode)
        
    def search_product(self, keyword: Optional[str] = None) -> bool:
        """搜尋產品"""
        try:
            if not self.driver:
                self.logger.error("WebDriver未初始化，無法搜尋產品")
                return False
                
            # 使用配置中的默認關鍵字或傳入的關鍵字
            if keyword is None:
                keyword = self.config.get("search_parameters", {}).get("keyword", {}).get("default", "")
                
            if not keyword:
                self.logger.error("搜尋關鍵字為空")
                return False
                
            self.logger.info(f"搜尋產品: {keyword}")
            
            # 從配置獲取搜尋相關的選擇器
            search_config = self.config.get("search_parameters", {}).get("keyword", {})
            input_selector = search_config.get("input_selector", "//input[@class='shopee-searchbar-input__input']")
            submit_selector = search_config.get("submit_selector", "//button[@class='btn btn-solid-primary btn--s btn--inline shopee-searchbar__search-button']")
            
            # 等待搜尋輸入框出現
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, input_selector))
            )
            
            # 清空搜尋框
            search_input.clear()
            
            # 模擬人類輸入
            # 移動到搜尋框
            ActionChains(self.driver).move_to_element(search_input).perform()
            time.sleep(random.uniform(0.5, 1.0))
            
            # 輸入關鍵字
            for char in keyword:
                search_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
                
            # 暫停一下
            time.sleep(random.uniform(0.5, 1.0))
            
            # 找到搜尋按鈕
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, submit_selector))
            )
            
            # 移動到搜尋按鈕
            ActionChains(self.driver).move_to_element(submit_button).perform()
            time.sleep(random.uniform(0.5, 1.0))
            
            # 點擊搜尋按鈕
            submit_button.click()
            
            # 等待搜尋結果載入
            wait_time = search_config.get("wait_after_submit", 5)
            time.sleep(wait_time)
            
            # 處理可能的驗證碼
            self.anti_fingerprint.handle_captcha(self.driver)
            
            # 截圖
            self._take_screenshot("search_results")
            
            # 模擬人類瀏覽行為
            self._scroll_for_products()
            
            return True
            
        except Exception as e:
            self.logger.error(f"搜尋產品時發生錯誤: {str(e)}")
            return False
            
    def _scroll_for_products(self, max_scrolls: int = 5) -> None:
        """滾動頁面以載入更多產品"""
        if not self.driver:
            return
            
        self.logger.info(f"滾動頁面以載入更多產品 (最多 {max_scrolls} 次)")
        
        # 獲取頁面加載延遲配置
        scroll_pause = self.config.get("advanced_settings", {}).get("scroll_behavior", {}).get("scroll_pause", 1.5)
        
        # 滾動頁面
        for i in range(max_scrolls):
            # 滾動頁面
            self.driver.execute_script(f"window.scrollBy(0, {random.randint(300, 800)});")
            
            # 等待頁面加載
            time.sleep(scroll_pause * random.uniform(0.8, 1.2))
            
            # 模擬隨機瀏覽行為
            if random.random() < 0.3:  # 30%的機率
                # 隨機暫停
                time.sleep(random.uniform(0.5, 1.5))
                
                # 有時向上滾動一點
                if random.random() < 0.5:
                    self.driver.execute_script(f"window.scrollBy(0, {-random.randint(100, 300)});")
                    time.sleep(random.uniform(0.5, 1.0))
                    
        # 最後再截圖
        self._take_screenshot("scrolled_products")
        
    def extract_products(self) -> List[Dict]:
        """提取產品數據"""
        if not self.driver:
            self.logger.error("WebDriver未初始化，無法提取產品數據")
            return []
            
        try:
            self.logger.info("開始提取產品數據")
            
            # 獲取配置
            list_page_config = self.config.get("list_page", {})
            container_xpath = list_page_config.get("container_xpath", "//div[contains(@class, 'shop-search-result-view')]")
            item_xpath = list_page_config.get("item_xpath", "//div[contains(@class, 'shop-search-result-view__item')]/a")
            fields = list_page_config.get("fields", {})
            
            # 等待產品容器出現
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, container_xpath))
            )
            
            # 獲取所有產品元素
            product_elements = self.driver.find_elements(By.XPATH, item_xpath)
            self.logger.info(f"找到 {len(product_elements)} 個產品")
            
            # 提取產品數據
            products = []
            for i, product_element in enumerate(product_elements):
                product_data = {}
                
                # 提取每個字段
                for field_name, field_config in fields.items():
                    xpath = field_config.get("xpath", "")
                    field_type = field_config.get("type", "text")
                    
                    try:
                        if field_type == "attribute":
                            # 獲取屬性
                            elements = product_element.find_elements(By.XPATH, xpath)
                            if elements:
                                attr = field_config.get("attribute", "src")
                                product_data[field_name] = elements[0].get_attribute(attr)
                        elif field_type == "text":
                            # 獲取文字
                            elements = product_element.find_elements(By.XPATH, xpath)
                            if elements:
                                product_data[field_name] = elements[0].text
                        elif field_type == "html":
                            # 獲取HTML
                            elements = product_element.find_elements(By.XPATH, xpath)
                            if elements:
                                product_data[field_name] = elements[0].get_attribute("innerHTML")
                    except Exception as field_e:
                        self.logger.warning(f"提取字段 {field_name} 時發生錯誤: {str(field_e)}")
                        product_data[field_name] = ""
                
                products.append(product_data)
                
                # 避免過快提取造成機器人行為特徵
                if i < len(product_elements) - 1:
                    time.sleep(random.uniform(0.05, 0.2))
                    
            # 清理數據
            products = self._clean_product_data(products)
            
            # 保存數據
            self._save_product_data(products)
            
            return products
            
        except Exception as e:
            self.logger.error(f"提取產品數據時發生錯誤: {str(e)}")
            return []
            
    def _clean_product_data(self, products: List[Dict]) -> List[Dict]:
        """清理產品數據"""
        cleaned_products = []
        for product in products:
            cleaned_product = {}
            for key, value in product.items():
                # 清理字符串
                if isinstance(value, str):
                    # 移除多餘空白
                    cleaned_value = ' '.join(value.split())
                    cleaned_product[key] = cleaned_value
                else:
                    cleaned_product[key] = value
                    
            # 標準化URL
            if 'detail_link' in cleaned_product:
                link = cleaned_product['detail_link']
                base_url = self.config.get("base_url", f"https://{self.domain}")
                
                # 確保完整URL
                if link.startswith('/'):
                    link = base_url + link
                elif not link.startswith(('http://', 'https://')):
                    link = base_url + '/' + link
                    
                cleaned_product['detail_link'] = link
                
            cleaned_products.append(cleaned_product)
            
        return cleaned_products
        
    def _save_product_data(self, products: List[Dict]) -> None:
        """保存產品數據"""
        if not products:
            self.logger.warning("沒有產品數據可保存")
            return
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存為JSON
            json_filename = f"shopee_products_{timestamp}.json"
            json_path = self.output_dir / json_filename
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"產品數據已保存為JSON: {json_path}")
            
            # 保存為CSV
            csv_filename = f"shopee_products_{timestamp}.csv"
            csv_path = self.output_dir / csv_filename
            
            import pandas as pd
            df = pd.DataFrame(products)
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            self.logger.info(f"產品數據已保存為CSV: {csv_path}")
            
        except Exception as e:
            self.logger.error(f"保存產品數據時發生錯誤: {str(e)}")
            
    def run(self, keyword: Optional[str] = None) -> bool:
        """
        執行爬蟲
        
        Args:
            keyword: 搜尋關鍵字
            
        Returns:
            是否成功
        """
        try:
            # 設置爬蟲環境
            if not self.setup():
                self.logger.error("設置爬蟲環境失敗")
                return False
                
            # 搜尋產品
            if not self.search_product(keyword):
                self.logger.error("搜尋產品失敗")
                return False
                
            # 提取產品數據
            products = self.extract_products()
            if not products:
                self.logger.error("提取產品數據失敗")
                return False
                
            self.logger.info(f"成功提取 {len(products)} 個產品數據")
            return True
            
        except Exception as e:
            self.logger.error(f"執行爬蟲時發生錯誤: {str(e)}")
            return False
        finally:
            self.close()
            
if __name__ == "__main__":
    # 設定日誌
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("shopee_scraper.log"),
            logging.StreamHandler()
        ]
    )
    
    # 創建爬蟲實例
    scraper = ShopeeScraper(
        config_path="product.json",
        data_dir="./examples/data",
        domain="shopee.tw",
        debug_mode=True
    )
    
    # 執行爬蟲
    scraper.run(keyword="手機")
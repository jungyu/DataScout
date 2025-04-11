"""
蝦皮網站分頁處理器模組

提供蝦皮網站專用的分頁處理功能，包括：
- 商品列表分頁
- 商品詳情提取
- 蝦皮特定的分頁邏輯處理
"""

from typing import Dict, Any, Optional, List, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import hashlib

from .web_pagination_handler import WebPaginationHandler
from ...config import ExtractionConfig
from ...core.exceptions import ParseError, handle_exception

class ShopeePaginationHandler(WebPaginationHandler):
    """蝦皮網站分頁處理器類"""
    
    def __init__(self, config: Union[Dict[str, Any], ExtractionConfig], driver: Optional[webdriver.Chrome] = None):
        """
        初始化蝦皮分頁處理器
        
        Args:
            config: 配置字典或ExtractionConfig對象
            driver: WebDriver實例
        """
        # 設置蝦皮特定的默認配置
        if isinstance(config, dict):
            # 設置蝦皮特定的選擇器
            config.setdefault("next_button_xpath", "//button[contains(@class, 'shopee-search-item-result__next-page')]")
            config.setdefault("page_number_xpath", "//div[contains(@class, 'shopee-search-item-result__pagination')]//a[contains(@class, 'shopee-search-item-result__page-number')]")
            config.setdefault("scroll_element_xpath", "//div[contains(@class, 'shopee-search-item-result__items')]")
            config.setdefault("new_content_xpath", "//div[contains(@class, 'shopee-search-item-result__item')]")
            
            # 設置蝦皮特定的延遲
            config.setdefault("page_load_delay", 3)
            config.setdefault("between_pages_delay", 2.0)
            
            # 設置蝦皮特定的分頁類型
            config.setdefault("pagination_type", "button_click")
            
            # 設置蝦皮特定的AJAX檢測
            config.setdefault("use_ajax_detection", True)
            config.setdefault("ajax_complete_check", "return (typeof jQuery !== 'undefined') ? jQuery.active === 0 : true")
        
        super().__init__(config, driver)
        
        # 蝦皮特定的狀態追蹤
        self.last_product_count = 0
        self.product_ids = set()
    
    def _extract_regular_items(self) -> List[Dict[str, Any]]:
        """
        提取蝦皮商品列表頁面的數據
        
        Returns:
            商品數據列表
        """
        items = []
        
        try:
            # 等待商品列表加載
            product_elements = self._wait_for_elements(By.XPATH, "//div[contains(@class, 'shopee-search-item-result__item')]")
            if not product_elements:
                self.logger.warning("未找到商品元素")
                return items
            
            # 提取每個商品
            for element in product_elements:
                try:
                    item = self._extract_item_from_element(element)
                    if item and item.get("product_id") not in self.product_ids:
                        items.append(item)
                        self.product_ids.add(item.get("product_id"))
                except Exception as e:
                    self.logger.warning(f"提取商品失敗: {str(e)}")
            
            # 更新商品計數
            self.last_product_count = len(items)
            
            return items
            
        except Exception as e:
            self.logger.error(f"提取商品列表失敗: {str(e)}")
            return items
    
    def _extract_item_from_element(self, element) -> Optional[Dict[str, Any]]:
        """
        從蝦皮商品元素中提取數據
        
        Args:
            element: 商品元素
            
        Returns:
            商品數據
        """
        try:
            # 提取商品ID
            product_id = element.get_attribute("data-itemid")
            if not product_id:
                # 嘗試從URL中提取
                product_link = element.find_element(By.XPATH, ".//a[contains(@href, '/product/')]")
                if product_link:
                    href = product_link.get_attribute("href")
                    match = re.search(r'/product/(\d+)', href)
                    if match:
                        product_id = match.group(1)
            
            if not product_id:
                self.logger.warning("無法提取商品ID")
                return None
            
            # 提取商品標題
            title_element = element.find_element(By.XPATH, ".//div[contains(@class, 'shopee-search-item-result__item-name')]")
            title = title_element.text.strip() if title_element else ""
            
            # 提取商品價格
            price_element = element.find_element(By.XPATH, ".//div[contains(@class, 'shopee-search-item-result__price')]")
            price_text = price_element.text.strip() if price_element else ""
            price = self._extract_price(price_text)
            
            # 提取商品評分
            rating_element = element.find_element(By.XPATH, ".//div[contains(@class, 'shopee-search-item-result__rating')]")
            rating = rating_element.text.strip() if rating_element else ""
            
            # 提取商品銷量
            sales_element = element.find_element(By.XPATH, ".//div[contains(@class, 'shopee-search-item-result__sold')]")
            sales_text = sales_element.text.strip() if sales_element else ""
            sales = self._extract_sales(sales_text)
            
            # 提取商品圖片
            image_element = element.find_element(By.XPATH, ".//img")
            image_url = image_element.get_attribute("src") if image_element else ""
            
            # 提取商品鏈接
            link_element = element.find_element(By.XPATH, ".//a[contains(@href, '/product/')]")
            product_url = link_element.get_attribute("href") if link_element else ""
            
            # 構建商品數據
            item = {
                "product_id": product_id,
                "title": title,
                "price": price,
                "rating": rating,
                "sales": sales,
                "image_url": image_url,
                "product_url": product_url,
                "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return item
            
        except Exception as e:
            self.logger.warning(f"從元素提取商品數據失敗: {str(e)}")
            return None
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """
        從價格文本中提取數值
        
        Args:
            price_text: 價格文本
            
        Returns:
            價格數值
        """
        try:
            # 移除貨幣符號和空格
            price_text = re.sub(r'[^\d.,]', '', price_text)
            
            # 處理不同格式的價格
            if ',' in price_text:
                # 處理帶千位分隔符的價格
                price_text = price_text.replace(',', '')
            
            # 轉換為浮點數
            return float(price_text)
            
        except Exception as e:
            self.logger.warning(f"提取價格失敗: {str(e)}")
            return None
    
    def _extract_sales(self, sales_text: str) -> Optional[int]:
        """
        從銷量文本中提取數值
        
        Args:
            sales_text: 銷量文本
            
        Returns:
            銷量數值
        """
        try:
            # 提取數字
            match = re.search(r'(\d+)', sales_text)
            if match:
                return int(match.group(1))
            return None
            
        except Exception as e:
            self.logger.warning(f"提取銷量失敗: {str(e)}")
            return None
    
    def _check_has_next_page(self) -> bool:
        """
        檢查蝦皮是否有下一頁
        
        Returns:
            是否有下一頁
        """
        try:
            # 首先使用父類的方法
            has_next = super()._check_has_next_page()
            
            # 蝦皮特定的檢查
            if has_next:
                # 檢查是否有"沒有更多商品"的提示
                no_more_elements = self.driver.find_elements(By.XPATH, "//div[contains(text(), '沒有更多商品')]")
                if no_more_elements and no_more_elements[0].is_displayed():
                    return False
                
                # 檢查當前頁的商品數量是否為0
                if self.last_product_count == 0:
                    return False
            
            return has_next
            
        except Exception as e:
            self.logger.warning(f"檢查蝦皮是否有下一頁時出錯: {str(e)}")
            return False
    
    def validate_item(self, item: Dict[str, Any]) -> bool:
        """
        驗證蝦皮商品數據
        
        Args:
            item: 商品數據
            
        Returns:
            是否有效
        """
        try:
            # 檢查必要字段
            if not item.get("product_id"):
                self.logger.warning("商品ID缺失")
                return False
            
            if not item.get("title"):
                self.logger.warning("商品標題缺失")
                return False
            
            if item.get("price") is None:
                self.logger.warning("商品價格缺失")
                return False
            
            # 檢查價格範圍
            if item.get("price") is not None and (item["price"] <= 0 or item["price"] > 1000000):
                self.logger.warning(f"商品價格異常: {item['price']}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"驗證商品數據失敗: {str(e)}")
            return False 
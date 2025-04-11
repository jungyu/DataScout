#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
蝦皮爬蟲

提供蝦皮商品搜尋和產品詳情爬取功能，包括：
- 關鍵字搜尋
- 商品列表爬取
- 產品詳情爬取
- 產品評論爬取
- 產品規格爬取
- 產品價格爬取
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Generator
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException
)

from src.core import (
    CrawlerException,
    NavigationError,
    ExtractionError,
    StateError
)

from src.captcha.handlers.service import CaptchaType
from src.captcha import CaptchaConfig

from src.captcha.solvers.shopee_solver import ShopeeSolver

from .base import ShopeeBaseScraper

class ShopeeError(CrawlerException):
    """蝦皮爬蟲錯誤"""
    pass

class ShopeeCrawler(ShopeeBaseScraper):
    """蝦皮爬蟲"""
    
    def __init__(self, config_path: str, data_dir: str = "./examples/data", captcha_config: Optional[CaptchaConfig] = None):
        """
        初始化蝦皮爬蟲
        
        Args:
            config_path: 配置文件路徑
            data_dir: 數據目錄
            captcha_config: 驗證碼配置
        """
        # 讀取配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # 添加數據目錄到配置
        config['data_dir'] = data_dir
        
        # 調用父類初始化
        super().__init__(config)
        
        # 初始化配置工具
        self.config_utils = self.config.get("utils", {})
        
        # 初始化蝦皮驗證碼求解器
        self.shopee_solver = ShopeeSolver(
            browser=self.driver,
            config=captcha_config or CaptchaConfig(
                id="shopee_captcha",
                enabled=True,
                captcha_type=CaptchaType.IMAGE,
                captcha_source="local",
                max_retries=3,
                retry_delay=1.0,
                timeout=30.0
            )
        )
        
        # 載入爬蟲相關配置
        self._load_crawler_config()
        
    def _load_crawler_config(self) -> None:
        """載入爬蟲相關配置"""
        try:
            # 載入搜尋配置
            self.search_config = self.config.get("search", {})
            self.search_selectors = self.search_config.get("selectors", {})
            self.search_timeouts = self.search_config.get("timeouts", {})
            
            # 載入產品配置
            self.product_config = self.config.get("product", {})
            self.product_selectors = self.product_config.get("selectors", {})
            self.product_timeouts = self.product_config.get("timeouts", {})
            
            # 載入評論配置
            self.review_config = self.product_config.get("review", {})
            self.review_selectors = self.review_config.get("selectors", {})
            
            # 載入規格配置
            self.spec_config = self.product_config.get("spec", {})
            self.spec_selectors = self.spec_config.get("selectors", {})
            
        except Exception as e:
            raise ShopeeError(f"載入爬蟲配置失敗: {str(e)}")
            
    def _handle_captcha(self) -> bool:
        """
        處理驗證碼
        
        Returns:
            是否處理成功
        """
        try:
            # 檢查是否存在驗證碼
            captcha_type = self._detect_captcha()
            if not captcha_type:
                return True
                
            # 檢查驗證碼元素
            captcha_selector = self._get_captcha_selector(captcha_type)
            if not captcha_selector:
                self.logger.error(f"未找到驗證碼選擇器: {captcha_type}")
                return False
                
            # 獲取驗證碼元素
            captcha_element = self.driver.find_element(By.CSS_SELECTOR, captcha_selector)
            if not captcha_element:
                self.logger.error(f"未找到驗證碼元素: {captcha_selector}")
                return False
                
            # 使用蝦皮驗證碼求解器處理
            result = self.shopee_solver.solve(
                driver=self.driver,
                element=captcha_element,
                captcha_type=captcha_type
            )
            
            if result.success:
                self.logger.info(f"成功解決驗證碼: {captcha_type}")
                return True
                
            self.logger.error(f"解決驗證碼失敗: {captcha_type}")
            return False
            
        except Exception as e:
            self.logger.error(f"處理驗證碼失敗: {str(e)}")
            return False
            
    def _detect_captcha(self) -> Optional[CaptchaType]:
        """
        檢測驗證碼類型
        
        Returns:
            驗證碼類型，如果不存在則返回 None
        """
        try:
            # 檢查滑塊驗證碼
            if self._is_element_present(self.search_selectors.get("slider_captcha")):
                return CaptchaType.SLIDER
                
            # 檢查圖片驗證碼
            if self._is_element_present(self.search_selectors.get("image_captcha")):
                return CaptchaType.IMAGE
                
            # 檢查點擊驗證碼
            if self._is_element_present(self.search_selectors.get("click_captcha")):
                return CaptchaType.CLICK
                
            return None
            
        except Exception as e:
            self.logger.error(f"檢測驗證碼失敗: {str(e)}")
            return None
            
    def _is_element_present(self, selector: Optional[str]) -> bool:
        """
        檢查元素是否存在
        
        Args:
            selector: CSS 選擇器
            
        Returns:
            元素是否存在
        """
        if not selector:
            return False
            
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.is_displayed()
        except NoSuchElementException:
            return False
            
    def search_products(self, keyword: str, max_pages: int = 1) -> Generator[Dict[str, Any], None, None]:
        """
        搜尋商品
        
        Args:
            keyword: 搜尋關鍵字
            max_pages: 最大爬取頁數
            
        Yields:
            商品資訊字典
        """
        try:
            # 構建搜尋 URL
            search_url = self.url_utils.build_search_url(keyword)
            
            # 訪問搜尋頁面
            self.driver.get(search_url)
            
            # 處理驗證碼
            if not self._handle_captcha():
                raise ShopeeError("處理驗證碼失敗")
                
            # 等待搜尋結果加載
            self.wait_for_element(
                By.CSS_SELECTOR,
                self.search_selectors.get("product_list"),
                self.search_timeouts.get("search_load")
            )
            
            # 爬取指定頁數
            for page in range(max_pages):
                # 獲取當前頁面的商品列表
                products = self._get_product_list()
                
                # 輸出商品資訊
                for product in products:
                    yield product
                    
                # 如果不是最後一頁，點擊下一頁
                if page < max_pages - 1:
                    if not self._go_to_next_page():
                        break
                        
        except Exception as e:
            raise ShopeeError(f"搜尋商品失敗: {str(e)}")
            
    def _get_product_list(self) -> List[Dict[str, Any]]:
        """獲取商品列表"""
        try:
            products = []
            product_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                self.search_selectors.get("product_item")
            )
            
            for element in product_elements:
                try:
                    product = {
                        "id": element.get_attribute("data-productid"),
                        "title": element.find_element(
                            By.CSS_SELECTOR,
                            self.search_selectors.get("title")
                        ).text.strip(),
                        "price": self._extract_price(
                            element.find_element(
                                By.CSS_SELECTOR,
                                self.search_selectors.get("price")
                            ).text
                        ),
                        "shop": element.find_element(
                            By.CSS_SELECTOR,
                            self.search_selectors.get("shop")
                        ).text.strip(),
                        "location": element.find_element(
                            By.CSS_SELECTOR,
                            self.search_selectors.get("location")
                        ).text.strip(),
                        "crawl_time": datetime.now().isoformat()
                    }
                    products.append(product)
                except NoSuchElementException:
                    continue
                    
            return products
            
        except Exception as e:
            raise ExtractionError(f"獲取商品列表失敗: {str(e)}")
            
    def _go_to_next_page(self) -> bool:
        """前往下一頁"""
        try:
            next_button = self.driver.find_element(
                By.CSS_SELECTOR,
                self.search_selectors.get("next_page")
            )
            
            if not next_button.is_enabled():
                return False
                
            next_button.click()
            
            # 等待頁面加載
            self.wait_for_element(
                By.CSS_SELECTOR,
                self.search_selectors.get("product_list"),
                self.search_timeouts.get("page_load")
            )
            
            return True
            
        except NoSuchElementException:
            return False
        except Exception as e:
            self.logger.error(f"前往下一頁失敗: {str(e)}")
            return False
            
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """
        獲取產品詳情
        
        Args:
            product_id: 產品 ID
            
        Returns:
            產品詳情字典
        """
        try:
            # 構建產品 URL
            product_url = self.url_utils.build_product_url(product_id)
            
            # 訪問產品頁面
            self.driver.get(product_url)
            
            # 處理驗證碼
            if not self._handle_captcha():
                raise ShopeeError("處理驗證碼失敗")
                
            # 等待產品詳情加載
            self.wait_for_element(
                By.CSS_SELECTOR,
                self.product_selectors.get("product_container"),
                self.product_timeouts.get("product_load")
            )
            
            # 提取產品詳情
            product_details = {
                "id": product_id,
                "title": self._get_product_title(),
                "price": self._get_product_price(),
                "specs": self._get_product_specs(),
                "reviews": self._get_product_reviews(),
                "shop": self._get_shop_info(),
                "crawl_time": datetime.now().isoformat()
            }
            
            return product_details
            
        except Exception as e:
            raise ShopeeError(f"獲取產品詳情失敗: {str(e)}")
            
    def _get_product_title(self) -> str:
        """獲取產品標題"""
        try:
            element = self.wait_for_element(
                By.CSS_SELECTOR,
                self.product_selectors.get("title")
            )
            return element.text.strip()
        except Exception as e:
            raise ExtractionError(f"獲取產品標題失敗: {str(e)}")
            
    def _get_product_price(self) -> Dict[str, Any]:
        """獲取產品價格"""
        try:
            price_element = self.wait_for_element(
                By.CSS_SELECTOR,
                self.product_selectors.get("price")
            )
            
            return {
                "current": self._extract_price(price_element.text),
                "original": self._get_original_price(),
                "discount": self._get_discount_info()
            }
        except Exception as e:
            raise ExtractionError(f"獲取產品價格失敗: {str(e)}")
            
    def _extract_price(self, price_text: str) -> float:
        """提取價格數值"""
        try:
            # 移除貨幣符號和空格
            price_text = price_text.replace("$", "").replace(",", "").strip()
            return float(price_text)
        except ValueError:
            raise ExtractionError(f"價格格式無效: {price_text}")
            
    def _get_original_price(self) -> Optional[float]:
        """獲取原價"""
        try:
            element = self.driver.find_element(
                By.CSS_SELECTOR,
                self.product_selectors.get("original_price")
            )
            return self._extract_price(element.text)
        except NoSuchElementException:
            return None
        except Exception as e:
            self.logger.warning(f"獲取原價失敗: {str(e)}")
            return None
            
    def _get_discount_info(self) -> Dict[str, Any]:
        """獲取折扣信息"""
        try:
            element = self.driver.find_element(
                By.CSS_SELECTOR,
                self.product_selectors.get("discount")
            )
            return {
                "percentage": self._extract_discount_percentage(element.text),
                "end_time": self._extract_discount_end_time()
            }
        except NoSuchElementException:
            return {"percentage": 0, "end_time": None}
        except Exception as e:
            self.logger.warning(f"獲取折扣信息失敗: {str(e)}")
            return {"percentage": 0, "end_time": None}
            
    def _extract_discount_percentage(self, discount_text: str) -> int:
        """提取折扣百分比"""
        try:
            # 移除百分號和空格
            discount_text = discount_text.replace("%", "").strip()
            return int(discount_text)
        except ValueError:
            return 0
            
    def _extract_discount_end_time(self) -> Optional[str]:
        """提取折扣結束時間"""
        try:
            element = self.driver.find_element(
                By.CSS_SELECTOR,
                self.product_selectors.get("discount_end_time")
            )
            return element.text.strip()
        except NoSuchElementException:
            return None
        except Exception as e:
            self.logger.warning(f"提取折扣結束時間失敗: {str(e)}")
            return None
            
    def _get_product_specs(self) -> List[Dict[str, Any]]:
        """獲取產品規格"""
        try:
            specs = []
            spec_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                self.spec_selectors.get("spec_item")
            )
            
            for element in spec_elements:
                try:
                    spec = {
                        "name": element.find_element(
                            By.CSS_SELECTOR,
                            self.spec_selectors.get("name")
                        ).text.strip(),
                        "value": element.find_element(
                            By.CSS_SELECTOR,
                            self.spec_selectors.get("value")
                        ).text.strip()
                    }
                    specs.append(spec)
                except NoSuchElementException:
                    continue
                    
            return specs
            
        except Exception as e:
            raise ExtractionError(f"獲取產品規格失敗: {str(e)}")
            
    def _get_product_reviews(self) -> List[Dict[str, Any]]:
        """獲取產品評論"""
        try:
            reviews = []
            
            # 點擊評論標籤
            review_tab = self.wait_for_element(
                By.CSS_SELECTOR,
                self.review_selectors.get("review_tab")
            )
            review_tab.click()
            
            # 等待評論加載
            self.wait_for_element(
                By.CSS_SELECTOR,
                self.review_selectors.get("review_list"),
                self.product_timeouts.get("review_load")
            )
            
            # 獲取評論列表
            review_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                self.review_selectors.get("review_item")
            )
            
            for element in review_elements:
                try:
                    review = {
                        "user": element.find_element(
                            By.CSS_SELECTOR,
                            self.review_selectors.get("user")
                        ).text.strip(),
                        "rating": self._extract_rating(element),
                        "content": element.find_element(
                            By.CSS_SELECTOR,
                            self.review_selectors.get("content")
                        ).text.strip(),
                        "time": element.find_element(
                            By.CSS_SELECTOR,
                            self.review_selectors.get("time")
                        ).text.strip()
                    }
                    reviews.append(review)
                except NoSuchElementException:
                    continue
                    
            return reviews
            
        except Exception as e:
            raise ExtractionError(f"獲取產品評論失敗: {str(e)}")
            
    def _extract_rating(self, element: Any) -> int:
        """提取評分"""
        try:
            rating_element = element.find_element(
                By.CSS_SELECTOR,
                self.review_selectors.get("rating")
            )
            # 假設評分是 1-5 的整數
            return int(rating_element.get_attribute("data-rating"))
        except (NoSuchElementException, ValueError):
            return 0
            
    def _get_shop_info(self) -> Dict[str, Any]:
        """獲取商店信息"""
        try:
            return {
                "name": self.wait_for_element(
                    By.CSS_SELECTOR,
                    self.product_selectors.get("shop_name")
                ).text.strip(),
                "rating": self._extract_shop_rating(),
                "follower_count": self._extract_shop_follower_count(),
                "product_count": self._extract_shop_product_count()
            }
        except Exception as e:
            raise ExtractionError(f"獲取商店信息失敗: {str(e)}")
            
    def _extract_shop_rating(self) -> float:
        """提取商店評分"""
        try:
            element = self.driver.find_element(
                By.CSS_SELECTOR,
                self.product_selectors.get("shop_rating")
            )
            return float(element.text.strip())
        except (NoSuchElementException, ValueError):
            return 0.0
            
    def _extract_shop_follower_count(self) -> int:
        """提取商店粉絲數"""
        try:
            element = self.driver.find_element(
                By.CSS_SELECTOR,
                self.product_selectors.get("shop_follower_count")
            )
            # 移除逗號和空格
            count_text = element.text.replace(",", "").strip()
            return int(count_text)
        except (NoSuchElementException, ValueError):
            return 0
            
    def _extract_shop_product_count(self) -> int:
        """提取商店商品數"""
        try:
            element = self.driver.find_element(
                By.CSS_SELECTOR,
                self.product_selectors.get("shop_product_count")
            )
            # 移除逗號和空格
            count_text = element.text.replace(",", "").strip()
            return int(count_text)
        except (NoSuchElementException, ValueError):
            return 0

    def _get_captcha_selector(self, captcha_type: CaptchaType) -> Optional[str]:
        """
        獲取驗證碼選擇器
        
        Args:
            captcha_type: 驗證碼類型
            
        Returns:
            選擇器字符串
        """
        selector_map = {
            CaptchaType.SLIDER: self.search_selectors.get("slider_captcha"),
            CaptchaType.IMAGE: self.search_selectors.get("image_captcha"),
            CaptchaType.CLICK: self.search_selectors.get("click_captcha")
        }
        return selector_map.get(captcha_type)

def main():
    """主函數"""
    # 配置
    config = {
        "webdriver": {
            "browser_type": "chrome",
            "headless": True,
            "timeout": 30,
            "retry_count": 3
        },
        "output_dir": "output/shopee",
        "max_pages": 10
    }
    
    # 創建爬蟲實例
    crawler = ShopeeCrawler(config)
    
    # 開始爬取
    search_url = "https://shopee.tw/search?keyword=手機"
    items = crawler.start(search_url)
    
    # 輸出統計信息
    print(f"爬取完成，共獲取 {len(items)} 個商品")

if __name__ == "__main__":
    main() 
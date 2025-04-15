#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MomoShop 爬蟲

此模組提供 MomoShop 網站的爬蟲功能。
支援以下功能：
- 關鍵字搜尋（-method search -keyword "關鍵字"）
- 分類瀏覽（-method category -category_id "分類ID"）
- 商品詳情（-method product -product_id "商品ID"）
"""

import logging
import argparse
from typing import Dict, List, Optional, Any
import sys
from pathlib import Path
from urllib.parse import urlencode, quote
import json

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from playwright_base import PlaywrightBase, setup_logger
from examples.formal.momoshop.captcha_handler import MomoShopCaptchaHandler
from examples.formal.momoshop.config import SITE_CONFIG, SELECTORS, BROWSER_CONFIG

# 設置日誌
logger = setup_logger(name=__name__)

class MomoShopScraper(PlaywrightBase):
    """
    MomoShop 爬蟲類
    
    繼承自 PlaywrightBase，提供 MomoShop 網站的爬蟲功能
    """
    
    def __init__(self):
        """
        初始化 MomoShop 爬蟲
        """
        self.logger = logging.getLogger(__name__)
        super().__init__(
            headless=BROWSER_CONFIG.get("headless", True),
            proxy=BROWSER_CONFIG.get("proxy", None),
            browser_type=BROWSER_CONFIG.get("browser_type", "chromium"),
            **BROWSER_CONFIG.get("launch_options", {})
        )
        
        self.site_config = SITE_CONFIG
        self.selectors = SELECTORS
        self.captcha_handler = None
        
        # 設置瀏覽器上下文選項
        if self._context:
            context_options = BROWSER_CONFIG.get("context_options", {})
            if "viewport" in context_options:
                self._context.set_viewport_size(**context_options["viewport"])
        
        # 啟動瀏覽器
        self.start()
        
        logger.info("MomoShop 爬蟲已初始化")
        
    def setup_captcha_handler(self):
        """
        設置驗證碼處理器
        """
        if not self.captcha_handler:
            self.captcha_handler = MomoShopCaptchaHandler(
                driver=self.page,
                config=self.site_config.get("captcha", {}),
                logger=logger
            )
            logger.info("驗證碼處理器已設置")
            
    def search_products(self, keyword: str, page: int = 1) -> List[Dict[str, Any]]:
        """
        搜索商品
        
        Args:
            keyword: 搜索關鍵字
            page: 頁碼
            
        Returns:
            List[Dict[str, Any]]: 商品列表
        """
        url = f"{self.site_config['base_url']}/search/searchShop.jsp?searchKeyword={quote(keyword)}&curPage={page}"
        logger.info(f"搜索商品: {keyword}, 頁碼: {page}")
        
        self.navigate(url)
        self.wait_for_load_state("networkidle", timeout=60000)
        
        # 檢查是否有驗證碼
        if self.page.locator(self.selectors["captcha"]["recaptcha"]).count() > 0:
            logger.info("檢測到 reCAPTCHA 驗證碼")
            self.setup_captcha_handler()
            self.captcha_handler.handle_recaptcha()
            
        # 保存頁面內容以供分析
        content = self.page.content()
        with open(f"search_result_{keyword}_{page}.html", "w", encoding="utf-8") as f:
            f.write(content)
        self.page.screenshot(path=f"search_result_{keyword}_{page}.png")
        logger.info(f"已保存搜尋結果頁面到 search_result_{keyword}_{page}.html")
            
        # 提取商品列表
        products = []
        try:
            product_elements = self.page.locator(self.selectors["search"]["list_item"]).all()
            logger.info(f"找到 {len(product_elements)} 個商品元素")
            
            for element in product_elements:
                try:
                    product = {
                        "name": element.locator(self.selectors["search"]["name"]).text_content(),
                        "price": element.locator(self.selectors["search"]["price"]).text_content(),
                        "image_url": element.locator(self.selectors["search"]["image"]).get_attribute("src"),
                        "product_url": element.locator(self.selectors["search"]["link"]).get_attribute("href"),
                        "promotion": element.locator(self.selectors["search"]["promotion"]).text_content(),
                        "tags": [tag.text_content() for tag in element.locator(self.selectors["search"]["tags"]).all()]
                    }
                    products.append(product)
                except Exception as e:
                    logger.error(f"提取商品信息失敗: {str(e)}")
                    continue
                    
            logger.info(f"成功提取 {len(products)} 個商品")
            return products
            
        except Exception as e:
            logger.error(f"搜尋商品時發生錯誤: {str(e)}")
            raise
        
    def get_category_products(self, category_id: str, page: int = 1) -> List[Dict[str, Any]]:
        """
        獲取分類商品
        
        Args:
            category_id: 分類 ID
            page: 頁碼
            
        Returns:
            List[Dict[str, Any]]: 商品列表
        """
        url = f"{self.site_config['base_url']}/category.momo?cateLevel=0&cateId={category_id}&curPage={page}"
        logger.info(f"獲取分類商品: {category_id}, 頁碼: {page}")
        
        self.navigate(url)
        self.wait_for_load_state("networkidle")
        
        # 檢查是否有驗證碼
        if self.page.locator(self.selectors["captcha"]["recaptcha"]).count() > 0:
            logger.info("檢測到 reCAPTCHA 驗證碼")
            self.setup_captcha_handler()
            self.captcha_handler.handle_recaptcha()
            
        # 提取商品列表
        products = []
        product_elements = self.page.locator(self.selectors["product"]["list_item"]).all()
        
        for element in product_elements:
            try:
                product = {
                    "id": element.get_attribute("data-product-id"),
                    "name": element.locator(self.selectors["product"]["name"]).text_content(),
                    "price": element.locator(self.selectors["product"]["price"]).text_content(),
                    "url": element.locator(self.selectors["product"]["link"]).get_attribute("href"),
                }
                products.append(product)
            except Exception as e:
                logger.error(f"提取商品信息失敗: {str(e)}")
                
        logger.info(f"成功提取 {len(products)} 個商品")
        return products
        
    def get_product_detail(self, product_id: str) -> Dict[str, Any]:
        """
        獲取商品詳情
        
        Args:
            product_id: 商品 ID
            
        Returns:
            Dict[str, Any]: 商品詳情
        """
        url = f"{self.site_config['base_url']}/goods/GoodsDetail.jsp?i_code={product_id}"
        logger.info(f"獲取商品詳情: {product_id}")
        
        self.navigate(url)
        self.wait_for_load_state("networkidle")
        
        # 檢查是否有驗證碼
        if self.page.locator(self.selectors["captcha"]["recaptcha"]).count() > 0:
            logger.info("檢測到 reCAPTCHA 驗證碼")
            self.setup_captcha_handler()
            self.captcha_handler.handle_recaptcha()
            
        try:
            # 使用配置中定義的選擇器提取商品資訊
            product = {
                "name": self.page.locator(self.selectors["product"]["detail_name"]).text_content(),
                "price": self.page.locator(self.selectors["product"]["detail_price"]).text_content(),
                "image_url": self.page.locator(self.selectors["product"]["image"]).get_attribute("src"),
                "product_url": self.page.locator(self.selectors["product"]["link"]).get_attribute("href"),
                "promotion": self.page.locator(self.selectors["product"]["promotion"]).text_content(),
                "tags": [tag.text_content() for tag in self.page.locator(self.selectors["product"]["tags"]).all()]
            }
            
            logger.info(f"成功提取商品詳情: {product['name']}")
            return product
            
        except Exception as e:
            logger.error(f"提取商品詳情時發生錯誤: {str(e)}")
            raise
            
    def close(self):
        """
        關閉瀏覽器
        """
        super().close()
        logger.info("MomoShop 爬蟲已關閉")
        
def parse_args():
    """
    解析命令行參數
    
    Returns:
        argparse.Namespace: 命令行參數
    """
    parser = argparse.ArgumentParser(description="MomoShop 爬蟲")
    parser.add_argument("-method", type=str, required=True, choices=["search", "category", "product"],
                        help="爬蟲方法: search(搜尋), category(分類), product(商品詳情)")
    parser.add_argument("-keyword", type=str, help="搜尋關鍵字")
    parser.add_argument("-category_id", type=str, help="分類 ID")
    parser.add_argument("-product_id", type=str, help="商品 ID")
    parser.add_argument("-page", type=int, default=1, help="頁碼")
    
    return parser.parse_args()
    
def main():
    """
    主函數
    """
    args = parse_args()
    
    scraper = MomoShopScraper()
    
    try:
        if args.method == "search":
            if not args.keyword:
                logger.error("搜尋方法需要提供關鍵字")
                return
            products = scraper.search_products(args.keyword, args.page)
            logger.info(f"搜尋結果: {len(products)} 個商品")
            
        elif args.method == "category":
            if not args.category_id:
                logger.error("分類方法需要提供分類 ID")
                return
            products = scraper.get_category_products(args.category_id, args.page)
            logger.info(f"分類結果: {len(products)} 個商品")
            
        elif args.method == "product":
            if not args.product_id:
                logger.error("商品詳情方法需要提供商品 ID")
                return
            product = scraper.get_product_detail(args.product_id)
            logger.info(f"商品詳情: {product}")
            
    except Exception as e:
        logger.error(f"執行爬蟲時發生錯誤: {str(e)}")
    finally:
        scraper.close()
        
if __name__ == "__main__":
    main() 
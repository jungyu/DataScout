#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MomoShop 爬蟲

此模組提供 MomoShop 網站的爬蟲功能。
"""

import logging
import argparse
from typing import Dict, List, Optional, Any
import sys
from pathlib import Path
from urllib.parse import quote
from datetime import datetime

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from playwright_base import PlaywrightBase, setup_logger
from examples.formal.momoshop.captcha_handler import MomoShopCaptchaHandler
from examples.formal.momoshop.config import SITE_CONFIG, SELECTORS, BROWSER_CONFIG

logger = setup_logger(name=__name__)

class PageException(Exception):
    """頁面操作失敗異常"""
    pass

class ElementException(Exception):
    """元素操作失敗異常"""
    pass

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

    def search_products(self, keyword: str, page: int = 1, save_page: bool = True) -> List[Dict[str, Any]]:
        """
        搜索商品並提取結果

        Args:
            keyword: 搜索關鍵字
            page: 頁碼，默認為1
            save_page: 是否保存頁面內容，默認為True

        Returns:
            List[Dict[str, Any]]: 商品列表，每個商品為一個字典

        Raises:
            PageException: 頁面操作失敗
            ElementException: 元素操作失敗
        """
        try:
            url = f"{self.site_config['search_url']}?keyword={quote(keyword)}&cateLevel=0&_isFuzzy=0&searchType=1&curPage={page}"
            logger.info(f"搜索商品: {keyword}, 頁碼: {page}")

            self.navigate(url)
            self.wait_for_load_state("networkidle", timeout=self.site_config.get("request", {}).get("timeout", 60000))

            self._handle_captcha_if_present()

            if save_page:
                self._save_page_content(keyword, page)

            return self._extract_product_list("search")

        except Exception as e:
            logger.error(f"搜尋商品時發生錯誤: {str(e)}")
            raise PageException(f"搜尋商品失敗: {str(e)}")

    def _handle_captcha_if_present(self):
        """處理頁面上可能出現的驗證碼"""
        captcha_selectors = self.selectors.get("captcha", {})

        for captcha_type, selector in captcha_selectors.items():
            try:
                if self.page.locator(selector).count() > 0:
                    logger.info(f"檢測到 {captcha_type} 驗證碼")
                    self.setup_captcha_handler()
                    handler_method = getattr(self.captcha_handler, f"handle_{captcha_type}", None)
                    if handler_method and callable(handler_method):
                        result = handler_method()
                        if result:
                            logger.info(f"{captcha_type} 驗證碼處理成功")
                        else:
                            logger.warning(f"{captcha_type} 驗證碼處理失敗")
                    else:
                        logger.warning(f"未找到處理 {captcha_type} 驗證碼的方法")
            except Exception as e:
                logger.error(f"處理 {captcha_type} 驗證碼時發生錯誤: {str(e)}")

    def _save_page_content(self, keyword: str, page: int):
        """保存頁面內容和截圖"""
        try:
            base_name = f"search_result_{keyword}_{page}"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{base_name}_{timestamp}"

            save_dir = Path(self.site_config.get("save_path", "data/raw"))
            save_dir.mkdir(parents=True, exist_ok=True)

            content = self.page.content()
            html_path = save_dir / f"{file_name}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(content)

            screenshot_path = save_dir / f"{file_name}.png"
            self.page.screenshot(path=str(screenshot_path))

            logger.info(f"已保存頁面內容: HTML={html_path}, 截圖={screenshot_path}")
        except Exception as e:
            logger.warning(f"保存頁面內容時發生錯誤: {str(e)}")

    def _extract_product_list(self, list_type: str) -> List[Dict[str, Any]]:
        """
        從頁面提取商品列表

        Args:
            list_type: 列表類型，可以是 "search" 或 "category"

        Returns:
            List[Dict[str, Any]]: 商品列表
        """
        products = []
        selectors = self.selectors.get(list_type, {})

        try:
            product_elements = self.page.locator(selectors.get("list_item", "")).all()
            logger.info(f"找到 {len(product_elements)} 個商品元素")

            for element in product_elements:
                try:
                    product = self._extract_product_data(element, selectors)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.error(f"提取商品信息失敗: {str(e)}")
                    continue

            logger.info(f"成功提取 {len(products)} 個商品")
            return products

        except Exception as e:
            logger.error(f"提取商品列表時發生錯誤: {str(e)}")
            return []

    def _extract_product_data(self, element, selectors: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """從元素中提取商品數據"""
        try:
            product = {}

            for field, selector in selectors.items():
                if field in ["list_item", "tags"]:
                    continue

                try:
                    if field.endswith("_url") or field.endswith("_src"):
                        attr_name = "src" if field.endswith("_src") else "href"
                        value = element.locator(selector).get_attribute(attr_name)
                    else:
                        value = element.locator(selector).text_content().strip()

                    product[field] = value
                except Exception:
                    product[field] = ""

            if "tags" in selectors:
                try:
                    product["tags"] = [tag.text_content().strip() for tag in element.locator(selectors["tags"]).all()]
                except Exception:
                    product["tags"] = []

            return product

        except Exception as e:
            logger.error(f"提取商品數據時發生錯誤: {str(e)}")
            return None

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

        self._handle_captcha_if_present()

        return self._extract_product_list("product")

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

        self._handle_captcha_if_present()

        try:
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
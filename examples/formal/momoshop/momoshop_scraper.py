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

    def search_products(self, keyword: str, page: int = 1, save_page: bool = True, auto_paging: bool = False) -> List[Dict[str, Any]]:
        """
        搜索商品並提取結果，可自動翻頁直到最後一頁

        Args:
            keyword: 搜索關鍵字
            page: 起始頁碼，默認為1
            save_page: 是否保存頁面內容，默認為True
            auto_paging: 是否自動翻頁直到最後一頁

        Returns:
            List[Dict[str, Any]]: 商品列表，每個商品為一個字典

        Raises:
            PageException: 頁面操作失敗
            ElementException: 元素操作失敗
        """
        all_products = []
        cur_page = page

        while True:
            try:
                url = (
                    f"{self.site_config['search_url']}?keyword={quote(keyword)}"
                    f"&cateLevel=0&_isFuzzy=0&searchType=1&curPage={cur_page}"
                )
                logger.info(f"搜索商品: {keyword}, 頁碼: {cur_page}，URL: {url}")

                self.navigate(url)
                self.wait_for_load_state("networkidle", timeout=self.site_config.get("request", {}).get("timeout", 60000))
                self._handle_captcha_if_present()

                if save_page:
                    self._save_page_content(keyword, cur_page)

                products = self._extract_product_list("search")
                if not products:
                    logger.info(f"第 {cur_page} 頁無商品，結束自動翻頁")
                    break

                all_products.extend(products)
                logger.info(f"第 {cur_page} 頁擷取 {len(products)} 筆商品，累計 {len(all_products)} 筆")

                if not auto_paging:
                    break

                # 檢查是否有下一頁（根據分頁按鈕是否存在或商品數量是否小於每頁最大數）
                next_btn = self.page.locator("a.next")
                if next_btn.count() == 0 or "disabled" in (next_btn.get_attribute("class") or ""):
                    logger.info("已到最後一頁，結束自動翻頁")
                    break

                cur_page += 1

            except Exception as e:
                logger.error(f"搜尋商品時發生錯誤: {str(e)}")
                raise PageException(f"搜尋商品失敗: {str(e)}")

        return all_products

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
            # 等待商品列表加載完成
            self.page.wait_for_selector(selectors.get("list_item", "div.goodsUrl"), 
                                        timeout=self.site_config.get("request", {}).get("timeout", 60000))
            
            # 使用 locator 方法查找所有商品元素
            product_elements = self.page.locator(selectors.get("list_item", "div.goodsUrl")).all()
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
        """從元素中提取商品數據

        Args:
            element: 商品元素
            selectors: 選擇器字典

        Returns:
            Optional[Dict[str, Any]]: 商品數據字典，如果提取失敗則返回 None
        """
        try:
            product = {}

            # 商品名稱
            try:
                name_element = element.locator(selectors.get("name", "h3.prdName"))
                product["name"] = name_element.text_content().strip()
                product["full_name"] = name_element.get_attribute("title") or product["name"]
            except Exception as e:
                logger.warning(f"提取商品名稱失敗: {str(e)}")
                product["name"] = ""
                product["full_name"] = ""

            # 商品價格
            try:
                price_element = element.locator(selectors.get("price", "div.money b"))
                price_text = price_element.text_content().strip()
                product["price"] = price_text.replace(",", "")
            except Exception as e:
                logger.warning(f"提取商品價格失敗: {str(e)}")
                product["price"] = ""

            # 商品連結
            try:
                link_element = element.locator(selectors.get("link", "a.goods-img-url"))
                if link_element.count() > 0:
                    product["link"] = link_element.first.get_attribute("href")
                else:
                    product["link"] = ""
            except Exception as e:
                logger.warning(f"提取商品鏈接失敗: {str(e)}")
                product["link"] = ""

            # 商品主圖
            try:
                img_element = element.locator(selectors.get("image", "img.prdImg"))
                if img_element.count() > 0:
                    product["image"] = img_element.first.get_attribute("src")
                    product["image_alt"] = img_element.first.get_attribute("alt") or ""
                else:
                    product["image"] = ""
                    product["image_alt"] = ""
            except Exception as e:
                logger.warning(f"提取商品圖片失敗: {str(e)}")
                product["image"] = ""
                product["image_alt"] = ""

            # 促銷資訊
            try:
                promotion_element = element.locator(selectors.get("promotion", "p.sloganTitle"))
                product["promotion"] = promotion_element.text_content().strip()
            except Exception as e:
                logger.warning(f"提取促銷信息失敗: {str(e)}")
                product["promotion"] = ""

            # 標籤
            try:
                tags_elements = element.locator(selectors.get("tags", "div.iconArea i")).all()
                product["tags"] = [tag.text_content().strip() for tag in tags_elements if tag.text_content().strip()]
            except Exception as e:
                logger.warning(f"提取標籤失敗: {str(e)}")
                product["tags"] = []

            # 商品 ID
            try:
                if product["link"]:
                    import re
                    id_match = re.search(r"i_code=(\d+)", product["link"])
                    if id_match:
                        product["id"] = id_match.group(1)
                    else:
                        product["id"] = ""
                else:
                    product["id"] = ""
            except Exception as e:
                logger.warning(f"提取商品 ID 失敗: {str(e)}")
                product["id"] = ""

            # 評分
            try:
                rating_element = element.locator(selectors.get("rating", "div.ratingStars"))
                if rating_element.count() > 0:
                    product["rating"] = rating_element.first.get_attribute("data-rating") or "0"
                else:
                    product["rating"] = "0"
            except Exception as e:
                logger.warning(f"提取評分失敗: {str(e)}")
                product["rating"] = "0"

            # 折扣
            try:
                discount_element = element.locator(selectors.get("discount", "span.discountTxt"))
                if discount_element.count() > 0:
                    product["discount"] = discount_element.first.text_content().strip()
                else:
                    product["discount"] = ""
            except Exception as e:
                logger.warning(f"提取折扣信息失敗: {str(e)}")
                product["discount"] = ""

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
        獲取商品詳情（包含商品規格與評論）

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

        sel = self.selectors["product"]
        try:
            product = {
                "name": self.page.locator(sel["detail_name"]).text_content().strip(),
                "price": self.page.locator(sel["detail_price"]).text_content().strip(),
                "image_url": self.page.locator(sel["image"]).get_attribute("src"),
                "promotion": self.page.locator(sel["promotion"]).text_content().strip(),
                "tags": [tag.text_content().strip() for tag in self.page.locator(sel["tags"]).all()],
                "description": self.page.locator(sel["description"]).text_content().strip() if self.page.locator(sel["description"]).count() > 0 else "",
                "images": [img.get_attribute("src") for img in self.page.locator(sel["images"]).all()],
            }

            # 商品規格
            specs = {}
            for row in self.page.locator(sel["specs_table"]).all():
                th = row.locator(sel["spec_name"])
                td = row.locator(sel["spec_value"])
                if th.count() > 0 and td.count() > 0:
                    key = th.first.text_content().strip()
                    values = [li.text_content().strip() for li in td.first.locator("li").all()]
                    specs[key] = values if len(values) > 1 else (values[0] if values else "")
            product["specs"] = specs

            # 商品評論
            reviews = []
            for card in self.page.locator(sel["review_card"]).all():
                try:
                    review = {
                        "name": card.locator(sel["review_name"]).first.text_content().strip() if card.locator(sel["review_name"]).count() > 0 else "",
                        "score": card.locator(sel["review_score"]).first.get_attribute("score") if card.locator(sel["review_score"]).count() > 0 else "",
                        "date": card.locator(sel["review_date"]).first.text_content().strip() if card.locator(sel["review_date"]).count() > 0 else "",
                        "comment": card.locator(sel["review_comment"]).first.text_content().strip() if card.locator(sel["review_comment"]).count() > 0 else "",
                        "images": [img.get_attribute("src") for img in card.locator(sel["review_images"]).all()],
                    }
                    reviews.append(review)
                except Exception as e:
                    logger.warning(f"擷取單一評論失敗: {str(e)}")
            product["reviews"] = reviews

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
            products = scraper.search_products(args.keyword, args.page, auto_paging=True)
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
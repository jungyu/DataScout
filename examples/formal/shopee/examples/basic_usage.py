"""
Shopee 爬蟲基本使用範例

此範例展示如何使用 Shopee 爬蟲的基本功能：
1. 搜尋商品
2. 獲取商品詳情
3. 處理驗證碼
"""

import os
import sys
import logging
from datetime import datetime

# 添加父目錄到系統路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import BaseConfig
from crawler import ShopeeCrawler

def setup_logger():
    """設定日誌"""
    # 建立日誌目錄
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 設定日誌檔案
    log_file = os.path.join(log_dir, f"shopee_crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # 設定日誌格式
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("shopee_crawler")

def main():
    """主程式"""
    # 設定日誌
    logger = setup_logger()
    logger.info("開始執行 Shopee 爬蟲範例")
    
    try:
        # 建立配置
        config = BaseConfig()
        
        # 建立爬蟲
        crawler = ShopeeCrawler(config, logger)
        logger.info("成功建立爬蟲實例")
        
        # 搜尋商品
        keyword = "手機"
        logger.info(f"開始搜尋商品：{keyword}")
        products = crawler.search_products(keyword)
        logger.info(f"成功搜尋到 {len(products)} 個商品")
        
        # 顯示商品資訊
        for i, product in enumerate(products[:5], 1):
            logger.info(f"商品 {i}:")
            logger.info(f"  標題：{product['title']}")
            logger.info(f"  價格：{product['price']}")
            logger.info(f"  評分：{product['rating']}")
            logger.info(f"  銷量：{product['sales']}")
            logger.info(f"  連結：{product['url']}")
        
        # 獲取第一個商品的詳情
        if products:
            product_url = products[0]["url"]
            logger.info(f"開始獲取商品詳情：{product_url}")
            details = crawler.get_product_details(product_url)
            logger.info("成功獲取商品詳情")
            
            # 顯示商品詳情
            logger.info("商品詳情：")
            logger.info(f"  標題：{details['title']}")
            logger.info(f"  價格：{details['price']}")
            logger.info(f"  描述：{details['description'][:100]}...")
            logger.info(f"  圖片數量：{len(details['images'])}")
            logger.info(f"  規格：{details['specifications']}")
            logger.info(f"  評分：{details['rating']}")
            logger.info(f"  評論數量：{details['review_count']}")
            logger.info(f"  銷量：{details['sales']}")
            logger.info(f"  商店名稱：{details['shop_name']}")
            logger.info(f"  商店評分：{details['shop_rating']}")
            logger.info(f"  商店位置：{details['shop_location']}")
        
        logger.info("範例執行完成")
        
    except Exception as e:
        logger.error(f"執行範例時發生錯誤：{str(e)}")
        raise

if __name__ == "__main__":
    main() 
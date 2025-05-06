#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MomoShop 爬蟲主程式

此模組提供 MomoShop 爬蟲的主要入口點。
支援以下功能：
- 關鍵字搜尋（-method search -keyword "關鍵字"）
- 分類瀏覽（-method category -category_id "分類ID"）
- 商品詳情（-method product -product_id "商品ID"）
- 批量爬取（-method batch -file "輸入文件"）
"""

import argparse
import json
import os
import sys
import time
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 確保能找到相關模組
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent.parent.parent))  # 添加專案根目錄

from playwright_base import setup_logger
from examples.formal.momoshop.momoshop_scraper import MomoShopScraper
from examples.formal.momoshop.config import SITE_CONFIG, LOG_CONFIG, BROWSER_CONFIG

# 設置日誌
logger = setup_logger(
    name=__name__,
    level=LOG_CONFIG.get("level", "INFO"),
    log_file=LOG_CONFIG.get("file", None)
)

def setup_output_dirs() -> Dict[str, Path]:
    """
    設置輸出目錄
    
    Returns:
        Dict[str, Path]: 目錄路徑字典
    """
    # 定義目錄
    output_dirs = {
        "data": Path("data"),
        "raw": Path("data/raw"),
        "processed": Path("data/processed"),
        "logs": Path("logs"),
        "screenshots": Path("data/screenshots"),
    }
    
    # 創建目錄
    for dir_path in output_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
        
    return output_dirs

def save_results(data: Any, method: str, query: str, format: str = "json") -> Path:
    """
    保存爬取結果

    Args:
        data: 爬取的數據
        method: 爬取方法 (search/category/product)
        query: 查詢內容 (關鍵字/分類ID/商品ID)
        format: 輸出格式 (json/csv)

    Returns:
        Path: 保存的文件路徑
    """
    # 建立文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{method}_{query}_{timestamp}"

    # 修改輸出路徑到 examples/formal/momoshop/data/
    output_dir = Path(__file__).parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    if format.lower() == "json":
        file_path = output_dir / f"{filename}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    elif format.lower() == "csv":
        file_path = output_dir / f"{filename}.csv"
        if isinstance(data, list) and data:
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                fields = data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(data)
        else:
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                if isinstance(data, dict):
                    fields = data.keys()
                    writer = csv.DictWriter(f, fieldnames=fields)
                    writer.writeheader()
                    writer.writerow(data)
                else:
                    logger.warning(f"無法將數據類型 {type(data)} 保存為 CSV")
    else:
        logger.warning(f"不支持的格式: {format}")
        return None

    logger.info(f"結果已保存到 {file_path}")
    return file_path

def search_products(scraper: MomoShopScraper, keyword: str, page: int = 1, 
                   save_format: str = "json") -> None:
    """
    使用關鍵字搜尋商品
    
    Args:
        scraper: MomoShop 爬蟲實例
        keyword: 搜尋關鍵字
        page: 頁碼
        save_format: 保存格式
    """
    logger.info(f"開始搜尋商品: 關鍵字={keyword}, 頁碼={page}")
    
    try:
        # 執行爬蟲
        start_time = time.time()
        products = scraper.search_products(keyword, page)
        end_time = time.time()
        
        # 輸出結果
        logger.info(f"搜尋完成: 找到 {len(products)} 個商品, 耗時 {end_time - start_time:.2f} 秒")
        
        # 保存結果
        save_results(products, "search", keyword, save_format)
        
    except Exception as e:
        logger.error(f"搜尋商品時發生錯誤: {str(e)}")

def browse_category(scraper: MomoShopScraper, category_id: str, page: int = 1, 
                   save_format: str = "json") -> None:
    """
    瀏覽分類商品
    
    Args:
        scraper: MomoShop 爬蟲實例
        category_id: 分類 ID
        page: 頁碼
        save_format: 保存格式
    """
    logger.info(f"開始瀏覽分類: 分類ID={category_id}, 頁碼={page}")
    
    try:
        # 執行爬蟲
        start_time = time.time()
        products = scraper.get_category_products(category_id, page)
        end_time = time.time()
        
        # 輸出結果
        logger.info(f"瀏覽完成: 找到 {len(products)} 個商品, 耗時 {end_time - start_time:.2f} 秒")
        
        # 保存結果
        save_results(products, "category", category_id, save_format)
        
    except Exception as e:
        logger.error(f"瀏覽分類時發生錯誤: {str(e)}")

def get_product_detail(scraper: MomoShopScraper, product_id: str, 
                      save_format: str = "json") -> None:
    """
    獲取商品詳情
    
    Args:
        scraper: MomoShop 爬蟲實例
        product_id: 商品 ID
        save_format: 保存格式
    """
    logger.info(f"開始獲取商品詳情: 商品ID={product_id}")
    
    try:
        # 執行爬蟲
        start_time = time.time()
        product = scraper.get_product_detail(product_id)
        end_time = time.time()
        
        # 輸出結果
        logger.info(f"獲取商品詳情完成: {product.get('name', '')}, 耗時 {end_time - start_time:.2f} 秒")
        
        # 保存結果
        save_results(product, "product", product_id, save_format)
        
    except Exception as e:
        logger.error(f"獲取商品詳情時發生錯誤: {str(e)}")

def batch_process(scraper: MomoShopScraper, file_path: str, 
                 save_format: str = "json") -> None:
    """
    批量處理任務
    
    Args:
        scraper: MomoShop 爬蟲實例
        file_path: 輸入文件路徑
        save_format: 保存格式
    """
    logger.info(f"開始批量處理任務: 輸入文件={file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"輸入文件不存在: {file_path}")
        return
    
    try:
        # 解析輸入文件
        with open(file_path, "r", encoding="utf-8") as f:
            if file_path.endswith(".json"):
                tasks = json.load(f)
            elif file_path.endswith(".csv"):
                reader = csv.DictReader(f)
                tasks = list(reader)
            else:
                logger.error(f"不支持的文件格式: {file_path}")
                return
        
        logger.info(f"已讀取 {len(tasks)} 個任務")
        
        # 執行任務
        for i, task in enumerate(tasks):
            try:
                method = task.get("method")
                
                if method == "search":
                    keyword = task.get("keyword")
                    page = int(task.get("page", 1))
                    if keyword:
                        search_products(scraper, keyword, page, save_format)
                
                elif method == "category":
                    category_id = task.get("category_id")
                    page = int(task.get("page", 1))
                    if category_id:
                        browse_category(scraper, category_id, page, save_format)
                
                elif method == "product":
                    product_id = task.get("product_id")
                    if product_id:
                        get_product_detail(scraper, product_id, save_format)
                
                else:
                    logger.warning(f"不支持的方法: {method}")
                
                # 任務間添加隨機延時
                if i < len(tasks) - 1:
                    delay = SITE_CONFIG.get("request", {}).get("retry_delay", 1000) / 1000
                    logger.info(f"等待 {delay} 秒後繼續下一個任務")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"執行任務 {i+1} 時發生錯誤: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"批量處理任務時發生錯誤: {str(e)}")

def parse_args():
    """
    解析命令行參數
    
    Returns:
        argparse.Namespace: 命令行參數
    """
    parser = argparse.ArgumentParser(description="MomoShop 爬蟲")
    
    # 主要參數
    parser.add_argument("-method", type=str, required=True, 
                       choices=["search", "category", "product", "batch"],
                       help="爬蟲方法: search(搜尋), category(分類), product(商品詳情), batch(批量)")
    
    # 方法相關參數
    parser.add_argument("-keyword", type=str, help="搜尋關鍵字")
    parser.add_argument("-category_id", type=str, help="分類 ID")
    parser.add_argument("-product_id", type=str, help="商品 ID")
    parser.add_argument("-file", type=str, help="批量任務輸入文件")
    parser.add_argument("-page", type=int, default=1, help="頁碼")
    
    # 輸出格式
    parser.add_argument("-format", type=str, default="json", choices=["json", "csv"],
                       help="輸出格式: json 或 csv")
    
    # 浏覽器設置
    parser.add_argument("-headless", action="store_true", help="是否使用無頭模式")
    parser.add_argument("-proxy", type=str, help="代理伺服器")
    
    # 其他設置
    parser.add_argument("-debug", action="store_true", help="啟用調試模式")
    
    return parser.parse_args()

def main():
    """
    主函數
    """
    # 解析命令行參數
    args = parse_args()
    
    # 設置目錄
    dirs = setup_output_dirs()
    
    # 調整日誌級別
    if args.debug:
        logger.setLevel("DEBUG")
        logger.debug("已啟用調試模式")
    
    # 更新瀏覽器配置
    browser_config = BROWSER_CONFIG.copy()
    if args.headless is not None:
        browser_config["headless"] = args.headless
    if args.proxy:
        browser_config["proxy"] = {"server": args.proxy}
    
    # 初始化爬蟲
    scraper = None
    
    try:
        logger.info("初始化 MomoShop 爬蟲...")
        scraper = MomoShopScraper()
        
        # 根據方法執行不同操作
        if args.method == "search":
            if not args.keyword:
                logger.error("搜尋方法需要提供關鍵字")
                return
            search_products(scraper, args.keyword, args.page, args.format)
            
        elif args.method == "category":
            if not args.category_id:
                logger.error("分類方法需要提供分類 ID")
                return
            browse_category(scraper, args.category_id, args.page, args.format)
            
        elif args.method == "product":
            if not args.product_id:
                logger.error("商品詳情方法需要提供商品 ID")
                return
            get_product_detail(scraper, args.product_id, args.format)
            
        elif args.method == "batch":
            if not args.file:
                logger.error("批量方法需要提供輸入文件")
                return
            batch_process(scraper, args.file, args.format)
            
    except KeyboardInterrupt:
        logger.info("操作已由用戶中斷")
    except Exception as e:
        logger.error(f"執行爬蟲時發生錯誤: {str(e)}")
    finally:
        # 關閉爬蟲
        if scraper:
            logger.info("關閉 MomoShop 爬蟲...")
            scraper.close()
        
        logger.info("程式執行完畢")

if __name__ == "__main__":
    main()
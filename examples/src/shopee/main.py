#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
蝦皮爬蟲執行檔

提供蝦皮爬蟲的命令行介面，支援：
- 關鍵字搜尋
- 產品詳情爬取
- 批量爬取
- 結果保存
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any
from datetime import datetime

from .crawler import ShopeeCrawler

def parse_args():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description="蝦皮爬蟲")
    
    # 基本參數
    parser.add_argument(
        "--config",
        type=str,
        default="examples/config/shopee/formal/search.json",
        help="配置文件路徑"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="./examples/data",
        help="數據保存目錄"
    )
    
    # 搜尋參數
    parser.add_argument(
        "--keyword",
        type=str,
        help="搜尋關鍵字"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=1,
        help="最大爬取頁數"
    )
    
    # 產品詳情參數
    parser.add_argument(
        "--product-ids",
        type=str,
        help="產品ID列表，用逗號分隔"
    )
    
    # 輸出參數
    parser.add_argument(
        "--output",
        type=str,
        help="輸出文件路徑"
    )
    
    return parser.parse_args()

def save_results(results: List[Dict[str, Any]], output_path: str):
    """保存爬取結果"""
    try:
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 生成文件名
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"examples/data/shopee_products_{timestamp}.json"
            
        # 保存為JSON文件
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"結果已保存到: {output_path}")
        print(f"共爬取 {len(results)} 個商品")
        
    except Exception as e:
        print(f"保存結果失敗: {str(e)}")

def main():
    """主函數"""
    try:
        # 解析命令行參數
        args = parse_args()
        
        # 初始化爬蟲
        crawler = ShopeeCrawler(args.config, args.data_dir)
        
        results = []
        
        # 搜尋商品
        if args.keyword:
            print(f"開始搜尋關鍵字: {args.keyword}")
            for product in crawler.search_products(args.keyword, args.max_pages):
                results.append(product)
                print(f"商品: {product['title']}")
                
                # 獲取產品詳情
                details = crawler.get_product_details(product['id'])
                results[-1].update(details)
                print(f"詳情: {details}")
                
        # 爬取指定產品
        elif args.product_ids:
            product_ids = args.product_ids.split(",")
            print(f"開始爬取產品: {product_ids}")
            for product_id in product_ids:
                details = crawler.get_product_details(product_id)
                results.append(details)
                print(f"產品: {details['title']}")
                
        # 保存結果
        save_results(results, args.output)
        
    except Exception as e:
        print(f"執行失敗: {str(e)}")
        sys.exit(1)
        
    finally:
        # 清理資源
        if 'crawler' in locals():
            crawler.cleanup()

if __name__ == "__main__":
    main() 
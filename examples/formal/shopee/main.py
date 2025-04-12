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
import traceback
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
import logging

# 添加項目根目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(project_root)

try:
    from src.captcha.types import CaptchaConfig, CaptchaType
    from examples.formal.shopee.crawler import ShopeeCrawler
except ImportError as e:
    print(f"匯入模組失敗: {e}")
    sys.exit(1)

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
    
    # 瀏覽器參數
    parser.add_argument(
        "--headless",
        action="store_true",
        help="無頭模式"
    )
    
    # 偵錯參數
    parser.add_argument(
        "--debug",
        action="store_true",
        help="偵錯模式"
    )
    
    return parser.parse_args()

def save_results(results: List[Dict[str, Any]], output_path: str = None):
    """保存爬取結果"""
    try:
        # 生成文件名
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"examples/data/shopee_products_{timestamp}.json"
        
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
        # 保存為JSON文件
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"結果已保存到: {output_path}")
        print(f"共爬取 {len(results)} 個商品")
        
    except Exception as e:
        print(f"保存結果失敗: {str(e)}")

def load_config(config_path: str) -> Dict:
    """載入配置文件"""
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"配置已從 {config_path} 載入")
            return config
        else:
            print(f"配置文件 {config_path} 不存在，使用預設配置")
            return {}
    except Exception as e:
        print(f"載入配置失敗: {str(e)}，使用預設配置")
        return {}

def main():
    # 解析命令行參數
    args = parse_args()
    
    # 設置日誌級別
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # 從配置文件路徑中獲取目錄和文件名
        config_dir = str(Path(args.config).parent)
        config_name = "search.json"  # 直接使用 search.json
        
        # 初始化爬蟲
        crawler = ShopeeCrawler(
            config_dir=config_dir,
            config_name=config_name
        )
        
        # 設置關鍵字
        keyword = args.keyword or "手機"
        
        # 搜索商品
        results = crawler.search_products(keyword, args.max_pages)
        
        # 保存結果
        if results:
            save_results(results, args.output)
            logger.info(f"已成功保存 {len(results)} 個商品資訊")
        
    except Exception as e:
        logger.error(f"執行過程中發生錯誤: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()
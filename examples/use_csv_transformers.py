#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CSV 轉換器使用範例
"""

import os
import asyncio
import argparse
from pathlib import Path
import logging

from adapter.transformers import (
    ChartJSTransformer,
    EnhancedChartJSTransformer,
    StockDataTransformer
)

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 資料目錄
DATA_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data')))
CSV_DIR = DATA_DIR / "csv"
JSON_DIR = DATA_DIR / "json"

async def main():
    parser = argparse.ArgumentParser(description='CSV 轉換器使用範例')
    parser.add_argument('--converter', choices=['basic', 'enhanced', 'stock'], default='enhanced', 
                      help='選擇轉換器類型: basic, enhanced, stock')
    parser.add_argument('--input-dir', default=str(CSV_DIR), help='CSV 檔案目錄')
    parser.add_argument('--output-dir', default=str(JSON_DIR), help='輸出 JSON 檔案目錄')
    parser.add_argument('--limit', type=int, help='限制處理檔案數量')
    parser.add_argument('--pattern', help='檔案名稱匹配模式')
    
    args = parser.parse_args()
    
    # 確保目錄存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 設定轉換器配置
    config = {
        'input_dir': args.input_dir,
        'output_dir': args.output_dir,
        'limit': args.limit,
        'pattern': args.pattern
    }
    
    # 選擇並初始化轉換器
    if args.converter == 'basic':
        logger.info("使用標準 Chart.js 轉換器")
        transformer = ChartJSTransformer(config)
    elif args.converter == 'stock':
        logger.info("使用股票數據轉換器")
        transformer = StockDataTransformer(config)
    else:  # enhanced
        logger.info("使用增強版 Chart.js 轉換器")
        transformer = EnhancedChartJSTransformer(config)
    
    # 執行轉換
    results = await transformer.transform()
    
    # 輸出結果
    logger.info(f"轉換完成: 成功 {results['successful']}/{results['total']} 個檔案")
    
if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主程序模組

此模組提供爬蟲程序的主入口，包括：
1. 命令行參數解析
2. 配置文件加載
3. 爬蟲任務執行
4. 結果保存
"""

import os
import json
import logging
import argparse
from datetime import datetime
from src.config.paths import OUTPUT_DIR, DEBUG_DIR, SCREENSHOTS_DIR

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description="爬蟲程序")
    parser.add_argument("-c", "--config", required=True, help="配置文件路徑")
    parser.add_argument("-o", "--output", help="輸出文件路徑")
    parser.add_argument("-v", "--verbose", action="store_true", help="顯示詳細日誌")
    parser.add_argument("-d", "--debug", action="store_true", help="啟用調試模式")
    return parser.parse_args()

def load_config(config_path):
    """加載配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 設置調試模式
        if args.debug:
            config["debug"] = config.get("debug", {})
            config["debug"]["screenshot"] = True
            config["debug"]["save_page_source"] = True
            config["debug"]["error_page_dir"] = DEBUG_DIR
        
        # 設置截圖目錄
        if "screenshot" in config:
            config["screenshot"]["directory"] = SCREENSHOTS_DIR
        
        return config
    except Exception as e:
        logger.error(f"加載配置文件失敗: {str(e)}")
        raise

def save_results(data, output_path=None):
    """保存結果"""
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(OUTPUT_DIR, f"results_{timestamp}.json")
    
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"數據已保存到: {output_path}")
    return output_path

def main():
    """主函數"""
    global args
    args = parse_args()
    
    # 設置日誌級別
    log_level = logging.DEBUG if args.debug or args.verbose else logging.INFO
    logger.setLevel(log_level)
    
    try:
        # 加載配置
        config = load_config(args.config)
        
        # 執行爬蟲任務
        # TODO: 實現爬蟲邏輯
        
        # 保存結果
        if args.output:
            save_results({}, args.output)
        
    except Exception as e:
        logger.error(f"程序執行失敗: {str(e)}")
        raise

if __name__ == "__main__":
    main()
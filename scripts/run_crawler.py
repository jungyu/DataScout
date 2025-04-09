#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬蟲運行腳本

此模組提供爬蟲程序的運行入口，包括：
1. 命令行參數解析
2. 配置文件加載
3. 爬蟲任務執行
4. 結果保存
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.config.paths import OUTPUT_DIR, DEBUG_DIR, SCREENSHOTS_DIR
from src.core.crawler_engine import CrawlerEngine
from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader
from src.anti_detection.stealth_manager import StealthManager
from src.captcha.captcha_manager import CaptchaManager

def parse_args():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description="爬蟲程序")
    parser.add_argument("-c", "--config", required=True, help="配置文件路徑")
    parser.add_argument("-t", "--template", required=True, help="爬蟲模板文件路徑")
    parser.add_argument("-o", "--output", help="輸出文件路徑")
    parser.add_argument("-v", "--verbose", action="store_true", help="顯示詳細日誌")
    parser.add_argument("-d", "--debug", action="store_true", help="啟用調試模式")
    parser.add_argument("--headless", action="store_true", help="使用無頭模式")
    parser.add_argument("--screenshot", action="store_true", help="保存截圖")
    return parser.parse_args()

def setup_environment(args):
    """設置運行環境"""
    # 設置日誌
    log_level = logging.DEBUG if args.debug or args.verbose else logging.INFO
    logger = setup_logger("crawler", log_level)
    
    # 加載配置
    config = ConfigLoader(args.config).load()
    
    # 更新配置
    if args.headless:
        config["webdriver"]["headless"] = True
    if args.screenshot:
        config["debug"] = config.get("debug", {})
        config["debug"]["screenshot"] = True
        config["debug"]["directory"] = SCREENSHOTS_DIR
    
    return logger, config

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
    
    return output_path

def main():
    """主函數"""
    # 解析參數
    args = parse_args()
    
    try:
        # 設置環境
        logger, config = setup_environment(args)
        logger.info("開始執行爬蟲任務")
        
        # 初始化組件
        stealth_manager = StealthManager(config.get("anti_detection", {}))
        captcha_manager = CaptchaManager(config.get("captcha", {}))
        
        # 創建爬蟲引擎
        engine = CrawlerEngine(
            config=config,
            template_file=args.template,
            stealth_manager=stealth_manager,
            captcha_manager=captcha_manager
        )
        
        # 執行爬蟲
        results = engine.run()
        
        # 保存結果
        if results:
            output_path = save_results(results, args.output)
            logger.info(f"數據已保存到: {output_path}")
        else:
            logger.warning("未獲取到任何數據")
        
    except Exception as e:
        logger.error(f"程序執行失敗: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

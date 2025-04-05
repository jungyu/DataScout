"""
Selenium模板化爬蟲框架 (Selenium Template Crawler Framework)
Copyright (c) 2024 Aaron-Yu
Author: Aaron-Yu <jungyuyu@gmail.com>, Claude AI
License: MIT License
版本: 1.0.0
"""

import os
import argparse
import json
from datetime import datetime
import logging

# 核心模組
from src.core.crawler_engine import CrawlerEngine
from src.core._template_crawler import TemplateCrawler
from src.utils.logger import LoggerManager
from src.utils.config_loader import ConfigLoader
from src.captcha.captcha_manager import CaptchaManager


def main():
    """
    爬蟲程式主入口點，解析命令行參數並執行爬蟲任務
    """
    # 解析命令行參數
    parser = argparse.ArgumentParser(description="模板化網站爬蟲工具")
    parser.add_argument("-t", "--template", required=True, help="爬蟲模板文件路徑")
    parser.add_argument("-c", "--config", default="config/config.json", help="配置文件路徑")
    parser.add_argument("-p", "--pages", type=int, help="最大爬取頁數")
    parser.add_argument("-i", "--items", type=int, help="最大爬取項目數")
    parser.add_argument("-r", "--resume", action="store_true", help="從中斷點恢復爬取")
    parser.add_argument("-o", "--output", help="輸出文件路徑")
    parser.add_argument("-v", "--verbose", action="store_true", help="顯示詳細日誌")
    parser.add_argument("-d", "--debug", action="store_true", help="啟用調試模式")
    parser.add_argument("--headless", type=str, choices=["true", "false"], help="是否使用無頭模式")
    parser.add_argument("--screenshot", action="store_true", help="是否保存截圖")
    args = parser.parse_args()
    
    # 初始化日誌管理器
    log_level = logging.DEBUG if args.debug or args.verbose else logging.INFO
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logger_manager = LoggerManager(name="crawler", level=log_level, log_file=log_file)
    logger = logger_manager.get_logger()
    
    logger.info(f"開始執行爬蟲 - 模板: {args.template}")
    
    try:
        # 載入配置
        config = ConfigLoader(args.config).load()
        
        # 處理命令行參數覆蓋配置
        if args.headless:
            config["webdriver"]["headless"] = args.headless.lower() == "true"
        if args.screenshot:
            config["debug"] = config.get("debug", {})
            config["debug"]["screenshot"] = True
        
        # 決定是否從中斷點恢復
        if args.resume:
            logger.info(f"從中斷點恢復爬取: {args.template}")
            crawler = TemplateCrawler(
                template_file=args.template,
                config_file=args.config,
                log_level=log_level
            )
            data = crawler.resume_crawl(
                max_pages=args.pages,
                max_items=args.items
            )
        else:
            logger.info(f"開始爬取: {args.template}")
            crawler = TemplateCrawler(
                template_file=args.template,
                config_file=args.config,
                log_level=log_level
            )
            data = crawler.crawl(
                max_pages=args.pages,
                max_items=args.items
            )
        
        # 處理爬取結果
        if data:
            logger.info(f"爬取完成，共獲取 {len(data)} 筆資料")
            
            # 保存到指定輸出文件
            if args.output:
                output_dir = os.path.dirname(args.output)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                    
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"數據已保存到: {args.output}")
            
            # 使用內建的數據持久化
            crawler.data_manager.save_data(data, crawler.template.get("site_name", "unnamed_site"))
            logger.info("數據已通過配置的持久化方式保存")
        else:
            logger.warning("未獲取到任何數據")
    
    except FileNotFoundError as e:
        logger.error(f"找不到文件: {e}")
        return 1
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析錯誤: {e}")
        return 1
    except Exception as e:
        logger.error(f"爬蟲執行錯誤: {str(e)}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
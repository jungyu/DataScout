"""
模板化爬蟲範例
展示如何使用框架的模板化功能進行網站爬取
"""

import os
import sys
import json
from pathlib import Path

# 添加專案根目錄到路徑，以便導入模組
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.template_crawler import TemplateCrawler
from src.utils.logger import LoggerManager
import logging

def basic_template_usage():
    """
    展示如何使用基本模板進行爬蟲
    """
    # 設置日誌
    logger_manager = LoggerManager(name="example", level=logging.INFO)
    logger = logger_manager.get_logger()
    
    logger.info("開始執行模板化爬蟲示例")
    
    # 模板和配置文件路徑
    template_file = os.path.join(project_root, "examples/basic_template.json")
    config_file = os.path.join(project_root, "config/config.json")
    
    # 如果配置文件不存在，則創建一個基本配置
    if not os.path.exists(config_file):
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        basic_config = {
            "webdriver": {
                "browser": "chrome",
                "headless": False,
                "user_agent": "Mozilla/5.0",
                "timeout": 30
            },
            "proxy": {
                "enabled": False
            },
            "storage": {
                "type": "json",
                "path": "output"
            },
            "debug": {
                "screenshot": True,
                "screenshot_path": "screenshots"
            }
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(basic_config, f, indent=2)
        logger.info(f"創建了基本配置文件: {config_file}")
    
    try:
        # 初始化模板爬蟲
        logger.info(f"初始化模板爬蟲，使用模板: {template_file}")
        crawler = TemplateCrawler(
            template_file=template_file,
            config_file=config_file,
            log_level=logging.INFO
        )
        
        # 開始爬取 (限制爬取頁數和項目數)
        logger.info("開始爬取...")
        data = crawler.crawl(max_pages=2, max_items=10)
        
        # 處理結果
        if data:
            logger.info(f"爬取完成，共獲取 {len(data)} 筆資料")
            
            # 保存結果
            os.makedirs("output", exist_ok=True)
            output_file = "output/template_crawler_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"數據已保存到: {output_file}")
        else:
            logger.warning("未獲取到任何數據")
            
    except FileNotFoundError as e:
        logger.error(f"找不到文件: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析錯誤: {e}")
    except Exception as e:
        logger.error(f"爬蟲執行錯誤: {str(e)}", exc_info=True)
    
    logger.info("模板化爬蟲示例執行完成")

if __name__ == "__main__":
    basic_template_usage()

"""
蝦皮爬蟲示例程序

展示如何使用蝦皮分頁處理器來爬取蝦皮商品數據。
"""

import os
import sys
import json
from typing import Dict, Any, List
from datetime import datetime

# 添加項目根目錄到Python路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from src.core.webdriver_manager import WebDriverManager
from src.extractors.handlers.shopee_pagination_handler import ShopeePaginationHandler
from src.core.exceptions import handle_exception

class ShopeeCrawler:
    """蝦皮爬蟲類"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化蝦皮爬蟲
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.driver_manager = WebDriverManager(config.get("webdriver", {}))
        self.pagination_handler = None
        self.output_dir = config.get("output_dir", "output/shopee")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def start(self, search_url: str) -> List[Dict[str, Any]]:
        """
        開始爬取蝦皮商品
        
        Args:
            search_url: 搜索頁面URL
            
        Returns:
            爬取的商品數據列表
        """
        try:
            # 獲取WebDriver實例
            driver = self.driver_manager.get_driver()
            
            # 創建分頁處理器
            handler_config = {
                "name": "shopee_crawler",
                "version": "1.0.0",
                "enabled": True,
                "timeout": 30,
                "retry_count": 3,
                "validate_data": True,
                "output_dir": self.output_dir,
                "log_level": "INFO",
                "log_file": os.path.join(self.output_dir, "crawler.log"),
                "pagination_type": "button_click",
                "page_load_delay": 3,
                "between_pages_delay": 2.0,
                "max_pages": self.config.get("max_pages", 10),
                "use_ajax_detection": True
            }
            
            self.pagination_handler = ShopeePaginationHandler(handler_config, driver)
            
            # 開始爬取
            items = self.pagination_handler.extract(search_url)
            
            # 保存結果
            self._save_results(items)
            
            return items
            
        except Exception as e:
            handle_exception(e, "爬取蝦皮商品失敗")
            return []
        
        finally:
            # 清理資源
            if self.pagination_handler:
                self.pagination_handler.cleanup()
            if self.driver_manager:
                self.driver_manager.cleanup()
    
    def _save_results(self, items: List[Dict[str, Any]]):
        """
        保存爬取結果
        
        Args:
            items: 商品數據列表
        """
        try:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, f"shopee_products_{timestamp}.json")
            
            # 保存為JSON文件
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            
            print(f"結果已保存到: {filename}")
            print(f"共爬取 {len(items)} 個商品")
            
        except Exception as e:
            handle_exception(e, "保存爬取結果失敗")

def main():
    """主函數"""
    # 配置
    config = {
        "webdriver": {
            "browser_type": "chrome",
            "headless": True,
            "timeout": 30,
            "retry_count": 3
        },
        "output_dir": "output/shopee",
        "max_pages": 10
    }
    
    # 創建爬蟲實例
    crawler = ShopeeCrawler(config)
    
    # 開始爬取
    search_url = "https://shopee.tw/search?keyword=手機"
    items = crawler.start(search_url)
    
    # 輸出統計信息
    print(f"爬取完成，共獲取 {len(items)} 個商品")

if __name__ == "__main__":
    main() 
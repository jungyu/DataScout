"""
Shopee 爬蟲進階使用範例

此範例展示如何使用 Shopee 爬蟲的進階功能：
1. 自定義瀏覽器指紋
2. 自定義請求控制
3. 批次處理商品
4. 錯誤處理和重試
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any

# 添加父目錄到系統路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import BaseConfig
from crawler import ShopeeCrawler
from core.browser_fingerprint import BrowserFingerprint
from core.request_controller import RequestController

def setup_logger():
    """設定日誌"""
    # 建立日誌目錄
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 設定日誌檔案
    log_file = os.path.join(log_dir, f"shopee_crawler_advanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # 設定日誌格式
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("shopee_crawler_advanced")

def save_results(data: List[Dict[str, Any]], filename: str):
    """儲存結果到 JSON 檔案"""
    # 建立結果目錄
    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # 儲存結果
    filepath = os.path.join(results_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def batch_process_products(crawler: ShopeeCrawler, products: List[Dict[str, Any]], batch_size: int = 5) -> List[Dict[str, Any]]:
    """批次處理商品"""
    results = []
    
    for i in range(0, len(products), batch_size):
        batch = products[i:i + batch_size]
        for product in batch:
            try:
                # 獲取商品詳情
                details = crawler.get_product_details(product["url"])
                results.append(details)
                
                # 等待一段時間，避免請求過於頻繁
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"處理商品時發生錯誤：{str(e)}")
                continue
    
    return results

def main():
    """主程式"""
    # 設定日誌
    logger = setup_logger()
    logger.info("開始執行 Shopee 爬蟲進階範例")
    
    try:
        # 建立配置
        config = BaseConfig()
        
        # 自定義瀏覽器指紋
        browser_fingerprint = BrowserFingerprint(config)
        browser_fingerprint.webgl_params = {
            "vendor": "Google Inc.",
            "renderer": "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)",
            "webgl_version": "WebGL 1.0",
            "shading_language_version": "WebGL GLSL ES 1.0"
        }
        browser_fingerprint.canvas_noise = {
            "noise_level": 0.1,
            "pattern": "random"
        }
        browser_fingerprint.audio_params = {
            "sample_rate": 44100,
            "channel_count": 2,
            "buffer_size": 4096
        }
        browser_fingerprint.font_list = [
            "Arial",
            "Helvetica",
            "Times New Roman",
            "Times",
            "Courier New",
            "Courier",
            "Verdana",
            "Georgia",
            "Palatino",
            "Garamond",
            "Bookman",
            "Comic Sans MS",
            "Trebuchet MS",
            "Arial Black"
        ]
        browser_fingerprint.webrtc_config = {
            "mode": "disable-non-proxied-udp",
            "proxy_only": True,
            "proxy_server": "socks5://127.0.0.1:1080"
        }
        browser_fingerprint.hardware_config = {
            "concurrency": 4,
            "device_memory": 8,
            "platform": "Win32"
        }
        browser_fingerprint.timezone = "Asia/Taipei"
        browser_fingerprint.language = "zh-TW"
        
        # 自定義請求控制
        request_controller = RequestController(config)
        request_controller.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]
        request_controller.referers = [
            "https://www.google.com/",
            "https://www.google.com.tw/",
            "https://www.bing.com/",
            "https://www.yahoo.com/"
        ]
        
        # 建立爬蟲
        crawler = ShopeeCrawler(config, logger)
        crawler.browser_fingerprint = browser_fingerprint
        crawler.request_controller = request_controller
        logger.info("成功建立爬蟲實例")
        
        # 搜尋商品
        keywords = ["手機", "筆電", "耳機"]
        all_products = []
        
        for keyword in keywords:
            logger.info(f"開始搜尋商品：{keyword}")
            products = crawler.search_products(keyword)
            logger.info(f"成功搜尋到 {len(products)} 個商品")
            all_products.extend(products)
            
            # 等待一段時間，避免請求過於頻繁
            time.sleep(5)
        
        # 儲存搜尋結果
        save_results(all_products, "search_results.json")
        logger.info("成功儲存搜尋結果")
        
        # 批次處理商品
        logger.info("開始批次處理商品")
        product_details = batch_process_products(crawler, all_products)
        logger.info(f"成功處理 {len(product_details)} 個商品")
        
        # 儲存商品詳情
        save_results(product_details, "product_details.json")
        logger.info("成功儲存商品詳情")
        
        logger.info("範例執行完成")
        
    except Exception as e:
        logger.error(f"執行範例時發生錯誤：{str(e)}")
        raise

if __name__ == "__main__":
    main() 
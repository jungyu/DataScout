"""
Shopee 爬蟲代理伺服器使用範例

此範例展示如何使用代理伺服器：
1. 設定代理伺服器
2. 輪換代理伺服器
3. 代理伺服器健康檢查
4. 錯誤處理和重試
"""

import os
import sys
import json
import logging
import time
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

# 添加父目錄到系統路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import BaseConfig
from crawler import ShopeeCrawler
from core.browser_fingerprint import BrowserFingerprint
from core.request_controller import RequestController

class ProxyManager:
    """代理伺服器管理器"""
    
    def __init__(self, proxies: List[Dict[str, str]]):
        """
        初始化代理伺服器管理器
        
        Args:
            proxies: 代理伺服器列表，格式為 [{"http": "http://host:port", "https": "http://host:port"}, ...]
        """
        self.proxies = proxies
        self.current_index = 0
        self.health_status = {proxy["http"]: True for proxy in proxies}
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """
        獲取下一個可用的代理伺服器
        
        Returns:
            代理伺服器設定，如果沒有可用的代理伺服器則返回 None
        """
        # 檢查是否有可用的代理伺服器
        if not any(self.health_status.values()):
            return None
        
        # 尋找下一個可用的代理伺服器
        for _ in range(len(self.proxies)):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            if self.health_status[proxy["http"]]:
                return proxy
        
        return None
    
    def mark_proxy_failed(self, proxy: Dict[str, str]):
        """
        標記代理伺服器為不可用
        
        Args:
            proxy: 代理伺服器設定
        """
        self.health_status[proxy["http"]] = False
    
    def mark_proxy_success(self, proxy: Dict[str, str]):
        """
        標記代理伺服器為可用
        
        Args:
            proxy: 代理伺服器設定
        """
        self.health_status[proxy["http"]] = True
    
    def reset_health_status(self):
        """重置所有代理伺服器的健康狀態"""
        for proxy in self.proxies:
            self.health_status[proxy["http"]] = True

def setup_logger():
    """設定日誌"""
    # 建立日誌目錄
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 設定日誌檔案
    log_file = os.path.join(log_dir, f"shopee_crawler_proxy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # 設定日誌格式
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("shopee_crawler_proxy")

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

def batch_process_products_with_proxy(
    crawler: ShopeeCrawler,
    proxy_manager: ProxyManager,
    products: List[Dict[str, Any]],
    batch_size: int = 5,
    max_retries: int = 3
) -> List[Dict[str, Any]]:
    """
    使用代理伺服器批次處理商品
    
    Args:
        crawler: 爬蟲實例
        proxy_manager: 代理伺服器管理器
        products: 商品列表
        batch_size: 批次大小
        max_retries: 最大重試次數
    
    Returns:
        處理結果列表
    """
    results = []
    
    for i in range(0, len(products), batch_size):
        batch = products[i:i + batch_size]
        for product in batch:
            retries = 0
            success = False
            
            while retries < max_retries and not success:
                # 獲取下一個代理伺服器
                proxy = proxy_manager.get_next_proxy()
                if not proxy:
                    logging.error("沒有可用的代理伺服器")
                    break
                
                try:
                    # 設定代理伺服器
                    crawler.browser_profile.proxy = proxy
                    
                    # 獲取商品詳情
                    details = crawler.get_product_details(product["url"])
                    results.append(details)
                    
                    # 標記代理伺服器為可用
                    proxy_manager.mark_proxy_success(proxy)
                    success = True
                    
                    # 等待一段時間，避免請求過於頻繁
                    time.sleep(random.uniform(2, 5))
                    
                except Exception as e:
                    logging.error(f"處理商品時發生錯誤：{str(e)}")
                    # 標記代理伺服器為不可用
                    proxy_manager.mark_proxy_failed(proxy)
                    retries += 1
                    # 等待一段時間後重試
                    time.sleep(random.uniform(5, 10))
            
            if not success:
                logging.error(f"處理商品失敗：{product['url']}")
    
    return results

def main():
    """主程式"""
    # 設定日誌
    logger = setup_logger()
    logger.info("開始執行 Shopee 爬蟲代理伺服器範例")
    
    try:
        # 建立配置
        config = BaseConfig()
        
        # 建立代理伺服器管理器
        proxies = [
            {"http": "http://proxy1.example.com:8080", "https": "http://proxy1.example.com:8080"},
            {"http": "http://proxy2.example.com:8080", "https": "http://proxy2.example.com:8080"},
            {"http": "http://proxy3.example.com:8080", "https": "http://proxy3.example.com:8080"}
        ]
        proxy_manager = ProxyManager(proxies)
        
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
            # 獲取下一個代理伺服器
            proxy = proxy_manager.get_next_proxy()
            if not proxy:
                logger.error("沒有可用的代理伺服器")
                break
            
            try:
                # 設定代理伺服器
                crawler.browser_profile.proxy = proxy
                
                logger.info(f"開始搜尋商品：{keyword}")
                products = crawler.search_products(keyword)
                logger.info(f"成功搜尋到 {len(products)} 個商品")
                all_products.extend(products)
                
                # 標記代理伺服器為可用
                proxy_manager.mark_proxy_success(proxy)
                
                # 等待一段時間，避免請求過於頻繁
                time.sleep(random.uniform(5, 10))
                
            except Exception as e:
                logger.error(f"搜尋商品時發生錯誤：{str(e)}")
                # 標記代理伺服器為不可用
                proxy_manager.mark_proxy_failed(proxy)
                # 等待一段時間後重試
                time.sleep(random.uniform(10, 20))
        
        # 儲存搜尋結果
        save_results(all_products, "search_results.json")
        logger.info("成功儲存搜尋結果")
        
        # 批次處理商品
        logger.info("開始批次處理商品")
        product_details = batch_process_products_with_proxy(crawler, proxy_manager, all_products)
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
"""
Shopee 分散式爬蟲範例

此範例展示如何使用多個爬蟲實例同時處理不同的任務：
1. 任務分配
2. 結果合併
3. 進度追蹤
4. 錯誤處理
"""

import os
import sys
import json
import time
import random
import logging
import threading
import queue
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加父目錄到系統路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import BaseConfig
from crawler import ShopeeCrawler
from core.browser_fingerprint import BrowserFingerprint
from core.request_controller import RequestController

class Task:
    """爬蟲任務"""
    
    def __init__(self, task_id: str, task_type: str, data: Dict[str, Any]):
        """
        初始化任務
        
        Args:
            task_id: 任務 ID
            task_type: 任務類型（search 或 detail）
            data: 任務數據
        """
        self.task_id = task_id
        self.task_type = task_type
        self.data = data
        self.status = "pending"
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None

class TaskManager:
    """任務管理器"""
    
    def __init__(self, max_workers: int = 3):
        """
        初始化任務管理器
        
        Args:
            max_workers: 最大工作執行緒數
        """
        self.task_queue = queue.Queue()
        self.tasks = {}
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []
        self.lock = threading.Lock()
    
    def add_task(self, task: Task):
        """
        添加任務到佇列
        
        Args:
            task: 爬蟲任務
        """
        self.tasks[task.task_id] = task
        self.task_queue.put(task)
    
    def get_task(self) -> Optional[Task]:
        """
        從佇列獲取任務
        
        Returns:
            爬蟲任務，如果佇列為空則返回 None
        """
        try:
            return self.task_queue.get_nowait()
        except queue.Empty:
            return None
    
    def update_task_status(self, task_id: str, status: str, result: Any = None, error: str = None):
        """
        更新任務狀態
        
        Args:
            task_id: 任務 ID
            status: 任務狀態
            result: 任務結果
            error: 錯誤訊息
        """
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = status
                task.result = result
                task.error = error
                if status == "running":
                    task.start_time = datetime.now()
                elif status in ["completed", "failed"]:
                    task.end_time = datetime.now()
    
    def get_task_progress(self) -> Dict[str, int]:
        """
        獲取任務進度
        
        Returns:
            任務進度統計
        """
        with self.lock:
            total = len(self.tasks)
            completed = sum(1 for task in self.tasks.values() if task.status == "completed")
            failed = sum(1 for task in self.tasks.values() if task.status == "failed")
            running = sum(1 for task in self.tasks.values() if task.status == "running")
            pending = sum(1 for task in self.tasks.values() if task.status == "pending")
            
            return {
                "total": total,
                "completed": completed,
                "failed": failed,
                "running": running,
                "pending": pending
            }
    
    def get_task_results(self) -> List[Dict[str, Any]]:
        """
        獲取所有完成的任務結果
        
        Returns:
            任務結果列表
        """
        with self.lock:
            return [
                {
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "status": task.status,
                    "result": task.result,
                    "error": task.error,
                    "start_time": task.start_time.isoformat() if task.start_time else None,
                    "end_time": task.end_time.isoformat() if task.end_time else None
                }
                for task in self.tasks.values()
                if task.status == "completed"
            ]
    
    def shutdown(self):
        """關閉任務管理器"""
        self.executor.shutdown(wait=True)

def setup_logger():
    """設定日誌"""
    # 建立日誌目錄
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 設定日誌檔案
    log_file = os.path.join(log_dir, f"shopee_crawler_distributed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # 設定日誌格式
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("shopee_crawler_distributed")

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

def create_crawler(config: BaseConfig, logger: logging.Logger) -> ShopeeCrawler:
    """
    建立爬蟲實例
    
    Args:
        config: 配置物件
        logger: 日誌物件
    
    Returns:
        爬蟲實例
    """
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
    
    return crawler

def process_task(task: Task, config: BaseConfig, logger: logging.Logger) -> Any:
    """
    處理爬蟲任務
    
    Args:
        task: 爬蟲任務
        config: 配置物件
        logger: 日誌物件
    
    Returns:
        任務結果
    """
    try:
        # 建立爬蟲
        crawler = create_crawler(config, logger)
        
        # 根據任務類型執行不同的操作
        if task.task_type == "search":
            result = crawler.search_products(task.data["keyword"])
        elif task.task_type == "detail":
            result = crawler.get_product_details(task.data["url"])
        else:
            raise ValueError(f"不支援的任務類型：{task.task_type}")
        
        return result
        
    except Exception as e:
        logger.error(f"處理任務時發生錯誤：{str(e)}")
        raise

def worker(task_manager: TaskManager, config: BaseConfig, logger: logging.Logger):
    """
    工作執行緒
    
    Args:
        task_manager: 任務管理器
        config: 配置物件
        logger: 日誌物件
    """
    while True:
        # 獲取任務
        task = task_manager.get_task()
        if not task:
            break
        
        # 更新任務狀態為執行中
        task_manager.update_task_status(task.task_id, "running")
        logger.info(f"開始執行任務：{task.task_id}")
        
        try:
            # 處理任務
            result = process_task(task, config, logger)
            
            # 更新任務狀態為完成
            task_manager.update_task_status(task.task_id, "completed", result=result)
            logger.info(f"任務完成：{task.task_id}")
            
        except Exception as e:
            # 更新任務狀態為失敗
            task_manager.update_task_status(task.task_id, "failed", error=str(e))
            logger.error(f"任務失敗：{task.task_id}，錯誤：{str(e)}")
        
        # 等待一段時間，避免請求過於頻繁
        time.sleep(random.uniform(2, 5))

def main():
    """主程式"""
    # 設定日誌
    logger = setup_logger()
    logger.info("開始執行 Shopee 分散式爬蟲範例")
    
    try:
        # 建立配置
        config = BaseConfig()
        
        # 建立任務管理器
        task_manager = TaskManager(max_workers=3)
        
        # 添加搜尋任務
        keywords = ["手機", "筆電", "耳機", "相機", "手錶"]
        for i, keyword in enumerate(keywords):
            task = Task(
                task_id=f"search_{i}",
                task_type="search",
                data={"keyword": keyword}
            )
            task_manager.add_task(task)
        
        # 啟動工作執行緒
        threads = []
        for _ in range(task_manager.max_workers):
            thread = threading.Thread(
                target=worker,
                args=(task_manager, config, logger)
            )
            thread.start()
            threads.append(thread)
        
        # 等待所有工作執行緒完成
        for thread in threads:
            thread.join()
        
        # 獲取任務結果
        results = task_manager.get_task_results()
        
        # 儲存結果
        save_results(results, "distributed_results.json")
        logger.info("成功儲存結果")
        
        # 輸出任務進度
        progress = task_manager.get_task_progress()
        logger.info(f"任務進度：{progress}")
        
        logger.info("範例執行完成")
        
    except Exception as e:
        logger.error(f"執行範例時發生錯誤：{str(e)}")
        raise
    finally:
        # 關閉任務管理器
        task_manager.shutdown()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CrawlerEngine 模組
負責協調多個爬蟲任務，提供任務隊列、多線程支持和狀態管理
支援模板驅動設計、錯誤處理和效能優化
"""

import os
import time
import logging
import threading
import queue
import json
import traceback
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from .template_crawler import TemplateCrawler
from .config_loader import ConfigLoader
from ..utils.logger import setup_logger
from ..persistence.data_persistence_manager import DataPersistenceManager

class CrawlerEngine:
    """
    爬蟲引擎類，負責協調多個爬蟲任務的執行
    提供多線程支持、任務隊列管理、統計信息收集和錯誤處理等功能
    """
    
    def __init__(
        self,
        config_file: str = "config/config.json",
        logger=None,
        max_workers: int = None,
        resume_crawling: bool = False
    ):
        """
        初始化爬蟲引擎
        
        Args:
            config_file: 配置文件路徑
            logger: 日誌記錄器，如果為None則創建新的
            max_workers: 最大工作線程數，如果為None則從配置中讀取
            resume_crawling: 是否啟用斷點續爬功能
        """
        self.logger = logger or setup_logger(__name__)
        self.logger.info(f"初始化爬蟲引擎，配置: {config_file}")
        
        # 載入配置
        self.config_loader = ConfigLoader(self.logger)
        self.config = self.config_loader.load_config(config_file)
        self.engine_config = self.config.get("engine_config", {})
        
        # 任務隊列和結果
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
        # 線程池設置
        self.max_workers = max_workers or self.engine_config.get("max_threads", 1)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.active_tasks = 0
        
        # 運行狀態
        self.is_running = False
        self.stop_requested = False
        self.resume_crawling = resume_crawling or self.engine_config.get("resume_crawling", False)
        
        # 統計信息
        self.stats = {
            "tasks_total": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "items_scraped": 0,
            "start_time": None,
            "end_time": None,
            "errors": []
        }
        
        # 初始化數據持久化管理器
        persistence_config = self.config.get("persistence_config", {})
        try:
            self.data_manager = DataPersistenceManager(persistence_config)
            self.logger.info("數據持久化管理器初始化成功")
        except ImportError:
            self.logger.warning("無法載入 DataPersistenceManager，將使用簡單的文件存儲")
            self.data_manager = None
        except Exception as e:
            self.logger.error(f"初始化數據持久化管理器失敗: {str(e)}")
            self.data_manager = None
        
        # 狀態鎖
        self.thread_lock = threading.Lock()
        self.logger.info(f"爬蟲引擎初始化完成，最大線程數: {self.max_workers}")
    
    def add_task(self, template_file: str, task_config: Dict = None, priority: int = 0):
        """
        添加爬蟲任務
        
        Args:
            template_file: 模板文件路徑
            task_config: 任務配置，可以覆蓋默認配置
            priority: 任務優先級，數字越大優先級越高
        """
        task = {
            "template_file": template_file,
            "config": task_config or {},
            "id": os.path.basename(template_file).replace(".json", ""),
            "priority": priority,
            "timestamp": time.time()
        }
        
        with self.thread_lock:
            self.stats["tasks_total"] += 1
        
        self.task_queue.put(task)
        self.logger.info(f"添加任務: {task['id']}, 優先級: {priority}")
    
    def add_tasks_from_directory(self, directory: str, filter_pattern: str = "*.json", priority: int = 0):
        """
        從目錄中添加所有匹配的模板文件作為任務
        
        Args:
            directory: 模板目錄路徑
            filter_pattern: 文件過濾模式
            priority: 任務優先級，數字越大優先級越高
        """
        import glob
        template_files = glob.glob(os.path.join(directory, filter_pattern))
        
        if not template_files:
            self.logger.warning(f"在目錄 {directory} 中沒有找到匹配 {filter_pattern} 的文件")
            return
        
        self.logger.info(f"從目錄 {directory} 添加 {len(template_files)} 個任務，優先級: {priority}")
        
        for template_file in template_files:
            self.add_task(template_file, priority=priority)
    
    def _worker(self, task: Dict) -> Dict:
        """
        工作線程函數，處理單個任務
        
        Args:
            task: 任務配置
            
        Returns:
            任務結果
        """
        task_id = task["id"]
        self.logger.info(f"開始處理任務: {task_id}")
        
        # 初始化任務狀態
        task_result = {
            "id": task_id,
            "template_file": task["template_file"],
            "success": False,
            "error": None,
            "items_count": 0,
            "start_time": time.time(),
            "end_time": None,
            "data": []
        }
        
        try:
            # 檢查是否需要恢復爬取
            resume_data = None
            if self.resume_crawling and self.data_manager:
                resume_data = self.data_manager.get_resume_data(task_id)
                if resume_data:
                    self.logger.info(f"找到任務 {task_id} 的斷點續爬數據")
            
            # 創建模板爬蟲實例
            crawler = TemplateCrawler(
                template_file=task["template_file"],
                config_file=self.config.get("config_file", "config/config.json"),
                logger=self.logger
            )
            
            # 設置爬蟲配置
            max_pages = task["config"].get("max_pages")
            max_items = task["config"].get("max_items")
            
            # 執行爬取
            data = crawler.start(
                max_pages=max_pages, 
                max_items=max_items,
                resume_data=resume_data
            )
            
            # 更新任務結果
            task_result["success"] = True
            task_result["items_count"] = len(data)
            task_result["data"] = data
            
            with self.thread_lock:
                self.stats["tasks_completed"] += 1
                self.stats["items_scraped"] += len(data)
            
            self.logger.info(f"任務 {task_id} 完成，爬取了 {len(data)} 個項目")
            
            # 保存數據
            if data:
                if self.data_manager is not None:
                    self._save_data(task_id, data)
                else:
                    self._save_to_file(task_id, data)
        
        except Exception as e:
            task_result["success"] = False
            task_result["error"] = str(e)
            
            with self.thread_lock:
                self.stats["tasks_failed"] += 1
                self.stats["errors"].append({
                    "task_id": task_id,
                    "error": str(e),
                    "timestamp": time.time()
                })
            
            self.logger.error(f"任務 {task_id} 失敗: {str(e)}")
            self.logger.debug(traceback.format_exc())
        
        finally:
            # 標記任務完成時間
            task_result["end_time"] = time.time()
            
            # 將結果加入結果隊列
            self.result_queue.put(task_result)
            
            # 更新活動任務計數
            with self.thread_lock:
                self.active_tasks -= 1
            
            return task_result
    
    def start(self, wait: bool = False):
        """
        啟動爬蟲引擎，開始處理任務
        
        Args:
            wait: 是否等待所有任務完成
        """
        if self.is_running:
            self.logger.warning("爬蟲引擎已經在運行")
            return
        
        self.is_running = True
        self.stop_requested = False
        self.stats["start_time"] = time.time()
        
        self.logger.info(f"啟動爬蟲引擎，最大線程數: {self.max_workers}")
        
        # 啟動任務處理
        self._process_tasks()
        
        # 如果需要等待所有任務完成
        if wait:
            self.logger.info("等待所有任務完成")
            self.wait_for_tasks()
            self.stop()
    
    def _process_tasks(self):
        """處理任務隊列中的任務"""
        if self.stop_requested:
            return
        
        # 檢查是否有任務需要處理
        if self.task_queue.empty():
            if self.active_tasks == 0:
                self.logger.info("所有任務已完成，停止引擎")
                self.stop()
            return
        
        # 提交任務到線程池
        while not self.task_queue.empty() and self.active_tasks < self.max_workers:
            try:
                task = self.task_queue.get(block=False)
                with self.thread_lock:
                    self.active_tasks += 1
                
                # 提交任務到線程池
                self.thread_pool.submit(self._worker, task)
                
                # 標記任務已從隊列中取出
                self.task_queue.task_done()
            except queue.Empty:
                break
        
        # 如果引擎仍在運行，安排下一次任務處理
        if self.is_running and not self.stop_requested:
            threading.Timer(1.0, self._process_tasks).start()
    
    def stop(self):
        """停止爬蟲引擎"""
        if not self.is_running:
            return
        
        self.logger.info("停止爬蟲引擎")
        self.stop_requested = True
        self.is_running = False
        
        # 等待所有活動任務完成
        self.wait_for_tasks(timeout=30)
        
        # 關閉線程池
        self.thread_pool.shutdown(wait=False)
        
        self.stats["end_time"] = time.time()
        
        self.logger.info("爬蟲引擎已停止")
    
    def get_status(self) -> Dict:
        """
        獲取爬蟲引擎狀態
        
        Returns:
            引擎狀態信息
        """
        with self.thread_lock:
            status = {
                "is_running": self.is_running,
                "active_tasks": self.active_tasks,
                "queued_tasks": self.task_queue.qsize(),
                "completed_results": self.result_queue.qsize(),
                "stats": self.stats.copy()
            }
            
            # 計算運行時間
            if self.stats["start_time"]:
                end_time = self.stats["end_time"] or time.time()
                status["runtime_seconds"] = end_time - self.stats["start_time"]
                
                # 計算任務處理速率
                if self.stats["tasks_completed"] > 0:
                    status["tasks_per_second"] = self.stats["tasks_completed"] / status["runtime_seconds"]
                    status["items_per_second"] = self.stats["items_scraped"] / status["runtime_seconds"]
            
            # 添加最近的錯誤
            if self.stats["errors"]:
                status["recent_errors"] = self.stats["errors"][-5:]  # 只返回最近5個錯誤
            
            return status
    
    def get_results(self, clear: bool = False, limit: int = None) -> List[Dict]:
        """
        獲取所有已完成任務的結果
        
        Args:
            clear: 是否清空結果隊列
            limit: 返回結果的最大數量，None表示返回所有結果
            
        Returns:
            任務結果列表
        """
        results = []
        
        # 將結果隊列中的所有項目取出
        while not self.result_queue.empty() and (limit is None or len(results) < limit):
            results.append(self.result_queue.get())
            self.result_queue.task_done()
        
        # 如果不需要清空結果，將結果重新放回隊列
        if not clear:
            for result in results:
                self.result_queue.put(result)
        
        return results
    
    def wait_for_tasks(self, timeout: float = None) -> bool:
        """
        等待所有任務完成
        
        Args:
            timeout: 超時時間（秒），None表示無限等待
            
        Returns:
            是否所有任務都已完成
        """
        try:
            # 等待任務隊列為空
            self.task_queue.join(timeout=timeout)
            
            # 等待活動任務完成
            start_time = time.time()
            while self.active_tasks > 0:
                if timeout and (time.time() - start_time) > timeout:
                    self.logger.warning(f"等待任務完成超時，仍有 {self.active_tasks} 個活動任務")
                    return False
                time.sleep(0.5)
            
            return True
        except Exception as e:
            self.logger.error(f"等待任務完成時出錯: {str(e)}")
            return False
    
    def run_crawler(self, template_file: str, config: Dict = None) -> Dict:
        """
        直接運行單個爬蟲任務，不使用線程池
        
        Args:
            template_file: 模板文件路徑
            config: 任務配置
            
        Returns:
            爬取結果
        """
        task_id = os.path.basename(template_file).replace(".json", "")
        self.logger.info(f"直接運行爬蟲任務: {task_id}")
        
        config = config or {}
        result = {
            "id": task_id,
            "template_file": template_file,
            "success": False,
            "error": None,
            "items_count": 0,
            "start_time": time.time(),
            "end_time": None,
            "data": []
        }
        
        try:
            # 檢查是否需要恢復爬取
            resume_data = None
            if self.resume_crawling and self.data_manager:
                resume_data = self.data_manager.get_resume_data(task_id)
                if resume_data:
                    self.logger.info(f"找到任務 {task_id} 的斷點續爬數據")
            
            # 創建模板爬蟲實例
            crawler = TemplateCrawler(
                template_file=template_file,
                config_file=self.config.get("config_file", "config/config.json"),
                logger=self.logger
            )
            
            # 執行爬取
            data = crawler.start(
                max_pages=config.get("max_pages"),
                max_items=config.get("max_items"),
                resume_data=resume_data
            )
            
            # 更新結果
            result["success"] = True
            result["items_count"] = len(data)
            result["data"] = data
            
            # 保存數據
            if data and config.get("save_data", True):
                if self.data_manager is not None:
                    self._save_data(task_id, data)
                else:
                    self._save_to_file(task_id, data)
                
            self.logger.info(f"任務 {task_id} 完成，爬取了 {len(data)} 個項目")
        
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            
            # 提供完整的異常堆疊信息以便調試
            self.logger.error(f"任務 {task_id} 失敗: {str(e)}", exc_info=True)
        
        finally:
            # 標記完成時間
            result["end_time"] = time.time()
        
        return result
    
    def _save_data(self, task_id: str, data: List[Dict]) -> bool:
        """
        使用數據持久化管理器保存數據
        
        Args:
            task_id: 任務ID
            data: 爬取的數據
            
        Returns:
            是否保存成功
        """
        try:
            self.logger.info(f"使用數據持久化管理器保存 {len(data)} 項數據")
            result = self.data_manager.save_data(task_id, data)
            if result:
                self.logger.info(f"數據保存成功: {task_id}")
            else:
                self.logger.warning(f"數據保存失敗: {task_id}")
            return result
        except Exception as e:
            self.logger.error(f"保存數據時出錯: {str(e)}")
            self._save_to_file(task_id, data)  # 備用方案
            return False
    
    def _save_to_file(self, task_id: str, data: List[Dict]) -> bool:
        """
        將數據保存到文件
        
        Args:
            task_id: 任務ID
            data: 爬取的數據
            
        Returns:
            是否保存成功
        """
        if not data:
            self.logger.warning(f"沒有數據需要保存: {task_id}")
            return False
        
        try:
            # 獲取輸出目錄
            output_dir = self.engine_config.get("output_dir", "output")
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{task_id}_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            # 保存數據
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"數據已保存到文件: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"保存數據到文件時出錯: {str(e)}")
            return False
    
    def clear_results(self) -> None:
        """清空結果隊列"""
        while not self.result_queue.empty():
            self.result_queue.get()
            self.result_queue.task_done()
        self.logger.info("結果隊列已清空")
    
    def reset_stats(self) -> None:
        """重置統計信息"""
        with self.thread_lock:
            self.stats = {
                "tasks_total": 0,
                "tasks_completed": 0,
                "tasks_failed": 0,
                "items_scraped": 0,
                "start_time": None,
                "end_time": None,
                "errors": []
            }
        self.logger.info("統計信息已重置")
    
    def get_task_progress(self) -> Dict[str, Any]:
        """
        獲取任務進度信息
        
        Returns:
            任務進度信息
        """
        with self.thread_lock:
            total = self.stats["tasks_total"]
            completed = self.stats["tasks_completed"]
            failed = self.stats["tasks_failed"]
            in_progress = self.active_tasks
            queued = self.task_queue.qsize()
            
            if total > 0:
                progress_percent = (completed + failed) / total * 100
            else:
                progress_percent = 0
            
            return {
                "total": total,
                "completed": completed,
                "failed": failed,
                "in_progress": in_progress,
                "queued": queued,
                "progress_percent": progress_percent,
                "items_scraped": self.stats["items_scraped"]
            }
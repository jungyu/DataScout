#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬蟲引擎模組

提供爬蟲核心功能，包括：
- 任務管理
- 多線程支持
- 狀態管理
- 錯誤處理
- 資源管理
- 性能監控
"""

import os
import time
import queue
import logging
import threading
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from .utils.logger import Logger, setup_logger
from .utils.url_utils import URLUtils
from .utils.data_processor import SimpleDataProcessor as UtilsDataProcessor
from .utils.config_utils import ConfigUtils
from .utils.path_utils import PathUtils
from .utils.cookie_manager import CookieManager
from .utils.error_handler import ErrorHandler
from .crawler_state_manager import CrawlerStateManager
from .data_processor import DataProcessor
from .webdriver_manager import WebDriverManager

@dataclass
class Task:
    """爬蟲任務"""
    id: str
    url: str
    params: Dict
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    status: str = "pending"
    result: Any = None
    error: str = None

class CrawlerEngine:
    """爬蟲引擎"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化爬蟲引擎
        
        Args:
            config: 配置字典
        """
        # 初始化工具類
        self.logger = setup_logger(
            name="crawler_engine",
            level=logging.INFO,
            log_dir="logs",
            console_output=True,
            file_output=True
        )
        self.url_utils = URLUtils(self.logger)
        self.data_processor = UtilsDataProcessor(self.logger)
        self.config_utils = ConfigUtils(self.logger)
        self.path_utils = PathUtils(self.logger)
        self.error_handler = ErrorHandler(self.logger)
        
        # 加載配置
        config_dict = config or {}
        self.config = {
            "max_workers": config_dict.get("max_workers", 4),
            "task_queue_size": config_dict.get("task_queue_size", 1000),
            "max_retries": config_dict.get("max_retries", 3),
            "retry_delay": config_dict.get("retry_delay", 5),
            "timeout": config_dict.get("timeout", 30),
            "output_dir": config_dict.get("output_dir", "data/output"),
            "temp_dir": config_dict.get("temp_dir", "data/temp"),
            "log_dir": config_dict.get("log_dir", "logs"),
            "cookie_file": config_dict.get("cookie_file", "data/cookies.json"),
            "state_file": config_dict.get("state_file", "data/state.json")
        }
        
        # 初始化組件
        self.state_manager = CrawlerStateManager(self.config["state_file"])
        self.data_processor = DataProcessor(config_dict.get("data_processor", {}))
        self.webdriver_manager = WebDriverManager(config_dict.get("webdriver", {}))
        self.cookie_manager = CookieManager(self.config["cookie_file"])
        
        # 初始化任務隊列
        self.task_queue = queue.PriorityQueue(maxsize=self.config["task_queue_size"])
        self.task_results = {}
        self.task_lock = threading.Lock()
        
        # 初始化線程池
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.config["max_workers"],
            thread_name_prefix="crawler_worker"
        )
        
        # 初始化狀態
        self.is_running = False
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "retried_tasks": 0,
            "start_time": None,
            "last_update": None
        }
        
        # 創建目錄
        self.path_utils.ensure_dir(self.config["output_dir"])
        self.path_utils.ensure_dir(self.config["temp_dir"])
        self.path_utils.ensure_dir(self.config["log_dir"])
    
    def add_task(self, url: str, params: Optional[Dict] = None, priority: int = 0) -> str:
        """
        添加任務
        
        Args:
            url: 目標URL
            params: 任務參數
            priority: 任務優先級
            
        Returns:
            任務ID
        """
        try:
            # 驗證URL
            if not self.url_utils.is_valid_url(url):
                raise ValueError(f"無效的URL: {url}")
            
            # 生成任務ID
            task_id = f"task_{int(time.time() * 1000)}_{self.stats['total_tasks']}"
            
            # 創建任務
            task = Task(
                id=task_id,
                url=url,
                params=params or {},
                priority=priority,
                created_at=datetime.now()
            )
            
            # 添加到隊列
            self.task_queue.put((-priority, task))
            
            # 更新統計信息
            with self.task_lock:
                self.stats["total_tasks"] += 1
                self.stats["last_update"] = datetime.now()
            
            self.logger.info(f"添加任務: {task_id} - {url}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"添加任務失敗: {str(e)}")
            self.error_handler.handle_error(e)
            raise
    
    def start(self):
        """啟動爬蟲引擎"""
        try:
            if self.is_running:
                self.logger.warning("爬蟲引擎已在運行")
                return
            
            self.is_running = True
            self.stats["start_time"] = datetime.now()
            
            # 啟動工作線程
            for _ in range(self.config["max_workers"]):
                self.thread_pool.submit(self._worker_loop)
            
            self.logger.info("爬蟲引擎已啟動")
            
        except Exception as e:
            self.logger.error(f"啟動爬蟲引擎失敗: {str(e)}")
            self.error_handler.handle_error(e)
            self.is_running = False
            raise
    
    def stop(self):
        """停止爬蟲引擎"""
        try:
            if not self.is_running:
                self.logger.warning("爬蟲引擎未運行")
                return
            
            self.is_running = False
            
            # 等待任務完成
            self.thread_pool.shutdown(wait=True)
            
            # 清理資源
            self.webdriver_manager.close_all()
            self.webdriver_manager.clear_temp_files()
            
            self.logger.info("爬蟲引擎已停止")
            
        except Exception as e:
            self.logger.error(f"停止爬蟲引擎失敗: {str(e)}")
            self.error_handler.handle_error(e)
            raise
    
    def _worker_loop(self):
        """工作線程循環"""
        while self.is_running:
            try:
                # 獲取任務
                priority, task = self.task_queue.get(timeout=1)
                
                # 更新任務狀態
                task.status = "running"
                task.started_at = datetime.now()
                
                # 處理任務
                self._process_task(task)
                
                # 標記任務完成
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"工作線程異常: {str(e)}")
                self.error_handler.handle_error(e)
    
    def _process_task(self, task: Task):
        """
        處理任務
        
        Args:
            task: 爬蟲任務
        """
        driver = None
        try:
            # 獲取WebDriver
            driver = self.webdriver_manager.get_driver()
            
            # 加載cookies
            self.cookie_manager.load_cookies(driver)
            
            # 訪問URL
            driver.get(task.url)
            
            # 等待頁面加載
            time.sleep(2)
            
            # 提取數據
            result = self._extract_data(driver, task.params)
            
            # 處理數據
            processed_result = self.data_processor.process(result)
            
            # 保存結果
            self._save_result(task.id, processed_result)
            
            # 更新任務狀態
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = processed_result
            
            # 更新統計信息
            with self.task_lock:
                self.stats["completed_tasks"] += 1
                self.stats["last_update"] = datetime.now()
            
            self.logger.info(f"任務完成: {task.id}")
            
        except Exception as e:
            self.logger.error(f"處理任務失敗: {str(e)}")
            self.error_handler.handle_error(e)
            
            # 重試任務
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = "retrying"
                task.error = str(e)
                
                # 重新加入隊列
                self.task_queue.put((-task.priority, task))
                
                # 更新統計信息
                with self.task_lock:
                    self.stats["retried_tasks"] += 1
                    self.stats["last_update"] = datetime.now()
                
                self.logger.info(f"任務重試: {task.id} - 第 {task.retry_count} 次")
                
            else:
                # 任務失敗
                task.status = "failed"
                task.completed_at = datetime.now()
                task.error = str(e)
                
                # 更新統計信息
                with self.task_lock:
                    self.stats["failed_tasks"] += 1
                    self.stats["last_update"] = datetime.now()
                
                self.logger.error(f"任務失敗: {task.id}")
            
        finally:
            # 釋放WebDriver
            if driver:
                self.webdriver_manager.release_driver(driver)
    
    def _extract_data(self, driver: Any, params: Dict) -> Dict:
        """
        提取數據
        
        Args:
            driver: WebDriver實例
            params: 提取參數
            
        Returns:
            提取的數據
        """
        try:
            # 使用工具類提取數據
            data = self.data_processor.extract_data(driver, params)
            return data
            
        except Exception as e:
            self.logger.error(f"提取數據失敗: {str(e)}")
            self.error_handler.handle_error(e)
            raise
    
    def _save_result(self, task_id: str, result: Any):
        """
        保存結果
        
        Args:
            task_id: 任務ID
            result: 結果數據
        """
        try:
            # 生成文件名
            filename = f"{task_id}_{int(time.time())}.json"
            file_path = self.path_utils.join_path(self.config["output_dir"], filename)
            
            # 保存結果
            self.data_processor.save_to_file(result, file_path)
            
            self.logger.info(f"結果已保存: {file_path}")
            
        except Exception as e:
            self.logger.error(f"保存結果失敗: {str(e)}")
            self.error_handler.handle_error(e)
    
    def get_task_status(self, task_id: str) -> Dict:
        """
        獲取任務狀態
        
        Args:
            task_id: 任務ID
            
        Returns:
            任務狀態
        """
        try:
            with self.task_lock:
                for _, task in list(self.task_queue.queue):
                    if task.id == task_id:
                        return {
                            "id": task.id,
                            "url": task.url,
                            "status": task.status,
                            "created_at": task.created_at,
                            "started_at": task.started_at,
                            "completed_at": task.completed_at,
                            "retry_count": task.retry_count,
                            "error": task.error
                        }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"獲取任務狀態失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return {}
    
    def get_stats(self) -> Dict:
        """
        獲取統計信息
        
        Returns:
            Dict: 統計信息
        """
        try:
            stats = self.stats.copy()
            
            if stats["start_time"]:
                stats["duration"] = (datetime.now() - stats["start_time"]).total_seconds()
            
            return stats
            
        except Exception as e:
            self.logger.error(f"獲取統計信息失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return {}
    
    def __del__(self):
        """析構函數"""
        self.stop()
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
性能優化提取器模組

提供提取器性能優化功能，包括：
1. 資源管理
2. 並行處理
3. 緩存優化
4. 性能監控
"""

from typing import Dict, List, Optional, Union, Any, Set, Callable, Type
from dataclasses import dataclass
import time
import threading
import logging
import queue
import concurrent.futures
import psutil
import gc
from datetime import datetime
from functools import wraps

from ..core.base import BaseExtractor
from ..core.error import handle_extractor_error, ExtractorError

@dataclass
class PerformanceConfig:
    """性能配置"""
    # 資源管理
    max_memory: float = 0.8  # 最大內存使用率
    max_cpu: float = 0.8  # 最大 CPU 使用率
    gc_threshold: int = 1000  # GC 觸發閾值
    cleanup_interval: int = 300  # 清理間隔（秒）
    
    # 並行處理
    max_workers: int = 4  # 最大工作線程數
    task_timeout: float = 30.0  # 任務超時時間
    queue_size: int = 100  # 任務隊列大小
    
    # 緩存優化
    cache_size: int = 1000  # 緩存大小
    cache_ttl: int = 3600  # 緩存過期時間（秒）
    cache_cleanup: int = 300  # 緩存清理間隔（秒）
    
    # 性能監控
    monitor_interval: int = 60  # 監控間隔（秒）
    log_performance: bool = True  # 是否記錄性能日誌
    alert_threshold: float = 0.9  # 告警閾值

class PerformanceExtractor(BaseExtractor):
    """性能優化提取器類別"""
    
    def __init__(self, driver: Any, config: Optional[PerformanceConfig] = None):
        """初始化性能優化提取器
        
        Args:
            driver: WebDriver 實例
            config: 性能配置
        """
        super().__init__(driver)
        self.config = config or PerformanceConfig()
        self._logger = logging.getLogger(__name__)
        self._task_queue = queue.Queue(maxsize=self.config.queue_size)
        self._result_cache = {}
        self._performance_stats = {
            "start_time": time.time(),
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "total_time": 0,
            "avg_time": 0,
            "max_time": 0,
            "min_time": float("inf"),
            "memory_usage": [],
            "cpu_usage": []
        }
        self._lock = threading.Lock()
        self._monitor_thread = None
        self._cleanup_thread = None
        self._running = True
        
        # 啟動監控和清理線程
        self._start_monitor()
        self._start_cleanup()
        
    def _start_monitor(self):
        """啟動性能監控"""
        def monitor():
            while self._running:
                try:
                    self._update_performance_stats()
                    if self.config.log_performance:
                        self._log_performance()
                    time.sleep(self.config.monitor_interval)
                except Exception as e:
                    self._logger.error(f"性能監控錯誤: {str(e)}")
                    
        self._monitor_thread = threading.Thread(target=monitor, daemon=True)
        self._monitor_thread.start()
        
    def _start_cleanup(self):
        """啟動資源清理"""
        def cleanup():
            while self._running:
                try:
                    self._cleanup_resources()
                    time.sleep(self.config.cleanup_interval)
                except Exception as e:
                    self._logger.error(f"資源清理錯誤: {str(e)}")
                    
        self._cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        self._cleanup_thread.start()
        
    def _update_performance_stats(self):
        """更新性能統計"""
        with self._lock:
            process = psutil.Process()
            memory_percent = process.memory_percent()
            cpu_percent = process.cpu_percent()
            
            self._performance_stats["memory_usage"].append(memory_percent)
            self._performance_stats["cpu_usage"].append(cpu_percent)
            
            # 檢查資源使用是否超過閾值
            if memory_percent > self.config.max_memory:
                self._logger.warning(f"內存使用率過高: {memory_percent:.2%}")
                gc.collect()
                
            if cpu_percent > self.config.max_cpu:
                self._logger.warning(f"CPU 使用率過高: {cpu_percent:.2%}")
                
    def _log_performance(self):
        """記錄性能日誌"""
        with self._lock:
            stats = self._performance_stats
            avg_memory = sum(stats["memory_usage"][-10:]) / min(10, len(stats["memory_usage"]))
            avg_cpu = sum(stats["cpu_usage"][-10:]) / min(10, len(stats["cpu_usage"]))
            
            self._logger.info(
                f"性能統計:\n"
                f"運行時間: {time.time() - stats['start_time']:.2f}秒\n"
                f"總任務數: {stats['total_tasks']}\n"
                f"完成任務: {stats['completed_tasks']}\n"
                f"失敗任務: {stats['failed_tasks']}\n"
                f"平均耗時: {stats['avg_time']:.2f}秒\n"
                f"最大耗時: {stats['max_time']:.2f}秒\n"
                f"最小耗時: {stats['min_time']:.2f}秒\n"
                f"平均內存: {avg_memory:.2%}\n"
                f"平均 CPU: {avg_cpu:.2%}"
            )
            
    def _cleanup_resources(self):
        """清理資源"""
        with self._lock:
            # 清理過期緩存
            current_time = time.time()
            expired_keys = [
                k for k, v in self._result_cache.items()
                if current_time - v["timestamp"] > self.config.cache_ttl
            ]
            for k in expired_keys:
                del self._result_cache[k]
                
            # 限制緩存大小
            if len(self._result_cache) > self.config.cache_size:
                sorted_cache = sorted(
                    self._result_cache.items(),
                    key=lambda x: x[1]["timestamp"]
                )
                for k, _ in sorted_cache[:-self.config.cache_size]:
                    del self._result_cache[k]
                    
            # 觸發垃圾回收
            if len(self._performance_stats["memory_usage"]) > self.config.gc_threshold:
                gc.collect()
                self._performance_stats["memory_usage"] = self._performance_stats["memory_usage"][-100:]
                self._performance_stats["cpu_usage"] = self._performance_stats["cpu_usage"][-100:]
                
    def _update_task_stats(self, task_time: float, success: bool):
        """更新任務統計
        
        Args:
            task_time: 任務耗時
            success: 是否成功
        """
        with self._lock:
            stats = self._performance_stats
            stats["total_tasks"] += 1
            if success:
                stats["completed_tasks"] += 1
            else:
                stats["failed_tasks"] += 1
                
            stats["total_time"] += task_time
            stats["avg_time"] = stats["total_time"] / stats["completed_tasks"]
            stats["max_time"] = max(stats["max_time"], task_time)
            stats["min_time"] = min(stats["min_time"], task_time)
            
    def performance_monitor(self, func: Callable) -> Callable:
        """性能監控裝飾器
        
        Args:
            func: 被裝飾的函數
            
        Returns:
            Callable: 裝飾後的函數
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            finally:
                task_time = time.time() - start_time
                self._update_task_stats(task_time, success)
        return wrapper
        
    @handle_extractor_error()
    def execute_parallel(self, tasks: List[Dict[str, Any]]) -> List[Any]:
        """並行執行任務
        
        Args:
            tasks: 任務列表
            
        Returns:
            List[Any]: 結果列表
        """
        results = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.max_workers
        ) as executor:
            future_to_task = {
                executor.submit(
                    self._execute_task,
                    task,
                    timeout=self.config.task_timeout
                ): task
                for task in tasks
            }
            
            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self._logger.error(f"任務執行失敗: {str(e)}")
                    results.append(None)
                    
        return results
        
    @handle_extractor_error()
    def _execute_task(self, task: Dict[str, Any], timeout: float) -> Any:
        """執行單個任務
        
        Args:
            task: 任務信息
            timeout: 超時時間
            
        Returns:
            Any: 執行結果
        """
        start_time = time.time()
        success = False
        try:
            # 檢查緩存
            cache_key = str(task)
            if cache_key in self._result_cache:
                cache_data = self._result_cache[cache_key]
                if time.time() - cache_data["timestamp"] <= self.config.cache_ttl:
                    return cache_data["result"]
                    
            # 執行任務
            result = task["func"](*task.get("args", []), **task.get("kwargs", {}))
            success = True
            
            # 更新緩存
            self._result_cache[cache_key] = {
                "result": result,
                "timestamp": time.time()
            }
            
            return result
            
        finally:
            task_time = time.time() - start_time
            self._update_task_stats(task_time, success)
            
    def get_performance_stats(self) -> Dict[str, Any]:
        """獲取性能統計
        
        Returns:
            Dict[str, Any]: 性能統計信息
        """
        with self._lock:
            return self._performance_stats.copy()
            
    def cleanup(self):
        """清理資源"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join()
        if self._cleanup_thread:
            self._cleanup_thread.join()
        self._cleanup_resources()
        
    def __del__(self):
        """析構函數"""
        self.cleanup() 
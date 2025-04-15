#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
監控提取器模組

提供提取器監控和統計功能，包括：
1. 提取器狀態監控
2. 性能指標統計
3. 錯誤追蹤
4. 資源使用分析
"""

from typing import Dict, List, Optional, Union, Any, Set, Callable, Type
from dataclasses import dataclass
import time
import threading
import logging
import json
import os
from datetime import datetime
import psutil
import gc
from collections import defaultdict
import traceback
from pathlib import Path

from ..core.base import BaseExtractor
from ..core.error import handle_extractor_error, ExtractorError

@dataclass
class MonitorConfig:
    """監控配置"""
    # 監控設置
    monitor_interval: int = 60  # 監控間隔（秒）
    log_interval: int = 300  # 日誌間隔（秒）
    stats_file: str = "extractor_stats.json"
    error_file: str = "extractor_errors.json"
    
    # 性能指標
    track_memory: bool = True
    track_cpu: bool = True
    track_network: bool = True
    track_disk: bool = True
    
    # 錯誤追蹤
    max_errors: int = 1000
    error_retention: int = 86400  # 錯誤保留時間（秒）
    alert_threshold: int = 10  # 錯誤告警閾值
    
    # 資源分析
    resource_threshold: float = 0.8  # 資源使用閾值
    analysis_interval: int = 3600  # 分析間隔（秒）
    
    def __post_init__(self):
        # 創建日誌目錄
        log_dir = os.path.dirname(self.stats_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
class MonitorExtractor(BaseExtractor):
    """監控提取器類別"""
    
    def __init__(self, driver: Any, config: Optional[MonitorConfig] = None):
        """初始化監控提取器
        
        Args:
            driver: WebDriver 實例
            config: 監控配置
        """
        super().__init__(driver)
        self.config = config or MonitorConfig()
        self._logger = logging.getLogger(__name__)
        self._stats = {
            "start_time": time.time(),
            "extractors": defaultdict(lambda: {
                "calls": 0,
                "success": 0,
                "errors": 0,
                "total_time": 0,
                "avg_time": 0,
                "max_time": 0,
                "min_time": float("inf"),
                "last_error": None,
                "last_success": None
            }),
            "resources": {
                "memory": [],
                "cpu": [],
                "network": [],
                "disk": []
            },
            "errors": [],
            "alerts": []
        }
        self._lock = threading.Lock()
        self._monitor_thread = None
        self._analysis_thread = None
        self._running = True
        
        # 啟動監控和分析線程
        self._start_monitor()
        self._start_analysis()
        
    def _start_monitor(self):
        """啟動監控線程"""
        def monitor():
            while self._running:
                try:
                    self._update_stats()
                    if time.time() % self.config.log_interval < self.config.monitor_interval:
                        self._save_stats()
                    time.sleep(self.config.monitor_interval)
                except Exception as e:
                    self._logger.error(f"監控錯誤: {str(e)}")
                    
        self._monitor_thread = threading.Thread(target=monitor, daemon=True)
        self._monitor_thread.start()
        
    def _start_analysis(self):
        """啟動分析線程"""
        def analyze():
            while self._running:
                try:
                    self._analyze_resources()
                    time.sleep(self.config.analysis_interval)
                except Exception as e:
                    self._logger.error(f"分析錯誤: {str(e)}")
                    
        self._analysis_thread = threading.Thread(target=analyze, daemon=True)
        self._analysis_thread.start()
        
    def _update_stats(self):
        """更新統計信息"""
        with self._lock:
            # 更新資源使用
            process = psutil.Process()
            
            if self.config.track_memory:
                memory_info = process.memory_info()
                self._stats["resources"]["memory"].append({
                    "timestamp": time.time(),
                    "rss": memory_info.rss,
                    "vms": memory_info.vms,
                    "percent": process.memory_percent()
                })
                
            if self.config.track_cpu:
                self._stats["resources"]["cpu"].append({
                    "timestamp": time.time(),
                    "percent": process.cpu_percent(),
                    "num_threads": process.num_threads()
                })
                
            if self.config.track_network:
                net_io = process.io_counters()
                self._stats["resources"]["network"].append({
                    "timestamp": time.time(),
                    "read_bytes": net_io.read_bytes,
                    "write_bytes": net_io.write_bytes
                })
                
            if self.config.track_disk:
                disk_io = process.io_counters()
                self._stats["resources"]["disk"].append({
                    "timestamp": time.time(),
                    "read_count": disk_io.read_count,
                    "write_count": disk_io.write_count
                })
                
            # 清理舊數據
            self._cleanup_old_data()
            
    def _cleanup_old_data(self):
        """清理舊數據"""
        current_time = time.time()
        
        # 清理錯誤記錄
        self._stats["errors"] = [
            error for error in self._stats["errors"]
            if current_time - error["timestamp"] <= self.config.error_retention
        ][-self.config.max_errors:]
        
        # 清理資源數據
        for resource_type in self._stats["resources"]:
            self._stats["resources"][resource_type] = [
                data for data in self._stats["resources"][resource_type]
                if current_time - data["timestamp"] <= self.config.error_retention
            ]
            
    def _analyze_resources(self):
        """分析資源使用"""
        with self._lock:
            # 分析內存使用
            if self.config.track_memory:
                memory_data = self._stats["resources"]["memory"]
                if memory_data:
                    avg_memory = sum(d["percent"] for d in memory_data) / len(memory_data)
                    if avg_memory > self.config.resource_threshold:
                        self._add_alert("內存使用率過高", {
                            "type": "memory",
                            "value": avg_memory,
                            "threshold": self.config.resource_threshold
                        })
                        
            # 分析 CPU 使用
            if self.config.track_cpu:
                cpu_data = self._stats["resources"]["cpu"]
                if cpu_data:
                    avg_cpu = sum(d["percent"] for d in cpu_data) / len(cpu_data)
                    if avg_cpu > self.config.resource_threshold:
                        self._add_alert("CPU 使用率過高", {
                            "type": "cpu",
                            "value": avg_cpu,
                            "threshold": self.config.resource_threshold
                        })
                        
            # 分析錯誤率
            total_errors = sum(e["errors"] for e in self._stats["extractors"].values())
            total_calls = sum(e["calls"] for e in self._stats["extractors"].values())
            if total_calls > 0:
                error_rate = total_errors / total_calls
                if error_rate > self.config.alert_threshold / 100:
                    self._add_alert("錯誤率過高", {
                        "type": "error_rate",
                        "value": error_rate,
                        "threshold": self.config.alert_threshold / 100
                    })
                    
    def _add_alert(self, message: str, data: Dict[str, Any]):
        """添加告警
        
        Args:
            message: 告警消息
            data: 告警數據
        """
        alert = {
            "timestamp": time.time(),
            "message": message,
            "data": data
        }
        self._stats["alerts"].append(alert)
        self._logger.warning(f"告警: {message} - {json.dumps(data)}")
        
    def _save_stats(self):
        """保存統計信息"""
        try:
            with open(self.config.stats_file, "w", encoding="utf-8") as f:
                json.dump(self._stats, f, indent=2)
        except Exception as e:
            self._logger.error(f"保存統計信息失敗: {str(e)}")
            
    def track_extractor(self, name: str, start_time: float, success: bool, error: Optional[Exception] = None):
        """追蹤提取器執行
        
        Args:
            name: 提取器名稱
            start_time: 開始時間
            success: 是否成功
            error: 錯誤信息
        """
        with self._lock:
            stats = self._stats["extractors"][name]
            stats["calls"] += 1
            
            if success:
                stats["success"] += 1
                stats["last_success"] = time.time()
            else:
                stats["errors"] += 1
                stats["last_error"] = time.time()
                
                if error:
                    self._stats["errors"].append({
                        "timestamp": time.time(),
                        "extractor": name,
                        "error": str(error),
                        "traceback": traceback.format_exc()
                    })
                    
            execution_time = time.time() - start_time
            stats["total_time"] += execution_time
            stats["avg_time"] = stats["total_time"] / stats["calls"]
            stats["max_time"] = max(stats["max_time"], execution_time)
            stats["min_time"] = min(stats["min_time"], execution_time)
            
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        with self._lock:
            return self._stats.copy()
            
    def get_extractor_stats(self, name: str) -> Dict[str, Any]:
        """獲取提取器統計信息
        
        Args:
            name: 提取器名稱
            
        Returns:
            Dict[str, Any]: 提取器統計信息
        """
        with self._lock:
            return self._stats["extractors"][name].copy()
            
    def get_errors(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """獲取錯誤記錄
        
        Args:
            limit: 限制數量
            
        Returns:
            List[Dict[str, Any]]: 錯誤記錄
        """
        with self._lock:
            errors = self._stats["errors"]
            if limit:
                errors = errors[-limit:]
            return errors
            
    def get_alerts(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """獲取告警記錄
        
        Args:
            limit: 限制數量
            
        Returns:
            List[Dict[str, Any]]: 告警記錄
        """
        with self._lock:
            alerts = self._stats["alerts"]
            if limit:
                alerts = alerts[-limit:]
            return alerts
            
    def cleanup(self):
        """清理資源"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join()
        if self._analysis_thread:
            self._analysis_thread.join()
        self._save_stats()
        
    def __del__(self):
        """析構函數"""
        self.cleanup() 
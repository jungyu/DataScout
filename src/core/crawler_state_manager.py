#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬蟲狀態管理器

此模組提供爬蟲狀態的保存、載入和管理功能，支持任務的中斷和恢復，
以及多重備份策略。支持多種存儲格式（JSON、Pickle）和自動保存機制。
"""

import json
import time
import pickle
import logging
import shutil
import threading
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum, auto
from datetime import datetime

from ..utils.logger import setup_logger
from ..utils.error_handler import retry_on_exception, handle_exception


class StorageFormat(Enum):
    """存儲格式枚舉"""
    JSON = "json"
    PICKLE = "pickle"


@dataclass
class CrawlerStateConfig:
    """爬蟲狀態配置"""
    auto_save_interval: int = 60  # 自動保存間隔（秒）
    auto_save_enabled: bool = True  # 是否啟用自動保存
    max_backups: int = 5  # 最大備份數量
    backup_on_save: bool = True  # 保存時是否創建備份
    storage_formats: Set[StorageFormat] = field(default_factory=lambda: {StorageFormat.JSON, StorageFormat.PICKLE})
    compression: bool = False  # 是否壓縮
    encoding: str = "utf-8"  # 文件編碼


@dataclass
class CrawlerState:
    """爬蟲狀態數據類"""
    crawler_id: str
    created_time: int = field(default_factory=lambda: int(time.time()))
    completed: bool = False
    completion_time: Optional[int] = None
    timestamp: Optional[int] = None
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "crawler_id": self.crawler_id,
            "created_time": self.created_time,
            "completed": self.completed,
            "completion_time": self.completion_time,
            "timestamp": self.timestamp,
            "data": self.data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrawlerState':
        """從字典創建實例"""
        return cls(
            crawler_id=data.get("crawler_id", ""),
            created_time=data.get("created_time", int(time.time())),
            completed=data.get("completed", False),
            completion_time=data.get("completion_time"),
            timestamp=data.get("timestamp"),
            data=data.get("data", {})
        )


class CrawlerStateManager:
    """
    爬蟲狀態管理器，負責爬蟲狀態的保存、載入和管理，
    支持任務的中斷和恢復，以及多重備份策略。
    """
    
    def __init__(
        self,
        crawler_id: str,
        config: Optional[Dict] = None,
        state_dir: str = "states",
        log_level: int = logging.INFO
    ):
        """
        初始化爬蟲狀態管理器
        
        Args:
            crawler_id: 爬蟲ID，用於標識不同的爬蟲任務
            config: 配置字典
            state_dir: 狀態存儲目錄
            log_level: 日誌級別
        """
        self.logger = setup_logger(__name__, log_level)
        self.crawler_id = crawler_id
        
        # 加載配置
        config_dict = config or {}
        self.config = CrawlerStateConfig(
            auto_save_interval=config_dict.get("auto_save_interval", 60),
            auto_save_enabled=config_dict.get("auto_save_enabled", True),
            max_backups=config_dict.get("max_backups", 5),
            backup_on_save=config_dict.get("backup_on_save", True),
            storage_formats={StorageFormat(fmt) for fmt in config_dict.get("storage_formats", ["json", "pickle"])},
            compression=config_dict.get("compression", False),
            encoding=config_dict.get("encoding", "utf-8")
        )
        
        # 初始化目錄
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # 備份目錄
        self.backup_dir = self.state_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # 狀態文件路徑
        self.state_files = {
            StorageFormat.JSON: self.state_dir / f"{crawler_id}_state.json",
            StorageFormat.PICKLE: self.state_dir / f"{crawler_id}_state.pickle"
        }
        
        # 當前狀態
        self.current_state: Optional[CrawlerState] = None
        
        # 鎖，用於線程安全
        self.lock = threading.Lock()
        
        # 自動保存線程
        self.auto_save_thread = None
        self.stop_auto_save = threading.Event()
        
        # 載入初始狀態
        self._load_state()
        
        # 初始化並啟動自動保存
        if self.config.auto_save_enabled:
            self._start_auto_save()
        
        self.logger.info(f"爬蟲狀態管理器初始化完成，ID: {crawler_id}")
    
    def save_state(self, state_data: Dict[str, Any]) -> bool:
        """
        保存爬蟲狀態
        
        Args:
            state_data: 狀態數據字典
            
        Returns:
            是否成功保存
        """
        try:
            with self.lock:
                # 更新當前狀態
                if self.current_state is None:
                    self.current_state = CrawlerState(crawler_id=self.crawler_id)
                
                # 更新狀態數據
                self.current_state.data.update(state_data)
                self.current_state.timestamp = int(time.time())
                self.current_state.completed = False
                
                # 保存到文件
                success = self._save_to_storage()
                
                if success and self.config.backup_on_save:
                    self._create_backup()
                
                return success
        
        except Exception as e:
            self.logger.error(f"保存狀態失敗: {str(e)}")
            return False
    
    def _save_to_storage(self) -> bool:
        """
        保存狀態到所有配置的存儲媒介
        
        Returns:
            是否所有存儲都成功
        """
        if self.current_state is None:
            return False
        
        success = True
        state_dict = self.current_state.to_dict()
        
        # 保存到JSON
        if StorageFormat.JSON in self.config.storage_formats:
            try:
                with open(self.state_files[StorageFormat.JSON], "w", encoding=self.config.encoding) as f:
                    json.dump(state_dict, f, indent=2, ensure_ascii=False)
                self.logger.debug(f"已保存狀態到JSON: {self.state_files[StorageFormat.JSON]}")
            except Exception as e:
                self.logger.error(f"保存狀態到JSON失敗: {str(e)}")
                success = False
        
        # 保存到Pickle
        if StorageFormat.PICKLE in self.config.storage_formats:
            try:
                with open(self.state_files[StorageFormat.PICKLE], "wb") as f:
                    pickle.dump(state_dict, f)
                self.logger.debug(f"已保存狀態到Pickle: {self.state_files[StorageFormat.PICKLE]}")
            except Exception as e:
                self.logger.error(f"保存狀態到Pickle失敗: {str(e)}")
                success = False
        
        return success
    
    def _create_backup(self) -> bool:
        """
        創建狀態備份
        
        Returns:
            是否成功創建備份
        """
        try:
            # 生成備份文件名
            timestamp = int(time.time())
            
            # 備份所有格式的文件
            for fmt, file_path in self.state_files.items():
                if file_path.exists():
                    backup_file = self.backup_dir / f"{self.crawler_id}_state_{timestamp}.{fmt.value}"
                    shutil.copy2(file_path, backup_file)
                    self.logger.debug(f"已創建狀態備份: {backup_file}")
            
            # 清理過舊的備份
            self._cleanup_backups()
            
            return True
        
        except Exception as e:
            self.logger.error(f"創建備份失敗: {str(e)}")
            return False
    
    def _cleanup_backups(self):
        """清理過舊的備份文件"""
        try:
            # 按格式分組備份文件
            backup_files = {fmt: [] for fmt in StorageFormat}
            
            # 收集所有備份文件
            for file_path in self.backup_dir.glob(f"{self.crawler_id}_state_*"):
                for fmt in StorageFormat:
                    if file_path.suffix == f".{fmt.value}":
                        backup_files[fmt].append((file_path, file_path.stat().st_mtime))
                        break
            
            # 清理每種格式的過舊備份
            for fmt, files in backup_files.items():
                if len(files) > self.config.max_backups:
                    # 按修改時間排序
                    files.sort(key=lambda x: x[1])
                    
                    # 刪除最舊的備份
                    for i in range(len(files) - self.config.max_backups):
                        files[i][0].unlink()
                        self.logger.debug(f"已刪除過舊的備份: {files[i][0]}")
        
        except Exception as e:
            self.logger.error(f"清理備份失敗: {str(e)}")
    
    def get_state(self) -> Optional[CrawlerState]:
        """
        獲取當前爬蟲狀態
        
        Returns:
            當前狀態對象，如果沒有則返回None
        """
        with self.lock:
            return self.current_state
    
    def get_state_dict(self) -> Optional[Dict[str, Any]]:
        """
        獲取當前爬蟲狀態字典
        
        Returns:
            當前狀態字典，如果沒有則返回None
        """
        with self.lock:
            if self.current_state is None:
                return None
            return self.current_state.to_dict()
    
    def mark_completed(self) -> bool:
        """
        標記爬蟲任務已完成
        
        Returns:
            是否成功標記
        """
        try:
            with self.lock:
                if self.current_state is None:
                    self.current_state = CrawlerState(crawler_id=self.crawler_id)
                
                self.current_state.completed = True
                self.current_state.completion_time = int(time.time())
                
                return self._save_to_storage()
        
        except Exception as e:
            self.logger.error(f"標記完成失敗: {str(e)}")
            return False
    
    def is_completed(self) -> bool:
        """
        檢查爬蟲任務是否已完成
        
        Returns:
            是否已完成
        """
        with self.lock:
            if self.current_state is None:
                return False
            
            return self.current_state.completed
    
    def clear_state(self) -> bool:
        """
        清除爬蟲狀態
        
        Returns:
            是否成功清除
        """
        try:
            with self.lock:
                # 備份當前狀態
                if self.current_state is not None:
                    self._create_backup()
                
                # 清除狀態
                self.current_state = None
                
                # 刪除狀態文件
                for file_path in self.state_files.values():
                    if file_path.exists():
                        file_path.unlink()
                        self.logger.debug(f"已刪除狀態文件: {file_path}")
                
                return True
        
        except Exception as e:
            self.logger.error(f"清除狀態失敗: {str(e)}")
            return False
    
    def _load_state(self):
        """載入爬蟲狀態"""
        # 嘗試從各種存儲中載入
        loaded = False
        
        # 從JSON載入
        if not loaded and StorageFormat.JSON in self.config.storage_formats and self.state_files[StorageFormat.JSON].exists():
            try:
                with open(self.state_files[StorageFormat.JSON], "r", encoding=self.config.encoding) as f:
                    state_dict = json.load(f)
                self.current_state = CrawlerState.from_dict(state_dict)
                self.logger.info(f"已從JSON載入狀態: {self.state_files[StorageFormat.JSON]}")
                loaded = True
            except Exception as e:
                self.logger.error(f"從JSON載入狀態失敗: {str(e)}")
        
        # 從Pickle載入
        if not loaded and StorageFormat.PICKLE in self.config.storage_formats and self.state_files[StorageFormat.PICKLE].exists():
            try:
                with open(self.state_files[StorageFormat.PICKLE], "rb") as f:
                    state_dict = pickle.load(f)
                self.current_state = CrawlerState.from_dict(state_dict)
                self.logger.info(f"已從Pickle載入狀態: {self.state_files[StorageFormat.PICKLE]}")
                loaded = True
            except Exception as e:
                self.logger.error(f"從Pickle載入狀態失敗: {str(e)}")
        
        # 從備份中恢復
        if not loaded:
            # 查找最新的備份
            backup_files = []
            
            # 查找所有備份
            for fmt in StorageFormat:
                for file_path in self.backup_dir.glob(f"{self.crawler_id}_state_*.{fmt.value}"):
                    backup_files.append((file_path, file_path.stat().st_mtime))
            
            if backup_files:
                # 按修改時間排序
                backup_files.sort(key=lambda x: x[1], reverse=True)
                
                # 嘗試載入最新的備份
                try:
                    backup_file = backup_files[0][0]
                    if backup_file.suffix == ".json":
                        with open(backup_file, "r", encoding=self.config.encoding) as f:
                            state_dict = json.load(f)
                    else:
                        with open(backup_file, "rb") as f:
                            state_dict = pickle.load(f)
                    
                    self.current_state = CrawlerState.from_dict(state_dict)
                    self.logger.info(f"已從備份載入狀態: {backup_file}")
                    
                    # 保存到正常的狀態文件
                    self._save_to_storage()
                    
                    loaded = True
                except Exception as e:
                    self.logger.error(f"從備份載入狀態失敗: {str(e)}")
        
        if not loaded:
            self.logger.info("沒有找到有效的狀態，將創建新狀態")
            self.current_state = CrawlerState(crawler_id=self.crawler_id)
            self._save_to_storage()
    
    def _start_auto_save(self):
        """啟動自動保存線程"""
        if self.config.auto_save_enabled and self.auto_save_thread is None:
            self.stop_auto_save.clear()
            self.auto_save_thread = threading.Thread(target=self._auto_save_worker, daemon=True)
            self.auto_save_thread.start()
            self.logger.debug(f"已啟動自動保存線程，間隔: {self.config.auto_save_interval}秒")
    
    def _stop_auto_save(self):
        """停止自動保存線程"""
        if self.auto_save_thread is not None:
            self.stop_auto_save.set()
            self.auto_save_thread.join(timeout=1)
            self.auto_save_thread = None
            self.logger.debug("已停止自動保存線程")
    
    def _auto_save_worker(self):
        """自動保存工作線程"""
        while not self.stop_auto_save.is_set():
            try:
                # 等待指定時間
                if self.stop_auto_save.wait(self.config.auto_save_interval):
                    break
                
                # 保存當前狀態
                with self.lock:
                    if self.current_state is not None:
                        self._save_to_storage()
                        self.logger.debug("已自動保存狀態")
            
            except Exception as e:
                self.logger.error(f"自動保存狀態失敗: {str(e)}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self._stop_auto_save()
    
    def __del__(self):
        """析構函數，確保線程正確關閉"""
        self._stop_auto_save()
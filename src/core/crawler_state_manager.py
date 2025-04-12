#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬蟲狀態管理模組

負責管理爬蟲任務狀態，包括：
- 狀態追蹤
- 狀態恢復
- 狀態持久化
- 狀態統計
- 檢查點管理
"""

import json
import time
import pickle
import logging
import shutil
import threading
import os
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum, auto
from datetime import datetime

from src.core.utils.logger import setup_logger
from src.core.utils.error_handler import retry_on_error, handle_exception
from src.core.utils.logger import Logger
from src.core.utils.path_utils import PathUtils
from src.core.utils.config_utils import ConfigUtils
from src.core.utils.data_processor import SimpleDataProcessor as UtilsDataProcessor
from src.core.utils.error_handler import ErrorHandler


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


@dataclass
class TaskState:
    """任務狀態"""
    id: str
    url: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    error: Optional[str] = None
    result: Optional[Any] = None
    checkpoint: Optional[Dict] = None


class CrawlerStateManager:
    """爬蟲狀態管理器"""
    
    def __init__(self, state_file: str):
        """
        初始化狀態管理器
        
        Args:
            state_file: 狀態文件路徑
        """
        # 初始化工具類
        self.logger = setup_logger(
            name="state_manager",
            level_name="INFO",
            log_dir="logs",
            console_output=True,
            file_output=True
        )
        self.path_utils = PathUtils(self.logger)
        self.config_utils = ConfigUtils(self.logger)
        self.data_processor = UtilsDataProcessor(self.logger)
        self.error_handler = ErrorHandler(self.logger)
        
        # 設置狀態文件
        self.state_file = state_file
        self.state_dir = os.path.dirname(state_file)
        self.checkpoint_dir = os.path.join(self.state_dir, "checkpoints")
        
        # 創建目錄
        os.makedirs(self.state_dir, exist_ok=True)
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        # 初始化狀態
        self.states: Dict[str, TaskState] = {}
        self.state_lock = threading.Lock()
        
        # 加載狀態
        self._load_states()
        
        # 初始化統計信息
        self.stats = {
            "total_states": 0,
            "active_states": 0,
            "completed_states": 0,
            "failed_states": 0,
            "checkpoint_count": 0,
            "last_update": datetime.now()
        }
        
        # 更新統計信息
        self._update_stats()
    
    def _load_states(self):
        """加載狀態"""
        try:
            if self.path_utils.exists(self.state_file):
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                for state_data in data:
                    state = TaskState(
                        id=state_data["id"],
                        url=state_data["url"],
                        status=state_data["status"],
                        created_at=datetime.fromisoformat(state_data["created_at"]),
                        started_at=datetime.fromisoformat(state_data["started_at"]) if state_data.get("started_at") else None,
                        completed_at=datetime.fromisoformat(state_data["completed_at"]) if state_data.get("completed_at") else None,
                        retry_count=state_data.get("retry_count", 0),
                        error=state_data.get("error"),
                        result=state_data.get("result"),
                        checkpoint=state_data.get("checkpoint")
                    )
                    self.states[state.id] = state
                
                self.logger.info(f"已加載 {len(self.states)} 個狀態")
                
        except Exception as e:
            self.logger.error(f"加載狀態失敗: {str(e)}")
            self.error_handler.handle_error(e)
    
    def _save_states(self):
        """保存狀態"""
        try:
            data = []
            for state in self.states.values():
                state_data = {
                    "id": state.id,
                    "url": state.url,
                    "status": state.status,
                    "created_at": state.created_at.isoformat(),
                    "retry_count": state.retry_count
                }
                
                if state.started_at:
                    state_data["started_at"] = state.started_at.isoformat()
                if state.completed_at:
                    state_data["completed_at"] = state.completed_at.isoformat()
                if state.error:
                    state_data["error"] = state.error
                if state.result:
                    state_data["result"] = state.result
                if state.checkpoint:
                    state_data["checkpoint"] = state.checkpoint
                
                data.append(state_data)
            
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"已保存 {len(data)} 個狀態")
            
        except Exception as e:
            self.logger.error(f"保存狀態失敗: {str(e)}")
            self.error_handler.handle_error(e)
    
    def update_task_state(self, task_id: str, **kwargs) -> bool:
        """
        更新任務狀態
        
        Args:
            task_id: 任務ID
            **kwargs: 狀態更新參數
            
        Returns:
            是否更新成功
        """
        try:
            with self.state_lock:
                if task_id not in self.states:
                    self.logger.warning(f"任務狀態不存在: {task_id}")
                    return False
                
                state = self.states[task_id]
                
                # 更新狀態
                for key, value in kwargs.items():
                    if hasattr(state, key):
                        setattr(state, key, value)
                
                # 保存狀態
                self._save_states()
                
                # 更新統計信息
                self._update_stats()
                
                self.logger.info(f"已更新任務狀態: {task_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"更新任務狀態失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return False
    
    def get_task_state(self, task_id: str) -> Optional[TaskState]:
        """
        獲取任務狀態
        
        Args:
            task_id: 任務ID
            
        Returns:
            任務狀態
        """
        try:
            with self.state_lock:
                return self.states.get(task_id)
                
        except Exception as e:
            self.logger.error(f"獲取任務狀態失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return None
    
    def save_result(self, task_id: str, result: Any) -> bool:
        """
        保存任務結果
        
        Args:
            task_id: 任務ID
            result: 結果數據
            
        Returns:
            是否保存成功
        """
        try:
            with self.state_lock:
                if task_id not in self.states:
                    self.logger.warning(f"任務狀態不存在: {task_id}")
                    return False
                
                state = self.states[task_id]
                state.result = result
                state.completed_at = datetime.now()
                state.status = "completed"
                
                # 保存狀態
                self._save_states()
                
                # 更新統計信息
                self._update_stats()
                
                self.logger.info(f"已保存任務結果: {task_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"保存任務結果失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return False
    
    def save_checkpoint(self, task_id: str, checkpoint: Dict) -> bool:
        """
        保存檢查點
        
        Args:
            task_id: 任務ID
            checkpoint: 檢查點數據
            
        Returns:
            是否保存成功
        """
        try:
            with self.state_lock:
                if task_id not in self.states:
                    self.logger.warning(f"任務狀態不存在: {task_id}")
                    return False
                
                state = self.states[task_id]
                state.checkpoint = checkpoint
                
                # 保存檢查點文件
                checkpoint_file = self.path_utils.join_path(
                    self.checkpoint_dir,
                    f"{task_id}_{int(time.time())}.json"
                )
                
                with open(checkpoint_file, "w", encoding="utf-8") as f:
                    json.dump(checkpoint, f, ensure_ascii=False, indent=2)
                
                # 保存狀態
                self._save_states()
                
                # 更新統計信息
                self._update_stats()
                
                self.logger.info(f"已保存檢查點: {task_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"保存檢查點失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return False
    
    def clear_checkpoint(self, task_id: str) -> bool:
        """
        清除檢查點
        
        Args:
            task_id: 任務ID
            
        Returns:
            是否清除成功
        """
        try:
            with self.state_lock:
                if task_id not in self.states:
                    self.logger.warning(f"任務狀態不存在: {task_id}")
                    return False
                
                state = self.states[task_id]
                state.checkpoint = None
                
                # 刪除檢查點文件
                for file in self.path_utils.list_files(self.checkpoint_dir):
                    if file.startswith(task_id):
                        self.path_utils.remove_file(file)
                
                # 保存狀態
                self._save_states()
                
                # 更新統計信息
                self._update_stats()
                
                self.logger.info(f"已清除檢查點: {task_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"清除檢查點失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return False
    
    def get_all_states(self) -> List[TaskState]:
        """
        獲取所有狀態
        
        Returns:
            狀態列表
        """
        try:
            with self.state_lock:
                return list(self.states.values())
                
        except Exception as e:
            self.logger.error(f"獲取所有狀態失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return []
    
    def clear_all_states(self) -> bool:
        """
        清除所有狀態
        
        Returns:
            是否清除成功
        """
        try:
            with self.state_lock:
                self.states.clear()
                
                # 刪除狀態文件
                if self.path_utils.exists(self.state_file):
                    self.path_utils.remove_file(self.state_file)
                
                # 刪除檢查點目錄
                if self.path_utils.exists(self.checkpoint_dir):
                    self.path_utils.remove_dir(self.checkpoint_dir)
                    self.path_utils.ensure_dir(self.checkpoint_dir)
                
                # 更新統計信息
                self._update_stats()
                
                self.logger.info("已清除所有狀態")
                return True
                
        except Exception as e:
            self.logger.error(f"清除所有狀態失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return False
    
    def _update_stats(self):
        """更新統計信息"""
        try:
            with self.state_lock:
                self.stats["total_states"] = len(self.states)
                self.stats["active_states"] = len([s for s in self.states.values() if s.status == "running"])
                self.stats["completed_states"] = len([s for s in self.states.values() if s.status == "completed"])
                self.stats["failed_states"] = len([s for s in self.states.values() if s.status == "failed"])
                self.stats["checkpoint_count"] = len(self.path_utils.list_files(self.checkpoint_dir))
                self.stats["last_update"] = datetime.now()
                
        except Exception as e:
            self.logger.error(f"更新統計信息失敗: {str(e)}")
            self.error_handler.handle_error(e)
    
    def get_stats(self) -> Dict:
        """
        獲取統計信息
        
        Returns:
            Dict: 統計信息
        """
        try:
            stats = self.stats.copy()
            
            # 計算平均處理時間
            completed_states = [s for s in self.states.values() if s.status == "completed"]
            if completed_states:
                total_time = sum(
                    (s.completed_at - s.started_at).total_seconds()
                    for s in completed_states
                    if s.started_at and s.completed_at
                )
                stats["avg_processing_time"] = total_time / len(completed_states)
            else:
                stats["avg_processing_time"] = 0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"獲取統計信息失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return {}
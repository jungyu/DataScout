#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
本地存儲處理器模組
實現基於本地文件的數據存儲功能
"""

import json
import pickle
import csv
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_handler import StorageHandler
from ..config.storage_config import StorageConfig
from ..utils.storage_utils import StorageUtils


class LocalStorageHandler(StorageHandler):
    """本地存儲處理器"""
    
    def __init__(self, config: StorageConfig):
        """
        初始化本地存儲處理器
        
        Args:
            config: 存儲配置
        """
        super().__init__(config)
        self.storage_path = self.config.get_storage_path()
        self.backup_path = self.storage_path / "backups"
        self.storage_utils = StorageUtils()
        self.storage_utils.ensure_directory(self.storage_path)
        self.storage_utils.ensure_directory(self.backup_path)
        
        # 初始化狀態
        self.status['connected'] = True
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """
        保存單條數據
        
        Args:
            data: 要保存的數據
            
        Returns:
            bool: 是否成功
        """
        try:
            # 添加時間戳
            if self.config.timestamp_field not in data:
                data[self.config.timestamp_field] = self.get_timestamp()
            
            # 保存到文件
            file_path = self._get_file_path("json")
            success = self.storage_utils.save_json(data, file_path)
            
            # 更新狀態
            self._update_status("save_data", success)
            return success
            
        except Exception as e:
            self._update_status("save_data", False, e)
            return False
    
    def save_batch(self, data_list: List[Dict[str, Any]]) -> bool:
        """
        批量保存數據
        
        Args:
            data_list: 要保存的數據列表
            
        Returns:
            bool: 是否成功
        """
        try:
            # 添加時間戳
            for data in data_list:
                if self.config.timestamp_field not in data:
                    data[self.config.timestamp_field] = self.get_timestamp()
            
            # 保存到文件
            file_path = self._get_file_path("json")
            success = self.storage_utils.save_json(data_list, file_path)
            
            # 更新狀態
            self._update_status("save_batch", success)
            return success
            
        except Exception as e:
            self._update_status("save_batch", False, e)
            return False
    
    def load_data(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        加載數據
        
        Args:
            query: 查詢條件
            
        Returns:
            List[Dict[str, Any]]: 加載的數據列表
        """
        try:
            # 加載數據
            file_path = self._get_file_path("json")
            data = self.storage_utils.load_json(file_path)
            
            if not data:
                return []
            
            # 轉換為列表
            if isinstance(data, dict):
                data = [data]
            
            # 過濾數據
            if query:
                data = self._filter_data(data, query)
            
            # 更新狀態
            self._update_status("load_data", True)
            return data
            
        except Exception as e:
            self._update_status("load_data", False, e)
            return []
    
    def delete_data(self, query: Dict[str, Any]) -> bool:
        """
        刪除數據
        
        Args:
            query: 刪除條件
            
        Returns:
            bool: 是否成功
        """
        try:
            # 加載數據
            data = self.load_data()
            
            # 過濾數據
            filtered_data = [item for item in data if not self._match_query(item, query)]
            
            # 保存過濾後的數據
            file_path = self._get_file_path("json")
            success = self.storage_utils.save_json(filtered_data, file_path)
            
            # 更新狀態
            self._update_status("delete_data", success)
            return success
            
        except Exception as e:
            self._update_status("delete_data", False, e)
            return False
    
    def clear_data(self) -> bool:
        """
        清空數據
        
        Returns:
            bool: 是否成功
        """
        try:
            # 清空數據
            file_path = self._get_file_path("json")
            success = self.storage_utils.save_json([], file_path)
            
            # 更新狀態
            self._update_status("clear_data", success)
            return success
            
        except Exception as e:
            self._update_status("clear_data", False, e)
            return False
    
    def get_data_count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """
        獲取數據數量
        
        Args:
            query: 查詢條件
            
        Returns:
            int: 數據數量
        """
        try:
            # 加載數據
            data = self.load_data()
            
            # 過濾數據
            if query:
                data = self._filter_data(data, query)
            
            # 更新狀態
            self._update_status("get_data_count", True)
            return len(data)
            
        except Exception as e:
            self._update_status("get_data_count", False, e)
            return 0
    
    def create_backup(self) -> bool:
        """
        創建備份
        
        Returns:
            bool: 是否成功
        """
        try:
            if not self.config.backup_enabled:
                return False
            
            # 創建備份
            backup_path = self.storage_utils.create_backup(
                self.storage_path,
                self.backup_path,
                "local_backup"
            )
            
            # 清理舊備份
            self._cleanup_old_backups()
            
            # 更新狀態
            success = backup_path is not None
            self._update_status("create_backup", success)
            return success
            
        except Exception as e:
            self._update_status("create_backup", False, e)
            return False
    
    def restore_backup(self, backup_id: str) -> bool:
        """
        恢復備份
        
        Args:
            backup_id: 備份ID
            
        Returns:
            bool: 是否成功
        """
        try:
            # 獲取備份路徑
            backup_path = self.backup_path / backup_id
            if not backup_path.exists():
                return False
            
            # 恢復備份
            success = self.storage_utils.restore_backup(backup_path, self.storage_path)
            
            # 更新狀態
            self._update_status("restore_backup", success)
            return success
            
        except Exception as e:
            self._update_status("restore_backup", False, e)
            return False
    
    def list_backups(self) -> List[str]:
        """
        列出所有備份
        
        Returns:
            List[str]: 備份ID列表
        """
        try:
            # 列出備份
            backups = self.storage_utils.list_backups(self.backup_path, "local_backup")
            
            # 更新狀態
            self._update_status("list_backups", True)
            return [str(backup['path'].name) for backup in backups]
            
        except Exception as e:
            self._update_status("list_backups", False, e)
            return []
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        刪除備份
        
        Args:
            backup_id: 備份ID
            
        Returns:
            bool: 是否成功
        """
        try:
            # 獲取備份路徑
            backup_path = self.backup_path / backup_id
            if not backup_path.exists():
                return False
            
            # 刪除備份
            success = self.storage_utils.delete_backup(backup_path)
            
            # 更新狀態
            self._update_status("delete_backup", success)
            return success
            
        except Exception as e:
            self._update_status("delete_backup", False, e)
            return False
    
    def _get_file_path(self, fmt: str) -> Path:
        """
        獲取文件路徑
        
        Args:
            fmt: 文件格式
            
        Returns:
            Path: 文件路徑
        """
        return self.storage_path / f"data.{fmt}"
    
    def _filter_data(self, data: List[Dict[str, Any]], query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        過濾數據
        
        Args:
            data: 數據列表
            query: 查詢條件
            
        Returns:
            List[Dict[str, Any]]: 過濾後的數據列表
        """
        return [item for item in data if self._match_query(item, query)]
    
    def _match_query(self, data: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """
        匹配查詢條件
        
        Args:
            data: 數據
            query: 查詢條件
            
        Returns:
            bool: 是否匹配
        """
        for key, value in query.items():
            if key not in data or data[key] != value:
                return False
        return True
    
    def _cleanup_old_backups(self) -> None:
        """清理舊備份"""
        try:
            # 列出備份
            backups = self.storage_utils.list_backups(self.backup_path, "local_backup")
            
            # 如果超過最大備份數，刪除舊備份
            if len(backups) > self.config.max_backups:
                for backup in backups[self.config.max_backups:]:
                    self.storage_utils.delete_backup(backup['path'])
        except Exception as e:
            self.log_error(f"清理舊備份失敗: {str(e)}") 
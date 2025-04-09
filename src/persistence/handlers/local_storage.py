#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
本地存儲處理器模組
實現本地文件存儲功能
"""

import json
import pickle
import csv
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from ..config.storage_config import StorageConfig
from .base_handler import StorageHandler


class LocalStorageHandler(StorageHandler):
    """本地存儲處理器"""
    
    def __init__(self, config: StorageConfig):
        """初始化本地存儲處理器"""
        super().__init__(config)
        self.storage_path = config.get_storage_path()
        self.backup_path = self.storage_path / "backups"
        self.backup_path.mkdir(parents=True, exist_ok=True)
        self.data_cache: List[Dict[str, Any]] = []
        self._load_data()
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """保存單條數據"""
        try:
            # 添加時間戳
            if self.config.timestamp_field not in data:
                data[self.config.timestamp_field] = time.time()
            
            # 更新緩存
            self.data_cache.append(data)
            
            # 保存到文件
            return self._save_to_storage()
            
        except Exception as e:
            print(f"保存數據失敗: {str(e)}")
            return False
    
    def save_batch(self, data_list: List[Dict[str, Any]]) -> bool:
        """批量保存數據"""
        try:
            # 添加時間戳
            for data in data_list:
                if self.config.timestamp_field not in data:
                    data[self.config.timestamp_field] = time.time()
            
            # 更新緩存
            self.data_cache.extend(data_list)
            
            # 保存到文件
            return self._save_to_storage()
            
        except Exception as e:
            print(f"批量保存數據失敗: {str(e)}")
            return False
    
    def load_data(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """加載數據"""
        try:
            if query is None:
                return self.data_cache
            
            # 過濾數據
            return [data for data in self.data_cache if all(
                data.get(k) == v for k, v in query.items()
            )]
            
        except Exception as e:
            print(f"加載數據失敗: {str(e)}")
            return []
    
    def delete_data(self, query: Dict[str, Any]) -> bool:
        """刪除數據"""
        try:
            # 過濾數據
            self.data_cache = [data for data in self.data_cache if not all(
                data.get(k) == v for k, v in query.items()
            )]
            
            # 保存到文件
            return self._save_to_storage()
            
        except Exception as e:
            print(f"刪除數據失敗: {str(e)}")
            return False
    
    def clear_data(self) -> bool:
        """清空數據"""
        try:
            self.data_cache = []
            return self._save_to_storage()
        except Exception as e:
            print(f"清空數據失敗: {str(e)}")
            return False
    
    def get_data_count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """獲取數據數量"""
        return len(self.load_data(query))
    
    def create_backup(self) -> bool:
        """創建備份"""
        try:
            # 生成備份ID
            backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backup_path / backup_id
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 複製文件
            for format in self.config.local_formats:
                src_file = self.storage_path / f"data.{format}"
                if src_file.exists():
                    shutil.copy2(src_file, backup_dir / f"data.{format}")
            
            # 清理舊備份
            self._cleanup_old_backups()
            
            return True
            
        except Exception as e:
            print(f"創建備份失敗: {str(e)}")
            return False
    
    def restore_backup(self, backup_id: str) -> bool:
        """恢復備份"""
        try:
            backup_dir = self.backup_path / backup_id
            if not backup_dir.exists():
                raise ValueError(f"備份不存在: {backup_id}")
            
            # 複製文件
            for format in self.config.local_formats:
                src_file = backup_dir / f"data.{format}"
                if src_file.exists():
                    shutil.copy2(src_file, self.storage_path / f"data.{format}")
            
            # 重新加載數據
            self._load_data()
            
            return True
            
        except Exception as e:
            print(f"恢復備份失敗: {str(e)}")
            return False
    
    def list_backups(self) -> List[str]:
        """列出所有備份"""
        try:
            return [d.name for d in self.backup_path.iterdir() if d.is_dir()]
        except Exception as e:
            print(f"列出備份失敗: {str(e)}")
            return []
    
    def delete_backup(self, backup_id: str) -> bool:
        """刪除備份"""
        try:
            backup_dir = self.backup_path / backup_id
            if not backup_dir.exists():
                raise ValueError(f"備份不存在: {backup_id}")
            
            shutil.rmtree(backup_dir)
            return True
            
        except Exception as e:
            print(f"刪除備份失敗: {str(e)}")
            return False
    
    def _save_to_storage(self) -> bool:
        """保存數據到存儲"""
        try:
            # 保存為 JSON
            if "json" in self.config.local_formats:
                json_file = self.storage_path / "data.json"
                with json_file.open("w", encoding=self.config.encoding) as f:
                    json.dump(self.data_cache, f, ensure_ascii=False, indent=self.config.local_indent)
            
            # 保存為 Pickle
            if "pickle" in self.config.local_formats:
                pickle_file = self.storage_path / "data.pickle"
                with pickle_file.open("wb") as f:
                    pickle.dump(self.data_cache, f)
            
            # 保存為 CSV
            if "csv" in self.config.local_formats and self.data_cache:
                csv_file = self.storage_path / "data.csv"
                headers = self.config.local_csv_headers or list(self.data_cache[0].keys())
                with csv_file.open("w", encoding=self.config.encoding, newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(self.data_cache)
            
            # 創建備份
            if self.config.backup_enabled:
                self.create_backup()
            
            return True
            
        except Exception as e:
            print(f"保存到存儲失敗: {str(e)}")
            return False
    
    def _load_data(self) -> None:
        """從存儲加載數據"""
        try:
            # 嘗試從 JSON 加載
            json_file = self.storage_path / "data.json"
            if json_file.exists():
                with json_file.open("r", encoding=self.config.encoding) as f:
                    self.data_cache = json.load(f)
                return
            
            # 嘗試從 Pickle 加載
            pickle_file = self.storage_path / "data.pickle"
            if pickle_file.exists():
                with pickle_file.open("rb") as f:
                    self.data_cache = pickle.load(f)
                return
            
            # 嘗試從 CSV 加載
            csv_file = self.storage_path / "data.csv"
            if csv_file.exists():
                with csv_file.open("r", encoding=self.config.encoding, newline="") as f:
                    reader = csv.DictReader(f)
                    self.data_cache = list(reader)
                return
            
        except Exception as e:
            print(f"從存儲加載數據失敗: {str(e)}")
            self.data_cache = []
    
    def _cleanup_old_backups(self) -> None:
        """清理舊備份"""
        try:
            backups = sorted(self.list_backups(), reverse=True)
            if len(backups) > self.config.max_backups:
                for backup_id in backups[self.config.max_backups:]:
                    self.delete_backup(backup_id)
                    
        except Exception as e:
            print(f"清理舊備份失敗: {str(e)}")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if self.config.auto_save:
            self._save_to_storage() 
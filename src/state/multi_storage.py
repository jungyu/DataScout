#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import pickle
import logging
import shutil
import threading
import csv
from typing import Dict, List, Optional, Any, Union

from ..utils.logger import setup_logger
from ..utils.error_handler import retry_on_exception, handle_exception


class MultiStorageManager:
    """
    多重儲存管理器，提供多種儲存方式，增強數據可靠性。
    支持JSON、Pickle、本地文件系統等多種存儲媒介。
    """
    
    def __init__(
        self,
        storage_id: str,
        config: Dict = None,
        storage_dir: str = "data",
        log_level: int = logging.INFO
    ):
        """
        初始化多重儲存管理器
        
        Args:
            storage_id: 存儲ID，用於標識不同的存儲任務
            config: 配置字典
            storage_dir: 存儲目錄
            log_level: 日誌級別
        """
        self.logger = setup_logger(__name__, log_level)
        self.storage_id = storage_id
        self.config = config or {}
        self.storage_dir = storage_dir
        
        # 確保存儲目錄存在
        os.makedirs(storage_dir, exist_ok=True)
        
        # 存儲媒介
        self.storage_modes = self.config.get("storage_modes", ["json", "pickle", "csv"])
        
        # JSON設置
        self.json_file = os.path.join(storage_dir, f"{storage_id}.json")
        
        # Pickle設置
        self.pickle_file = os.path.join(storage_dir, f"{storage_id}.pickle")
        
        # CSV設置
        self.csv_file = os.path.join(storage_dir, f"{storage_id}.csv")
        self.csv_headers = self.config.get("csv_headers", [])
        
        # 備份設置
        self.backup_dir = os.path.join(storage_dir, "backups")
        os.makedirs(self.backup_dir, exist_ok=True)
        self.max_backups = self.config.get("max_backups", 5)
        self.backup_on_save = self.config.get("backup_on_save", True)
        
        # 數據緩存
        self.data_cache = []
        
        # 鎖，用於線程安全
        self.lock = threading.Lock()
        
        # 自動保存設置
        self.auto_save_interval = self.config.get("auto_save_interval", 300)  # 秒
        self.auto_save_enabled = self.config.get("auto_save_enabled", True)
        self.auto_save_thread = None
        self.stop_auto_save = threading.Event()
        
        # 載入現有數據
        self._load_data()
        
        # 啟動自動保存
        if self.auto_save_enabled:
            self._start_auto_save()
        
        self.logger.info(f"多重儲存管理器初始化完成，ID: {storage_id}")
    
    def save_data(self, data: Dict) -> bool:
        """
        保存數據
        
        Args:
            data: 數據字典
            
        Returns:
            是否成功保存
        """
        try:
            with self.lock:
                # 添加時間戳
                if "timestamp" not in data:
                    data["timestamp"] = int(time.time())
                
                # 添加到緩存
                self.data_cache.append(data)
                
                # 保存到文件
                success = self._save_to_storage()
                
                if success and self.backup_on_save:
                    self._create_backup()
                
                return success
        
        except Exception as e:
            self.logger.error(f"保存數據失敗: {str(e)}")
            return False
    
    def save_batch(self, data_list: List[Dict]) -> bool:
        """
        批量保存數據
        
        Args:
            data_list: 數據字典列表
            
        Returns:
            是否成功保存
        """
        try:
            with self.lock:
                # 添加時間戳
                timestamp = int(time.time())
                for data in data_list:
                    if "timestamp" not in data:
                        data["timestamp"] = timestamp
                
                # 添加到緩存
                self.data_cache.extend(data_list)
                
                # 保存到文件
                success = self._save_to_storage()
                
                if success and self.backup_on_save:
                    self._create_backup()
                
                return success
        
        except Exception as e:
            self.logger.error(f"批量保存數據失敗: {str(e)}")
            return False
    
    def get_data(self) -> List[Dict]:
        """
        獲取所有數據
        
        Returns:
            數據列表
        """
        with self.lock:
            return self.data_cache.copy()
    
    def get_data_by_filter(self, filter_func: callable) -> List[Dict]:
        """
        獲取符合過濾條件的數據
        
        Args:
            filter_func: 過濾函數，接受一個數據字典，返回布爾值
            
        Returns:
            過濾後的數據列表
        """
        with self.lock:
            return [data for data in self.data_cache if filter_func(data)]
    
    def clear_data(self) -> bool:
        """
        清除所有數據
        
        Returns:
            是否成功清除
        """
        try:
            with self.lock:
                # 備份當前數據
                if self.data_cache:
                    self._create_backup()
                
                # 清空緩存
                self.data_cache = []
                
                # 清除存儲文件
                if "json" in self.storage_modes and os.path.exists(self.json_file):
                    os.remove(self.json_file)
                
                if "pickle" in self.storage_modes and os.path.exists(self.pickle_file):
                    os.remove(self.pickle_file)
                
                if "csv" in self.storage_modes and os.path.exists(self.csv_file):
                    os.remove(self.csv_file)
                
                return True
        
        except Exception as e:
            self.logger.error(f"清除數據失敗: {str(e)}")
            return False
    
    def _save_to_storage(self) -> bool:
        """
        保存數據到所有配置的存儲媒介
        
        Returns:
            是否所有存儲都成功
        """
        success = True
        
        # 保存到JSON
        if "json" in self.storage_modes:
            try:
                with open(self.json_file, "w", encoding="utf-8") as f:
                    json.dump(self.data_cache, f, indent=2)
                self.logger.debug(f"已保存數據到JSON: {self.json_file}")
            except Exception as e:
                self.logger.error(f"保存數據到JSON失敗: {str(e)}")
                success = False
        
        # 保存到Pickle
        if "pickle" in self.storage_modes:
            try:
                with open(self.pickle_file, "wb") as f:
                    pickle.dump(self.data_cache, f)
                self.logger.debug(f"已保存數據到Pickle: {self.pickle_file}")
            except Exception as e:
                self.logger.error(f"保存數據到Pickle失敗: {str(e)}")
                success = False
        
        # 保存到CSV
        if "csv" in self.storage_modes:
            try:
                # 確定CSV標頭
                headers = self.csv_headers
                if not headers and self.data_cache:
                    # 從數據中提取所有可能的字段
                    headers = set()
                    for data in self.data_cache:
                        headers.update(data.keys())
                    headers = sorted(list(headers))
                
                with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(self.data_cache)
                
                self.logger.debug(f"已保存數據到CSV: {self.csv_file}")
            except Exception as e:
                self.logger.error(f"保存數據到CSV失敗: {str(e)}")
                success = False
        
        return success
    
    def _create_backup(self) -> bool:
        """
        創建數據備份
        
        Returns:
            是否成功創建備份
        """
        try:
            # 生成備份文件名
            timestamp = int(time.time())
            
            # 備份JSON文件
            if "json" in self.storage_modes and os.path.exists(self.json_file):
                backup_file = os.path.join(self.backup_dir, f"{self.storage_id}_{timestamp}.json")
                shutil.copy2(self.json_file, backup_file)
                self.logger.debug(f"已創建數據備份: {backup_file}")
            
            # 備份Pickle文件
            if "pickle" in self.storage_modes and os.path.exists(self.pickle_file):
                backup_file = os.path.join(self.backup_dir, f"{self.storage_id}_{timestamp}.pickle")
                shutil.copy2(self.pickle_file, backup_file)
                self.logger.debug(f"已創建數據備份: {backup_file}")
            
            # 備份CSV文件
            if "csv" in self.storage_modes and os.path.exists(self.csv_file):
                backup_file = os.path.join(self.backup_dir, f"{self.storage_id}_{timestamp}.csv")
                shutil.copy2(self.csv_file, backup_file)
                self.logger.debug(f"已創建數據備份: {backup_file}")
            
            # 清理過舊的備份
            self._cleanup_backups()
            
            return True
        
        except Exception as e:
            self.logger.error(f"創建備份失敗: {str(e)}")
            return False
    
    def _cleanup_backups(self):
        """清理過舊的備份文件"""
        try:
            # 對每種存儲類型分別清理
            for ext in ["json", "pickle", "csv"]:
                # 獲取備份文件
                backup_files = []
                for file in os.listdir(self.backup_dir):
                    if file.startswith(f"{self.storage_id}_") and file.endswith(f".{ext}"):
                        file_path = os.path.join(self.backup_dir, file)
                        backup_files.append((file_path, os.path.getmtime(file_path)))
                
                if not backup_files:
                    continue
                
                # 按修改時間排序
                backup_files.sort(key=lambda x: x[1], reverse=True)
                latest_backup = backup_files[0][0]
                
                # 嘗試載入最新的備份
                try:
                    if ext == "json":
                        with open(latest_backup, "r", encoding="utf-8") as f:
                            self.data_cache = json.load(f)
                    elif ext == "pickle":
                        with open(latest_backup, "rb") as f:
                            self.data_cache = pickle.load(f)
                    elif ext == "csv":
                        self.data_cache = []
                        with open(latest_backup, "r", newline="", encoding="utf-8") as f:
                            reader = csv.DictReader(f)
                            for row in reader:
                                # 轉換數據類型
                                data = {}
                                for key, value in row.items():
                                    # 嘗試轉換為數字或布爾值
                                    if value.lower() == "true":
                                        data[key] = True
                                    elif value.lower() == "false":
                                        data[key] = False
                                    else:
                                        try:
                                            # 嘗試轉換為整數或浮點數
                                            if value.isdigit():
                                                data[key] = int(value)
                                            else:
                                                data[key] = float(value)
                                        except ValueError:
                                            data[key] = value
                                
                                self.data_cache.append(data)
                    
                    self.logger.info(f"已從備份載入數據: {latest_backup}, {len(self.data_cache)} 條記錄")
                    loaded = True
                    backup_found = True
                    
                    # 保存到正常的存儲文件
                    self._save_to_storage()
                
                except Exception as e:
                    self.logger.error(f"從備份載入數據失敗: {str(e)}")
        
        # 初始化空緩存
        if not loaded:
            self.data_cache = []
            self.logger.info("沒有找到有效的數據，初始化空緩存")
    
    def _start_auto_save(self):
        """啟動自動保存線程"""
        if self.auto_save_enabled and self.auto_save_thread is None:
            self.stop_auto_save.clear()
            self.auto_save_thread = threading.Thread(target=self._auto_save_worker, daemon=True)
            self.auto_save_thread.start()
            self.logger.debug(f"已啟動自動保存線程，間隔: {self.auto_save_interval}秒")
    
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
                if self.stop_auto_save.wait(self.auto_save_interval):
                    break
                
                # 保存當前數據
                with self.lock:
                    if self.data_cache:
                        self._save_to_storage()
                        self.logger.debug("已自動保存數據")
            
            except Exception as e:
                self.logger.error(f"自動保存數據失敗: {str(e)}")
    
    def __del__(self):
        """析構函數，確保線程正確關閉"""
        self._stop_auto_save()
    
    def export_to_json(self, file_path: str = None) -> bool:
        """
        導出數據到JSON文件
        
        Args:
            file_path: 導出文件路徑，為None時使用默認路徑
            
        Returns:
            是否成功導出
        """
        if file_path is None:
            file_path = os.path.join(self.storage_dir, "exports", f"{self.storage_id}_export.json")
        
        try:
            # 確保導出目錄存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with self.lock:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.data_cache, f, indent=2)
            
            self.logger.info(f"已導出數據到JSON: {file_path}, {len(self.data_cache)} 條記錄")
            return True
        
        except Exception as e:
            self.logger.error(f"導出數據到JSON失敗: {str(e)}")
            return False
    
    def export_to_csv(self, file_path: str = None, headers: List[str] = None) -> bool:
        """
        導出數據到CSV文件
        
        Args:
            file_path: 導出文件路徑，為None時使用默認路徑
            headers: 字段標頭，為None時自動生成
            
        Returns:
            是否成功導出
        """
        if file_path is None:
            file_path = os.path.join(self.storage_dir, "exports", f"{self.storage_id}_export.csv")
        
        try:
            # 確保導出目錄存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with self.lock:
                # 確定CSV標頭
                if headers is None:
                    headers = self.csv_headers
                
                if not headers and self.data_cache:
                    # 從數據中提取所有可能的字段
                    headers_set = set()
                    for data in self.data_cache:
                        headers_set.update(data.keys())
                    headers = sorted(list(headers_set))
                
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(self.data_cache)
            
            self.logger.info(f"已導出數據到CSV: {file_path}, {len(self.data_cache)} 條記錄")
            return True
        
        except Exception as e:
            self.logger.error(f"導出數據到CSV失敗: {str(e)}")
            return False
    
    def get_storage_info(self) -> Dict:
        """
        獲取存儲信息
        
        Returns:
            存儲信息字典
        """
        info = {
            "storage_id": self.storage_id,
            "record_count": len(self.data_cache),
            "storage_modes": self.storage_modes,
            "files": {}
        }
        
        # 檢查各個存儲文件
        if "json" in self.storage_modes:
            if os.path.exists(self.json_file):
                info["files"]["json"] = {
                    "path": self.json_file,
                    "size": os.path.getsize(self.json_file),
                    "last_modified": os.path.getmtime(self.json_file)
                }
        
        if "pickle" in self.storage_modes:
            if os.path.exists(self.pickle_file):
                info["files"]["pickle"] = {
                    "path": self.pickle_file,
                    "size": os.path.getsize(self.pickle_file),
                    "last_modified": os.path.getmtime(self.pickle_file)
                }
        
        if "csv" in self.storage_modes:
            if os.path.exists(self.csv_file):
                info["files"]["csv"] = {
                    "path": self.csv_file,
                    "size": os.path.getsize(self.csv_file),
                    "last_modified": os.path.getmtime(self.csv_file)
                }
        
        # 備份信息
        backup_count = 0
        backup_size = 0
        
        for ext in ["json", "pickle", "csv"]:
            for file in os.listdir(self.backup_dir):
                if file.startswith(f"{self.storage_id}_") and file.endswith(f".{ext}"):
                    backup_count += 1
                    file_path = os.path.join(self.backup_dir, file)
                    backup_size += os.path.getsize(file_path)
        
        info["backups"] = {
            "count": backup_count,
            "total_size": backup_size
        }
        
        return info
                    if file.startswith(f"{self.storage_id}_") and file.endswith(f".{ext}"):
                        file_path = os.path.join(self.backup_dir, file)
                        backup_files.append((file_path, os.path.getmtime(file_path)))
                
                # 清理過舊的備份
                if len(backup_files) > self.max_backups:
                    # 按修改時間排序
                    backup_files.sort(key=lambda x: x[1])
                    
                    # 刪除最舊的備份
                    for i in range(len(backup_files) - self.max_backups):
                        os.remove(backup_files[i][0])
                        self.logger.debug(f"已刪除過舊的備份: {backup_files[i][0]}")
        
        except Exception as e:
            self.logger.error(f"清理備份失敗: {str(e)}")
    
    def _load_data(self):
        """載入數據"""
        # 嘗試從各種存儲中載入
        loaded = False
        
        # 從JSON載入
        if not loaded and "json" in self.storage_modes and os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    self.data_cache = json.load(f)
                self.logger.info(f"已從JSON載入數據: {self.json_file}, {len(self.data_cache)} 條記錄")
                loaded = True
            except Exception as e:
                self.logger.error(f"從JSON載入數據失敗: {str(e)}")
        
        # 從Pickle載入
        if not loaded and "pickle" in self.storage_modes and os.path.exists(self.pickle_file):
            try:
                with open(self.pickle_file, "rb") as f:
                    self.data_cache = pickle.load(f)
                self.logger.info(f"已從Pickle載入數據: {self.pickle_file}, {len(self.data_cache)} 條記錄")
                loaded = True
            except Exception as e:
                self.logger.error(f"從Pickle載入數據失敗: {str(e)}")
        
        # 從CSV載入
        if not loaded and "csv" in self.storage_modes and os.path.exists(self.csv_file):
            try:
                self.data_cache = []
                with open(self.csv_file, "r", newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # 轉換數據類型
                        data = {}
                        for key, value in row.items():
                            # 嘗試轉換為數字或布爾值
                            try:
                                if value.lower() == "true":
                                    data[key] = True
                                elif value.lower() == "false":
                                    data[key] = False
                                elif value.isdigit():
                                    data[key] = int(value)
                                elif value.replace(".", "", 1).isdigit():
                                    data[key] = float(value)
                                else:
                                    data[key] = value
                            except (AttributeError, ValueError):
                                data[key] = value
                        
                        self.data_cache.append(data)
                
                self.logger.info(f"已從CSV載入數據: {self.csv_file}, {len(self.data_cache)} 條記錄")
                loaded = True
            except Exception as e:
                self.logger.error(f"從CSV載入數據失敗: {str(e)}")
        
        # 初始化空緩存
        if not loaded:
            self.data_cache = []
            self.logger.info("沒有找到有效的數據，初始化空緩存")
    
    def __enter__(self):
        """上下文管理器進入方法"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出方法"""
        self._stop_auto_save()
        
        if exc_type is not None:
            # 發生異常時，嘗試保存數據
            try:
                self._save_to_storage()
                self.logger.info("已在異常退出時保存數據")
            except Exception as e:
                self.logger.error(f"異常退出時保存數據失敗: {str(e)}")
            return False  # 不處理異常，向上傳播
        
        # 正常退出時保存數據
        try:
            self._save_to_storage()
            self.logger.info("已在正常退出時保存數據")
        except Exception as e:
            self.logger.error(f"正常退出時保存數據失敗: {str(e)}")
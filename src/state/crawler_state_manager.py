#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import pickle
import logging
import shutil
import threading
from typing import Dict, List, Optional, Any, Union

from ..utils.logger import setup_logger
from ..utils.error_handler import retry_on_exception, handle_exception


class CrawlerStateManager:
    """
    爬蟲狀態管理器，負責爬蟲狀態的保存、載入和管理，
    支持任務的中斷和恢復，以及多重備份策略。
    """
    
    def __init__(
        self,
        crawler_id: str,
        config: Dict = None,
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
        self.config = config or {}
        self.state_dir = state_dir
        
        # 確保狀態目錄存在
        os.makedirs(state_dir, exist_ok=True)
        
        # 備份目錄
        self.backup_dir = os.path.join(state_dir, "backups")
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 狀態文件路徑
        self.state_file = os.path.join(state_dir, f"{crawler_id}_state.json")
        self.state_pickle_file = os.path.join(state_dir, f"{crawler_id}_state.pickle")
        
        # 當前狀態
        self.current_state = None
        
        # 自動保存設置
        self.auto_save_interval = self.config.get("auto_save_interval", 60)  # 秒
        self.auto_save_enabled = self.config.get("auto_save_enabled", True)
        
        # 備份設置
        self.max_backups = self.config.get("max_backups", 5)
        self.backup_on_save = self.config.get("backup_on_save", True)
        
        # 多存儲策略
        self.storage_modes = self.config.get("storage_modes", ["json", "pickle"])
        
        # 鎖，用於線程安全
        self.lock = threading.Lock()
        
        # 自動保存線程
        self.auto_save_thread = None
        self.stop_auto_save = threading.Event()
        
        # 載入初始狀態
        self._load_state()
        
        # 初始化並啟動自動保存
        if self.auto_save_enabled:
            self._start_auto_save()
        
        self.logger.info(f"爬蟲狀態管理器初始化完成，ID: {crawler_id}")
    
    def save_state(self, state: Dict) -> bool:
        """
        保存爬蟲狀態
        
        Args:
            state: 狀態字典
            
        Returns:
            是否成功保存
        """
        try:
            with self.lock:
                # 更新當前狀態
                if self.current_state is None:
                    self.current_state = {}
                
                # 添加時間戳
                state["timestamp"] = int(time.time())
                state["completed"] = False
                
                # 更新當前狀態
                self.current_state.update(state)
                
                # 保存到文件
                success = self._save_to_storage()
                
                if success and self.backup_on_save:
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
        success = True
        
        # 保存到JSON
        if "json" in self.storage_modes:
            try:
                with open(self.state_file, "w", encoding="utf-8") as f:
                    json.dump(self.current_state, f, indent=2)
                self.logger.debug(f"已保存狀態到JSON: {self.state_file}")
            except Exception as e:
                self.logger.error(f"保存狀態到JSON失敗: {str(e)}")
                success = False
        
        # 保存到Pickle
        if "pickle" in self.storage_modes:
            try:
                with open(self.state_pickle_file, "wb") as f:
                    pickle.dump(self.current_state, f)
                self.logger.debug(f"已保存狀態到Pickle: {self.state_pickle_file}")
            except Exception as e:
                self.logger.error(f"保存狀態到Pickle失敗: {str(e)}")
                success = False
        
        # 其他存儲方式可以在這裡添加
        
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
            backup_file = os.path.join(self.backup_dir, f"{self.crawler_id}_state_{timestamp}.json")
            
            # 備份JSON文件
            if os.path.exists(self.state_file):
                shutil.copy2(self.state_file, backup_file)
                self.logger.debug(f"已創建狀態備份: {backup_file}")
            
            # 備份Pickle文件
            if os.path.exists(self.state_pickle_file):
                pickle_backup_file = os.path.join(self.backup_dir, f"{self.crawler_id}_state_{timestamp}.pickle")
                shutil.copy2(self.state_pickle_file, pickle_backup_file)
                self.logger.debug(f"已創建狀態備份: {pickle_backup_file}")
            
            # 清理過舊的備份
            self._cleanup_backups()
            
            return True
        
        except Exception as e:
            self.logger.error(f"創建備份失敗: {str(e)}")
            return False
    
    def _cleanup_backups(self):
        """清理過舊的備份文件"""
        try:
            # 獲取JSON備份文件
            json_backups = []
            for file in os.listdir(self.backup_dir):
                if file.startswith(f"{self.crawler_id}_state_") and file.endswith(".json"):
                    file_path = os.path.join(self.backup_dir, file)
                    json_backups.append((file_path, os.path.getmtime(file_path)))
            
            # 清理過舊的JSON備份
            if len(json_backups) > self.max_backups:
                # 按修改時間排序
                json_backups.sort(key=lambda x: x[1])
                
                # 刪除最舊的備份
                for i in range(len(json_backups) - self.max_backups):
                    os.remove(json_backups[i][0])
                    self.logger.debug(f"已刪除過舊的備份: {json_backups[i][0]}")
            
            # 獲取Pickle備份文件
            pickle_backups = []
            for file in os.listdir(self.backup_dir):
                if file.startswith(f"{self.crawler_id}_state_") and file.endswith(".pickle"):
                    file_path = os.path.join(self.backup_dir, file)
                    pickle_backups.append((file_path, os.path.getmtime(file_path)))
            
            # 清理過舊的Pickle備份
            if len(pickle_backups) > self.max_backups:
                # 按修改時間排序
                pickle_backups.sort(key=lambda x: x[1])
                
                # 刪除最舊的備份
                for i in range(len(pickle_backups) - self.max_backups):
                    os.remove(pickle_backups[i][0])
                    self.logger.debug(f"已刪除過舊的備份: {pickle_backups[i][0]}")
        
        except Exception as e:
            self.logger.error(f"清理備份失敗: {str(e)}")
    
    def get_state(self) -> Optional[Dict]:
        """
        獲取當前爬蟲狀態
        
        Returns:
            當前狀態字典，如果沒有則返回None
        """
        with self.lock:
            return self.current_state
    
    def mark_completed(self) -> bool:
        """
        標記爬蟲任務已完成
        
        Returns:
            是否成功標記
        """
        try:
            with self.lock:
                if self.current_state is None:
                    self.current_state = {}
                
                self.current_state["completed"] = True
                self.current_state["completion_time"] = int(time.time())
                
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
            
            return self.current_state.get("completed", False)
    
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
                if os.path.exists(self.state_file):
                    os.remove(self.state_file)
                    self.logger.debug(f"已刪除狀態文件: {self.state_file}")
                
                if os.path.exists(self.state_pickle_file):
                    os.remove(self.state_pickle_file)
                    self.logger.debug(f"已刪除狀態文件: {self.state_pickle_file}")
                
                return True
        
        except Exception as e:
            self.logger.error(f"清除狀態失敗: {str(e)}")
            return False
    
    def _load_state(self):
        """載入爬蟲狀態"""
        # 嘗試從各種存儲中載入
        loaded = False
        
        # 從JSON載入
        if not loaded and "json" in self.storage_modes and os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    self.current_state = json.load(f)
                self.logger.info(f"已從JSON載入狀態: {self.state_file}")
                loaded = True
            except Exception as e:
                self.logger.error(f"從JSON載入狀態失敗: {str(e)}")
        
        # 從Pickle載入
        if not loaded and "pickle" in self.storage_modes and os.path.exists(self.state_pickle_file):
            try:
                with open(self.state_pickle_file, "rb") as f:
                    self.current_state = pickle.load(f)
                self.logger.info(f"已從Pickle載入狀態: {self.state_pickle_file}")
                loaded = True
            except Exception as e:
                self.logger.error(f"從Pickle載入狀態失敗: {str(e)}")
        
        # 從備份中恢復
        if not loaded:
            # 查找最新的備份
            backup_files = []
            
            # 查找JSON備份
            for file in os.listdir(self.backup_dir):
                if file.startswith(f"{self.crawler_id}_state_") and file.endswith(".json"):
                    file_path = os.path.join(self.backup_dir, file)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            if backup_files:
                # 按修改時間排序
                backup_files.sort(key=lambda x: x[1], reverse=True)
                
                # 嘗試載入最新的備份
                try:
                    with open(backup_files[0][0], "r", encoding="utf-8") as f:
                        self.current_state = json.load(f)
                    self.logger.info(f"已從備份載入狀態: {backup_files[0][0]}")
                    
                    # 保存到正常的狀態文件
                    self._save_to_storage()
                    
                    loaded = True
                except Exception as e:
                    self.logger.error(f"從備份載入狀態失敗: {str(e)}")
        
        if not loaded:
            self.logger.info("沒有找到有效的狀態，將創建新狀態")
            self.current_state = {
                "crawler_id": self.crawler_id,
                "created_time": int(time.time()),
                "completed": False
            }
            self._save_to_storage()
    
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
                
                # 保存當前狀態
                with self.lock:
                    if self.current_state is not None:
                        self._save_to_storage()
                        self.logger.debug("已自動保存狀態")
            
            except Exception as e:
                self.logger.error(f"自動保存狀態失敗: {str(e)}")
    
    def __del__(self):
        """析構函數，確保線程正確關閉"""
        self._stop_auto_save()
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存儲管理器模組
提供統一的存儲管理接口
"""

from typing import Dict, List, Optional, Any, Type
from datetime import datetime

from src.core.utils import (
    ConfigUtils,
    Logger,
    PathUtils,
    DataProcessor,
    ErrorHandler
)

from ..config.storage_config import StorageConfig
from ..handlers.base_handler import StorageHandler
from ..handlers.local_handler import LocalStorageHandler
from ..handlers.mongodb_handler import MongoDBHandler
from ..handlers.notion_handler import NotionHandler
from ..utils.core_mixin import CoreMixin


class StorageManager(CoreMixin):
    """存儲管理器"""
    
    # 存儲處理器映射
    HANDLER_MAP: Dict[str, Type[StorageHandler]] = {
        "local": LocalStorageHandler,
        "mongodb": MongoDBHandler,
        "notion": NotionHandler
    }
    
    def __init__(self, config: StorageConfig):
        """
        初始化存儲管理器
        
        Args:
            config: 存儲配置
        """
        # 初始化核心工具類
        self.config_utils = ConfigUtils()
        self.logger = Logger()
        self.path_utils = PathUtils()
        self.data_processor = DataProcessor()
        self.error_handler = ErrorHandler()
        
        # 設置配置
        self.config = config
        
        # 初始化處理器
        self.handler = self._init_handler()
        
        # 初始化狀態
        self.status = {
            "last_operation": None,
            "last_operation_time": None,
            "operation_counts": {},
            "error_counts": {},
            "last_error": None
        }
    
    def _init_handler(self) -> StorageHandler:
        """
        初始化存儲處理器
        
        Returns:
            StorageHandler: 存儲處理器實例
            
        Raises:
            ValueError: 不支持的存儲模式
        """
        try:
            # 獲取處理器類
            handler_class = self.HANDLER_MAP.get(self.config.storage_mode)
            if not handler_class:
                raise ValueError(f"不支持的存儲模式: {self.config.storage_mode}")
            
            # 創建處理器實例
            handler = handler_class(self.config)
            
            # 更新狀態
            self._update_status("init_handler", True)
            return handler
            
        except Exception as e:
            self._update_status("init_handler", False, e)
            raise
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """
        保存數據
        
        Args:
            data: 要保存的數據
            
        Returns:
            bool: 是否成功
        """
        try:
            # 驗證數據
            if not self.validate_data(data):
                return False
            
            # 保存數據
            result = self.handler.save_data(data)
            
            # 更新狀態
            self._update_status("save_data", result)
            return result
            
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
            # 驗證數據
            for data in data_list:
                if not self.validate_data(data):
                    return False
            
            # 保存數據
            result = self.handler.save_batch(data_list)
            
            # 更新狀態
            self._update_status("save_batch", result)
            return result
            
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
            result = self.handler.load_data(query)
            
            # 更新狀態
            self._update_status("load_data", True)
            return result
            
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
            # 刪除數據
            result = self.handler.delete_data(query)
            
            # 更新狀態
            self._update_status("delete_data", result)
            return result
            
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
            result = self.handler.clear_data()
            
            # 更新狀態
            self._update_status("clear_data", result)
            return result
            
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
            # 獲取數量
            result = self.handler.get_data_count(query)
            
            # 更新狀態
            self._update_status("get_data_count", True)
            return result
            
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
            # 檢查備份功能
            if not self.config.backup_enabled:
                self.log_error("備份功能未啟用")
                return False
            
            # 創建備份
            result = self.handler.create_backup()
            
            # 更新狀態
            self._update_status("create_backup", result)
            return result
            
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
            # 檢查備份功能
            if not self.config.backup_enabled:
                self.log_error("備份功能未啟用")
                return False
            
            # 恢復備份
            result = self.handler.restore_backup(backup_id)
            
            # 更新狀態
            self._update_status("restore_backup", result)
            return result
            
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
            # 檢查備份功能
            if not self.config.backup_enabled:
                self.log_error("備份功能未啟用")
                return []
            
            # 列出備份
            result = self.handler.list_backups()
            
            # 更新狀態
            self._update_status("list_backups", True)
            return result
            
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
            # 檢查備份功能
            if not self.config.backup_enabled:
                self.log_error("備份功能未啟用")
                return False
            
            # 刪除備份
            result = self.handler.delete_backup(backup_id)
            
            # 更新狀態
            self._update_status("delete_backup", result)
            return result
            
        except Exception as e:
            self._update_status("delete_backup", False, e)
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        獲取狀態信息
        
        Returns:
            Dict[str, Any]: 狀態信息
        """
        return {
            **self.status,
            "handler_status": self.handler.status if self.handler else None
        }
    
    def _update_status(self, operation: str, success: bool, error: Optional[Exception] = None) -> None:
        """
        更新狀態
        
        Args:
            operation: 操作名稱
            success: 是否成功
            error: 錯誤信息
        """
        # 更新操作信息
        self.status["last_operation"] = operation
        self.status["last_operation_time"] = self.get_timestamp()
        
        # 更新計數
        self.status["operation_counts"][operation] = self.status["operation_counts"].get(operation, 0) + 1
        if not success:
            self.status["error_counts"][operation] = self.status["error_counts"].get(operation, 0) + 1
            self.status["last_error"] = str(error) if error else "未知錯誤"
            self.log_error(f"操作失敗: {operation}", error)
        else:
            self.log_info(f"操作成功: {operation}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if exc_type is not None:
            self._update_status("context_exit", False, exc_val)
        else:
            self._update_status("context_exit", True) 
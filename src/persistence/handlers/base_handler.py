#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存儲處理器基類模組
定義所有存儲處理器必須實現的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..utils.core_mixin import CoreMixin
from ..config.storage_config import StorageConfig


class StorageHandler(CoreMixin, ABC):
    """存儲處理器基類"""
    
    def __init__(self, config: StorageConfig):
        """
        初始化存儲處理器
        
        Args:
            config: 存儲配置
        """
        # 初始化核心工具類
        self.init_core_utils()
        
        # 設置配置
        self.config = config
        if not config.validate():
            raise ValueError("配置驗證失敗")
            
        # 初始化狀態
        self.status = {
            'connected': False,
            'last_operation': None,
            'last_operation_time': None,
            'operation_count': 0,
            'success_count': 0,
            'error_count': 0,
            'start_time': self.get_timestamp(),
            'last_error': None
        }
    
    @abstractmethod
    def save_data(self, data: Dict[str, Any]) -> bool:
        """
        保存數據
        
        Args:
            data: 要保存的數據
            
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    def save_batch(self, data_list: List[Dict[str, Any]]) -> bool:
        """
        批量保存數據
        
        Args:
            data_list: 要保存的數據列表
            
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    def load_data(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        加載數據
        
        Args:
            query: 查詢條件
            
        Returns:
            List[Dict[str, Any]]: 加載的數據列表
        """
        pass
    
    @abstractmethod
    def delete_data(self, query: Dict[str, Any]) -> bool:
        """
        刪除數據
        
        Args:
            query: 刪除條件
            
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    def clear_data(self) -> bool:
        """
        清空數據
        
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    def get_data_count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """
        獲取數據數量
        
        Args:
            query: 查詢條件
            
        Returns:
            int: 數據數量
        """
        pass
    
    @abstractmethod
    def create_backup(self) -> bool:
        """
        創建備份
        
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    def restore_backup(self, backup_id: str) -> bool:
        """
        恢復備份
        
        Args:
            backup_id: 備份ID
            
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    def list_backups(self) -> List[str]:
        """
        列出所有備份
        
        Returns:
            List[str]: 備份ID列表
        """
        pass
    
    @abstractmethod
    def delete_backup(self, backup_id: str) -> bool:
        """
        刪除備份
        
        Args:
            backup_id: 備份ID
            
        Returns:
            bool: 是否成功
        """
        pass
    
    def _update_status(self, operation: str, success: bool, error: Optional[Exception] = None) -> None:
        """
        更新狀態
        
        Args:
            operation: 操作名稱
            success: 是否成功
            error: 錯誤信息
        """
        # 更新基本信息
        self.status['last_operation'] = operation
        self.status['last_operation_time'] = self.get_timestamp()
        self.status['operation_count'] += 1
        
        if success:
            # 成功處理
            self.status['success_count'] += 1
            self.log_info(f"操作成功: {operation}")
        else:
            # 錯誤處理
            self.status['error_count'] += 1
            if error:
                self.status['last_error'] = str(error)
                self.log_error(f"操作失敗: {operation}, 錯誤: {str(error)}")
            else:
                self.log_error(f"操作失敗: {operation}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if exc_type:
            self._update_status("context_exit", False, exc_val)
            self.handle_error(exc_val) 
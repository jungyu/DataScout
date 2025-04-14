#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
持久化模組基礎類

提供存儲處理器的基礎接口和通用功能
"""

import os
import time
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
from .config import StorageConfig
from .exceptions import (
    PersistenceError,
    StorageError,
    ValidationError,
    ConfigError,
    NotFoundError
)

class StorageHandler(ABC):
    """存儲處理器基類"""
    
    def __init__(self, config: Union[Dict[str, Any], StorageConfig]):
        """
        初始化存儲處理器
        
        Args:
            config: 配置對象或配置字典
        """
        # 轉換配置
        if isinstance(config, dict):
            self.config = StorageConfig(**config)
        else:
            self.config = config
        
        # 設置日誌
        self._setup_logging()
        
        # 初始化存儲
        self._initialize()
    
    def _setup_logging(self) -> None:
        """設置日誌"""
        if not self.config.enable_logging:
            return
        
        # 創建日誌記錄器
        self.logger = logging.getLogger(f'persistence.{self.__class__.__name__}')
        self.logger.setLevel(getattr(logging, self.config.log_level))
        
        # 如果沒有處理器，添加一個
        if not self.logger.handlers:
            # 創建控制台處理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, self.config.log_level))
            
            # 創建格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            
            # 添加處理器
            self.logger.addHandler(console_handler)
            
            # 如果指定了日誌文件，添加文件處理器
            if self.config.log_file:
                file_handler = logging.FileHandler(self.config.log_file)
                file_handler.setLevel(getattr(logging, self.config.log_level))
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
    
    def _initialize(self) -> None:
        """初始化存儲"""
        try:
            self._setup_storage()
        except Exception as e:
            self.logger.error(f"初始化存儲失敗: {str(e)}")
            raise StorageError(f"初始化存儲失敗: {str(e)}")
    
    @abstractmethod
    def _setup_storage(self) -> None:
        """設置存儲環境"""
        pass
    
    def _validate_data(self, data: Any) -> None:
        """
        驗證數據
        
        Args:
            data: 要驗證的數據
            
        Raises:
            ValidationError: 數據驗證失敗
        """
        if not self.config.validate_data:
            return
        
        if self.config.schema:
            # TODO: 實現基於schema的數據驗證
            pass
    
    def _backup_data(self, data: Any, path: str) -> None:
        """
        備份數據
        
        Args:
            data: 要備份的數據
            path: 數據路徑
        """
        if not self.config.enable_backup:
            return
        
        try:
            # 創建備份目錄
            backup_dir = os.path.join(
                self.config.backup_path,
                datetime.now().strftime('%Y%m%d')
            )
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成備份文件名
            backup_file = os.path.join(
                backup_dir,
                f"{os.path.basename(path)}.{int(time.time())}"
            )
            
            # 保存備份
            self._save_to_file(data, backup_file)
            
            # 清理舊備份
            self._cleanup_backups(path)
            
            self.logger.info(f"數據已備份到: {backup_file}")
        except Exception as e:
            self.logger.error(f"備份數據失敗: {str(e)}")
    
    def _cleanup_backups(self, path: str) -> None:
        """
        清理舊備份
        
        Args:
            path: 數據路徑
        """
        if not self.config.enable_backup:
            return
        
        try:
            # 獲取備份目錄
            backup_dir = os.path.join(
                self.config.backup_path,
                datetime.now().strftime('%Y%m%d')
            )
            
            # 獲取所有備份文件
            backup_files = []
            for file in os.listdir(backup_dir):
                if file.startswith(os.path.basename(path)):
                    backup_files.append(os.path.join(backup_dir, file))
            
            # 按修改時間排序
            backup_files.sort(key=lambda x: os.path.getmtime(x))
            
            # 刪除多餘的備份
            while len(backup_files) > self.config.max_backups:
                os.remove(backup_files.pop(0))
        except Exception as e:
            self.logger.error(f"清理舊備份失敗: {str(e)}")
    
    def _save_to_file(self, data: Any, path: str) -> None:
        """
        保存數據到文件
        
        Args:
            data: 要保存的數據
            path: 文件路徑
        """
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # 根據格式保存數據
            if self.config.format == 'json':
                with open(path, 'w', encoding=self.config.encoding) as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                raise StorageError(f"不支援的數據格式: {self.config.format}")
        except Exception as e:
            raise StorageError(f"保存數據失敗: {str(e)}")
    
    def _load_from_file(self, path: str) -> Any:
        """
        從文件加載數據
        
        Args:
            path: 文件路徑
            
        Returns:
            Any: 加載的數據
            
        Raises:
            NotFoundError: 文件不存在
            StorageError: 加載失敗
        """
        if not os.path.exists(path):
            raise NotFoundError(f"文件不存在: {path}")
        
        try:
            # 根據格式加載數據
            if self.config.format == 'json':
                with open(path, 'r', encoding=self.config.encoding) as f:
                    return json.load(f)
            else:
                raise StorageError(f"不支援的數據格式: {self.config.format}")
        except Exception as e:
            raise StorageError(f"加載數據失敗: {str(e)}")
    
    @abstractmethod
    def save(self, data: Any, path: str) -> None:
        """
        保存數據
        
        Args:
            data: 要保存的數據
            path: 數據路徑
        """
        pass
    
    @abstractmethod
    def load(self, path: str) -> Any:
        """
        加載數據
        
        Args:
            path: 數據路徑
            
        Returns:
            Any: 加載的數據
        """
        pass
    
    @abstractmethod
    def delete(self, path: str) -> None:
        """
        刪除數據
        
        Args:
            path: 數據路徑
        """
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        檢查數據是否存在
        
        Args:
            path: 數據路徑
            
        Returns:
            bool: 是否存在
        """
        pass
    
    @abstractmethod
    def list(self, path: str = None) -> List[str]:
        """
        列出數據
        
        Args:
            path: 數據路徑，None表示根路徑
            
        Returns:
            List[str]: 數據路徑列表
        """
        pass 
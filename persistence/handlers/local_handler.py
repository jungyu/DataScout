#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
本地存儲處理器

提供基於文件系統的數據存儲功能
"""

import os
import shutil
from typing import Dict, Any, List, Optional
from ..core.base import StorageHandler
from ..core.config import LocalStorageConfig
from ..core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError
)

class LocalStorageHandler(StorageHandler):
    """本地存儲處理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化本地存儲處理器
        
        Args:
            config: 配置字典
        """
        super().__init__(LocalStorageConfig(**config))
    
    def _setup_storage(self) -> None:
        """設置存儲環境"""
        try:
            # 創建基礎目錄
            os.makedirs(self.config.base_path, exist_ok=True)
            
            # 如果啟用備份，創建備份目錄
            if self.config.enable_backup:
                os.makedirs(self.config.backup_path, exist_ok=True)
            
            self.logger.info(f"本地存儲環境已初始化: {self.config.base_path}")
        except Exception as e:
            raise StorageError(f"初始化本地存儲環境失敗: {str(e)}")
    
    def save(self, data: Any, path: str) -> None:
        """
        保存數據到本地文件
        
        Args:
            data: 要保存的數據
            path: 文件路徑
        """
        try:
            # 驗證數據
            self._validate_data(data)
            
            # 構建完整路徑
            full_path = os.path.join(self.config.base_path, path)
            
            # 保存數據
            self._save_to_file(data, full_path)
            
            # 備份數據
            self._backup_data(data, path)
            
            self.logger.info(f"數據已保存到: {full_path}")
        except Exception as e:
            raise StorageError(f"保存數據失敗: {str(e)}")
    
    def load(self, path: str) -> Any:
        """
        從本地文件加載數據
        
        Args:
            path: 文件路徑
            
        Returns:
            Any: 加載的數據
        """
        try:
            # 構建完整路徑
            full_path = os.path.join(self.config.base_path, path)
            
            # 加載數據
            data = self._load_from_file(full_path)
            
            self.logger.info(f"數據已從 {full_path} 加載")
            return data
        except Exception as e:
            raise StorageError(f"加載數據失敗: {str(e)}")
    
    def delete(self, path: str) -> None:
        """
        刪除本地文件
        
        Args:
            path: 文件路徑
        """
        try:
            # 構建完整路徑
            full_path = os.path.join(self.config.base_path, path)
            
            # 檢查文件是否存在
            if not os.path.exists(full_path):
                raise NotFoundError(f"文件不存在: {full_path}")
            
            # 刪除文件
            os.remove(full_path)
            
            self.logger.info(f"文件已刪除: {full_path}")
        except Exception as e:
            raise StorageError(f"刪除文件失敗: {str(e)}")
    
    def exists(self, path: str) -> bool:
        """
        檢查本地文件是否存在
        
        Args:
            path: 文件路徑
            
        Returns:
            bool: 是否存在
        """
        try:
            # 構建完整路徑
            full_path = os.path.join(self.config.base_path, path)
            
            # 檢查文件是否存在
            return os.path.exists(full_path)
        except Exception as e:
            raise StorageError(f"檢查文件是否存在失敗: {str(e)}")
    
    def list(self, path: str = None) -> List[str]:
        """
        列出本地文件
        
        Args:
            path: 目錄路徑，None表示根目錄
            
        Returns:
            List[str]: 文件路徑列表
        """
        try:
            # 構建完整路徑
            if path:
                full_path = os.path.join(self.config.base_path, path)
            else:
                full_path = self.config.base_path
            
            # 檢查目錄是否存在
            if not os.path.exists(full_path):
                raise NotFoundError(f"目錄不存在: {full_path}")
            
            # 列出文件
            files = []
            for root, _, filenames in os.walk(full_path):
                for filename in filenames:
                    # 構建相對路徑
                    rel_path = os.path.relpath(
                        os.path.join(root, filename),
                        self.config.base_path
                    )
                    files.append(rel_path)
            
            return files
        except Exception as e:
            raise StorageError(f"列出文件失敗: {str(e)}")
    
    def copy(self, src_path: str, dst_path: str) -> None:
        """
        複製文件
        
        Args:
            src_path: 源文件路徑
            dst_path: 目標文件路徑
        """
        try:
            # 構建完整路徑
            src_full_path = os.path.join(self.config.base_path, src_path)
            dst_full_path = os.path.join(self.config.base_path, dst_path)
            
            # 檢查源文件是否存在
            if not os.path.exists(src_full_path):
                raise NotFoundError(f"源文件不存在: {src_full_path}")
            
            # 確保目標目錄存在
            os.makedirs(os.path.dirname(dst_full_path), exist_ok=True)
            
            # 複製文件
            shutil.copy2(src_full_path, dst_full_path)
            
            self.logger.info(f"文件已複製: {src_path} -> {dst_path}")
        except Exception as e:
            raise StorageError(f"複製文件失敗: {str(e)}")
    
    def move(self, src_path: str, dst_path: str) -> None:
        """
        移動文件
        
        Args:
            src_path: 源文件路徑
            dst_path: 目標文件路徑
        """
        try:
            # 構建完整路徑
            src_full_path = os.path.join(self.config.base_path, src_path)
            dst_full_path = os.path.join(self.config.base_path, dst_path)
            
            # 檢查源文件是否存在
            if not os.path.exists(src_full_path):
                raise NotFoundError(f"源文件不存在: {src_full_path}")
            
            # 確保目標目錄存在
            os.makedirs(os.path.dirname(dst_full_path), exist_ok=True)
            
            # 移動文件
            shutil.move(src_full_path, dst_full_path)
            
            self.logger.info(f"文件已移動: {src_path} -> {dst_path}")
        except Exception as e:
            raise StorageError(f"移動文件失敗: {str(e)}")
    
    def get_size(self, path: str) -> int:
        """
        獲取文件大小
        
        Args:
            path: 文件路徑
            
        Returns:
            int: 文件大小（字節）
        """
        try:
            # 構建完整路徑
            full_path = os.path.join(self.config.base_path, path)
            
            # 檢查文件是否存在
            if not os.path.exists(full_path):
                raise NotFoundError(f"文件不存在: {full_path}")
            
            # 獲取文件大小
            return os.path.getsize(full_path)
        except Exception as e:
            raise StorageError(f"獲取文件大小失敗: {str(e)}")
    
    def get_modified_time(self, path: str) -> float:
        """
        獲取文件修改時間
        
        Args:
            path: 文件路徑
            
        Returns:
            float: 修改時間（時間戳）
        """
        try:
            # 構建完整路徑
            full_path = os.path.join(self.config.base_path, path)
            
            # 檢查文件是否存在
            if not os.path.exists(full_path):
                raise NotFoundError(f"文件不存在: {full_path}")
            
            # 獲取修改時間
            return os.path.getmtime(full_path)
        except Exception as e:
            raise StorageError(f"獲取文件修改時間失敗: {str(e)}") 
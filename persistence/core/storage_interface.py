#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存儲介面
定義統一的存儲操作介面，所有存儲處理器都必須實現此介面
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Callable, Iterator

class StorageInterface(ABC):
    """存儲介面抽象類"""
    
    @abstractmethod
    def __init__(self, config: Union[Dict[str, Any], Any]):
        """初始化存儲處理器
        
        Args:
            config: 配置對象，可以是字典或配置類實例
        """
        pass
    
    @abstractmethod
    def save(self, data: Dict[str, Any], path: str) -> None:
        """保存數據
        
        Args:
            data: 要保存的數據
            path: 數據路徑
        """
        pass
    
    @abstractmethod
    def load(self, path: str) -> Dict[str, Any]:
        """加載數據
        
        Args:
            path: 數據路徑
            
        Returns:
            加載的數據
        """
        pass
    
    @abstractmethod
    def delete(self, path: str) -> None:
        """刪除數據
        
        Args:
            path: 數據路徑
        """
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """檢查數據是否存在
        
        Args:
            path: 數據路徑
            
        Returns:
            數據是否存在
        """
        pass
    
    @abstractmethod
    def list(self, prefix: Optional[str] = None) -> List[str]:
        """列出數據路徑
        
        Args:
            prefix: 路徑前綴
            
        Returns:
            數據路徑列表
        """
        pass
    
    @abstractmethod
    def find(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """查詢數據
        
        Args:
            query: 查詢條件
            
        Returns:
            查詢結果列表
        """
        pass
    
    @abstractmethod
    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """統計數據數量
        
        Args:
            query: 查詢條件
            
        Returns:
            數據數量
        """
        pass
    
    @abstractmethod
    def batch_save(self, data_list: List[Dict[str, Any]]) -> None:
        """批量保存數據
        
        Args:
            data_list: 數據列表，每個元素包含 path 和 data
        """
        pass
    
    @abstractmethod
    def batch_load(self, paths: List[str]) -> List[Dict[str, Any]]:
        """批量加載數據
        
        Args:
            paths: 數據路徑列表
            
        Returns:
            數據列表，每個元素包含 path 和 data
        """
        pass
    
    @abstractmethod
    def batch_delete(self, paths: List[str]) -> None:
        """批量刪除數據
        
        Args:
            paths: 數據路徑列表
        """
        pass
    
    @abstractmethod
    def batch_exists(self, paths: List[str]) -> Dict[str, bool]:
        """批量檢查數據是否存在
        
        Args:
            paths: 數據路徑列表
            
        Returns:
            數據存在狀態字典
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """清理資源"""
        pass 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Supabase 處理器模組

此模組提供與 Supabase 資料庫的業務層交互功能。
"""

from typing import Dict, Any, List, Optional
from functools import wraps
from persistence.handlers.supabase_handler import SupabaseHandler as BaseSupabaseHandler
from .config import SupabaseConfig

class SupabaseHandler:
    """Supabase 處理器類"""
    
    def __init__(self, config: SupabaseConfig):
        """初始化 Supabase 處理器
        
        Args:
            config: Supabase 配置對象
        """
        self._config = config
        self._handler: Optional[BaseSupabaseHandler] = None
    
    async def initialize(self) -> None:
        """初始化 Supabase 客戶端"""
        if not self._handler:
            self._handler = BaseSupabaseHandler(self._config.get_connection_config())
    
    async def create(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """創建記錄
        
        Args:
            table: 表名
            data: 要創建的數據
            
        Returns:
            創建的記錄
        """
        await self.initialize()
        return await self._handler.create(table, data)
    
    async def read(self, table: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """讀取記錄
        
        Args:
            table: 表名
            filters: 過濾條件
            
        Returns:
            符合條件的記錄列表
        """
        await self.initialize()
        return await self._handler.read(table, filters)
    
    async def update(self, table: str, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新記錄
        
        Args:
            table: 表名
            id: 記錄ID
            data: 要更新的數據
            
        Returns:
            更新後的記錄
        """
        await self.initialize()
        return await self._handler.update(table, {'id': id}, data)
    
    async def delete(self, table: str, id: str) -> bool:
        """刪除記錄
        
        Args:
            table: 表名
            id: 記錄ID
            
        Returns:
            是否刪除成功
        """
        await self.initialize()
        return await self._handler.delete(table, {'id': id})
    
    async def save_image(self, table: str, image_data: bytes,
                        metadata: Dict[str, Any]) -> Dict[str, Any]:
        """保存圖片
        
        Args:
            table: 表名
            image_data: 圖片數據
            metadata: 圖片元數據
            
        Returns:
            保存的圖片記錄
        """
        await self.initialize()
        return await self._handler.save_image(table, image_data, metadata)
    
    async def get_images(self, table: str,
                        filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """獲取圖片記錄
        
        Args:
            table: 表名
            filters: 過濾條件
            
        Returns:
            符合條件的圖片記錄列表
        """
        await self.initialize()
        return await self._handler.get_images(table, filters) 
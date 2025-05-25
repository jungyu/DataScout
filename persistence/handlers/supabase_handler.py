#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Supabase存儲處理器

提供基於Supabase的數據存儲功能，支持數據的增刪改查操作
"""

import time
import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from supabase import create_client, Client
from ..core.base import StorageHandler
from ..core.config import SupabaseConfig
from ..core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

class SupabaseHandler(StorageHandler):
    """Supabase存儲處理器"""
    
    def __init__(self, config: Union[Dict[str, Any], SupabaseConfig]):
        """
        初始化Supabase存儲處理器
        
        Args:
            config: 配置對象或配置字典
        """
        super().__init__(config)
        self.client: Optional[Client] = None
    
    def _setup_storage(self) -> None:
        """設置存儲環境"""
        try:
            # 創建Supabase客戶端
            self.client = create_client(
                self.config.url,
                self.config.key
            )
            
            # 創建表（如果不存在）
            self._create_table()
            
            self.logger.info(
                f"Supabase存儲環境已初始化: "
                f"{self.config.url}/{self.config.schema}/"
                f"{self.config.table_name}"
            )
        except Exception as e:
            raise ConnectionError(f"連接Supabase失敗: {str(e)}")
    
    def _create_table(self) -> None:
        """檢查存儲表是否存在，不自動建表，若不存在則提示需手動建立"""
        try:
            # 檢查表是否存在
            response = self.client.table(self.config.table_name).select("*").limit(1).execute()
            # 若能查詢到，代表表存在
        except Exception as e:
            raise StorageError(
                f"Supabase 資料表 `{self.config.table_name}` 不存在，請先在 Supabase SQL Editor 建立該表。原始錯誤: {str(e)}"
            )
    
    def save(self, data: Any, path: str) -> None:
        """
        保存數據到Supabase
        
        Args:
            data: 要保存的數據
            path: 數據路徑（作為ID）
        """
        try:
            # 驗證數據
            self._validate_data(data)
            
            # 序列化數據
            serialized_data = json.dumps(data)
            
            # 獲取當前時間
            now = time.time()
            
            # 構建數據
            record = {
                self.config.id_field: path,
                self.config.data_field: serialized_data,
                self.config.updated_at_field: now
            }
            
            # 檢查記錄是否存在
            exists = self.exists(path)
            
            if exists:
                # 更新記錄
                self.client.table(self.config.table_name).update(record).eq(
                    self.config.id_field, path
                ).execute()
            else:
                # 添加創建時間
                record[self.config.created_at_field] = now
                
                # 插入記錄
                self.client.table(self.config.table_name).insert(record).execute()
            
            # 備份數據
            self._backup_data(data, path)
            
            self.logger.info(f"數據已保存到Supabase: {path}")
        except Exception as e:
            raise StorageError(f"保存數據到Supabase失敗: {str(e)}")
    
    def load(self, path: str) -> Any:
        """
        從Supabase加載數據
        
        Args:
            path: 數據路徑（作為ID）
            
        Returns:
            Any: 加載的數據
        """
        try:
            # 查詢記錄
            response = self.client.table(self.config.table_name).select("*").eq(
                self.config.id_field, path
            ).execute()
            
            # 檢查記錄是否存在
            if not response.data or len(response.data) == 0:
                raise NotFoundError(f"數據不存在: {path}")
            
            # 獲取記錄
            record = response.data[0]
            
            # 反序列化數據
            data = json.loads(record[self.config.data_field])
            
            self.logger.info(f"數據已從Supabase加載: {path}")
            return data
        except Exception as e:
            raise StorageError(f"從Supabase加載數據失敗: {str(e)}")
    
    def delete(self, path: str) -> None:
        """
        從Supabase刪除數據
        
        Args:
            path: 數據路徑（作為ID）
        """
        try:
            # 刪除記錄
            response = self.client.table(self.config.table_name).delete().eq(
                self.config.id_field, path
            ).execute()
            
            # 檢查是否刪除成功
            if not response.data or len(response.data) == 0:
                raise NotFoundError(f"數據不存在: {path}")
            
            self.logger.info(f"數據已從Supabase刪除: {path}")
        except Exception as e:
            raise StorageError(f"從Supabase刪除數據失敗: {str(e)}")
    
    def exists(self, path: str) -> bool:
        """
        檢查Supabase數據是否存在
        
        Args:
            path: 數據路徑（作為ID）
            
        Returns:
            bool: 是否存在
        """
        try:
            # 查詢記錄
            response = self.client.table(self.config.table_name).select("*").eq(
                self.config.id_field, path
            ).execute()
            
            return response.data is not None and len(response.data) > 0
        except Exception as e:
            raise StorageError(f"檢查Supabase數據是否存在失敗: {str(e)}")
    
    def list(self, path: str = None) -> List[str]:
        """
        列出Supabase數據
        
        Args:
            path: 數據路徑前綴，None表示所有數據
            
        Returns:
            List[str]: 數據路徑列表
        """
        try:
            # 構建查詢
            query = self.client.table(self.config.table_name).select(self.config.id_field)
            
            # 添加路徑前綴條件
            if path:
                query = query.ilike(self.config.id_field, f"{path}%")
            
            # 執行查詢
            response = query.execute()
            
            # 提取路徑
            paths = [row[self.config.id_field] for row in response.data]
            
            return paths
        except Exception as e:
            raise StorageError(f"列出Supabase數據失敗: {str(e)}")
    
    def find(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        查詢Supabase數據
        
        Args:
            query: 查詢條件
            
        Returns:
            List[Dict[str, Any]]: 數據列表
        """
        try:
            # 構建查詢
            supabase_query = self.client.table(self.config.table_name).select("*")
            
            # 添加查詢條件
            for key, value in query.items():
                supabase_query = supabase_query.eq(key, value)
            
            # 執行查詢
            response = supabase_query.execute()
            
            # 轉換結果
            data = []
            for row in response.data:
                record = dict(row)
                record[self.config.data_field] = json.loads(
                    record[self.config.data_field]
                )
                data.append(record)
            
            return data
        except Exception as e:
            raise StorageError(f"查詢Supabase數據失敗: {str(e)}")
    
    def count(self, query: Dict[str, Any] = None) -> int:
        """
        統計Supabase數據數量
        
        Args:
            query: 查詢條件，None表示所有數據
            
        Returns:
            int: 數據數量
        """
        try:
            # 構建查詢
            supabase_query = self.client.table(self.config.table_name).select("*", count='exact')
            
            # 添加查詢條件
            if query:
                for key, value in query.items():
                    supabase_query = supabase_query.eq(key, value)
            
            # 執行查詢
            response = supabase_query.execute()
            
            return response.count
        except Exception as e:
            raise StorageError(f"統計Supabase數據數量失敗: {str(e)}")
    
    def __del__(self):
        """清理資源"""
        # Supabase客戶端不需要顯式關閉
        pass

    async def create(self, table: str, data: dict) -> dict:
        """在指定表新增一筆資料"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.table(table).insert(data).execute()
            )
            if not response.data or len(response.data) == 0:
                raise StorageError(f"新增資料失敗: {data}")
            return response.data[0]
        except Exception as e:
            raise StorageError(f"Supabase create 失敗: {str(e)}")

    async def read(self, table: str, query: dict) -> list:
        """查詢指定表的資料"""
        try:
            loop = asyncio.get_event_loop()
            def _query():
                q = self.client.table(table).select('*')
                for k, v in query.items():
                    q = q.eq(k, v)
                return q.execute()
            response = await loop.run_in_executor(None, _query)
            return response.data or []
        except Exception as e:
            raise StorageError(f"Supabase read 失敗: {str(e)}")

    async def update(self, table: str, query: dict, data: dict) -> dict:
        """更新指定表的資料"""
        try:
            loop = asyncio.get_event_loop()
            def _update():
                q = self.client.table(table).update(data)
                for k, v in query.items():
                    q = q.eq(k, v)
                return q.execute()
            response = await loop.run_in_executor(None, _update)
            if not response.data or len(response.data) == 0:
                raise NotFoundError(f"更新資料失敗: {query}")
            return response.data[0]
        except Exception as e:
            raise StorageError(f"Supabase update 失敗: {str(e)}")

    async def delete(self, table: str, query: dict) -> bool:
        """刪除指定表的資料"""
        try:
            loop = asyncio.get_event_loop()
            def _delete():
                q = self.client.table(table).delete()
                for k, v in query.items():
                    q = q.eq(k, v)
                return q.execute()
            response = await loop.run_in_executor(None, _delete)
            return bool(response.data and len(response.data) > 0)
        except Exception as e:
            raise StorageError(f"Supabase delete 失敗: {str(e)}")

    async def save_image(self, table: str, image_data: bytes, metadata: dict) -> dict:
        """儲存圖片資料"""
        import base64
        try:
            loop = asyncio.get_event_loop()
            data = metadata.copy()
            data['image_data'] = base64.b64encode(image_data).decode('utf-8')
            response = await loop.run_in_executor(
                None,
                lambda: self.client.table(table).insert(data).execute()
            )
            if not response.data or len(response.data) == 0:
                raise StorageError("圖片儲存失敗")
            return response.data[0]
        except Exception as e:
            raise StorageError(f"Supabase save_image 失敗: {str(e)}")

    async def get_images(self, table: str, query: dict) -> list:
        """查詢圖片資料"""
        try:
            loop = asyncio.get_event_loop()
            def _query():
                q = self.client.table(table).select('*')
                for k, v in query.items():
                    q = q.eq(k, v)
                return q.execute()
            response = await loop.run_in_executor(None, _query)
            return response.data or []
        except Exception as e:
            raise StorageError(f"Supabase get_images 失敗: {str(e)}") 
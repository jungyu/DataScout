#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Supabase存儲處理器

提供基於Supabase的數據存儲功能，支持數據的增刪改查操作
"""

import time
import json
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
        """創建存儲表"""
        try:
            # 檢查表是否存在
            response = self.client.table(self.config.table_name).select("*").limit(1).execute()
            
            # 如果表不存在，創建表
            if response.data is None:
                # 使用SQL創建表
                sql = f"""
                CREATE TABLE IF NOT EXISTS {self.config.schema}.{self.config.table_name} (
                    {self.config.id_field} TEXT PRIMARY KEY,
                    {self.config.data_field} JSONB,
                    {self.config.created_at_field} TIMESTAMP WITH TIME ZONE,
                    {self.config.updated_at_field} TIMESTAMP WITH TIME ZONE
                );
                """
                self.client.rpc('exec_sql', {'sql': sql}).execute()
                
                self.logger.info(f"已創建Supabase表: {self.config.table_name}")
        except Exception as e:
            raise StorageError(f"創建Supabase表失敗: {str(e)}")
    
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
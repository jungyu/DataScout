#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MySQL存儲處理器

提供基於MySQL的數據存儲功能，支持數據的增刪改查操作
"""

import time
import json
from typing import Dict, Any, List, Optional, Union
from sqlalchemy import create_engine, Table, Column, String, DateTime, MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from ..core.base import StorageHandler
from ..core.config import MySQLConfig
from ..core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

class MySQLHandler(StorageHandler):
    """MySQL存儲處理器"""
    
    def __init__(self, config: Union[Dict[str, Any], MySQLConfig]):
        """
        初始化MySQL存儲處理器
        
        Args:
            config: 配置對象或配置字典
        """
        super().__init__(config)
        self.engine: Optional[Engine] = None
        self.session: Optional[Session] = None
        self.table: Optional[Table] = None
    
    def _setup_storage(self) -> None:
        """設置存儲環境"""
        try:
            # 構建連接URI
            uri = self._build_connection_uri()
            
            # 創建引擎
            self.engine = create_engine(
                uri,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                pool_recycle=self.config.pool_recycle,
                pool_timeout=self.config.pool_timeout,
                pool_pre_ping=True
            )
            
            # 創建會話
            self.session = sessionmaker(bind=self.engine)()
            
            # 創建表
            self._create_table()
            
            self.logger.info(
                f"MySQL存儲環境已初始化: "
                f"{self.config.host}:{self.config.port}/"
                f"{self.config.database}/{self.config.table_name}"
            )
        except Exception as e:
            raise ConnectionError(f"連接MySQL失敗: {str(e)}")
    
    def _build_connection_uri(self) -> str:
        """
        構建MySQL連接URI
        
        Returns:
            str: 連接URI
        """
        # 構建URI
        return (
            f"mysql+pymysql://{self.config.username}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}"
            f"?charset={self.config.charset}"
        )
    
    def _create_table(self) -> None:
        """創建存儲表"""
        try:
            # 創建元數據
            metadata = MetaData()
            
            # 創建表
            self.table = Table(
                self.config.table_name,
                metadata,
                Column(self.config.id_field, String(255), primary_key=True),
                Column(self.config.data_field, String(65535)),
                Column(self.config.created_at_field, DateTime),
                Column(self.config.updated_at_field, DateTime)
            )
            
            # 創建表（如果不存在）
            metadata.create_all(self.engine)
        except Exception as e:
            raise StorageError(f"創建MySQL表失敗: {str(e)}")
    
    def save(self, data: Any, path: str) -> None:
        """
        保存數據到MySQL
        
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
                self.table.update().where(
                    self.table.c[self.config.id_field] == path
                ).values(**record).execute()
            else:
                # 添加創建時間
                record[self.config.created_at_field] = now
                
                # 插入記錄
                self.table.insert().values(**record).execute()
            
            # 提交事務
            self.session.commit()
            
            # 備份數據
            self._backup_data(data, path)
            
            self.logger.info(f"數據已保存到MySQL: {path}")
        except Exception as e:
            # 回滾事務
            self.session.rollback()
            raise StorageError(f"保存數據到MySQL失敗: {str(e)}")
    
    def load(self, path: str) -> Any:
        """
        從MySQL加載數據
        
        Args:
            path: 數據路徑（作為ID）
            
        Returns:
            Any: 加載的數據
        """
        try:
            # 查詢記錄
            result = self.table.select().where(
                self.table.c[self.config.id_field] == path
            ).execute().first()
            
            # 檢查記錄是否存在
            if not result:
                raise NotFoundError(f"數據不存在: {path}")
            
            # 反序列化數據
            data = json.loads(result[self.config.data_field])
            
            self.logger.info(f"數據已從MySQL加載: {path}")
            return data
        except Exception as e:
            raise StorageError(f"從MySQL加載數據失敗: {str(e)}")
    
    def delete(self, path: str) -> None:
        """
        從MySQL刪除數據
        
        Args:
            path: 數據路徑（作為ID）
        """
        try:
            # 刪除記錄
            result = self.table.delete().where(
                self.table.c[self.config.id_field] == path
            ).execute()
            
            # 檢查是否刪除成功
            if result.rowcount == 0:
                raise NotFoundError(f"數據不存在: {path}")
            
            # 提交事務
            self.session.commit()
            
            self.logger.info(f"數據已從MySQL刪除: {path}")
        except Exception as e:
            # 回滾事務
            self.session.rollback()
            raise StorageError(f"從MySQL刪除數據失敗: {str(e)}")
    
    def exists(self, path: str) -> bool:
        """
        檢查MySQL數據是否存在
        
        Args:
            path: 數據路徑（作為ID）
            
        Returns:
            bool: 是否存在
        """
        try:
            # 查詢記錄
            result = self.table.select().where(
                self.table.c[self.config.id_field] == path
            ).execute().first()
            
            return result is not None
        except Exception as e:
            raise StorageError(f"檢查MySQL數據是否存在失敗: {str(e)}")
    
    def list(self, path: str = None) -> List[str]:
        """
        列出MySQL數據
        
        Args:
            path: 數據路徑前綴，None表示所有數據
            
        Returns:
            List[str]: 數據路徑列表
        """
        try:
            # 構建查詢
            query = self.table.select()
            
            # 添加路徑前綴條件
            if path:
                query = query.where(
                    self.table.c[self.config.id_field].like(f"{path}%")
                )
            
            # 執行查詢
            results = query.execute()
            
            # 提取路徑
            paths = [row[self.config.id_field] for row in results]
            
            return paths
        except Exception as e:
            raise StorageError(f"列出MySQL數據失敗: {str(e)}")
    
    def find(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        查詢MySQL數據
        
        Args:
            query: 查詢條件
            
        Returns:
            List[Dict[str, Any]]: 數據列表
        """
        try:
            # 構建查詢
            sql_query = self.table.select()
            
            # 添加查詢條件
            for key, value in query.items():
                sql_query = sql_query.where(
                    self.table.c[key] == value
                )
            
            # 執行查詢
            results = sql_query.execute()
            
            # 轉換結果
            data = []
            for row in results:
                record = dict(row)
                record[self.config.data_field] = json.loads(
                    record[self.config.data_field]
                )
                data.append(record)
            
            return data
        except Exception as e:
            raise StorageError(f"查詢MySQL數據失敗: {str(e)}")
    
    def count(self, query: Dict[str, Any] = None) -> int:
        """
        統計MySQL數據數量
        
        Args:
            query: 查詢條件，None表示所有數據
            
        Returns:
            int: 數據數量
        """
        try:
            # 構建查詢
            sql_query = self.table.select()
            
            # 添加查詢條件
            if query:
                for key, value in query.items():
                    sql_query = sql_query.where(
                        self.table.c[key] == value
                    )
            
            # 執行查詢
            result = sql_query.execute()
            
            return result.rowcount
        except Exception as e:
            raise StorageError(f"統計MySQL數據數量失敗: {str(e)}")
    
    def __del__(self):
        """清理資源"""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose() 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SQL Server存儲處理器

提供基於SQL Server的數據存儲功能，支持數據的增刪改查操作
"""

import time
import json
import functools
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from sqlalchemy import create_engine, Table, Column, String, DateTime, MetaData, schema, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.sql import Select
from ..core.base import StorageHandler
from ..core.config import SQLServerConfig
from ..core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

class SQLServerHandler(StorageHandler):
    """SQL Server存儲處理器"""
    
    def __init__(self, config: Union[Dict[str, Any], SQLServerConfig]):
        """
        初始化SQL Server存儲處理器
        
        Args:
            config: 配置對象或配置字典
        """
        super().__init__(config)
        self.engine: Optional[Engine] = None
        self.session: Optional[Session] = None
        self.table: Optional[Table] = None
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._cache_ttl = 300  # 緩存過期時間（秒）
    
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
                pool_pre_ping=True,
                echo=False,  # 關閉SQL語句日誌
                echo_pool=False,  # 關閉連接池日誌
                max_overflow=10,  # 最大溢出連接數
                pool_use_lifo=True  # 使用LIFO策略提高連接重用率
            )
            
            # 創建會話
            self.session = sessionmaker(
                bind=self.engine,
                expire_on_commit=False  # 避免提交後對象過期
            )()
            
            # 創建表
            self._create_table()
            
            self.logger.info(
                f"SQL Server存儲環境已初始化: "
                f"{self.config.host}:{self.config.port}/"
                f"{self.config.database}/{self.config.schema}/"
                f"{self.config.table_name}"
            )
        except Exception as e:
            raise ConnectionError(f"連接SQL Server失敗: {str(e)}")
    
    def _build_connection_uri(self) -> str:
        """
        構建SQL Server連接URI
        
        Returns:
            str: 連接URI
        """
        # 構建URI
        if self.config.instance:
            # 使用實例名
            return (
                f"mssql+pyodbc://{self.config.username}:{self.config.password}"
                f"@{self.config.host}\\{self.config.instance}/{self.config.database}"
                f"?driver=ODBC+Driver+17+for+SQL+Server"
                f"&fast_executemany=True"  # 啟用快速批量執行
                f"&connect_timeout=30"  # 連接超時時間
                f"&timeout=30"  # 命令超時時間
            )
        else:
            # 使用端口
            return (
                f"mssql+pyodbc://{self.config.username}:{self.config.password}"
                f"@{self.config.host}:{self.config.port}/{self.config.database}"
                f"?driver=ODBC+Driver+17+for+SQL+Server"
                f"&fast_executemany=True"  # 啟用快速批量執行
                f"&connect_timeout=30"  # 連接超時時間
                f"&timeout=30"  # 命令超時時間
            )
    
    def _create_table(self) -> None:
        """創建存儲表"""
        try:
            # 創建元數據
            metadata = MetaData(schema=self.config.schema)
            
            # 創建表
            self.table = Table(
                self.config.table_name,
                metadata,
                Column(self.config.id_field, String(255), primary_key=True),
                Column(self.config.data_field, String),
                Column(self.config.created_at_field, DateTime),
                Column(self.config.updated_at_field, DateTime),
                schema=self.config.schema
            )
            
            # 創建表（如果不存在）
            metadata.create_all(self.engine)
            
            # 創建索引
            self._create_default_indexes()
        except Exception as e:
            raise StorageError(f"創建SQL Server表失敗: {str(e)}")
    
    def _create_default_indexes(self) -> None:
        """創建默認索引"""
        try:
            # 創建更新時間索引
            self._create_index(
                f"idx_{self.config.table_name}_updated_at",
                [self.config.updated_at_field],
                False
            )
            
            # 創建創建時間索引
            self._create_index(
                f"idx_{self.config.table_name}_created_at",
                [self.config.created_at_field],
                False
            )
        except Exception as e:
            self.logger.warning(f"創建默認索引失敗: {str(e)}")
    
    def _cache_result(self, key: str, value: Any) -> None:
        """
        緩存查詢結果
        
        Args:
            key: 緩存鍵
            value: 緩存值
        """
        self._cache[key] = (value, time.time())
    
    def _get_cached_result(self, key: str) -> Optional[Any]:
        """
        獲取緩存的查詢結果
        
        Args:
            key: 緩存鍵
            
        Returns:
            Optional[Any]: 緩存的值，如果不存在或已過期則返回None
        """
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return value
            else:
                del self._cache[key]
        return None
    
    def _clear_cache(self) -> None:
        """清理過期的緩存"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if current_time - timestamp >= self._cache_ttl
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def _optimize_query(self, query: Select) -> Select:
        """
        優化SQL查詢
        
        Args:
            query: 原始查詢
            
        Returns:
            Select: 優化後的查詢
        """
        # 添加查詢提示
        query = query.with_hint(
            self.table,
            'WITH (NOLOCK)',
            dialect_name='mssql'
        )
        
        return query
    
    def save(self, data: Any, path: str) -> None:
        """
        保存數據到SQL Server
        
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
                
                # 更新緩存
                self._cache_result(path, data)
            else:
                # 添加創建時間
                record[self.config.created_at_field] = now
                
                # 插入記錄
                self.table.insert().values(**record).execute()
                
                # 添加緩存
                self._cache_result(path, data)
            
            # 提交事務
            self.session.commit()
            
            # 備份數據
            self._backup_data(data, path)
            
            self.logger.info(f"數據已保存到SQL Server: {path}")
        except Exception as e:
            # 回滾事務
            self.session.rollback()
            raise StorageError(f"保存數據到SQL Server失敗: {str(e)}")
    
    def load(self, path: str) -> Any:
        """
        從SQL Server加載數據
        
        Args:
            path: 數據路徑（作為ID）
            
        Returns:
            Any: 加載的數據
        """
        try:
            # 檢查緩存
            cached_data = self._get_cached_result(path)
            if cached_data is not None:
                return cached_data
            
            # 查詢記錄
            query = self.table.select().where(
                self.table.c[self.config.id_field] == path
            )
            
            # 優化查詢
            query = self._optimize_query(query)
            
            # 執行查詢
            result = query.execute().first()
            
            # 檢查記錄是否存在
            if not result:
                raise NotFoundError(f"數據不存在: {path}")
            
            # 反序列化數據
            data = json.loads(result[self.config.data_field])
            
            # 緩存結果
            self._cache_result(path, data)
            
            self.logger.info(f"數據已從SQL Server加載: {path}")
            return data
        except Exception as e:
            raise StorageError(f"從SQL Server加載數據失敗: {str(e)}")
    
    def delete(self, path: str) -> None:
        """
        從SQL Server刪除數據
        
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
            
            # 清理緩存
            if path in self._cache:
                del self._cache[path]
            
            self.logger.info(f"數據已從SQL Server刪除: {path}")
        except Exception as e:
            # 回滾事務
            self.session.rollback()
            raise StorageError(f"從SQL Server刪除數據失敗: {str(e)}")
    
    def exists(self, path: str) -> bool:
        """
        檢查SQL Server數據是否存在
        
        Args:
            path: 數據路徑（作為ID）
            
        Returns:
            bool: 是否存在
        """
        try:
            # 檢查緩存
            if path in self._cache:
                return True
            
            # 查詢記錄
            query = self.table.select().where(
                self.table.c[self.config.id_field] == path
            )
            
            # 優化查詢
            query = self._optimize_query(query)
            
            # 執行查詢
            result = query.execute().first()
            
            return result is not None
        except Exception as e:
            raise StorageError(f"檢查SQL Server數據是否存在失敗: {str(e)}")
    
    def list(self, path: str = None) -> List[str]:
        """
        列出SQL Server數據
        
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
            
            # 優化查詢
            query = self._optimize_query(query)
            
            # 執行查詢
            results = query.execute()
            
            # 提取路徑
            paths = [row[self.config.id_field] for row in results]
            
            return paths
        except Exception as e:
            raise StorageError(f"列出SQL Server數據失敗: {str(e)}")
    
    def find(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        查詢SQL Server數據
        
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
            
            # 優化查詢
            sql_query = self._optimize_query(sql_query)
            
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
            raise StorageError(f"查詢SQL Server數據失敗: {str(e)}")
    
    def count(self, query: Dict[str, Any] = None) -> int:
        """
        統計SQL Server數據數量
        
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
            
            # 優化查詢
            sql_query = self._optimize_query(sql_query)
            
            # 執行查詢
            result = sql_query.execute()
            
            return result.rowcount
        except Exception as e:
            raise StorageError(f"統計SQL Server數據數量失敗: {str(e)}")
    
    def batch_save(self, data_list: List[Dict[str, Any]]) -> None:
        """
        批量保存數據到SQL Server
        
        Args:
            data_list: 數據列表，每個元素為包含data和path的字典
        """
        try:
            # 獲取當前時間
            now = time.time()
            
            # 構建批量插入數據
            insert_data = []
            update_data = []
            
            for item in data_list:
                # 驗證數據
                self._validate_data(item['data'])
                
                # 序列化數據
                serialized_data = json.dumps(item['data'])
                
                # 構建記錄
                record = {
                    self.config.id_field: item['path'],
                    self.config.data_field: serialized_data,
                    self.config.updated_at_field: now
                }
                
                # 檢查記錄是否存在
                if self.exists(item['path']):
                    update_data.append(record)
                else:
                    # 添加創建時間
                    record[self.config.created_at_field] = now
                    insert_data.append(record)
                
                # 更新緩存
                self._cache_result(item['path'], item['data'])
            
            # 批量插入
            if insert_data:
                self.table.insert().values(insert_data).execute()
            
            # 批量更新
            for record in update_data:
                self.table.update().where(
                    self.table.c[self.config.id_field] == record[self.config.id_field]
                ).values(**record).execute()
            
            # 提交事務
            self.session.commit()
            
            # 備份數據
            for item in data_list:
                self._backup_data(item['data'], item['path'])
            
            self.logger.info(f"批量數據已保存到SQL Server: {len(data_list)}條")
        except Exception as e:
            # 回滾事務
            self.session.rollback()
            raise StorageError(f"批量保存數據到SQL Server失敗: {str(e)}")
    
    def batch_load(self, paths: List[str]) -> List[Dict[str, Any]]:
        """
        批量從SQL Server加載數據
        
        Args:
            paths: 數據路徑列表
            
        Returns:
            List[Dict[str, Any]]: 數據列表，每個元素為包含data和path的字典
        """
        try:
            # 檢查緩存
            data_list = []
            missing_paths = []
            
            for path in paths:
                cached_data = self._get_cached_result(path)
                if cached_data is not None:
                    data_list.append({
                        'path': path,
                        'data': cached_data
                    })
                else:
                    missing_paths.append(path)
            
            # 如果有缺失的數據，從數據庫加載
            if missing_paths:
                # 構建查詢
                query = self.table.select().where(
                    self.table.c[self.config.id_field].in_(missing_paths)
                )
                
                # 優化查詢
                query = self._optimize_query(query)
                
                # 執行查詢
                results = query.execute()
                
                # 轉換結果
                for row in results:
                    data = json.loads(row[self.config.data_field])
                    data_list.append({
                        'path': row[self.config.id_field],
                        'data': data
                    })
                    
                    # 緩存結果
                    self._cache_result(row[self.config.id_field], data)
            
            # 檢查是否所有路徑都有數據
            if len(data_list) != len(paths):
                missing_paths = set(paths) - set(item['path'] for item in data_list)
                raise NotFoundError(f"部分數據不存在: {missing_paths}")
            
            return data_list
        except Exception as e:
            raise StorageError(f"批量從SQL Server加載數據失敗: {str(e)}")
    
    def batch_delete(self, paths: List[str]) -> None:
        """
        批量從SQL Server刪除數據
        
        Args:
            paths: 數據路徑列表
        """
        try:
            # 刪除記錄
            result = self.table.delete().where(
                self.table.c[self.config.id_field].in_(paths)
            ).execute()
            
            # 檢查是否刪除成功
            if result.rowcount == 0:
                raise NotFoundError(f"數據不存在: {paths}")
            
            # 提交事務
            self.session.commit()
            
            # 清理緩存
            for path in paths:
                if path in self._cache:
                    del self._cache[path]
            
            self.logger.info(f"批量數據已從SQL Server刪除: {len(paths)}條")
        except Exception as e:
            # 回滾事務
            self.session.rollback()
            raise StorageError(f"批量從SQL Server刪除數據失敗: {str(e)}")
    
    def batch_exists(self, paths: List[str]) -> Dict[str, bool]:
        """
        批量檢查SQL Server數據是否存在
        
        Args:
            paths: 數據路徑列表
            
        Returns:
            Dict[str, bool]: 路徑到存在狀態的映射
        """
        try:
            # 檢查緩存
            exists_map = {}
            missing_paths = []
            
            for path in paths:
                if path in self._cache:
                    exists_map[path] = True
                else:
                    missing_paths.append(path)
                    exists_map[path] = False
            
            # 如果有缺失的數據，從數據庫查詢
            if missing_paths:
                # 構建查詢
                query = self.table.select().where(
                    self.table.c[self.config.id_field].in_(missing_paths)
                )
                
                # 優化查詢
                query = self._optimize_query(query)
                
                # 執行查詢
                results = query.execute()
                
                # 更新結果
                for row in results:
                    exists_map[row[self.config.id_field]] = True
            
            return exists_map
        except Exception as e:
            raise StorageError(f"批量檢查SQL Server數據是否存在失敗: {str(e)}")
    
    def migrate_data(self, target_handler: 'SQLServerHandler', batch_size: int = 1000) -> Tuple[int, int]:
        """
        遷移數據到目標SQL Server
        
        Args:
            target_handler: 目標SQL Server處理器
            batch_size: 每批處理的數據量
            
        Returns:
            Tuple[int, int]: (成功遷移的數據量, 失敗的數據量)
        """
        try:
            # 初始化計數器
            success_count = 0
            failed_count = 0
            
            # 獲取所有數據路徑
            paths = self.list()
            total_paths = len(paths)
            
            # 分批處理
            for i in range(0, total_paths, batch_size):
                batch_paths = paths[i:i + batch_size]
                
                try:
                    # 批量加載數據
                    data_list = self.batch_load(batch_paths)
                    
                    # 批量保存到目標
                    target_handler.batch_save(data_list)
                    
                    success_count += len(batch_paths)
                    self.logger.info(
                        f"數據遷移進度: {success_count}/{total_paths} "
                        f"({success_count/total_paths*100:.2f}%)"
                    )
                except Exception as e:
                    failed_count += len(batch_paths)
                    self.logger.error(f"批量遷移數據失敗: {str(e)}")
            
            self.logger.info(
                f"數據遷移完成: 成功 {success_count} 條, "
                f"失敗 {failed_count} 條"
            )
            return success_count, failed_count
        except Exception as e:
            raise StorageError(f"數據遷移失敗: {str(e)}")
    
    def migrate_schema(self, target_handler: 'SQLServerHandler') -> None:
        """
        遷移表結構到目標SQL Server
        
        Args:
            target_handler: 目標SQL Server處理器
        """
        try:
            # 獲取源表結構
            source_metadata = MetaData(schema=self.config.schema)
            source_table = Table(
                self.config.table_name,
                source_metadata,
                Column(self.config.id_field, String(255), primary_key=True),
                Column(self.config.data_field, String),
                Column(self.config.created_at_field, DateTime),
                Column(self.config.updated_at_field, DateTime),
                schema=self.config.schema
            )
            
            # 創建目標表
            target_metadata = MetaData(schema=target_handler.config.schema)
            target_table = Table(
                target_handler.config.table_name,
                target_metadata,
                Column(target_handler.config.id_field, String(255), primary_key=True),
                Column(target_handler.config.data_field, String),
                Column(target_handler.config.created_at_field, DateTime),
                Column(target_handler.config.updated_at_field, DateTime),
                schema=target_handler.config.schema
            )
            
            # 創建表
            target_metadata.create_all(target_handler.engine)
            
            self.logger.info(
                f"表結構已遷移到目標SQL Server: "
                f"{target_handler.config.host}:{target_handler.config.port}/"
                f"{target_handler.config.database}/{target_handler.config.schema}/"
                f"{target_handler.config.table_name}"
            )
        except Exception as e:
            raise StorageError(f"表結構遷移失敗: {str(e)}")
    
    def migrate_indexes(self, target_handler: 'SQLServerHandler') -> None:
        """
        遷移索引到目標SQL Server
        
        Args:
            target_handler: 目標SQL Server處理器
        """
        try:
            # 獲取源表索引
            source_indexes = self._get_table_indexes()
            
            # 創建目標表索引
            for index in source_indexes:
                target_handler._create_index(
                    index['name'],
                    index['columns'],
                    index['unique']
                )
            
            self.logger.info(
                f"索引已遷移到目標SQL Server: {len(source_indexes)}個"
            )
        except Exception as e:
            raise StorageError(f"索引遷移失敗: {str(e)}")
    
    def _get_table_indexes(self) -> List[Dict[str, Any]]:
        """
        獲取表索引信息
        
        Returns:
            List[Dict[str, Any]]: 索引信息列表
        """
        try:
            # 查詢索引信息
            query = text("""
                SELECT 
                    i.name AS index_name,
                    STRING_AGG(c.name, ',') AS column_names,
                    i.is_unique
                FROM sys.indexes i
                INNER JOIN sys.index_columns ic 
                    ON i.object_id = ic.object_id 
                    AND i.index_id = ic.index_id
                INNER JOIN sys.columns c 
                    ON ic.object_id = c.object_id 
                    AND ic.column_id = c.column_id
                WHERE i.object_id = OBJECT_ID(:table_name)
                GROUP BY i.name, i.is_unique
            """)
            
            result = self.engine.execute(
                query,
                table_name=f"{self.config.schema}.{self.config.table_name}"
            )
            
            # 轉換結果
            indexes = []
            for row in result:
                indexes.append({
                    'name': row.index_name,
                    'columns': row.column_names.split(','),
                    'unique': bool(row.is_unique)
                })
            
            return indexes
        except Exception as e:
            raise StorageError(f"獲取表索引信息失敗: {str(e)}")
    
    def _create_index(self, name: str, columns: List[str], unique: bool = False) -> None:
        """
        創建索引
        
        Args:
            name: 索引名稱
            columns: 索引列
            unique: 是否為唯一索引
        """
        try:
            # 構建索引
            index = schema.Index(
                name,
                *[self.table.c[col] for col in columns],
                unique=unique
            )
            
            # 創建索引
            index.create(self.engine)
            
            self.logger.info(f"索引已創建: {name}")
        except Exception as e:
            raise StorageError(f"創建索引失敗: {str(e)}")
    
    def __del__(self):
        """清理資源"""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose() 
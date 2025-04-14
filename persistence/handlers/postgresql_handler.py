#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PostgreSQL 存儲處理器
提供基於 PostgreSQL 的數據存儲功能，支持 CRUD 操作
"""

import time
import json
from typing import Dict, Any, List, Optional, Union, Tuple
import psycopg2
from psycopg2.extras import Json
from psycopg2.pool import ThreadedConnectionPool
from persistence.core.config import PostgreSQLConfig
from persistence.core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

class PostgreSQLHandler:
    """PostgreSQL 存儲處理器類"""
    
    def __init__(self, config: Union[Dict[str, Any], PostgreSQLConfig]):
        """初始化 PostgreSQL 存儲處理器
        
        Args:
            config: 配置對象，可以是字典或 PostgreSQLConfig 實例
        """
        if isinstance(config, dict):
            self.config = PostgreSQLConfig(**config)
        else:
            self.config = config
        
        self.pool = None
        self._setup_storage()
    
    def _setup_storage(self):
        """設置存儲環境"""
        try:
            # 創建連接池
            self.pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=self.config.pool_size,
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                database=self.config.database,
                sslmode=self.config.ssl_mode
            )
            
            # 創建表
            self._create_table()
            
            # 創建索引
            self._create_indexes()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {str(e)}")
    
    def _get_connection(self):
        """獲取連接"""
        try:
            return self.pool.getconn()
        except Exception as e:
            raise ConnectionError(f"Failed to get connection: {str(e)}")
    
    def _return_connection(self, conn):
        """歸還連接"""
        try:
            self.pool.putconn(conn)
        except Exception as e:
            raise ConnectionError(f"Failed to return connection: {str(e)}")
    
    def _create_table(self):
        """創建表"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 創建模式（如果不存在）
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {self.config.schema}")
            
            # 創建表
            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.config.schema}.{self.config.table_name} (
                {self.config.id_field} TEXT PRIMARY KEY,
                {self.config.data_field} JSONB NOT NULL,
                {self.config.created_at_field} TIMESTAMP NOT NULL,
                {self.config.updated_at_field} TIMESTAMP NOT NULL
            )
            """)
            
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise StorageError(f"Failed to create table: {str(e)}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def _create_indexes(self):
        """創建索引"""
        if not self.config.index_fields:
            return
        
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            for field in self.config.index_fields:
                index_name = f"idx_{self.config.table_name}_{field}"
                cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {index_name}
                ON {self.config.schema}.{self.config.table_name}
                USING GIN (({self.config.data_field}->'{field}'))
                """)
            
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise StorageError(f"Failed to create indexes: {str(e)}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def save(self, data: Dict[str, Any], path: str) -> None:
        """保存數據
        
        Args:
            data: 要保存的數據
            path: 數據路徑
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 檢查數據是否存在
            cursor.execute(f"""
            SELECT {self.config.id_field}
            FROM {self.config.schema}.{self.config.table_name}
            WHERE {self.config.id_field} = %s
            """, (path,))
            
            now = time.time()
            
            if cursor.fetchone():
                # 更新數據
                cursor.execute(f"""
                UPDATE {self.config.schema}.{self.config.table_name}
                SET {self.config.data_field} = %s, {self.config.updated_at_field} = %s
                WHERE {self.config.id_field} = %s
                """, (Json(data), now, path))
            else:
                # 插入數據
                cursor.execute(f"""
                INSERT INTO {self.config.schema}.{self.config.table_name}
                ({self.config.id_field}, {self.config.data_field}, {self.config.created_at_field}, {self.config.updated_at_field})
                VALUES (%s, %s, %s, %s)
                """, (path, Json(data), now, now))
            
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise StorageError(f"Failed to save data: {str(e)}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def load(self, path: str) -> Dict[str, Any]:
        """加載數據
        
        Args:
            path: 數據路徑
            
        Returns:
            加載的數據
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
            SELECT {self.config.data_field}
            FROM {self.config.schema}.{self.config.table_name}
            WHERE {self.config.id_field} = %s
            """, (path,))
            
            result = cursor.fetchone()
            
            if not result:
                raise NotFoundError(f"Data not found: {path}")
            
            return result[0]
        except NotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to load data: {str(e)}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def delete(self, path: str) -> None:
        """刪除數據
        
        Args:
            path: 數據路徑
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
            DELETE FROM {self.config.schema}.{self.config.table_name}
            WHERE {self.config.id_field} = %s
            """, (path,))
            
            if cursor.rowcount == 0:
                raise NotFoundError(f"Data not found: {path}")
            
            conn.commit()
        except NotFoundError:
            raise
        except Exception as e:
            if conn:
                conn.rollback()
            raise StorageError(f"Failed to delete data: {str(e)}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def exists(self, path: str) -> bool:
        """檢查數據是否存在
        
        Args:
            path: 數據路徑
            
        Returns:
            數據是否存在
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
            SELECT COUNT(*)
            FROM {self.config.schema}.{self.config.table_name}
            WHERE {self.config.id_field} = %s
            """, (path,))
            
            result = cursor.fetchone()
            
            return result[0] > 0
        except Exception as e:
            raise StorageError(f"Failed to check data existence: {str(e)}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def list(self, prefix: Optional[str] = None) -> List[str]:
        """列出數據路徑
        
        Args:
            prefix: 路徑前綴
            
        Returns:
            數據路徑列表
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if prefix:
                cursor.execute(f"""
                SELECT DISTINCT {self.config.id_field}
                FROM {self.config.schema}.{self.config.table_name}
                WHERE {self.config.id_field} LIKE %s
                """, (f"{prefix}%",))
            else:
                cursor.execute(f"""
                SELECT DISTINCT {self.config.id_field}
                FROM {self.config.schema}.{self.config.table_name}
                """)
            
            result = cursor.fetchall()
            
            return [row[0] for row in result]
        except Exception as e:
            raise StorageError(f"Failed to list data: {str(e)}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def find(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """查詢數據
        
        Args:
            query: 查詢條件
            
        Returns:
            查詢結果列表
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            for key, value in query.items():
                conditions.append(f"{self.config.data_field}->%s = %s")
                params.extend([key, Json(value)])
            
            sql = f"""
            SELECT {self.config.data_field}
            FROM {self.config.schema}.{self.config.table_name}
            """
            
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(sql, params)
            
            result = cursor.fetchall()
            
            return [row[0] for row in result]
        except Exception as e:
            raise StorageError(f"Failed to find data: {str(e)}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """統計數據數量
        
        Args:
            query: 查詢條件
            
        Returns:
            數據數量
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if query:
                for key, value in query.items():
                    conditions.append(f"{self.config.data_field}->%s = %s")
                    params.extend([key, Json(value)])
            
            sql = f"""
            SELECT COUNT(*)
            FROM {self.config.schema}.{self.config.table_name}
            """
            
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(sql, params)
            
            result = cursor.fetchone()
            
            return result[0]
        except Exception as e:
            raise StorageError(f"Failed to count data: {str(e)}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def batch_save(self, data_list: List[Dict[str, Any]]) -> None:
        """批量保存數據
        
        Args:
            data_list: 數據列表，每個元素包含 path 和 data
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = time.time()
            
            # 準備數據
            values = []
            for item in data_list:
                path = item["path"]
                data = item["data"]
                values.append((path, Json(data), now, now))
            
            # 批量插入
            cursor.executemany(f"""
            INSERT INTO {self.config.schema}.{self.config.table_name}
            ({self.config.id_field}, {self.config.data_field}, {self.config.created_at_field}, {self.config.updated_at_field})
            VALUES (%s, %s, %s, %s)
            ON CONFLICT ({self.config.id_field})
            DO UPDATE SET {self.config.data_field} = EXCLUDED.{self.config.data_field}, {self.config.updated_at_field} = EXCLUDED.{self.config.updated_at_field}
            """, values)
            
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise StorageError(f"Failed to batch save data: {str(e)}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def batch_load(self, paths: List[str]) -> List[Dict[str, Any]]:
        """批量加載數據
        
        Args:
            paths: 數據路徑列表
            
        Returns:
            數據列表，每個元素包含 path 和 data
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 使用 IN 子句批量查詢
            placeholders = ", ".join(["%s"] * len(paths))
            cursor.execute(f"""
            SELECT {self.config.id_field}, {self.config.data_field}
            FROM {self.config.schema}.{self.config.table_name}
            WHERE {self.config.id_field} IN ({placeholders})
            """, paths)
            
            result = cursor.fetchall()
            
            # 構建結果
            data_dict = {row[0]: row[1] for row in result}
            
            # 確保返回所有請求的路徑
            return [
                {"path": path, "data": data_dict.get(path)}
                for path in paths
            ]
        except Exception as e:
            raise StorageError(f"Failed to batch load data: {str(e)}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def batch_delete(self, paths: List[str]) -> None:
        """批量刪除數據
        
        Args:
            paths: 數據路徑列表
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 使用 IN 子句批量刪除
            placeholders = ", ".join(["%s"] * len(paths))
            cursor.execute(f"""
            DELETE FROM {self.config.schema}.{self.config.table_name}
            WHERE {self.config.id_field} IN ({placeholders})
            """, paths)
            
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise StorageError(f"Failed to batch delete data: {str(e)}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def batch_exists(self, paths: List[str]) -> Dict[str, bool]:
        """批量檢查數據是否存在
        
        Args:
            paths: 數據路徑列表
            
        Returns:
            數據存在狀態字典
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 使用 IN 子句批量查詢
            placeholders = ", ".join(["%s"] * len(paths))
            cursor.execute(f"""
            SELECT {self.config.id_field}, COUNT(*)
            FROM {self.config.schema}.{self.config.table_name}
            WHERE {self.config.id_field} IN ({placeholders})
            GROUP BY {self.config.id_field}
            """, paths)
            
            result = cursor.fetchall()
            
            # 構建結果
            exists_dict = {path: False for path in paths}
            for row in result:
                exists_dict[row[0]] = row[1] > 0
            
            return exists_dict
        except Exception as e:
            raise StorageError(f"Failed to batch check data existence: {str(e)}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def migrate_data(self, target_handler: 'PostgreSQLHandler') -> Tuple[int, int]:
        """遷移數據到目標處理器
        
        Args:
            target_handler: 目標處理器
            
        Returns:
            (成功數量, 失敗數量)
        """
        try:
            # 獲取所有數據
            paths = self.list()
            
            # 批量加載數據
            data_list = self.batch_load(paths)
            
            # 過濾掉不存在的數據
            data_list = [item for item in data_list if item["data"] is not None]
            
            # 批量保存到目標
            target_handler.batch_save(data_list)
            
            return len(data_list), 0
        except Exception as e:
            raise StorageError(f"Failed to migrate data: {str(e)}")
    
    def migrate_schema(self, target_handler: 'PostgreSQLHandler') -> None:
        """遷移表結構到目標處理器
        
        Args:
            target_handler: 目標處理器
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 獲取表結構
            cursor.execute(f"""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
            """, (self.config.schema, self.config.table_name))
            
            columns = cursor.fetchall()
            
            # 獲取索引
            cursor.execute(f"""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = %s AND tablename = %s
            """, (self.config.schema, self.config.table_name))
            
            indexes = cursor.fetchall()
            
            # 在目標創建表
            target_conn = target_handler._get_connection()
            target_cursor = target_conn.cursor()
            
            # 創建模式
            target_cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {target_handler.config.schema}")
            
            # 創建表
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {target_handler.config.schema}.{target_handler.config.table_name} (
            """
            
            column_defs = []
            for column in columns:
                column_name = column[0]
                data_type = column[1]
                max_length = column[2]
                is_nullable = column[3]
                
                if max_length:
                    column_def = f"{column_name} {data_type}({max_length})"
                else:
                    column_def = f"{column_name} {data_type}"
                
                if is_nullable == "NO":
                    column_def += " NOT NULL"
                
                column_defs.append(column_def)
            
            create_table_sql += ", ".join(column_defs)
            create_table_sql += ")"
            
            target_cursor.execute(create_table_sql)
            
            # 創建索引
            for index in indexes:
                index_name = index[0]
                index_def = index[1]
                
                # 修改索引定義以使用目標模式
                index_def = index_def.replace(
                    f"{self.config.schema}.{self.config.table_name}",
                    f"{target_handler.config.schema}.{target_handler.config.table_name}"
                )
                
                target_cursor.execute(index_def)
            
            target_conn.commit()
            target_handler._return_connection(target_conn)
        except Exception as e:
            if conn:
                conn.rollback()
            if target_conn:
                target_conn.rollback()
            raise StorageError(f"Failed to migrate schema: {str(e)}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def cleanup(self) -> None:
        """清理資源"""
        try:
            if self.pool:
                self.pool.closeall()
        except Exception as e:
            raise StorageError(f"Failed to cleanup: {str(e)}") 
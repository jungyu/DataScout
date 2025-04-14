#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ClickHouse 存儲處理器
提供基於 ClickHouse 的數據存儲功能，支持 CRUD 操作
"""

import time
import json
from typing import Dict, Any, List, Optional, Union
from clickhouse_driver import Client
from persistence.core.config import ClickHouseConfig
from persistence.core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

class ClickHouseHandler:
    """ClickHouse 存儲處理器類"""
    
    def __init__(self, config: Union[Dict[str, Any], ClickHouseConfig]):
        """初始化 ClickHouse 存儲處理器
        
        Args:
            config: 配置對象，可以是字典或 ClickHouseConfig 實例
        """
        if isinstance(config, dict):
            self.config = ClickHouseConfig(**config)
        else:
            self.config = config
        
        self.client = None
        self._setup_storage()
    
    def _setup_storage(self):
        """設置存儲環境"""
        try:
            # 創建客戶端
            self.client = Client(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                database=self.config.database,
                secure=self.config.secure,
                verify=self.config.verify,
                settings={
                    "max_execution_time": self.config.pool_timeout,
                    "max_block_size": 100000,
                    "max_threads": self.config.pool_size
                }
            )
            
            # 創建表
            self._create_table()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to ClickHouse: {str(e)}")
    
    def _create_table(self):
        """創建表"""
        try:
            # 構建建表 SQL
            sql = f"""
            CREATE TABLE IF NOT EXISTS {self.config.database}.{self.config.table_name} (
                {self.config.id_field} String,
                {self.config.data_field} String,
                {self.config.created_at_field} DateTime,
                {self.config.updated_at_field} DateTime
            )
            """
            
            # 添加分區
            if self.config.partition_by:
                sql += f" PARTITION BY {self.config.partition_by}"
            
            # 添加排序
            if self.config.order_by:
                sql += f" ORDER BY {self.config.order_by}"
            
            # 添加引擎
            if self.config.sharding_key:
                sql += f" ENGINE = Distributed({self.config.database}, {self.config.table_name}, {self.config.sharding_key}, rand())"
            else:
                sql += " ENGINE = MergeTree()"
            
            # 添加設置
            sql += f" SETTINGS storage_policy = 'hot_to_cold'"
            
            # 執行建表
            self.client.execute(sql)
        except Exception as e:
            raise StorageError(f"Failed to create table: {str(e)}")
    
    def save(self, data: Dict[str, Any], path: str) -> None:
        """保存數據
        
        Args:
            data: 要保存的數據
            path: 數據路徑
        """
        try:
            # 序列化數據
            data_str = json.dumps(data)
            
            # 構建插入 SQL
            sql = f"""
            INSERT INTO {self.config.database}.{self.config.table_name}
            ({self.config.id_field}, {self.config.data_field}, {self.config.created_at_field}, {self.config.updated_at_field})
            VALUES
            """
            
            # 構建數據
            now = time.time()
            values = [(path, data_str, now, now)]
            
            # 執行插入
            self.client.execute(sql, values)
        except Exception as e:
            raise StorageError(f"Failed to save data: {str(e)}")
    
    def load(self, path: str) -> Dict[str, Any]:
        """加載數據
        
        Args:
            path: 數據路徑
            
        Returns:
            加載的數據
        """
        try:
            # 構建查詢 SQL
            sql = f"""
            SELECT {self.config.data_field}
            FROM {self.config.database}.{self.config.table_name}
            WHERE {self.config.id_field} = %(path)s
            LIMIT 1
            """
            
            # 執行查詢
            result = self.client.execute(sql, {"path": path})
            
            # 檢查結果
            if not result:
                raise NotFoundError(f"Data not found: {path}")
            
            # 反序列化數據
            return json.loads(result[0][0])
        except NotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to load data: {str(e)}")
    
    def delete(self, path: str) -> None:
        """刪除數據
        
        Args:
            path: 數據路徑
        """
        try:
            # 構建刪除 SQL
            sql = f"""
            ALTER TABLE {self.config.database}.{self.config.table_name}
            DELETE WHERE {self.config.id_field} = %(path)s
            """
            
            # 執行刪除
            self.client.execute(sql, {"path": path})
        except Exception as e:
            raise StorageError(f"Failed to delete data: {str(e)}")
    
    def exists(self, path: str) -> bool:
        """檢查數據是否存在
        
        Args:
            path: 數據路徑
            
        Returns:
            數據是否存在
        """
        try:
            # 構建查詢 SQL
            sql = f"""
            SELECT count()
            FROM {self.config.database}.{self.config.table_name}
            WHERE {self.config.id_field} = %(path)s
            """
            
            # 執行查詢
            result = self.client.execute(sql, {"path": path})
            
            # 返回結果
            return result[0][0] > 0
        except Exception as e:
            raise StorageError(f"Failed to check data existence: {str(e)}")
    
    def list(self, prefix: Optional[str] = None) -> List[str]:
        """列出數據路徑
        
        Args:
            prefix: 路徑前綴
            
        Returns:
            數據路徑列表
        """
        try:
            # 構建查詢 SQL
            sql = f"""
            SELECT DISTINCT {self.config.id_field}
            FROM {self.config.database}.{self.config.table_name}
            """
            
            # 添加前綴條件
            if prefix:
                sql += f" WHERE {self.config.id_field} LIKE %(prefix)s"
            
            # 執行查詢
            result = self.client.execute(sql, {"prefix": f"{prefix}%" if prefix else None})
            
            # 返回結果
            return [row[0] for row in result]
        except Exception as e:
            raise StorageError(f"Failed to list data: {str(e)}")
    
    def find(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """查詢數據
        
        Args:
            query: 查詢條件
            
        Returns:
            查詢結果列表
        """
        try:
            # 構建查詢 SQL
            sql = f"""
            SELECT {self.config.data_field}
            FROM {self.config.database}.{self.config.table_name}
            WHERE 1=1
            """
            
            # 添加查詢條件
            params = {}
            for key, value in query.items():
                sql += f" AND JSONExtractString({self.config.data_field}, '{key}') = %({key})s"
                params[key] = str(value)
            
            # 執行查詢
            result = self.client.execute(sql, params)
            
            # 反序列化數據
            return [json.loads(row[0]) for row in result]
        except Exception as e:
            raise StorageError(f"Failed to find data: {str(e)}")
    
    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """統計數據數量
        
        Args:
            query: 查詢條件
            
        Returns:
            數據數量
        """
        try:
            # 構建查詢 SQL
            sql = f"""
            SELECT count()
            FROM {self.config.database}.{self.config.table_name}
            """
            
            # 添加查詢條件
            params = {}
            if query:
                sql += " WHERE 1=1"
                for key, value in query.items():
                    sql += f" AND JSONExtractString({self.config.data_field}, '{key}') = %({key})s"
                    params[key] = str(value)
            
            # 執行查詢
            result = self.client.execute(sql, params)
            
            # 返回結果
            return result[0][0]
        except Exception as e:
            raise StorageError(f"Failed to count data: {str(e)}")
    
    def batch_save(self, data_list: List[Dict[str, Any]]) -> None:
        """批量保存數據
        
        Args:
            data_list: 數據列表，每個元素包含 path 和 data
        """
        try:
            # 構建插入 SQL
            sql = f"""
            INSERT INTO {self.config.database}.{self.config.table_name}
            ({self.config.id_field}, {self.config.data_field}, {self.config.created_at_field}, {self.config.updated_at_field})
            VALUES
            """
            
            # 構建數據
            now = time.time()
            values = [
                (item["path"], json.dumps(item["data"]), now, now)
                for item in data_list
            ]
            
            # 執行插入
            self.client.execute(sql, values)
        except Exception as e:
            raise StorageError(f"Failed to batch save data: {str(e)}")
    
    def batch_load(self, paths: List[str]) -> List[Dict[str, Any]]:
        """批量加載數據
        
        Args:
            paths: 數據路徑列表
            
        Returns:
            數據列表，每個元素包含 path 和 data
        """
        try:
            # 構建查詢 SQL
            sql = f"""
            SELECT {self.config.id_field}, {self.config.data_field}
            FROM {self.config.database}.{self.config.table_name}
            WHERE {self.config.id_field} IN %(paths)s
            """
            
            # 執行查詢
            result = self.client.execute(sql, {"paths": paths})
            
            # 構建結果
            return [
                {
                    "path": row[0],
                    "data": json.loads(row[1])
                }
                for row in result
            ]
        except Exception as e:
            raise StorageError(f"Failed to batch load data: {str(e)}")
    
    def batch_delete(self, paths: List[str]) -> None:
        """批量刪除數據
        
        Args:
            paths: 數據路徑列表
        """
        try:
            # 構建刪除 SQL
            sql = f"""
            ALTER TABLE {self.config.database}.{self.config.table_name}
            DELETE WHERE {self.config.id_field} IN %(paths)s
            """
            
            # 執行刪除
            self.client.execute(sql, {"paths": paths})
        except Exception as e:
            raise StorageError(f"Failed to batch delete data: {str(e)}")
    
    def batch_exists(self, paths: List[str]) -> Dict[str, bool]:
        """批量檢查數據是否存在
        
        Args:
            paths: 數據路徑列表
            
        Returns:
            數據存在狀態字典
        """
        try:
            # 構建查詢 SQL
            sql = f"""
            SELECT {self.config.id_field}, count()
            FROM {self.config.database}.{self.config.table_name}
            WHERE {self.config.id_field} IN %(paths)s
            GROUP BY {self.config.id_field}
            """
            
            # 執行查詢
            result = self.client.execute(sql, {"paths": paths})
            
            # 構建結果
            exists_dict = {path: False for path in paths}
            for row in result:
                exists_dict[row[0]] = row[1] > 0
            
            return exists_dict
        except Exception as e:
            raise StorageError(f"Failed to batch check data existence: {str(e)}")
    
    def migrate_data(self, target_handler: 'ClickHouseHandler') -> tuple[int, int]:
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
            
            # 批量保存到目標
            target_handler.batch_save(data_list)
            
            return len(data_list), 0
        except Exception as e:
            raise StorageError(f"Failed to migrate data: {str(e)}")
    
    def migrate_schema(self, target_handler: 'ClickHouseHandler') -> None:
        """遷移表結構到目標處理器
        
        Args:
            target_handler: 目標處理器
        """
        try:
            # 獲取表結構
            sql = f"""
            SHOW CREATE TABLE {self.config.database}.{self.config.table_name}
            """
            
            result = self.client.execute(sql)
            create_sql = result[0][0]
            
            # 修改表名
            create_sql = create_sql.replace(
                f"{self.config.database}.{self.config.table_name}",
                f"{target_handler.config.database}.{target_handler.config.table_name}"
            )
            
            # 在目標執行建表
            target_handler.client.execute(create_sql)
        except Exception as e:
            raise StorageError(f"Failed to migrate schema: {str(e)}")
    
    def cleanup(self) -> None:
        """清理資源"""
        try:
            if self.client:
                self.client.disconnect()
        except Exception as e:
            raise StorageError(f"Failed to cleanup: {str(e)}") 
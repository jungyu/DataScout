#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
適配器基礎類別
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Type
from datetime import datetime
import json
import asyncio
from .logger import Logger
from .exceptions import (
    AdapterError, ValidationError, TransformationError, 
    ConnectionError, QueryError, SchemaError, MappingError,
    BatchError, IncrementalError, RollbackError, PluginError
)

class DatabaseConnection(ABC):
    """資料庫連接基礎類別"""
    
    def __init__(self, config: Dict[str, Any], logger: Optional[Logger] = None):
        """
        初始化資料庫連接
        
        Args:
            config: 連接配置
            logger: 日誌對象
        """
        self.config = config
        self.logger = logger or Logger()
        self.connection = None
        self.transaction = None
        
    @abstractmethod
    async def connect(self) -> None:
        """建立連接"""
        pass
        
    @abstractmethod
    async def disconnect(self) -> None:
        """關閉連接"""
        pass
        
    @abstractmethod
    async def begin_transaction(self) -> None:
        """開始事務"""
        pass
        
    @abstractmethod
    async def commit_transaction(self) -> None:
        """提交事務"""
        pass
        
    @abstractmethod
    async def rollback_transaction(self) -> None:
        """回滾事務"""
        pass
        
    @abstractmethod
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """執行查詢"""
        pass
        
    @abstractmethod
    async def fetch_one(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """獲取一條記錄"""
        pass
        
    @abstractmethod
    async def fetch_all(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """獲取所有記錄"""
        pass
        
    @abstractmethod
    async def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> None:
        """批量執行"""
        pass
        
    @abstractmethod
    async def get_schema(self, table: str) -> Dict[str, Any]:
        """獲取表結構"""
        pass
        
    @abstractmethod
    async def create_table(self, table: str, schema: Dict[str, Any]) -> None:
        """創建表"""
        pass
        
    @abstractmethod
    async def drop_table(self, table: str) -> None:
        """刪除表"""
        pass
        
    @abstractmethod
    async def truncate_table(self, table: str) -> None:
        """清空表"""
        pass
        
    @abstractmethod
    async def insert(self, table: str, data: Dict[str, Any]) -> Any:
        """插入數據"""
        pass
        
    @abstractmethod
    async def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """更新數據"""
        pass
        
    @abstractmethod
    async def delete(self, table: str, where: Dict[str, Any]) -> int:
        """刪除數據"""
        pass
        
    @abstractmethod
    async def bulk_insert(self, table: str, data_list: List[Dict[str, Any]]) -> None:
        """批量插入"""
        pass
        
    @abstractmethod
    async def bulk_update(self, table: str, data_list: List[Dict[str, Any]], key_fields: List[str]) -> None:
        """批量更新"""
        pass
        
    @abstractmethod
    async def bulk_delete(self, table: str, data_list: List[Dict[str, Any]], key_fields: List[str]) -> None:
        """批量刪除"""
        pass
        
    @abstractmethod
    async def get_changes(self, table: str, since: datetime) -> List[Dict[str, Any]]:
        """獲取變更"""
        pass
        
    @abstractmethod
    async def apply_changes(self, table: str, changes: List[Dict[str, Any]]) -> None:
        """應用變更"""
        pass

class BaseValidator(ABC):
    """驗證器基礎類別"""
    
    def __init__(self, config: Dict[str, Any], logger: Optional[Logger] = None):
        """
        初始化驗證器
        
        Args:
            config: 驗證配置
            logger: 日誌對象
        """
        self.config = config
        self.logger = logger or Logger()
        
    @abstractmethod
    async def validate(self, data: Any) -> bool:
        """
        驗證數據
        
        Args:
            data: 待驗證數據
            
        Returns:
            bool: 驗證結果
        """
        pass

class BaseTransformer(ABC):
    """轉換器基礎類別"""
    
    def __init__(self, config: Dict[str, Any], logger: Optional[Logger] = None):
        """
        初始化轉換器
        
        Args:
            config: 轉換配置
            logger: 日誌對象
        """
        self.config = config
        self.logger = logger or Logger()
        
    @abstractmethod
    async def transform(self, data: Any) -> Any:
        """
        轉換數據
        
        Args:
            data: 待轉換數據
            
        Returns:
            Any: 轉換後數據
        """
        pass

class BaseAdapter(ABC):
    """適配器基礎類別"""
    
    def __init__(self, config: Dict[str, Any], logger: Optional[Logger] = None):
        """
        初始化適配器
        
        Args:
            config: 適配器配置
            logger: 日誌對象
        """
        self.config = config
        self.logger = logger or Logger()
        self.validators: List[BaseValidator] = []
        self.transformers: List[BaseTransformer] = []
        self.source_connection: Optional[DatabaseConnection] = None
        self.target_connection: Optional[DatabaseConnection] = None
        
    def add_validator(self, validator: BaseValidator) -> None:
        """
        添加驗證器
        
        Args:
            validator: 驗證器對象
        """
        self.validators.append(validator)
        
    def add_transformer(self, transformer: BaseTransformer) -> None:
        """
        添加轉換器
        
        Args:
            transformer: 轉換器對象
        """
        self.transformers.append(transformer)
        
    async def validate(self, data: Any) -> bool:
        """
        驗證數據
        
        Args:
            data: 待驗證數據
            
        Returns:
            bool: 驗證結果
        """
        for validator in self.validators:
            try:
                if not await validator.validate(data):
                    return False
            except Exception as e:
                self.logger.log_error(e, {"validator": validator.__class__.__name__, "data": data})
                raise ValidationError(f"驗證失敗: {str(e)}")
        return True
        
    async def transform(self, data: Any) -> Any:
        """
        轉換數據
        
        Args:
            data: 待轉換數據
            
        Returns:
            Any: 轉換後數據
        """
        result = data
        for transformer in self.transformers:
            try:
                result = await transformer.transform(result)
            except Exception as e:
                self.logger.log_error(e, {"transformer": transformer.__class__.__name__, "data": data})
                raise TransformationError(f"轉換失敗: {str(e)}")
        return result
        
    @abstractmethod
    async def connect(self) -> None:
        """建立連接"""
        pass
        
    @abstractmethod
    async def disconnect(self) -> None:
        """關閉連接"""
        pass
        
    @abstractmethod
    async def adapt(self, source: Any, target: Any) -> None:
        """
        適配數據
        
        Args:
            source: 源數據
            target: 目標數據
        """
        pass
        
    @abstractmethod
    async def batch_process(self, source: List[Any], target: List[Any], batch_size: int = 1000) -> None:
        """
        批量處理
        
        Args:
            source: 源數據列表
            target: 目標數據列表
            batch_size: 批次大小
        """
        pass
        
    @abstractmethod
    async def stream_process(self, source: Any, target: Any) -> None:
        """
        流式處理
        
        Args:
            source: 源數據流
            target: 目標數據流
        """
        pass
        
    @abstractmethod
    async def incremental_sync(self, source: str, target: str, since: datetime) -> None:
        """
        增量同步
        
        Args:
            source: 源數據庫
            target: 目標數據庫
            since: 起始時間
        """
        pass
        
    @abstractmethod
    async def rollback(self, transaction_id: str) -> None:
        """
        回滾操作
        
        Args:
            transaction_id: 事務 ID
        """
        pass
        
    @abstractmethod
    async def get_mapping(self, source: str, target: str) -> Dict[str, str]:
        """
        獲取映射關係
        
        Args:
            source: 源字段
            target: 目標字段
            
        Returns:
            Dict[str, str]: 映射關係
        """
        pass
        
    @abstractmethod
    async def set_mapping(self, source: str, target: str, mapping: Dict[str, str]) -> None:
        """
        設置映射關係
        
        Args:
            source: 源字段
            target: 目標字段
            mapping: 映射關係
        """
        pass
        
    @abstractmethod
    async def get_schema(self, database: str, table: str) -> Dict[str, Any]:
        """
        獲取表結構
        
        Args:
            database: 數據庫名稱
            table: 表名
            
        Returns:
            Dict[str, Any]: 表結構
        """
        pass
        
    @abstractmethod
    async def create_schema(self, database: str, table: str, schema: Dict[str, Any]) -> None:
        """
        創建表結構
        
        Args:
            database: 數據庫名稱
            table: 表名
            schema: 表結構
        """
        pass
        
    @abstractmethod
    async def drop_schema(self, database: str, table: str) -> None:
        """
        刪除表結構
        
        Args:
            database: 數據庫名稱
            table: 表名
        """
        pass
        
    @abstractmethod
    async def validate_schema(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """
        驗證表結構
        
        Args:
            source: 源表結構
            target: 目標表結構
            
        Returns:
            bool: 驗證結果
        """
        pass
        
    @abstractmethod
    async def transform_schema(self, source: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
        """
        轉換表結構
        
        Args:
            source: 源表結構
            target: 目標表結構
            
        Returns:
            Dict[str, Any]: 轉換後表結構
        """
        pass
        
    @abstractmethod
    async def get_plugins(self) -> List[str]:
        """
        獲取插件列表
        
        Returns:
            List[str]: 插件列表
        """
        pass
        
    @abstractmethod
    async def load_plugin(self, plugin: str) -> None:
        """
        加載插件
        
        Args:
            plugin: 插件名稱
        """
        pass
        
    @abstractmethod
    async def unload_plugin(self, plugin: str) -> None:
        """
        卸載插件
        
        Args:
            plugin: 插件名稱
        """
        pass
        
    @abstractmethod
    async def execute_plugin(self, plugin: str, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        執行插件
        
        Args:
            plugin: 插件名稱
            action: 操作類型
            params: 參數
            
        Returns:
            Any: 執行結果
        """
        pass 
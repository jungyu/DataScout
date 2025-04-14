#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Redis存儲處理器

提供基於Redis的數據存儲功能，支持鍵值對的增刪改查操作
"""

import time
import json
import pickle
import msgpack
from typing import Dict, Any, List, Optional, Union
from redis import Redis, ConnectionPool
from ..core.base import StorageHandler
from ..core.config import RedisConfig
from ..core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

class RedisHandler(StorageHandler):
    """Redis存儲處理器"""
    
    def __init__(self, config: Union[Dict[str, Any], RedisConfig]):
        """
        初始化Redis存儲處理器
        
        Args:
            config: 配置對象或配置字典
        """
        super().__init__(config)
        self.client: Optional[Redis] = None
        self.pool: Optional[ConnectionPool] = None
    
    def _setup_storage(self) -> None:
        """設置存儲環境"""
        try:
            # 創建連接池
            self.pool = ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                db=self.config.db,
                max_connections=self.config.max_connections,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                decode_responses=True
            )
            
            # 創建Redis客戶端
            self.client = Redis(connection_pool=self.pool)
            
            # 測試連接
            self.client.ping()
            
            self.logger.info(
                f"Redis存儲環境已初始化: "
                f"{self.config.host}:{self.config.port}/"
                f"{self.config.db}"
            )
        except Exception as e:
            raise ConnectionError(f"連接Redis失敗: {str(e)}")
    
    def _serialize(self, data: Any) -> str:
        """
        序列化數據
        
        Args:
            data: 要序列化的數據
            
        Returns:
            str: 序列化後的字符串
        """
        try:
            if self.config.serializer == 'json':
                return json.dumps(data)
            elif self.config.serializer == 'pickle':
                return pickle.dumps(data).hex()
            elif self.config.serializer == 'msgpack':
                return msgpack.packb(data).hex()
            else:
                raise ValidationError(f"不支持的序列化器: {self.config.serializer}")
        except Exception as e:
            raise ValidationError(f"序列化數據失敗: {str(e)}")
    
    def _deserialize(self, data: str) -> Any:
        """
        反序列化數據
        
        Args:
            data: 要反序列化的字符串
            
        Returns:
            Any: 反序列化後的數據
        """
        try:
            if self.config.serializer == 'json':
                return json.loads(data)
            elif self.config.serializer == 'pickle':
                return pickle.loads(bytes.fromhex(data))
            elif self.config.serializer == 'msgpack':
                return msgpack.unpackb(bytes.fromhex(data))
            else:
                raise ValidationError(f"不支持的序列化器: {self.config.serializer}")
        except Exception as e:
            raise ValidationError(f"反序列化數據失敗: {str(e)}")
    
    def _build_key(self, path: str) -> str:
        """
        構建Redis鍵
        
        Args:
            path: 原始路徑
            
        Returns:
            str: Redis鍵
        """
        if self.config.key_prefix:
            return f"{self.config.key_prefix}{self.config.key_separator}{path}"
        return path
    
    def save(self, data: Any, path: str) -> None:
        """
        保存數據到Redis
        
        Args:
            data: 要保存的數據
            path: 鍵路徑
        """
        try:
            # 驗證數據
            self._validate_data(data)
            
            # 序列化數據
            serialized_data = self._serialize(data)
            
            # 構建鍵
            key = self._build_key(path)
            
            # 保存數據
            self.client.set(key, serialized_data)
            
            # 備份數據
            self._backup_data(data, path)
            
            self.logger.info(f"數據已保存到Redis: {key}")
        except Exception as e:
            raise StorageError(f"保存數據到Redis失敗: {str(e)}")
    
    def load(self, path: str) -> Any:
        """
        從Redis加載數據
        
        Args:
            path: 鍵路徑
            
        Returns:
            Any: 加載的數據
        """
        try:
            # 構建鍵
            key = self._build_key(path)
            
            # 獲取數據
            serialized_data = self.client.get(key)
            
            # 檢查數據是否存在
            if serialized_data is None:
                raise NotFoundError(f"數據不存在: {key}")
            
            # 反序列化數據
            data = self._deserialize(serialized_data)
            
            self.logger.info(f"數據已從Redis加載: {key}")
            return data
        except Exception as e:
            raise StorageError(f"從Redis加載數據失敗: {str(e)}")
    
    def delete(self, path: str) -> None:
        """
        從Redis刪除數據
        
        Args:
            path: 鍵路徑
        """
        try:
            # 構建鍵
            key = self._build_key(path)
            
            # 刪除數據
            result = self.client.delete(key)
            
            # 檢查是否刪除成功
            if result == 0:
                raise NotFoundError(f"數據不存在: {key}")
            
            self.logger.info(f"數據已從Redis刪除: {key}")
        except Exception as e:
            raise StorageError(f"從Redis刪除數據失敗: {str(e)}")
    
    def exists(self, path: str) -> bool:
        """
        檢查Redis數據是否存在
        
        Args:
            path: 鍵路徑
            
        Returns:
            bool: 是否存在
        """
        try:
            # 構建鍵
            key = self._build_key(path)
            
            # 檢查數據是否存在
            return bool(self.client.exists(key))
        except Exception as e:
            raise StorageError(f"檢查Redis數據是否存在失敗: {str(e)}")
    
    def list(self, path: str = None) -> List[str]:
        """
        列出Redis鍵
        
        Args:
            path: 鍵路徑前綴，None表示所有鍵
            
        Returns:
            List[str]: 鍵列表
        """
        try:
            # 構建模式
            pattern = self._build_key(path or '*')
            
            # 獲取鍵列表
            keys = self.client.keys(pattern)
            
            # 移除前綴
            if self.config.key_prefix:
                prefix = f"{self.config.key_prefix}{self.config.key_separator}"
                keys = [k[len(prefix):] for k in keys]
            
            return keys
        except Exception as e:
            raise StorageError(f"列出Redis鍵失敗: {str(e)}")
    
    def set_expire(self, path: str, seconds: int) -> None:
        """
        設置Redis鍵的過期時間
        
        Args:
            path: 鍵路徑
            seconds: 過期時間（秒）
        """
        try:
            # 構建鍵
            key = self._build_key(path)
            
            # 設置過期時間
            self.client.expire(key, seconds)
            
            self.logger.info(f"Redis鍵過期時間已設置: {key}, {seconds}秒")
        except Exception as e:
            raise StorageError(f"設置Redis鍵過期時間失敗: {str(e)}")
    
    def get_expire(self, path: str) -> int:
        """
        獲取Redis鍵的過期時間
        
        Args:
            path: 鍵路徑
            
        Returns:
            int: 過期時間（秒），-1表示永不過期，-2表示鍵不存在
        """
        try:
            # 構建鍵
            key = self._build_key(path)
            
            # 獲取過期時間
            return self.client.ttl(key)
        except Exception as e:
            raise StorageError(f"獲取Redis鍵過期時間失敗: {str(e)}")
    
    def increment(self, path: str, amount: int = 1) -> int:
        """
        增加Redis鍵的值
        
        Args:
            path: 鍵路徑
            amount: 增加量
            
        Returns:
            int: 增加後的值
        """
        try:
            # 構建鍵
            key = self._build_key(path)
            
            # 增加值
            return self.client.incrby(key, amount)
        except Exception as e:
            raise StorageError(f"增加Redis鍵值失敗: {str(e)}")
    
    def decrement(self, path: str, amount: int = 1) -> int:
        """
        減少Redis鍵的值
        
        Args:
            path: 鍵路徑
            amount: 減少量
            
        Returns:
            int: 減少後的值
        """
        try:
            # 構建鍵
            key = self._build_key(path)
            
            # 減少值
            return self.client.decrby(key, amount)
        except Exception as e:
            raise StorageError(f"減少Redis鍵值失敗: {str(e)}")
    
    def __del__(self):
        """清理資源"""
        if self.client:
            self.client.close() 
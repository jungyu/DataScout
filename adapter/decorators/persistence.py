#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
持久化裝飾器
提供資料驗證、轉換、加密、壓縮等功能
"""

import functools
import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Type, TypeVar, Callable, Union
from datetime import datetime
import json
import zlib
import base64
from cryptography.fernet import Fernet
from ..core.exceptions import (
    ValidationError,
    DatabaseError,
    ConnectionError,
    AuthenticationError
)

T = TypeVar('T')

class PersistenceDecorator:
    """持久化裝飾器"""
    
    def __init__(
        self,
        retry_config: Optional[Dict[str, Any]] = None,
        pool_config: Optional[Dict[str, Any]] = None,
        transaction_config: Optional[Dict[str, Any]] = None,
        cache_config: Optional[Dict[str, Any]] = None,
        validation_config: Optional[Dict[str, Any]] = None,
        encryption_config: Optional[Dict[str, Any]] = None,
        compression_config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化裝飾器
        
        Args:
            retry_config: 重試配置
            pool_config: 連接池配置
            transaction_config: 事務配置
            cache_config: 快取配置
            validation_config: 驗證配置
            encryption_config: 加密配置
            compression_config: 壓縮配置
        """
        self.retry_config = retry_config or {
            "max_attempts": 3,
            "delay": 1.0,
            "backoff_factor": 2.0
        }
        
        self.pool_config = pool_config or {
            "min_size": 5,
            "max_size": 20,
            "timeout": 30.0
        }
        
        self.transaction_config = transaction_config or {
            "timeout": 30.0,
            "isolation_level": "read_committed"
        }
        
        self.cache_config = cache_config or {
            "enabled": True,
            "ttl": 300,
            "max_size": 1000
        }
        
        self.validation_config = validation_config or {
            "enabled": True,
            "strict": True
        }
        
        self.encryption_config = encryption_config or {
            "enabled": False,
            "key": None
        }
        
        self.compression_config = compression_config or {
            "enabled": False,
            "level": 6
        }
        
        self.logger = logging.getLogger(__name__)
        self._cache = {}
        self._pool = None
        self._fernet = None
        
        if self.encryption_config["enabled"]:
            key = self.encryption_config["key"]
            if not key:
                key = Fernet.generate_key()
                self.encryption_config["key"] = key
            self._fernet = Fernet(key)
            
    def __call__(self, cls: Type[T]) -> Type[T]:
        """
        裝飾器調用
        
        Args:
            cls: 被裝飾的類別
            
        Returns:
            Type[T]: 裝飾後的類別
        """
        # 保存原始方法
        original_methods = {}
        for name, method in cls.__dict__.items():
            if callable(method) and not name.startswith("_"):
                original_methods[name] = method
                
        # 裝飾方法
        for name, method in original_methods.items():
            setattr(cls, name, self._decorate_method(method))
            
        return cls
        
    def _decorate_method(self, method: Callable) -> Callable:
        """
        裝飾方法
        
        Args:
            method: 原始方法
            
        Returns:
            Callable: 裝飾後的方法
        """
        @functools.wraps(method)
        async def wrapper(*args, **kwargs):
            # 開始時間
            start_time = time.time()
            
            # 重試邏輯
            attempt = 0
            last_error = None
            
            while attempt < self.retry_config["max_attempts"]:
                try:
                    # 驗證參數
                    if self.validation_config["enabled"]:
                        self._validate_args(args, kwargs)
                        
                    # 加密資料
                    if self.encryption_config["enabled"]:
                        args, kwargs = self._encrypt_data(args, kwargs)
                        
                    # 壓縮資料
                    if self.compression_config["enabled"]:
                        args, kwargs = self._compress_data(args, kwargs)
                        
                    # 檢查快取
                    if self.cache_config["enabled"]:
                        cache_key = self._generate_cache_key(method, args, kwargs)
                        cached_result = self._get_from_cache(cache_key)
                        if cached_result is not None:
                            return cached_result
                            
                    # 執行方法
                    result = await method(*args, **kwargs)
                    
                    # 解密結果
                    if self.encryption_config["enabled"]:
                        result = self._decrypt_data(result)
                        
                    # 解壓縮結果
                    if self.compression_config["enabled"]:
                        result = self._decompress_data(result)
                        
                    # 驗證結果
                    if self.validation_config["enabled"]:
                        self._validate_result(result)
                        
                    # 存入快取
                    if self.cache_config["enabled"]:
                        self._add_to_cache(cache_key, result)
                        
                    # 記錄性能指標
                    self._log_performance(method, time.time() - start_time)
                    
                    return result
                    
                except (ConnectionError, AuthenticationError) as e:
                    # 這些錯誤不需要重試
                    raise
                    
                except Exception as e:
                    last_error = e
                    attempt += 1
                    
                    if attempt < self.retry_config["max_attempts"]:
                        delay = self.retry_config["delay"] * (
                            self.retry_config["backoff_factor"] ** (attempt - 1)
                        )
                        await asyncio.sleep(delay)
                        continue
                        
            # 所有重試都失敗
            raise DatabaseError(f"操作失敗: {str(last_error)}")
            
        return wrapper
        
    def _validate_args(self, args: tuple, kwargs: dict) -> None:
        """
        驗證參數
        
        Args:
            args: 位置參數
            kwargs: 關鍵字參數
            
        Raises:
            ValidationError: 驗證錯誤
        """
        # 檢查必要參數
        for arg in args:
            if arg is None:
                raise ValidationError("參數不能為 None")
                
        for key, value in kwargs.items():
            if value is None:
                raise ValidationError(f"參數 {key} 不能為 None")
                
    def _validate_result(self, result: Any) -> None:
        """
        驗證結果
        
        Args:
            result: 結果
            
        Raises:
            ValidationError: 驗證錯誤
        """
        if result is None:
            raise ValidationError("結果不能為 None")
            
    def _encrypt_data(self, args: tuple, kwargs: dict) -> tuple:
        """
        加密資料
        
        Args:
            args: 位置參數
            kwargs: 關鍵字參數
            
        Returns:
            tuple: 加密後的參數
        """
        if not self._fernet:
            return args, kwargs
            
        encrypted_args = []
        for arg in args:
            if isinstance(arg, (str, bytes)):
                encrypted_args.append(self._fernet.encrypt(str(arg).encode()))
            else:
                encrypted_args.append(arg)
                
        encrypted_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, (str, bytes)):
                encrypted_kwargs[key] = self._fernet.encrypt(str(value).encode())
            else:
                encrypted_kwargs[key] = value
                
        return tuple(encrypted_args), encrypted_kwargs
        
    def _decrypt_data(self, data: Any) -> Any:
        """
        解密資料
        
        Args:
            data: 要解密的資料
            
        Returns:
            Any: 解密後的資料
        """
        if not self._fernet:
            return data
            
        if isinstance(data, bytes):
            return self._fernet.decrypt(data).decode()
            
        if isinstance(data, dict):
            return {
                key: self._decrypt_data(value)
                for key, value in data.items()
            }
            
        if isinstance(data, list):
            return [self._decrypt_data(item) for item in data]
            
        return data
        
    def _compress_data(self, args: tuple, kwargs: dict) -> tuple:
        """
        壓縮資料
        
        Args:
            args: 位置參數
            kwargs: 關鍵字參數
            
        Returns:
            tuple: 壓縮後的參數
        """
        compressed_args = []
        for arg in args:
            if isinstance(arg, (str, bytes)):
                compressed_args.append(
                    base64.b64encode(
                        zlib.compress(
                            str(arg).encode(),
                            level=self.compression_config["level"]
                        )
                    )
                )
            else:
                compressed_args.append(arg)
                
        compressed_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, (str, bytes)):
                compressed_kwargs[key] = base64.b64encode(
                    zlib.compress(
                        str(value).encode(),
                        level=self.compression_config["level"]
                    )
                )
            else:
                compressed_kwargs[key] = value
                
        return tuple(compressed_args), compressed_kwargs
        
    def _decompress_data(self, data: Any) -> Any:
        """
        解壓縮資料
        
        Args:
            data: 要解壓縮的資料
            
        Returns:
            Any: 解壓縮後的資料
        """
        if isinstance(data, bytes):
            return zlib.decompress(base64.b64decode(data)).decode()
            
        if isinstance(data, dict):
            return {
                key: self._decompress_data(value)
                for key, value in data.items()
            }
            
        if isinstance(data, list):
            return [self._decompress_data(item) for item in data]
            
        return data
        
    def _generate_cache_key(self, method: Callable, args: tuple, kwargs: dict) -> str:
        """
        生成快取鍵
        
        Args:
            method: 方法
            args: 位置參數
            kwargs: 關鍵字參數
            
        Returns:
            str: 快取鍵
        """
        key_parts = [
            method.__name__,
            str(args),
            str(sorted(kwargs.items()))
        ]
        return ":".join(key_parts)
        
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """
        從快取獲取資料
        
        Args:
            key: 快取鍵
            
        Returns:
            Optional[Any]: 快取資料
        """
        if key not in self._cache:
            return None
            
        cache_entry = self._cache[key]
        if time.time() - cache_entry["timestamp"] > self.cache_config["ttl"]:
            del self._cache[key]
            return None
            
        return cache_entry["data"]
        
    def _add_to_cache(self, key: str, data: Any) -> None:
        """
        添加資料到快取
        
        Args:
            key: 快取鍵
            data: 要快取的資料
        """
        # 檢查快取大小
        if len(self._cache) >= self.cache_config["max_size"]:
            # 刪除最舊的項目
            oldest_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k]["timestamp"]
            )
            del self._cache[oldest_key]
            
        self._cache[key] = {
            "data": data,
            "timestamp": time.time()
        }
        
    def _log_performance(self, method: Callable, duration: float) -> None:
        """
        記錄性能指標
        
        Args:
            method: 方法
            duration: 執行時間
        """
        self.logger.info(
            f"方法 {method.__name__} 執行時間: {duration:.3f} 秒"
        )
        
def persistence(
    retry_config: Optional[Dict[str, Any]] = None,
    pool_config: Optional[Dict[str, Any]] = None,
    transaction_config: Optional[Dict[str, Any]] = None,
    cache_config: Optional[Dict[str, Any]] = None,
    validation_config: Optional[Dict[str, Any]] = None,
    encryption_config: Optional[Dict[str, Any]] = None,
    compression_config: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    持久化裝飾器工廠函數
    
    Args:
        retry_config: 重試配置
        pool_config: 連接池配置
        transaction_config: 事務配置
        cache_config: 快取配置
        validation_config: 驗證配置
        encryption_config: 加密配置
        compression_config: 壓縮配置
        
    Returns:
        Callable: 裝飾器
    """
    decorator = PersistenceDecorator(
        retry_config=retry_config,
        pool_config=pool_config,
        transaction_config=transaction_config,
        cache_config=cache_config,
        validation_config=validation_config,
        encryption_config=encryption_config,
        compression_config=compression_config
    )
    return decorator 
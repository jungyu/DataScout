#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
緩存提取器模組

提供提取器緩存功能，包括：
1. 結果緩存
2. 選擇器緩存
3. 元素緩存
4. 緩存管理
"""

from typing import Dict, List, Optional, Union, Any, Set, Callable, Type
from dataclasses import dataclass
import hashlib
import json
import time
import os
from datetime import datetime, timedelta
import pickle
import threading
from functools import wraps

from ..core.base import BaseExtractor
from ..core.error import handle_extractor_error, ExtractorError

@dataclass
class CacheConfig:
    """緩存配置"""
    # 緩存設置
    enabled: bool = True
    cache_dir: str = ".cache"
    max_size: int = 1000
    max_age: int = 3600  # 秒
    cleanup_interval: int = 300  # 秒
    
    # 緩存策略
    cache_results: bool = True
    cache_selectors: bool = True
    cache_elements: bool = True
    cache_validation: bool = True
    
    # 緩存鍵生成
    key_prefix: str = ""
    key_suffix: str = ""
    include_timestamp: bool = False
    include_url: bool = True
    include_selector: bool = True
    
    # 緩存驗證
    validate_cache: bool = True
    validation_timeout: float = 5.0
    validation_retries: int = 3
    
    def __post_init__(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

class CacheExtractor(BaseExtractor):
    """緩存提取器類別"""
    
    def __init__(self, driver: Any, config: Optional[CacheConfig] = None):
        """初始化緩存提取器
        
        Args:
            driver: WebDriver 實例
            config: 緩存配置
        """
        super().__init__(driver)
        self.config = config or CacheConfig()
        self._cache: Dict[str, Any] = {}
        self._cache_lock = threading.Lock()
        self._last_cleanup = time.time()
        
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """生成緩存鍵
        
        Args:
            *args: 位置參數
            **kwargs: 關鍵字參數
            
        Returns:
            str: 緩存鍵
        """
        key_parts = []
        
        if self.config.key_prefix:
            key_parts.append(self.config.key_prefix)
            
        if self.config.include_timestamp:
            key_parts.append(str(int(time.time())))
            
        if self.config.include_url:
            key_parts.append(self.driver.current_url)
            
        if self.config.include_selector:
            if "selector" in kwargs:
                key_parts.append(kwargs["selector"])
            elif args and isinstance(args[0], str):
                key_parts.append(args[0])
                
        key_parts.extend(str(arg) for arg in args[1:])
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        
        if self.config.key_suffix:
            key_parts.append(self.config.key_suffix)
            
        key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
        return key
        
    def _get_cache_path(self, key: str) -> str:
        """獲取緩存文件路徑
        
        Args:
            key: 緩存鍵
            
        Returns:
            str: 緩存文件路徑
        """
        return os.path.join(self.config.cache_dir, f"{key}.cache")
        
    @handle_extractor_error()
    def get_cache(self, key: str) -> Optional[Any]:
        """獲取緩存
        
        Args:
            key: 緩存鍵
            
        Returns:
            Optional[Any]: 緩存數據
        """
        if not self.config.enabled:
            return None
            
        with self._cache_lock:
            # 檢查內存緩存
            if key in self._cache:
                cache_data = self._cache[key]
                if time.time() - cache_data["timestamp"] <= self.config.max_age:
                    return cache_data["data"]
                else:
                    del self._cache[key]
                    
            # 檢查文件緩存
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, "rb") as f:
                        cache_data = pickle.load(f)
                    if time.time() - cache_data["timestamp"] <= self.config.max_age:
                        self._cache[key] = cache_data
                        return cache_data["data"]
                    else:
                        os.remove(cache_path)
                except Exception:
                    if os.path.exists(cache_path):
                        os.remove(cache_path)
                        
        return None
        
    @handle_extractor_error()
    def set_cache(self, key: str, data: Any) -> None:
        """設置緩存
        
        Args:
            key: 緩存鍵
            data: 緩存數據
        """
        if not self.config.enabled:
            return
            
        with self._cache_lock:
            # 檢查緩存大小
            if len(self._cache) >= self.config.max_size:
                self._cleanup_cache()
                
            # 設置內存緩存
            cache_data = {
                "timestamp": time.time(),
                "data": data
            }
            self._cache[key] = cache_data
            
            # 設置文件緩存
            cache_path = self._get_cache_path(key)
            try:
                with open(cache_path, "wb") as f:
                    pickle.dump(cache_data, f)
            except Exception:
                if os.path.exists(cache_path):
                    os.remove(cache_path)
                    
    @handle_extractor_error()
    def _cleanup_cache(self) -> None:
        """清理緩存"""
        current_time = time.time()
        
        # 定期清理
        if current_time - self._last_cleanup >= self.config.cleanup_interval:
            self._last_cleanup = current_time
            
            # 清理內存緩存
            expired_keys = [
                key for key, data in self._cache.items()
                if current_time - data["timestamp"] > self.config.max_age
            ]
            for key in expired_keys:
                del self._cache[key]
                
            # 清理文件緩存
            for filename in os.listdir(self.config.cache_dir):
                if filename.endswith(".cache"):
                    file_path = os.path.join(self.config.cache_dir, filename)
                    try:
                        if current_time - os.path.getmtime(file_path) > self.config.max_age:
                            os.remove(file_path)
                    except Exception:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            
        # 強制清理
        if len(self._cache) >= self.config.max_size:
            # 按時間排序
            sorted_items = sorted(
                self._cache.items(),
                key=lambda x: x[1]["timestamp"]
            )
            
            # 刪除最舊的項目
            items_to_remove = len(self._cache) - self.config.max_size + 1
            for key, _ in sorted_items[:items_to_remove]:
                del self._cache[key]
                
    @handle_extractor_error()
    def clear_cache(self) -> None:
        """清除所有緩存"""
        with self._cache_lock:
            # 清除內存緩存
            self._cache.clear()
            
            # 清除文件緩存
            for filename in os.listdir(self.config.cache_dir):
                if filename.endswith(".cache"):
                    file_path = os.path.join(self.config.cache_dir, filename)
                    try:
                        os.remove(file_path)
                    except Exception:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            
    @handle_extractor_error()
    def get_cache_stats(self) -> Dict[str, Any]:
        """獲取緩存統計信息
        
        Returns:
            Dict[str, Any]: 緩存統計信息
        """
        stats = {
            "memory_cache_size": len(self._cache),
            "file_cache_size": len([
                f for f in os.listdir(self.config.cache_dir)
                if f.endswith(".cache")
            ]),
            "total_size": 0,
            "oldest_item": None,
            "newest_item": None
        }
        
        # 計算文件大小
        for filename in os.listdir(self.config.cache_dir):
            if filename.endswith(".cache"):
                file_path = os.path.join(self.config.cache_dir, filename)
                try:
                    stats["total_size"] += os.path.getsize(file_path)
                except Exception:
                    pass
                    
        # 計算時間範圍
        if self._cache:
            timestamps = [data["timestamp"] for data in self._cache.values()]
            stats["oldest_item"] = datetime.fromtimestamp(min(timestamps))
            stats["newest_item"] = datetime.fromtimestamp(max(timestamps))
            
        return stats
        
    def cache_result(self, func: Callable) -> Callable:
        """結果緩存裝飾器
        
        Args:
            func: 被裝飾的函數
            
        Returns:
            Callable: 裝飾後的函數
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.config.enabled or not self.config.cache_results:
                return func(*args, **kwargs)
                
            key = self._generate_cache_key(*args, **kwargs)
            cached_result = self.get_cache(key)
            
            if cached_result is not None:
                return cached_result
                
            result = func(*args, **kwargs)
            self.set_cache(key, result)
            return result
            
        return wrapper
        
    def cache_selector(self, func: Callable) -> Callable:
        """選擇器緩存裝飾器
        
        Args:
            func: 被裝飾的函數
            
        Returns:
            Callable: 裝飾後的函數
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.config.enabled or not self.config.cache_selectors:
                return func(*args, **kwargs)
                
            key = self._generate_cache_key(*args, **kwargs)
            cached_result = self.get_cache(key)
            
            if cached_result is not None:
                if self.config.validate_cache:
                    try:
                        # 驗證緩存的選擇器是否仍然有效
                        self.driver.find_element(By.CSS_SELECTOR, cached_result)
                        return cached_result
                    except Exception:
                        # 選擇器無效，刪除緩存
                        with self._cache_lock:
                            if key in self._cache:
                                del self._cache[key]
                            cache_path = self._get_cache_path(key)
                            if os.path.exists(cache_path):
                                os.remove(cache_path)
                                
                else:
                    return cached_result
                    
            result = func(*args, **kwargs)
            self.set_cache(key, result)
            return result
            
        return wrapper
        
    def cache_element(self, func: Callable) -> Callable:
        """元素緩存裝飾器
        
        Args:
            func: 被裝飾的函數
            
        Returns:
            Callable: 裝飾後的函數
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.config.enabled or not self.config.cache_elements:
                return func(*args, **kwargs)
                
            key = self._generate_cache_key(*args, **kwargs)
            cached_result = self.get_cache(key)
            
            if cached_result is not None:
                if self.config.validate_cache:
                    try:
                        # 驗證緩存的元素是否仍然有效
                        self.driver.execute_script("return arguments[0].offsetParent !== null", cached_result)
                        return cached_result
                    except Exception:
                        # 元素無效，刪除緩存
                        with self._cache_lock:
                            if key in self._cache:
                                del self._cache[key]
                            cache_path = self._get_cache_path(key)
                            if os.path.exists(cache_path):
                                os.remove(cache_path)
                                
                else:
                    return cached_result
                    
            result = func(*args, **kwargs)
            self.set_cache(key, result)
            return result
            
        return wrapper
        
    def cache_validation(self, func: Callable) -> Callable:
        """驗證緩存裝飾器
        
        Args:
            func: 被裝飾的函數
            
        Returns:
            Callable: 裝飾後的函數
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.config.enabled or not self.config.cache_validation:
                return func(*args, **kwargs)
                
            key = self._generate_cache_key(*args, **kwargs)
            cached_result = self.get_cache(key)
            
            if cached_result is not None:
                return cached_result
                
            result = func(*args, **kwargs)
            self.set_cache(key, result)
            return result
            
        return wrapper 
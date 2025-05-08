#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提取器管理器模組

提供提取器的管理功能，包括：
1. 提取器註冊
2. 提取器獲取
3. 提取器配置
4. 提取器狀態
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, Union

# 修正相對導入問題
from .error import handle_error, ExtractorError, handle_extractor_error
from .base import BaseExtractor

# 導入配置相關類型，使用簡單的字典替代
class BaseConfig:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
    def __getitem__(self, key):
        return self.config.get(key)
        
    def __setitem__(self, key, value):
        self.config[key] = value
        
    def get(self, key, default=None):
        return self.config.get(key, default)

class BaseExtractorManager(ABC):
    """基礎提取器管理器類別"""
    
    def __init__(
        self,
        config: Optional[Union[Dict[str, Any], BaseConfig]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化提取器管理器
        
        Args:
            config: 配置字典或配置對象
            logger: 日誌記錄器
        """
        self.config = config if isinstance(config, BaseConfig) else BaseConfig(config or {})
        # 使用標準 logging 模組而非未定義的 get_logger 函數
        self.logger = logger or logging.getLogger(__name__)
        self._extractors: Dict[str, Type[BaseExtractor]] = {}
        self._instances: Dict[str, BaseExtractor] = {}
        
    @handle_extractor_error()
    def register(self, name: str, extractor: Type[BaseExtractor]) -> None:
        """
        註冊提取器
        
        Args:
            name: 提取器名稱
            extractor: 提取器類別
        """
        if name in self._extractors:
            raise ExtractorError(f"提取器已存在：{name}")
            
        self._extractors[name] = extractor
        
    @handle_extractor_error()
    def unregister(self, name: str) -> None:
        """
        註銷提取器
        
        Args:
            name: 提取器名稱
        """
        if name in self._extractors:
            del self._extractors[name]
            
    @handle_extractor_error()
    def get_extractor(self, name: str) -> Type[BaseExtractor]:
        """
        獲取提取器類別
        
        Args:
            name: 提取器名稱
            
        Returns:
            提取器類別
        """
        if name not in self._extractors:
            raise ExtractorError(f"提取器不存在：{name}")
            
        return self._extractors[name]
        
    @handle_extractor_error()
    def create_extractor(self, name: str, **kwargs: Any) -> BaseExtractor:
        """
        創建提取器實例
        
        Args:
            name: 提取器名稱
            **kwargs: 初始化參數
            
        Returns:
            提取器實例
        """
        extractor_class = self.get_extractor(name)
        instance = extractor_class(config=self.config, logger=self.logger, **kwargs)
        self._instances[name] = instance
        return instance
        
    @handle_extractor_error()
    def get_instance(self, name: str) -> BaseExtractor:
        """
        獲取提取器實例
        
        Args:
            name: 提取器名稱
            
        Returns:
            提取器實例
        """
        if name not in self._instances:
            raise ExtractorError(f"提取器實例不存在：{name}")
            
        return self._instances[name]
        
    @handle_extractor_error()
    def remove_instance(self, name: str) -> None:
        """
        移除提取器實例
        
        Args:
            name: 提取器名稱
        """
        if name in self._instances:
            del self._instances[name]
            
    @handle_extractor_error()
    def clear_instances(self) -> None:
        """清空所有提取器實例"""
        self._instances.clear()
        
    @handle_extractor_error()
    def setup(self) -> None:
        """設置提取器管理器環境"""
        self._setup()
        
    @abstractmethod
    def _setup(self) -> None:
        """具體的設置邏輯"""
        pass
        
    @handle_extractor_error()
    def cleanup(self) -> None:
        """清理提取器管理器環境"""
        self._cleanup()
        self.clear_instances()
        
    @abstractmethod
    def _cleanup(self) -> None:
        """具體的清理邏輯"""
        pass
        
    def __enter__(self) -> 'BaseExtractorManager':
        """上下文管理器入口"""
        self.setup()
        return self
        
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """上下文管理器出口"""
        self.cleanup()
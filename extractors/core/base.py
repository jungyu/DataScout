#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基礎提取器模組

提供提取器的基礎功能，包括：
1. 配置管理
2. 狀態管理
3. 錯誤處理
4. 日誌記錄
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

from ...core.error import handle_error
from ...core.logger import get_logger
from ...core.config import BaseConfig
from .error import ExtractorError, handle_extractor_error
from .types import ExtractorConfig, ExtractorState, ExtractorResult

class BaseExtractor(ABC):
    """基礎提取器類別"""
    
    def __init__(
        self,
        config: Optional[Union[Dict[str, Any], ExtractorConfig]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化提取器
        
        Args:
            config: 配置字典或配置對象
            logger: 日誌記錄器
        """
        self.config = config if isinstance(config, ExtractorConfig) else ExtractorConfig(**(config or {}))
        self.logger = logger or get_logger(__name__)
        self._state = ExtractorState()
        
    @handle_extractor_error()
    def setup(self) -> None:
        """設置提取器環境"""
        self._state = ExtractorState()
        self._setup()
        
    @abstractmethod
    def _setup(self) -> None:
        """具體的設置邏輯"""
        pass
        
    @handle_extractor_error()
    def cleanup(self) -> None:
        """清理提取器環境"""
        self._cleanup()
        self._state = ExtractorState()
        
    @abstractmethod
    def _cleanup(self) -> None:
        """具體的清理邏輯"""
        pass
        
    @handle_extractor_error()
    def get_state(self) -> Dict[str, Any]:
        """
        獲取當前狀態
        
        Returns:
            狀態字典
        """
        return self._state.to_dict()
        
    @handle_extractor_error()
    def set_state(self, state: Dict[str, Any]) -> None:
        """
        設置當前狀態
        
        Args:
            state: 狀態字典
        """
        self._state = ExtractorState.from_dict(state)
        
    @handle_extractor_error()
    def update_state(self, **kwargs: Any) -> None:
        """
        更新當前狀態
        
        Args:
            **kwargs: 要更新的狀態項
        """
        current_state = self._state.to_dict()
        current_state.update(kwargs)
        self._state = ExtractorState.from_dict(current_state)
        
    @handle_extractor_error()
    def clear_state(self) -> None:
        """清空當前狀態"""
        self._state = ExtractorState()
        
    @handle_extractor_error()
    def validate_config(self) -> bool:
        """
        驗證配置
        
        Returns:
            bool: 是否有效
        """
        return self._validate_config()
        
    @abstractmethod
    def _validate_config(self) -> bool:
        """具體的配置驗證邏輯"""
        pass
        
    @handle_extractor_error()
    def extract(self, *args: Any, **kwargs: Any) -> ExtractorResult:
        """
        提取數據
        
        Args:
            *args: 位置參數
            **kwargs: 關鍵字參數
            
        Returns:
            ExtractorResult: 提取結果
        """
        try:
            data = self._extract(*args, **kwargs)
            return ExtractorResult(success=True, data=data)
        except Exception as e:
            return ExtractorResult(success=False, data=None, error=str(e))
        
    @abstractmethod
    def _extract(self, *args: Any, **kwargs: Any) -> Any:
        """具體的提取邏輯"""
        pass
        
    def __enter__(self) -> 'BaseExtractor':
        """上下文管理器入口"""
        self.setup()
        return this
        
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """上下文管理器出口"""
        self.cleanup() 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基礎管理器模組

此模組提供基礎管理器功能，包括：
1. 基礎管理器類
2. 配置管理
3. 日誌記錄
4. 狀態管理
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
import os

from selenium.webdriver.remote.webdriver import WebDriver

from .base_error import AntiDetectionError, handle_error, log_error
from ...core.logger import setup_logger
from ...core.utils import Utils
from ...core.config import BaseConfig

logger = setup_logger(__name__)

class BaseManager(ABC):
    """基礎管理器類"""
    
    def __init__(
        self,
        driver: WebDriver,
        config: Union[Dict[str, Any], BaseConfig],
        logger: Optional[Any] = None
    ):
        """
        初始化基礎管理器
        
        Args:
            driver: WebDriver 實例
            config: 配置字典或配置對象
            logger: 日誌記錄器
        """
        self.driver = driver
        self.config = config if isinstance(config, BaseConfig) else BaseConfig(config)
        self.logger = logger or setup_logger(self.__class__.__name__)
        self._initialized = False
        self._state: Dict[str, Any] = {}
        
    @abstractmethod
    def setup(self) -> None:
        """
        設置管理器
        
        此方法應該在初始化時調用，用於設置必要的環境和資源。
        """
        pass
        
    @abstractmethod
    def cleanup(self) -> None:
        """
        清理管理器
        
        此方法應該在不需要時調用，用於清理資源。
        """
        pass
        
    @handle_error()
    def get_state(self) -> Dict[str, Any]:
        """
        獲取當前狀態
        
        Returns:
            當前狀態字典
        """
        return self._state.copy()
        
    @handle_error()
    def set_state(self, state: Dict[str, Any]) -> None:
        """
        設置當前狀態
        
        Args:
            state: 狀態字典
        """
        self._state = state.copy()
        
    @handle_error()
    def update_state(self, updates: Dict[str, Any]) -> None:
        """
        更新當前狀態
        
        Args:
            updates: 更新字典
        """
        self._state.update(updates)
        
    @handle_error()
    def clear_state(self) -> None:
        """
        清除當前狀態
        """
        self._state.clear()
        
    @handle_error()
    def is_initialized(self) -> bool:
        """
        檢查是否已初始化
        
        Returns:
            是否已初始化
        """
        return self._initialized
        
    @handle_error()
    def validate_config(self) -> None:
        """
        驗證配置
        
        此方法應該在設置前調用，用於驗證配置的有效性。
        """
        if not isinstance(self.config, BaseConfig):
            raise AntiDetectionError("配置必須是 BaseConfig 類型")
            
    @handle_error()
    def save_config(self, path: str) -> None:
        """
        保存配置到文件
        
        Args:
            path: 文件路徑
        """
        try:
            Utils.ensure_dir(os.path.dirname(path))
            self.config.save(path)
            self.logger.info(f"配置已保存到：{path}")
        except Exception as e:
            self.logger.error(f"保存配置失敗：{str(e)}")
            raise AntiDetectionError(f"保存配置失敗：{str(e)}")
            
    @handle_error()
    def load_config(self, path: str) -> None:
        """
        從文件加載配置
        
        Args:
            path: 文件路徑
        """
        try:
            self.config.load(path)
            self.logger.info(f"配置已從 {path} 加載")
        except Exception as e:
            self.logger.error(f"加載配置失敗：{str(e)}")
            raise AntiDetectionError(f"加載配置失敗：{str(e)}")
            
    def execute_script(self, script: str, *args) -> Any:
        """
        執行 JavaScript 腳本
        
        Args:
            script: JavaScript 腳本
            args: 腳本參數
            
        Returns:
            腳本執行結果
        """
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self.logger.error(f"執行腳本失敗：{str(e)}")
            raise AntiDetectionError(f"執行腳本失敗：{str(e)}")
            
    def add_cdp_command(self, command: str, params: Dict) -> None:
        """
        添加 CDP 命令
        
        Args:
            command: 命令名稱
            params: 命令參數
        """
        try:
            self.driver.execute_cdp_cmd(command, params)
        except Exception as e:
            self.logger.error(f"添加 CDP 命令失敗：{str(e)}")
            raise AntiDetectionError(f"添加 CDP 命令失敗：{str(e)}")
            
    def __enter__(self):
        """上下文管理器入口"""
        self.setup()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup() 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日誌處理工具模組

提供日誌處理相關的工具類和函數，包括：
1. 日誌配置
2. 日誌格式化
3. 日誌過濾
4. 日誌輪轉
"""

import os
import logging
import logging.handlers
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LogConfig:
    """日誌配置數據類"""
    level: int = logging.INFO
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format: str = '%Y-%m-%d %H:%M:%S'
    log_dir: str = 'logs'
    log_file: Optional[str] = None
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_output: bool = True
    file_output: bool = True

class LogFilter(logging.Filter):
    """日誌過濾器"""
    
    def __init__(self, name: str = '', level: int = logging.NOTSET):
        """
        初始化過濾器
        
        Args:
            name: 過濾器名稱
            level: 日誌等級
        """
        super().__init__(name)
        self.level = level
        
    def filter(self, record: logging.LogRecord) -> bool:
        """
        過濾日誌記錄
        
        Args:
            record: 日誌記錄
            
        Returns:
            是否通過過濾
        """
        return record.levelno >= self.level

class LogFormatter(logging.Formatter):
    """日誌格式化器"""
    
    def __init__(self, fmt: str = None, datefmt: str = None):
        """
        初始化格式化器
        
        Args:
            fmt: 格式化字符串
            datefmt: 日期格式化字符串
        """
        super().__init__(fmt, datefmt)
        
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日誌記錄
        
        Args:
            record: 日誌記錄
            
        Returns:
            格式化後的日誌字符串
        """
        # 添加額外的上下文信息
        if not hasattr(record, 'context'):
            record.context = {}
            
        # 格式化消息
        message = super().format(record)
        
        # 如果有上下文信息，添加到消息末尾
        if record.context:
            context_str = ' '.join(f'{k}={v}' for k, v in record.context.items())
            message = f'{message} [{context_str}]'
            
        return message

class Logger:
    """日誌處理工具類"""
    
    def __init__(self, name: str, config: Optional[LogConfig] = None):
        """
        初始化日誌處理器
        
        Args:
            name: 日誌記錄器名稱
            config: 日誌配置
        """
        self.name = name
        self.config = config or LogConfig()
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """
        設置日誌記錄器
        
        Returns:
            配置好的日誌記錄器
        """
        logger = logging.getLogger(self.name)
        logger.setLevel(self.config.level)
        
        # 清除現有的處理器
        logger.handlers.clear()
        
        # 創建格式化器
        formatter = LogFormatter(
            fmt=self.config.format,
            datefmt=self.config.date_format
        )
        
        # 添加控制台處理器
        if self.config.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
        # 添加文件處理器
        if self.config.file_output and self.config.log_file:
            # 確保日誌目錄存在
            log_dir = Path(self.config.log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 創建文件處理器
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_dir / self.config.log_file,
                maxBytes=self.config.max_bytes,
                backupCount=self.config.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        return logger
        
    def _log(self, level: int, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """
        記錄日誌
        
        Args:
            level: 日誌等級
            msg: 日誌消息
            context: 上下文信息
            **kwargs: 額外參數
        """
        if context is None:
            context = {}
            
        # 添加額外的上下文信息
        extra = {'context': context}
        extra.update(kwargs)
        
        self.logger.log(level, msg, extra=extra)
        
    def debug(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """記錄調試日誌"""
        self._log(logging.DEBUG, msg, context, **kwargs)
        
    def info(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """記錄信息日誌"""
        self._log(logging.INFO, msg, context, **kwargs)
        
    def warning(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """記錄警告日誌"""
        self._log(logging.WARNING, msg, context, **kwargs)
        
    def error(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """記錄錯誤日誌"""
        self._log(logging.ERROR, msg, context, **kwargs)
        
    def critical(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """記錄嚴重錯誤日誌"""
        self._log(logging.CRITICAL, msg, context, **kwargs)
        
    def exception(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """記錄異常日誌"""
        self._log(logging.ERROR, msg, context, exc_info=True, **kwargs)
        
    def add_context(self, **kwargs):
        """
        添加上下文信息
        
        Args:
            **kwargs: 上下文信息
        """
        if not hasattr(self.logger, 'context'):
            self.logger.context = {}
        self.logger.context.update(kwargs)
        
    def clear_context(self):
        """清除上下文信息"""
        if hasattr(self.logger, 'context'):
            self.logger.context.clear()
            
    def get_logger(self) -> logging.Logger:
        """
        獲取日誌記錄器
        
        Returns:
            日誌記錄器
        """
        return self.logger 
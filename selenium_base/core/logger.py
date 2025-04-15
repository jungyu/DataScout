#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日誌記錄模組

提供日誌記錄功能
"""

import os
import logging
import logging.handlers
import json
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from selenium_base.core.exceptions import LoggerError

class LoggerManager:
    """日誌管理器"""
    
    def __init__(
        self,
        name: str,
        log_level: str = "INFO",
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_file: Optional[str] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """
        初始化日誌管理器
        
        Args:
            name: 日誌名稱
            log_level: 日誌級別
            log_format: 日誌格式
            log_file: 日誌文件路徑
            max_bytes: 單個日誌文件最大大小
            backup_count: 保留的日誌文件數量
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper())
        self.log_format = log_format
        self.log_file = log_file
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """設置日誌記錄器"""
        try:
            logger = logging.getLogger(self.name)
            logger.setLevel(self.log_level)
            
            # 清除現有的處理器
            logger.handlers = []
            
            # 添加控制台處理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(logging.Formatter(self.log_format))
            logger.addHandler(console_handler)
            
            # 如果指定了日誌文件，添加文件處理器
            if self.log_file:
                # 確保日誌目錄存在
                log_dir = os.path.dirname(self.log_file)
                if log_dir:
                    os.makedirs(log_dir, exist_ok=True)
                
                # 添加文件處理器
                file_handler = logging.handlers.RotatingFileHandler(
                    self.log_file,
                    maxBytes=self.max_bytes,
                    backupCount=self.backup_count,
                    encoding='utf-8'
                )
                file_handler.setLevel(self.log_level)
                file_handler.setFormatter(logging.Formatter(self.log_format))
                logger.addHandler(file_handler)
            
            return logger
            
        except Exception as e:
            raise LoggerError(f"設置日誌記錄器失敗: {str(e)}")
    
    def get_logger(self) -> logging.Logger:
        """獲取日誌記錄器"""
        return self.logger
    
    def set_level(self, level: str) -> None:
        """
        設置日誌級別
        
        Args:
            level: 日誌級別
        """
        try:
            log_level = getattr(logging, level.upper())
            self.logger.setLevel(log_level)
            for handler in self.logger.handlers:
                handler.setLevel(log_level)
        except AttributeError:
            raise LoggerError(f"無效的日誌級別: {level}")
    
    def add_file_handler(
        self,
        log_file: str,
        level: Optional[str] = None,
        max_bytes: Optional[int] = None,
        backup_count: Optional[int] = None
    ) -> None:
        """
        添加文件處理器
        
        Args:
            log_file: 日誌文件路徑
            level: 日誌級別
            max_bytes: 單個日誌文件最大大小
            backup_count: 保留的日誌文件數量
        """
        try:
            # 確保日誌目錄存在
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            # 創建文件處理器
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes or self.max_bytes,
                backupCount=backup_count or self.backup_count,
                encoding='utf-8'
            )
            
            # 設置日誌級別
            if level:
                log_level = getattr(logging, level.upper())
                file_handler.setLevel(log_level)
            else:
                file_handler.setLevel(self.log_level)
            
            # 設置格式
            file_handler.setFormatter(logging.Formatter(self.log_format))
            
            # 添加處理器
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            raise LoggerError(f"添加文件處理器失敗: {str(e)}")
    
    def remove_file_handler(self, log_file: str) -> None:
        """
        移除文件處理器
        
        Args:
            log_file: 日誌文件路徑
        """
        try:
            for handler in self.logger.handlers[:]:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    if handler.baseFilename == log_file:
                        self.logger.removeHandler(handler)
                        handler.close()
        except Exception as e:
            raise LoggerError(f"移除文件處理器失敗: {str(e)}")
    
    def log_error(
        self,
        message: str,
        error: Exception,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        記錄錯誤
        
        Args:
            message: 錯誤消息
            error: 異常對象
            details: 詳細信息
        """
        try:
            error_details = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": datetime.now().isoformat()
            }
            
            if details:
                error_details.update(details)
            
            self.logger.error(
                f"{message}: {str(error)}",
                extra={"details": json.dumps(error_details, ensure_ascii=False)}
            )
            
        except Exception as e:
            raise LoggerError(f"記錄錯誤失敗: {str(e)}")
    
    def log_request(
        self,
        method: str,
        url: str,
        status_code: Optional[int] = None,
        response_time: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        記錄請求
        
        Args:
            method: 請求方法
            url: 請求URL
            status_code: 狀態碼
            response_time: 響應時間
            details: 詳細信息
        """
        try:
            request_details = {
                "method": method,
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
            
            if status_code is not None:
                request_details["status_code"] = status_code
            
            if response_time is not None:
                request_details["response_time"] = response_time
            
            if details:
                request_details.update(details)
            
            self.logger.info(
                f"Request: {method} {url}",
                extra={"details": json.dumps(request_details, ensure_ascii=False)}
            )
            
        except Exception as e:
            raise LoggerError(f"記錄請求失敗: {str(e)}")
    
    def log_response(
        self,
        method: str,
        url: str,
        status_code: int,
        response_time: float,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        記錄響應
        
        Args:
            method: 請求方法
            url: 請求URL
            status_code: 狀態碼
            response_time: 響應時間
            details: 詳細信息
        """
        try:
            response_details = {
                "method": method,
                "url": url,
                "status_code": status_code,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            }
            
            if details:
                response_details.update(details)
            
            self.logger.info(
                f"Response: {method} {url} {status_code} ({response_time:.2f}s)",
                extra={"details": json.dumps(response_details, ensure_ascii=False)}
            )
            
        except Exception as e:
            raise LoggerError(f"記錄響應失敗: {str(e)}")

def setup_logger(
    name: str,
    log_level: str = "INFO",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5
) -> logging.Logger:
    """
    設置日誌記錄器
    
    Args:
        name: 日誌名稱
        log_level: 日誌級別
        log_format: 日誌格式
        log_file: 日誌文件路徑
        max_bytes: 單個日誌文件最大大小
        backup_count: 保留的日誌文件數量
        
    Returns:
        日誌記錄器
    """
    logger_manager = LoggerManager(
        name=name,
        log_level=log_level,
        log_format=log_format,
        log_file=log_file,
        max_bytes=max_bytes,
        backup_count=backup_count
    )
    return logger_manager.get_logger() 
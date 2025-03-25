#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import time
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional, Union, Dict, Any


class ColoredFormatter(logging.Formatter):
    """
    帶顏色的日誌格式化器
    """
    # 顏色代碼
    COLORS = {
        'DEBUG': '\033[94m',     # 藍色
        'INFO': '\033[92m',      # 綠色
        'WARNING': '\033[93m',   # 黃色
        'ERROR': '\033[91m',     # 紅色
        'CRITICAL': '\033[91m',  # 紅色
        'RESET': '\033[0m'       # 重置
    }
    
    def __init__(self, fmt: str = None, datefmt: str = None, style: str = '%'):
        """
        初始化顏色格式化器
        
        Args:
            fmt: 格式字符串
            datefmt: 日期格式字符串
            style: 格式化風格
        """
        super().__init__(fmt, datefmt, style)
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日誌記錄，添加顏色
        
        Args:
            record: 日誌記錄
            
        Returns:
            格式化後的日誌字符串
        """
        # 檢查是否在終端環境
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logger(
    name: str, 
    level: int = logging.INFO,
    log_file: str = None,
    console: bool = True,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 10,
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    date_format: str = '%Y-%m-%d %H:%M:%S'
) -> logging.Logger:
    """
    設置日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        level: 日誌級別
        log_file: 日誌文件路徑，為None時不寫入文件
        console: 是否輸出到控制台
        max_bytes: 日誌文件最大大小
        backup_count: 日誌文件備份數量
        log_format: 日誌格式
        date_format: 日期格式
        
    Returns:
        配置好的日誌記錄器
    """
    # 獲取或創建日誌記錄器
    logger = logging.getLogger(name)
    
    # 如果已經配置過，直接返回
    if logger.handlers:
        return logger
    
    # 設置日誌級別
    logger.setLevel(level)
    
    # 創建格式化器
    formatter = logging.Formatter(log_format, date_format)
    colored_formatter = ColoredFormatter(log_format, date_format)
    
    # 添加控制台處理器
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(colored_formatter)
        logger.addHandler(console_handler)
    
    # 添加文件處理器
    if log_file:
        # 確保日誌目錄存在
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 創建按大小輪轉的文件處理器
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


class CrawlerLogger:
    """
    爬蟲專用日誌記錄器，提供更豐富的日誌功能，
    包括任務狀態追蹤、錯誤堆疊、性能監控等。
    """
    
    def __init__(
        self,
        name: str,
        log_dir: str = "logs",
        level: int = logging.INFO,
        log_to_console: bool = True,
        log_to_file: bool = True,
        rotate_interval: str = "daily",  # "daily", "hourly", "never"
        max_bytes: int = 10485760,       # 10MB
        backup_count: int = 10
    ):
        """
        初始化爬蟲日誌記錄器
        
        Args:
            name: 日誌記錄器名稱
            log_dir: 日誌目錄
            level: 日誌級別
            log_to_console: 是否輸出到控制台
            log_to_file: 是否寫入文件
            rotate_interval: 日誌輪轉間隔
            max_bytes: 日誌文件最大大小
            backup_count: 日誌文件備份數量
        """
        self.name = name
        self.level = level
        self.log_dir = log_dir
        
        # 確保日誌目錄存在
        if log_to_file and log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 創建日誌記錄器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 清除現有處理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 日誌格式
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        self.colored_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        
        # 添加控制台處理器
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(self.colored_formatter)
            self.logger.addHandler(console_handler)
        
        # 添加文件處理器
        if log_to_file:
            # 主日誌文件
            main_log_file = os.path.join(log_dir, f"{name}.log")
            
            if rotate_interval == "daily":
                file_handler = TimedRotatingFileHandler(
                    main_log_file,
                    when='midnight',
                    interval=1,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
            elif rotate_interval == "hourly":
                file_handler = TimedRotatingFileHandler(
                    main_log_file,
                    when='H',
                    interval=1,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
            else:  # "never" 或其他值
                file_handler = RotatingFileHandler(
                    main_log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
            
            file_handler.setLevel(level)
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)
            
            # 錯誤日誌文件
            error_log_file = os.path.join(log_dir, f"{name}_error.log")
            error_handler = RotatingFileHandler(
                error_log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(self.formatter)
            self.logger.addHandler(error_handler)
        
        # 性能計時器
        self.timers = {}
    
    def debug(self, message: str, *args, **kwargs):
        """記錄調試信息"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """記錄一般信息"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """記錄警告信息"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, error: Exception = None, *args, **kwargs):
        """
        記錄錯誤信息，可選包含異常對象
        
        Args:
            message: 錯誤信息
            error: 異常對象
            *args, **kwargs: 傳遞給日誌記錄器的參數
        """
        if error:
            import traceback
            error_details = traceback.format_exception(type(error), error, error.__traceback__)
            error_message = f"{message}: {str(error)}\n{''.join(error_details)}"
            self.logger.error(error_message, *args, **kwargs)
        else:
            self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, error: Exception = None, *args, **kwargs):
        """記錄嚴重錯誤信息"""
        if error:
            import traceback
            error_details = traceback.format_exception(type(error), error, error.__traceback__)
            error_message = f"{message}: {str(error)}\n{''.join(error_details)}"
            self.logger.critical(error_message, *args, **kwargs)
        else:
            self.logger.critical(message, *args, **kwargs)
    
    def start_timer(self, name: str):
        """
        啟動命名計時器
        
        Args:
            name: 計時器名稱
        """
        self.timers[name] = time.time()
        self.debug(f"Timer '{name}' started")
    
    def stop_timer(self, name: str, log_level: int = logging.DEBUG) -> float:
        """
        停止命名計時器並返回耗時
        
        Args:
            name: 計時器名稱
            log_level: 記錄耗時的日誌級別
            
        Returns:
            耗時（秒）
        """
        if name not in self.timers:
            self.warning(f"Timer '{name}' not found")
            return 0.0
        
        elapsed = time.time() - self.timers[name]
        del self.timers[name]
        
        # 根據級別記錄耗時
        if log_level == logging.DEBUG:
            self.debug(f"Timer '{name}' stopped: {elapsed:.3f} seconds")
        elif log_level == logging.INFO:
            self.info(f"Timer '{name}' stopped: {elapsed:.3f} seconds")
        elif log_level == logging.WARNING:
            self.warning(f"Timer '{name}' stopped: {elapsed:.3f} seconds")
        else:
            self.debug(f"Timer '{name}' stopped: {elapsed:.3f} seconds")
        
        return elapsed
    
    def log_dict(self, data: Dict, title: str = None, level: int = logging.DEBUG):
        """
        記錄字典內容
        
        Args:
            data: 要記錄的字典
            title: 可選標題
            level: 日誌級別
        """
        import json
        
        if title:
            message = f"{title}:\n{json.dumps(data, indent=2, ensure_ascii=False)}"
        else:
            message = json.dumps(data, indent=2, ensure_ascii=False)
        
        if level == logging.DEBUG:
            self.debug(message)
        elif level == logging.INFO:
            self.info(message)
        elif level == logging.WARNING:
            self.warning(message)
        elif level == logging.ERROR:
            self.error(message)
        elif level == logging.CRITICAL:
            self.critical(message)
        else:
            self.debug(message)
    
    def log_task_start(self, task_id: str, details: Dict = None):
        """
        記錄任務開始
        
        Args:
            task_id: 任務ID
            details: 任務詳情
        """
        message = f"Task '{task_id}' started"
        if details:
            import json
            message += f":\n{json.dumps(details, indent=2, ensure_ascii=False)}"
        
        self.info(message)
    
    def log_task_end(self, task_id: str, status: str, details: Dict = None):
        """
        記錄任務結束
        
        Args:
            task_id: 任務ID
            status: 任務狀態（例如 "completed", "failed"）
            details: 任務詳情
        """
        message = f"Task '{task_id}' {status}"
        if details:
            import json
            message += f":\n{json.dumps(details, indent=2, ensure_ascii=False)}"
        
        if status.lower() in ["completed", "success", "succeeded"]:
            self.info(message)
        elif status.lower() in ["failed", "error", "crashed"]:
            self.error(message)
        else:
            self.info(message)
    
    def get_logger(self) -> logging.Logger:
        """獲取原始日誌記錄器"""
        return self.logger
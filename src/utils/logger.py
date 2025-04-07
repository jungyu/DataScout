#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日誌記錄模組

提供統一的日誌記錄功能
"""

import os
import logging
import datetime
from typing import Optional, Dict, Any


class Logger:
    """
    日誌記錄類
    
    提供配置和管理日誌記錄的功能
    """
    
    def __init__(
        self, 
        name: str, 
        level: int = logging.INFO,
        log_to_console: bool = True,
        log_to_file: bool = False,
        log_dir: str = "logs",
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ):
        """
        初始化日誌記錄器
        
        Args:
            name: 記錄器名稱
            level: 日誌級別
            log_to_console: 是否輸出到控制台
            log_to_file: 是否輸出到文件
            log_dir: 日誌文件目錄
            log_format: 日誌格式
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.formatter = logging.Formatter(log_format)
        
        # 避免日誌重複
        if not self.logger.handlers:
            # 控制台處理器
            if log_to_console:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(self.formatter)
                self.logger.addHandler(console_handler)
            
            # 文件處理器
            if log_to_file:
                os.makedirs(log_dir, exist_ok=True)
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                log_file = os.path.join(log_dir, f"{name}_{today}.log")
                
                file_handler = logging.FileHandler(log_file, encoding="utf-8")
                file_handler.setFormatter(self.formatter)
                self.logger.addHandler(file_handler)
    
    def get_logger(self) -> logging.Logger:
        """
        獲取記錄器實例
        
        Returns:
            logging.Logger: 記錄器實例
        """
        return self.logger


def setup_logger(
    name: str = "crawler", 
    level: int = logging.INFO,
    log_to_file: bool = False
) -> logging.Logger:
    """
    設置並獲取記錄器
    
    Args:
        name: 記錄器名稱
        level: 日誌級別
        log_to_file: 是否輸出到文件
        
    Returns:
        configured logger instance
    """
    logger_instance = Logger(
        name=name,
        level=level,
        log_to_console=True,
        log_to_file=log_to_file
    )
    return logger_instance.get_logger()
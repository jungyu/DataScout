#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日誌模組

提供 Playwright 基礎框架的日誌設置功能
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union, Dict, Any

def setup_logger(
    name: Optional[str] = None,
    level: Union[int, str] = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    format_str: Optional[str] = None,
    **kwargs
) -> logging.Logger:
    """
    設置日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        level: 日誌級別
        log_file: 日誌文件路徑
        format_str: 日誌格式字符串
        **kwargs: 其他參數
        
    Returns:
        logging.Logger: 日誌記錄器
    """
    if name is None:
        name = "playwright_base"
        
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
    logger = logging.getLogger(name)
    
    # 如果已經設置過處理器，則不重複設置
    if logger.handlers:
        return logger
        
    logger.setLevel(level)
    
    # 創建控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(format_str)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 如果指定了日誌文件，則創建文件處理器
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(format_str)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
    return logger 
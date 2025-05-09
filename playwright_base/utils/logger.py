"""
日誌工具模組

提供統一的日誌記錄功能，支援自訂日誌級別和輸出格式。
"""

import os
import logging
import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(
    name=None,
    log_level=logging.INFO,
    log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    log_file=None,
    max_bytes=10485760,  # 10MB
    backup_count=5
):
    """
    設置並返回一個日誌記錄器。

    參數:
        name (str): 日誌記錄器的名稱，預設為 root logger。
        log_level (int): 日誌記錄級別，預設為 INFO。
        log_format (str): 日誌記錄格式。
        log_file (str): 日誌檔案路徑，若為 None，則只輸出到控制台。
        max_bytes (int): 日誌檔案的最大大小，超過後將進行輪替。
        backup_count (int): 保留的備份日誌檔案數量。

    返回:
        logging.Logger: 配置好的日誌記錄器。
    """
    # 如果沒有指定名稱，則使用調用模組的名稱
    logger = logging.getLogger(name)
    
    # 避免重複添加處理器
    if logger.handlers:
        return logger
    
    logger.setLevel(log_level)
    
    # 創建控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(log_format)
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # 如果指定了日誌檔案，則添加檔案處理器
    if log_file:
        # 確保日誌目錄存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # 自動添加日期到日誌檔案名稱
        if not os.path.splitext(log_file)[0].endswith(datetime.datetime.now().strftime('%Y%m%d')):
            base_name, ext = os.path.splitext(log_file)
            log_file = f"{base_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            
        # 創建輪替檔案處理器
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(log_level)
        file_format = logging.Formatter(log_format)
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger
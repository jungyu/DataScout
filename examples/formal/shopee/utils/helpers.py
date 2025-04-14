"""
Shopee 爬蟲工具函數

提供爬蟲過程中常用的工具函數，包括：
- 檔案操作
- 數據處理
- 日誌記錄
- 錯誤處理
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

def save_results(data: Dict[str, Any], prefix: str, base_dir: Optional[str] = None) -> str:
    """
    儲存爬取結果
    
    Args:
        data: 要儲存的數據
        prefix: 檔案名前綴
        base_dir: 基礎目錄路徑，預設為當前目錄下的 data/results
        
    Returns:
        str: 儲存的檔案路徑
    """
    try:
        # 確定基礎目錄
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "results")
        
        # 創建結果目錄
        os.makedirs(base_dir, exist_ok=True)
        
        # 生成檔案名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.json"
        filepath = os.path.join(base_dir, filename)
        
        # 儲存結果
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
        
    except Exception as e:
        logging.error(f"儲存結果失敗: {str(e)}")
        raise

def load_config(config_name: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    載入配置檔案
    
    Args:
        config_name: 配置檔案名稱
        base_dir: 基礎目錄路徑，預設為當前目錄下的 config
        
    Returns:
        Dict[str, Any]: 配置數據
    """
    try:
        # 確定基礎目錄
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
        
        # 構建檔案路徑
        config_path = os.path.join(base_dir, config_name)
        
        # 載入配置
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    except Exception as e:
        logging.error(f"載入配置失敗: {str(e)}")
        raise

def setup_logger(name: str, log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    設置日誌記錄器
    
    Args:
        name: 記錄器名稱
        log_file: 日誌檔案路徑，預設為當前目錄下的 logs 目錄
        level: 日誌級別
        
    Returns:
        logging.Logger: 配置好的日誌記錄器
    """
    # 創建記錄器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 如果已經有處理器，直接返回
    if logger.handlers:
        return logger
    
    # 創建格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # 創建控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果指定了日誌檔案，創建檔案處理器
    if log_file:
        # 確保日誌目錄存在
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 創建檔案處理器
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger 
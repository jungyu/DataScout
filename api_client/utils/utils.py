#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API 工具類
"""

import json
import yaml
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path

class Utils:
    """API 工具類"""
    
    @staticmethod
    def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
        """載入 JSON 文件
        
        Args:
            file_path: 文件路徑
            
        Returns:
            JSON 數據
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"載入 JSON 文件失敗: {str(e)}")
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
        """保存 JSON 文件
        
        Args:
            data: 要保存的數據
            file_path: 文件路徑
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ValueError(f"保存 JSON 文件失敗: {str(e)}")
    
    @staticmethod
    def load_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
        """載入 YAML 文件
        
        Args:
            file_path: 文件路徑
            
        Returns:
            YAML 數據
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"載入 YAML 文件失敗: {str(e)}")
    
    @staticmethod
    def save_yaml(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
        """保存 YAML 文件
        
        Args:
            data: 要保存的數據
            file_path: 文件路徑
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            raise ValueError(f"保存 YAML 文件失敗: {str(e)}")
    
    @staticmethod
    def setup_logger(
        name: str,
        level: str = "INFO",
        format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        file_path: Optional[Union[str, Path]] = None
    ) -> logging.Logger:
        """設置日誌記錄器
        
        Args:
            name: 日誌記錄器名稱
            level: 日誌級別
            format: 日誌格式
            file_path: 日誌文件路徑
            
        Returns:
            日誌記錄器
        """
        # 創建日誌記錄器
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 創建格式化器
        formatter = logging.Formatter(format)
        
        # 創建控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 如果指定了文件路徑，創建文件處理器
        if file_path:
            file_handler = logging.FileHandler(file_path, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def validate_response(response: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """驗證響應數據
        
        Args:
            response: 響應數據
            schema: 數據結構定義
            
        Returns:
            驗證結果
        """
        try:
            for key, value_type in schema.items():
                if key not in response:
                    raise ValueError(f"缺少必要字段: {key}")
                if not isinstance(response[key], value_type):
                    raise ValueError(f"字段類型錯誤: {key}")
            return True
        except Exception as e:
            raise ValueError(f"數據驗證失敗: {str(e)}")
    
    @staticmethod
    def retry(
        func,
        max_retries: int = 3,
        retry_interval: int = 1,
        exceptions: tuple = (Exception,)
    ):
        """重試裝飾器
        
        Args:
            func: 要重試的函數
            max_retries: 最大重試次數
            retry_interval: 重試間隔（秒）
            exceptions: 要捕獲的異常類型
            
        Returns:
            裝飾後的函數
        """
        def wrapper(*args, **kwargs):
            import time
            
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if i == max_retries - 1:
                        raise
                    time.sleep(retry_interval)
            
            return None
        
        return wrapper 
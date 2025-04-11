#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數據處理工具

提供數據處理相關的功能，包括：
- 數據清理
- 數據轉換
- 數據驗證
- 數據格式化
"""

import re
import json
import logging
from typing import Any, Dict, List, Union, Optional
from datetime import datetime

class DataProcessor:
    """數據處理工具類"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化數據處理器
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
    def clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理後的文本
        """
        if not text:
            return ""
            
        # 移除多餘的空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        
        return text
        
    def clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理數據
        
        Args:
            data: 原始數據
            
        Returns:
            清理後的數據
        """
        try:
            cleaned_data = {}
            
            for key, value in data.items():
                if isinstance(value, str):
                    cleaned_data[key] = self.clean_text(value)
                elif isinstance(value, dict):
                    cleaned_data[key] = self.clean_data(value)
                elif isinstance(value, list):
                    cleaned_data[key] = [
                        self.clean_data(item) if isinstance(item, dict)
                        else self.clean_text(item) if isinstance(item, str)
                        else item
                        for item in value
                    ]
                else:
                    cleaned_data[key] = value
                    
            return cleaned_data
            
        except Exception as e:
            self.logger.error(f"清理數據失敗: {str(e)}")
            return data
            
    def format_for_json(self, data: Any) -> Any:
        """
        格式化數據為 JSON 格式
        
        Args:
            data: 原始數據
            
        Returns:
            格式化後的數據
        """
        if isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, (list, tuple)):
            return [self.format_for_json(item) for item in data]
        elif isinstance(data, dict):
            return {key: self.format_for_json(value) for key, value in data.items()}
        else:
            return data
            
    def validate_data(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        驗證數據
        
        Args:
            data: 要驗證的數據
            schema: 數據模式
            
        Returns:
            是否驗證通過
        """
        try:
            for key, value_type in schema.items():
                # 檢查必填字段
                if value_type.get("required", False) and key not in data:
                    self.logger.error(f"缺少必填字段: {key}")
                    return False
                    
                # 檢查字段類型
                if key in data:
                    value = data[key]
                    expected_type = value_type.get("type")
                    
                    if expected_type == "string" and not isinstance(value, str):
                        self.logger.error(f"字段類型錯誤: {key} 應該是字符串")
                        return False
                        
                    if expected_type == "number" and not isinstance(value, (int, float)):
                        self.logger.error(f"字段類型錯誤: {key} 應該是數字")
                        return False
                        
                    if expected_type == "boolean" and not isinstance(value, bool):
                        self.logger.error(f"字段類型錯誤: {key} 應該是布爾值")
                        return False
                        
                    if expected_type == "array" and not isinstance(value, list):
                        self.logger.error(f"字段類型錯誤: {key} 應該是數組")
                        return False
                        
                    if expected_type == "object" and not isinstance(value, dict):
                        self.logger.error(f"字段類型錯誤: {key} 應該是對象")
                        return False
                        
            return True
            
        except Exception as e:
            self.logger.error(f"驗證數據失敗: {str(e)}")
            return False
            
    def merge_data(self, data1: Dict[str, Any], data2: Dict[str, Any]) -> Dict[str, Any]:
        """
        合併數據
        
        Args:
            data1: 第一個數據
            data2: 第二個數據
            
        Returns:
            合併後的數據
        """
        try:
            merged = data1.copy()
            
            for key, value in data2.items():
                if key in merged:
                    if isinstance(merged[key], dict) and isinstance(value, dict):
                        merged[key] = self.merge_data(merged[key], value)
                    elif isinstance(merged[key], list) and isinstance(value, list):
                        merged[key].extend(value)
                    else:
                        merged[key] = value
                else:
                    merged[key] = value
                    
            return merged
            
        except Exception as e:
            self.logger.error(f"合併數據失敗: {str(e)}")
            return data1
            
    def extract_data(self, data: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        """
        提取數據
        
        Args:
            data: 原始數據
            fields: 要提取的字段列表
            
        Returns:
            提取後的數據
        """
        try:
            extracted = {}
            
            for field in fields:
                if field in data:
                    extracted[field] = data[field]
                    
            return extracted
            
        except Exception as e:
            self.logger.error(f"提取數據失敗: {str(e)}")
            return {}
            
    def transform_data(self, data: Dict[str, Any], transform_map: Dict[str, str]) -> Dict[str, Any]:
        """
        轉換數據
        
        Args:
            data: 原始數據
            transform_map: 轉換映射
            
        Returns:
            轉換後的數據
        """
        try:
            transformed = {}
            
            for old_key, new_key in transform_map.items():
                if old_key in data:
                    transformed[new_key] = data[old_key]
                    
            return transformed
            
        except Exception as e:
            self.logger.error(f"轉換數據失敗: {str(e)}")
            return {} 
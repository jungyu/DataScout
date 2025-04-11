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

class DataValidator:
    """數據驗證工具類"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化數據驗證器
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or setup_logger(
            name=__name__,
            level_name="INFO"
        )
        
    def validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        驗證數據是否符合模式
        
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
            
    def validate_format(self, data: Dict[str, Any], format_rules: Dict[str, str]) -> bool:
        """
        驗證數據格式
        
        Args:
            data: 要驗證的數據
            format_rules: 格式規則
            
        Returns:
            是否驗證通過
        """
        try:
            for key, pattern in format_rules.items():
                if key in data:
                    value = str(data[key])
                    if not re.match(pattern, value):
                        self.logger.error(f"格式錯誤: {key} 不符合規則 {pattern}")
                        return False
            return True
        except Exception as e:
            self.logger.error(f"驗證格式失敗: {str(e)}")
            return False
            
    def validate_range(self, data: Dict[str, Any], range_rules: Dict[str, Dict[str, Any]]) -> bool:
        """
        驗證數據範圍
        
        Args:
            data: 要驗證的數據
            range_rules: 範圍規則
            
        Returns:
            是否驗證通過
        """
        try:
            for key, rules in range_rules.items():
                if key in data:
                    value = data[key]
                    if "min" in rules and value < rules["min"]:
                        self.logger.error(f"範圍錯誤: {key} 小於最小值 {rules['min']}")
                        return False
                    if "max" in rules and value > rules["max"]:
                        self.logger.error(f"範圍錯誤: {key} 大於最大值 {rules['max']}")
                        return False
            return True
        except Exception as e:
            self.logger.error(f"驗證範圍失敗: {str(e)}")
            return False

class DataNormalizer:
    """數據標準化工具類"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化數據標準化器
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or setup_logger(
            name=__name__,
            level_name="INFO"
        )
        
    def normalize_text(self, text: str) -> str:
        """
        標準化文本
        
        Args:
            text: 原始文本
            
        Returns:
            標準化後的文本
        """
        if not text:
            return ""
            
        # 移除多餘的空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 標準化標點符號
        text = text.replace('，', ',').replace('。', '.').replace('！', '!').replace('？', '?')
        
        # 標準化引號
        text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
        
        return text
        
    def normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        標準化數據
        
        Args:
            data: 原始數據
            
        Returns:
            標準化後的數據
        """
        try:
            normalized = {}
            
            for key, value in data.items():
                if isinstance(value, str):
                    normalized[key] = self.normalize_text(value)
                elif isinstance(value, dict):
                    normalized[key] = self.normalize_data(value)
                elif isinstance(value, list):
                    normalized[key] = [
                        self.normalize_data(item) if isinstance(item, dict)
                        else self.normalize_text(item) if isinstance(item, str)
                        else item
                        for item in value
                    ]
                else:
                    normalized[key] = value
                    
            return normalized
            
        except Exception as e:
            self.logger.error(f"標準化數據失敗: {str(e)}")
            return data
            
    def normalize_date(self, date_str: str, format: str = "%Y-%m-%d") -> str:
        """
        標準化日期
        
        Args:
            date_str: 日期字符串
            format: 目標格式
            
        Returns:
            標準化後的日期字符串
        """
        try:
            # 嘗試解析常見的日期格式
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%Y年%m月%d日"]:
                try:
                    date = datetime.strptime(date_str, fmt)
                    return date.strftime(format)
                except ValueError:
                    continue
                    
            raise ValueError(f"無法解析日期: {date_str}")
            
        except Exception as e:
            self.logger.error(f"標準化日期失敗: {str(e)}")
            return date_str
            
    def normalize_number(self, number_str: str) -> float:
        """
        標準化數字
        
        Args:
            number_str: 數字字符串
            
        Returns:
            標準化後的數字
        """
        try:
            # 移除貨幣符號和空格
            number_str = re.sub(r'[^\d.-]', '', number_str)
            
            # 轉換為浮點數
            return float(number_str)
            
        except Exception as e:
            self.logger.error(f"標準化數字失敗: {str(e)}")
            return 0.0

class SimpleDataProcessor:
    """簡單數據處理器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化簡單數據處理器
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or setup_logger(
            name=__name__,
            level_name="INFO"
        )
        self.validator = DataValidator(self.logger)
        self.normalizer = DataNormalizer(self.logger)
        
    def process(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        處理數據
        
        Args:
            data: 要處理的數據
            
        Returns:
            處理後的數據
        """
        try:
            if isinstance(data, dict):
                return self.normalizer.normalize_data(data)
            elif isinstance(data, list):
                return [self.normalizer.normalize_data(item) for item in data]
            else:
                self.logger.error(f"不支持的數據類型: {type(data)}")
                return data
        except Exception as e:
            self.logger.error(f"處理數據失敗: {str(e)}")
            return data
            
    def validate(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        驗證數據
        
        Args:
            data: 要驗證的數據
            schema: 數據模式
            
        Returns:
            是否驗證通過
        """
        return self.validator.validate_schema(data, schema)
        
    def clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 要清理的文本
            
        Returns:
            清理後的文本
        """
        return self.normalizer.normalize_text(text)
        
    def clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理數據
        
        Args:
            data: 原始數據
            
        Returns:
            清理後的數據
        """
        return self.normalizer.normalize_data(data)
        
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
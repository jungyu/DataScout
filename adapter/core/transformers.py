#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
適配器模組轉換器類定義
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
import re
import logging
from pathlib import Path

from .base import BaseTransformer
from .exceptions import TransformationError
from .config import TransformerConfig

class TypeTransformer(BaseTransformer):
    """類型轉換器"""
    
    def transform(self, data: Any) -> Any:
        """
        轉換資料類型
        
        Args:
            data: 要轉換的資料
            
        Returns:
            轉換後的資料
            
        Raises:
            TransformationError: 轉換失敗
        """
        target_type = self.config.params.get("type")
        if not target_type:
            raise TransformationError("未指定目標類型")
            
        try:
            return target_type(data)
        except Exception as e:
            raise TransformationError(f"類型轉換失敗: {str(e)}")

class StringTransformer(BaseTransformer):
    """字串轉換器"""
    
    def transform(self, data: Any) -> str:
        """
        轉換為字串
        
        Args:
            data: 要轉換的資料
            
        Returns:
            轉換後的字串
            
        Raises:
            TransformationError: 轉換失敗
        """
        try:
            return str(data)
        except Exception as e:
            raise TransformationError(f"字串轉換失敗: {str(e)}")

class NumberTransformer(BaseTransformer):
    """數值轉換器"""
    
    def transform(self, data: Any) -> Union[int, float]:
        """
        轉換為數值
        
        Args:
            data: 要轉換的資料
            
        Returns:
            轉換後的數值
            
        Raises:
            TransformationError: 轉換失敗
        """
        try:
            if isinstance(data, (int, float)):
                return data
            return float(data)
        except Exception as e:
            raise TransformationError(f"數值轉換失敗: {str(e)}")

class DateTimeTransformer(BaseTransformer):
    """日期時間轉換器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.format = config.get('format', '%Y-%m-%d %H:%M:%S')
    
    def transform(self, data: Any) -> datetime:
        """將資料轉換為日期時間"""
        try:
            if isinstance(data, datetime):
                return data
            if isinstance(data, str):
                return datetime.strptime(data, self.format)
            if isinstance(data, (int, float)):
                return datetime.fromtimestamp(data)
            raise TransformationError("無法轉換為日期時間")
        except Exception as e:
            raise TransformationError(f"日期時間轉換失敗: {str(e)}")

class ListTransformer(BaseTransformer):
    """列表轉換器"""
    
    def transform(self, data: Any) -> List:
        """
        轉換為列表
        
        Args:
            data: 要轉換的資料
            
        Returns:
            轉換後的列表
            
        Raises:
            TransformationError: 轉換失敗
        """
        try:
            if isinstance(data, list):
                return data
            if isinstance(data, (tuple, set)):
                return list(data)
            if isinstance(data, str):
                return [data]
            return [data]
        except Exception as e:
            raise TransformationError(f"列表轉換失敗: {str(e)}")

class DictTransformer(BaseTransformer):
    """字典轉換器"""
    
    def transform(self, data: Any) -> Dict:
        """
        轉換為字典
        
        Args:
            data: 要轉換的資料
            
        Returns:
            轉換後的字典
            
        Raises:
            TransformationError: 轉換失敗
        """
        try:
            if isinstance(data, dict):
                return data
            if isinstance(data, str):
                return json.loads(data)
            if hasattr(data, "__dict__"):
                return data.__dict__
            raise TransformationError("無法轉換為字典")
        except Exception as e:
            raise TransformationError(f"字典轉換失敗: {str(e)}")

class BooleanTransformer(BaseTransformer):
    """布爾值轉換器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.true_values = config.get('true_values', ['true', '1', 'yes', 'y', 't'])
        self.false_values = config.get('false_values', ['false', '0', 'no', 'n', 'f'])
    
    def transform(self, data: Any) -> bool:
        """將資料轉換為布爾值"""
        try:
            if isinstance(data, bool):
                return data
            if isinstance(data, str):
                data = data.lower().strip()
                if data in self.true_values:
                    return True
                if data in self.false_values:
                    return False
            if isinstance(data, (int, float)):
                return bool(data)
            raise TransformationError("無法轉換為布爾值")
        except Exception as e:
            raise TransformationError(f"布爾值轉換失敗: {str(e)}")

class JsonTransformer(BaseTransformer):
    """JSON 轉換器"""
    
    def transform(self, data: Any) -> str:
        """將資料轉換為 JSON 字串"""
        try:
            if isinstance(data, str):
                # 驗證是否為有效的 JSON
                json.loads(data)
                return data
            return json.dumps(data, ensure_ascii=False)
        except Exception as e:
            raise TransformationError(f"JSON 轉換失敗: {str(e)}")

class PathTransformer(BaseTransformer):
    """路徑轉換器"""
    
    def transform(self, data: Any) -> Path:
        """將資料轉換為路徑"""
        try:
            if isinstance(data, Path):
                return data
            if isinstance(data, str):
                return Path(data)
            raise TransformationError("無法轉換為路徑")
        except Exception as e:
            raise TransformationError(f"路徑轉換失敗: {str(e)}")

class RegexTransformer(BaseTransformer):
    """正則表達式轉換器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.pattern = config.get('pattern')
        if not self.pattern:
            raise TransformationError("未指定正則表達式模式")
        self.regex = re.compile(self.pattern)
    
    def transform(self, data: Any) -> str:
        """使用正則表達式轉換資料"""
        try:
            if not isinstance(data, str):
                data = str(data)
            match = self.regex.search(data)
            if match:
                return match.group(0)
            raise TransformationError("未找到匹配項")
        except Exception as e:
            raise TransformationError(f"正則表達式轉換失敗: {str(e)}")

class CustomTransformer(BaseTransformer):
    """自定義轉換器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.transform_func = config.get('transform_func')
        if not callable(self.transform_func):
            raise TransformationError("未指定轉換函數")
    
    def transform(self, data: Any) -> Any:
        """使用自定義函數轉換資料"""
        try:
            return self.transform_func(data)
        except Exception as e:
            raise TransformationError(f"自定義轉換失敗: {str(e)}")

class CaseTransformer(BaseTransformer):
    """大小寫轉換器"""
    
    def transform(self, data: Any) -> str:
        """
        轉換字串大小寫
        
        Args:
            data: 要轉換的資料
            
        Returns:
            轉換後的字串
            
        Raises:
            TransformationError: 轉換失敗
        """
        try:
            if not isinstance(data, str):
                data = str(data)
                
            case_type = self.config.params.get("case", "lower")
            if case_type == "lower":
                return data.lower()
            elif case_type == "upper":
                return data.upper()
            elif case_type == "title":
                return data.title()
            elif case_type == "capitalize":
                return data.capitalize()
            else:
                raise TransformationError(f"不支援的大小寫類型: {case_type}")
        except Exception as e:
            raise TransformationError(f"大小寫轉換失敗: {str(e)}") 
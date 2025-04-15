#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
適配器模組驗證器類定義
"""

from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
import json
import re
import logging
from pathlib import Path

from .base import BaseValidator
from .exceptions import ValidationError
from .config import ValidatorConfig

class StringValidator(BaseValidator):
    """字串驗證器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.min_length = config.get('min_length')
        self.max_length = config.get('max_length')
        self.pattern = config.get('pattern')
        if self.pattern:
            self.regex = re.compile(self.pattern)
    
    def validate(self, data: Any) -> bool:
        """驗證字串"""
        try:
            if not isinstance(data, str):
                raise ValidationError("資料必須是字串類型")
            
            if self.min_length is not None and len(data) < self.min_length:
                raise ValidationError(f"字串長度必須大於等於 {self.min_length}")
            
            if self.max_length is not None and len(data) > self.max_length:
                raise ValidationError(f"字串長度必須小於等於 {self.max_length}")
            
            if self.pattern and not self.regex.match(data):
                raise ValidationError(f"字串必須符合模式: {self.pattern}")
            
            return True
        except Exception as e:
            raise ValidationError(f"字串驗證失敗: {str(e)}")

class NumberValidator(BaseValidator):
    """數字驗證器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.min_value = config.get('min_value')
        self.max_value = config.get('max_value')
        self.is_integer = config.get('is_integer', False)
    
    def validate(self, data: Any) -> bool:
        """驗證數字"""
        try:
            if not isinstance(data, (int, float)):
                raise ValidationError("資料必須是數字類型")
            
            if self.is_integer and not isinstance(data, int):
                raise ValidationError("資料必須是整數")
            
            if self.min_value is not None and data < self.min_value:
                raise ValidationError(f"數字必須大於等於 {self.min_value}")
            
            if self.max_value is not None and data > self.max_value:
                raise ValidationError(f"數字必須小於等於 {self.max_value}")
            
            return True
        except Exception as e:
            raise ValidationError(f"數字驗證失敗: {str(e)}")

class DateTimeValidator(BaseValidator):
    """日期時間驗證器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.format = config.get('format', '%Y-%m-%d %H:%M:%S')
        self.min_date = config.get('min_date')
        self.max_date = config.get('max_date')
    
    def validate(self, data: Any) -> bool:
        """驗證日期時間"""
        try:
            if isinstance(data, str):
                data = datetime.strptime(data, self.format)
            elif not isinstance(data, datetime):
                raise ValidationError("資料必須是日期時間類型")
            
            if self.min_date and data < self.min_date:
                raise ValidationError(f"日期必須大於等於 {self.min_date}")
            
            if self.max_date and data > self.max_date:
                raise ValidationError(f"日期必須小於等於 {self.max_date}")
            
            return True
        except Exception as e:
            raise ValidationError(f"日期時間驗證失敗: {str(e)}")

class ListValidator(BaseValidator):
    """列表驗證器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.min_length = config.get('min_length')
        self.max_length = config.get('max_length')
        self.item_validator = config.get('item_validator')
    
    def validate(self, data: Any) -> bool:
        """驗證列表"""
        try:
            if not isinstance(data, list):
                raise ValidationError("資料必須是列表類型")
            
            if self.min_length is not None and len(data) < self.min_length:
                raise ValidationError(f"列表長度必須大於等於 {self.min_length}")
            
            if self.max_length is not None and len(data) > self.max_length:
                raise ValidationError(f"列表長度必須小於等於 {self.max_length}")
            
            if self.item_validator:
                for item in data:
                    if not self.item_validator.validate(item):
                        raise ValidationError("列表項目驗證失敗")
            
            return True
        except Exception as e:
            raise ValidationError(f"列表驗證失敗: {str(e)}")

class DictValidator(BaseValidator):
    """字典驗證器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.required_fields = config.get('required_fields', [])
        self.field_validators = config.get('field_validators', {})
    
    def validate(self, data: Any) -> bool:
        """驗證字典"""
        try:
            if not isinstance(data, dict):
                raise ValidationError("資料必須是字典類型")
            
            # 檢查必填欄位
            for field in self.required_fields:
                if field not in data:
                    raise ValidationError(f"缺少必填欄位: {field}")
            
            # 驗證欄位
            for field, validator in self.field_validators.items():
                if field in data and not validator.validate(data[field]):
                    raise ValidationError(f"欄位 {field} 驗證失敗")
            
            return True
        except Exception as e:
            raise ValidationError(f"字典驗證失敗: {str(e)}")

class BooleanValidator(BaseValidator):
    """布爾值驗證器"""
    
    def validate(self, data: Any) -> bool:
        """驗證布爾值"""
        try:
            if not isinstance(data, bool):
                raise ValidationError("資料必須是布爾值類型")
            return True
        except Exception as e:
            raise ValidationError(f"布爾值驗證失敗: {str(e)}")

class JsonValidator(BaseValidator):
    """JSON 驗證器"""
    
    def validate(self, data: Any) -> bool:
        """驗證 JSON"""
        try:
            if isinstance(data, str):
                json.loads(data)
            else:
                json.dumps(data)
            return True
        except Exception as e:
            raise ValidationError(f"JSON 驗證失敗: {str(e)}")

class PathValidator(BaseValidator):
    """路徑驗證器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.exists = config.get('exists', False)
        self.is_file = config.get('is_file', False)
        self.is_dir = config.get('is_dir', False)
    
    def validate(self, data: Any) -> bool:
        """驗證路徑"""
        try:
            if not isinstance(data, (str, Path)):
                raise ValidationError("資料必須是路徑類型")
            
            path = Path(data)
            
            if self.exists and not path.exists():
                raise ValidationError("路徑必須存在")
            
            if self.is_file and not path.is_file():
                raise ValidationError("路徑必須是檔案")
            
            if self.is_dir and not path.is_dir():
                raise ValidationError("路徑必須是目錄")
            
            return True
        except Exception as e:
            raise ValidationError(f"路徑驗證失敗: {str(e)}")

class RegexValidator(BaseValidator):
    """正則表達式驗證器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.pattern = config.get('pattern')
        if not self.pattern:
            raise ValidationError("未指定正則表達式模式")
        self.regex = re.compile(self.pattern)
    
    def validate(self, data: Any) -> bool:
        """驗證正則表達式"""
        try:
            if not isinstance(data, str):
                raise ValidationError("資料必須是字串類型")
            
            if not self.regex.match(data):
                raise ValidationError(f"字串必須符合模式: {self.pattern}")
            
            return True
        except Exception as e:
            raise ValidationError(f"正則表達式驗證失敗: {str(e)}")

class CustomValidator(BaseValidator):
    """自定義驗證器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.validate_func = config.get('validate_func')
        if not callable(self.validate_func):
            raise ValidationError("未指定驗證函數")
    
    def validate(self, data: Any) -> bool:
        """使用自定義函數驗證資料"""
        try:
            return self.validate_func(data)
        except Exception as e:
            raise ValidationError(f"自定義驗證失敗: {str(e)}")

class TypeValidator(BaseValidator):
    """類型驗證器"""
    
    def validate(self, data: Any) -> bool:
        """
        驗證資料類型
        
        Args:
            data: 要驗證的資料
            
        Returns:
            驗證結果
            
        Raises:
            ValidationError: 驗證失敗
        """
        expected_type = self.config.params.get("type")
        if not expected_type:
            raise ValidationError("未指定期望的類型")
            
        if not isinstance(data, expected_type):
            raise ValidationError(f"資料類型不匹配: 期望 {expected_type.__name__}, 實際 {type(data).__name__}")
            
        return True

class RangeValidator(BaseValidator):
    """範圍驗證器"""
    
    def validate(self, data: Any) -> bool:
        """
        驗證數值範圍
        
        Args:
            data: 要驗證的資料
            
        Returns:
            驗證結果
            
        Raises:
            ValidationError: 驗證失敗
        """
        min_value = self.config.params.get("min")
        max_value = self.config.params.get("max")
        
        if min_value is not None and data < min_value:
            raise ValidationError(f"數值小於最小值: {min_value}")
            
        if max_value is not None and data > max_value:
            raise ValidationError(f"數值大於最大值: {max_value}")
            
        return True

class LengthValidator(BaseValidator):
    """長度驗證器"""
    
    def validate(self, data: Any) -> bool:
        """
        驗證序列長度
        
        Args:
            data: 要驗證的資料
            
        Returns:
            驗證結果
            
        Raises:
            ValidationError: 驗證失敗
        """
        min_length = self.config.params.get("min_length")
        max_length = self.config.params.get("max_length")
        
        if not hasattr(data, "__len__"):
            raise ValidationError("資料沒有長度屬性")
            
        length = len(data)
        
        if min_length is not None and length < min_length:
            raise ValidationError(f"長度小於最小值: {min_length}")
            
        if max_length is not None and length > max_length:
            raise ValidationError(f"長度大於最大值: {max_length}")
            
        return True

class PatternValidator(BaseValidator):
    """模式驗證器"""
    
    def validate(self, data: Any) -> bool:
        """
        驗證字串模式
        
        Args:
            data: 要驗證的資料
            
        Returns:
            驗證結果
            
        Raises:
            ValidationError: 驗證失敗
        """
        import re
        
        pattern = self.config.params.get("pattern")
        if not pattern:
            raise ValidationError("未指定正則表達式模式")
            
        if not isinstance(data, str):
            raise ValidationError("資料不是字串類型")
            
        if not re.match(pattern, data):
            raise ValidationError(f"字串不符合模式: {pattern}")
            
        return True

class EnumValidator(BaseValidator):
    """枚舉驗證器"""
    
    def validate(self, data: Any) -> bool:
        """
        驗證枚舉值
        
        Args:
            data: 要驗證的資料
            
        Returns:
            驗證結果
            
        Raises:
            ValidationError: 驗證失敗
        """
        allowed_values = self.config.params.get("values")
        if not allowed_values:
            raise ValidationError("未指定允許的值")
            
        if data not in allowed_values:
            raise ValidationError(f"值不在允許範圍內: {allowed_values}")
            
        return True 
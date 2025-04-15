#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基本適配器實現
"""

from typing import Any, Dict, List, Optional, Union
from .base import BaseAdapter
from .config import AdapterConfig
from .exceptions import AdaptationError
from .validators import TypeValidator, RangeValidator, LengthValidator, PatternValidator, EnumValidator
from .transformers import TypeTransformer, StringTransformer, NumberTransformer, ListTransformer, DictTransformer, CaseTransformer

class DataAdapter(BaseAdapter):
    """資料適配器"""
    
    def __init__(self, config: AdapterConfig):
        """
        初始化資料適配器
        
        Args:
            config: 適配器配置
        """
        super().__init__(config)
        self._setup_default_validators()
        self._setup_default_transformers()
        
    def _setup_default_validators(self):
        """設置預設驗證器"""
        # 類型驗證
        if "type" in self.config.validation:
            self.add_validator(TypeValidator(self.config.validation["type"]))
            
        # 範圍驗證
        if "range" in self.config.validation:
            self.add_validator(RangeValidator(self.config.validation["range"]))
            
        # 長度驗證
        if "length" in self.config.validation:
            self.add_validator(LengthValidator(self.config.validation["length"]))
            
        # 模式驗證
        if "pattern" in self.config.validation:
            self.add_validator(PatternValidator(self.config.validation["pattern"]))
            
        # 枚舉驗證
        if "enum" in self.config.validation:
            self.add_validator(EnumValidator(self.config.validation["enum"]))
            
    def _setup_default_transformers(self):
        """設置預設轉換器"""
        # 類型轉換
        if "type" in self.config.transformation:
            self.add_transformer(TypeTransformer(self.config.transformation["type"]))
            
        # 字串轉換
        if "string" in self.config.transformation:
            self.add_transformer(StringTransformer(self.config.transformation["string"]))
            
        # 數值轉換
        if "number" in self.config.transformation:
            self.add_transformer(NumberTransformer(self.config.transformation["number"]))
            
        # 列表轉換
        if "list" in self.config.transformation:
            self.add_transformer(ListTransformer(self.config.transformation["list"]))
            
        # 字典轉換
        if "dict" in self.config.transformation:
            self.add_transformer(DictTransformer(self.config.transformation["dict"]))
            
        # 大小寫轉換
        if "case" in self.config.transformation:
            self.add_transformer(CaseTransformer(self.config.transformation["case"]))
            
    def adapt(self, data: Any) -> Any:
        """
        適配資料
        
        Args:
            data: 要適配的資料
            
        Returns:
            適配後的資料
            
        Raises:
            AdaptationError: 適配失敗
        """
        try:
            # 驗證資料
            for validator in self.validators:
                validator.validate(data)
                
            # 轉換資料
            result = data
            for transformer in self.transformers:
                result = transformer.transform(result)
                
            return result
        except Exception as e:
            raise AdaptationError(f"資料適配失敗: {str(e)}")
            
    def validate(self, data: Any) -> bool:
        """
        驗證資料
        
        Args:
            data: 要驗證的資料
            
        Returns:
            驗證是否通過
        """
        try:
            for validator in self.validators:
                validator.validate(data)
            return True
        except Exception:
            return False
            
    def transform(self, data: Any) -> Any:
        """
        轉換資料
        
        Args:
            data: 要轉換的資料
            
        Returns:
            轉換後的資料
            
        Raises:
            AdaptationError: 轉換失敗
        """
        try:
            result = data
            for transformer in self.transformers:
                result = transformer.transform(result)
            return result
        except Exception as e:
            raise AdaptationError(f"資料轉換失敗: {str(e)}") 
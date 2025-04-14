#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置驗證器模組

提供配置文件的驗證功能，包括：
1. JSON Schema 驗證
2. 類型檢查
3. 範圍檢查
4. 依賴檢查
"""

import json
from typing import Dict, Any, List, Optional, Union, Callable
from pathlib import Path

from .paths import CONFIG_DIR
from ..core.error import ConfigError, handle_error

class ConfigValidator:
    """配置驗證器類別"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化配置驗證器
        
        Args:
            config_dir: 配置目錄路徑
        """
        self.config_dir = config_dir or CONFIG_DIR
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.validators: Dict[str, List[Callable]] = {}
        
    @handle_error()
    def load_schema(self, filename: str) -> Dict[str, Any]:
        """
        加載 JSON Schema
        
        Args:
            filename: Schema 文件名
            
        Returns:
            Schema 字典
        """
        filepath = os.path.join(self.config_dir, "schemas", filename)
        if not os.path.exists(filepath):
            raise ConfigError(f"Schema 文件不存在：{filepath}")
            
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    @handle_error()
    def register_schema(self, name: str, schema: Dict[str, Any]) -> None:
        """
        註冊 Schema
        
        Args:
            name: Schema 名稱
            schema: Schema 字典
        """
        self.schemas[name] = schema
        
    @handle_error()
    def register_validator(self, name: str, validator: Callable) -> None:
        """
        註冊驗證器
        
        Args:
            name: 驗證器名稱
            validator: 驗證函數
        """
        if name not in self.validators:
            self.validators[name] = []
        self.validators[name].append(validator)
        
    @handle_error()
    def validate_schema(self, config: Dict[str, Any], schema_name: str) -> bool:
        """
        使用 JSON Schema 驗證配置
        
        Args:
            config: 配置字典
            schema_name: Schema 名稱
            
        Returns:
            是否驗證通過
        """
        if schema_name not in self.schemas:
            raise ConfigError(f"Schema 不存在：{schema_name}")
            
        schema = self.schemas[schema_name]
        try:
            import jsonschema
            jsonschema.validate(instance=config, schema=schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            raise ConfigError(f"配置驗證失敗：{str(e)}")
            
    @handle_error()
    def validate_type(self, value: Any, expected_type: type) -> bool:
        """
        驗證類型
        
        Args:
            value: 待驗證的值
            expected_type: 期望的類型
            
        Returns:
            是否驗證通過
        """
        return isinstance(value, expected_type)
        
    @handle_error()
    def validate_range(self, value: Union[int, float], min_value: Union[int, float], max_value: Union[int, float]) -> bool:
        """
        驗證範圍
        
        Args:
            value: 待驗證的值
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            是否驗證通過
        """
        return min_value <= value <= max_value
        
    @handle_error()
    def validate_dependency(self, config: Dict[str, Any], dependency: Dict[str, Any]) -> bool:
        """
        驗證依賴
        
        Args:
            config: 配置字典
            dependency: 依賴字典
            
        Returns:
            是否驗證通過
        """
        for key, value in dependency.items():
            if key not in config or config[key] != value:
                return False
        return True
        
    @handle_error()
    def validate(self, config: Dict[str, Any], schema_name: Optional[str] = None) -> bool:
        """
        驗證配置
        
        Args:
            config: 配置字典
            schema_name: Schema 名稱
            
        Returns:
            是否驗證通過
        """
        # 使用 Schema 驗證
        if schema_name:
            self.validate_schema(config, schema_name)
            
        # 使用自定義驗證器
        for name, validators in self.validators.items():
            for validator in validators:
                if not validator(config):
                    raise ConfigError(f"配置驗證失敗：{name}")
                    
        return True 
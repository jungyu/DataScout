#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置加載器模組

提供配置文件的加載功能，包括：
1. JSON 配置文件加載
2. YAML 配置文件加載
3. 環境變量加載
4. 命令行參數加載
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path

from .paths import CONFIG_DIR
from ..core.error import ConfigError, handle_error

class ConfigLoader:
    """配置加載器類別"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化配置加載器
        
        Args:
            config_dir: 配置目錄路徑
        """
        self.config_dir = config_dir or CONFIG_DIR
        self.config: Dict[str, Any] = {}
        
    @handle_error()
    def load_json(self, filename: str) -> Dict[str, Any]:
        """
        加載 JSON 配置文件
        
        Args:
            filename: 配置文件名
            
        Returns:
            配置字典
        """
        filepath = os.path.join(self.config_dir, filename)
        if not os.path.exists(filepath):
            raise ConfigError(f"配置文件不存在：{filepath}")
            
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    @handle_error()
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        加載 YAML 配置文件
        
        Args:
            filename: 配置文件名
            
        Returns:
            配置字典
        """
        filepath = os.path.join(self.config_dir, filename)
        if not os.path.exists(filepath):
            raise ConfigError(f"配置文件不存在：{filepath}")
            
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    @handle_error()
    def load_env(self, prefix: str = "SELENIUM_") -> Dict[str, Any]:
        """
        加載環境變量
        
        Args:
            prefix: 環境變量前綴
            
        Returns:
            配置字典
        """
        config = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                config[config_key] = value
        return config
        
    @handle_error()
    def load(self, filename: str) -> Dict[str, Any]:
        """
        加載配置文件
        
        Args:
            filename: 配置文件名
            
        Returns:
            配置字典
        """
        filepath = os.path.join(self.config_dir, filename)
        if not os.path.exists(filepath):
            raise ConfigError(f"配置文件不存在：{filepath}")
            
        ext = Path(filepath).suffix.lower()
        if ext == '.json':
            return self.load_json(filename)
        elif ext in ['.yml', '.yaml']:
            return self.load_yaml(filename)
        else:
            raise ConfigError(f"不支持的配置文件格式：{ext}")
            
    @handle_error()
    def save(self, config: Dict[str, Any], filename: str) -> None:
        """
        保存配置文件
        
        Args:
            config: 配置字典
            filename: 配置文件名
        """
        filepath = os.path.join(self.config_dir, filename)
        ext = Path(filepath).suffix.lower()
        
        if ext == '.json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        elif ext in ['.yml', '.yaml']:
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
        else:
            raise ConfigError(f"不支持的配置文件格式：{ext}")
            
    @handle_error()
    def merge(self, config: Dict[str, Any]) -> None:
        """
        合併配置
        
        Args:
            config: 配置字典
        """
        self.config.update(config)
        
    @handle_error()
    def get(self, key: str, default: Any = None) -> Any:
        """
        獲取配置項
        
        Args:
            key: 配置項鍵名
            default: 默認值
            
        Returns:
            配置項值
        """
        return self.config.get(key, default)
        
    @handle_error()
    def set(self, key: str, value: Any) -> None:
        """
        設置配置項
        
        Args:
            key: 配置項鍵名
            value: 配置項值
        """
        self.config[key] = value
        
    @handle_error()
    def clear(self) -> None:
        """清空配置"""
        self.config.clear()
        
    def __getitem__(self, key: str) -> Any:
        """獲取配置項"""
        return self.config[key]
        
    def __setitem__(self, key: str, value: Any) -> None:
        """設置配置項"""
        self.config[key] = value
        
    def __contains__(self, key: str) -> bool:
        """檢查配置項是否存在"""
        return key in self.config 
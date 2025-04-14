#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理器模組

提供以下功能：
1. 配置加載
2. 配置驗證
3. 配置管理
4. 配置合併
"""

import os
import yaml
import logging
from typing import Dict, Optional, List
from pathlib import Path

from .config_exceptions import ConfigError
from .config_validator import ConfigValidator

class ConfigManager:
    """配置管理器類"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置目錄路徑，默認為模組目錄
        """
        self.config_dir = config_dir or os.path.dirname(__file__)
        self.logger = logging.getLogger("crawler.config")
        self.validator = ConfigValidator()
        
        # 初始化配置
        self.configs = {}
        self._load_configs()
        
    def _load_configs(self) -> None:
        """加載所有配置"""
        # 加載通用配置
        self.configs["common"] = self._load_yaml("common/default.yaml")
        
        # 加載瀏覽器配置
        self.configs["browser"] = self._load_yaml("browser/default.yaml")
        
        # 加載請求配置
        self.configs["request"] = self._load_yaml("request/default.yaml")
        
        # 加載速率限制配置
        self.configs["rate_limit"] = self._load_yaml("rate_limit/default.yaml")
        
    def _load_yaml(self, relative_path: str) -> Dict:
        """
        加載 YAML 配置文件
        
        Args:
            relative_path: 相對路徑
            
        Returns:
            配置字典
        """
        try:
            file_path = os.path.join(self.config_dir, relative_path)
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"加載配置文件失敗: {file_path}, 錯誤: {str(e)}")
            return {}
            
    def get_config(self, module: str) -> Dict:
        """
        獲取指定模組的配置
        
        Args:
            module: 模組名稱
            
        Returns:
            配置字典
        """
        return self.configs.get(module, {})
        
    def get_full_config(self) -> Dict:
        """
        獲取完整配置
        
        Returns:
            完整配置字典
        """
        return {
            "common": self.configs["common"],
            "browser": self.configs["browser"],
            "request": self.configs["request"],
            "rate_limit": self.configs["rate_limit"]
        }
        
    def update_config(self, module: str, config: Dict) -> None:
        """
        更新指定模組的配置
        
        Args:
            module: 模組名稱
            config: 新配置
        """
        if module not in self.configs:
            raise ConfigError(f"未知的模組: {module}")
            
        # 驗證配置
        self.validator.validate_config(module, config)
        
        # 更新配置
        self.configs[module].update(config)
        
    def save_config(self, module: str, config: Dict) -> None:
        """
        保存配置到文件
        
        Args:
            module: 模組名稱
            config: 配置字典
        """
        try:
            file_path = os.path.join(self.config_dir, f"{module}/default.yaml")
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            self.logger.error(f"保存配置文件失敗: {file_path}, 錯誤: {str(e)}")
            
    def reload_config(self) -> None:
        """重新加載所有配置"""
        self._load_configs() 
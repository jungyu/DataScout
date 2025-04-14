#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置更新器模組

提供配置文件的更新功能，包括：
1. 配置合併
2. 配置覆蓋
3. 配置回滾
4. 配置備份
"""

import os
import json
import shutil
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path

from .paths import CONFIG_DIR
from ..core.error import ConfigError, handle_error

class ConfigUpdater:
    """配置更新器類別"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化配置更新器
        
        Args:
            config_dir: 配置目錄路徑
        """
        self.config_dir = config_dir or CONFIG_DIR
        self.backup_dir = os.path.join(self.config_dir, "backups")
        os.makedirs(self.backup_dir, exist_ok=True)
        
    @handle_error()
    def merge(self, config: Dict[str, Any], new_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        合併配置
        
        Args:
            config: 原始配置
            new_config: 新配置
            
        Returns:
            合併後的配置
        """
        result = config.copy()
        for key, value in new_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge(result[key], value)
            else:
                result[key] = value
        return result
        
    @handle_error()
    def update(self, config: Dict[str, Any], new_config: Dict[str, Any], backup: bool = True) -> Dict[str, Any]:
        """
        更新配置
        
        Args:
            config: 原始配置
            new_config: 新配置
            backup: 是否備份
            
        Returns:
            更新後的配置
        """
        if backup:
            self.backup(config)
            
        return self.merge(config, new_config)
        
    @handle_error()
    def backup(self, config: Dict[str, Any], name: Optional[str] = None) -> str:
        """
        備份配置
        
        Args:
            config: 配置字典
            name: 備份名稱
            
        Returns:
            備份文件路徑
        """
        if name is None:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")
            
        backup_file = os.path.join(self.backup_dir, f"{name}.json")
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            
        return backup_file
        
    @handle_error()
    def restore(self, name: str) -> Dict[str, Any]:
        """
        恢復配置
        
        Args:
            name: 備份名稱
            
        Returns:
            恢復的配置
        """
        backup_file = os.path.join(self.backup_dir, f"{name}.json")
        if not os.path.exists(backup_file):
            raise ConfigError(f"備份文件不存在：{backup_file}")
            
        with open(backup_file, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    @handle_error()
    def list_backups(self) -> List[str]:
        """
        列出所有備份
        
        Returns:
            備份名稱列表
        """
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.json'):
                backups.append(file[:-5])
        return sorted(backups)
        
    @handle_error()
    def delete_backup(self, name: str) -> None:
        """
        刪除備份
        
        Args:
            name: 備份名稱
        """
        backup_file = os.path.join(self.backup_dir, f"{name}.json")
        if os.path.exists(backup_file):
            os.remove(backup_file)
            
    @handle_error()
    def clear_backups(self) -> None:
        """清空所有備份"""
        shutil.rmtree(self.backup_dir)
        os.makedirs(self.backup_dir, exist_ok=True) 
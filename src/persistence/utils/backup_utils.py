#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
備份工具類
提供數據備份和恢復功能
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .config_utils import ConfigUtils
from .logger import Logger
from .path_utils import PathUtils

class BackupUtils:
    """備份工具類"""
    
    def __init__(self):
        """初始化備份工具"""
        self.config_utils = ConfigUtils()
        self.logger = Logger()
        self.path_utils = PathUtils()
        
        # 獲取備份配置
        self.backup_config = self.config_utils.get_config('backup')
        self.backup_dir = self.path_utils.get_abs_path('backups')
        self.max_backups = self.backup_config.get('max_backups', 5)
        
        # 確保備份目錄存在
        self.path_utils.ensure_dir_exists(self.backup_dir)
    
    def create_backup(self, name: str) -> bool:
        """
        創建備份
        
        Args:
            name: 備份名稱
            
        Returns:
            bool: 是否成功
        """
        try:
            # 生成備份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{name}_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            # 創建備份目錄
            self.path_utils.ensure_dir_exists(backup_path)
            
            # 備份數據目錄
            data_dir = self.path_utils.get_abs_path('data')
            if data_dir.exists():
                shutil.copytree(data_dir, backup_path / 'data')
            
            # 備份配置文件
            config_dir = self.path_utils.get_abs_path('config')
            if config_dir.exists():
                shutil.copytree(config_dir, backup_path / 'config')
            
            # 記錄備份信息
            backup_info = {
                'name': name,
                'timestamp': timestamp,
                'path': str(backup_path)
            }
            
            # 保存備份信息
            info_path = backup_path / 'backup_info.json'
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, ensure_ascii=False, indent=2)
            
            # 清理舊備份
            self._cleanup_old_backups()
            
            self.logger.info(f"創建備份成功: {backup_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"創建備份失敗: {str(e)}")
            return False
    
    def restore_backup(self, name: str) -> bool:
        """
        恢復備份
        
        Args:
            name: 備份名稱
            
        Returns:
            bool: 是否成功
        """
        try:
            # 查找備份
            backup_path = self._find_backup(name)
            if not backup_path:
                self.logger.error(f"找不到備份: {name}")
                return False
            
            # 恢復數據目錄
            data_dir = self.path_utils.get_abs_path('data')
            backup_data_dir = backup_path / 'data'
            if backup_data_dir.exists():
                if data_dir.exists():
                    shutil.rmtree(data_dir)
                shutil.copytree(backup_data_dir, data_dir)
            
            # 恢復配置文件
            config_dir = self.path_utils.get_abs_path('config')
            backup_config_dir = backup_path / 'config'
            if backup_config_dir.exists():
                if config_dir.exists():
                    shutil.rmtree(config_dir)
                shutil.copytree(backup_config_dir, config_dir)
            
            self.logger.info(f"恢復備份成功: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"恢復備份失敗: {str(e)}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        列出所有備份
        
        Returns:
            List[Dict[str, Any]]: 備份列表
        """
        backups = []
        try:
            for backup_dir in self.backup_dir.iterdir():
                if not backup_dir.is_dir():
                    continue
                    
                info_path = backup_dir / 'backup_info.json'
                if not info_path.exists():
                    continue
                    
                with open(info_path, 'r', encoding='utf-8') as f:
                    backup_info = json.load(f)
                    backups.append(backup_info)
                    
            return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"列出備份失敗: {str(e)}")
            return []
    
    def delete_backup(self, name: str) -> bool:
        """
        刪除備份
        
        Args:
            name: 備份名稱
            
        Returns:
            bool: 是否成功
        """
        try:
            # 查找備份
            backup_path = self._find_backup(name)
            if not backup_path:
                self.logger.error(f"找不到備份: {name}")
                return False
            
            # 刪除備份目錄
            shutil.rmtree(backup_path)
            
            self.logger.info(f"刪除備份成功: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"刪除備份失敗: {str(e)}")
            return False
    
    def _find_backup(self, name: str) -> Optional[Path]:
        """
        查找備份
        
        Args:
            name: 備份名稱
            
        Returns:
            Optional[Path]: 備份路徑
        """
        for backup_dir in self.backup_dir.iterdir():
            if not backup_dir.is_dir():
                continue
                
            info_path = backup_dir / 'backup_info.json'
            if not info_path.exists():
                continue
                
            with open(info_path, 'r', encoding='utf-8') as f:
                backup_info = json.load(f)
                if backup_info['name'] == name:
                    return backup_dir
                    
        return None
    
    def _cleanup_old_backups(self):
        """清理舊備份"""
        try:
            backups = self.list_backups()
            if len(backups) <= self.max_backups:
                return
                
            # 刪除多餘的備份
            for backup in backups[self.max_backups:]:
                backup_path = Path(backup['path'])
                if backup_path.exists():
                    shutil.rmtree(backup_path)
                    
        except Exception as e:
            self.logger.error(f"清理舊備份失敗: {str(e)}") 
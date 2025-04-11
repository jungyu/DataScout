#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存儲工具類
提供存儲相關的通用功能
"""

import os
import json
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from src.core.utils import CoreMixin

class StorageUtils(CoreMixin):
    """存儲工具類"""
    
    @staticmethod
    def ensure_directory(path: Path) -> None:
        """
        確保目錄存在
        
        Args:
            path: 目錄路徑
        """
        path.mkdir(parents=True, exist_ok=True)
        
    @staticmethod
    def save_json(data: Dict[str, Any], filepath: Path) -> bool:
        """
        保存 JSON 數據
        
        Args:
            data: 要保存的數據
            filepath: 文件路徑
            
        Returns:
            是否保存成功
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            return False
            
    @staticmethod
    def load_json(filepath: Path) -> Optional[Dict[str, Any]]:
        """
        加載 JSON 數據
        
        Args:
            filepath: 文件路徑
            
        Returns:
            加載的數據，如果失敗則返回 None
        """
        try:
            if not filepath.exists():
                return None
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
            
    @staticmethod
    def create_backup(source: Path, backup_dir: Path, prefix: str = "backup") -> Optional[Path]:
        """
        創建備份
        
        Args:
            source: 源文件或目錄
            backup_dir: 備份目錄
            prefix: 備份文件名前綴
            
        Returns:
            備份路徑，如果失敗則返回 None
        """
        try:
            if not source.exists():
                return None
                
            # 生成備份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{prefix}_{timestamp}"
            backup_path = backup_dir / backup_name
            
            # 創建備份
            if source.is_file():
                shutil.copy2(source, backup_path)
            else:
                shutil.copytree(source, backup_path)
                
            return backup_path
        except Exception:
            return None
            
    @staticmethod
    def restore_backup(backup_path: Path, target: Path) -> bool:
        """
        恢復備份
        
        Args:
            backup_path: 備份路徑
            target: 目標路徑
            
        Returns:
            是否恢復成功
        """
        try:
            if not backup_path.exists():
                return False
                
            # 如果目標存在，先刪除
            if target.exists():
                if target.is_file():
                    target.unlink()
                else:
                    shutil.rmtree(target)
                    
            # 恢復備份
            if backup_path.is_file():
                shutil.copy2(backup_path, target)
            else:
                shutil.copytree(backup_path, target)
                
            return True
        except Exception:
            return False
            
    @staticmethod
    def list_backups(backup_dir: Path, prefix: str = "backup") -> List[Dict[str, Any]]:
        """
        列出備份
        
        Args:
            backup_dir: 備份目錄
            prefix: 備份文件名前綴
            
        Returns:
            備份列表，每個備份包含路徑和時間戳
        """
        try:
            if not backup_dir.exists():
                return []
                
            backups = []
            for item in backup_dir.iterdir():
                if item.name.startswith(prefix):
                    try:
                        # 從文件名中提取時間戳
                        timestamp_str = item.name.split('_')[1]
                        timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        backups.append({
                            'path': item,
                            'timestamp': timestamp,
                            'size': item.stat().st_size if item.is_file() else sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                        })
                    except (ValueError, IndexError):
                        continue
                        
            return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
        except Exception:
            return []
            
    @staticmethod
    def delete_backup(backup_path: Path) -> bool:
        """
        刪除備份
        
        Args:
            backup_path: 備份路徑
            
        Returns:
            是否刪除成功
        """
        try:
            if not backup_path.exists():
                return False
                
            if backup_path.is_file():
                backup_path.unlink()
            else:
                shutil.rmtree(backup_path)
                
            return True
        except Exception:
            return False 
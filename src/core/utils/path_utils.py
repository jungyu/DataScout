#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
路徑處理工具

提供路徑處理相關的功能，包括：
- 路徑操作
- 目錄管理
- 文件操作
- 路徑轉換
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional, List, Union
from datetime import datetime

class PathUtils:
    """路徑處理工具類"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化路徑工具
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
    def join_path(self, *paths: str) -> str:
        """
        連接路徑
        
        Args:
            *paths: 路徑片段
            
        Returns:
            連接後的路徑
        """
        try:
            return os.path.join(*paths)
        except Exception as e:
            self.logger.error(f"連接路徑失敗: {str(e)}")
            return ""
            
    def ensure_dir(self, path: str) -> bool:
        """
        確保目錄存在
        
        Args:
            path: 目錄路徑
            
        Returns:
            是否成功
        """
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"創建目錄失敗: {str(e)}")
            return False
            
    def get_output_dir(self, base_dir: str, config: Optional[dict] = None) -> str:
        """
        獲取輸出目錄
        
        Args:
            base_dir: 基礎目錄
            config: 配置信息
            
        Returns:
            輸出目錄路徑
        """
        try:
            output_dir = config.get("output_dir", "output") if config else "output"
            return self.join_path(base_dir, output_dir)
        except Exception as e:
            self.logger.error(f"獲取輸出目錄失敗: {str(e)}")
            return self.join_path(base_dir, "output")
            
    def get_screenshot_dir(self, base_dir: str, config: Optional[dict] = None) -> str:
        """
        獲取截圖目錄
        
        Args:
            base_dir: 基礎目錄
            config: 配置信息
            
        Returns:
            截圖目錄路徑
        """
        try:
            screenshot_dir = config.get("screenshot_dir", "screenshots") if config else "screenshots"
            return self.join_path(base_dir, screenshot_dir)
        except Exception as e:
            self.logger.error(f"獲取截圖目錄失敗: {str(e)}")
            return self.join_path(base_dir, "screenshots")
            
    def get_debug_dir(self, base_dir: str, config: Optional[dict] = None) -> str:
        """
        獲取調試目錄
        
        Args:
            base_dir: 基礎目錄
            config: 配置信息
            
        Returns:
            調試目錄路徑
        """
        try:
            debug_dir = config.get("debug_dir", "debug") if config else "debug"
            return self.join_path(base_dir, debug_dir)
        except Exception as e:
            self.logger.error(f"獲取調試目錄失敗: {str(e)}")
            return self.join_path(base_dir, "debug")
            
    def get_log_dir(self, base_dir: str, config: Optional[dict] = None) -> str:
        """
        獲取日誌目錄
        
        Args:
            base_dir: 基礎目錄
            config: 配置信息
            
        Returns:
            日誌目錄路徑
        """
        try:
            log_dir = config.get("log_dir", "logs") if config else "logs"
            return self.join_path(base_dir, log_dir)
        except Exception as e:
            self.logger.error(f"獲取日誌目錄失敗: {str(e)}")
            return self.join_path(base_dir, "logs")
            
    def get_temp_dir(self, base_dir: str, config: Optional[dict] = None) -> str:
        """
        獲取臨時目錄
        
        Args:
            base_dir: 基礎目錄
            config: 配置信息
            
        Returns:
            臨時目錄路徑
        """
        try:
            temp_dir = config.get("temp_dir", "temp") if config else "temp"
            return self.join_path(base_dir, temp_dir)
        except Exception as e:
            self.logger.error(f"獲取臨時目錄失敗: {str(e)}")
            return self.join_path(base_dir, "temp")
            
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """
        列出目錄中的文件
        
        Args:
            directory: 目錄路徑
            pattern: 文件匹配模式
            
        Returns:
            文件路徑列表
        """
        try:
            return [str(f) for f in Path(directory).glob(pattern)]
        except Exception as e:
            self.logger.error(f"列出文件失敗: {str(e)}")
            return []
            
    def delete_file(self, filepath: str) -> bool:
        """
        刪除文件
        
        Args:
            filepath: 文件路徑
            
        Returns:
            是否成功
        """
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            self.logger.error(f"刪除文件失敗: {str(e)}")
            return False
            
    def delete_dir(self, directory: str) -> bool:
        """
        刪除目錄
        
        Args:
            directory: 目錄路徑
            
        Returns:
            是否成功
        """
        try:
            shutil.rmtree(directory)
            return True
        except Exception as e:
            self.logger.error(f"刪除目錄失敗: {str(e)}")
            return False
            
    def copy_file(self, src: str, dst: str) -> bool:
        """
        複製文件
        
        Args:
            src: 源文件路徑
            dst: 目標文件路徑
            
        Returns:
            是否成功
        """
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            self.logger.error(f"複製文件失敗: {str(e)}")
            return False
            
    def move_file(self, src: str, dst: str) -> bool:
        """
        移動文件
        
        Args:
            src: 源文件路徑
            dst: 目標文件路徑
            
        Returns:
            是否成功
        """
        try:
            shutil.move(src, dst)
            return True
        except Exception as e:
            self.logger.error(f"移動文件失敗: {str(e)}")
            return False
            
    def get_file_size(self, filepath: str) -> int:
        """
        獲取文件大小
        
        Args:
            filepath: 文件路徑
            
        Returns:
            文件大小（字節）
        """
        try:
            return os.path.getsize(filepath)
        except Exception as e:
            self.logger.error(f"獲取文件大小失敗: {str(e)}")
            return 0
            
    def get_file_extension(self, filepath: str) -> str:
        """
        獲取文件擴展名
        
        Args:
            filepath: 文件路徑
            
        Returns:
            文件擴展名
        """
        try:
            return os.path.splitext(filepath)[1]
        except Exception as e:
            self.logger.error(f"獲取文件擴展名失敗: {str(e)}")
            return ""
            
    def get_file_name(self, filepath: str) -> str:
        """
        獲取文件名
        
        Args:
            filepath: 文件路徑
            
        Returns:
            文件名
        """
        try:
            return os.path.basename(filepath)
        except Exception as e:
            self.logger.error(f"獲取文件名失敗: {str(e)}")
            return ""
            
    def get_dir_name(self, filepath: str) -> str:
        """
        獲取目錄名
        
        Args:
            filepath: 文件路徑
            
        Returns:
            目錄名
        """
        try:
            return os.path.dirname(filepath)
        except Exception as e:
            self.logger.error(f"獲取目錄名失敗: {str(e)}")
            return ""
            
    def is_file(self, filepath: str) -> bool:
        """
        判斷是否為文件
        
        Args:
            filepath: 文件路徑
            
        Returns:
            是否為文件
        """
        try:
            return os.path.isfile(filepath)
        except Exception as e:
            self.logger.error(f"判斷是否為文件失敗: {str(e)}")
            return False
            
    def is_dir(self, filepath: str) -> bool:
        """
        判斷是否為目錄
        
        Args:
            filepath: 文件路徑
            
        Returns:
            是否為目錄
        """
        try:
            return os.path.isdir(filepath)
        except Exception as e:
            self.logger.error(f"判斷是否為目錄失敗: {str(e)}")
            return False
            
    def exists(self, filepath: str) -> bool:
        """
        判斷路徑是否存在
        
        Args:
            filepath: 文件路徑
            
        Returns:
            是否存在
        """
        try:
            return os.path.exists(filepath)
        except Exception as e:
            self.logger.error(f"判斷路徑是否存在失敗: {str(e)}")
            return False 
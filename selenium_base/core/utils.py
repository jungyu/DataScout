"""
工具類別模組

提供各種通用工具函數
"""

import os
import json
import yaml
import hashlib
import random
import string
import time
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

class Utils:
    """工具類別"""
    
    @staticmethod
    def generate_id(length: int = 8) -> str:
        """生成隨機ID
        
        Args:
            length: ID長度
            
        Returns:
            隨機ID字串
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_timestamp() -> str:
        """生成時間戳
        
        Returns:
            時間戳字串
        """
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    @staticmethod
    def calculate_md5(data: Union[str, bytes]) -> str:
        """計算MD5雜湊值
        
        Args:
            data: 要計算的資料
            
        Returns:
            MD5雜湊值字串
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.md5(data).hexdigest()
    
    @staticmethod
    def load_json(file_path: str) -> Dict:
        """載入JSON檔案
        
        Args:
            file_path: JSON檔案路徑
            
        Returns:
            JSON資料字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f'載入JSON檔案失敗: {e}')
            raise
    
    @staticmethod
    def save_json(data: Dict, file_path: str) -> None:
        """儲存JSON檔案
        
        Args:
            data: 要儲存的資料
            file_path: JSON檔案路徑
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f'儲存JSON檔案失敗: {e}')
            raise
    
    @staticmethod
    def load_yaml(file_path: str) -> Dict:
        """載入YAML檔案
        
        Args:
            file_path: YAML檔案路徑
            
        Returns:
            YAML資料字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.error(f'載入YAML檔案失敗: {e}')
            raise
    
    @staticmethod
    def save_yaml(data: Dict, file_path: str) -> None:
        """儲存YAML檔案
        
        Args:
            data: 要儲存的資料
            file_path: YAML檔案路徑
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            logging.error(f'儲存YAML檔案失敗: {e}')
            raise
    
    @staticmethod
    def sleep(seconds: float) -> None:
        """睡眠指定秒數
        
        Args:
            seconds: 睡眠秒數
        """
        time.sleep(seconds)
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """取得檔案大小
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            檔案大小(位元組)
        """
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            logging.error(f'取得檔案大小失敗: {e}')
            raise
    
    @staticmethod
    def ensure_dir(directory: str) -> None:
        """確保目錄存在
        
        Args:
            directory: 目錄路徑
        """
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            logging.error(f'建立目錄失敗: {e}')
            raise
    
    @staticmethod
    def list_files(directory: str, pattern: Optional[str] = None) -> List[str]:
        """列出目錄中的檔案
        
        Args:
            directory: 目錄路徑
            pattern: 檔案名稱模式
            
        Returns:
            檔案路徑列表
        """
        try:
            files = []
            for file in os.listdir(directory):
                if pattern is None or file.endswith(pattern):
                    files.append(os.path.join(directory, file))
            return files
        except Exception as e:
            logging.error(f'列出檔案失敗: {e}')
            raise
    
    @staticmethod
    def delete_file(file_path: str) -> None:
        """刪除檔案
        
        Args:
            file_path: 檔案路徑
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logging.error(f'刪除檔案失敗: {e}')
            raise 
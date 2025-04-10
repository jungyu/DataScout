"""
配置工具模組
提供配置文件的載入、驗證和管理功能
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigUtils:
    """配置工具類"""
    
    def __init__(self, logger=None):
        """
        初始化配置工具
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or print
        
    def load_config(self, config_path: str) -> Dict:
        """
        載入配置檔案
        
        Args:
            config_path: 配置文件路徑
            
        Returns:
            配置字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            self.logger(f"已載入配置檔案: {config_path}")
            return config
            
        except Exception as e:
            self.logger(f"載入配置檔案失敗: {str(e)}")
            raise
            
    def save_config(self, config: Dict, config_path: str) -> bool:
        """
        保存配置檔案
        
        Args:
            config: 配置字典
            config_path: 配置文件路徑
            
        Returns:
            是否成功
        """
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            self.logger(f"已保存配置檔案: {config_path}")
            return True
            
        except Exception as e:
            self.logger(f"保存配置檔案失敗: {str(e)}")
            return False
            
    def validate_config(self, config: Dict, required_fields: Dict[str, type]) -> bool:
        """
        驗證配置是否包含所有必要字段
        
        Args:
            config: 配置字典
            required_fields: 必要字段及其類型
            
        Returns:
            是否有效
        """
        try:
            for field, field_type in required_fields.items():
                if field not in config:
                    self.logger(f"缺少必要字段: {field}")
                    return False
                    
                if not isinstance(config[field], field_type):
                    self.logger(f"字段類型錯誤: {field} 應為 {field_type.__name__}")
                    return False
                    
            return True
            
        except Exception as e:
            self.logger(f"驗證配置時發生錯誤: {str(e)}")
            return False
            
    def get_nested_config(self, config: Dict, *keys: str, default: Any = None) -> Any:
        """
        獲取嵌套配置值
        
        Args:
            config: 配置字典
            keys: 配置鍵路徑
            default: 默認值
            
        Returns:
            配置值
        """
        try:
            value = config
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
            
    def merge_configs(self, base_config: Dict, override_config: Dict) -> Dict:
        """
        合併兩個配置字典
        
        Args:
            base_config: 基礎配置
            override_config: 覆蓋配置
            
        Returns:
            合併後的配置
        """
        result = base_config.copy()
        
        for key, value in override_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
                
        return result
        
    def create_default_config(self, config_path: str, template: Dict) -> bool:
        """
        創建默認配置文件
        
        Args:
            config_path: 配置文件路徑
            template: 配置模板
            
        Returns:
            是否成功
        """
        try:
            if os.path.exists(config_path):
                self.logger(f"配置文件已存在: {config_path}")
                return False
                
            return self.save_config(template, config_path)
            
        except Exception as e:
            self.logger(f"創建默認配置時發生錯誤: {str(e)}")
            return False 
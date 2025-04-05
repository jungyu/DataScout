#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ConfigLoader 模組
負責載入、合併和驗證配置文件
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from jsonschema import validate, ValidationError

class ConfigLoader:
    """
    配置載入器類，處理配置文件的載入、驗證和合併
    """
    
    def __init__(self, logger=None):
        """
        初始化配置載入器
        
        Args:
            logger: 日誌記錄器，如果為None則創建新的
        """
        self.logger = logger or logging.getLogger(__name__)
        self.schema_cache = {}  # 用於緩存已加載的schema
        
    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        """
        載入配置文件
        
        Args:
            config_path: 配置文件路徑
            
        Returns:
            配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: 配置文件格式不正確
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"配置文件格式不正確: {str(e)}", e.doc, e.pos)
    
    @staticmethod
    def load_template(template_path: str) -> Dict[str, Any]:
        """
        載入爬蟲模板文件
        
        Args:
            template_path: 模板文件路徑
            
        Returns:
            模板字典
            
        Raises:
            FileNotFoundError: 模板文件不存在
            json.JSONDecodeError: 模板文件格式不正確
        """
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = json.load(f)
            return template
        except FileNotFoundError:
            raise FileNotFoundError(f"模板文件不存在: {template_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"模板文件格式不正確: {str(e)}", e.doc, e.pos)
    
    def validate_config(self, config: Dict[str, Any], schema_path: str) -> bool:
        """
        驗證配置是否符合schema
        
        Args:
            config: 配置字典
            schema_path: schema文件路徑
            
        Returns:
            驗證是否通過
        """
        # 從緩存加載或讀取schema
        if schema_path in self.schema_cache:
            schema = self.schema_cache[schema_path]
        else:
            try:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                self.schema_cache[schema_path] = schema
            except (FileNotFoundError, json.JSONDecodeError) as e:
                self.logger.error(f"加載schema失敗: {str(e)}")
                return False
        
        # 驗證配置
        try:
            validate(instance=config, schema=schema)
            return True
        except ValidationError as e:
            self.logger.error(f"配置驗證失敗: {str(e)}")
            return False
    
    def merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        合併兩個配置，override_config覆蓋base_config的相同鍵
        
        Args:
            base_config: 基礎配置
            override_config: 覆蓋配置
            
        Returns:
            合併後的配置
        """
        merged = base_config.copy()
        
        # 遞迴合併字典
        def _merge_dict(d1, d2):
            for k, v2 in d2.items():
                if k in d1 and isinstance(d1[k], dict) and isinstance(v2, dict):
                    _merge_dict(d1[k], v2)
                else:
                    d1[k] = v2
        
        _merge_dict(merged, override_config)
        return merged
    
    def load_and_validate(self, config_path: str, schema_path: str = None) -> Dict[str, Any]:
        """
        載入並驗證配置
        
        Args:
            config_path: 配置文件路徑
            schema_path: schema文件路徑，如果不提供則跳過驗證
            
        Returns:
            驗證後的配置
            
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: 配置文件格式不正確
            ValidationError: 配置不符合schema
        """
        # 載入配置
        config = self.load_config(config_path)
        
        # 驗證配置
        if schema_path and not self.validate_config(config, schema_path):
            self.logger.warning(f"配置 {config_path} 不符合schema，但仍然繼續")
        
        return config
    
    def load_with_override(self, base_path: str, override_path: str = None, schema_path: str = None) -> Dict[str, Any]:
        """
        載入基礎配置並可選覆蓋
        
        Args:
            base_path: 基礎配置文件路徑
            override_path: 覆蓋配置文件路徑，如果不提供則僅使用基礎配置
            schema_path: schema文件路徑，如果不提供則跳過驗證
            
        Returns:
            最終配置
        """
        # 載入基礎配置
        base_config = self.load_config(base_path)
        
        # 如果提供覆蓋配置，則載入並合併
        if override_path and os.path.exists(override_path):
            try:
                override_config = self.load_config(override_path)
                base_config = self.merge_configs(base_config, override_config)
            except Exception as e:
                self.logger.error(f"合併覆蓋配置 {override_path} 失敗: {str(e)}")
        
        # 驗證最終配置
        if schema_path and not self.validate_config(base_config, schema_path):
            self.logger.warning(f"最終配置不符合schema，但仍然繼續")
        
        return base_config
    
    def save_config(self, config: Dict[str, Any], config_path: str) -> bool:
        """
        保存配置到文件
        
        Args:
            config: 配置字典
            config_path: 保存路徑
            
        Returns:
            是否保存成功
        """
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
            
            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"保存配置失敗: {str(e)}")
            return False
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理提取器模組

提供提取器配置管理功能，包括：
1. 配置加載和保存
2. 配置驗證
3. 配置版本控制
4. 配置模板管理
"""

from typing import Dict, List, Optional, Union, Any, Set, Callable, Type
from dataclasses import dataclass, asdict
import json
import yaml
import os
import time
import hashlib
import logging
from datetime import datetime
from pathlib import Path
import jsonschema
import copy
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from ..core.base import BaseExtractor
from ..core.error import handle_extractor_error, ExtractorError

@dataclass
class ConfigSchema:
    """配置模式"""
    type: str = "object"
    properties: Dict[str, Any] = None
    required: List[str] = None
    additional_properties: bool = False
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.required is None:
            self.required = []
            
@dataclass
class ConfigTemplate:
    """配置模板"""
    name: str
    description: str
    schema: ConfigSchema
    default_values: Dict[str, Any]
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "name": self.name,
            "description": self.description,
            "schema": asdict(self.schema),
            "default_values": self.default_values,
            "version": self.version
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfigTemplate":
        """從字典創建
        
        Args:
            data: 字典數據
            
        Returns:
            ConfigTemplate: 配置模板
        """
        schema = ConfigSchema(**data["schema"])
        return cls(
            name=data["name"],
            description=data["description"],
            schema=schema,
            default_values=data["default_values"],
            version=data["version"]
        )

class ConfigExtractor(BaseExtractor):
    """配置管理提取器類別"""
    
    def __init__(self, driver: Any, config_dir: str = "configs"):
        """初始化配置管理提取器
        
        Args:
            driver: WebDriver 實例
            config_dir: 配置目錄
        """
        super().__init__(driver)
        self.config_dir = config_dir
        self._logger = logging.getLogger(__name__)
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._templates: Dict[str, ConfigTemplate] = {}
        self._versions: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = threading.Lock()
        self._observer = None
        
        # 創建配置目錄
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        # 啟動文件監控
        self._start_file_monitor()
        
    def _start_file_monitor(self):
        """啟動文件監控"""
        class ConfigFileHandler(FileSystemEventHandler):
            def __init__(self, extractor):
                self.extractor = extractor
                
            def on_modified(self, event):
                if event.is_directory:
                    return
                if event.src_path.endswith((".json", ".yaml", ".yml")):
                    self.extractor._load_config_file(event.src_path)
                    
        self._observer = Observer()
        self._observer.schedule(
            ConfigFileHandler(self),
            self.config_dir,
            recursive=True
        )
        self._observer.start()
        
    @handle_extractor_error()
    def load_config(self, name: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """加載配置
        
        Args:
            name: 配置名稱
            file_path: 配置文件路徑
            
        Returns:
            Dict[str, Any]: 配置數據
        """
        if file_path is None:
            file_path = os.path.join(self.config_dir, f"{name}.json")
            
        if not os.path.exists(file_path):
            raise ExtractorError(f"配置文件不存在: {file_path}")
            
        return self._load_config_file(file_path)
        
    def _load_config_file(self, file_path: str) -> Dict[str, Any]:
        """加載配置文件
        
        Args:
            file_path: 配置文件路徑
            
        Returns:
            Dict[str, Any]: 配置數據
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.endswith(".json"):
                    config = json.load(f)
                else:
                    config = yaml.safe_load(f)
                    
            name = os.path.splitext(os.path.basename(file_path))[0]
            
            # 驗證配置
            if name in self._templates:
                self._validate_config(config, self._templates[name].schema)
                
            # 保存配置
            with self._lock:
                self._configs[name] = config
                self._add_version(name, config)
                
            return config
            
        except Exception as e:
            self._logger.error(f"加載配置文件失敗: {file_path} - {str(e)}")
            raise
            
    @handle_extractor_error()
    def save_config(self, name: str, config: Dict[str, Any], file_path: Optional[str] = None) -> bool:
        """保存配置
        
        Args:
            name: 配置名稱
            config: 配置數據
            file_path: 配置文件路徑
            
        Returns:
            bool: 是否成功
        """
        if file_path is None:
            file_path = os.path.join(self.config_dir, f"{name}.json")
            
        try:
            # 驗證配置
            if name in self._templates:
                self._validate_config(config, self._templates[name].schema)
                
            # 保存文件
            with open(file_path, "w", encoding="utf-8") as f:
                if file_path.endswith(".json"):
                    json.dump(config, f, indent=2)
                else:
                    yaml.dump(config, f)
                    
            # 更新配置
            with self._lock:
                self._configs[name] = config
                self._add_version(name, config)
                
            return True
            
        except Exception as e:
            self._logger.error(f"保存配置文件失敗: {file_path} - {str(e)}")
            return False
            
    @handle_extractor_error()
    def _validate_config(self, config: Dict[str, Any], schema: ConfigSchema) -> bool:
        """驗證配置
        
        Args:
            config: 配置數據
            schema: 配置模式
            
        Returns:
            bool: 是否有效
        """
        try:
            jsonschema.validate(config, asdict(schema))
            return True
        except jsonschema.exceptions.ValidationError as e:
            self._logger.error(f"配置驗證失敗: {str(e)}")
            return False
            
    @handle_extractor_error()
    def _add_version(self, name: str, config: Dict[str, Any]):
        """添加配置版本
        
        Args:
            name: 配置名稱
            config: 配置數據
        """
        if name not in self._versions:
            self._versions[name] = []
            
        version = {
            "timestamp": time.time(),
            "config": copy.deepcopy(config),
            "hash": self._calculate_hash(config)
        }
        
        self._versions[name].append(version)
        
    def _calculate_hash(self, config: Dict[str, Any]) -> str:
        """計算配置哈希值
        
        Args:
            config: 配置數據
            
        Returns:
            str: 哈希值
        """
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
        
    @handle_extractor_error()
    def get_config(self, name: str) -> Optional[Dict[str, Any]]:
        """獲取配置
        
        Args:
            name: 配置名稱
            
        Returns:
            Optional[Dict[str, Any]]: 配置數據
        """
        with self._lock:
            return self._configs.get(name)
            
    @handle_extractor_error()
    def get_config_versions(self, name: str) -> List[Dict[str, Any]]:
        """獲取配置版本歷史
        
        Args:
            name: 配置名稱
            
        Returns:
            List[Dict[str, Any]]: 版本歷史
        """
        with self._lock:
            return self._versions.get(name, [])
            
    @handle_extractor_error()
    def restore_config(self, name: str, version_index: int) -> bool:
        """恢復配置版本
        
        Args:
            name: 配置名稱
            version_index: 版本索引
            
        Returns:
            bool: 是否成功
        """
        with self._lock:
            if name not in self._versions:
                return False
                
            versions = self._versions[name]
            if version_index < 0 or version_index >= len(versions):
                return False
                
            version = versions[version_index]
            return self.save_config(name, version["config"])
            
    @handle_extractor_error()
    def register_template(self, template: ConfigTemplate) -> bool:
        """註冊配置模板
        
        Args:
            template: 配置模板
            
        Returns:
            bool: 是否成功
        """
        try:
            # 保存模板
            template_path = os.path.join(self.config_dir, "templates", f"{template.name}.json")
            os.makedirs(os.path.dirname(template_path), exist_ok=True)
            
            with open(template_path, "w", encoding="utf-8") as f:
                json.dump(template.to_dict(), f, indent=2)
                
            # 更新模板
            with self._lock:
                self._templates[template.name] = template
                
            return True
            
        except Exception as e:
            self._logger.error(f"註冊配置模板失敗: {str(e)}")
            return False
            
    @handle_extractor_error()
    def get_template(self, name: str) -> Optional[ConfigTemplate]:
        """獲取配置模板
        
        Args:
            name: 模板名稱
            
        Returns:
            Optional[ConfigTemplate]: 配置模板
        """
        with self._lock:
            return self._templates.get(name)
            
    @handle_extractor_error()
    def create_config_from_template(self, template_name: str, name: str, values: Optional[Dict[str, Any]] = None) -> bool:
        """從模板創建配置
        
        Args:
            template_name: 模板名稱
            name: 配置名稱
            values: 配置值
            
        Returns:
            bool: 是否成功
        """
        template = self.get_template(template_name)
        if template is None:
            return False
            
        config = template.default_values.copy()
        if values:
            config.update(values)
            
        return self.save_config(name, config)
        
    def cleanup(self):
        """清理資源"""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            
    def __del__(self):
        """析構函數"""
        self.cleanup() 
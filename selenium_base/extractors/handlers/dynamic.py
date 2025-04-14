#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
動態提取器模組

提供提取器動態加載功能，包括：
1. 提取器動態加載
2. 提取器熱重載
3. 提取器版本管理
4. 提取器依賴管理
"""

from typing import Dict, List, Optional, Union, Any, Set, Callable, Type
from dataclasses import dataclass
import importlib
import importlib.util
import inspect
import os
import sys
import json
import time
from datetime import datetime
import threading
import logging
from pathlib import Path

from ..core.base import BaseExtractor
from ..core.error import handle_extractor_error, ExtractorError

@dataclass
class DynamicExtractorConfig:
    """動態提取器配置"""
    # 提取器目錄設置
    extractor_dir: str = "extractors"
    plugin_dir: str = "plugins"
    temp_dir: str = "temp"
    
    # 加載設置
    auto_reload: bool = True
    reload_interval: int = 300  # 秒
    lazy_load: bool = True
    load_timeout: float = 30.0
    
    # 版本管理
    version_check: bool = True
    version_file: str = "versions.json"
    min_version: str = "1.0.0"
    max_version: str = "2.0.0"
    
    # 依賴管理
    check_dependencies: bool = True
    dependency_file: str = "dependencies.json"
    install_missing: bool = True
    
    # 錯誤處理
    continue_on_error: bool = True
    error_threshold: int = 5
    error_callback: Optional[Callable[[Exception], None]] = None
    
    def __post_init__(self):
        # 創建必要的目錄
        for directory in [self.extractor_dir, self.plugin_dir, self.temp_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

class DynamicExtractor(BaseExtractor):
    """動態提取器類別"""
    
    def __init__(self, driver: Any, config: Optional[DynamicExtractorConfig] = None):
        """初始化動態提取器
        
        Args:
            driver: WebDriver 實例
            config: 提取器配置
        """
        super().__init__(driver)
        self.config = config or DynamicExtractorConfig()
        self._extractors: Dict[str, Type[BaseExtractor]] = {}
        self._loaded_modules: Dict[str, Any] = {}
        self._extractor_versions: Dict[str, str] = {}
        self._last_reload = time.time()
        self._reload_lock = threading.Lock()
        self._logger = logging.getLogger(__name__)
        
    @handle_extractor_error()
    def load_extractor(self, name: str, module_path: Optional[str] = None) -> Optional[Type[BaseExtractor]]:
        """加載提取器
        
        Args:
            name: 提取器名稱
            module_path: 模組路徑
            
        Returns:
            Optional[Type[BaseExtractor]]: 提取器類別
        """
        try:
            # 檢查是否已加載
            if name in self._extractors:
                return self._extractors[name]
                
            # 獲取模組路徑
            if module_path is None:
                module_path = os.path.join(self.config.extractor_dir, f"{name}.py")
                
            if not os.path.exists(module_path):
                self._logger.warning(f"提取器模組不存在: {module_path}")
                return None
                
            # 加載模組
            spec = importlib.util.spec_from_file_location(name, module_path)
            if spec is None or spec.loader is None:
                self._logger.error(f"無法加載提取器模組: {module_path}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            
            # 查找提取器類別
            extractor_class = None
            for item in dir(module):
                obj = getattr(module, item)
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseExtractor) and 
                    obj != BaseExtractor):
                    extractor_class = obj
                    break
                    
            if extractor_class is None:
                self._logger.error(f"未找到提取器類別: {name}")
                return None
                
            # 檢查版本
            if self.config.version_check:
                version = getattr(extractor_class, "VERSION", "1.0.0")
                if not self._check_version(version):
                    self._logger.error(f"提取器版本不兼容: {name} {version}")
                    return None
                    
            # 檢查依賴
            if self.config.check_dependencies:
                dependencies = getattr(extractor_class, "DEPENDENCIES", {})
                if not self._check_dependencies(dependencies):
                    self._logger.error(f"提取器依賴不滿足: {name}")
                    return None
                    
            # 保存提取器
            self._extractors[name] = extractor_class
            self._loaded_modules[name] = module
            self._extractor_versions[name] = getattr(extractor_class, "VERSION", "1.0.0")
            
            return extractor_class
            
        except Exception as e:
            self._logger.error(f"加載提取器失敗: {name} - {str(e)}")
            if self.config.error_callback:
                self.config.error_callback(e)
            return None
            
    @handle_extractor_error()
    def unload_extractor(self, name: str) -> bool:
        """卸載提取器
        
        Args:
            name: 提取器名稱
            
        Returns:
            bool: 是否成功卸載
        """
        try:
            if name in self._extractors:
                del self._extractors[name]
            if name in self._loaded_modules:
                del self._loaded_modules[name]
            if name in self._extractor_versions:
                del self._extractor_versions[name]
            if name in sys.modules:
                del sys.modules[name]
            return True
        except Exception as e:
            self._logger.error(f"卸載提取器失敗: {name} - {str(e)}")
            return False
            
    @handle_extractor_error()
    def reload_extractor(self, name: str) -> Optional[Type[BaseExtractor]]:
        """重新加載提取器
        
        Args:
            name: 提取器名稱
            
        Returns:
            Optional[Type[BaseExtractor]]: 提取器類別
        """
        with self._reload_lock:
            self.unload_extractor(name)
            return self.load_extractor(name)
            
    @handle_extractor_error()
    def reload_all(self) -> Dict[str, bool]:
        """重新加載所有提取器
        
        Returns:
            Dict[str, bool]: 重載結果
        """
        results = {}
        for name in list(self._extractors.keys()):
            results[name] = self.reload_extractor(name) is not None
        return results
        
    @handle_extractor_error()
    def _check_version(self, version: str) -> bool:
        """檢查版本兼容性
        
        Args:
            version: 版本號
            
        Returns:
            bool: 是否兼容
        """
        try:
            from packaging import version as pkg_version
            current = pkg_version.parse(version)
            min_version = pkg_version.parse(self.config.min_version)
            max_version = pkg_version.parse(self.config.max_version)
            return min_version <= current <= max_version
        except Exception:
            return True
            
    @handle_extractor_error()
    def _check_dependencies(self, dependencies: Dict[str, str]) -> bool:
        """檢查依賴是否滿足
        
        Args:
            dependencies: 依賴字典
            
        Returns:
            bool: 是否滿足
        """
        try:
            import pkg_resources
            for package, version in dependencies.items():
                try:
                    pkg_resources.require(f"{package}{version}")
                except pkg_resources.VersionConflict:
                    return False
                except pkg_resources.DistributionNotFound:
                    if self.config.install_missing:
                        import subprocess
                        subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package}{version}"])
                    else:
                        return False
            return True
        except Exception:
            return True
            
    @handle_extractor_error()
    def get_extractor(self, name: str) -> Optional[Type[BaseExtractor]]:
        """獲取提取器
        
        Args:
            name: 提取器名稱
            
        Returns:
            Optional[Type[BaseExtractor]]: 提取器類別
        """
        # 檢查是否需要重新加載
        if (self.config.auto_reload and 
            time.time() - self._last_reload >= self.config.reload_interval):
            self.reload_all()
            self._last_reload = time.time()
            
        # 懶加載
        if self.config.lazy_load and name not in self._extractors:
            return self.load_extractor(name)
            
        return self._extractors.get(name)
        
    @handle_extractor_error()
    def get_extractor_info(self, name: str) -> Dict[str, Any]:
        """獲取提取器信息
        
        Args:
            name: 提取器名稱
            
        Returns:
            Dict[str, Any]: 提取器信息
        """
        extractor_class = self.get_extractor(name)
        if extractor_class is None:
            return {}
            
        return {
            "name": name,
            "version": getattr(extractor_class, "VERSION", "1.0.0"),
            "description": getattr(extractor_class, "__doc__", ""),
            "dependencies": getattr(extractor_class, "DEPENDENCIES", {}),
            "author": getattr(extractor_class, "AUTHOR", ""),
            "created_at": getattr(extractor_class, "CREATED_AT", ""),
            "updated_at": getattr(extractor_class, "UPDATED_AT", ""),
            "methods": [
                name for name, _ in inspect.getmembers(
                    extractor_class,
                    predicate=inspect.isfunction
                )
            ]
        }
        
    @handle_extractor_error()
    def list_extractors(self) -> List[Dict[str, Any]]:
        """列出所有提取器
        
        Returns:
            List[Dict[str, Any]]: 提取器列表
        """
        extractors = []
        for name in self._extractors:
            info = self.get_extractor_info(name)
            if info:
                extractors.append(info)
        return extractors
        
    @handle_extractor_error()
    def extract(self, name: str, *args, **kwargs) -> Any:
        """執行提取操作
        
        Args:
            name: 提取器名稱
            *args: 位置參數
            **kwargs: 關鍵字參數
            
        Returns:
            Any: 提取結果
        """
        extractor_class = self.get_extractor(name)
        if extractor_class is None:
            raise ExtractorError(f"提取器不存在: {name}")
            
        try:
            extractor = extractor_class(self.driver)
            return extractor.extract(*args, **kwargs)
        except Exception as e:
            self._logger.error(f"提取失敗: {name} - {str(e)}")
            if self.config.error_callback:
                self.config.error_callback(e)
            if not self.config.continue_on_error:
                raise
            return None 
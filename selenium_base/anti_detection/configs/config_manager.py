"""
反檢測配置管理器模組

此模組提供反檢測配置的管理功能，包括：
- 加載多個配置文件
- 切換不同配置
- 備份和恢復配置
- 配置版本控制
- 配置性能監控
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

from .anti_detection_config import AntiDetectionConfig
from ..exceptions import ConfigError


class ConfigManager:
    """反檢測配置管理器
    
    用於管理多個反檢測配置文件，提供配置的加載、切換、備份等功能。
    
    Attributes:
        config_dir (str): 配置文件目錄
        current_config (AntiDetectionConfig): 當前使用的配置
        configs (Dict[str, AntiDetectionConfig]): 所有配置的字典
        backup_dir (str): 備份目錄
        version_control_dir (str): 版本控制目錄
    """
    
    def __init__(
        self,
        config_dir: str = "configs",
        backup_dir: str = "backups",
        version_control_dir: str = "versions",
        logger: Optional[Any] = None,
    ):
        """初始化配置管理器
        
        Args:
            config_dir: 配置文件目錄
            backup_dir: 備份目錄
            version_control_dir: 版本控制目錄
            logger: 日誌記錄器
        """
        self.config_dir = config_dir
        self.backup_dir = backup_dir
        self.version_control_dir = version_control_dir
        self.logger = logger
        
        self.current_config = None
        self.configs = {}
        
        self._ensure_directories()
        self._load_configs()
    
    def _ensure_directories(self) -> None:
        """確保必要的目錄存在"""
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.version_control_dir, exist_ok=True)
    
    def _load_configs(self) -> None:
        """加載所有配置文件"""
        try:
            for file_name in os.listdir(self.config_dir):
                if file_name.endswith(".json"):
                    config_path = os.path.join(self.config_dir, file_name)
                    config = AntiDetectionConfig.from_file(config_path)
                    self.configs[config.id] = config
            
            if self.configs:
                self.current_config = list(self.configs.values())[0]
                if self.logger:
                    self.logger.info(f"已加載 {len(self.configs)} 個配置文件")
            else:
                if self.logger:
                    self.logger.warning("未找到任何配置文件")
        except Exception as e:
            if self.logger:
                self.logger.error(f"加載配置文件失敗: {e}")
            raise ConfigError(f"加載配置文件失敗: {e}")
    
    def get_config(self, config_id: str) -> Optional[AntiDetectionConfig]:
        """獲取指定ID的配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            Optional[AntiDetectionConfig]: 配置對象，如果不存在則返回None
        """
        return self.configs.get(config_id)
    
    def get_current_config(self) -> Optional[AntiDetectionConfig]:
        """獲取當前使用的配置
        
        Returns:
            Optional[AntiDetectionConfig]: 當前配置對象
        """
        return self.current_config
    
    def switch_config(self, config_id: str) -> bool:
        """切換到指定ID的配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            bool: 是否切換成功
        """
        if config_id in self.configs:
            self.current_config = self.configs[config_id]
            if self.logger:
                self.logger.info(f"已切換到配置: {config_id}")
            return True
        else:
            if self.logger:
                self.logger.warning(f"配置不存在: {config_id}")
            return False
    
    def add_config(self, config: AntiDetectionConfig) -> bool:
        """添加新配置
        
        Args:
            config: 配置對象
            
        Returns:
            bool: 是否添加成功
        """
        try:
            if config.id in self.configs:
                if self.logger:
                    self.logger.warning(f"配置已存在: {config.id}")
                return False
            
            self.configs[config.id] = config
            config_path = os.path.join(self.config_dir, f"{config.id}.json")
            config.save_to_file(config_path)
            
            if self.logger:
                self.logger.info(f"已添加配置: {config.id}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"添加配置失敗: {e}")
            return False
    
    def update_config(self, config_id: str, data: Dict[str, Any]) -> bool:
        """更新指定ID的配置
        
        Args:
            config_id: 配置ID
            data: 更新數據
            
        Returns:
            bool: 是否更新成功
        """
        try:
            if config_id not in self.configs:
                if self.logger:
                    self.logger.warning(f"配置不存在: {config_id}")
                return False
            
            config = self.configs[config_id]
            config.update(data)
            
            config_path = os.path.join(self.config_dir, f"{config_id}.json")
            config.save_to_file(config_path)
            
            if self.logger:
                self.logger.info(f"已更新配置: {config_id}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"更新配置失敗: {e}")
            return False
    
    def delete_config(self, config_id: str) -> bool:
        """刪除指定ID的配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            bool: 是否刪除成功
        """
        try:
            if config_id not in self.configs:
                if self.logger:
                    self.logger.warning(f"配置不存在: {config_id}")
                return False
            
            config_path = os.path.join(self.config_dir, f"{config_id}.json")
            os.remove(config_path)
            
            del self.configs[config_id]
            
            if self.current_config and self.current_config.id == config_id:
                self.current_config = list(self.configs.values())[0] if self.configs else None
            
            if self.logger:
                self.logger.info(f"已刪除配置: {config_id}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"刪除配置失敗: {e}")
            return False
    
    def backup_config(self, config_id: str) -> bool:
        """備份指定ID的配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            bool: 是否備份成功
        """
        try:
            if config_id not in self.configs:
                if self.logger:
                    self.logger.warning(f"配置不存在: {config_id}")
                return False
            
            config = self.configs[config_id]
            backup_path = os.path.join(
                self.backup_dir,
                f"{config_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            config.save_to_file(backup_path)
            
            if self.logger:
                self.logger.info(f"已備份配置: {config_id}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"備份配置失敗: {e}")
            return False
    
    def restore_config(self, backup_file: str) -> bool:
        """從備份文件恢復配置
        
        Args:
            backup_file: 備份文件名
            
        Returns:
            bool: 是否恢復成功
        """
        try:
            backup_path = os.path.join(self.backup_dir, backup_file)
            if not os.path.exists(backup_path):
                if self.logger:
                    self.logger.warning(f"備份文件不存在: {backup_file}")
                return False
            
            config = AntiDetectionConfig.from_file(backup_path)
            self.configs[config.id] = config
            
            config_path = os.path.join(self.config_dir, f"{config.id}.json")
            config.save_to_file(config_path)
            
            if self.logger:
                self.logger.info(f"已恢復配置: {config.id}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"恢復配置失敗: {e}")
            return False
    
    def create_version(self, config_id: str, version: str) -> bool:
        """創建配置版本
        
        Args:
            config_id: 配置ID
            version: 版本號
            
        Returns:
            bool: 是否創建成功
        """
        try:
            if config_id not in self.configs:
                if self.logger:
                    self.logger.warning(f"配置不存在: {config_id}")
                return False
            
            config = self.configs[config_id]
            version_path = os.path.join(
                self.version_control_dir,
                f"{config_id}_{version}.json"
            )
            
            config.version = version
            config.save_to_file(version_path)
            
            if self.logger:
                self.logger.info(f"已創建配置版本: {config_id} {version}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"創建配置版本失敗: {e}")
            return False
    
    def switch_version(self, config_id: str, version: str) -> bool:
        """切換到指定版本
        
        Args:
            config_id: 配置ID
            version: 版本號
            
        Returns:
            bool: 是否切換成功
        """
        try:
            version_path = os.path.join(
                self.version_control_dir,
                f"{config_id}_{version}.json"
            )
            
            if not os.path.exists(version_path):
                if self.logger:
                    self.logger.warning(f"版本不存在: {config_id} {version}")
                return False
            
            config = AntiDetectionConfig.from_file(version_path)
            self.configs[config_id] = config
            
            config_path = os.path.join(self.config_dir, f"{config_id}.json")
            config.save_to_file(config_path)
            
            if self.current_config and self.current_config.id == config_id:
                self.current_config = config
            
            if self.logger:
                self.logger.info(f"已切換到版本: {config_id} {version}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"切換版本失敗: {e}")
            return False
    
    def get_versions(self, config_id: str) -> List[str]:
        """獲取配置的所有版本
        
        Args:
            config_id: 配置ID
            
        Returns:
            List[str]: 版本號列表
        """
        versions = []
        for file_name in os.listdir(self.version_control_dir):
            if file_name.startswith(f"{config_id}_") and file_name.endswith(".json"):
                version = file_name[len(f"{config_id}_"):-5]
                versions.append(version)
        return sorted(versions)
    
    def get_config_metrics(self, config_id: str) -> Dict[str, Any]:
        """獲取配置的性能指標
        
        Args:
            config_id: 配置ID
            
        Returns:
            Dict[str, Any]: 性能指標
        """
        if config_id in self.configs:
            return self.configs[config_id].get_metrics()
        return {}
    
    def update_config_metrics(self, config_id: str, metrics: Dict[str, Any]) -> None:
        """更新配置的性能指標
        
        Args:
            config_id: 配置ID
            metrics: 性能指標
        """
        if config_id in self.configs:
            self.configs[config_id].update_metrics(metrics)
    
    def clear_config_metrics(self, config_id: str) -> None:
        """清除配置的性能指標
        
        Args:
            config_id: 配置ID
        """
        if config_id in self.configs:
            self.configs[config_id].clear_metrics()
    
    def get_config_metadata(self, config_id: str) -> Dict[str, Any]:
        """獲取配置的元數據
        
        Args:
            config_id: 配置ID
            
        Returns:
            Dict[str, Any]: 元數據
        """
        if config_id in self.configs:
            return self.configs[config_id].get_metadata()
        return {}
    
    def update_config_metadata(self, config_id: str, metadata: Dict[str, Any]) -> None:
        """更新配置的元數據
        
        Args:
            config_id: 配置ID
            metadata: 元數據
        """
        if config_id in self.configs:
            self.configs[config_id].update_metadata(metadata)
    
    def clear_config_metadata(self, config_id: str) -> None:
        """清除配置的元數據
        
        Args:
            config_id: 配置ID
        """
        if config_id in self.configs:
            self.configs[config_id].clear_metadata() 
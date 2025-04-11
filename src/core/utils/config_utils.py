#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置工具模組

提供配置文件的讀取、解析和驗證功能。
支持JSON格式的配置文件，提供配置值的獲取和設置功能。
支持配置文件的合併和默認配置的創建。
支持配置文件的備份、恢復、版本控制和加密。
"""

import os
import json
import shutil
import logging
import hashlib
import difflib
from datetime import datetime
from typing import Dict, Any, Optional, List, Union, Type, Tuple
from cryptography.fernet import Fernet

class ConfigUtils:
    """配置工具類，提供配置文件的讀取和管理功能"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化配置工具類
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
        self._encryption_key = None
        self._version_history = {}
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        從文件加載配置
        
        Args:
            config_path: 配置文件路徑
            
        Returns:
            配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: 配置文件格式錯誤
        """
        try:
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"配置文件不存在: {config_path}")
                
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 更新版本歷史
            self._update_version_history(config_path, config)
                
            self.logger.info(f"已加載配置文件: {config_path}")
            return config
            
        except json.JSONDecodeError as e:
            self.logger.error(f"配置文件格式錯誤: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"加載配置文件失敗: {str(e)}")
            raise
            
    def save_config(self, config: Dict[str, Any], config_path: str) -> bool:
        """
        保存配置到文件
        
        Args:
            config: 配置字典
            config_path: 配置文件路徑
            
        Returns:
            是否保存成功
        """
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
                
            # 更新版本歷史
            self._update_version_history(config_path, config)
                
            self.logger.info(f"配置已保存到: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存配置文件失敗: {str(e)}")
            return False
            
    def backup_config(self, config_path: str, backup_dir: Optional[str] = None) -> Optional[str]:
        """
        備份配置文件
        
        Args:
            config_path: 配置文件路徑
            backup_dir: 備份目錄，如果為None則使用默認目錄
            
        Returns:
            備份文件路徑，如果失敗則返回None
        """
        try:
            if not os.path.exists(config_path):
                self.logger.error(f"配置文件不存在: {config_path}")
                return None
                
            # 生成備份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(config_path)
            backup_name = f"{os.path.splitext(filename)[0]}_{timestamp}.json"
            
            # 設置備份目錄
            if backup_dir is None:
                backup_dir = os.path.join(os.path.dirname(config_path), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # 複製文件
            backup_path = os.path.join(backup_dir, backup_name)
            shutil.copy2(config_path, backup_path)
            
            self.logger.info(f"配置文件已備份到: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"備份配置文件失敗: {str(e)}")
            return None
            
    def restore_config(self, backup_path: str, config_path: str) -> bool:
        """
        從備份恢復配置
        
        Args:
            backup_path: 備份文件路徑
            config_path: 目標配置文件路徑
            
        Returns:
            是否恢復成功
        """
        try:
            if not os.path.exists(backup_path):
                self.logger.error(f"備份文件不存在: {backup_path}")
                return False
                
            # 確保目標目錄存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # 複製備份文件
            shutil.copy2(backup_path, config_path)
            
            # 更新版本歷史
            with open(backup_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self._update_version_history(config_path, config)
            
            self.logger.info(f"已從備份恢復配置: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"恢復配置文件失敗: {str(e)}")
            return False
            
    def set_encryption_key(self, key: Optional[bytes] = None) -> None:
        """
        設置加密密鑰
        
        Args:
            key: 加密密鑰，如果為None則生成新密鑰
        """
        if key is None:
            key = Fernet.generate_key()
        self._encryption_key = key
        self.logger.info("已設置加密密鑰")
        
    def encrypt_config(self, config: Dict[str, Any]) -> bytes:
        """
        加密配置
        
        Args:
            config: 配置字典
            
        Returns:
            加密後的數據
            
        Raises:
            ValueError: 未設置加密密鑰
        """
        if self._encryption_key is None:
            raise ValueError("未設置加密密鑰")
            
        try:
            # 將配置轉換為JSON字符串
            config_str = json.dumps(config)
            
            # 加密
            f = Fernet(self._encryption_key)
            encrypted_data = f.encrypt(config_str.encode())
            
            return encrypted_data
            
        except Exception as e:
            self.logger.error(f"加密配置失敗: {str(e)}")
            raise
            
    def decrypt_config(self, encrypted_data: bytes) -> Dict[str, Any]:
        """
        解密配置
        
        Args:
            encrypted_data: 加密後的數據
            
        Returns:
            解密後的配置字典
            
        Raises:
            ValueError: 未設置加密密鑰
        """
        if self._encryption_key is None:
            raise ValueError("未設置加密密鑰")
            
        try:
            # 解密
            f = Fernet(self._encryption_key)
            decrypted_data = f.decrypt(encrypted_data)
            
            # 解析JSON
            config = json.loads(decrypted_data.decode())
            
            return config
            
        except Exception as e:
            self.logger.error(f"解密配置失敗: {str(e)}")
            raise
            
    def save_encrypted_config(self, config: Dict[str, Any], config_path: str) -> bool:
        """
        保存加密的配置
        
        Args:
            config: 配置字典
            config_path: 配置文件路徑
            
        Returns:
            是否保存成功
            
        Raises:
            ValueError: 未設置加密密鑰
        """
        if self._encryption_key is None:
            raise ValueError("未設置加密密鑰")
            
        try:
            # 加密配置
            encrypted_data = self.encrypt_config(config)
            
            # 確保目錄存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # 保存加密數據
            with open(config_path, 'wb') as f:
                f.write(encrypted_data)
                
            # 更新版本歷史
            self._update_version_history(config_path, config)
                
            self.logger.info(f"加密配置已保存到: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存加密配置失敗: {str(e)}")
            return False
            
    def load_encrypted_config(self, config_path: str) -> Optional[Dict[str, Any]]:
        """
        加載加密的配置
        
        Args:
            config_path: 配置文件路徑
            
        Returns:
            解密後的配置字典，如果失敗則返回None
            
        Raises:
            ValueError: 未設置加密密鑰
        """
        if self._encryption_key is None:
            raise ValueError("未設置加密密鑰")
            
        try:
            if not os.path.exists(config_path):
                self.logger.error(f"配置文件不存在: {config_path}")
                return None
                
            # 讀取加密數據
            with open(config_path, 'rb') as f:
                encrypted_data = f.read()
                
            # 解密配置
            config = self.decrypt_config(encrypted_data)
            
            # 更新版本歷史
            self._update_version_history(config_path, config)
                
            self.logger.info(f"已加載加密配置: {config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"加載加密配置失敗: {str(e)}")
            return None
            
    def get_config_value(self, config: Dict[str, Any], key: str, default: Any = None) -> Any:
        """
        獲取配置值
        
        Args:
            config: 配置字典
            key: 配置鍵
            default: 默認值
            
        Returns:
            配置值
        """
        return config.get(key, default)
        
    def set_config_value(self, config: Dict[str, Any], key: str, value: Any) -> None:
        """
        設置配置值
        
        Args:
            config: 配置字典
            key: 配置鍵
            value: 配置值
        """
        config[key] = value
        
    def validate_config(self, config: Dict[str, Any], required_keys: Union[List[str], Dict[str, Type]]) -> bool:
        """
        驗證配置
        
        Args:
            config: 配置字典
            required_keys: 必需的鍵列表或鍵類型字典
            
        Returns:
            是否有效
        """
        try:
            if isinstance(required_keys, list):
                # 檢查必需的鍵是否存在
                missing_keys = [key for key in required_keys if key not in config]
                if missing_keys:
                    self.logger.error(f"缺少必需的配置項: {missing_keys}")
                    return False
            else:
                # 檢查鍵的類型
                for key, expected_type in required_keys.items():
                    if key not in config:
                        self.logger.error(f"缺少必需的配置項: {key}")
                        return False
                    if not isinstance(config[key], expected_type):
                        self.logger.error(f"配置項類型錯誤: {key} 應為 {expected_type.__name__}")
                        return False
            return True
        except Exception as e:
            self.logger.error(f"驗證配置失敗: {str(e)}")
            return False
            
    def merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        合併配置
        
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
        
    def get_nested_config_value(self, config: Dict[str, Any], path: str, default: Any = None) -> Any:
        """
        獲取嵌套配置值
        
        Args:
            config: 配置字典
            path: 配置路徑，使用點號分隔
            default: 默認值
            
        Returns:
            配置值
        """
        try:
            current = config
            for key in path.split('.'):
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
            
    def set_nested_config_value(self, config: Dict[str, Any], path: str, value: Any) -> None:
        """
        設置嵌套配置值
        
        Args:
            config: 配置字典
            path: 配置路徑，使用點號分隔
            value: 配置值
        """
        keys = path.split('.')
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        
    def remove_config_value(self, config: Dict[str, Any], key: str) -> bool:
        """
        移除配置值
        
        Args:
            config: 配置字典
            key: 配置鍵
            
        Returns:
            是否移除成功
        """
        try:
            if key in config:
                del config[key]
                return True
            return False
        except Exception as e:
            self.logger.error(f"移除配置值失敗: {str(e)}")
            return False
            
    def get_config_section(self, config: Dict[str, Any], section: str) -> Dict[str, Any]:
        """
        獲取配置區段
        
        Args:
            config: 配置字典
            section: 區段名稱
            
        Returns:
            區段配置
        """
        return config.get(section, {})
        
    def update_config_section(self, config: Dict[str, Any], section: str, section_config: Dict[str, Any]) -> None:
        """
        更新配置區段
        
        Args:
            config: 配置字典
            section: 區段名稱
            section_config: 區段配置
        """
        config[section] = section_config
        
    def list_config_sections(self, config: Dict[str, Any]) -> List[str]:
        """
        列出配置區段
        
        Args:
            config: 配置字典
            
        Returns:
            區段名稱列表
        """
        return list(config.keys())
        
    def clear_config_section(self, config: Dict[str, Any], section: str) -> bool:
        """
        清空配置區段
        
        Args:
            config: 配置字典
            section: 區段名稱
            
        Returns:
            是否清空成功
        """
        try:
            if section in config:
                config[section] = {}
                return True
            return False
        except Exception as e:
            self.logger.error(f"清空配置區段失敗: {str(e)}")
            return False
            
    def create_default_config(self, config_path: str, template: Dict[str, Any]) -> bool:
        """
        創建默認配置
        
        Args:
            config_path: 配置文件路徑
            template: 配置模板
            
        Returns:
            是否創建成功
        """
        try:
            if os.path.exists(config_path):
                self.logger.warning(f"配置文件已存在: {config_path}")
                return False
                
            # 確保目錄存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=4, ensure_ascii=False)
                
            self.logger.info(f"已創建默認配置: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"創建默認配置失敗: {str(e)}")
            return False
            
    def _update_version_history(self, config_path: str, config: Dict[str, Any]) -> None:
        """
        更新版本歷史
        
        Args:
            config_path: 配置文件路徑
            config: 配置字典
        """
        if config_path not in self._version_history:
            self._version_history[config_path] = []
            
        # 計算配置的哈希值
        config_str = json.dumps(config, sort_keys=True)
        config_hash = hashlib.md5(config_str.encode()).hexdigest()
        
        # 添加版本記錄
        version = {
            'timestamp': datetime.now().isoformat(),
            'hash': config_hash,
            'config': config
        }
        
        self._version_history[config_path].append(version)
        
        # 保留最近的10個版本
        if len(self._version_history[config_path]) > 10:
            self._version_history[config_path] = self._version_history[config_path][-10:]
            
    def get_version_history(self, config_path: str) -> List[Dict[str, Any]]:
        """
        獲取版本歷史
        
        Args:
            config_path: 配置文件路徑
            
        Returns:
            版本歷史列表
        """
        return self._version_history.get(config_path, [])
        
    def compare_config_versions(self, config_path: str, version1: int, version2: int) -> Tuple[bool, str]:
        """
        比較配置版本
        
        Args:
            config_path: 配置文件路徑
            version1: 第一個版本索引
            version2: 第二個版本索引
            
        Returns:
            (是否有差異, 差異描述)
        """
        try:
            history = self._version_history.get(config_path, [])
            if not history or version1 >= len(history) or version2 >= len(history):
                return False, "版本不存在"
                
            v1 = history[version1]
            v2 = history[version2]
            
            if v1['hash'] == v2['hash']:
                return False, "配置相同"
                
            # 生成差異報告
            diff = difflib.unified_diff(
                json.dumps(v1['config'], indent=2, sort_keys=True).splitlines(),
                json.dumps(v2['config'], indent=2, sort_keys=True).splitlines(),
                fromfile=f"版本 {version1}",
                tofile=f"版本 {version2}"
            )
            
            return True, "\n".join(diff)
            
        except Exception as e:
            self.logger.error(f"比較配置版本失敗: {str(e)}")
            return False, f"比較失敗: {str(e)}"
            
    def rollback_config(self, config_path: str, version: int) -> bool:
        """
        回滾配置版本
        
        Args:
            config_path: 配置文件路徑
            version: 版本索引
            
        Returns:
            是否回滾成功
        """
        try:
            history = self._version_history.get(config_path, [])
            if not history or version >= len(history):
                self.logger.error("版本不存在")
                return False
                
            # 獲取指定版本的配置
            config = history[version]['config']
            
            # 保存配置
            return self.save_config(config, config_path)
            
        except Exception as e:
            self.logger.error(f"回滾配置版本失敗: {str(e)}")
            return False
            
    def validate_config_schema(self, config: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        驗證配置模式
        
        Args:
            config: 配置字典
            schema: 配置模式
            
        Returns:
            (是否有效, 錯誤列表)
        """
        errors = []
        
        def validate_value(value: Any, schema_value: Any, path: str = "") -> None:
            if isinstance(schema_value, dict):
                if not isinstance(value, dict):
                    errors.append(f"{path} 應為字典")
                    return
                    
                for key, sub_schema in schema_value.items():
                    if key not in value:
                        errors.append(f"{path}.{key} 不存在")
                    else:
                        validate_value(value[key], sub_schema, f"{path}.{key}")
                        
            elif isinstance(schema_value, list):
                if not isinstance(value, list):
                    errors.append(f"{path} 應為列表")
                    return
                    
                if schema_value and isinstance(schema_value[0], (dict, list)):
                    for i, item in enumerate(value):
                        validate_value(item, schema_value[0], f"{path}[{i}]")
                        
            elif isinstance(schema_value, type):
                if not isinstance(value, schema_value):
                    errors.append(f"{path} 應為 {schema_value.__name__}")
                    
        validate_value(config, schema)
        return len(errors) == 0, errors
        
    def create_config_template(self, config: Dict[str, Any], template_path: str) -> bool:
        """
        創建配置模板
        
        Args:
            config: 配置字典
            template_path: 模板文件路徑
            
        Returns:
            是否創建成功
        """
        try:
            # 創建模板
            template = {}
            
            def create_template(value: Any) -> Any:
                if isinstance(value, dict):
                    return {k: create_template(v) for k, v in value.items()}
                elif isinstance(value, list):
                    return [create_template(value[0])] if value else []
                else:
                    return type(value)()
                    
            template = create_template(config)
            
            # 保存模板
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=4, ensure_ascii=False)
                
            self.logger.info(f"已創建配置模板: {template_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"創建配置模板失敗: {str(e)}")
            return False
            
    def apply_config_template(self, template: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        應用配置模板
        
        Args:
            template: 配置模板
            config: 配置字典
            
        Returns:
            應用模板後的配置
        """
        result = template.copy()
        
        def apply_template(template_value: Any, config_value: Any) -> Any:
            if isinstance(template_value, dict):
                if not isinstance(config_value, dict):
                    return template_value
                    
                result = template_value.copy()
                for key, value in config_value.items():
                    if key in template_value:
                        result[key] = apply_template(template_value[key], value)
                    else:
                        result[key] = value
                return result
                
            elif isinstance(template_value, list):
                if not isinstance(config_value, list):
                    return template_value
                    
                if template_value and isinstance(template_value[0], (dict, list)):
                    return [apply_template(template_value[0], item) for item in config_value]
                return config_value
                
            return config_value
            
        return apply_template(template, config) 
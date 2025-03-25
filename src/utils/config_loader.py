#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional
import base64

from .logger import setup_logger


class ConfigLoader:
    """
    配置載入工具，支持從JSON或YAML文件載入配置，
    提供敏感信息的加密/解密功能，以及配置合併和驗證功能。
    """
    
    logger = setup_logger(__name__)
    
    @classmethod
    def load_config(cls, config_file: str, default_config: Dict = None) -> Dict:
        """
        從文件載入配置
        
        Args:
            config_file: 配置文件路徑
            default_config: 默認配置，當配置項缺失時使用
            
        Returns:
            合併後的配置字典
        """
        try:
            config_dir = os.path.dirname(config_file)
            config = cls._load_config_file(config_file)
            
            # 若配置為空，使用默認配置
            if not config:
                cls.logger.warning(f"配置文件 {config_file} 為空，使用默認配置")
                return default_config or {}
            
            # 處理導入配置
            if "imports" in config:
                for import_file in config["imports"]:
                    # 處理相對路徑
                    if not os.path.isabs(import_file):
                        import_file = os.path.join(config_dir, import_file)
                    
                    if os.path.exists(import_file):
                        imported_config = cls._load_config_file(import_file)
                        # 合併配置，使當前配置優先
                        cls._merge_configs(config, imported_config)
                    else:
                        cls.logger.warning(f"導入配置文件不存在: {import_file}")
                
                # 移除導入列表
                del config["imports"]
            
            # 處理敏感信息
            if "credentials" in config:
                cred_file = config["credentials"]
                
                # 處理相對路徑
                if not os.path.isabs(cred_file):
                    cred_file = os.path.join(config_dir, cred_file)
                
                if os.path.exists(cred_file):
                    credentials = cls._load_credentials(cred_file)
                    # 合併敏感信息
                    cls._merge_configs(config, credentials)
                else:
                    cls.logger.warning(f"憑證文件不存在: {cred_file}")
                
                # 移除憑證文件引用
                del config["credentials"]
            
            # 使用默認配置填充缺失項
            if default_config:
                cls._merge_configs(config, default_config, override=False)
            
            return config
        
        except Exception as e:
            cls.logger.error(f"載入配置文件 {config_file} 失敗: {str(e)}")
            # 發生錯誤時使用默認配置
            return default_config or {}
    
    @classmethod
    def _load_config_file(cls, file_path: str) -> Dict:
        """從文件載入配置，支持JSON和YAML格式"""
        try:
            _, ext = os.path.splitext(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                if ext.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                else:  # 默認為JSON
                    return json.load(f)
        
        except FileNotFoundError:
            cls.logger.error(f"配置文件不存在: {file_path}")
            return {}
        except json.JSONDecodeError:
            cls.logger.error(f"配置文件JSON格式錯誤: {file_path}")
            return {}
        except yaml.YAMLError:
            cls.logger.error(f"配置文件YAML格式錯誤: {file_path}")
            return {}
        except Exception as e:
            cls.logger.error(f"載入配置文件失敗: {str(e)}")
            return {}
    
    @classmethod
    def _load_credentials(cls, credentials_file: str) -> Dict:
        """載入敏感信息配置"""
        try:
            config = cls._load_config_file(credentials_file)
            
            # 檢查是否包含加密信息
            if "encrypted" in config and config["encrypted"]:
                # 解密配置
                decrypted_config = cls._decrypt_config(config)
                return decrypted_config
            
            return config
        
        except Exception as e:
            cls.logger.error(f"載入憑證文件失敗: {str(e)}")
            return {}
    
    @classmethod
    def _encrypt_config(cls, config: Dict, password: str = None) -> Dict:
        """
        加密配置信息
        
        Args:
            config: 原始配置
            password: 加密密碼，為None時使用環境變量或默認密碼
            
        Returns:
            加密後的配置
        """
        # 簡單的加密示範，實際應用中應使用更安全的加密方法
        try:
            import cryptography.fernet
            
            # 獲取密碼
            if password is None:
                password = os.environ.get("CONFIG_ENCRYPT_KEY", "default_encryption_key")
            
            # 生成密鑰
            key = base64.urlsafe_b64encode(password.ljust(32)[:32].encode())
            cipher = cryptography.fernet.Fernet(key)
            
            # 移除不需要加密的項目
            encrypted_config = {k: v for k, v in config.items() if k != "encrypted"}
            
            # 加密配置
            encrypted_data = cipher.encrypt(json.dumps(encrypted_config).encode())
            
            # 返回加密結果
            return {
                "encrypted": True,
                "data": encrypted_data.decode()
            }
        
        except ImportError:
            cls.logger.warning("未安裝cryptography庫，無法加密配置")
            return config
        except Exception as e:
            cls.logger.error(f"加密配置失敗: {str(e)}")
            return config
    
    @classmethod
    def _decrypt_config(cls, config: Dict, password: str = None) -> Dict:
        """
        解密配置信息
        
        Args:
            config: 加密的配置
            password: 解密密碼，為None時使用環境變量或默認密碼
            
        Returns:
            解密後的配置
        """
        # 與加密方法對應的解密實現
        try:
            import cryptography.fernet
            
            # 檢查配置格式
            if not config.get("encrypted") or "data" not in config:
                return config
            
            # 獲取密碼
            if password is None:
                password = os.environ.get("CONFIG_ENCRYPT_KEY", "default_encryption_key")
            
            # 生成密鑰
            key = base64.urlsafe_b64encode(password.ljust(32)[:32].encode())
            cipher = cryptography.fernet.Fernet(key)
            
            # 解密數據
            decrypted_data = cipher.decrypt(config["data"].encode())
            decrypted_config = json.loads(decrypted_data.decode())
            
            return decrypted_config
        
        except ImportError:
            cls.logger.warning("未安裝cryptography庫，無法解密配置")
            return config
        except Exception as e:
            cls.logger.error(f"解密配置失敗: {str(e)}")
            return config
    
    @classmethod
    def _merge_configs(cls, target: Dict, source: Dict, override: bool = True) -> Dict:
        """
        合併兩個配置字典，可選是否覆蓋現有值
        
        Args:
            target: 目標配置，會被修改
            source: 源配置
            override: 是否覆蓋目標配置中的現有值
            
        Returns:
            合併後的配置
        """
        for key, value in source.items():
            # 如果目標中不存在此鍵或允許覆蓋
            if key not in target or override:
                # 如果是字典，遞歸合併
                if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                    cls._merge_configs(target[key], value, override)
                else:
                    # 否則直接賦值
                    target[key] = value
        
        return target
    
    @classmethod
    def save_config(cls, config: Dict, file_path: str, encrypt: bool = False, password: str = None) -> bool:
        """
        保存配置到文件
        
        Args:
            config: 配置字典
            file_path: 保存路徑
            encrypt: 是否加密
            password: 加密密碼
            
        Returns:
            是否成功保存
        """
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 如果需要加密
            if encrypt:
                config = cls._encrypt_config(config, password)
            
            # 根據文件擴展名選擇格式
            _, ext = os.path.splitext(file_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                if ext.lower() in ['.yaml', '.yml']:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                else:  # 默認為JSON
                    json.dump(config, f, indent=4, ensure_ascii=False)
            
            cls.logger.info(f"配置已保存到: {file_path}")
            return True
        
        except Exception as e:
            cls.logger.error(f"保存配置失敗: {str(e)}")
            return False
    
    @classmethod
    def validate_config(cls, config: Dict, schema: Dict) -> Dict:
        """
        驗證配置是否符合模式
        
        Args:
            config: 配置字典
            schema: 配置模式
            
        Returns:
            包含驗證結果的字典：
            {
                "valid": True/False,
                "errors": [錯誤列表]
            }
        """
        try:
            import jsonschema
            
            errors = []
            valid = True
            
            try:
                jsonschema.validate(config, schema)
            except jsonschema.exceptions.ValidationError as e:
                valid = False
                errors.append(str(e))
            
            return {
                "valid": valid,
                "errors": errors
            }
        
        except ImportError:
            cls.logger.warning("未安裝jsonschema庫，無法驗證配置")
            return {"valid": True, "errors": []}
        except Exception as e:
            cls.logger.error(f"驗證配置失敗: {str(e)}")
            return {"valid": False, "errors": [str(e)]}
    
    @classmethod
    def get_nested_value(cls, config: Dict, path: str, default: Any = None) -> Any:
        """
        獲取嵌套配置中的值
        
        Args:
            config: 配置字典
            path: 路徑，使用點號分隔，例如 "database.connection.host"
            default: 如果值不存在，返回的默認值
            
        Returns:
            配置值或默認值
        """
        parts = path.split('.')
        current = config
        
        try:
            for part in parts:
                current = current[part]
            
            return current
        except (KeyError, TypeError):
            return default
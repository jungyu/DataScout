"""
配置管理模組

提供框架的全局配置設置和讀取功能。
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union

from playwright_base.utils.logger import setup_logger
from playwright_base.utils.exceptions import ConfigException

# 設置日誌
logger = setup_logger(name=__name__)

# 預設配置
DEFAULT_CONFIG = {
    "browser": {
        "browser_type": "chromium",  # 'chromium', 'firefox', 'webkit'
        "headless": False,
        "slow_mo": 0,  # 操作間延遲毫秒數，用於調試
        "launch_options": {
            "args": ["--start-maximized"]
        },
        "context_options": {
            "viewport": {
                "width": 1920,
                "height": 1080
            },
            "ignore_https_errors": True
        }
    },
    "storage": {
        "storage_dir": "data/storage",
        "default_storage_file": "storage.json",
        "auto_save": True,
        "auto_load": True
    },
    "network": {
        "timeout": 30000,  # 網絡請求超時（毫秒）
        "navigation_timeout": 60000,  # 頁面導航超時（毫秒）
        "retry": {
            "max_retries": 3,
            "retry_delay": 1000  # 重試間隔（毫秒）
        },
        "wait_until": "domcontentloaded"  # 'load', 'domcontentloaded', 'networkidle'
    },
    "proxy": {
        "enabled": False,
        "proxies_file": "data/proxies.json",
        "rotation": {
            "enabled": False,
            "max_requests": 10,  # 每個代理的最大請求數
            "rotation_policy": "sequential"  # 'sequential', 'random'
        }
    },
    "user_agent": {
        "enabled": True,
        "user_agents_file": "data/user_agents.json",
        "rotation": {
            "enabled": False,
            "max_requests": 10,  # 每個用戶代理的最大請求數
            "rotation_policy": "sequential"  # 'sequential', 'random'
        }
    },
    "anti_detection": {
        "stealth_mode": True,
        "webgl_spoof": True,
        "canvas_spoof": True,
        "audio_spoof": False,
        "human_like_behavior": {
            "enabled": True,
            "scroll": {
                "enabled": True,
                "min_scroll_times": 3,
                "max_scroll_times": 8,
                "min_scroll_distance": 300,
                "max_scroll_distance": 800,
                "min_delay": 0.5,
                "max_delay": 2.0
            },
            "mouse": {
                "enabled": True,
                "min_moves": 3,
                "max_moves": 10,
                "min_delay": 0.1,
                "max_delay": 0.5
            },
            "keyboard": {
                "enabled": True,
                "min_delay": 0.05,
                "max_delay": 0.2,
                "mistake_probability": 0.05
            }
        }
    },
    "page_management": {
        "max_pages": 3,  # 最大允許的頁面數量
        "auto_close_popups": True
    },
    "logging": {
        "level": "INFO",  # 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "log_dir": "logs",
        "log_file": None,  # 設置後將同時輸出到檔案
        "console": True  # 是否輸出到控制台
    },
    "screenshot": {
        "enabled": True,
        "on_error": True,  # 錯誤時是否自動截圖
        "save_path": "data/screenshots",
        "full_page": True
    },
    "debug": {
        "enabled": False,
        "trace": False,  # 是否啟用 Playwright 的 trace 功能
        "trace_path": "data/trace",
        "devtools": False  # 是否自動打開 devtools
    }
}

class ConfigManager:
    """
    配置管理類。
    
    負責載入、保存和訪問框架配置。
    """
    
    def __init__(self, config_path: str = None):
        """
        初始化 ConfigManager 實例。
        
        參數:
            config_path (str): 配置檔案路徑。
        """
        self.config = DEFAULT_CONFIG.copy()
        self.config_path = config_path
        
        # 如果提供了配置檔案路徑，則從檔案載入
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
        else:
            logger.info("使用默認配置")
    
    def load_config(self, config_path: str) -> None:
        """
        從檔案載入配置。
        
        參數:
            config_path (str): 配置檔案路徑。
            
        異常:
            ConfigException: 載入配置失敗時拋出。
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                
            # 合併配置
            self._merge_config(self.config, user_config)
            self.config_path = config_path
            
            logger.info(f"已從 {config_path} 載入配置")
        except Exception as e:
            logger.error(f"載入配置檔案時發生錯誤: {str(e)}")
            raise ConfigException(f"載入配置失敗: {str(e)}")
    
    def _merge_config(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        深度合併兩個配置字典。
        
        參數:
            target (Dict[str, Any]): 目標配置字典，將被修改。
            source (Dict[str, Any]): 源配置字典，提供要合併的值。
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # 兩者都是字典，遞迴合併
                self._merge_config(target[key], value)
            else:
                # 覆蓋或添加值
                target[key] = value
    
    def save_config(self, config_path: str = None) -> None:
        """
        保存當前配置到檔案。
        
        參數:
            config_path (str): 保存的檔案路徑，若為 None 則使用初始化時的路徑。
            
        異常:
            ConfigException: 保存配置失敗時拋出。
        """
        path = config_path or self.config_path
        if not path:
            logger.warning("未指定配置檔案路徑，無法保存")
            return
            
        try:
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
                
            logger.info(f"已保存配置到 {path}")
        except Exception as e:
            logger.error(f"保存配置檔案時發生錯誤: {str(e)}")
            raise ConfigException(f"保存配置失敗: {str(e)}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        獲取指定路徑的配置值。
        
        參數:
            key_path (str): 配置鍵路徑，使用 '.' 分隔層級，例如 'browser.headless'。
            default (Any): 如果指定路徑不存在，返回的默認值。
            
        返回:
            Any: 配置值或默認值。
        """
        keys = key_path.split('.')
        config = self.config
        
        try:
            for key in keys:
                config = config[key]
            return config
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """
        設置指定路徑的配置值。
        
        參數:
            key_path (str): 配置鍵路徑，使用 '.' 分隔層級，例如 'browser.headless'。
            value (Any): 要設置的值。
            
        異常:
            ConfigException: 設置配置失敗時拋出。
        """
        keys = key_path.split('.')
        config = self.config
        
        try:
            # 導航到最後一個鍵的父級
            for key in keys[:-1]:
                if key not in config or not isinstance(config[key], dict):
                    config[key] = {}
                config = config[key]
                
            # 設置最後一個鍵的值
            config[keys[-1]] = value
            logger.debug(f"已設置配置 {key_path} = {value}")
        except Exception as e:
            logger.error(f"設置配置 {key_path} 時發生錯誤: {str(e)}")
            raise ConfigException(f"設置配置失敗: {str(e)}")
    
    def get_browser_config(self) -> Dict[str, Any]:
        """
        獲取瀏覽器配置。
        
        返回:
            Dict[str, Any]: 瀏覽器配置字典。
        """
        return self.config.get("browser", {})
    
    def get_network_config(self) -> Dict[str, Any]:
        """
        獲取網絡配置。
        
        返回:
            Dict[str, Any]: 網絡配置字典。
        """
        return self.config.get("network", {})
    
    def get_anti_detection_config(self) -> Dict[str, Any]:
        """
        獲取反檢測配置。
        
        返回:
            Dict[str, Any]: 反檢測配置字典。
        """
        return self.config.get("anti_detection", {})
    
    def get_logging_level(self) -> int:
        """
        獲取日誌級別。
        
        返回:
            int: 日誌級別數值。
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        
        level_str = self.get("logging.level", "INFO").upper()
        return level_map.get(level_str, logging.INFO)
    
    def get_all_config(self) -> Dict[str, Any]:
        """
        獲取所有配置。
        
        返回:
            Dict[str, Any]: 完整配置字典。
        """
        return self.config


# 創建全局配置管理器實例
config_manager = ConfigManager()

def get_config() -> ConfigManager:
    """
    獲取全局配置管理器實例。
    
    返回:
        ConfigManager: 配置管理器實例。
    """
    return config_manager
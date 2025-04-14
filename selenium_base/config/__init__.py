#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模組

提供爬蟲系統的配置管理功能，包括：
1. 配置加載
2. 配置驗證
3. 配置更新
4. 配置備份
"""

from .paths import (
    DATA_DIR,
    CAPTCHA_DIR,
    DEBUG_DIR,
    OUTPUT_DIR,
    SCREENSHOTS_DIR,
    LOGS_DIR,
    CONFIG_DIR,
    get_paths
)
from .loader import ConfigLoader
from .validator import ConfigValidator
from .updater import ConfigUpdater

__version__ = '1.0.0'
__author__ = 'Aaron Yu (https://github.com/jungyu), Claude AI, Cursor AI'
__license__ = 'MIT'

__all__ = [
    # 路徑
    'DATA_DIR',
    'CAPTCHA_DIR',
    'DEBUG_DIR',
    'OUTPUT_DIR',
    'SCREENSHOTS_DIR',
    'LOGS_DIR',
    'CONFIG_DIR',
    'get_paths',
    
    # 類別
    'ConfigLoader',
    'ConfigValidator',
    'ConfigUpdater'
]

def load_config(config_type: str, config_path: Optional[str] = None) -> Dict:
    """
    加載指定類型的配置
    
    Args:
        config_type: 配置類型，可選值：request, rate_limit, notification
        config_path: 配置文件路徑
        
    Returns:
        配置字典
    """
    config_loaders = {
        "request": load_request_config,
        "rate_limit": load_rate_limit_config,
        "notification": load_notification_config
    }
    
    if config_type not in config_loaders:
        raise ValueError(f"不支持的配置類型：{config_type}")
        
    return config_loaders[config_type](config_path)

def save_config(config: Dict, config_type: str, config_path: Optional[str] = None) -> None:
    """
    保存配置
    
    Args:
        config: 配置字典
        config_type: 配置類型
        config_path: 配置文件路徑
    """
    if config_path is None:
        config_dir = os.path.dirname(__file__)
        config_path = os.path.join(config_dir, f"{config_type}.json")
        
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False) 
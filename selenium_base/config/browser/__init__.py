#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
瀏覽器配置模組

提供以下功能：
1. 瀏覽器基本設置
2. 代理設置
3. 用戶代理設置
4. 窗口設置
5. 超時設置
"""

from typing import Dict, Optional
import yaml
import os

def load_config(config_path: Optional[str] = None) -> Dict:
    """
    加載瀏覽器配置
    
    Args:
        config_path: 配置文件路徑，默認為 default.yaml
        
    Returns:
        配置字典
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "default.yaml")
        
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) 
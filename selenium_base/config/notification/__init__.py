#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
通知配置模組

提供以下功能：
1. 郵件通知設置
2. Slack通知設置
3. Telegram通知設置
4. 通知規則設置
5. 通知模板設置
6. 速率限制設置
"""

from typing import Dict, Optional
import json
import os

def load_config(config_path: Optional[str] = None) -> Dict:
    """
    加載通知配置
    
    Args:
        config_path: 配置文件路徑，默認為 notification.json
        
    Returns:
        配置字典
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "notification.json")
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f) 
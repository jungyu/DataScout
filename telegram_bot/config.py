#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模組

此模組提供了配置管理功能。
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Config:
    """配置類"""
    
    token: str
    admin_ids: list[int] = None
    debug: bool = False
    
    def __post_init__(self):
        """初始化後處理"""
        if self.admin_ids is None:
            self.admin_ids = []
    
    @classmethod
    def from_env(cls) -> 'Config':
        """從環境變數創建配置
        
        Returns:
            Config: 配置對象
        """
        # 載入環境變數
        load_dotenv()
        
        # 獲取配置
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ValueError("未設置 TELEGRAM_BOT_TOKEN 環境變數")
        
        # 解析管理員 ID
        admin_ids = []
        admin_ids_str = os.getenv('TELEGRAM_ADMIN_IDS', '')
        if admin_ids_str:
            admin_ids = [int(id.strip()) for id in admin_ids_str.split(',')]
        
        # 獲取調試模式
        debug = os.getenv('TELEGRAM_BOT_DEBUG', '').lower() == 'true'
        
        return cls(
            token=token,
            admin_ids=admin_ids,
            debug=debug
        )

# Bot 設定
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_USER_IDS = [int(id) for id in os.environ.get("ADMIN_USER_IDS", "").split(",") if id.strip()]

# API 金鑰
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# 授權控制
AUTHORIZED_USERS = [int(id) for id in os.environ.get("AUTHORIZED_USERS", "").split(",") if id.strip()]
REQUIRE_AUTH = os.environ.get("REQUIRE_AUTH", "True").lower() in ("true", "1", "yes")

# 請求限制設定
RATE_LIMIT = {
    "window_seconds": 60,
    "max_requests": 10
}

# 任務設定
MAX_TASKS_PER_USER = 5
MAX_CONCURRENT_TASKS = 10
TASK_TIMEOUT_SECONDS = 300  # 5分鐘

# 結果格式設定
DEFAULT_EXPORT_FORMAT = "json"
AVAILABLE_EXPORT_FORMATS = ["json", "csv", "excel"]

# 訊息設定
MESSAGES = {
    "welcome": "歡迎使用 DataScout Bot！使用 /help 查看可用指令。",
    "unauthorized": "抱歉，您未被授權使用此機器人。",
    "rate_limited": "請求頻率過高，請稍後再試。",
    "command_not_found": "未知指令，請使用 /help 查看可用指令。"
}

def get_config(key: str, default: Any = None) -> Any:
    """取得設定值"""
    if key in globals():
        return globals()[key]
    return default

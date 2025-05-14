"""
DataScout Telegram Bot 配置檔案
"""

import os
from typing import Dict, Any, Optional

# Bot 設定
TELEGRAM_BOT_TOKEN = os.environ.get("DATASCOUT_BOT_TOKEN", "")
ADMIN_USER_IDS = [int(id) for id in os.environ.get("ADMIN_USER_IDS", "").split(",") if id.strip()]

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

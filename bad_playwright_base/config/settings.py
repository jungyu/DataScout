"""
配置模塊
提供框架的各種配置選項
"""

from typing import Dict, Any, Optional
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# 配置位置優先級：
# 1. 環境變量
# 2. 配置文件
# 3. 默認值

# 加載環境變量
load_dotenv()

# 配置文件路徑
CONFIG_PATH = os.getenv("PLAYWRIGHT_CONFIG_PATH", "config/config.json")

# 嘗試從配置文件加載
def load_config_file() -> Dict[str, Any]:
    """從配置文件加載配置"""
    config_path = Path(CONFIG_PATH)
    if not config_path.exists():
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

# 配置文件中的設置
FILE_CONFIG = load_config_file()

# 獲取配置值的輔助函數
def get_config_value(
    key: str, 
    default: Any, 
    config_section: Optional[str] = None
) -> Any:
    """
    按優先級獲取配置值:
    1. 環境變量 (例如 PLAYWRIGHT_HEADLESS)
    2. 配置文件中的值
    3. 默認值

    Args:
        key: 配置鍵名
        default: 默認值
        config_section: 配置文件中的部分名稱

    Returns:
        Any: 配置值
    """
    # 先查找環境變量
    env_key = f"PLAYWRIGHT_{key.upper()}"
    env_value = os.getenv(env_key)
    if env_value is not None:
        # 嘗試將字符串轉換為適當類型
        if env_value.lower() in ["true", "false"]:
            return env_value.lower() == "true"
        try:
            # 嘗試轉換為數字
            if "." in env_value:
                return float(env_value)
            return int(env_value)
        except ValueError:
            return env_value

    # 其次查找配置文件
    if config_section:
        return FILE_CONFIG.get(config_section, {}).get(key, default)
    return FILE_CONFIG.get(key, default)

# 瀏覽器配置
BROWSER_CONFIG: Dict[str, Any] = {
    "headless": get_config_value("headless", False, "browser"),
    "slow_mo": get_config_value("slow_mo", 50, "browser"),
    "viewport": {
        "width": get_config_value("viewport_width", 1920, "browser"),
        "height": get_config_value("viewport_height", 1080, "browser"),
    },
    "user_agent": get_config_value("user_agent", None, "browser"),
    "launch_options": {
        "args": get_config_value("browser_args", [], "browser"),
    }
}

# 代理配置
PROXY_CONFIG = {
    "enabled": get_config_value("proxy_enabled", False, "proxy"),
    "server": get_config_value("proxy_server", None, "proxy"),
    "username": get_config_value("proxy_username", None, "proxy"),
    "password": get_config_value("proxy_password", None, "proxy"),
    "rotation_interval": get_config_value("proxy_rotation_interval", 300, "proxy"),
}

# 反偵測配置
ANTI_DETECTION_CONFIG = {
    "random_delay": get_config_value("random_delay", True, "anti_detection"),
    "delay_min": get_config_value("delay_min", 1, "anti_detection"),
    "delay_max": get_config_value("delay_max", 3, "anti_detection"),
    # 你可以根據需要擴充更多反偵測參數
}

# 請求攔截配置
REQUEST_INTERCEPT_CONFIG = {
    "enabled": get_config_value("request_intercept_enabled", False, "request_intercept"),
    "block_resource_types": get_config_value("block_resource_types", ["image", "stylesheet", "font"], "request_intercept"),
    "block_urls": get_config_value("block_urls", [], "request_intercept"),
    # 可根據需求擴充更多請求攔截相關參數
}

# 超時相關配置
TIMEOUT_CONFIG = {
    "page_load": get_config_value("page_load_timeout", 30000, "timeout"),
    "element": get_config_value("element_timeout", 10000, "timeout"),
    "captcha": get_config_value("captcha_timeout", 60000, "timeout"),
    "network_idle": get_config_value("network_idle_timeout", 30000, "timeout"),
    # 可根據需求擴充更多超時參數
}

# 日誌相關設定
LOGGING_CONFIG = {
    "level": get_config_value("log_level", "INFO", "logging"),
    "log_to_file": get_config_value("log_to_file", True, "logging"),
    "log_file_path": get_config_value("log_file_path", "logs/app.log", "logging"),
    "rotation": get_config_value("log_rotation", "10 MB", "logging"),
    "retention": get_config_value("log_retention", "7 days", "logging"),
    "format": get_config_value("log_format", "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", "logging"),
}

# 重試相關設定
RETRY_CONFIG = {
    "max_retries": get_config_value("max_retries", 3, "retry"),
    "retry_interval": get_config_value("retry_interval", 2, "retry"),  # 單位：秒
    "backoff_factor": get_config_value("backoff_factor", 2, "retry"),
}

# 資料儲存相關設定
STORAGE_CONFIG = {
    "base_dir": get_config_value("storage_base_dir", "data", "storage"),
    "json_dir": get_config_value("storage_json_dir", "data/json", "storage"),
    "csv_dir": get_config_value("storage_csv_dir", "data/csv", "storage"),
    "excel_dir": get_config_value("storage_excel_dir", "data/excel", "storage"),
    "raw_dir": get_config_value("storage_raw_dir", "data/raw", "storage"),
}

# 多 User-Agent 輪換清單
USER_AGENT_LIST = get_config_value(
    "user_agent_list",
    [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ],
    "browser"
)

# 自訂 HTTP headers 設定
HEADERS_CONFIG = get_config_value(
    "headers",
    {
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    },
    "http"
)
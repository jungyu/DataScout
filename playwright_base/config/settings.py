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

# ...其餘配置可依照上述模式擴充...
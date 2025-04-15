from typing import Dict, Any
import os
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

# 瀏覽器配置
BROWSER_CONFIG: Dict[str, Any] = {
    "headless": False,
    "slow_mo": 50,
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": None,  # 將由 UserAgentManager 管理
}

# 代理配置
PROXY_CONFIG = {
    "server": os.getenv("PROXY_SERVER"),
    "username": os.getenv("PROXY_USERNAME"),
    "password": os.getenv("PROXY_PASSWORD"),
}

# 防檢測配置
ANTI_DETECTION_CONFIG = {
    "random_delay": True,
    "delay_min": float(os.getenv("RANDOM_DELAY_MIN", "1")),
    "delay_max": float(os.getenv("RANDOM_DELAY_MAX", "3")),
    "human_like": True,
    "rotate_user_agent": os.getenv("USER_AGENT_ROTATION", "true").lower() == "true",
}

# 請求攔截配置
REQUEST_INTERCEPT_CONFIG = {
    "block_images": False,
    "block_stylesheets": False,
    "block_fonts": False,
    "block_media": False,
}

# 超時配置
TIMEOUT_CONFIG = {
    "navigation_timeout": 30000,
    "wait_for_timeout": 5000,
    "action_timeout": 5000,
}

# 重試配置
RETRY_CONFIG = {
    "max_retries": 3,
    "retry_delay": 1,
} 
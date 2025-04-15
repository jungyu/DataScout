"""
Playwright Base 包

提供瀏覽器自動化的基礎框架
"""

from playwright_base.core.base import PlaywrightBase
from playwright_base.utils.exceptions import (
    PlaywrightBaseException,
    BrowserException,
    PageException,
    ElementException,
    CaptchaException,
    StorageException,
    ProxyException,
    AuthenticationException,
    ConfigException,
    NavigationException,
    RequestException,
    AntiDetectionException,
)
from playwright_base.anti_detection import (
    WebGLSpoofer,
    CanvasSpoofer,
    AudioSpoofer,
    FingerprintManager,
    ProxyManager,
    HumanLikeBehavior,
    UserAgentManager,
)
from playwright_base.storage import StorageManager
from playwright_base.config import (
    BROWSER_CONFIG,
    PROXY_CONFIG,
    ANTI_DETECTION_CONFIG,
    REQUEST_INTERCEPT_CONFIG,
    TIMEOUT_CONFIG,
    RETRY_CONFIG,
)

try:
    from playwright_base.utils.logger import setup_logger
    __all__ = [
        # 核心類
        "PlaywrightBase",
        
        # 異常類
        "PlaywrightBaseException",
        "BrowserException",
        "PageException",
        "ElementException",
        "CaptchaException",
        "StorageException",
        "ProxyException",
        "AuthenticationException",
        "ConfigException",
        "NavigationException",
        "RequestException",
        "AntiDetectionException",
        
        # 反檢測類
        "WebGLSpoofer",
        "CanvasSpoofer",
        "AudioSpoofer",
        "FingerprintManager",
        "ProxyManager",
        "HumanLikeBehavior",
        "UserAgentManager",
        
        # 存儲類
        "StorageManager",
        
        # 配置常量
        "BROWSER_CONFIG",
        "PROXY_CONFIG",
        "ANTI_DETECTION_CONFIG",
        "REQUEST_INTERCEPT_CONFIG",
        "TIMEOUT_CONFIG",
        "RETRY_CONFIG",
        
        # 工具函數
        "setup_logger",
    ]
except ImportError:
    __all__ = [
        # 核心類
        "PlaywrightBase",
        
        # 異常類
        "PlaywrightBaseException",
        "BrowserException",
        "PageException",
        "ElementException",
        "CaptchaException",
        "StorageException",
        "ProxyException",
        "AuthenticationException",
        "ConfigException",
        "NavigationException",
        "RequestException",
        "AntiDetectionException",
        
        # 反檢測類
        "WebGLSpoofer",
        "CanvasSpoofer",
        "AudioSpoofer",
        "FingerprintManager",
        "ProxyManager",
        "HumanLikeBehavior",
        "UserAgentManager",
        
        # 存儲類
        "StorageManager",
        
        # 配置常量
        "BROWSER_CONFIG",
        "PROXY_CONFIG",
        "ANTI_DETECTION_CONFIG",
        "REQUEST_INTERCEPT_CONFIG",
        "TIMEOUT_CONFIG",
        "RETRY_CONFIG",
    ]

__version__ = "0.1.0" 
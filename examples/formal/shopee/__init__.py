"""
Shopee 爬蟲模組

提供蝦皮商品爬蟲的完整功能，包括：
- 商品搜尋
- 商品詳情爬取
- 瀏覽器指紋偽裝
- 請求控制
- 瀏覽器配置
"""

from .core.shopee_crawler import ShopeeCrawler
from .shopee_cli import ShopeeCrawlerCLI
from .core.browser_profile import BrowserProfile
from .core.request_controller import RequestController
from .core.browser_fingerprint import BrowserFingerprint
from .config.fingerprint_config import (
    FingerprintConfig,
    WebGLConfig,
    CanvasConfig,
    AudioConfig,
    WebRTCConfig,
    HardwareConfig
)

__version__ = "1.0.0"
__author__ = "DataScout Team"

__all__ = [
    "ShopeeCrawler",
    "ShopeeCrawlerCLI",
    "BrowserProfile",
    "RequestController",
    "BrowserFingerprint",
    "FingerprintConfig",
    "WebGLConfig",
    "CanvasConfig",
    "AudioConfig",
    "WebRTCConfig",
    "HardwareConfig"
] 
"""
Playwright Base 包

提供瀏覽器自動化的基礎框架
"""

__version__ = '0.1.0'

# 導入核心類別和函數以便使用者可直接從 playwright_base 導入
from playwright_base.core.base import PlaywrightBase
from playwright_base.utils.logger import setup_logger

# 添加新的反檢測模組導入
from playwright_base.core.stealth import inject_stealth_js
from playwright_base.core.popup_handler import check_and_handle_popup

# 只導入確定存在的模組
try:
    from playwright_base.anti_detection.platform_spoofer import PlatformSpoofer
    from playwright_base.anti_detection.advanced_detection import AdvancedAntiDetection
except ImportError:
    # 如果模組不存在，記錄一個警告但不中斷程序
    import warnings
    warnings.warn("某些反檢測模組無法導入，可能影響部分功能")

# 匯入例外類別
try:
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
        TimeoutException
    )
except ImportError:
    pass  # 如果例外類別未定義，則跳過

# 定義對外公開的模組
__all__ = [
    'PlaywrightBase',
    'setup_logger',
    'inject_stealth_js',
    'check_and_handle_popup',
]

# 動態添加可能存在的模組到 __all__
try:
    from playwright_base.anti_detection.platform_spoofer import PlatformSpoofer
    __all__.append('PlatformSpoofer')
except ImportError:
    pass

try:
    from playwright_base.anti_detection.advanced_detection import AdvancedAntiDetection
    __all__.append('AdvancedAntiDetection')
except ImportError:
    pass

# 可能已存在的模組
try:
    from playwright_base.storage.storage_manager import StorageManager
    __all__.append('StorageManager')
except ImportError:
    pass

try:
    from playwright_base.anti_detection.human_like import HumanLikeBehavior
    __all__.append('HumanLikeBehavior')
except ImportError:
    pass
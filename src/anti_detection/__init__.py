"""
反檢測模組

此模組提供反檢測和繞過反爬蟲措施的功能，包括：
1. 人類行為模擬
2. 瀏覽器指紋管理
3. 蜜罐檢測
4. 錯誤處理
5. 配置管理
"""

from .anti_detection_manager import AntiDetectionManager
from .human_behavior import HumanBehaviorSimulator, HumanBehaviorResult, HumanBehaviorError
from .browser_fingerprint import BrowserFingerprint, FingerprintResult, FingerprintError
from .honeypot_detector import HoneypotDetector, HoneypotResult, HoneypotError
from .base_error import BaseError, handle_error, retry_on_error
from .configs.human_behavior_config import HumanBehaviorConfig
from .configs.fingerprint_config import FingerprintConfig
from .configs.honeypot_config import HoneypotConfig

__all__ = [
    # 管理器
    'AntiDetectionManager',
    
    # 人類行為模擬
    'HumanBehaviorSimulator',
    'HumanBehaviorResult',
    'HumanBehaviorError',
    
    # 瀏覽器指紋
    'BrowserFingerprint',
    'FingerprintResult',
    'FingerprintError',
    
    # 蜜罐檢測
    'HoneypotDetector',
    'HoneypotResult',
    'HoneypotError',
    
    # 錯誤處理
    'BaseError',
    'handle_error',
    'retry_on_error',
    
    # 配置類
    'HumanBehaviorConfig',
    'FingerprintConfig',
    'HoneypotConfig'
]

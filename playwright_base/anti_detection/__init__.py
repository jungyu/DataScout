"""
Anti-Detection 模組

提供反檢測功能，幫助避免網站的反爬蟲檢測
"""

# 現有導入
from .anti_detection_manager import AntiDetectionManager
from .audio_spoofer import AudioSpoofer
from .canvas_spoofer import CanvasSpoofer
from .fingerprint import FingerprintManager
from .human_like import HumanLikeBehavior
from .proxy_manager import ProxyManager
from .user_agent_manager import UserAgentManager
from .webgl_spoofer import WebGLSpoofer

# 新增模組導入
from .platform_spoofer import PlatformSpoofer
from .advanced_detection import AdvancedAntiDetection

__all__ = [
    # 現有導出
    "AntiDetectionManager",
    "AudioSpoofer",
    "CanvasSpoofer",
    "FingerprintManager",
    "HumanLikeBehavior",
    "ProxyManager",
    "UserAgentManager",
    "WebGLSpoofer",
    
    # 新增功能
    "PlatformSpoofer",
    "AdvancedAntiDetection",
]
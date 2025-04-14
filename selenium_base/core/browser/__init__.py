"""
瀏覽器控制模組

提供瀏覽器配置、驅動程式管理等功能
"""

from .profile import BrowserProfile
from .driver import BrowserDriver

__all__ = ['BrowserProfile', 'BrowserDriver'] 
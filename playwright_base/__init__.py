"""
DataScout Playwright Base

這是一個基於 Playwright 的網頁自動化與數據採集框架，
提供強大的反檢測功能，優化爬蟲穩定性和效能。
"""

__version__ = '0.1.0'

# 導入核心類別和函數以便使用者可直接從 playwright_base 導入
from playwright_base.core.base import PlaywrightBase
from playwright_base.utils.logger import setup_logger

# 定義對外公開的模組
__all__ = [
    'PlaywrightBase',
    'setup_logger'
]
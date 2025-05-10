"""
Utils 模組初始化檔案
包含日誌、錯誤處理和其他實用工具
"""

from playwright_base.utils.error_handler import ErrorHandler
from playwright_base.utils.logger import setup_logger

__all__ = [
    'ErrorHandler',
    'setup_logger'
]

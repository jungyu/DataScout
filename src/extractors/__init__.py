"""
提取器包 - 包含用於從網頁中提取數據的各種提取器
"""

__all__ = [
    # 核心提取器
    'BaseExtractor',
    'DataExtractor',
    'ListExtractor',
    'DetailExtractor',
    'CompoundExtractor',
    
    # 處理器
    'CaptchaHandler',
    'PaginationHandler',
    'StorageHandler'
]

# 導入核心提取器
from .core import (
    BaseExtractor,
    DataExtractor,
    ListExtractor,
    DetailExtractor,
    CompoundExtractor
)

# 導入處理器
from .handlers import (
    CaptchaHandler,
    PaginationHandler,
    StorageHandler
)

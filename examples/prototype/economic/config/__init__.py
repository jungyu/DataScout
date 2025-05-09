"""
配置模組

此目錄包含各個爬蟲的配置文件，包括：
- Nikkei Asia 配置
- Reuters 配置
- Bloomberg 配置
- Financial Times 配置
"""

from .nikkei_config import SITE_CONFIG as NIKKEI_CONFIG
from .nikkei_config import SELECTORS as NIKKEI_SELECTORS

__all__ = [
    'NIKKEI_CONFIG',
    'NIKKEI_SELECTORS'
]

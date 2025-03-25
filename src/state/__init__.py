"""
State management module for the crawler system.
Handles crawler state persistence and recovery.
"""

from .crawler_state_manager import CrawlerStateManager
from .multi_storage import MultiStorage

__all__ = ['CrawlerStateManager', 'MultiStorage']

"""
Telegram Bot 包

此包提供了一個可擴展的 Telegram 機器人框架。
"""

from .bot import TelegramBot
from .config import Config
from .exceptions import BotError

__version__ = "0.1.0"
__all__ = ['TelegramBot', 'Config', 'BotError']

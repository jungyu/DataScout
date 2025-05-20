"""
指令處理器模組
"""

from linebot import WebhookHandler
from .basic_commands import register_basic_commands
from .crawler_commands import register_crawler_commands
from .admin_commands import register_admin_commands

def register_all_commands(handler: WebhookHandler):
    """註冊所有指令處理器"""
    register_basic_commands(handler)
    register_crawler_commands(handler)
    register_admin_commands(handler)

"""
訊息處理器模組
"""

from linebot import WebhookHandler
from .text_handler import register_text_handler
from .image_handler import register_image_handler

def register_all_handlers(handler: WebhookHandler):
    """註冊所有訊息處理器"""
    register_text_handler(handler)
    register_image_handler(handler)

"""
中介軟體模組
"""

from linebot import WebhookHandler
from .auth_middleware import setup_auth_middleware
from .rate_limit_middleware import setup_rate_limit_middleware

def setup_middlewares(handler: WebhookHandler):
    """設定所有中介軟體"""
    setup_auth_middleware(handler)
    setup_rate_limit_middleware(handler)

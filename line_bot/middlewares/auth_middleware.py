"""
身份驗證中介軟體
"""

import logging
from linebot import WebhookHandler
from line_bot.config import REQUIRE_AUTH, AUTHORIZED_USERS
from line_bot.utils.auth import check_auth

logger = logging.getLogger(__name__)

def setup_auth_middleware(handler: WebhookHandler):
    """設定身份驗證中介軟體"""
    
    @handler.add(MessageEvent)
    def auth_middleware(event):
        """處理身份驗證"""
        if not REQUIRE_AUTH:
            return True
            
        user_id = event.source.user_id
        if not check_auth(user_id):
            logger.warning(f"未授權用戶嘗試訪問：{user_id}")
            return False
            
        return True 
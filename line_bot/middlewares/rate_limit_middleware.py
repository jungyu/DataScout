"""
請求頻率限制中介軟體
"""

import logging
import time
from collections import defaultdict
from linebot import WebhookHandler
from line_bot.config import RATE_LIMIT
from line_bot.utils.rate_limit import check_rate_limit

logger = logging.getLogger(__name__)

def setup_rate_limit_middleware(handler: WebhookHandler):
    """設定請求頻率限制中介軟體"""
    
    @handler.add(MessageEvent)
    def rate_limit_middleware(event):
        """處理請求頻率限制"""
        user_id = event.source.user_id
        if not check_rate_limit(user_id):
            logger.warning(f"用戶請求頻率過高：{user_id}")
            return False
            
        return True 
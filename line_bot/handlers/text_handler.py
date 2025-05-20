"""
文字訊息處理器
"""

import logging
from linebot import WebhookHandler
from linebot.models import TextSendMessage
from line_bot.config import MESSAGES

logger = logging.getLogger(__name__)

def register_text_handler(handler: WebhookHandler):
    """註冊文字訊息處理器"""
    
    @handler.add(MessageEvent, message=TextMessage)
    def handle_text(event):
        """處理文字訊息"""
        text = event.message.text.strip()
        
        # 如果訊息不是指令，則回覆預設訊息
        if not text.startswith(("爬蟲", "排程", "取消", "狀態", "列表", "歷史", "結果", "匯出", "系統", "所有任務", "終止", "開始", "說明")):
            return TextSendMessage(text=MESSAGES["command_not_found"])
            
        return None 
"""
管理員指令處理器
"""

import logging
from linebot import WebhookHandler
from linebot.models import TextSendMessage
from line_bot.config import MESSAGES, ADMIN_USER_IDS
from line_bot.utils.auth import is_admin

logger = logging.getLogger(__name__)

def register_admin_commands(handler: WebhookHandler):
    """註冊管理員指令"""
    
    @handler.add(MessageEvent, message=TextMessage)
    def handle_admin_commands(event):
        """處理管理員指令"""
        text = event.message.text.strip()
        user_id = event.source.user_id
        
        # 檢查是否為管理員
        if not is_admin(user_id):
            return None
            
        # 系統狀態
        if text == "系統":
            # TODO: 實作系統狀態查詢邏輯
            return TextSendMessage(text="系統狀態：正常運行中")
            
        # 所有任務
        elif text == "所有任務":
            # TODO: 實作所有任務查詢邏輯
            return TextSendMessage(text="目前沒有進行中的任務")
            
        # 終止任務
        elif text.startswith("終止 "):
            try:
                # 解析任務ID
                _, task_id = text.split()
                # TODO: 實作任務終止邏輯
                return TextSendMessage(text=f"已終止任務：{task_id}")
            except Exception as e:
                logger.error(f"終止指令處理錯誤：{e}")
                return TextSendMessage(text="終止指令格式錯誤，請使用「說明」查看正確格式")
                
        return None 
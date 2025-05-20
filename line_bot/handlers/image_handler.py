"""
圖片訊息處理器
"""

import logging
from linebot import WebhookHandler, LineBotApi
from linebot.models import ImageSendMessage, TextSendMessage
from line_bot.config import LINE_CHANNEL_ACCESS_TOKEN, GEMINI_API_KEY
from line_bot.utils.auth import check_auth
from line_bot.utils.rate_limit import check_rate_limit

logger = logging.getLogger(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def register_image_handler(handler: WebhookHandler):
    """註冊圖片訊息處理器"""
    
    @handler.add(MessageEvent, message=ImageMessage)
    def handle_image(event):
        """處理圖片訊息"""
        user_id = event.source.user_id
        
        # 檢查授權
        if not check_auth(user_id):
            return TextSendMessage(text="抱歉，您未被授權使用此功能")
            
        # 檢查頻率限制
        if not check_rate_limit(user_id):
            return TextSendMessage(text="請求頻率過高，請稍後再試")
            
        try:
            # 取得圖片內容
            message_content = line_bot_api.get_message_content(event.message.id)
            
            # TODO: 使用 Google Gemini API 分析圖片
            # 這裡需要實作圖片分析邏輯
            
            return TextSendMessage(text="圖片分析完成，但尚未實作具體分析邏輯")
            
        except Exception as e:
            logger.error(f"圖片處理錯誤：{e}")
            return TextSendMessage(text="圖片處理失敗，請稍後再試") 
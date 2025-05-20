"""
基本指令處理器
"""

import logging
from linebot import WebhookHandler
from linebot.models import TextSendMessage
from line_bot.config import MESSAGES

logger = logging.getLogger(__name__)

def register_basic_commands(handler: WebhookHandler):
    """註冊基本指令"""
    
    @handler.add(MessageEvent, message=TextMessage)
    def handle_basic_commands(event):
        """處理基本指令"""
        text = event.message.text.strip()
        user_id = event.source.user_id
        
        if text == "開始":
            return TextSendMessage(text=MESSAGES["welcome"])
            
        elif text == "說明":
            help_text = """
📱 DataScout Bot 使用說明

基本指令：
- 「開始」 - 開始使用機器人
- 「說明」 - 顯示此說明

爬蟲操作：
- 「爬蟲 [URL] [選項]」 - 啟動爬蟲任務
- 「排程 [URL] [選項] [時間]」 - 排程爬蟲任務
- 「取消 [任務ID]」 - 取消爬蟲任務

狀態查詢：
- 「狀態 [任務ID]」 - 查詢特定任務狀態
- 「列表」 - 列出所有進行中的任務
- 「歷史」 - 顯示歷史任務

結果處理：
- 「結果 [任務ID]」 - 獲取任務結果
- 「匯出 [任務ID] [格式]」 - 匯出特定格式的結果

圖像處理：
- 「圖片」 - 顯示圖像分析功能說明
- 直接發送圖片 - 自動分析圖片內容
- 發送圖片時添加說明 - 使用自定義提示詞

管理員指令：
- 「系統」 - 查看系統狀態
- 「所有任務」 - 列出所有任務
- 「終止 [任務ID]」 - 強制終止任務
            """
            return TextSendMessage(text=help_text)
            
        return None 
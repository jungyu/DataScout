"""
DataScout LINE Bot 主入口
"""

import logging
import os
from pathlib import Path
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
from flask import Flask, request, abort
from dotenv import load_dotenv

from line_bot.config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from line_bot.commands import register_all_commands
from line_bot.handlers import register_all_handlers
from line_bot.middlewares import setup_middlewares

# 設定日誌
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

class DataScoutLineBot:
    """DataScout LINE Bot 核心類別"""
    
    def __init__(self):
        """初始化 Bot"""
        if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
            raise ValueError("LINE Channel Access Token and Secret are required")
            
        self._setup_bot()
        
    def _setup_bot(self):
        """設定 Bot 的指令和中介軟體"""
        # 註冊所有指令
        register_all_commands(handler)
        
        # 註冊所有訊息處理器
        register_all_handlers(handler)
        
        # 設定中介軟體
        setup_middlewares(handler)
        
        logger.info("Bot setup completed")
        
    @app.route("/callback", methods=['POST'])
    def callback():
        """處理 LINE 的 Webhook 請求"""
        # 取得 X-Line-Signature header
        signature = request.headers['X-Line-Signature']

        # 取得請求內容
        body = request.get_data(as_text=True)
        logger.info("Request body: " + body)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return 'OK'
        
    def run(self, host='0.0.0.0', port=5000):
        """啟動 Bot"""
        logger.info("Starting DataScout LINE Bot")
        app.run(host=host, port=port)
        
    @classmethod
    def start(cls):
        """便捷方法：創建實例並運行 Bot"""
        # 確保加載環境變量
        load_dotenv()
        
        bot = cls()
        bot.run()

if __name__ == "__main__":
    # 直接執行此檔案時運行 Bot
    DataScoutLineBot.start() 
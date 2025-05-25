#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram 服務

此模組提供了與 Telegram Bot API 交互的功能。
"""

import os
import logging
from typing import Dict, Any
from telegram import Bot
from telegram.error import TelegramError

class TelegramService:
    """Telegram 服務類"""
    
    def __init__(self):
        """初始化 Telegram 服務"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("未設置 TELEGRAM_BOT_TOKEN 環境變數")
        self.bot = Bot(token=self.token)
    
    async def send_message(self, chat_id: int, text: str) -> None:
        """發送消息
        
        Args:
            chat_id: 聊天 ID
            text: 消息內容
        """
        try:
            await self.bot.send_message(chat_id=chat_id, text=text)
        except TelegramError as e:
            self.logger.error(f"發送消息時發生錯誤：{str(e)}")
            raise 
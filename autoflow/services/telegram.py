#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram 服務模組

此模組提供與 Telegram Bot API 的互動功能
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from autoflow.core.config import Config

logger = logging.getLogger(__name__)

class TelegramService:
    """Telegram 服務類別"""
    
    def __init__(self):
        """初始化 Telegram 服務"""
        self.config = Config()
        self.app: Optional[Application] = None
        self.logger = logger
        self._running = False
    
    async def start(self) -> Dict[str, Any]:
        """啟動 Telegram 服務
        
        Returns:
            Dict[str, Any]: 機器人信息
        """
        try:
            # 驗證配置
            if not self.config.get('telegram_token'):
                raise ValueError("缺少 Telegram Bot Token")
            
            # 創建應用實例
            self.app = Application.builder().token(self.config.get('telegram_token')).build()
            
            # 註冊命令處理器
            self.app.add_handler(CommandHandler('start', self._handle_start))
            
            # 註冊消息處理器
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
            
            # 啟動輪詢（非阻塞）
            self._running = True
            asyncio.create_task(self._run_polling())
            
            # 獲取機器人信息
            bot = await self.app.bot.get_me()
            self.logger.info(f"Telegram 服務已啟動，機器人：{bot.username}")
            
            return bot.to_dict()
            
        except Exception as e:
            self.logger.error(f"啟動 Telegram 服務時發生錯誤：{str(e)}")
            raise
    
    async def stop(self) -> None:
        """停止 Telegram 服務"""
        try:
            if self.app:
                self._running = False
                await self.app.stop()
                self.logger.info("Telegram 服務已停止")
        except Exception as e:
            self.logger.error(f"停止 Telegram 服務時發生錯誤：{str(e)}")
            raise
    
    async def _run_polling(self) -> None:
        """在背景運行輪詢"""
        try:
            while self._running:
                await self.app.update_queue.get()
        except Exception as e:
            self.logger.error(f"輪詢時發生錯誤：{str(e)}")
            self._running = False
    
    async def send_message(self, chat_id: int, text: str) -> None:
        """發送訊息"""
        try:
            if not self.app:
                raise RuntimeError("Telegram 服務尚未啟動")
            
            await self.app.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode='HTML'
            )
        except Exception as e:
            self.logger.error(f"發送訊息時發生錯誤：{str(e)}")
            raise
    
    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """處理 /start 命令"""
        try:
            welcome_message = (
                "👋 歡迎使用股票行情查詢機器人！\n\n"
                "📊 使用方法：\n"
                "1. 直接輸入股票代碼（例如：AAPL）\n"
                "2. 等待機器人回覆股票資訊\n\n"
                "💡 提示：\n"
                "- 支援美股、港股等市場\n"
                "- 使用標準股票代碼格式"
            )
            await update.message.reply_text(welcome_message)
        except Exception as e:
            self.logger.error(f"處理 /start 命令時發生錯誤：{str(e)}")
            await update.message.reply_text("處理命令時發生錯誤，請稍後再試。")
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """處理一般訊息"""
        try:
            # 這裡只處理訊息，實際的股票查詢邏輯在 StockBotFlow 中
            await update.message.reply_text("正在處理您的請求，請稍候...")
        except Exception as e:
            self.logger.error(f"處理訊息時發生錯誤：{str(e)}")
            await update.message.reply_text("處理訊息時發生錯誤，請稍後再試。") 
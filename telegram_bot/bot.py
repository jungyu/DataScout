#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram Bot 主模組

此模組提供了 Telegram 機器人的主要功能。
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from .config import Config
from .exceptions import BotError

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramBot:
    """Telegram 機器人類"""
    
    def __init__(self, config: Optional[Config] = None):
        """初始化機器人
        
        Args:
            config: 配置對象，如果為 None 則使用默認配置
        """
        self.config = config or Config()
        self.app: Optional[Application] = None
        
    async def start(self) -> None:
        """啟動機器人"""
        try:
            # 創建應用
            self.app = Application.builder().token(self.config.token).build()
            
            # 註冊處理器
            self._register_handlers()
            
            # 啟動機器人
            await self.app.initialize()
            await self.app.start()
            await self.app.run_polling()
            
        except Exception as e:
            logger.error(f"啟動機器人時發生錯誤：{str(e)}")
            raise BotError(f"啟動失敗：{str(e)}")
    
    async def stop(self) -> None:
        """停止機器人"""
        if self.app:
            await self.app.stop()
            await self.app.shutdown()
    
    def _register_handlers(self) -> None:
        """註冊消息處理器"""
        if not self.app:
            raise BotError("應用未初始化")
            
        # 註冊命令處理器
        self.app.add_handler(CommandHandler("start", self._handle_start))
        self.app.add_handler(CommandHandler("help", self._handle_help))
        
        # 註冊消息處理器
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
    
    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """處理 /start 命令"""
        await update.message.reply_text("歡迎使用 Telegram Bot！")
    
    async def _handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """處理 /help 命令"""
        help_text = """
可用命令：
/start - 開始使用機器人
/help - 顯示幫助信息
        """
        await update.message.reply_text(help_text)
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """處理普通消息"""
        await update.message.reply_text(f"收到消息：{update.message.text}")

async def main() -> None:
    """主函數"""
    try:
        # 載入環境變數
        load_dotenv()
        
        # 創建並啟動機器人
        bot = TelegramBot()
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("正在關閉機器人...")
    except Exception as e:
        logger.error(f"運行時發生錯誤：{str(e)}")
        raise
    finally:
        # 清理資源
        if 'bot' in locals():
            await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())

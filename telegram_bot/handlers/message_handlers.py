"""
訊息處理器
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.config import MESSAGES

logger = logging.getLogger(__name__)

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理未知指令
    
    當用戶發送一個未定義的指令時，回應一個提示訊息。
    """
    user = update.effective_user
    command = update.message.text
    logger.info(f"User {user.id} sent unknown command: {command}")
    
    await update.message.reply_text(
        f"{MESSAGES['command_not_found']}\n"
        "使用 /help 查看可用指令列表。"
    )

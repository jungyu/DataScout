"""
基本指令處理
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.config import MESSAGES

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /start 指令
    
    向用戶發送歡迎訊息和基本使用說明
    """
    user = update.effective_user
    logger.info(f"User {user.id} ({user.full_name}) started the bot")
    
    welcome_message = (
        f"👋 {MESSAGES['welcome']}\n\n"
        "DataScout Bot 可以幫助你管理和控制爬蟲任務。\n\n"
        "🔸 使用 /crawl 指令開始一個新的爬蟲任務\n"
        "🔸 使用 /status 查詢任務狀態\n"
        "🔸 使用 /list 列出所有進行中的任務\n\n"
        "完整指令列表請使用 /help 查詢"
    )
    
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /help 指令
    
    顯示所有可用指令的說明
    """
    user = update.effective_user
    logger.info(f"User {user.id} requested help")
    
    help_text = (
        "📚 *DataScout Bot 指令說明*\n\n"
        "*基本指令:*\n"
        "/start - 啟動機器人\n"
        "/help - 顯示此幫助訊息\n\n"
        
        "*爬蟲操作:*\n"
        "/crawl [URL] [選項] - 啟動爬蟲任務\n"
        "/schedule [URL] [選項] [時間] - 排程爬蟲任務\n"
        "/cancel [任務ID] - 取消爬蟲任務\n\n"
        
        "*狀態查詢:*\n"
        "/status [任務ID] - 查詢特定任務狀態\n"
        "/list - 列出所有進行中的任務\n"
        "/history - 顯示歷史任務記錄\n\n"
        
        "*結果處理:*\n"
        "/result [任務ID] - 獲取任務結果\n"
        "/export [任務ID] [格式] - 匯出特定格式的結果\n\n"
        
        "*設定:*\n"
        "/config [參數] [值] - 設定爬蟲參數\n"
        "/profile - 顯示用戶設定\n\n"
        
        "詳細使用說明請參考文件: https://datascout.docs/bot"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

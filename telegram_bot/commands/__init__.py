"""
指令註冊與管理
"""

from telegram.ext import Application, CommandHandler, MessageHandler, filters

# 匯入指令處理器
from telegram_bot.commands.crawl_commands import register_crawl_commands
from telegram_bot.commands.status_commands import register_status_commands
from telegram_bot.commands.admin_commands import register_admin_commands
from telegram_bot.commands.result_commands import register_result_commands


def register_all_commands(application: Application):
    """註冊所有指令處理器
    
    Args:
        application: Telegram bot application 實例
    """
    # 註冊基本指令
    from telegram_bot.commands.basic_commands import start, help_command
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # 註冊爬蟲相關指令
    register_crawl_commands(application)
    
    # 註冊狀態查詢指令
    register_status_commands(application)
    
    # 註冊結果處理指令
    register_result_commands(application)
    
    # 註冊管理員指令
    register_admin_commands(application)
    
    # 註冊圖像處理指令
    from telegram_bot.handlers.image_handlers import image_help_command
    application.add_handler(CommandHandler("image", image_help_command))
    
    # 註冊預設處理器已移到 handlers/__init__.py
    # 這樣可以確保指令處理器優先於訊息處理器被調用

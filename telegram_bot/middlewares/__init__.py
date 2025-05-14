"""
中介軟體註冊與管理
"""

from telegram.ext import Application, MessageHandler, filters
from functools import partial

def setup_middlewares(application: Application):
    """設定中介軟體
    
    Args:
        application: Telegram bot application 實例
    """
    # 在新版的 python-telegram-bot 中，我們需要使用處理器來實現中介軟體功能
    
    # 身份驗證中介軟體
    from telegram_bot.middlewares.auth import check_auth
    application.add_handler(
        MessageHandler(filters.ALL, check_auth), group=-100
    )
    
    # 請求頻率限制中介軟體
    from telegram_bot.middlewares.rate_limit import check_rate_limit
    application.add_handler(
        MessageHandler(filters.ALL, check_rate_limit), group=-99
    )

"""
訊息處理器註冊模組

統一註冊所有訊息處理器
"""

import logging
from telegram.ext import Application, MessageHandler, filters, CallbackQueryHandler

logger = logging.getLogger(__name__)

def register_all_handlers(application: Application):
    """註冊所有處理器
    
    Args:
        application: Telegram bot application 實例
    """
    from telegram_bot.handlers.message_handlers import unknown_command
    from telegram_bot.handlers.image_handlers import handle_image, handle_image_callback
    
    # 註冊圖像處理器 - 放在最前面以優先處理
    application.add_handler(
        MessageHandler(
            filters.PHOTO | 
            (filters.Document.ALL & filters.Document.MimeType("image/jpeg") | 
             filters.Document.MimeType("image/png") | 
             filters.Document.MimeType("image/webp")), 
            handle_image
        )
    )
    
    # 註冊圖片按鈕回調處理器
    application.add_handler(
        CallbackQueryHandler(handle_image_callback, pattern=r"^img_")
    )
    
    # 註冊未知命令處理器 - 放在最後作為後備
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    logger.info("所有訊息處理器註冊完成")

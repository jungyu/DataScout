"""
DataScout Telegram Bot 主入口
"""

import logging
import asyncio
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler

from telegram_bot.config import TELEGRAM_BOT_TOKEN
from telegram_bot.commands import register_all_commands
from telegram_bot.middlewares import setup_middlewares

# 設定日誌
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class DataScoutBot:
    """DataScout Telegram Bot 核心類別"""
    
    def __init__(self, token: str = None):
        """初始化 Bot
        
        Args:
            token: Telegram Bot Token，預設使用設定檔中的值
        """
        self.token = token or TELEGRAM_BOT_TOKEN
        if not self.token:
            raise ValueError("Bot token is required")
            
        self.application = Application.builder().token(self.token).build()
        self._setup_bot()
        
    def _setup_bot(self):
        """設定 Bot 的指令和中介軟體"""
        # 註冊所有指令
        register_all_commands(self.application)
        
        # 設定中介軟體
        setup_middlewares(self.application)
        
        logger.info("Bot setup completed")
        
    async def start(self):
        """啟動 Bot"""
        logger.info("Starting DataScout Telegram Bot")
        await self.application.initialize()
        await self.application.start()
        await self.application.run_polling()
        
    async def stop(self):
        """停止 Bot"""
        logger.info("Stopping DataScout Telegram Bot")
        await self.application.stop()
        await self.application.shutdown()
        
    @classmethod
    def run(cls):
        """便捷方法：創建實例並運行 Bot"""
        bot = cls()
        
        # 在 python-telegram-bot 20.0+ 版本中，應該使用 asyncio.run() 來運行 Bot
        logger.info("Starting bot...")
        try:
            # 將 run_polling 設為自動處理啟動和停止程序
            asyncio.run(bot.application.run_polling(allowed_updates=Update.ALL_TYPES))
        except (KeyboardInterrupt, SystemExit):
            logger.info("Bot was interrupted")
        except Exception as e:
            logger.error(f"Error running bot: {e}", exc_info=True)


if __name__ == "__main__":
    # 直接執行此檔案時運行 Bot
    DataScoutBot.run()

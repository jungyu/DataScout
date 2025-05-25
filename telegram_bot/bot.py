"""
DataScout Telegram Bot 主入口
"""

import logging
import asyncio
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from telegram import Update
from telegram.ext import Application, CommandHandler
from dotenv import load_dotenv

from telegram_bot.config import TELEGRAM_BOT_TOKEN, get_config
from telegram_bot.commands import register_all_commands
from telegram_bot.handlers import register_all_handlers
from telegram_bot.middlewares import setup_middlewares
from telegram_bot.handlers.base_handler import BaseTelegramHandler
from telegram_bot.exceptions import BotError

# 設定日誌
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class DataScoutBot(BaseTelegramHandler):
    """DataScout Telegram Bot 核心類別"""
    
    def __init__(
        self, 
        token: str = None, 
        config: Optional[Dict[str, Any]] = None,
        allowed_updates: Optional[List[str]] = None
    ):
        """初始化 Bot
        
        Args:
            token: Telegram Bot Token，預設使用設定檔中的值
            config: 額外的配置參數
            allowed_updates: 允許的更新類型列表
        """
        config = config or {}
        if token:
            config["token"] = token
        super().__init__(config)
        self.allowed_updates = allowed_updates or Update.ALL_TYPES
        
    async def initialize(self) -> None:
        """初始化 Bot
        
        Raises:
            BotError: 初始化失敗時拋出
        """
        try:
            await super().initialize()
            self._setup_bot()
            logger.info("DataScout Bot initialized")
        except Exception as e:
            logger.error(f"Failed to initialize DataScout Bot: {e}", exc_info=True)
            raise BotError(f"DataScout Bot initialization failed: {str(e)}")
        
    def _setup_bot(self):
        """設定 Bot 的指令和中介軟體"""
        try:
            # 註冊所有指令
            register_all_commands(self.application)
            
            # 註冊所有訊息處理器
            register_all_handlers(self.application)
            
            # 設定中介軟體
            setup_middlewares(self.application)
            
            logger.info("Bot setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup bot: {e}", exc_info=True)
            raise BotError(f"Bot setup failed: {str(e)}")
        
    async def start(self):
        """啟動 Bot
        
        Raises:
            BotError: 啟動失敗時拋出
        """
        try:
            if not self.application:
                await self.initialize()
            await self.application.initialize()
            await self.application.start()
            await self.application.run_polling(allowed_updates=self.allowed_updates)
            logger.info("DataScout Bot started")
        except Exception as e:
            logger.error(f"Failed to start DataScout Bot: {e}", exc_info=True)
            raise BotError(f"DataScout Bot start failed: {str(e)}")
        
    @classmethod
    def run(cls, config: Optional[Dict[str, Any]] = None):
        """便捷方法：創建實例並運行 Bot
        
        Args:
            config: 額外的配置參數
            
        Raises:
            BotError: 運行失敗時拋出
        """
        # 確保加載環境變量
        load_dotenv()
        
        try:
            bot = cls(config=config)
            logger.info("Starting bot...")
            asyncio.run(bot.application.run_polling(allowed_updates=bot.allowed_updates))
        except KeyboardInterrupt:
            logger.info("Bot was interrupted")
        except Exception as e:
            logger.error(f"Error running bot: {e}", exc_info=True)
            raise BotError(f"Bot run failed: {str(e)}")


if __name__ == "__main__":
    # 直接執行此檔案時運行 Bot
    DataScoutBot.run()

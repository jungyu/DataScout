"""
Telegram Bot 服務
"""

import logging
from typing import Dict, Any, Optional
from telegram_bot.bot import DataScoutBot
from telegram_bot.exceptions import BotError

logger = logging.getLogger(__name__)

class TelegramService:
    """Telegram Bot 服務類"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化服務
        
        Args:
            config: 配置參數
        """
        self.config = config or {}
        self.bot = None
        
    async def initialize(self):
        """初始化服務
        
        Raises:
            BotError: 初始化失敗時拋出
        """
        try:
            self.bot = DataScoutBot(
                config=self.config,
                allowed_updates=["message", "callback_query"]
            )
            await self.bot.initialize()
            logger.info("Telegram service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram service: {e}", exc_info=True)
            raise BotError(f"Telegram service initialization failed: {str(e)}")
            
    async def start(self):
        """啟動服務
        
        Raises:
            BotError: 啟動失敗時拋出
        """
        try:
            if not self.bot:
                await self.initialize()
            await self.bot.start()
            logger.info("Telegram service started")
        except Exception as e:
            logger.error(f"Failed to start Telegram service: {e}", exc_info=True)
            raise BotError(f"Telegram service start failed: {str(e)}")
            
    async def stop(self):
        """停止服務
        
        Raises:
            BotError: 停止失敗時拋出
        """
        try:
            if self.bot:
                await self.bot.stop()
                logger.info("Telegram service stopped")
        except Exception as e:
            logger.error(f"Failed to stop Telegram service: {e}", exc_info=True)
            raise BotError(f"Telegram service stop failed: {str(e)}")
            
    async def send_message(self, chat_id: int, text: str) -> None:
        """發送消息
        
        Args:
            chat_id: 聊天 ID
            text: 消息文本
            
        Raises:
            BotError: 發送失敗時拋出
        """
        try:
            if not self.bot:
                raise BotError("Telegram service not initialized")
            await self.bot.get_application().bot.send_message(
                chat_id=chat_id,
                text=text
            )
        except Exception as e:
            logger.error(f"Failed to send message: {e}", exc_info=True)
            raise BotError(f"Message sending failed: {str(e)}")
            
    def get_bot(self) -> DataScoutBot:
        """獲取 Bot 實例
        
        Returns:
            DataScoutBot: Bot 實例
            
        Raises:
            BotError: Bot 未初始化時拋出
        """
        if not self.bot:
            raise BotError("Telegram service not initialized")
        return self.bot 
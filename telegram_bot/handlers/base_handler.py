"""
Telegram Bot 基礎處理器
"""

import logging
from typing import Dict, Any, Optional
from telegram import Update
from telegram.ext import Application, ApplicationBuilder
from telegram_bot.exceptions import BotError

logger = logging.getLogger(__name__)

class BaseTelegramHandler:
    """Telegram Bot 基礎處理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化處理器
        
        Args:
            config: 配置參數
        """
        self.config = config or {}
        self.application = None
        
    async def initialize(self) -> None:
        """初始化 Bot 應用
        
        Raises:
            BotError: 初始化失敗時拋出
        """
        try:
            token = self.config.get("token")
            if not token:
                raise BotError("Bot token is required")
                
            # 使用 ApplicationBuilder 進行更靈活的配置
            builder = ApplicationBuilder().token(token)
            
            # 添加可選的配置
            if self.config.get("proxy_url"):
                builder.proxy_url(self.config["proxy_url"])
            if self.config.get("connect_timeout"):
                builder.connect_timeout(self.config["connect_timeout"])
            if self.config.get("read_timeout"):
                builder.read_timeout(self.config["read_timeout"])
            if self.config.get("write_timeout"):
                builder.write_timeout(self.config["write_timeout"])
                
            self.application = builder.build()
            logger.info("Base Telegram handler initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize base handler: {e}", exc_info=True)
            raise BotError(f"Base handler initialization failed: {str(e)}")
            
    async def start(self) -> None:
        """啟動 Bot
        
        Raises:
            BotError: 啟動失敗時拋出
        """
        try:
            if not self.application:
                await self.initialize()
            await self.application.initialize()
            await self.application.start()
            await self.application.run_polling()
            logger.info("Base Telegram handler started")
        except Exception as e:
            logger.error(f"Failed to start base handler: {e}", exc_info=True)
            raise BotError(f"Base handler start failed: {str(e)}")
            
    async def stop(self) -> None:
        """停止 Bot
        
        Raises:
            BotError: 停止失敗時拋出
        """
        try:
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
                logger.info("Base Telegram handler stopped")
        except Exception as e:
            logger.error(f"Failed to stop base handler: {e}", exc_info=True)
            raise BotError(f"Base handler stop failed: {str(e)}")
            
    def get_application(self) -> Application:
        """獲取 Bot 應用實例
        
        Returns:
            Application: Bot 應用實例
            
        Raises:
            BotError: 應用未初始化時拋出
        """
        if not self.application:
            raise BotError("Application not initialized")
        return self.application 
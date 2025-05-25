#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram Bot 與 AutoFlow 整合示例
"""

import asyncio
import logging
from typing import Dict, Any
from autoflow.core import AutoFlow
from telegram_bot.bot import DataScoutBot
from telegram_bot.exceptions import BotError

# 設定日誌
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBotFlow(AutoFlow):
    """Telegram Bot 流程示例"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化流程
        
        Args:
            config: 配置參數
        """
        super().__init__()
        self.config = config or {}
        self.bot = None
        
    async def setup(self):
        """設置流程"""
        try:
            # 初始化 Bot
            self.bot = DataScoutBot(
                config=self.config,
                allowed_updates=["message", "callback_query"]  # 只處理消息和回調
            )
        except Exception as e:
            logger.error(f"Failed to setup bot: {e}", exc_info=True)
            raise
        
    async def start(self):
        """啟動流程"""
        try:
            if not self.bot:
                await self.setup()
                
            # 啟動 Bot
            await self.bot.start()
        except Exception as e:
            logger.error(f"Failed to start bot: {e}", exc_info=True)
            raise
        
    async def stop(self):
        """停止流程"""
        try:
            if self.bot:
                await self.bot.stop()
        except Exception as e:
            logger.error(f"Failed to stop bot: {e}", exc_info=True)
            raise
            
    async def handle_message(self, message: str) -> str:
        """處理消息
        
        Args:
            message: 輸入消息
            
        Returns:
            str: 處理結果
            
        Raises:
            BotError: 處理消息時發生錯誤
        """
        try:
            # 這裡可以添加自定義的消息處理邏輯
            return f"處理消息: {message}"
        except Exception as e:
            logger.error(f"Failed to handle message: {e}", exc_info=True)
            raise BotError(f"Message handling failed: {str(e)}")


async def main():
    """主函數"""
    # 創建流程實例
    flow = TelegramBotFlow({
        "custom_setting": "value",
        "proxy_url": "http://proxy.example.com:8080",  # 可選的代理設置
        "connect_timeout": 30,  # 連接超時
        "read_timeout": 30,     # 讀取超時
        "write_timeout": 30     # 寫入超時
    })
    
    try:
        # 啟動流程
        await flow.start()
        
        # 運行一段時間
        await asyncio.sleep(3600)  # 運行1小時
        
    except KeyboardInterrupt:
        logger.info("收到中斷信號")
    except Exception as e:
        logger.error(f"Flow error: {e}", exc_info=True)
    finally:
        # 停止流程
        await flow.stop()


if __name__ == "__main__":
    asyncio.run(main()) 
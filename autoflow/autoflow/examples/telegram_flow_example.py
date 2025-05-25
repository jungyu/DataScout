#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram Bot 流程使用示例
"""

import asyncio
import logging
from autoflow.flows.telegram_flow import TelegramFlow

# 設定日誌
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """主函數"""
    # 創建流程實例
    flow = TelegramFlow({
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
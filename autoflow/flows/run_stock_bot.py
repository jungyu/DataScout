#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票機器人啟動腳本

此腳本用於啟動股票行情查詢機器人。
它會：
1. 載入環境變數
2. 檢查必要的配置
3. 啟動機器人服務
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from autoflow.flows.stock_bot_flow import StockBotFlow

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """主程式"""
    try:
        # 載入環境變數（從專案根目錄）
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))
        
        # 檢查必要的環境變數
        required_env_vars = [
            'TELEGRAM_BOT_TOKEN',
            'SUPABASE_URL',
            'SUPABASE_KEY'
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"缺少必要的環境變數：{', '.join(missing_vars)}")
        
        # 創建並啟動工作流程
        flow = StockBotFlow()
        logger.info("正在啟動股票機器人...")
        await flow.start()
        
        # 保持程式運行
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("正在關閉股票機器人...")
    except Exception as e:
        logger.error(f"運行時發生錯誤：{str(e)}")
        raise
    finally:
        # 清理資源
        if 'flow' in locals():
            await flow.stop()

if __name__ == "__main__":
    asyncio.run(main()) 
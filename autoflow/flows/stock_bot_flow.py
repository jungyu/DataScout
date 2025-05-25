#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票行情查詢機器人工作流程

此工作流程實現了以下功能：
1. 接收 Telegram 用戶的股票查詢請求
2. 使用 yfinance 獲取股票數據
3. 將數據存儲到 Supabase
4. 生成圖表並返回結果
5. 記錄用戶對話歷史
"""

from typing import Dict, Any, Optional
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import os
import asyncio
import logging
from dotenv import load_dotenv

# 修改導入路徑為相對路徑
from ..core.flow import Flow
from ..services.telegram import TelegramService
from ..services.supabase import SupabaseService
from ..services.web import WebService

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StockBotFlow(Flow):
    """股票行情查詢機器人工作流程"""
    
    def __init__(self):
        super().__init__()
        self.telegram = TelegramService()
        self.supabase = SupabaseService()
        self.web = WebService()
        
    async def handle_message(self, message: Dict[str, Any]) -> None:
        """處理用戶消息"""
        # 獲取用戶信息
        user = await self._get_or_create_user(message)
        if not user:
            await self.telegram.send_message(
                chat_id=message['chat']['id'],
                text="無法創建或獲取用戶信息，請稍後再試。"
            )
            return

        # 解析股票代碼
        symbol = message.get('text', '').strip().upper()
        if not symbol:
            response = "請輸入股票代碼，例如：AAPL"
            await self.telegram.send_message(
                chat_id=message['chat']['id'],
                text=response
            )
            # 記錄對話
            await self._log_conversation(user['id'], message.get('text', ''), response)
            return
            
        try:
            # 獲取股票數據
            stock_data = await self._fetch_stock_data(symbol)
            
            # 存儲數據
            await self._store_data(symbol, stock_data)
            
            # 生成圖表
            chart_url = await self._generate_chart(symbol)
            
            # 準備回應消息
            response = await self._prepare_response(symbol, stock_data, chart_url)
            
            # 發送結果
            await self.telegram.send_message(
                chat_id=message['chat']['id'],
                text=response
            )
            
            # 記錄對話
            await self._log_conversation(user['id'], symbol, response)
            
        except Exception as e:
            error_message = f"處理請求時發生錯誤：{str(e)}"
            await self.telegram.send_message(
                chat_id=message['chat']['id'],
                text=error_message
            )
            # 記錄錯誤對話
            await self._log_conversation(user['id'], symbol, error_message)
    
    async def _get_or_create_user(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """獲取或創建用戶"""
        try:
            # 獲取用戶信息
            telegram_id = message['from']['id']
            username = message['from'].get('username')
            first_name = message['from'].get('first_name')
            last_name = message['from'].get('last_name')
            
            # 查詢用戶是否存在
            user = await self.supabase.get_user(telegram_id)
            
            if not user:
                # 創建新用戶
                user = await self.supabase.create_user(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
            
            return user
        except Exception as e:
            self.logger.error(f"獲取或創建用戶時發生錯誤：{str(e)}")
            return None
    
    async def _log_conversation(self, user_id: str, message: str, response: str) -> None:
        """記錄對話"""
        try:
            await self.supabase.create_conversation(
                user_id=user_id,
                message=message,
                response=response
            )
        except Exception as e:
            self.logger.error(f"記錄對話時發生錯誤：{str(e)}")
    
    async def _prepare_response(self, symbol: str, data: pd.DataFrame, chart_url: str) -> str:
        """準備回應消息"""
        latest = data.iloc[-1]
        return (
            f"📊 {symbol} 股票行情\n\n"
            f"最新價格：${latest['Close']:.2f}\n"
            f"開盤價：${latest['Open']:.2f}\n"
            f"最高價：${latest['High']:.2f}\n"
            f"最低價：${latest['Low']:.2f}\n"
            f"成交量：{latest['Volume']:,}\n\n"
            f"查看詳細圖表：{chart_url}"
        )
    
    async def _fetch_stock_data(self, symbol: str) -> pd.DataFrame:
        """獲取股票數據"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        stock = yf.Ticker(symbol)
        data = stock.history(start=start_date, end=end_date)
        return data
    
    async def _store_data(self, symbol: str, data: pd.DataFrame) -> None:
        """存儲數據到 Supabase"""
        records = data.reset_index().to_dict('records')
        await self.supabase.create('stock_data', {
            'symbol': symbol,
            'data': records,
            'timestamp': datetime.now().isoformat()
        })
    
    async def _generate_chart(self, symbol: str) -> str:
        """生成圖表"""
        return await self.web.generate_chart(symbol)

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
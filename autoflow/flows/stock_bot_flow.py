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
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from autoflow.core.flow import Flow
from autoflow.services.telegram import TelegramService
from autoflow.services.supabase import SupabaseService
from autoflow.services.web import WebService

# 配置日誌
log_file = os.path.join(project_root, 'stock_bot.log')
logging.basicConfig(
    level=logging.DEBUG,  # 設置為 DEBUG 級別以獲取更詳細的日誌
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, encoding='utf-8', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# 設置其他模組的日誌級別
logging.getLogger('autoflow.services.telegram').setLevel(logging.DEBUG)
logging.getLogger('autoflow.services.supabase').setLevel(logging.DEBUG)
logging.getLogger('autoflow.services.web').setLevel(logging.DEBUG)

class StockBotFlow(Flow):
    """股票行情查詢機器人工作流程"""
    
    def __init__(self):
        super().__init__()
        self.telegram = TelegramService()
        self.supabase = SupabaseService()
        self.web = WebService()
        self.logger = logger
        
    async def start(self):
        """啟動工作流程"""
        try:
            # 先連接 Supabase
            await self.supabase.connect()
            self.logger.info("Supabase 服務已連接")
            
            # 啟動 Telegram 服務並獲取機器人信息
            bot_info = await self.telegram.start()
            self.logger.info("Telegram 服務已啟動")
            
            # 記錄機器人信息到 Supabase
            try:
                bot_data = {
                    'bot_id': bot_info['id'],
                    'username': bot_info['username'],
                    'first_name': bot_info['first_name'],
                    'is_bot': bot_info['is_bot'],
                    'can_join_groups': bot_info.get('can_join_groups', False),
                    'can_read_all_group_messages': bot_info.get('can_read_all_group_messages', False),
                    'supports_inline_queries': bot_info.get('supports_inline_queries', False),
                    'created_at': datetime.now().isoformat(),
                    'status': 'active'
                }
                
                # 檢查機器人是否已存在
                existing_bot = await self.supabase.get_bot(bot_info['id'])
                if existing_bot:
                    # 更新現有機器人信息
                    await self.supabase.update_bot(bot_info['id'], bot_data)
                    self.logger.info(f"已更新機器人信息：{bot_info['username']}")
                else:
                    # 創建新機器人記錄
                    await self.supabase.create('bots', bot_data)
                    self.logger.info(f"已記錄新機器人信息：{bot_info['username']}")
            except Exception as e:
                self.logger.error(f"記錄機器人信息時發生錯誤：{str(e)}")
                # 不中斷主流程，繼續啟動其他服務
            
            # 啟動 Web 服務
            await self.web.start()
            self.logger.info("Web 服務已啟動")
            
        except Exception as e:
            self.logger.error(f"啟動服務時發生錯誤：{str(e)}")
            # 嘗試清理資源
            try:
                await self.stop()
            except:
                pass
            raise

    async def stop(self):
        """停止工作流程"""
        try:
            await self.telegram.stop()
            await self.supabase.disconnect()
            await self.web.stop()
            self.logger.info("所有服務已停止")
        except Exception as e:
            self.logger.error(f"停止服務時發生錯誤：{str(e)}")
            raise

    async def handle_message(self, message: Dict[str, Any]) -> None:
        """處理用戶消息"""
        try:
            # 獲取用戶信息
            user = await self._get_or_create_user(message)
            if not user:
                self.logger.error("無法獲取或創建用戶")
                await self.telegram.send_message(
                    chat_id=message['chat']['id'],
                    text="無法創建或獲取用戶信息，請稍後再試。"
                )
                return

            self.logger.info(f"成功獲取用戶信息：{user['id']}")

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
                self.logger.info(f"正在獲取股票數據：{symbol}")
                stock_data = await self._fetch_stock_data(symbol)
                
                # 存儲數據
                self.logger.info(f"正在存儲股票數據：{symbol}")
                await self._store_data(symbol, stock_data)
                
                # 生成圖表
                self.logger.info(f"正在生成圖表：{symbol}")
                chart_url = await self._generate_chart(symbol)
                
                # 準備回應消息
                response = await self._prepare_response(symbol, stock_data, chart_url)
                
                # 發送結果
                await self.telegram.send_message(
                    chat_id=message['chat']['id'],
                    text=response
                )
                
                # 記錄對話
                self.logger.info(f"正在記錄對話：{symbol}")
                await self._log_conversation(user['id'], symbol, response)
                
            except Exception as e:
                error_message = f"處理請求時發生錯誤：{str(e)}"
                self.logger.error(f"處理股票請求時發生錯誤：{str(e)}")
                await self.telegram.send_message(
                    chat_id=message['chat']['id'],
                    text=error_message
                )
                # 記錄錯誤對話
                await self._log_conversation(user['id'], symbol, error_message)
        except Exception as e:
            self.logger.error(f"處理消息時發生錯誤：{str(e)}")
            raise

    async def _get_or_create_user(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """獲取或創建用戶
        
        Args:
            message: Telegram 消息對象
            
        Returns:
            Optional[Dict[str, Any]]: 用戶信息字典，如果失敗則返回 None
        """
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
                user_data = {
                    'telegram_id': telegram_id,
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'created_at': datetime.now().isoformat(),
                    'last_active': datetime.now().isoformat(),
                    'status': 'active'
                }
                
                user = await self.supabase.create('users', user_data)
                self.logger.info(f"已創建新用戶：{telegram_id}")
            else:
                # 更新用戶最後活動時間
                await self.supabase.update_user(
                    telegram_id=telegram_id,
                    last_active=datetime.now().isoformat()
                )
                self.logger.info(f"已更新用戶活動時間：{telegram_id}")
            
            return user
            
        except Exception as e:
            self.logger.error(f"獲取或創建用戶時發生錯誤：{str(e)}")
            return None
    
    async def _log_conversation(self, user_id: str, message: str, response: str) -> None:
        """記錄用戶對話歷史
        
        Args:
            user_id: 用戶 ID
            message: 用戶發送的消息
            response: 機器人的回應
        """
        try:
            # 準備對話數據
            conversation_data = {
                'user_id': user_id,
                'message': message,
                'response': response,
                'message_type': 'stock_query',
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            self.logger.info(f"準備記錄對話：user_id={user_id}, message={message[:50]}...")
            
            # 記錄對話
            result = await self.supabase.create('conversations', conversation_data)
            if not result:
                raise ValueError("Supabase 返回空結果")
                
            self.logger.info(f"已記錄用戶 {user_id} 的對話歷史，ID：{result.get('id')}")
            
        except Exception as e:
            self.logger.error(f"記錄對話歷史時發生錯誤：{str(e)}, 數據：{conversation_data}")
            # 不中斷主流程，只記錄錯誤
            pass
    
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
        """將股票數據存儲到 Supabase
        
        Args:
            symbol: 股票代碼
            data: 股票數據 DataFrame
        """
        try:
            if data.empty:
                self.logger.warning(f"沒有數據可存儲：{symbol}")
                return

            # 準備數據
            records = []
            for index, row in data.iterrows():
                record = {
                    'symbol': symbol,
                    'date': index.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume']),
                    'timestamp': datetime.now().isoformat()
                }
                records.append(record)
            
            self.logger.info(f"準備存儲 {len(records)} 條記錄")
            
            # 批量插入數據
            for record in records:
                try:
                    result = await self.supabase.create('stock_data', record)
                    self.logger.debug(f"成功存儲記錄：{record['date']}")
                except Exception as e:
                    self.logger.error(f"存儲記錄時發生錯誤：{str(e)}, 記錄：{record}")
                    raise
            
            self.logger.info(f"已成功存儲 {symbol} 的股票數據")
            
        except Exception as e:
            self.logger.error(f"存儲股票數據時發生錯誤：{str(e)}")
            raise
    
    async def _generate_chart(self, symbol: str) -> str:
        """生成圖表"""
        return await self.web.generate_chart(symbol)

async def main():
    """主程式"""
    try:
        # 載入環境變數（從專案根目錄）
        env_path = os.path.join(project_root, '.env')
        if not os.path.exists(env_path):
            raise FileNotFoundError(f"找不到環境變數檔案：{env_path}")
        
        load_dotenv(dotenv_path=env_path)
        
        # 檢查必要的環境變數
        required_env_vars = {
            'TELEGRAM_BOT_TOKEN': 'Telegram 機器人令牌',
            'SUPABASE_URL': 'Supabase 專案 URL',
            'SUPABASE_KEY': 'Supabase API 金鑰',
            'WEB_SERVICE_URL': 'Web 服務 URL'
        }
        
        missing_vars = [var for var, desc in required_env_vars.items() if not os.getenv(var)]
        if missing_vars:
            missing_desc = [f"{var} ({required_env_vars[var]})" for var in missing_vars]
            raise ValueError(f"缺少必要的環境變數：{', '.join(missing_desc)}")
        
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
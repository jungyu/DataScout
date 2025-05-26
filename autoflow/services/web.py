#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web 服務模組

此模組提供網頁相關功能，如生成圖表等
"""

import logging
import aiohttp
from typing import Dict, Any, Optional
from autoflow.core.config import Config

logger = logging.getLogger(__name__)

class WebService:
    """Web 服務類別"""
    
    def __init__(self):
        """初始化 Web 服務"""
        self.config = Config()
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logger
    
    async def start(self) -> None:
        """啟動 Web 服務"""
        try:
            # 驗證配置
            self.config.validate()
            
            # 創建 HTTP 會話
            self.session = aiohttp.ClientSession()
            
            self.logger.info("Web 服務已啟動")
        except Exception as e:
            self.logger.error(f"啟動 Web 服務時發生錯誤：{str(e)}")
            raise
    
    async def stop(self) -> None:
        """停止 Web 服務"""
        try:
            if self.session:
                await self.session.close()
                self.session = None
                self.logger.info("Web 服務已停止")
        except Exception as e:
            self.logger.error(f"停止 Web 服務時發生錯誤：{str(e)}")
            raise
    
    async def generate_chart(self, symbol: str) -> str:
        """生成股票圖表"""
        try:
            if not self.session:
                raise RuntimeError("Web 服務尚未啟動")
            
            # 構建請求 URL
            url = f"{self.config.web_service_url}/api/charts"
            params = {
                'symbol': symbol,
                'period': self.config.default_stock_period
            }
            
            # 發送請求
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    raise RuntimeError(f"生成圖表失敗：HTTP {response.status}")
                
                data = await response.json()
                return data.get('chart_url', '')
        except Exception as e:
            self.logger.error(f"生成圖表時發生錯誤：{str(e)}")
            raise 
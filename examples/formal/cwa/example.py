#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中央氣象局 API 示例
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from .config import CWAConfig
from .client import CWAClient
from .services import EarthquakeService

async def main():
    """主程式"""
    # 載入環境變數
    load_dotenv()
    
    # 從環境變數獲取 API 金鑰
    api_key = os.getenv("CWA_API_KEY")
    if not api_key:
        print("錯誤: 未設置 CWA_API_KEY 環境變數")
        print("請複製 .env.example 為 .env 並設置您的 API 金鑰")
        return
    
    # 建立 API 配置
    config = CWAConfig(api_key=api_key)
    
    # 建立 API 客戶端
    client = CWAClient(config)
    
    # 建立地震服務
    earthquake_service = EarthquakeService(client)
    
    # 範例 1: 取得最近的地震資料
    print("正在取得最近的地震資料...")
    recent_data = await earthquake_service.get_recent_earthquakes(limit=5)
    earthquake_service.display_earthquake_summary(recent_data)
    
    # 範例 2: 取得特定地區的地震
    print("\n正在取得花蓮縣和宜蘭縣的地震...")
    area_data = await earthquake_service.get_earthquakes_by_area(
        area_names=["花蓮縣", "宜蘭縣"],
        limit=3
    )
    earthquake_service.display_earthquake_summary(area_data)
    
    # 範例 3: 取得特定時間範圍內的地震
    print("\n正在取得特定時間範圍內的地震...")
    # 以上個月為例
    last_month = datetime.now().replace(month=datetime.now().month-1 if datetime.now().month > 1 else 12)
    time_from = last_month.strftime("%Y-%m-%dT00:00:00")
    time_data = await earthquake_service.get_earthquakes_by_time_range(
        time_from=time_from,
        limit=3
    )
    earthquake_service.display_earthquake_summary(time_data)
    
    # 範例 4: 取得特定測站的地震
    print("\n正在取得特定測站的地震...")
    station_data = await earthquake_service.get_earthquakes_by_station(
        station_names=["台北", "花蓮"],
        limit=3
    )
    earthquake_service.display_earthquake_summary(station_data)

if __name__ == "__main__":
    asyncio.run(main()) 
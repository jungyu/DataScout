#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中央氣象局 API 示例主程式
"""

import asyncio
import os
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .config import CWAConfig
from .client import CWAClient
from .services import EarthquakeService, RainfallService, TyphoonService, ForecastService, ObservationService, TownshipForecastService

async def run_earthquake_example(client: CWAClient, args):
    """執行地震示例"""
    print("執行地震資料示例...")
    earthquake_service = EarthquakeService(client)
    
    if args.time_range:
        # 取得特定時間範圍的地震資料
        print(f"\n正在取得 {args.time_range} 時間範圍內的地震資料...")
        time_data = await earthquake_service.get_earthquakes_by_time_range(
            time_from=args.time_range[0],
            time_to=args.time_range[1],
            limit=args.limit
        )
        earthquake_service.display_earthquake_summary(time_data)
    
    if args.area:
        # 取得特定地區的地震資料
        print(f"\n正在取得 {args.area} 地區的地震資料...")
        area_data = await earthquake_service.get_earthquakes_by_area(
            area_names=args.area,
            limit=args.limit
        )
        earthquake_service.display_earthquake_summary(area_data)
    
    if not args.time_range and not args.area:
        # 取得最近地震資料
        print("\n正在取得最近地震資料...")
        recent_data = await earthquake_service.get_recent_earthquakes(limit=args.limit)
        earthquake_service.display_earthquake_summary(recent_data)

async def run_rainfall_example(client: CWAClient, args):
    """執行雨量示例"""
    print("執行雨量資料示例...")
    rainfall_service = RainfallService(client)
    
    if args.station:
        # 取得特定測站的雨量資料
        print(f"\n正在取得測站 {args.station} 的雨量資料...")
        station_data = await rainfall_service.get_rainfall_by_station(
            station_ids=args.station,
            limit=args.limit
        )
        rainfall_service.display_rainfall_summary(station_data)
    
    if args.time_range:
        # 取得特定時間範圍的雨量資料
        print(f"\n正在取得 {args.time_range} 時間範圍內的雨量資料...")
        time_data = await rainfall_service.get_rainfall_by_date_range(
            time_from=args.time_range[0],
            time_to=args.time_range[1],
            limit=args.limit
        )
        rainfall_service.display_rainfall_summary(time_data)
    
    if args.monthly:
        # 取得每月雨量統計值
        print("\n正在取得每月雨量統計值...")
        stats_data = await rainfall_service.get_monthly_statistics(
            station_ids=args.station or ["466881", "466900"]
        )
        rainfall_service.display_rainfall_summary(stats_data)
    
    if not args.station and not args.time_range and not args.monthly:
        # 取得所有測站的雨量資料
        print("\n正在取得所有測站的雨量資料...")
        all_data = await rainfall_service.get_rainfall_by_station(
            station_ids=["466881", "466900"],
            limit=args.limit
        )
        rainfall_service.display_rainfall_summary(all_data)

async def run_typhoon_example(client: CWAClient, args):
    """執行颱風示例"""
    print("執行颱風資料示例...")
    typhoon_service = TyphoonService(client)
    
    if args.typhoon_no:
        # 取得特定編號的颱風資料
        print(f"\n正在取得編號 {args.typhoon_no} 的颱風資料...")
        typhoon_data = await typhoon_service.get_typhoon_by_number(cwa_td_no=args.typhoon_no)
        typhoon_service.display_typhoon_summary(typhoon_data)
    
    if args.forecast:
        # 取得特定颱風的預報資料
        print(f"\n正在取得編號 {args.typhoon_no or '當前'} 颱風的預報資料...")
        forecast_data = await typhoon_service.get_typhoon_forecast(
            cwa_td_no=args.typhoon_no,
            tau=args.forecast_hours
        )
        typhoon_service.display_typhoon_summary(forecast_data)
    
    if args.time_range:
        # 取得特定時間範圍的颱風資料
        print(f"\n正在取得 {args.time_range} 時間範圍內的颱風資料...")
        history_data = await typhoon_service.get_typhoon_history(
            cwa_td_no=args.typhoon_no,
            time_from=args.time_range[0],
            time_to=args.time_range[1]
        )
        typhoon_service.display_typhoon_summary(history_data)
    
    if not args.typhoon_no and not args.forecast and not args.time_range:
        # 取得目前活動中的颱風資料
        print("\n正在取得目前活動中的颱風資料...")
        current_data = await typhoon_service.get_current_typhoons(limit=args.limit)
        typhoon_service.display_typhoon_summary(current_data)

async def run_forecast_example(client: CWAClient, args):
    """執行未來天氣預報示例"""
    print("執行未來天氣預報示例...")
    forecast_service = ForecastService(client)
    
    if args.location:
        # 取得特定縣市的未來天氣預報
        print(f"\n正在取得 {args.location} 的未來天氣預報...")
        location_data = await forecast_service.get_forecast_by_location(
            location_name=args.location,
            limit=args.limit
        )
        forecast_service.display_forecast_summary(location_data)
    
    if args.time_range:
        # 取得特定時間範圍的未來天氣預報
        print(f"\n正在取得 {args.time_range} 時間範圍內的未來天氣預報...")
        time_data = await forecast_service.get_forecast_by_date_range(
            time_from=args.time_range[0],
            time_to=args.time_range[1],
            limit=args.limit
        )
        forecast_service.display_forecast_summary(time_data)
    
    if args.element:
        # 取得特定天氣因子的未來天氣預報
        print(f"\n正在取得 {args.element} 天氣因子的未來天氣預報...")
        element_data = await forecast_service.get_forecast_by_element(
            element_name=args.element,
            limit=args.limit
        )
        forecast_service.display_forecast_summary(element_data)
    
    if not args.location and not args.time_range and not args.element:
        # 取得所有縣市的未來天氣預報
        print("\n正在取得所有縣市的未來天氣預報...")
        all_data = await forecast_service.get_forecast_data(limit=args.limit)
        forecast_service.display_forecast_summary(all_data)

async def run_observation_example(client: CWAClient, args):
    """執行氣象觀測示例"""
    print("執行氣象觀測示例...")
    observation_service = ObservationService(client)
    
    if args.station:
        # 取得特定測站的氣象觀測資料
        print(f"\n正在取得測站 {args.station} 的氣象觀測資料...")
        station_data = await observation_service.get_observation_by_station(
            station_id=args.station,
            limit=args.limit
        )
        observation_service.display_observation_summary(station_data)
    
    if args.station_name:
        # 取得特定測站名稱的氣象觀測資料
        print(f"\n正在取得測站名稱 {args.station_name} 的氣象觀測資料...")
        station_name_data = await observation_service.get_observation_by_station_name(
            station_name=args.station_name,
            limit=args.limit
        )
        observation_service.display_observation_summary(station_name_data)
    
    if args.element:
        # 取得特定氣象因子的觀測資料
        print(f"\n正在取得 {args.element} 氣象因子的觀測資料...")
        element_data = await observation_service.get_observation_by_weather_element(
            weather_element=args.element,
            limit=args.limit
        )
        observation_service.display_observation_summary(element_data)
    
    if args.county:
        # 取得特定縣市的氣象觀測資料
        print(f"\n正在取得 {args.county} 縣市的氣象觀測資料...")
        county_data = await observation_service.get_observation_by_county(
            county_name=args.county,
            limit=args.limit
        )
        observation_service.display_observation_summary(county_data)
    
    if not args.station and not args.station_name and not args.element and not args.county:
        # 取得所有測站的氣象觀測資料
        print("\n正在取得所有測站的氣象觀測資料...")
        all_data = await observation_service.get_observation_data(limit=args.limit)
        observation_service.display_observation_summary(all_data)

async def run_township_forecast_example(client: CWAClient, args):
    """執行全台各鄉鎮天氣預報示例"""
    print("執行全台各鄉鎮天氣預報示例...")
    township_forecast_service = TownshipForecastService(client)
    
    if args.location_id:
        # 取得特定鄉鎮市區的天氣預報
        print(f"\n正在取得鄉鎮市區編號 {args.location_id} 的天氣預報...")
        location_data = await township_forecast_service.get_forecast_by_location(
            location_id=args.location_id,
            elements=args.elements,
            time_from=args.time_from,
            time_to=args.time_to,
            limit=args.limit
        )
        township_forecast_service.display_forecast_summary(location_data)
    
    if args.location_name:
        # 取得特定鄉鎮市區名稱的天氣預報
        print(f"\n正在取得鄉鎮市區名稱 {args.location_name} 的天氣預報...")
        location_name_data = await township_forecast_service.get_forecast_by_location_name(
            location_name=args.location_name,
            elements=args.elements,
            time_from=args.time_from,
            time_to=args.time_to,
            limit=args.limit
        )
        township_forecast_service.display_forecast_summary(location_name_data)
    
    if args.time_range:
        # 取得特定時間範圍的天氣預報
        print(f"\n正在取得 {args.time_range} 時間範圍內的天氣預報...")
        time_data = await township_forecast_service.get_forecast_by_time_range(
            location_ids=args.location_ids,
            location_names=args.location_names,
            elements=args.elements,
            days=args.days,
            limit=args.limit
        )
        township_forecast_service.display_forecast_summary(time_data)
    
    if not args.location_id and not args.location_name and not args.time_range:
        # 取得臺北市的天氣預報
        print("\n正在取得臺北市的天氣預報...")
        default_data = await township_forecast_service.get_forecast_by_location(
            location_id="F-D0047-001",
            limit=args.limit
        )
        township_forecast_service.display_forecast_summary(default_data)

async def main():
    """主程式"""
    # 解析命令行參數
    parser = argparse.ArgumentParser(description="中央氣象局 API 示例程式")
    parser.add_argument("-method", choices=["earthquake", "rainfall", "typhoon", "forecast", "observation", "township_forecast"], required=True,
                      help="選擇要執行的功能：earthquake（地震）、rainfall（雨量）、typhoon（颱風）、forecast（未來天氣預報）、observation（氣象觀測）或 township_forecast（全台各鄉鎮天氣預報）")
    
    # 通用參數
    parser.add_argument("-limit", type=int, default=5, help="限制返回的資料筆數")
    parser.add_argument("-time_range", nargs=2, metavar=("FROM", "TO"), help="時間範圍，格式：YYYY-MM-DD YYYY-MM-DD")
    
    # 地震相關參數
    parser.add_argument("-area", nargs="+", help="地區名稱，可指定多個")
    
    # 雨量相關參數
    parser.add_argument("-station", nargs="+", help="測站編號，可指定多個")
    parser.add_argument("-monthly", action="store_true", help="是否取得每月統計值")
    
    # 颱風相關參數
    parser.add_argument("-typhoon_no", type=int, help="颱風編號")
    parser.add_argument("-forecast", action="store_true", help="是否取得預報資料")
    parser.add_argument("-forecast_hours", type=int, nargs="+", default=[6, 12, 24, 48, 72], help="預報時距（小時）")
    
    # 天氣預報相關參數
    parser.add_argument("-location", help="縣市名稱")
    parser.add_argument("-element", help="天氣因子名稱")
    
    # 氣象觀測相關參數
    parser.add_argument("-station_name", help="測站名稱")
    parser.add_argument("-county", help="縣市名稱")
    
    # 全台各鄉鎮天氣預報相關參數
    parser.add_argument("-location_id", help="鄉鎮市區預報資料之資料項編號")
    parser.add_argument("-location_ids", nargs="+", help="鄉鎮市區預報資料之資料項編號列表，最多五個")
    parser.add_argument("-location_name", help="鄉鎮市區名稱")
    parser.add_argument("-location_names", nargs="+", help="鄉鎮市區名稱列表")
    parser.add_argument("-elements", nargs="+", help="天氣預報天氣因子列表")
    parser.add_argument("-time_from", help="時間區段起始時間，格式為「yyyy-MM-ddThh:mm:ss」")
    parser.add_argument("-time_to", help="時間區段結束時間，格式為「yyyy-MM-ddThh:mm:ss」")
    parser.add_argument("-days", type=int, default=7, help="要查詢的天數，預設為 7 天")
    
    args = parser.parse_args()
    
    # 載入環境變數
    load_dotenv()
    
    # 從環境變數獲取 API 金鑰
    api_key = os.getenv("CWA_API_KEY")
    if not api_key:
        print("錯誤: 未設置 CWA_API_KEY 環境變數")
        print("請複製 .env.example 為 .env 並設置您的 API 金鑰")
        return
    
    try:
        # 建立 API 配置
        config = CWAConfig(api_key=api_key)
        
        # 建立 API 客戶端
        client = CWAClient(config)
        
        # 根據選擇的方法執行相應的示例
        if args.method == "earthquake":
            await run_earthquake_example(client, args)
        elif args.method == "rainfall":
            await run_rainfall_example(client, args)
        elif args.method == "typhoon":
            await run_typhoon_example(client, args)
        elif args.method == "forecast":
            await run_forecast_example(client, args)
        elif args.method == "observation":
            await run_observation_example(client, args)
        elif args.method == "township_forecast":
            await run_township_forecast_example(client, args)
    except Exception as e:
        print(f"執行時發生錯誤: {str(e)}")
        return

if __name__ == "__main__":
    asyncio.run(main()) 
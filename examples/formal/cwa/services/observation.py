#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中央氣象局氣象觀測服務
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from ..client import CWAClient

class ObservationService:
    """氣象觀測服務類"""
    
    def __init__(self, client: CWAClient):
        """初始化氣象觀測服務
        
        Args:
            client: CWA API 客戶端
        """
        self.client = client
        self.dataset_id = "O-A0001-001"  # 氣象觀測資料集 ID
    
    async def get_observation_data(self,
                                 limit: Optional[int] = None,
                                 offset: Optional[int] = None,
                                 format: str = "JSON",
                                 station_ids: Optional[List[str]] = None,
                                 station_names: Optional[List[str]] = None,
                                 weather_elements: Optional[List[str]] = None,
                                 geo_info: Optional[List[str]] = None) -> Dict[str, Any]:
        """獲取氣象觀測資料
        
        Args:
            limit: 限制筆數
            offset: 起始位置
            format: 回傳格式
            station_ids: 測站站號列表
            station_names: 測站站名列表
            weather_elements: 氣象因子列表，可為 "Weather"（天氣現象）、"Now"（現在天氣）、"WindDirection"（風向）、"WindSpeed"（風速）、"AirTemperature"（氣溫）、"RelativeHumidity"（相對濕度）、"AirPressure"（氣壓）、"UVIndex"（紫外線指數）、"PeakGustSpeed"（陣風風速）
            geo_info: 地理資訊列表，可為 "Coordinates"（座標）、"StationAltitude"（測站高度）、"CountyName"（縣市名稱）、"TownName"（鄉鎮市區名稱）、"CountyCode"（縣市代碼）、"TownCode"（鄉鎮市區代碼）
            
        Returns:
            Dict[str, Any]: API 回應
        """
        # 構建查詢參數
        params = {}
        
        # 加入選用參數
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if format:
            params["format"] = format
        
        # 處理列表參數
        if station_ids:
            params["StationId"] = station_ids
        if station_names:
            params["StationName"] = station_names
        if weather_elements:
            params["WeatherElement"] = weather_elements
        if geo_info:
            params["GeoInfo"] = geo_info
        
        # 發送請求
        return await self.client.get_data(self.dataset_id, **params)
    
    async def get_observation_by_station(self, station_id: str, limit: int = 10) -> Dict[str, Any]:
        """獲取特定測站的氣象觀測資料
        
        Args:
            station_id: 測站站號
            limit: 限制筆數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.get_observation_data(station_ids=[station_id], limit=limit)
    
    async def get_observation_by_station_name(self, station_name: str, limit: int = 10) -> Dict[str, Any]:
        """獲取特定測站名稱的氣象觀測資料
        
        Args:
            station_name: 測站站名
            limit: 限制筆數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.get_observation_data(station_names=[station_name], limit=limit)
    
    async def get_observation_by_weather_element(self, weather_element: str, limit: int = 10) -> Dict[str, Any]:
        """獲取特定氣象因子的觀測資料
        
        Args:
            weather_element: 氣象因子
            limit: 限制筆數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.get_observation_data(weather_elements=[weather_element], limit=limit)
    
    async def get_observation_by_county(self, county_name: str, limit: int = 10) -> Dict[str, Any]:
        """獲取特定縣市的氣象觀測資料
        
        Args:
            county_name: 縣市名稱
            limit: 限制筆數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.get_observation_data(geo_info=["CountyName"], limit=limit)
    
    def display_observation_summary(self, data: Dict[str, Any]) -> None:
        """顯示氣象觀測摘要
        
        Args:
            data: API 回應資料
        """
        if not data.get("success"):
            print(f"API 錯誤: {data.get('message', '未知錯誤')}")
            return
        
        records = data.get("records", {})
        stations = records.get("Station", [])
        
        if not stations:
            print("找不到氣象觀測資料。")
            return
        
        print(f"找到 {len(stations)} 個測站的氣象觀測資料:")
        print("-" * 80)
        
        for station in stations:
            station_name = station.get("StationName", "未知測站")
            station_id = station.get("StationId", "未知站號")
            obs_time = station.get("ObsTime", {}).get("DateTime", "未知時間")
            
            print(f"測站: {station_name} ({station_id})")
            print(f"觀測時間: {obs_time}")
            
            # 顯示地理資訊
            geo_info = station.get("GeoInfo", {})
            if geo_info:
                county_name = geo_info.get("CountyName", "未知縣市")
                town_name = geo_info.get("TownName", "未知鄉鎮")
                station_altitude = geo_info.get("StationAltitude", "未知高度")
                
                print(f"位置: {county_name}{town_name} (高度: {station_altitude}公尺)")
            
            # 顯示天氣要素
            weather_element = station.get("WeatherElement", {})
            if weather_element:
                weather = weather_element.get("Weather", "未知天氣")
                now = weather_element.get("Now", {})
                precipitation = now.get("Precipitation", "未知雨量")
                wind_direction = weather_element.get("WindDirection", "未知風向")
                wind_speed = weather_element.get("WindSpeed", "未知風速")
                air_temperature = weather_element.get("AirTemperature", "未知氣溫")
                relative_humidity = weather_element.get("RelativeHumidity", "未知濕度")
                air_pressure = weather_element.get("AirPressure", "未知氣壓")
                
                print(f"天氣: {weather}")
                print(f"雨量: {precipitation} 毫米")
                print(f"風向: {wind_direction} 度")
                print(f"風速: {wind_speed} 公尺/秒")
                print(f"氣溫: {air_temperature} 度")
                print(f"相對濕度: {relative_humidity} %")
                print(f"氣壓: {air_pressure} 百帕")
            
            print("-" * 80) 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中央氣象局雨量服務
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from ..client import CWAClient

class RainfallService:
    """雨量服務類"""
    
    def __init__(self, client: CWAClient):
        """初始化雨量服務
        
        Args:
            client: CWA API 客戶端
        """
        self.client = client
        self.dataset_id = "C-B0025-001"  # 每日雨量資料集 ID
    
    async def get_rainfall_data(self,
                              limit: Optional[int] = None,
                              offset: Optional[int] = None,
                              format: str = "JSON",
                              station_ids: Optional[List[str]] = None,
                              sort: Optional[List[str]] = None,
                              dates: Optional[List[str]] = None,
                              time_from: Optional[str] = None,
                              time_to: Optional[str] = None,
                              statistics: bool = False) -> Dict[str, Any]:
        """獲取雨量資料
        
        Args:
            limit: 限制筆數
            offset: 起始位置
            format: 回傳格式
            station_ids: 測站站號列表
            sort: 排序方式，可為 "time" 或 "dataTime"
            dates: 時間因子列表，格式為 "yyyy-MM-dd"
            time_from: 開始時間，格式為 "yyyy-MM-dd"
            time_to: 結束時間，格式為 "yyyy-MM-dd"
            statistics: 是否選取每月雨量統計值
            
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
            params["StationID"] = station_ids
        if sort:
            params["sort"] = sort
        if dates:
            params["Date"] = dates
        
        # 時間範圍參數
        if time_from:
            params["timeFrom"] = time_from
        if time_to:
            params["timeTo"] = time_to
        
        # 統計參數
        if statistics:
            params["statistics"] = "true"
        
        # 發送請求
        return await self.client.get_data(self.dataset_id, **params)
    
    async def get_rainfall_by_station(self, station_ids: List[str], limit: int = 10) -> Dict[str, Any]:
        """獲取特定測站的雨量資料
        
        Args:
            station_ids: 測站站號列表
            limit: 限制筆數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.get_rainfall_data(
            station_ids=station_ids,
            limit=limit
        )
    
    async def get_rainfall_by_date_range(self, time_from: str, time_to: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """獲取特定時間範圍內的雨量資料
        
        Args:
            time_from: 開始時間，格式為 "yyyy-MM-dd"
            time_to: 結束時間，格式為 "yyyy-MM-dd"
            limit: 限制筆數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.get_rainfall_data(
            time_from=time_from,
            time_to=time_to,
            limit=limit
        )
    
    async def get_monthly_statistics(self, station_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """獲取每月雨量統計值
        
        Args:
            station_ids: 測站站號列表
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.get_rainfall_data(
            station_ids=station_ids,
            statistics=True
        )
    
    def display_rainfall_summary(self, data: Dict[str, Any]) -> None:
        """顯示雨量資料摘要
        
        Args:
            data: API 回應資料
        """
        if not data.get("success"):
            print(f"API 錯誤: {data.get('message', '未知錯誤')}")
            return
        
        records = data.get("records", {})
        locations = records.get("location", [])
        
        if not locations:
            print("找不到雨量資料。")
            return
        
        print(f"找到 {len(locations)} 個測站的雨量記錄:")
        print("-" * 80)
        
        for location in locations:
            station = location.get("station", {})
            station_id = station.get("StationID", "N/A")
            station_name = station.get("StationName", "N/A")
            station_name_en = station.get("StationNameEN", "N/A")
            station_attribute = station.get("StationAttribute", "N/A")
            
            print(f"測站: {station_name} ({station_name_en})")
            print(f"測站編號: {station_id}")
            print(f"測站屬性: {station_attribute}")
            
            # 顯示每日雨量
            station_obs_times = location.get("stationObsTimes", {})
            station_obs_time = station_obs_times.get("stationObsTime", [])
            
            if station_obs_time:
                print("\n每日雨量:")
                for obs in station_obs_time[:5]:  # 只顯示前 5 筆
                    date = obs.get("Date", "N/A")
                    precipitation = obs.get("weatherElements", {}).get("Precipitation", "N/A")
                    print(f"  {date}: {precipitation} mm")
                
                if len(station_obs_time) > 5:
                    print(f"  ... 還有 {len(station_obs_time) - 5} 筆記錄")
            
            # 顯示每月統計
            station_obs_statistics = location.get("stationObsStatistics", {})
            precipitation_stats = station_obs_statistics.get("Precipitation", {})
            monthly_stats = precipitation_stats.get("monthly", [])
            
            if monthly_stats:
                print("\n每月統計:")
                for stat in monthly_stats:
                    year_month = stat.get("YearMonth", "N/A")
                    total = stat.get("Total", "N/A")
                    print(f"  {year_month}: {total} mm")
            
            print("-" * 80) 
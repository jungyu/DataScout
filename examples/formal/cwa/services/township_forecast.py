"""
全台各鄉鎮天氣預報服務模組

此模組提供與中央氣象局全台各鄉鎮天氣預報 API 的互動功能。
"""

import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta

from ..client import CWAClient

logger = logging.getLogger(__name__)

class TownshipForecastService:
    """全台各鄉鎮天氣預報服務類別"""
    
    def __init__(self, client: CWAClient):
        """
        初始化全台各鄉鎮天氣預報服務
        
        Args:
            client: CWA API 客戶端實例
        """
        self.client = client
        self.dataset_id = "F-D0047-093"  # 全台各鄉鎮天氣預報資料集 ID
    
    def get_forecast(
        self,
        location_ids: Optional[List[str]] = None,
        location_names: Optional[List[str]] = None,
        elements: Optional[List[str]] = None,
        time_from: Optional[str] = None,
        time_to: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        取得全台各鄉鎮天氣預報資料
        
        Args:
            location_ids: 鄉鎮市區預報資料之資料項編號列表，最多五個，最少一個
            location_names: 各縣市所對應鄉鎮名稱列表
            elements: 天氣預報天氣因子列表
            time_from: 時間區段起始時間，格式為「yyyy-MM-ddThh:mm:ss」
            time_to: 時間區段結束時間，格式為「yyyy-MM-ddThh:mm:ss」
            limit: 限制最多回傳的資料筆數
            offset: 指定從第幾筆後開始回傳
            sort: 排序欄位，可為 StartTime、EndTime 或 DataTime
            
        Returns:
            天氣預報資料字典
        """
        params = {}
        
        # 處理必要參數
        if location_ids:
            params["locationId"] = ",".join(location_ids)
        
        # 處理選用參數
        if location_names:
            params["LocationName"] = ",".join(location_names)
        
        if elements:
            params["ElementName"] = ",".join(elements)
        
        if time_from:
            params["timeFrom"] = time_from
        
        if time_to:
            params["timeTo"] = time_to
        
        if limit:
            params["limit"] = limit
        
        if offset:
            params["offset"] = offset
        
        if sort:
            params["sort"] = sort
        
        # 發送 API 請求
        response = self.client.get_data(self.dataset_id, **params)
        
        return response
    
    def get_forecast_by_location(
        self,
        location_id: str,
        elements: Optional[List[str]] = None,
        time_from: Optional[str] = None,
        time_to: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        取得特定鄉鎮市區的天氣預報資料
        
        Args:
            location_id: 鄉鎮市區預報資料之資料項編號
            elements: 天氣預報天氣因子列表
            time_from: 時間區段起始時間，格式為「yyyy-MM-ddThh:mm:ss」
            time_to: 時間區段結束時間，格式為「yyyy-MM-ddThh:mm:ss」
            limit: 限制最多回傳的資料筆數
            
        Returns:
            天氣預報資料字典
        """
        return self.get_forecast(
            location_ids=[location_id],
            elements=elements,
            time_from=time_from,
            time_to=time_to,
            limit=limit
        )
    
    def get_forecast_by_location_name(
        self,
        location_name: str,
        elements: Optional[List[str]] = None,
        time_from: Optional[str] = None,
        time_to: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        取得特定鄉鎮市區名稱的天氣預報資料
        
        Args:
            location_name: 鄉鎮市區名稱
            elements: 天氣預報天氣因子列表
            time_from: 時間區段起始時間，格式為「yyyy-MM-ddThh:mm:ss」
            time_to: 時間區段結束時間，格式為「yyyy-MM-ddThh:mm:ss」
            limit: 限制最多回傳的資料筆數
            
        Returns:
            天氣預報資料字典
        """
        return self.get_forecast(
            location_names=[location_name],
            elements=elements,
            time_from=time_from,
            time_to=time_to,
            limit=limit
        )
    
    def get_forecast_by_time_range(
        self,
        location_ids: Optional[List[str]] = None,
        location_names: Optional[List[str]] = None,
        elements: Optional[List[str]] = None,
        days: int = 7,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        取得特定時間範圍的天氣預報資料
        
        Args:
            location_ids: 鄉鎮市區預報資料之資料項編號列表，最多五個，最少一個
            location_names: 各縣市所對應鄉鎮名稱列表
            elements: 天氣預報天氣因子列表
            days: 要查詢的天數，預設為 7 天
            limit: 限制最多回傳的資料筆數
            
        Returns:
            天氣預報資料字典
        """
        # 計算時間範圍
        now = datetime.now()
        time_from = now.strftime("%Y-%m-%dT%H:%M:%S")
        time_to = (now + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
        
        return self.get_forecast(
            location_ids=location_ids,
            location_names=location_names,
            elements=elements,
            time_from=time_from,
            time_to=time_to,
            limit=limit
        )
    
    def display_forecast_summary(self, forecast_data: Dict[str, Any]) -> None:
        """
        顯示天氣預報摘要
        
        Args:
            forecast_data: 天氣預報資料字典
        """
        if not forecast_data or "records" not in forecast_data or "Locations" not in forecast_data["records"]:
            print("無天氣預報資料")
            return
        
        locations = forecast_data["records"]["Locations"]
        
        for location in locations:
            location_name = location.get("LocationsName", "未知地區")
            print(f"\n{location_name}天氣預報:")
            
            for loc in location.get("Location", []):
                township_name = loc.get("LocationName", "未知鄉鎮")
                print(f"\n  {township_name}:")
                
                for element in loc.get("WeatherElement", []):
                    element_name = element.get("ElementName", "未知因子")
                    print(f"    {element_name}:")
                    
                    for time_data in element.get("Time", []):
                        start_time = time_data.get("StartTime", "")
                        end_time = time_data.get("EndTime", "")
                        
                        # 格式化時間顯示
                        try:
                            start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                            end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                            time_str = f"{start_dt.strftime('%Y-%m-%d %H:%M')} 至 {end_dt.strftime('%Y-%m-%d %H:%M')}"
                        except:
                            time_str = f"{start_time} 至 {end_time}"
                        
                        print(f"      {time_str}:")
                        
                        for value in time_data.get("ElementValue", []):
                            for key, val in value.items():
                                print(f"        {key}: {val}") 
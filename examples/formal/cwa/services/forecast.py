#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中央氣象局未來天氣預報（縣市）服務
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from ..client import CWAClient

class ForecastService:
    """未來天氣預報（縣市）服務類"""
    
    def __init__(self, client: CWAClient):
        """初始化未來天氣預報服務
        
        Args:
            client: CWA API 客戶端
        """
        self.client = client
        self.dataset_id = "F-C0032-001"  # 未來天氣預報（縣市）資料集 ID
    
    async def get_forecast_data(self,
                               limit: Optional[int] = None,
                               offset: Optional[int] = None,
                               format: str = "JSON",
                               location_name: Optional[List[str]] = None,
                               element_name: Optional[List[str]] = None,
                               sort: Optional[str] = None,
                               start_time: Optional[List[str]] = None,
                               time_from: Optional[str] = None,
                               time_to: Optional[str] = None) -> Dict[str, Any]:
        """獲取未來天氣預報資料
        
        Args:
            limit: 限制筆數
            offset: 起始位置
            format: 回傳格式
            location_name: 縣市名稱列表
            element_name: 天氣因子列表，可為 "Wx"（天氣現象）、"PoP"（降雨機率）、"MinT"（最低溫度）、"CI"（舒適度）、"MaxT"（最高溫度）
            sort: 排序方式
            start_time: 時間因子列表，格式為 "yyyy-MM-ddThh:mm:ss"
            time_from: 開始時間，格式為 "yyyy-MM-ddThh:mm:ss"
            time_to: 結束時間，格式為 "yyyy-MM-ddThh:mm:ss"
            
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
        if location_name:
            params["locationName"] = location_name
        if element_name:
            params["elementName"] = element_name
        if start_time:
            params["startTime"] = start_time
        if sort:
            params["sort"] = sort
        
        # 時間範圍參數
        if time_from:
            params["timeFrom"] = time_from
        if time_to:
            params["timeTo"] = time_to
        
        # 發送請求
        return await self.client.get_data(self.dataset_id, **params)
    
    async def get_forecast_by_location(self, location_name: str, limit: int = 10) -> Dict[str, Any]:
        """獲取特定縣市的未來天氣預報
        
        Args:
            location_name: 縣市名稱
            limit: 限制筆數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.get_forecast_data(location_name=[location_name], limit=limit)
    
    async def get_forecast_by_date_range(self, time_from: str, time_to: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """獲取特定時間範圍內的未來天氣預報
        
        Args:
            time_from: 開始時間，格式為 "yyyy-MM-ddThh:mm:ss"
            time_to: 結束時間，格式為 "yyyy-MM-ddThh:mm:ss"
            limit: 限制筆數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.get_forecast_data(time_from=time_from, time_to=time_to, limit=limit)
    
    async def get_forecast_by_element(self, element_name: str, limit: int = 10) -> Dict[str, Any]:
        """獲取特定天氣因子的未來天氣預報
        
        Args:
            element_name: 天氣因子，可為 "Wx"（天氣現象）、"PoP"（降雨機率）、"MinT"（最低溫度）、"CI"（舒適度）、"MaxT"（最高溫度）
            limit: 限制筆數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.get_forecast_data(element_name=[element_name], limit=limit)
    
    def display_forecast_summary(self, data: Dict[str, Any]) -> None:
        """顯示未來天氣預報摘要
        
        Args:
            data: API 回應資料
        """
        if not data.get("success"):
            print(f"API 錯誤: {data.get('message', '未知錯誤')}")
            return
        
        records = data.get("records", {})
        dataset_description = records.get("datasetDescription", "未知資料集")
        locations = records.get("location", [])
        
        if not locations:
            print("找不到天氣預報資料。")
            return
        
        print(f"資料集描述: {dataset_description}")
        print(f"找到 {len(locations)} 個縣市的天氣預報:")
        print("-" * 80)
        
        for location in locations:
            location_name = location.get("locationName", "未知地點")
            weather_elements = location.get("weatherElement", [])
            
            print(f"縣市: {location_name}")
            
            # 建立時間索引，用於組織不同天氣因子的資料
            time_index = {}
            
            # 先收集所有時間點
            for element in weather_elements:
                element_name = element.get("elementName", "未知因子")
                times = element.get("time", [])
                
                for time_data in times:
                    start_time = time_data.get("startTime", "未知時間")
                    end_time = time_data.get("endTime", "未知時間")
                    
                    if start_time not in time_index:
                        time_index[start_time] = {
                            "end_time": end_time,
                            "elements": {}
                        }
            
            # 再收集每個時間點的天氣因子資料
            for element in weather_elements:
                element_name = element.get("elementName", "未知因子")
                times = element.get("time", [])
                
                for time_data in times:
                    start_time = time_data.get("startTime", "未知時間")
                    parameter = time_data.get("parameter", {})
                    parameter_name = parameter.get("parameterName", "未知")
                    parameter_unit = parameter.get("parameterUnit", "")
                    
                    if start_time in time_index:
                        time_index[start_time]["elements"][element_name] = {
                            "name": parameter_name,
                            "unit": parameter_unit
                        }
            
            # 顯示每個時間點的天氣預報
            for start_time, time_data in sorted(time_index.items()):
                end_time = time_data["end_time"]
                elements = time_data["elements"]
                
                print(f"  時間: {start_time} 至 {end_time}")
                
                # 顯示天氣現象
                if "Wx" in elements:
                    wx_data = elements["Wx"]
                    print(f"  天氣現象: {wx_data['name']}")
                
                # 顯示降雨機率
                if "PoP" in elements:
                    pop_data = elements["PoP"]
                    print(f"  降雨機率: {pop_data['name']}{pop_data['unit']}")
                
                # 顯示溫度範圍
                min_t = elements.get("MinT", {}).get("name", "未知")
                max_t = elements.get("MaxT", {}).get("name", "未知")
                temp_unit = elements.get("MinT", {}).get("unit", "C")
                print(f"  溫度範圍: {min_t}°{temp_unit} 至 {max_t}°{temp_unit}")
                
                # 顯示舒適度
                if "CI" in elements:
                    ci_data = elements["CI"]
                    print(f"  舒適度: {ci_data['name']}")
                
                print("  ---")
            
            print("-" * 80) 
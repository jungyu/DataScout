#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中央氣象局地震服務
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from ..client import CWAClient

class EarthquakeService:
    """地震服務類"""
    
    def __init__(self, client: CWAClient):
        """初始化地震服務
        
        Args:
            client: CWA API 客戶端
        """
        self.client = client
        self.dataset_id = "E-A0015-001"  # 地震報告資料集 ID
    
    async def get_recent_earthquakes(self, limit: int = 5) -> Dict[str, Any]:
        """獲取最近的地震資料
        
        Args:
            limit: 限制筆數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_earthquake_data(limit=limit)
    
    async def get_earthquakes_by_area(self, area_names: List[str], limit: int = 3) -> Dict[str, Any]:
        """獲取特定地區的地震資料
        
        Args:
            area_names: 地區名稱列表
            limit: 限制筆數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_earthquake_data(
            area_names=area_names,
            limit=limit
        )
    
    async def get_earthquakes_by_time_range(self, time_from: str, time_to: Optional[str] = None, limit: int = 3) -> Dict[str, Any]:
        """獲取特定時間範圍內的地震資料
        
        Args:
            time_from: 開始時間 (格式: "yyyy-MM-ddThh:mm:ss")
            time_to: 結束時間 (格式: "yyyy-MM-ddThh:mm:ss")
            limit: 限制筆數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_earthquake_data(
            time_from=time_from,
            time_to=time_to,
            limit=limit
        )
    
    async def get_earthquakes_by_station(self, station_names: List[str], limit: int = 3) -> Dict[str, Any]:
        """獲取特定測站的地震資料
        
        Args:
            station_names: 測站名稱列表
            limit: 限制筆數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_earthquake_data(
            station_names=station_names,
            limit=limit
        )
    
    def display_earthquake_summary(self, data: Dict[str, Any]) -> None:
        """顯示地震資料摘要
        
        Args:
            data: API 回應資料
        """
        self.client.display_earthquake_summary(data) 
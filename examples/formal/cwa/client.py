#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中央氣象局 API 客戶端
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import httpx
from api_client.core.base_client import BaseClient
from .config import CWAConfig

class CWAClient(BaseClient):
    """中央氣象局 API 客戶端"""
    
    def __init__(self, config: CWAConfig):
        """初始化客戶端
        
        Args:
            config: API 配置
        """
        # 先驗證配置
        if not isinstance(config, CWAConfig):
            raise ValueError("配置必須是 CWAConfig 類型")
        config.validate()
        
        # 調用父類初始化
        super().__init__(config.to_dict())
        
        # 保存原始配置
        self._raw_config = config
    
    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """發送 HTTP 請求
        
        Args:
            method: 請求方法
            url: 請求 URL
            **kwargs: 請求參數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        # 構建請求頭
        headers = self.config.get("headers", {}).copy()
        headers[self.config.get("api_key_header")] = self.config.get("api_key")
        
        # 構建請求參數
        params = kwargs.get("params", {})
        params.update(self.config.get("params", {}))
        kwargs["params"] = params
        
        # 設置請求頭
        kwargs["headers"] = headers
        
        # 設置超時
        kwargs["timeout"] = self.config.get("timeout", 30)
        
        # 發送請求
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, **kwargs)
            
            # 檢查回應是否成功
            response.raise_for_status()
            
            # 根據請求的格式解析回應
            if self.config.get("response_type", "json").lower() == "json":
                return response.json()
            else:
                return {"text": response.text}
    
    async def get_data(self, dataset_id: str, **params) -> Dict[str, Any]:
        """獲取資料
        
        Args:
            dataset_id: 資料集 ID
            **params: 查詢參數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        url = f"{self.config.get('base_url')}/{dataset_id}"
        return await self._make_request("GET", url, params=params)
    
    async def get_earthquake_data(self,
                                limit: Optional[int] = None,
                                offset: Optional[int] = None,
                                format: str = "JSON",
                                area_names: Optional[List[str]] = None,
                                station_names: Optional[List[str]] = None,
                                sort_by_time: bool = False,
                                origin_times: Optional[List[str]] = None,
                                time_from: Optional[str] = None,
                                time_to: Optional[str] = None) -> Dict[str, Any]:
        """獲取地震資料
        
        Args:
            limit: 限制筆數
            offset: 起始位置
            format: 回傳格式
            area_names: 地區名稱列表
            station_names: 測站名稱列表
            sort_by_time: 是否依時間排序
            origin_times: 發生時間列表
            time_from: 開始時間
            time_to: 結束時間
            
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
        if area_names:
            params["AreaName"] = area_names
        if station_names:
            params["StationName"] = station_names
        if sort_by_time:
            params["sort"] = "OriginTime"
        if origin_times:
            params["OriginTime"] = origin_times
        
        # 時間範圍參數
        if time_from:
            params["timeFrom"] = time_from
        if time_to:
            params["timeTo"] = time_to
        
        # 發送請求
        return await self.get_data("E-A0015-001", **params)
    
    def display_earthquake_summary(self, data: Dict[str, Any]) -> None:
        """顯示地震資料摘要
        
        Args:
            data: API 回應資料
        """
        if not data.get("success"):
            print(f"API 錯誤: {data.get('message', '未知錯誤')}")
            return
        
        records = data.get("records", {})
        earthquakes = records.get("Earthquake", [])
        
        if not earthquakes:
            print("找不到地震資料。")
            return
        
        print(f"找到 {len(earthquakes)} 筆地震記錄:")
        print("-" * 80)
        
        for earthquake in earthquakes:
            # 提取關鍵資訊
            report_type = earthquake.get("ReportType", "N/A")
            report_content = earthquake.get("ReportContent", "N/A")
            earthquake_no = earthquake.get("EarthquakeNo", "N/A")
            report_color = earthquake.get("ReportColor", "N/A")
            
            # 提取地震資訊
            earthquake_info = earthquake.get("EarthquakeInfo", {})
            origin_time = earthquake_info.get("OriginTime", "N/A")
            focal_depth = earthquake_info.get("FocalDepth", "N/A")
            
            # 提取震央資訊
            epicenter = earthquake_info.get("Epicenter", {})
            location = epicenter.get("Location", "N/A")
            
            # 提取規模資訊
            magnitude_info = earthquake_info.get("EarthquakeMagnitude", {})
            magnitude_type = magnitude_info.get("MagnitudeType", "N/A")
            magnitude_value = magnitude_info.get("MagnitudeValue", "N/A")
            
            # 印出格式化摘要
            print(f"地震 #{earthquake_no} ({report_color})")
            print(f"時間: {origin_time}")
            print(f"地點: {location}")
            print(f"深度: {focal_depth} 公里")
            print(f"規模: {magnitude_value} ({magnitude_type})")
            print(f"報告: {report_content}")
            print("-" * 80) 
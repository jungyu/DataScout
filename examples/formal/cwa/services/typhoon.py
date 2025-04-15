#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中央氣象局颱風服務
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from ..client import CWAClient

class TyphoonService:
    """颱風服務類"""
    
    def __init__(self, client: CWAClient):
        """初始化颱風服務
        
        Args:
            client: CWA API 客戶端
        """
        self.client = client
        self.dataset_id = "W-C0034-005"  # 颱風資料集 ID
    
    async def get_typhoon_data(self,
                              limit: Optional[int] = None,
                              offset: Optional[int] = None,
                              format: str = "JSON",
                              cwa_td_no: Optional[int] = None,
                              dataset: Optional[List[str]] = None,
                              fix_time: Optional[List[str]] = None,
                              tau: Optional[List[int]] = None,
                              time_from: Optional[str] = None,
                              time_to: Optional[str] = None,
                              sort: Optional[List[str]] = None) -> Dict[str, Any]:
        """獲取颱風資料
        
        Args:
            limit: 限制筆數
            offset: 起始位置
            format: 回傳格式
            cwa_td_no: 熱帶性低氣壓編號
            dataset: 資料類型，可為 "analysisData" 或 "forecastData"
            fix_time: 定位時間列表，格式為 "yyyy-MM-ddThh:mm:ss"
            tau: 預報時距列表，可為 6~120 的數字
            time_from: 開始時間，格式為 "yyyy-MM-ddThh:mm:ss"
            time_to: 結束時間，格式為 "yyyy-MM-ddThh:mm:ss"
            sort: 排序方式，可為 "cwaTdNo"
            
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
        if cwa_td_no is not None:
            params["cwaTdNo"] = cwa_td_no
        
        # 處理列表參數
        if dataset:
            params["dataset"] = dataset
        if fix_time:
            params["fixTime"] = fix_time
        if tau:
            params["tau"] = tau
        if sort:
            params["sort"] = sort
        
        # 時間範圍參數
        if time_from:
            params["timeFrom"] = time_from
        if time_to:
            params["timeTo"] = time_to
        
        # 發送請求
        return await self.client.get_data(self.dataset_id, **params)
    
    async def get_current_typhoons(self, limit: int = 10) -> Dict[str, Any]:
        """獲取目前活動中的颱風資料
        
        Args:
            limit: 限制筆數
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.get_typhoon_data(limit=limit)
    
    async def get_typhoon_by_number(self, cwa_td_no: int) -> Dict[str, Any]:
        """獲取特定編號的颱風資料
        
        Args:
            cwa_td_no: 熱帶性低氣壓編號
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.get_typhoon_data(cwa_td_no=cwa_td_no)
    
    async def get_typhoon_forecast(self, cwa_td_no: int, tau: List[int] = [6, 12, 24, 48, 72]) -> Dict[str, Any]:
        """獲取特定颱風的預報資料
        
        Args:
            cwa_td_no: 熱帶性低氣壓編號
            tau: 預報時距列表，預設為 [6, 12, 24, 48, 72]
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.get_typhoon_data(
            cwa_td_no=cwa_td_no,
            dataset=["forecastData"],
            tau=tau
        )
    
    async def get_typhoon_history(self, cwa_td_no: int, time_from: str, time_to: Optional[str] = None) -> Dict[str, Any]:
        """獲取特定颱風的歷史資料
        
        Args:
            cwa_td_no: 熱帶性低氣壓編號
            time_from: 開始時間，格式為 "yyyy-MM-ddThh:mm:ss"
            time_to: 結束時間，格式為 "yyyy-MM-ddThh:mm:ss"
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.get_typhoon_data(
            cwa_td_no=cwa_td_no,
            dataset=["analysisData"],
            time_from=time_from,
            time_to=time_to
        )
    
    def display_typhoon_summary(self, data: Dict[str, Any]) -> None:
        """顯示颱風資料摘要
        
        Args:
            data: API 回應資料
        """
        if not data.get("success"):
            print(f"API 錯誤: {data.get('message', '未知錯誤')}")
            return
        
        records = data.get("records", {})
        tropical_cyclones = records.get("tropicalCyclones", {})
        typhoons = tropical_cyclones.get("tropicalCyclone", [])
        
        if not typhoons:
            print("找不到颱風資料。")
            return
        
        print(f"找到 {len(typhoons)} 個颱風:")
        print("-" * 80)
        
        for typhoon in typhoons:
            year = typhoon.get("year", "N/A")
            typhoon_name = typhoon.get("typhoonName", "N/A")
            cwa_typhoon_name = typhoon.get("cwaTyphoonName", "N/A")
            cwa_td_no = typhoon.get("cwaTdNo", "N/A")
            cwa_ty_no = typhoon.get("cwaTyNo", "N/A")
            
            print(f"颱風名稱: {cwa_typhoon_name} ({typhoon_name})")
            print(f"颱風編號: {cwa_ty_no}")
            print(f"熱帶性低氣壓編號: {cwa_td_no}")
            print(f"年份: {year}")
            
            # 顯示分析資料
            analysis_data = typhoon.get("analysisData", {})
            fixes = analysis_data.get("fix", [])
            
            if fixes:
                print("\n定位資料:")
                for fix in fixes[:5]:  # 只顯示前 5 筆
                    fix_time = fix.get("fixTime", "N/A")
                    coordinate = fix.get("coordinate", "N/A")
                    max_wind_speed = fix.get("maxWindSpeed", "N/A")
                    max_gust_speed = fix.get("maxGustSpeed", "N/A")
                    pressure = fix.get("pressure", "N/A")
                    moving_speed = fix.get("movingSpeed", "N/A")
                    moving_direction = fix.get("movingDirection", "N/A")
                    
                    print(f"  時間: {fix_time}")
                    print(f"  位置: {coordinate}")
                    print(f"  最大風速: {max_wind_speed} m/s")
                    print(f"  最大陣風: {max_gust_speed} m/s")
                    print(f"  氣壓: {pressure} hPa")
                    print(f"  移動速度: {moving_speed} km/h")
                    print(f"  移動方向: {moving_direction}")
                    print("  ---")
                
                if len(fixes) > 5:
                    print(f"  ... 還有 {len(fixes) - 5} 筆記錄")
            
            # 顯示預報資料
            forecast_data = typhoon.get("forecastData", {})
            forecast_fixes = forecast_data.get("fix", [])
            
            if forecast_fixes:
                print("\n預報資料:")
                for fix in forecast_fixes:
                    init_time = fix.get("initTime", "N/A")
                    tau = fix.get("tau", "N/A")
                    coordinate = fix.get("coordinate", "N/A")
                    max_wind_speed = fix.get("maxWindSpeed", "N/A")
                    max_gust_speed = fix.get("maxGustSpeed", "N/A")
                    pressure = fix.get("pressure", "N/A")
                    moving_speed = fix.get("movingSpeed", "N/A")
                    moving_direction = fix.get("movingDirection", "N/A")
                    radius = fix.get("radiusOf70PercentProbability", "N/A")
                    
                    print(f"  預報時間: {init_time}")
                    print(f"  預報時距: {tau} 小時")
                    print(f"  預報位置: {coordinate}")
                    print(f"  預報最大風速: {max_wind_speed} m/s")
                    print(f"  預報最大陣風: {max_gust_speed} m/s")
                    print(f"  預報氣壓: {pressure} hPa")
                    print(f"  預報移動速度: {moving_speed} km/h")
                    print(f"  預報移動方向: {moving_direction}")
                    print(f"  70% 機率半徑: {radius} 公里")
                    
                    # 顯示狀態轉換
                    state_transfers = fix.get("stateTransfers", [])
                    if state_transfers:
                        print("  狀態轉換:")
                        for transfer in state_transfers:
                            value = transfer.get("value", "N/A")
                            lang = transfer.get("lang", "N/A")
                            print(f"    {lang}: {value}")
                    
                    print("  ---")
            
            print("-" * 80) 
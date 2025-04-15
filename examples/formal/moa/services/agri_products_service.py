#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
農產品交易行情服務
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from ..client import MOAClient

class AgriProductsService:
    """農產品交易行情服務"""
    
    def __init__(self, client: MOAClient):
        """初始化服務
        
        Args:
            client: API 客戶端
        """
        self.client = client
    
    def _convert_to_roc_date(self, date_str: str) -> str:
        """將西元年日期轉換為民國年日期
        
        Args:
            date_str: 西元年日期，格式為 YYYY.MM.DD
            
        Returns:
            str: 民國年日期，格式為 YYY.MM.DD
        """
        year, month, day = date_str.split(".")
        roc_year = int(year) - 1911
        return f"{roc_year:03d}.{month}.{day}"
    
    async def get_all_trans(self,
                           start_time: Optional[str] = None,
                           end_time: Optional[str] = None,
                           crop_code: Optional[str] = None,
                           crop_name: Optional[str] = None,
                           market_name: Optional[str] = None,
                           page: Optional[str] = None,
                           tc_type: Optional[str] = None) -> Dict[str, Any]:
        """獲取所有農產品交易行情
        
        Args:
            start_time: 交易日期(起)，格式為 YYYY.MM.DD
            end_time: 交易日期(迄)，格式為 YYYY.MM.DD
            crop_code: 農產品代碼
            crop_name: 農產品名稱
            market_name: 市場名稱
            page: 頁碼控制
            tc_type: 農產品種類代碼
            
        Returns:
            Dict[str, Any]: API 回應
        """
        # 轉換日期格式
        if start_time:
            start_time = self._convert_to_roc_date(start_time)
        if end_time:
            end_time = self._convert_to_roc_date(end_time)
        
        return await self.client.get_agri_products_trans(
            start_time=start_time,
            end_time=end_time,
            crop_code=crop_code,
            crop_name=crop_name,
            market_name=market_name,
            page=page,
            tc_type=tc_type
        )
    
    async def get_trans_by_date(self, date: str) -> Dict[str, Any]:
        """獲取特定日期的農產品交易行情
        
        Args:
            date: 交易日期，格式為 YYYY.MM.DD
            
        Returns:
            Dict[str, Any]: API 回應
        """
        # 轉換日期格式
        roc_date = self._convert_to_roc_date(date)
        
        return await self.client.get_agri_products_trans(
            start_time=roc_date,
            end_time=roc_date
        )
    
    async def get_trans_by_date_range(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """獲取特定日期範圍的農產品交易行情
        
        Args:
            start_date: 開始日期，格式為 YYYY.MM.DD
            end_date: 結束日期，格式為 YYYY.MM.DD
            
        Returns:
            Dict[str, Any]: API 回應
        """
        # 轉換日期格式
        roc_start_date = self._convert_to_roc_date(start_date)
        roc_end_date = self._convert_to_roc_date(end_date)
        
        return await self.client.get_agri_products_trans(
            start_time=roc_start_date,
            end_time=roc_end_date
        )
    
    async def get_trans_by_crop(self, crop_name: str, date: Optional[str] = None) -> Dict[str, Any]:
        """獲取特定農產品的交易行情
        
        Args:
            crop_name: 農產品名稱
            date: 交易日期，格式為 YYYY.MM.DD，如果為 None 則使用今天
            
        Returns:
            Dict[str, Any]: API 回應
        """
        if date is None:
            date = datetime.now().strftime("%Y.%m.%d")
        
        # 轉換日期格式
        roc_date = self._convert_to_roc_date(date)
        
        return await self.client.get_agri_products_trans(
            crop_name=crop_name,
            start_time=roc_date,
            end_time=roc_date
        )
    
    async def get_trans_by_market(self, market_name: str, date: Optional[str] = None) -> Dict[str, Any]:
        """獲取特定市場的交易行情
        
        Args:
            market_name: 市場名稱
            date: 交易日期，格式為 YYYY.MM.DD，如果為 None 則使用今天
            
        Returns:
            Dict[str, Any]: API 回應
        """
        if date is None:
            date = datetime.now().strftime("%Y.%m.%d")
        
        # 轉換日期格式
        roc_date = self._convert_to_roc_date(date)
        
        return await self.client.get_agri_products_trans(
            market_name=market_name,
            start_time=roc_date,
            end_time=roc_date
        )
    
    async def get_recent_trans(self, days: int = 7) -> Dict[str, Any]:
        """獲取最近幾天的交易行情
        
        Args:
            days: 天數，預設為 7 天
            
        Returns:
            Dict[str, Any]: API 回應
        """
        today = datetime.now().strftime("%Y.%m.%d")
        last_week = (datetime.now() - timedelta(days=days)).strftime("%Y.%m.%d")
        
        # 轉換日期格式
        roc_today = self._convert_to_roc_date(today)
        roc_last_week = self._convert_to_roc_date(last_week)
        
        return await self.client.get_agri_products_trans(
            start_time=roc_last_week,
            end_time=roc_today
        )
    
    def display_trans_summary(self, data: Dict[str, Any]) -> None:
        """顯示交易行情摘要
        
        Args:
            data: API 回應資料
        """
        self.client.display_trans_summary(data)
    
    def analyze_trans_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析交易行情資料
        
        Args:
            data: API 回應資料
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        if data.get("RS") != "OK":
            return {"error": data.get("message", "未知錯誤")}
        
        records = data.get("Data", [])
        
        if not records:
            return {"error": "找不到交易行情資料"}
        
        # 計算平均價格
        total_price = 0
        total_quantity = 0
        crop_prices = {}
        market_prices = {}
        
        for record in records:
            avg_price = float(record.get("Avg_Price", 0))
            trans_quantity = float(record.get("Trans_Quantity", 0))
            
            if avg_price > 0 and trans_quantity > 0:
                total_price += avg_price * trans_quantity
                total_quantity += trans_quantity
                
                # 按農產品分類統計
                crop_name = record.get("CropName", "未知")
                if crop_name not in crop_prices:
                    crop_prices[crop_name] = {"total_price": 0, "total_quantity": 0}
                crop_prices[crop_name]["total_price"] += avg_price * trans_quantity
                crop_prices[crop_name]["total_quantity"] += trans_quantity
                
                # 按市場分類統計
                market_name = record.get("MarketName", "未知")
                if market_name not in market_prices:
                    market_prices[market_name] = {"total_price": 0, "total_quantity": 0}
                market_prices[market_name]["total_price"] += avg_price * trans_quantity
                market_prices[market_name]["total_quantity"] += trans_quantity
        
        # 計算總平均價格
        overall_avg_price = total_price / total_quantity if total_quantity > 0 else 0
        
        # 計算各農產品平均價格
        crop_avg_prices = {}
        for crop_name, data in crop_prices.items():
            crop_avg_prices[crop_name] = data["total_price"] / data["total_quantity"] if data["total_quantity"] > 0 else 0
        
        # 計算各市場平均價格
        market_avg_prices = {}
        for market_name, data in market_prices.items():
            market_avg_prices[market_name] = data["total_price"] / data["total_quantity"] if data["total_quantity"] > 0 else 0
        
        # 找出最高和最低價格的農產品
        max_price_crop = max(crop_avg_prices.items(), key=lambda x: x[1]) if crop_avg_prices else ("無資料", 0)
        min_price_crop = min(crop_avg_prices.items(), key=lambda x: x[1]) if crop_avg_prices else ("無資料", 0)
        
        # 找出最高和最低價格的市場
        max_price_market = max(market_avg_prices.items(), key=lambda x: x[1]) if market_avg_prices else ("無資料", 0)
        min_price_market = min(market_avg_prices.items(), key=lambda x: x[1]) if market_avg_prices else ("無資料", 0)
        
        return {
            "record_count": len(records),
            "overall_avg_price": overall_avg_price,
            "crop_avg_prices": crop_avg_prices,
            "market_avg_prices": market_avg_prices,
            "max_price_crop": max_price_crop,
            "min_price_crop": min_price_crop,
            "max_price_market": max_price_market,
            "min_price_market": min_price_market
        }
    
    def display_analysis(self, analysis: Dict[str, Any]) -> None:
        """顯示分析結果
        
        Args:
            analysis: 分析結果
        """
        if "error" in analysis:
            print(f"分析錯誤: {analysis['error']}")
            return
        
        print(f"分析 {analysis['record_count']} 筆交易記錄:")
        print("-" * 80)
        print(f"總平均價格: {analysis['overall_avg_price']:.2f} 元/公斤")
        print("-" * 80)
        
        print("各農產品平均價格:")
        for crop_name, avg_price in sorted(analysis['crop_avg_prices'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {crop_name}: {avg_price:.2f} 元/公斤")
        print("-" * 80)
        
        print("各市場平均價格:")
        for market_name, avg_price in sorted(analysis['market_avg_prices'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {market_name}: {avg_price:.2f} 元/公斤")
        print("-" * 80)
        
        print(f"最高價格農產品: {analysis['max_price_crop'][0]} ({analysis['max_price_crop'][1]:.2f} 元/公斤)")
        print(f"最低價格農產品: {analysis['min_price_crop'][0]} ({analysis['min_price_crop'][1]:.2f} 元/公斤)")
        print(f"最高價格市場: {analysis['max_price_market'][0]} ({analysis['max_price_market'][1]:.2f} 元/公斤)")
        print(f"最低價格市場: {analysis['min_price_market'][0]} ({analysis['min_price_market'][1]:.2f} 元/公斤)")
        print("-" * 80) 
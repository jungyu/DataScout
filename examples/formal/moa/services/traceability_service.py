#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
溯源農糧產品追溯系統服務
"""

from typing import Dict, Any, Optional, List
from ..client import MOAClient

class TraceabilityService:
    """溯源農糧產品追溯系統服務"""
    
    def __init__(self, client: MOAClient):
        """初始化服務
        
        Args:
            client: API 客戶端
        """
        self.client = client
    
    async def get_all_product_info(self,
                                  trace_code: Optional[str] = None,
                                  product: Optional[str] = None) -> Dict[str, Any]:
        """獲取所有產品資訊
        
        Args:
            trace_code: 追溯編號
            product: 產品名稱
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_agri_products_traceability(
            trace_code=trace_code,
            product=product
        )
    
    async def get_product_by_trace_code(self, trace_code: str) -> Dict[str, Any]:
        """根據追溯編號獲取產品資訊
        
        Args:
            trace_code: 追溯編號
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_agri_products_traceability(
            trace_code=trace_code
        )
    
    async def get_product_by_name(self, product: str) -> Dict[str, Any]:
        """根據產品名稱獲取產品資訊
        
        Args:
            product: 產品名稱
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_agri_products_traceability(
            product=product
        )
    
    def display_product_summary(self, data: Dict[str, Any]) -> None:
        """顯示產品資訊摘要
        
        Args:
            data: API 回應資料
        """
        self.client.display_traceability_summary(data)
    
    async def get_all_producer_info(self,
                                   trace_code: Optional[str] = None,
                                   producer: Optional[str] = None,
                                   address: Optional[str] = None,
                                   page: Optional[str] = None) -> Dict[str, Any]:
        """獲取所有生產者資訊
        
        Args:
            trace_code: 追溯編號
            producer: 生產者
            address: 聯絡地址
            page: 頁碼控制
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_agri_products_producer_info(
            trace_code=trace_code,
            producer=producer,
            address=address,
            page=page
        )
    
    async def get_producer_by_trace_code(self, trace_code: str) -> Dict[str, Any]:
        """根據追溯編號獲取生產者資訊
        
        Args:
            trace_code: 追溯編號
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_agri_products_producer_info(
            trace_code=trace_code
        )
    
    async def get_producer_by_name(self, producer: str) -> Dict[str, Any]:
        """根據生產者名稱獲取生產者資訊
        
        Args:
            producer: 生產者名稱
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await this.client.get_agri_products_producer_info(
            producer=producer
        )
    
    async def get_producer_by_address(self, address: str) -> Dict[str, Any]:
        """根據地址獲取生產者資訊
        
        Args:
            address: 聯絡地址
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_agri_products_producer_info(
            address=address
        )
    
    def display_producer_summary(self, data: Dict[str, Any]) -> None:
        """顯示生產者資訊摘要
        
        Args:
            data: API 回應資料
        """
        self.client.display_producer_info_summary(data)
    
    def analyze_producer_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析生產者資料
        
        Args:
            data: API 回應資料
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        if data.get("RS") != "OK":
            return {"error": data.get("message", "未知錯誤")}
        
        records = data.get("Data", [])
        
        if not records:
            return {"error": "找不到生產者資訊資料"}
        
        # 統計驗證標章
        marks = {}
        for record in records:
            mark = record.get("Mark", "")
            if mark:
                if mark not in marks:
                    marks[mark] = 0
                marks[mark] += 1
        
        # 統計使用狀態
        statuses = {}
        for record in records:
            status = record.get("Status", "未知")
            if status not in statuses:
                statuses[status] = 0
            statuses[status] += 1
        
        # 統計地區分布
        regions = {}
        for record in records:
            address = record.get("Address", "")
            if address:
                # 提取縣市名稱（假設地址格式為「縣市區域路街...」）
                region = address.split("市")[0] + "市" if "市" in address else address.split("縣")[0] + "縣" if "縣" in address else "其他"
                if region not in regions:
                    regions[region] = 0
                regions[region] += 1
        
        return {
            "record_count": len(records),
            "marks": marks,
            "statuses": statuses,
            "regions": regions
        }
    
    def display_producer_analysis(self, analysis: Dict[str, Any]) -> None:
        """顯示生產者分析結果
        
        Args:
            analysis: 分析結果
        """
        if "error" in analysis:
            print(f"分析錯誤: {analysis['error']}")
            return
        
        print(f"分析 {analysis['record_count']} 筆生產者資訊記錄:")
        print("-" * 80)
        
        print("驗證標章分布:")
        for mark, count in sorted(analysis['marks'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {mark}: {count} 筆 ({count/analysis['record_count']*100:.1f}%)")
        print("-" * 80)
        
        print("使用狀態分布:")
        for status, count in sorted(analysis['statuses'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {status}: {count} 筆 ({count/analysis['record_count']*100:.1f}%)")
        print("-" * 80)
        
        print("地區分布:")
        for region, count in sorted(analysis['regions'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {region}: {count} 筆 ({count/analysis['record_count']*100:.1f}%)")
        print("-" * 80) 
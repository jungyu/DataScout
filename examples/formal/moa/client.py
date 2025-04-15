#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
農產品交易行情 API 客戶端
"""

from typing import Dict, Any, Optional, List
import httpx
from api_client.core.base_client import BaseClient
from .config import MOAConfig

class MOAClient(BaseClient):
    """農產品交易行情 API 客戶端"""
    
    def __init__(self, config: MOAConfig):
        """初始化客戶端
        
        Args:
            config: API 配置
        """
        # 先驗證配置
        if not isinstance(config, MOAConfig):
            raise ValueError("配置必須是 MOAConfig 類型")
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
    
    async def get_agri_products_trans(self,
                                    start_time: Optional[str] = None,
                                    end_time: Optional[str] = None,
                                    crop_code: Optional[str] = None,
                                    crop_name: Optional[str] = None,
                                    market_name: Optional[str] = None,
                                    page: Optional[str] = None,
                                    tc_type: Optional[str] = None) -> Dict[str, Any]:
        """獲取農產品交易行情
        
        Args:
            start_time: 交易日期(起)
            end_time: 交易日期(迄)
            crop_code: 農產品代碼
            crop_name: 農產品名稱
            market_name: 市場名稱
            page: 頁碼控制
            tc_type: 農產品種類代碼
            
        Returns:
            Dict[str, Any]: API 回應
        """
        # 構建查詢參數
        params = {}
        
        # 加入選用參數
        if start_time:
            params["Start_time"] = start_time
        if end_time:
            params["End_time"] = end_time
        if crop_code:
            params["CropCode"] = crop_code
        if crop_name:
            params["CropName"] = crop_name
        if market_name:
            params["MarketName"] = market_name
        if page:
            params["Page"] = page
        if tc_type:
            params["TcType"] = tc_type
        
        # 發送請求
        return await self._make_request("GET", f"{self.config.get('base_url')}/AgriProductsTransType/", params=params)
    
    def display_trans_summary(self, data: Dict[str, Any]) -> None:
        """顯示交易行情摘要
        
        Args:
            data: API 回應資料
        """
        if data.get("RS") != "OK":
            print(f"API 錯誤: {data.get('message', '未知錯誤')}")
            return
        
        records = data.get("Data", [])
        
        if not records:
            print("找不到交易行情資料。")
            return
        
        print(f"找到 {len(records)} 筆交易記錄:")
        print("-" * 80)
        
        for record in records:
            # 提取關鍵資訊
            trans_date = record.get("TransDate", "N/A")
            crop_name = record.get("CropName", "N/A")
            market_name = record.get("MarketName", "N/A")
            avg_price = record.get("Avg_Price", "N/A")
            trans_quantity = record.get("Trans_Quantity", "N/A")
            
            # 印出格式化摘要
            print(f"交易日期: {trans_date}")
            print(f"農產品: {crop_name}")
            print(f"市場: {market_name}")
            print(f"平均價格: {avg_price} 元/公斤")
            print(f"交易量: {trans_quantity} 公斤")
            print("-" * 80)
            
    async def get_pest_disease_diagnosis(self,
                                       plant_type: Optional[str] = None,
                                       product_name: Optional[str] = None,
                                       page: Optional[str] = None) -> Dict[str, Any]:
        """獲取病蟲害診斷服務問答集
        
        Args:
            plant_type: 植物分類
            product_name: 品名
            page: 頁碼控制
            
        Returns:
            Dict[str, Any]: API 回應
        """
        # 構建查詢參數
        params = {}
        
        # 加入選用參數
        if plant_type:
            params["Type"] = plant_type
        if product_name:
            params["ProductName"] = product_name
        if page:
            params["Page"] = page
        
        # 發送請求
        return await self._make_request("GET", f"{self.config.get('base_url')}/PestDiseaseDiagnosisServiceType/", params=params)
    
    def display_diagnosis_summary(self, data: Dict[str, Any]) -> None:
        """顯示病蟲害診斷服務問答集摘要
        
        Args:
            data: API 回應資料
        """
        if data.get("RS") != "OK":
            print(f"API 錯誤: {data.get('message', '未知錯誤')}")
            return
        
        records = data.get("Data", [])
        
        if not records:
            print("找不到病蟲害診斷服務問答集資料。")
            return
        
        print(f"找到 {len(records)} 筆問答記錄:")
        print("-" * 80)
        
        for record in records:
            # 提取關鍵資訊
            plant_type = record.get("Type", "N/A")
            product_name = record.get("ProductName", "N/A")
            question = record.get("Question", "N/A")
            answer = record.get("Answer", "N/A")
            provision = record.get("Provision", "N/A")
            
            # 印出格式化摘要
            print(f"植物分類: {plant_type}")
            print(f"品名: {product_name}")
            print(f"問題: {question}")
            print(f"答案: {answer}")
            if provision:
                print(f"防治方法: {provision}")
            print("-" * 80)
            
    async def get_important_agricultural_pest_diagnostics(self,
                                                        order_latina: Optional[str] = None,
                                                        order_ch: Optional[str] = None,
                                                        pest_name_ch: Optional[str] = None,
                                                        pest_name_en: Optional[str] = None,
                                                        page: Optional[str] = None) -> Dict[str, Any]:
        """獲取重要農業害蟲診斷圖鑑
        
        Args:
            order_latina: 拉丁目別
            order_ch: 中文目別
            pest_name_ch: 害蟲中文名
            pest_name_en: 害蟲英文名
            page: 頁碼控制
            
        Returns:
            Dict[str, Any]: API 回應
        """
        # 構建查詢參數
        params = {}
        
        # 加入選用參數
        if order_latina:
            params["Order_Latina"] = order_latina
        if order_ch:
            params["Order_Ch"] = order_ch
        if pest_name_ch:
            params["PestName_Ch"] = pest_name_ch
        if pest_name_en:
            params["PestName_En"] = pest_name_en
        if page:
            params["Page"] = page
        
        # 發送請求
        return await self._make_request("GET", f"{self.config.get('base_url')}/ImportantAgriculturalPestDiagnosticsType/", params=params)
    
    def display_pest_diagnostics_summary(self, data: Dict[str, Any]) -> None:
        """顯示重要農業害蟲診斷圖鑑摘要
        
        Args:
            data: API 回應資料
        """
        if data.get("RS") != "OK":
            print(f"API 錯誤: {data.get('message', '未知錯誤')}")
            return
        
        records = data.get("Data", [])
        
        if not records:
            print("找不到重要農業害蟲診斷圖鑑資料。")
            return
        
        print(f"找到 {len(records)} 筆害蟲記錄:")
        print("-" * 80)
        
        for record in records:
            # 提取關鍵資訊
            pest_name_ch = record.get("PestName_Ch", "N/A")
            pest_name_en = record.get("PestName_En", "N/A")
            pest_name_scientific = record.get("PestName_Scientific", "N/A")
            order_ch = record.get("Order_Ch", "N/A")
            family_ch = record.get("Family_Ch", "N/A")
            crop_name = record.get("Crop_Name", "N/A")
            
            # 印出格式化摘要
            print(f"害蟲中文名: {pest_name_ch}")
            print(f"害蟲英文名: {pest_name_en}")
            print(f"害蟲學名: {pest_name_scientific}")
            print(f"目別: {order_ch}")
            print(f"科別: {family_ch}")
            print(f"作物: {crop_name}")
            print("-" * 80)
            
    async def get_agri_products_traceability(self,
                                           trace_code: Optional[str] = None,
                                           product: Optional[str] = None) -> Dict[str, Any]:
        """獲取溯源農糧產品追溯系統-產品資訊
        
        Args:
            trace_code: 追溯編號
            product: 產品名稱
            
        Returns:
            Dict[str, Any]: API 回應
        """
        # 構建查詢參數
        params = {}
        
        # 加入選用參數
        if trace_code:
            params["TraceCode"] = trace_code
        if product:
            params["Product"] = product
        
        # 發送請求
        return await self._make_request("GET", f"{self.config.get('base_url')}/TWAgriProductsTraceabilityType_ProductInfo/", params=params)
    
    def display_traceability_summary(self, data: Dict[str, Any]) -> None:
        """顯示溯源農糧產品追溯系統-產品資訊摘要
        
        Args:
            data: API 回應資料
        """
        if data.get("RS") != "OK":
            print(f"API 錯誤: {data.get('message', '未知錯誤')}")
            return
        
        records = data.get("Data", [])
        
        if not records:
            print("找不到溯源農糧產品追溯系統-產品資訊資料。")
            return
        
        print(f"找到 {len(records)} 筆產品追溯記錄:")
        print("-" * 80)
        
        for record in records:
            # 提取關鍵資訊
            trace_code = record.get("TraceCode", "N/A")
            product = record.get("Product", "N/A")
            place = record.get("Place", "N/A")
            mark = record.get("Mark", "N/A")
            
            # 印出格式化摘要
            print(f"追溯編號: {trace_code}")
            print(f"產品名稱: {product}")
            print(f"生產地: {place}")
            if mark:
                print(f"驗證標章: {mark}")
            print("-" * 80)
            
    async def get_agri_products_producer_info(self,
                                            trace_code: Optional[str] = None,
                                            producer: Optional[str] = None,
                                            address: Optional[str] = None,
                                            page: Optional[str] = None) -> Dict[str, Any]:
        """獲取溯源農糧產品追溯系統-生產者資訊
        
        Args:
            trace_code: 追溯編號
            producer: 生產者
            address: 聯絡地址
            page: 頁碼控制
            
        Returns:
            Dict[str, Any]: API 回應
        """
        # 構建查詢參數
        params = {}
        
        # 加入選用參數
        if trace_code:
            params["TraceCode"] = trace_code
        if producer:
            params["Producer"] = producer
        if address:
            params["Address"] = address
        if page:
            params["Page"] = page
        
        # 發送請求
        return await self._make_request("GET", f"{self.config.get('base_url')}/TWAgriProductsTraceabilityType_ProducerInfo/", params=params)
    
    def display_producer_info_summary(self, data: Dict[str, Any]) -> None:
        """顯示溯源農糧產品追溯系統-生產者資訊摘要
        
        Args:
            data: API 回應資料
        """
        if data.get("RS") != "OK":
            print(f"API 錯誤: {data.get('message', '未知錯誤')}")
            return
        
        records = data.get("Data", [])
        
        if not records:
            print("找不到溯源農糧產品追溯系統-生產者資訊資料。")
            return
        
        print(f"找到 {len(records)} 筆生產者資訊記錄:")
        print("-" * 80)
        
        for record in records:
            # 提取關鍵資訊
            trace_code = record.get("TraceCode", "N/A")
            producer = record.get("Producer", "N/A")
            address = record.get("Address", "N/A")
            mark = record.get("Mark", "N/A")
            url = record.get("Url", "N/A")
            status = record.get("Status", "N/A")
            modify_date = record.get("ModifyDate", "N/A")
            
            # 印出格式化摘要
            print(f"追溯編號: {trace_code}")
            print(f"生產者: {producer}")
            print(f"聯絡地址: {address}")
            if mark:
                print(f"驗證標章: {mark}")
            if url:
                print(f"網址: {url}")
            print(f"使用狀態: {status}")
            print(f"異動日期: {modify_date}")
            
            # 顯示簡介（如果太長則截斷）
            description = record.get("Description", "")
            if description:
                if len(description) > 100:
                    print(f"簡介: {description[:100]}...")
                else:
                    print(f"簡介: {description}")
            
            print("-" * 80) 
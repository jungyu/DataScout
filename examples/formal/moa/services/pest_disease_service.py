#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
病蟲害診斷服務
"""

from typing import Dict, Any, Optional, List
from ..client import MOAClient

class PestDiseaseService:
    """病蟲害診斷服務"""
    
    def __init__(self, client: MOAClient):
        """初始化服務
        
        Args:
            client: API 客戶端
        """
        self.client = client
    
    async def get_all_diagnosis(self) -> Dict[str, Any]:
        """獲取所有病蟲害診斷服務問答集
        
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_pest_disease_diagnosis()
    
    async def get_diagnosis_by_plant_type(self, plant_type: str) -> Dict[str, Any]:
        """根據植物分類獲取病蟲害診斷服務問答集
        
        Args:
            plant_type: 植物分類
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_pest_disease_diagnosis(plant_type=plant_type)
    
    async def get_diagnosis_by_product(self, product_name: str) -> Dict[str, Any]:
        """根據品名獲取病蟲害診斷服務問答集
        
        Args:
            product_name: 品名
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_pest_disease_diagnosis(product_name=product_name)
    
    async def search_diagnosis(self,
                             plant_type: Optional[str] = None,
                             product_name: Optional[str] = None) -> Dict[str, Any]:
        """搜尋病蟲害診斷服務問答集
        
        Args:
            plant_type: 植物分類
            product_name: 品名
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_pest_disease_diagnosis(
            plant_type=plant_type,
            product_name=product_name
        )
    
    def display_diagnosis(self, data: Dict[str, Any]) -> None:
        """顯示病蟲害診斷服務問答集
        
        Args:
            data: API 回應資料
        """
        self.client.display_diagnosis_summary(data)
    
    def analyze_diagnosis_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析病蟲害診斷服務問答集資料
        
        Args:
            data: API 回應資料
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        if data.get("RS") != "OK":
            return {
                "error": data.get("message", "未知錯誤"),
                "total": 0,
                "plant_types": {},
                "products": {}
            }
        
        records = data.get("Data", [])
        
        # 統計植物分類
        plant_types = {}
        for record in records:
            plant_type = record.get("Type", "未知")
            if plant_type not in plant_types:
                plant_types[plant_type] = 0
            plant_types[plant_type] += 1
        
        # 統計品名
        products = {}
        for record in records:
            product = record.get("ProductName", "未知")
            if product not in products:
                products[product] = 0
            products[product] += 1
        
        return {
            "total": len(records),
            "plant_types": plant_types,
            "products": products
        }
    
    def display_analysis(self, analysis: Dict[str, Any]) -> None:
        """顯示分析結果
        
        Args:
            analysis: 分析結果
        """
        if "error" in analysis:
            print(f"分析錯誤: {analysis['error']}")
            return
        
        print(f"總筆數: {analysis['total']}")
        
        print("\n植物分類統計:")
        for plant_type, count in analysis["plant_types"].items():
            print(f"  {plant_type}: {count} 筆")
        
        print("\n品名統計:")
        for product, count in analysis["products"].items():
            print(f"  {product}: {count} 筆")
            
    async def get_all_pest_diagnostics(self) -> Dict[str, Any]:
        """獲取所有重要農業害蟲診斷圖鑑
        
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_important_agricultural_pest_diagnostics()
    
    async def search_pest_diagnostics(self,
                                    order_latina: Optional[str] = None,
                                    order_ch: Optional[str] = None,
                                    pest_name_ch: Optional[str] = None,
                                    pest_name_en: Optional[str] = None) -> Dict[str, Any]:
        """搜尋重要農業害蟲診斷圖鑑
        
        Args:
            order_latina: 拉丁目別
            order_ch: 中文目別
            pest_name_ch: 害蟲中文名
            pest_name_en: 害蟲英文名
            
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_important_agricultural_pest_diagnostics(
            order_latina=order_latina,
            order_ch=order_ch,
            pest_name_ch=pest_name_ch,
            pest_name_en=pest_name_en
        )
    
    def display_pest_diagnostics(self, data: Dict[str, Any]) -> None:
        """顯示重要農業害蟲診斷圖鑑
        
        Args:
            data: API 回應資料
        """
        if data.get("RS") != "OK":
            print(f"錯誤: {data.get('message', '未知錯誤')}")
            return
        
        records = data.get("Data", [])
        if not records:
            print("沒有找到符合條件的資料")
            return
        
        print(f"找到 {len(records)} 筆重要農業害蟲診斷圖鑑資料:")
        for i, record in enumerate(records, 1):
            print(f"\n{i}. {record.get('PestName_Ch', '未知')} ({record.get('PestName_En', '未知')})")
            print(f"   學名: {record.get('PestName_Scientific', '未知')}")
            print(f"   目別: {record.get('Order_Ch', '未知')} ({record.get('Order_Latina', '未知')})")
            print(f"   科別: {record.get('Family_Ch', '未知')} ({record.get('Family_Latina', '未知')})")
            print(f"   口器: {record.get('EatWay', '未知')}")
            print(f"   危害部位: ", end="")
            harms = []
            if record.get("Harm_Root") == "Y":
                harms.append("根")
            if record.get("Harm_Stem") == "Y":
                harms.append("莖")
            if record.get("Harm_leaf") == "Y":
                harms.append("葉")
            if record.get("Harm_Flower") == "Y":
                harms.append("花")
            if record.get("Harm_Fruit") == "Y":
                harms.append("果")
            if record.get("Harm_Plant") == "Y":
                harms.append("整株")
            if record.get("Other"):
                harms.append(record.get("Other"))
            print(", ".join(harms) if harms else "未知")
            print(f"   作物: {record.get('Crop_Name', '未知')} ({record.get('Crop_ScientificName', '未知')})")
            print(f"   圖片: {record.get('Image', '無')}")
    
    def analyze_pest_diagnostics_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析重要農業害蟲診斷圖鑑資料
        
        Args:
            data: API 回應資料
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        if data.get("RS") != "OK":
            return {
                "error": data.get("message", "未知錯誤"),
                "total": 0,
                "orders": {},
                "families": {},
                "crops": {},
                "harm_types": {
                    "root": 0,
                    "stem": 0,
                    "leaf": 0,
                    "flower": 0,
                    "fruit": 0,
                    "plant": 0,
                    "other": 0
                }
            }
        
        records = data.get("Data", [])
        
        # 統計目別
        orders = {}
        for record in records:
            order = record.get("Order_Ch", "未知")
            if order not in orders:
                orders[order] = 0
            orders[order] += 1
        
        # 統計科別
        families = {}
        for record in records:
            family = record.get("Family_Ch", "未知")
            if family not in families:
                families[family] = 0
            families[family] += 1
        
        # 統計作物
        crops = {}
        for record in records:
            crop = record.get("Crop_Name", "未知")
            if crop not in crops:
                crops[crop] = 0
            crops[crop] += 1
        
        # 統計危害類型
        harm_types = {
            "root": 0,
            "stem": 0,
            "leaf": 0,
            "flower": 0,
            "fruit": 0,
            "plant": 0,
            "other": 0
        }
        
        for record in records:
            if record.get("Harm_Root") == "Y":
                harm_types["root"] += 1
            if record.get("Harm_Stem") == "Y":
                harm_types["stem"] += 1
            if record.get("Harm_leaf") == "Y":
                harm_types["leaf"] += 1
            if record.get("Harm_Flower") == "Y":
                harm_types["flower"] += 1
            if record.get("Harm_Fruit") == "Y":
                harm_types["fruit"] += 1
            if record.get("Harm_Plant") == "Y":
                harm_types["plant"] += 1
            if record.get("Other"):
                harm_types["other"] += 1
        
        return {
            "total": len(records),
            "orders": orders,
            "families": families,
            "crops": crops,
            "harm_types": harm_types
        }
    
    def display_pest_diagnostics_analysis(self, analysis: Dict[str, Any]) -> None:
        """顯示重要農業害蟲診斷圖鑑分析結果
        
        Args:
            analysis: 分析結果
        """
        if "error" in analysis:
            print(f"分析錯誤: {analysis['error']}")
            return
        
        print(f"總筆數: {analysis['total']}")
        
        print("\n目別統計:")
        for order, count in analysis["orders"].items():
            print(f"  {order}: {count} 筆")
        
        print("\n科別統計:")
        for family, count in analysis["families"].items():
            print(f"  {family}: {count} 筆")
        
        print("\n作物統計:")
        for crop, count in analysis["crops"].items():
            print(f"  {crop}: {count} 筆")
        
        print("\n危害類型統計:")
        harm_types = analysis["harm_types"]
        print(f"  根: {harm_types['root']} 筆")
        print(f"  莖: {harm_types['stem']} 筆")
        print(f"  葉: {harm_types['leaf']} 筆")
        print(f"  花: {harm_types['flower']} 筆")
        print(f"  果: {harm_types['fruit']} 筆")
        print(f"  整株: {harm_types['plant']} 筆")
        print(f"  其他: {harm_types['other']} 筆")
        
    async def get_all_agri_products_traceability(self) -> Dict[str, Any]:
        """獲取所有溯源農糧產品追溯系統-產品資訊
        
        Returns:
            Dict[str, Any]: API 回應
        """
        return await self.client.get_agri_products_traceability()
    
    async def search_agri_products_traceability(self,
                                              trace_code: Optional[str] = None,
                                              product: Optional[str] = None) -> Dict[str, Any]:
        """搜尋溯源農糧產品追溯系統-產品資訊
        
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
    
    def display_agri_products_traceability(self, data: Dict[str, Any]) -> None:
        """顯示溯源農糧產品追溯系統-產品資訊
        
        Args:
            data: API 回應資料
        """
        self.client.display_traceability_summary(data)
    
    def analyze_agri_products_traceability_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析溯源農糧產品追溯系統-產品資訊資料
        
        Args:
            data: API 回應資料
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        if data.get("RS") != "OK":
            return {
                "error": data.get("message", "未知錯誤"),
                "total": 0,
                "trace_codes": {},
                "products": {},
                "places": {},
                "marks": {}
            }
        
        records = data.get("Data", [])
        
        # 統計追溯編號
        trace_codes = {}
        for record in records:
            trace_code = record.get("TraceCode", "未知")
            if trace_code not in trace_codes:
                trace_codes[trace_code] = 0
            trace_codes[trace_code] += 1
        
        # 統計產品名稱
        products = {}
        for record in records:
            product = record.get("Product", "未知")
            if product not in products:
                products[product] = 0
            products[product] += 1
        
        # 統計生產地
        places = {}
        for record in records:
            place = record.get("Place", "未知")
            if place not in places:
                places[place] = 0
            places[place] += 1
        
        # 統計驗證標章
        marks = {}
        for record in records:
            mark = record.get("Mark", "未知")
            if mark not in marks:
                marks[mark] = 0
            marks[mark] += 1
        
        return {
            "total": len(records),
            "trace_codes": trace_codes,
            "products": products,
            "places": places,
            "marks": marks
        }
    
    def display_agri_products_traceability_analysis(self, analysis: Dict[str, Any]) -> None:
        """顯示溯源農糧產品追溯系統-產品資訊分析結果
        
        Args:
            analysis: 分析結果
        """
        if "error" in analysis:
            print(f"分析錯誤: {analysis['error']}")
            return
        
        print(f"總筆數: {analysis['total']}")
        
        print("\n追溯編號統計:")
        for trace_code, count in analysis["trace_codes"].items():
            print(f"  {trace_code}: {count} 筆")
        
        print("\n產品名稱統計:")
        for product, count in analysis["products"].items():
            print(f"  {product}: {count} 筆")
        
        print("\n生產地統計:")
        for place, count in analysis["places"].items():
            print(f"  {place}: {count} 筆")
        
        print("\n驗證標章統計:")
        for mark, count in analysis["marks"].items():
            print(f"  {mark}: {count} 筆") 
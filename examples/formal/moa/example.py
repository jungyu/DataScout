#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
農產品交易行情 API 示例
"""

import asyncio
from datetime import datetime, timedelta
from .config import MOAConfig
from .client import MOAClient
from .services.pest_disease_service import PestDiseaseService

async def main():
    """主程式"""
    # 建立 API 配置
    config = MOAConfig()
    
    # 建立 API 客戶端
    client = MOAClient(config)
    
    # 建立病蟲害診斷服務
    pest_disease_service = PestDiseaseService(client)
    
    # 範例 1: 取得今天的交易行情
    print("正在取得今天的交易行情...")
    today = datetime.now().strftime("%Y.%m.%d")
    today_data = await client.get_agri_products_trans(start_time=today, end_time=today)
    client.display_trans_summary(today_data)
    
    # 範例 2: 取得特定農產品的交易行情
    print("\n正在取得康乃馨的交易行情...")
    crop_data = await client.get_agri_products_trans(
        crop_name="康乃馨",
        start_time=today,
        end_time=today
    )
    client.display_trans_summary(crop_data)
    
    # 範例 3: 取得特定市場的交易行情
    print("\n正在取得台北市場的交易行情...")
    market_data = await client.get_agri_products_trans(
        market_name="台北市場",
        start_time=today,
        end_time=today
    )
    client.display_trans_summary(market_data)
    
    # 範例 4: 取得特定時間範圍的交易行情
    print("\n正在取得最近一週的交易行情...")
    # 計算一週前的日期
    last_week = (datetime.now() - timedelta(days=7)).strftime("%Y.%m.%d")
    time_data = await client.get_agri_products_trans(
        start_time=last_week,
        end_time=today
    )
    client.display_trans_summary(time_data)
    
    # 範例 5: 取得所有病蟲害診斷服務問答集
    print("\n正在取得所有病蟲害診斷服務問答集...")
    all_diagnosis = await pest_disease_service.get_all_diagnosis()
    pest_disease_service.display_diagnosis(all_diagnosis)
    
    # 分析所有病蟲害診斷服務問答集
    print("\n分析所有病蟲害診斷服務問答集...")
    analysis = pest_disease_service.analyze_diagnosis_data(all_diagnosis)
    pest_disease_service.display_analysis(analysis)
    
    # 範例 6: 取得特定植物分類的病蟲害診斷服務問答集
    print("\n正在取得果樹的病蟲害診斷服務問答集...")
    plant_type_data = await pest_disease_service.get_diagnosis_by_plant_type("果樹")
    pest_disease_service.display_diagnosis(plant_type_data)
    
    # 範例 7: 取得特定品名的病蟲害診斷服務問答集
    print("\n正在取得梨的病蟲害診斷服務問答集...")
    product_data = await pest_disease_service.get_diagnosis_by_product("梨")
    pest_disease_service.display_diagnosis(product_data)
    
    # 範例 8: 搜尋病蟲害診斷服務問答集
    print("\n正在搜尋果樹類別中梨的病蟲害診斷服務問答集...")
    search_data = await pest_disease_service.search_diagnosis(
        plant_type="果樹",
        product_name="梨"
    )
    pest_disease_service.display_diagnosis(search_data)

if __name__ == "__main__":
    asyncio.run(main()) 
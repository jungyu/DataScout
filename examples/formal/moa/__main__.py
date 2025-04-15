#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
農產品交易行情 API 示例主程式
"""

import asyncio
import os
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .config import MOAConfig
from .client import MOAClient
from .services import AgriProductsService, PestDiseaseService, TraceabilityService

async def run_agri_products_example(client: MOAClient, args):
    """執行農產品交易行情示例"""
    print("執行農產品交易行情示例...")
    agri_products_service = AgriProductsService(client)
    
    if args.date:
        # 取得特定日期的交易行情
        print(f"\n正在取得 {args.date} 的交易行情...")
        date_data = await agri_products_service.get_trans_by_date(args.date)
        agri_products_service.display_trans_summary(date_data)
    
    if args.date_range:
        # 取得特定日期範圍的交易行情
        print(f"\n正在取得 {args.date_range} 日期範圍內的交易行情...")
        range_data = await agri_products_service.get_trans_by_date_range(
            start_date=args.date_range[0],
            end_date=args.date_range[1]
        )
        agri_products_service.display_trans_summary(range_data)
    
    if args.crop:
        # 取得特定農產品的交易行情
        print(f"\n正在取得 {args.crop} 的交易行情...")
        crop_data = await agri_products_service.get_trans_by_crop(args.crop)
        agri_products_service.display_trans_summary(crop_data)
    
    if args.market:
        # 取得特定市場的交易行情
        print(f"\n正在取得 {args.market} 市場的交易行情...")
        market_data = await agri_products_service.get_trans_by_market(args.market)
        agri_products_service.display_trans_summary(market_data)
    
    if args.recent:
        # 取得最近幾天的交易行情
        print(f"\n正在取得最近 {args.recent} 天的交易行情...")
        recent_data = await agri_products_service.get_recent_trans(days=args.recent)
        agri_products_service.display_trans_summary(recent_data)
    
    if args.analyze:
        # 分析交易行情資料
        print("\n分析交易行情資料...")
        if args.date:
            data = date_data
        elif args.date_range:
            data = range_data
        elif args.crop:
            data = crop_data
        elif args.market:
            data = market_data
        elif args.recent:
            data = recent_data
        else:
            # 如果沒有指定任何參數，則使用今天的資料
            today = datetime.now().strftime("%Y.%m.%d")
            data = await agri_products_service.get_trans_by_date(today)
        
        analysis = agri_products_service.analyze_trans_data(data)
        agri_products_service.display_analysis(analysis)
    
    if not args.date and not args.date_range and not args.crop and not args.market and not args.recent and not args.analyze:
        # 如果沒有指定任何參數，則取得今天的交易行情
        print("\n正在取得今天的交易行情...")
        today = datetime.now().strftime("%Y.%m.%d")
        today_data = await agri_products_service.get_trans_by_date(today)
        agri_products_service.display_trans_summary(today_data)

async def run_pest_disease_example(client: MOAClient, args):
    """執行病蟲害診斷服務示例"""
    print("執行病蟲害診斷服務示例...")
    pest_disease_service = PestDiseaseService(client)
    
    if args.plant_type:
        # 取得特定植物分類的病蟲害診斷服務問答集
        print(f"\n正在取得 {args.plant_type} 的病蟲害診斷服務問答集...")
        plant_type_data = await pest_disease_service.get_diagnosis_by_plant_type(args.plant_type)
        pest_disease_service.display_diagnosis(plant_type_data)
    
    if args.product:
        # 取得特定品名的病蟲害診斷服務問答集
        print(f"\n正在取得 {args.product} 的病蟲害診斷服務問答集...")
        product_data = await pest_disease_service.get_diagnosis_by_product(args.product)
        pest_disease_service.display_diagnosis(product_data)
    
    if args.search:
        # 搜尋病蟲害診斷服務問答集
        print("\n正在搜尋病蟲害診斷服務問答集...")
        search_data = await pest_disease_service.search_diagnosis(
            plant_type=args.plant_type,
            product_name=args.product
        )
        pest_disease_service.display_diagnosis(search_data)
    
    if args.analyze:
        # 分析病蟲害診斷服務問答集
        print("\n分析病蟲害診斷服務問答集...")
        if args.plant_type:
            data = plant_type_data
        elif args.product:
            data = product_data
        elif args.search:
            data = search_data
        else:
            # 如果沒有指定任何參數，則取得所有病蟲害診斷服務問答集
            data = await pest_disease_service.get_all_diagnosis()
        
        analysis = pest_disease_service.analyze_diagnosis_data(data)
        pest_disease_service.display_analysis(analysis)
    
    if not args.plant_type and not args.product and not args.search and not args.analyze:
        # 如果沒有指定任何參數，則取得所有病蟲害診斷服務問答集
        print("\n正在取得所有病蟲害診斷服務問答集...")
        all_data = await pest_disease_service.get_all_diagnosis()
        pest_disease_service.display_diagnosis(all_data)

async def run_traceability_example(client: MOAClient, args):
    """執行溯源農糧產品追溯系統示例"""
    print("執行溯源農糧產品追溯系統示例...")
    traceability_service = TraceabilityService(client)
    
    if args.trace_code:
        # 取得特定追溯編號的產品資訊
        print(f"\n正在取得追溯編號 {args.trace_code} 的產品資訊...")
        product_data = await traceability_service.get_product_by_trace_code(args.trace_code)
        traceability_service.display_product_summary(product_data)
        
        # 取得特定追溯編號的生產者資訊
        print(f"\n正在取得追溯編號 {args.trace_code} 的生產者資訊...")
        producer_data = await traceability_service.get_producer_by_trace_code(args.trace_code)
        traceability_service.display_producer_summary(producer_data)
    
    if args.product_name:
        # 取得特定產品名稱的產品資訊
        print(f"\n正在取得產品名稱 {args.product_name} 的產品資訊...")
        product_data = await traceability_service.get_product_by_name(args.product_name)
        traceability_service.display_product_summary(product_data)
    
    if args.producer:
        # 取得特定生產者的生產者資訊
        print(f"\n正在取得生產者 {args.producer} 的生產者資訊...")
        producer_data = await traceability_service.get_producer_by_name(args.producer)
        traceability_service.display_producer_summary(producer_data)
    
    if args.address:
        # 取得特定地址的生產者資訊
        print(f"\n正在取得地址 {args.address} 的生產者資訊...")
        producer_data = await traceability_service.get_producer_by_address(args.address)
        traceability_service.display_producer_summary(producer_data)
    
    if args.analyze:
        # 分析生產者資料
        print("\n分析生產者資料...")
        if args.trace_code:
            data = producer_data
        elif args.producer:
            data = producer_data
        elif args.address:
            data = producer_data
        else:
            # 如果沒有指定任何參數，則取得所有生產者資訊
            data = await traceability_service.get_all_producer_info()
        
        analysis = traceability_service.analyze_producer_data(data)
        traceability_service.display_producer_analysis(analysis)
    
    if not args.trace_code and not args.product_name and not args.producer and not args.address and not args.analyze:
        # 如果沒有指定任何參數，則取得所有產品資訊
        print("\n正在取得所有產品資訊...")
        all_product_data = await traceability_service.get_all_product_info()
        traceability_service.display_product_summary(all_product_data)
        
        # 取得所有生產者資訊
        print("\n正在取得所有生產者資訊...")
        all_producer_data = await traceability_service.get_all_producer_info()
        traceability_service.display_producer_summary(all_producer_data)

async def main():
    """主程式"""
    # 解析命令行參數
    parser = argparse.ArgumentParser(description="農產品交易行情 API 示例程式")
    parser.add_argument("-method", choices=["agri_products", "pest_disease", "traceability"], required=True,
                      help="選擇要執行的功能：agri_products（農產品交易行情）、pest_disease（病蟲害診斷服務）或 traceability（溯源農糧產品追溯系統）")
    
    # 通用參數
    parser.add_argument("-analyze", action="store_true", help="是否分析資料")
    
    # 農產品交易行情相關參數
    parser.add_argument("-date", help="交易日期，格式為 YYYY.MM.DD")
    parser.add_argument("-date_range", nargs=2, metavar=("FROM", "TO"), help="日期範圍，格式：YYYY.MM.DD YYYY.MM.DD")
    parser.add_argument("-crop", help="農產品名稱")
    parser.add_argument("-market", help="市場名稱")
    parser.add_argument("-recent", type=int, default=7, help="最近幾天的交易行情，預設為 7 天")
    
    # 病蟲害診斷服務相關參數
    parser.add_argument("-plant_type", help="植物分類")
    parser.add_argument("-product", help="品名")
    parser.add_argument("-search", action="store_true", help="是否搜尋病蟲害診斷服務問答集")
    
    # 溯源農糧產品追溯系統相關參數
    parser.add_argument("-trace_code", help="追溯編號")
    parser.add_argument("-product_name", help="產品名稱")
    parser.add_argument("-producer", help="生產者")
    parser.add_argument("-address", help="聯絡地址")
    
    args = parser.parse_args()
    
    # 載入環境變數
    load_dotenv()
    
    # 從環境變數獲取 API 金鑰
    api_key = os.getenv("MOA_API_KEY")
    
    try:
        # 建立 API 配置
        config = MOAConfig(api_key=api_key)
        
        # 建立 API 客戶端
        client = MOAClient(config)
        
        # 根據選擇的方法執行相應的示例
        if args.method == "agri_products":
            await run_agri_products_example(client, args)
        elif args.method == "pest_disease":
            await run_pest_disease_example(client, args)
        elif args.method == "traceability":
            await run_traceability_example(client, args)
    except Exception as e:
        print(f"執行時發生錯誤: {str(e)}")
        return

if __name__ == "__main__":
    asyncio.run(main()) 
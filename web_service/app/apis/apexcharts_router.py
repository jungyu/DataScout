#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ApexCharts 相關 API 路由。
提供各類 ApexCharts 圖表的範例數據和配置。
"""

import os
import json
import logging
from typing import Dict, Any, List, Union
from fastapi import APIRouter, HTTPException

# 初始化路由器
apexcharts_router = APIRouter()

# 設置日誌
logger = logging.getLogger(__name__)

# 範例檔案路徑
EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'examples')

@apexcharts_router.get("/examples")
async def get_examples() -> Dict[str, List[Dict[str, str]]]:
    """
    獲取所有可用的 ApexCharts 範例清單
    """
    try:
        examples = []
        
        # 讀取 examples 目錄中的所有 JSON 文件
        if os.path.isdir(EXAMPLES_DIR):
            files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith('.json') and f.startswith('apexcharts_')]
            
            for file in files:
                # 從文件名中解析圖表類型和資料描述
                parts = file.replace('apexcharts_', '').replace('.json', '').split('_')
                if len(parts) >= 2:
                    chart_type = parts[0]
                    data_desc = '_'.join(parts[1:])
                    
                    examples.append({
                        "id": file.replace('.json', ''),
                        "file": file,
                        "type": chart_type,
                        "description": data_desc.capitalize(),
                        "path": f"/static/examples/{file}"
                    })
            
            # 按圖表類型排序
            examples.sort(key=lambda x: x['type'])
        
        return {
            "count": len(examples),
            "examples": examples
        }
    except Exception as e:
        logger.error(f"獲取 ApexCharts 範例時出錯: {e}")
        raise HTTPException(status_code=500, detail=f"獲取範例失敗: {str(e)}")

@apexcharts_router.get("/example/{example_id}")
async def get_example_data(example_id: str) -> Dict[str, Any]:
    """
    獲取特定 ApexCharts 範例的數據
    """
    try:
        file_name = f"{example_id}.json"
        file_path = os.path.join(EXAMPLES_DIR, file_name)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"找不到範例: {example_id}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return {
            "id": example_id,
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取 ApexCharts 範例數據時出錯: {e}")
        raise HTTPException(status_code=500, detail=f"獲取範例數據失敗: {str(e)}")

@apexcharts_router.get("/types")
async def get_chart_types() -> Dict[str, Union[int, List[str]]]:
    """
    獲取所有支援的 ApexCharts 圖表類型
    """
    # 按類別組織圖表類型
    chart_types_by_category = {
        "基本圖表類型": [
            "line", "area", "bar", "barHorizontal", "scatter", "pie", 
            "donut", "radar", "heatmap", "treemap"
        ],
        "進階圖表類型": [
            "candlestick", "boxPlot", "bubble", "polarArea", "rangeBar", 
            "rangeArea", "radialBar", "funnel"
        ],
        "時間序列與監控圖表": [
            "timeSeries", "timeSeriesArea", "syncCharts", "stepline", "mixedTime"
        ],
        "比較與分析圖表": [
            "groupedBar", "stackedBar", "percentStackedBar", "mixedChart", 
            "candlestickVolume", "heatmapLine", "multiYAxis", "technicalChart"
        ],
        "動態更新圖表": [
            "realtimeLine", "realtimeDashboard", "dynamicPie", "streamingLine"
        ]
    }
    
    # 獲取所有圖表類型的平坦列表
    all_chart_types = []
    for category_types in chart_types_by_category.values():
        all_chart_types.extend(category_types)
    
    return {
        "count": len(all_chart_types),
        "types": all_chart_types,
        "categories": chart_types_by_category
    }

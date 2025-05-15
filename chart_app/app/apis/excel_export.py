#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel 匯出 API 模組
提供將圖表資料匯出為 Excel 檔案的功能
"""

import io
import pandas as pd
import logging
from fastapi import APIRouter, Body, Response, HTTPException
from typing import List, Dict, Any, Optional

# 配置日誌
logger = logging.getLogger("chart_app.excel_export")

router = APIRouter()

def normalize_array_lengths(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    規範化 Chart.js 數據中的陣列長度，確保所有陣列長度一致
    
    Args:
        data: Chart.js 格式的圖表數據
        
    Returns:
        Dict[str, Any]: 處理後的數據
    """
    result = data.copy()
    
    # 檢查是否有 labels 和 datasets
    if "labels" not in result or not isinstance(result["labels"], list):
        logger.warning("JSON 數據中缺少 labels 字段或不是陣列格式")
        return result
        
    if "datasets" not in result or not isinstance(result["datasets"], list) or len(result["datasets"]) == 0:
        logger.warning("JSON 數據中缺少 datasets 字段或不是有效的陣列格式")
        return result
    
    # 獲取 labels 長度作為參考
    label_length = len(result["labels"])
    
    # 檢查並調整每個數據集
    for dataset in result["datasets"]:
        if "data" not in dataset or not isinstance(dataset["data"], list):
            logger.warning(f"數據集 '{dataset.get('label', 'unknown')}' 缺少 data 字段或不是陣列格式")
            continue
            
        data_length = len(dataset["data"])
        
        # 如果 data 陣列長度與 labels 不一致
        if data_length != label_length:
            logger.warning(f"數據集 '{dataset.get('label', 'unknown')}' 的數據長度 ({data_length}) 與標籤長度 ({label_length}) 不一致，進行調整")
            
            if data_length > label_length:
                # 如果數據過長，截斷
                dataset["data"] = dataset["data"][:label_length]
                logger.info(f"數據集 '{dataset.get('label', 'unknown')}' 截斷至 {label_length} 項")
            else:
                # 如果數據過短，用 None 填充
                dataset["data"].extend([None] * (label_length - data_length))
                logger.info(f"數據集 '{dataset.get('label', 'unknown')}' 填充至 {label_length} 項")
    
    return result

@router.post("/export-excel/")
async def export_chart_data_to_excel(
    data: Dict[str, Any] = Body(..., description="圖表資料 JSON")
) -> Response:
    """
    匯出圖表資料為 Excel 檔案
    
    Args:
        data: 包含圖表資料的 JSON 物件
        
    Returns:
        Response: Excel 檔案響應
    """
    try:
        # 提取資料
        chart_type = data.get("type", "line")
        
        # 規範化陣列長度，解決「All arrays must be of the same length」錯誤
        normalized_data = normalize_array_lengths(data)
        labels = normalized_data.get("labels", [])
        datasets = normalized_data.get("datasets", [])
        chart_title = normalized_data.get("chartTitle", "圖表")
        
        if not labels or not datasets:
            raise HTTPException(status_code=400, detail="缺少必要的圖表資料")
        
        # 創建 DataFrame
        df_data = {"Labels": labels}
        
        for dataset in datasets:
            label = dataset.get("label", "未命名資料")
            values = dataset.get("data", [])
            df_data[label] = values
            
        df = pd.DataFrame(df_data)
        
        # 創建 Excel 檔案
        excel_buffer = io.BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=f"{chart_type.capitalize()} 圖表", index=False)
            
            # 獲取 xlsxwriter 工作簿和工作表物件
            workbook = writer.book
            worksheet = writer.sheets[f"{chart_type.capitalize()} 圖表"]
            
            # 添加標題欄位格式
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # 應用標題格式
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # 設定列寬
            worksheet.set_column(0, 0, 18)  # 第一列 (Labels)
            worksheet.set_column(1, len(df.columns) - 1, 12)  # 資料列
            
            # 添加圖表
            chart = workbook.add_chart({'type': chart_type})
            
            # 設定圖表資料範圍
            for i in range(1, len(df.columns)):
                chart.add_series({
                    'name':       [f"{chart_type.capitalize()} 圖表", 0, i],
                    'categories': [f"{chart_type.capitalize()} 圖表", 1, 0, len(df.index), 0],
                    'values':     [f"{chart_type.capitalize()} 圖表", 1, i, len(df.index), i],
                })
            
            # 添加圖表標題
            chart.set_title({'name': chart_title})
            
            # 設定圖表大小並插入到工作表
            chart.set_size({'width': 720, 'height': 400})
            worksheet.insert_chart('H2', chart)
            
        # 重置緩衝區指針
        excel_buffer.seek(0)
        
        # 返回 Excel 檔案
        return Response(
            content=excel_buffer.read(),
            headers={
                "Content-Disposition": f'attachment; filename="chart_data.xlsx"',
                "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"匯出 Excel 時發生錯誤: {str(e)}")

@router.post("/normalize-json/")
async def normalize_chart_json(
    data: Dict[str, Any] = Body(..., description="圖表資料 JSON")
) -> Dict[str, Any]:
    """
    規範化 Chart.js JSON 數據中的陣列長度，確保所有陣列長度一致
    
    Args:
        data: 包含圖表資料的 JSON 物件
        
    Returns:
        Dict[str, Any]: 規範化後的 JSON 數據
    """
    try:
        # 規範化陣列長度
        normalized_data = normalize_array_lengths(data)
        
        # 檢查處理結果
        labels = normalized_data.get("labels", [])
        datasets = normalized_data.get("datasets", [])
        
        if not labels or not datasets:
            logger.warning("缺少必要的圖表資料")
            return {"error": "缺少必要的圖表資料", "normalized": False}
        
        # 返回規範化後的數據和處理訊息
        return {
            "data": normalized_data,
            "normalized": True,
            "message": "JSON 數據已成功規範化",
            "label_length": len(labels),
            "dataset_count": len(datasets)
        }
        
    except Exception as e:
        logger.error(f"規範化 JSON 數據時發生錯誤: {str(e)}")
        return {"error": f"處理 JSON 數據時發生錯誤: {str(e)}", "normalized": False}

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FastAPI 主應用程式。
提供網頁渲染、靜態檔案服務、API 端點等功能。
"""

import os
import pandas as pd
import numpy as np
import json
import openpyxl
import sys
from fastapi import FastAPI, Request, UploadFile, File, Query, Form, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
import glob
import io
import uuid
import importlib.util
import logging
import pickle

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', f'chart_app_{datetime.now().strftime("%Y%m%d")}.log'))
    ]
)
logger = logging.getLogger("chart_app")

# 建立 FastAPI 應用實例
app = FastAPI(
    title="Chart App",
    description="FastAPI + TailwindCSS + ChartJS 整合應用",
    version="1.0.0"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源，或指定來源如 ["http://localhost:8000"]
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有方法
    allow_headers=["*"],  # 允許所有頭
)

# 取得基礎目錄路徑
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path("/Users/aaron/Projects/DataScout/data")
DATA_CSV_DIR = DATA_DIR / "csv"
DATA_JSON_DIR = DATA_DIR / "json"
DATA_EXCEL_DIR = DATA_DIR / "excel"
PERSISTENCE_DIR = Path("/Users/aaron/Projects/DataScout/persistence")

# 確保所有需要的目錄存在
os.makedirs(DATA_CSV_DIR, exist_ok=True)
os.makedirs(DATA_JSON_DIR, exist_ok=True)
os.makedirs(DATA_EXCEL_DIR, exist_ok=True)

# 設定模板引擎
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# 設定靜態檔案目錄
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# 建立上傳資料夾（如果不存在）
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
TEMP_DIR = BASE_DIR / "static" / "temp"

for directory in [UPLOAD_DIR, TEMP_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)


# 資料來源類型枚舉
DATA_SOURCE_TYPES = {
    "csv": "CSV 檔案",
    "json": "JSON 檔案",
    "excel": "Excel 檔案",
    "persistence": "持久化存儲",
    "uploaded": "上傳的檔案"
}


def get_data_files(data_type: str) -> List[dict]:
    """
    獲取指定類型的資料檔案
    
    Args:
        data_type (str): 資料類型，可以是 'csv', 'json', 'excel', 'persistence'
        
    Returns:
        List[dict]: 檔案列表，包含檔案名和描述
    """
    files = []
    
    # 根據類型決定檢索路徑
    if data_type == 'csv':
        search_path = DATA_CSV_DIR
        pattern = "*.csv"
    elif data_type == 'json':
        search_path = DATA_JSON_DIR
        pattern = "*.json"
    elif data_type == 'excel':
        search_path = DATA_EXCEL_DIR
        pattern = "*.xlsx"
    elif data_type == 'persistence':
        search_path = PERSISTENCE_DIR
        pattern = "*.pkl"
    elif data_type == 'uploaded':
        search_path = UPLOAD_DIR
        pattern = "*.*"
    else:
        return []
    
    # 遍歷找到的文件
    for file_path in glob.glob(str(search_path / pattern)):
        file_name = os.path.basename(file_path)
        # 建立描述性名稱
        display_name = file_name.replace("_", " ").replace(".", " ").rsplit(" ", 1)[0]
        files.append({
            "filename": file_name,
            "display_name": display_name,
            "path": file_path,
            "type": data_type
        })
    
    # 依文件名排序
    files.sort(key=lambda x: x["filename"])
    return files


def read_data_file(file_path: str, file_type: str) -> pd.DataFrame:
    """
    讀取數據文件並返回 DataFrame
    
    Args:
        file_path (str): 檔案路徑
        file_type (str): 檔案類型 ('csv', 'json', 'excel', 'persistence')
        
    Returns:
        pd.DataFrame: 讀取的數據框
    """
    try:
        # 檢查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return pd.DataFrame()
        
        # 根據文件類型讀取數據
        if file_type == 'csv':
            df = pd.read_csv(file_path)
        elif file_type == 'json':
            df = pd.read_json(file_path)
        elif file_type == 'excel':
            df = pd.read_excel(file_path)
        elif file_type == 'persistence':
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            # 嘗試將持久化數據轉換為 DataFrame
            if isinstance(data, pd.DataFrame):
                df = data
            elif isinstance(data, dict):
                df = pd.DataFrame.from_dict(data)
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                logger.error(f"無法將持久化數據轉換為 DataFrame: {type(data)}")
                return pd.DataFrame()
        else:
            logger.error(f"不支持的文件類型: {file_type}")
            return pd.DataFrame()
        
        # 處理常見的日期列
        date_columns = ['Date', 'DATE', 'date', 'datetime', 'time', 'timestamp', 'Time', 'Timestamp']
        for date_col in date_columns:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        return df
    
    except Exception as e:
        logger.error(f"讀取文件錯誤 ({file_type}): {e}")
        return pd.DataFrame()


@app.get("/")
async def root(request: Request):
    """
    渲染首頁 HTML 模板。

    Args:
        request (Request): FastAPI 請求物件。

    Returns:
        TemplateResponse: 渲染後的 HTML 頁面。
    """
    # 獲取所有類型的數據文件
    csv_files = get_data_files('csv')
    json_files = get_data_files('json')
    excel_files = get_data_files('excel')
    persistence_files = get_data_files('persistence')
    uploaded_files = get_data_files('uploaded')
    
    # 合併所有文件列表
    all_data_files = {
        'csv': csv_files,
        'json': json_files,
        'excel': excel_files,
        'persistence': persistence_files,
        'uploaded': uploaded_files
    }
    
    # 獲取 Chart.js 支援的圖表類型
    chart_types = [
        {"id": "line", "name": "折線圖"},
        {"id": "bar", "name": "長條圖"},
        {"id": "radar", "name": "雷達圖"},
        {"id": "pie", "name": "圓餅圖"},
        {"id": "doughnut", "name": "環形圖"},
        {"id": "polarArea", "name": "極座標圖"},
        {"id": "bubble", "name": "氣泡圖"},
        {"id": "scatter", "name": "散點圖"}
    ]
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request, 
            "title": "資料視覺化平台", 
            "all_data_files": all_data_files,
            "data_source_types": DATA_SOURCE_TYPES,
            "chart_types": chart_types,
            "csv_files": csv_files  # 保留舊的 csv_files 變數以維持相容性
        }
    )


@app.get("/api/chart-data/")
async def chart_data():
    """
    提供圖表資料 API 端點。
    模擬 OLAP 操作並返回適合 Chart.js 使用的格式。

    Returns:
        JSONResponse: 含有圖表資料的 JSON 回應。
    """
    # 建立模擬資料
    np.random.seed(42)  # 確保資料可重現
    dates = pd.date_range(start="2025-01-01", periods=12, freq="M")
    categories = ["產品A", "產品B", "產品C"]
    regions = ["北區", "南區", "東區", "西區"]
    
    # 生成隨機資料
    data = []
    for date in dates:
        for category in categories:
            for region in regions:
                sales = np.random.randint(100, 1000)
                profit = sales * np.random.uniform(0.1, 0.4)
                data.append({
                    "日期": date,
                    "產品": category,
                    "地區": region,
                    "銷售額": sales,
                    "利潤": profit
                })
    
    # 建立 DataFrame
    df = pd.DataFrame(data)
    
    # 執行 OLAP 操作 (pivot_table) - 各產品每月的銷售總和
    pivot_data = df.pivot_table(
        values="銷售額", 
        index="日期", 
        columns="產品", 
        aggfunc="sum"
    )
    
    # 將資料轉換為 Chart.js 格式
    labels = [date.strftime("%Y-%m") for date in pivot_data.index]
    datasets = []
    
    # 為每個產品建立一個數據集
    for product in pivot_data.columns:
        color = {
            "產品A": "rgba(75, 192, 192, 0.6)",
            "產品B": "rgba(153, 102, 255, 0.6)",
            "產品C": "rgba(255, 159, 64, 0.6)"
        }.get(product, "rgba(0, 0, 0, 0.6)")
        
        datasets.append({
            "label": product,
            "data": pivot_data[product].tolist(),
            "backgroundColor": color,
            "borderColor": color.replace("0.6", "1.0"),
            "borderWidth": 1
        })
    
    # 返回 Chart.js 格式的資料
    return JSONResponse(content={
        "labels": labels,
        "datasets": datasets,
        "chartTitle": "各產品每月銷售額"
    })


@app.post("/upload-chart-image/")
async def upload_chart_image(file: UploadFile = File(...)):
    """
    接收前端上傳的圖表截圖。

    Args:
        file (UploadFile): 上傳的檔案。

    Returns:
        dict: 包含操作狀態和保存路徑的字典。
    """
    try:
        # 生成唯一的檔案名稱
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chart_{timestamp}_{file.filename}"
        filepath = UPLOAD_DIR / filename
        
        # 保存檔案
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {
            "status": "success",
            "message": "圖片上傳成功",
            "filepath": f"/static/uploads/{filename}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"圖片上傳失敗: {str(e)}"
        }


@app.get("/api/csv-files/")
async def get_available_csv_files():
    """
    獲取可用的 CSV 文件列表
    
    Returns:
        dict: 包含 CSV 文件列表的字典
    """
    csv_files = get_data_files('csv')
    return {"csv_files": csv_files}


@app.get("/api/csv-data/")
async def get_csv_data(filename: str = Query(..., description="CSV 文件名")):
    """
    讀取指定的 CSV 文件並返回圖表所需的數據
    
    Args:
        filename (str): CSV 文件名
        
    Returns:
        dict: 圖表所需的數據格式
    """
    # 構建文件完整路徑
    file_path = DATA_CSV_DIR / filename
    
    # 檢查文件是否存在
    if not os.path.exists(file_path):
        return JSONResponse(
            status_code=404,
            content={"error": f"文件 {filename} 不存在"}
        )
    
    # 讀取 CSV 文件
    df = read_data_file(file_path, 'csv')
    
    # 檢查是否成功讀取
    if df.empty:
        return JSONResponse(
            status_code=500,
            content={"error": f"無法讀取文件 {filename}"}
        )
    
    # 檢測日期列
    date_column = None
    for col in ['Date', 'DATE', 'date']:
        if col in df.columns:
            date_column = col
            break
    
    # 如果沒有日期列，使用索引作為日期
    if date_column is None:
        labels = df.index.astype(str).tolist()
    else:
        # 將日期轉換為字符串格式
        if pd.api.types.is_datetime64_any_dtype(df[date_column]):
            labels = df[date_column].dt.strftime('%Y-%m-%d').tolist()
        else:
            labels = df[date_column].astype(str).tolist()
    
    # 決定要繪製的數據列
    value_columns = []
    
    # 優先選擇這些列（如果存在）
    priority_columns = ['Close', 'Price', 'Value', 'CLOSE', 'PRICE', 'VALUE']
    for col in priority_columns:
        if col in df.columns:
            value_columns.append(col)
            break
    
    # 如果沒有找到優先列，則選擇數值型的列（最多5個）
    if not value_columns:
        numeric_cols = df.select_dtypes(include=['number']).columns
        # 排除日期列（如果它是數值型的）
        if date_column and date_column in numeric_cols:
            numeric_cols = numeric_cols.drop(date_column)
        
        # 取前5個數值列
        value_columns = numeric_cols[:min(5, len(numeric_cols))].tolist()
    
    # 如果有日期列，從數據框中排除它
    if date_column and date_column in df.columns:
        df_values = df.drop(columns=[date_column])
    else:
        df_values = df
    
    # 只保留數值型列
    df_values = df_values.select_dtypes(include=['number'])
    
    # 創建數據集
    datasets = []
    color_palette = [
        "rgba(75, 192, 192, 0.6)",    # 綠松石色
        "rgba(153, 102, 255, 0.6)",   # 紫色
        "rgba(255, 159, 64, 0.6)",    # 橙色
        "rgba(54, 162, 235, 0.6)",    # 藍色
        "rgba(255, 99, 132, 0.6)",    # 粉色
        "rgba(255, 206, 86, 0.6)",    # 黃色
        "rgba(199, 199, 199, 0.6)",   # 灰色
        "rgba(83, 102, 255, 0.6)",    # 暗藍色
        "rgba(255, 99, 71, 0.6)",     # 西紅柿色
        "rgba(50, 205, 50, 0.6)"      # 石灰色
    ]
    
    # 最多選擇10個列進行繪圖
    for i, column in enumerate(df_values.columns[:10]):
        # 檢查列的數據類型是否為數值型
        if np.issubdtype(df_values[column].dtype, np.number):
            color_index = i % len(color_palette)
            color = color_palette[color_index]
            
            # 過濾掉 NaN 值（使用 ffill 和 bfill 替代已棄用的 fillna(method=)）
            valid_data = df_values[column].ffill().bfill().tolist()
            
            datasets.append({
                "label": str(column),
                "data": valid_data,
                "backgroundColor": color,
                "borderColor": color.replace("0.6", "1.0"),
                "borderWidth": 1
            })
    
    # 獲取文件的顯示名稱
    file_display_name = filename.replace("_", " ").replace(".csv", "")
    
    # 返回 Chart.js 格式的資料
    return JSONResponse(content={
        "labels": labels,
        "datasets": datasets,
        "chartTitle": file_display_name
    })


@app.get("/api/csv-structure/")
async def get_csv_structure(filename: str = Query(..., description="CSV 文件名")):
    """
    獲取 CSV 文件結構信息
    
    Args:
        filename (str): CSV 文件名
        
    Returns:
        dict: 文件結構信息
    """
    # 構建文件完整路徑
    file_path = DATA_CSV_DIR / filename
    
    # 檢查文件是否存在
    if not os.path.exists(file_path):
        return JSONResponse(
            status_code=404,
            content={"error": f"文件 {filename} 不存在"}
        )
    
    # 讀取 CSV 文件
    df = read_data_file(file_path, 'csv')
    
    # 檢查是否成功讀取
    if df.empty:
        return JSONResponse(
            status_code=500,
            content={"error": f"無法讀取文件 {filename}"}
        )        # 獲取列信息
        columns = []
        for col in df.columns:
            columns.append({
                "name": col,
                "dtype": str(df[col].dtype),
                "has_nulls": bool(df[col].isna().any()),  # 直接轉換為布林值
                "unique_values": int(df[col].nunique()),  # 直接轉換為整數
                "sample": str(df[col].iloc[0]) if not df[col].empty else ""
            })
    
    return {
        "filename": filename,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": columns
    }


@app.get("/api/data-files/")
async def get_all_data_files():
    """
    獲取所有類型的可用數據文件列表
    
    Returns:
        dict: 包含所有數據文件列表的字典
    """
    return {
        "data_files": {
            "csv": get_data_files('csv'),
            "json": get_data_files('json'),
            "excel": get_data_files('excel'),
            "persistence": get_data_files('persistence'),
            "uploaded": get_data_files('uploaded')
        },
        "data_source_types": DATA_SOURCE_TYPES
    }


@app.get("/api/file-data/")
async def get_file_data(
    filename: str = Query(..., description="文件名"),
    file_type: str = Query(..., description="文件類型 (csv, json, excel, persistence, uploaded)")
):
    """
    讀取指定的數據文件並返回圖表所需的數據
    
    Args:
        filename (str): 文件名
        file_type (str): 文件類型
        
    Returns:
        dict: 圖表所需的數據格式
    """
    try:
        # 根據文件類型構建完整路徑
        if file_type == 'csv':
            file_path = DATA_CSV_DIR / filename
        elif file_type == 'json':
            file_path = DATA_JSON_DIR / filename
        elif file_type == 'excel':
            file_path = DATA_EXCEL_DIR / filename
        elif file_type == 'persistence':
            file_path = PERSISTENCE_DIR / filename
        elif file_type == 'uploaded':
            file_path = UPLOAD_DIR / filename
        else:
            return JSONResponse(
                status_code=400,
                content={"error": f"不支援的文件類型: {file_type}"}
            )
        
        # 檢查文件是否存在
        if not os.path.exists(file_path):
            return JSONResponse(
                status_code=404,
                content={"error": f"文件 {filename} 不存在"}
            )
        
        # 讀取文件數據
        df = read_data_file(str(file_path), file_type)
        
        # 檢查是否成功讀取
        if df.empty:
            return JSONResponse(
                status_code=500,
                content={"error": f"無法讀取文件 {filename}"}
            )
        
        # 檢測日期列
        date_column = None
        date_columns = ['Date', 'DATE', 'date', 'datetime', 'time', 'timestamp', 'Time', 'Timestamp']
        for col in date_columns:
            if col in df.columns:
                date_column = col
                break
        
        # 如果沒有日期列，使用索引作為標籤
        if date_column is None:
            labels = df.index.astype(str).tolist()
        else:
            # 將日期轉換為字符串格式
            if pd.api.types.is_datetime64_any_dtype(df[date_column]):
                labels = df[date_column].dt.strftime('%Y-%m-%d').tolist()
            else:
                labels = df[date_column].astype(str).tolist()
        
        # 決定要繪製的數據列
        value_columns = []
        
        # 優先選擇這些列（如果存在）
        priority_columns = [
            'Close', 'Price', 'Value', 'CLOSE', 'PRICE', 'VALUE', 
            'Sales', 'Revenue', 'Profit', 'Amount', 'Count', 'Total'
        ]
        
        # 嘗試查找優先列
        for col in priority_columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                value_columns.append(col)
        
        # 如果沒有找到優先列，則選擇所有數值型的列（最多10個）
        if not value_columns:
            numeric_cols = df.select_dtypes(include=['number']).columns
            # 排除日期列（如果它是數值型的）
            if date_column and date_column in numeric_cols:
                numeric_cols = numeric_cols.drop(date_column)
            
            # 取前10個數值列
            value_columns = numeric_cols[:min(10, len(numeric_cols))].tolist()
        
        # 如果有日期列，從數據框中排除它
        if date_column and date_column in df.columns:
            df_values = df.drop(columns=[date_column])
        else:
            df_values = df
        
        # 只保留數值型列
        df_values = df_values.select_dtypes(include=['number'])
        
        # 創建數據集
        datasets = []
        color_palette = [
            "rgba(75, 192, 192, 0.6)",    # 綠松石色
            "rgba(153, 102, 255, 0.6)",   # 紫色
            "rgba(255, 159, 64, 0.6)",    # 橙色
            "rgba(54, 162, 235, 0.6)",    # 藍色
            "rgba(255, 99, 132, 0.6)",    # 粉色
            "rgba(255, 206, 86, 0.6)",    # 黃色
            "rgba(199, 199, 199, 0.6)",   # 灰色
            "rgba(83, 102, 255, 0.6)",    # 暗藍色
            "rgba(255, 99, 71, 0.6)",     # 西紅柿色
            "rgba(50, 205, 50, 0.6)"      # 石灰色
        ]
        
        # 最多選擇10個列進行繪圖
        columns_to_plot = value_columns if value_columns else df_values.columns[:min(10, len(df_values.columns))]
        
        for i, column in enumerate(columns_to_plot):
            # 確保列存在於 DataFrame 中
            if column not in df_values.columns:
                continue
                
            # 檢查列的數據類型是否為數值型
            if np.issubdtype(df_values[column].dtype, np.number):
                color_index = i % len(color_palette)
                color = color_palette[color_index]
                
                # 過濾掉 NaN 值（使用新的方法替代已棄用的 fillna 方法）
                valid_data = df_values[column].ffill().bfill().tolist()
                
                # 為特定圖表類型添加額外數據
                # 例如，散點圖需要 x, y 坐標
                if len(columns_to_plot) >= 2 and i == 0:
                    # 為第一個數據集添加額外屬性，可用於散點圖、氣泡圖等
                    datasets.append({
                        "label": str(column),
                        "data": valid_data,
                        "backgroundColor": color,
                        "borderColor": color.replace("0.6", "1.0"),
                        "borderWidth": 1,
                        # 添加散點圖、氣泡圖可能需要的屬性
                        "pointRadius": 5,
                        "pointHoverRadius": 7
                    })
                else:
                    datasets.append({
                        "label": str(column),
                        "data": valid_data,
                        "backgroundColor": color,
                        "borderColor": color.replace("0.6", "1.0"),
                        "borderWidth": 1
                    })
        
        # 獲取文件的顯示名稱
        file_display_name = filename.replace("_", " ").split(".")[0]
        
        # 返回 Chart.js 格式的資料
        return JSONResponse(content={
            "labels": labels,
            "datasets": datasets,
            "chartTitle": file_display_name,
            "metadata": {
                "filename": filename,
                "file_type": file_type,
                "row_count": len(df),
                "column_count": len(df.columns)
            }
        })
        
    except Exception as e:
        logger.error(f"處理文件 {filename} 時發生錯誤: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"處理文件時發生錯誤: {str(e)}"}
        )


@app.get("/api/file-structure/")
async def get_file_structure(
    filename: str = Query(..., description="文件名"),
    file_type: str = Query(..., description="文件類型 (csv, json, excel, persistence, uploaded)")
):
    """
    獲取數據文件結構信息
    
    Args:
        filename (str): 文件名
        file_type (str): 文件類型
        
    Returns:
        dict: 文件結構信息
    """
    try:
        # 根據文件類型構建完整路徑
        if file_type == 'csv':
            file_path = DATA_CSV_DIR / filename
        elif file_type == 'json':
            file_path = DATA_JSON_DIR / filename
        elif file_type == 'excel':
            file_path = DATA_EXCEL_DIR / filename
        elif file_type == 'persistence':
            file_path = PERSISTENCE_DIR / filename
        elif file_type == 'uploaded':
            file_path = UPLOAD_DIR / filename
        else:
            return JSONResponse(
                status_code=400,
                content={"error": f"不支援的文件類型: {file_type}"}
            )
        
        # 檢查文件是否存在
        if not os.path.exists(file_path):
            return JSONResponse(
                status_code=404,
                content={"error": f"文件 {filename} 不存在"}
            )
        
        # 讀取文件數據
        df = read_data_file(str(file_path), file_type)
        
        # 檢查是否成功讀取
        if df.empty:
            return JSONResponse(
                status_code=500,
                content={"error": f"無法讀取文件 {filename}"}
            )
        
        # 獲取基本統計數據
        stats = {}
        for col in df.select_dtypes(include=['number']).columns:
            stats[col] = {
                "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                "median": float(df[col].median()) if not pd.isna(df[col].median()) else None
            }
        
        # 獲取列信息
        columns = []
        for col in df.columns:
            # 安全地獲取 null 值和唯一值信息
            has_nulls = bool(df[col].isna().any())  # 直接轉換為布林值
            unique_count = int(df[col].nunique())   # 直接轉換為整數
            
            col_info = {
                "name": col,
                "dtype": str(df[col].dtype),
                "has_nulls": has_nulls,
                "unique_values": unique_count,
                "sample": str(df[col].iloc[0]) if not df[col].empty else ""
            }
            
            # 額外增加數值列的統計數據
            if col in stats:
                col_info["statistics"] = stats[col]
                
            columns.append(col_info)
        
        return {
            "filename": filename,
            "file_type": file_type,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": columns
        }
        
    except Exception as e:
        logger.error(f"取得文件 {filename} 結構時發生錯誤: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"取得文件結構時發生錯誤: {str(e)}"}
        )


@app.post("/api/upload-file/")
async def upload_data_file(
    file: UploadFile = File(...),
    file_type: str = Form(..., description="檔案類型 (csv, json, excel)")
):
    """
    上傳數據文件並保存到對應目錄
    
    Args:
        file (UploadFile): 上傳的文件
        file_type (str): 文件類型
    
    Returns:
        dict: 操作結果
    """
    try:
        # 檢查文件類型是否支援
        if file_type not in ['csv', 'json', 'excel']:
            return JSONResponse(
                status_code=400,
                content={"error": f"不支援的文件類型: {file_type}"}
            )
        
        # 生成唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = file.filename
        filename = f"{timestamp}_{original_filename}"
        
        # 根據文件類型決定保存的目錄
        if file_type == 'csv':
            save_dir = UPLOAD_DIR
            # 確保檔名以 .csv 結尾
            if not filename.lower().endswith('.csv'):
                filename += '.csv'
        elif file_type == 'json':
            save_dir = UPLOAD_DIR
            # 確保檔名以 .json 結尾
            if not filename.lower().endswith('.json'):
                filename += '.json'
        elif file_type == 'excel':
            save_dir = UPLOAD_DIR
            # 確保檔名以 .xlsx 結尾
            if not filename.lower().endswith(('.xlsx', '.xls')):
                filename += '.xlsx'
        
        # 組合完整保存路徑
        file_path = save_dir / filename
        
        # 保存上傳的文件
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        # 嘗試讀取文件以驗證其有效性
        df = read_data_file(str(file_path), file_type)
        if df.empty:
            # 如果無法讀取，刪除文件並返回錯誤
            os.remove(file_path)
            return JSONResponse(
                status_code=400,
                content={"error": "無法解析上傳的文件，請確保文件格式正確"}
            )
        
        # 返回成功信息
        return {
            "status": "success",
            "message": "文件上傳成功",
            "filename": filename,
            "file_type": file_type,
            "row_count": len(df),
            "column_count": len(df.columns)
        }
        
    except Exception as e:
        logger.error(f"上傳文件時發生錯誤: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"上傳文件時發生錯誤: {str(e)}"}
        )


@app.post("/api/olap-operation/")
async def perform_olap_operation(
    filename: str = Form(..., description="文件名"),
    file_type: str = Form(..., description="文件類型 (csv, json, excel, persistence, uploaded)"),
    operation: str = Form(..., description="OLAP操作類型 (groupby, pivot_table, rolling)"),
    group_columns: str = Form(..., description="分組列，逗號分隔"),
    value_column: str = Form(..., description="值列"),
    agg_function: str = Form("sum", description="聚合函數 (sum, mean, count, min, max)"),
    rolling_window: int = Form(None, description="滾動窗口大小 (僅用於 rolling 操作)"),
    pivot_index: str = Form(None, description="透視表索引列 (僅用於 pivot_table)"),
    pivot_columns: str = Form(None, description="透視表列 (僅用於 pivot_table)")
):
    """
    對數據文件執行 OLAP 操作並返回結果
    
    Args:
        filename (str): 文件名
        file_type (str): 文件類型
        operation (str): OLAP 操作類型
        group_columns (str): 分組列，逗號分隔
        value_column (str): 值列
        agg_function (str): 聚合函數
        rolling_window (int): 滾動窗口大小
        pivot_index (str): 透視表索引列
        pivot_columns (str): 透視表列
        
    Returns:
        JSONResponse: OLAP 操作結果
    """
    try:
        # 根據文件類型構建完整路徑
        if file_type == 'csv':
            file_path = DATA_CSV_DIR / filename
        elif file_type == 'json':
            file_path = DATA_JSON_DIR / filename
        elif file_type == 'excel':
            file_path = DATA_EXCEL_DIR / filename
        elif file_type == 'persistence':
            file_path = PERSISTENCE_DIR / filename
        elif file_type == 'uploaded':
            file_path = UPLOAD_DIR / filename
        else:
            return JSONResponse(
                status_code=400,
                content={"error": f"不支援的文件類型: {file_type}"}
            )
        
        # 檢查文件是否存在
        if not os.path.exists(file_path):
            return JSONResponse(
                status_code=404,
                content={"error": f"文件 {filename} 不存在"}
            )
        
        # 讀取文件數據
        df = read_data_file(str(file_path), file_type)
        
        # 檢查是否成功讀取
        if df.empty:
            return JSONResponse(
                status_code=500,
                content={"error": f"無法讀取文件 {filename}"}
            )
        
        # 解析分組列
        try:
            group_cols = [col.strip() for col in group_columns.split(',') if col.strip()]
        except:
            group_cols = []
        
        # 執行 OLAP 操作
        result_df = None
        
        # 檢查所有必要的列都存在
        for col in [*group_cols, value_column]:
            if col and col not in df.columns:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"列 '{col}' 在數據中不存在"}
                )
        
        # 執行 groupby 操作
        if operation == 'groupby' and group_cols:
            try:
                # 定義聚合函數
                agg_funcs = {
                    "sum": "sum", 
                    "mean": "mean", 
                    "count": "count", 
                    "min": "min", 
                    "max": "max"
                }
                
                agg_func = agg_funcs.get(agg_function, "sum")
                
                # 執行分組聚合
                result_df = df.groupby(group_cols)[value_column].agg(agg_func).reset_index()
            except Exception as e:
                logger.error(f"執行 groupby 操作時發生錯誤: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"執行 groupby 操作時發生錯誤: {str(e)}"}
                )
        
        # 執行 pivot_table 操作
        elif operation == 'pivot_table' and pivot_index and pivot_columns:
            try:
                # 定義聚合函數
                agg_func = {
                    "sum": np.sum, 
                    "mean": np.mean, 
                    "count": "count", 
                    "min": np.min, 
                    "max": np.max
                }.get(agg_function, np.sum)
                
                # 執行透視表操作
                result_df = pd.pivot_table(
                    df, 
                    values=value_column, 
                    index=pivot_index, 
                    columns=pivot_columns, 
                    aggfunc=agg_func,
                    fill_value=0
                ).reset_index()
            except Exception as e:
                logger.error(f"執行 pivot_table 操作時發生錯誤: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"執行 pivot_table 操作時發生錯誤: {str(e)}"}
                )
        
        # 執行 rolling 操作
        elif operation == 'rolling' and rolling_window and rolling_window > 0:
            try:
                # 確保數據按時間排序
                date_column = None
                for col in ['Date', 'DATE', 'date', 'datetime', 'timestamp', 'Time', 'Timestamp']:
                    if col in df.columns:
                        date_column = col
                        break
                
                if date_column:
                    df = df.sort_values(by=date_column)
                
                # 執行滾動計算
                rolling_result = df[value_column].rolling(window=rolling_window).agg(agg_function)
                result_df = pd.DataFrame({
                    "原始值": df[value_column],
                    f"{rolling_window}期{agg_function}": rolling_result
                })
                
                # 如果有日期列，加入結果中
                if date_column:
                    result_df[date_column] = df[date_column]
            except Exception as e:
                logger.error(f"執行 rolling 操作時發生錯誤: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"執行 rolling 操作時發生錯誤: {str(e)}"}
                )
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "無效的操作或參數不足"}
            )
        
        # 處理結果為空的情況
        if result_df is None or result_df.empty:
            return JSONResponse(
                status_code=500,
                content={"error": "OLAP 操作無結果"}
            )
        
        # 格式化結果為 Chart.js 所需格式
        # 檢測日期列
        date_column = None
        for col in result_df.columns:
            if pd.api.types.is_datetime64_any_dtype(result_df[col]):
                date_column = col
                break
        
        # 處理標籤
        if date_column:
            labels = result_df[date_column].dt.strftime('%Y-%m-%d').tolist()
        elif len(group_cols) > 0:
            # 使用第一個分組列作為標籤
            labels = result_df[group_cols[0]].astype(str).tolist()
        else:
            # 使用索引作為標籤
            labels = result_df.index.astype(str).tolist()
        
        # 創建數據集
        datasets = []
        color_palette = [
            "rgba(75, 192, 192, 0.6)",    # 綠松石色
            "rgba(153, 102, 255, 0.6)",   # 紫色
            "rgba(255, 159, 64, 0.6)",    # 橙色
            "rgba(54, 162, 235, 0.6)",    # 藍色
            "rgba(255, 99, 132, 0.6)",    # 粉色
            "rgba(255, 206, 86, 0.6)",    # 黃色
            "rgba(199, 199, 199, 0.6)",   # 灰色
            "rgba(83, 102, 255, 0.6)",    # 暗藍色
            "rgba(255, 99, 71, 0.6)",     # 西紅柿色
            "rgba(50, 205, 50, 0.6)"      # 石灰色
        ]
        
        # 選擇要繪製的列
        numeric_cols = result_df.select_dtypes(include=['number']).columns
        if date_column and date_column in numeric_cols:
            numeric_cols = numeric_cols.drop(date_column)
            
        # 最多選擇10個列進行繪圖
        for i, column in enumerate(numeric_cols[:10]):
            color_index = i % len(color_palette)
            color = color_palette[color_index]
            
            # 過濾掉 NaN 值
            valid_data = result_df[column].fillna(0).tolist()
            
            datasets.append({
                "label": str(column),
                "data": valid_data,
                "backgroundColor": color,
                "borderColor": color.replace("0.6", "1.0"),
                "borderWidth": 1
            })
        
        # 返回 Chart.js 格式的資料
        operation_title = {
            'groupby': f"{', '.join(group_cols)} 分組 {value_column} {agg_function}",
            'pivot_table': f"{pivot_index} vs {pivot_columns} 透視表 ({value_column} {agg_function})",
            'rolling': f"{value_column} {rolling_window}期{agg_function}滾動分析"
        }.get(operation, "OLAP 分析結果")
        
        return JSONResponse(content={
            "labels": labels,
            "datasets": datasets,
            "chartTitle": operation_title,
            "metadata": {
                "operation": operation,
                "params": {
                    "group_columns": group_columns,
                    "value_column": value_column,
                    "agg_function": agg_function,
                    "rolling_window": rolling_window,
                    "pivot_index": pivot_index,
                    "pivot_columns": pivot_columns
                }
            }
        })
        
    except Exception as e:
        logger.error(f"執行 OLAP 操作時發生錯誤: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"執行 OLAP 操作時發生錯誤: {str(e)}"}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

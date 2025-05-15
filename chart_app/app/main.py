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
from fastapi import FastAPI, Request, UploadFile, File, Query, Form, HTTPException, Depends, Body
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
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
from .json_adapter import ChartJSAdapter
from .apis import excel_export_router, example_router

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

# 註冊 API 路由
app.include_router(excel_export_router)
app.include_router(example_router)

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

# 建立上傳資料夾（如果不存在）
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
TEMP_DIR = BASE_DIR / "static" / "temp"

for directory in [UPLOAD_DIR, TEMP_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# 設定靜態檔案目錄
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


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
        file_type (str): 檔案類型 ('csv', 'json', 'excel', 'persistence', 'uploaded')
        
    Returns:
        pd.DataFrame: 讀取的數據框
    """
    try:
        # 檢查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return pd.DataFrame()
        
        # 如果是上傳的檔案，根據副檔名判斷真實類型
        if file_type == 'uploaded':
            file_ext = os.path.splitext(file_path)[1].lower()
            logger.info(f"上傳檔案副檔名: {file_ext}")
            
            if file_ext == '.csv':
                actual_type = 'csv'
            elif file_ext in ['.json']:
                actual_type = 'json'
            elif file_ext in ['.xlsx', '.xls']:
                actual_type = 'excel'
            else:
                # 無法確定檔案類型時，嘗試猜測
                actual_type = 'csv'  # 預設為 CSV
                logger.warning(f"無法確定檔案類型，嘗試以CSV格式讀取: {file_path}")
        else:
            actual_type = file_type
            
        logger.info(f"讀取檔案: {file_path}, 類型: {actual_type}")
            
        # 根據文件類型讀取數據
        if actual_type == 'csv':
            df = pd.read_csv(file_path)
        elif actual_type == 'json':
            # 特殊處理 JSON 檔案，可能是 Chart.js 格式
            try:
                # 先嘗試標準 JSON 解析
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                # 檢查是否是 Chart.js 格式的 JSON
                if isinstance(json_data, dict) and 'labels' in json_data and 'datasets' in json_data:
                    # 是 Chart.js 格式，規範化陣列長度
                    labels = json_data.get('labels', [])
                    datasets = json_data.get('datasets', [])
                    
                    # 創建一個字典，包含所有數據
                    data_dict = {'labels': labels}
                    
                    # 添加每個數據集的數據，確保長度一致
                    for dataset in datasets:
                        label = dataset.get('label', 'Data')
                        data_values = dataset.get('data', [])
                        
                        # 確保數據長度與 labels 一致
                        if len(data_values) > len(labels):
                            # 截斷過長的數據
                            data_values = data_values[:len(labels)]
                            logger.warning(f"JSON 檔案 {file_path} 中的數據長度大於標籤長度，已截斷")
                        elif len(data_values) < len(labels):
                            # 填充過短的數據
                            data_values.extend([None] * (len(labels) - len(data_values)))
                            logger.warning(f"JSON 檔案 {file_path} 中的數據長度小於標籤長度，已填充")
                        
                        data_dict[label] = data_values
                    
                    # 創建 DataFrame
                    df = pd.DataFrame(data_dict)
                else:
                    # 不是 Chart.js 格式，使用標準解析
                    df = pd.read_json(file_path)
            except Exception as e:
                logger.error(f"讀取 JSON 檔案錯誤: {e}")
                df = pd.DataFrame()
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


@app.get("/docs/chart-format")
async def chart_json_format(request: Request):
    """
    顯示 Chart.js JSON 格式文檔。
    
    Args:
        request (Request): FastAPI 請求物件。
        
    Returns:
        TemplateResponse: 渲染後的文檔頁面。
    """
    # 讀取 Markdown 文件
    try:
        with open(BASE_DIR / "docs" / "chart_formats.md", "r", encoding="utf-8") as f:
            content = f.read()
            
        # 簡單地將 Markdown 內容轉換為 HTML (可以使用更完整的 MD 解析器)
        import re
        
        # 處理標題
        content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        
        # 處理代碼塊
        content = re.sub(r'```json(.*?)```', r'<pre><code class="language-json">\1</code></pre>', content, flags=re.DOTALL)
        content = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', content, flags=re.DOTALL)
        
        # 處理列表
        content = re.sub(r'^\- (.*?)$', r'<li>\1</li>', content, flags=re.MULTILINE)
        content = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\g<0></ul>', content, flags=re.DOTALL)
        
        # 處理表格
        # 這部分需要更複雜的解析，這裡只做一個簡單的實現
        table_pattern = r'\| (.*?) \|\n\|(.*?)\|\n((?:\|.*?\|\n)+)'
        
        def replace_table(match):
            headers = [h.strip() for h in match.group(1).split('|')]
            header_html = ''.join([f"<th>{h}</th>" for h in headers])
            
            rows_text = match.group(3)
            rows = []
            for row_text in rows_text.strip().split('\n'):
                cells = [cell.strip() for cell in row_text.strip('|').split('|')]
                row_html = ''.join([f"<td>{cell}</td>" for cell in cells])
                rows.append(f"<tr>{row_html}</tr>")
            
            return f'<table class="table-auto border-collapse w-full"><thead><tr>{header_html}</tr></thead><tbody>{"".join(rows)}</tbody></table>'
        
        content = re.sub(table_pattern, replace_table, content)
        
        # 處理段落
        content = re.sub(r'^([^<\n].*?)$', r'<p>\1</p>', content, flags=re.MULTILINE)
        
        # 創建一個簡單的 HTML 頁面
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Chart.js JSON 格式規範</title>
            <link href="{{ url_for('static', path='/css/output.css') }}" rel="stylesheet">
            <style>
                body {{ font-family: 'Noto Sans TC', sans-serif; line-height: 1.6; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                code {{ background-color: #f0f0f0; padding: 2px 4px; border-radius: 4px; }}
                pre {{ background-color: #f5f5f5; padding: 16px; border-radius: 8px; overflow-x: auto; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body class="bg-gray-100">
            <header class="bg-blue-600 shadow-md p-4 text-white">
                <div class="container mx-auto flex justify-between items-center">
                    <h1 class="text-2xl font-bold">Chart.js JSON 格式規範</h1>
                    <a href="/" class="text-white hover:text-gray-200">返回首頁</a>
                </div>
            </header>
            <main class="container mx-auto my-8 bg-white p-6 rounded-lg shadow-md">
                {content}
            </main>
        </body>
        </html>
        """
        
        # 返回 HTML 內容
        return HTMLResponse(content=html_content, media_type="text/html")
    except Exception as e:
        logger.error(f"讀取 Chart.js 格式文檔時發生錯誤: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"讀取文檔時發生錯誤: {str(e)}"}
        )


@app.get("/examples", response_class=HTMLResponse)
async def examples_page(request: Request):
    """
    渲染範例檔案管理頁面。
    
    Args:
        request (Request): FastAPI 請求物件。
        
    Returns:
        TemplateResponse: 渲染後的 HTML 頁面。
    """
    return templates.TemplateResponse("examples.html", {"request": request})


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
        {"id": "scatter", "name": "散點圖"},
        {"id": "candlestick", "name": "蠟燭圖", "category": "金融圖表"},
        {"id": "ohlc", "name": "OHLC 圖表", "category": "金融圖表"},
        {"id": "sankey", "name": "桑基圖", "category": "特殊圖表"},
        {"id": "barLine", "name": "柱狀圖+折線圖", "category": "混合圖表"},
        {"id": "ohlcVolume", "name": "OHLC+成交量圖", "category": "金融圖表"},
        {"id": "ohlcMaKd", "name": "OHLC+移動平均線+KD線", "category": "金融圖表"}
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
            # 對於上傳的檔案，確保從 uploads 目錄中讀取
            file_path = UPLOAD_DIR / filename
            logger.info(f"嘗試從上傳目錄讀取檔案: {file_path}")
            
            # 如果檔案不存在，嘗試檢查副檔名
            if not os.path.exists(file_path):
                logger.warning(f"上傳的檔案不存在: {file_path}，嘗試自動添加副檔名")
                # 嘗試添加常見副檔名
                for ext in ['.csv', '.json', '.xlsx', '.xls']:
                    test_path = UPLOAD_DIR / (filename + ext)
                    if os.path.exists(test_path):
                        file_path = test_path
                        logger.info(f"找到檔案: {file_path}")
                        break
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
        
        # 確保文件副檔名正確
        if file_type == 'csv' and not filename.lower().endswith('.csv'):
            filename += '.csv'
        elif file_type == 'json' and not filename.lower().endswith('.json'):
            filename += '.json'
        elif file_type == 'excel' and not filename.lower().endswith(('.xlsx', '.xls')):
            filename += '.xlsx'
        
        # 使用uploads目錄保存所有上傳文件
        save_dir = UPLOAD_DIR
        
        # 確保上傳目錄存在
        try:
            os.makedirs(save_dir, exist_ok=True)
            logger.info(f"確認上傳目錄存在: {save_dir}")
        except Exception as e:
            logger.error(f"建立上傳目錄時發生錯誤: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": f"建立上傳目錄時發生錯誤: {str(e)}"}
            )
        
        # 組合完整保存路徑
        file_path = save_dir / filename
        logger.info(f"準備保存上傳文件到: {file_path}")
        
        # 保存上傳的文件
        try:
            with open(file_path, "wb") as f:
                # 定位到文件開頭
                await file.seek(0)
                content = await file.read()
                f.write(content)
            
            logger.info(f"文件已成功保存: {file_path}, 大小: {len(content)} bytes")
        except Exception as e:
            logger.error(f"保存文件時發生錯誤: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": f"保存文件時發生錯誤: {str(e)}"}
            )
        
        try:
            # 嘗試讀取文件以驗證其有效性
            df = read_data_file(str(file_path), file_type)
            if df.empty:
                # 如果無法讀取，記錄錯誤但不刪除文件
                logger.warning(f"文件格式可能不正確: {file_path}, 但仍然保留")
                return JSONResponse(
                    status_code=400,
                    content={"error": "無法解析上傳的文件，請確保文件格式正確"}
                )
            
            # 返回成功信息
            return {
                "status": "success",
                "message": "文件上傳成功",
                "filename": filename,
                "file_type": "uploaded",  # 設為 uploaded 而不是原始類型
                "row_count": len(df),
                "column_count": len(df.columns)
            }
        except Exception as read_error:
            logger.error(f"讀取上傳的文件時發生錯誤: {read_error}")
            # 儘管發生錯誤，仍返回上傳成功信息
            return {
                "status": "partial_success",
                "message": f"文件已上傳，但無法讀取: {str(read_error)}",
                "filename": filename,
                "file_type": "uploaded",
                "row_count": 0,
                "column_count": 0
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


@app.post("/api/chart-from-json/")
async def create_chart_from_json(data: Dict[str, Any] = Body(...)):
    """
    從 JSON 格式的數據創建圖表。
    
    請求中的 JSON 必須遵循 Chart.js 格式:
    {
        "type": "line",  // 選填: 圖表類型
        "labels": [...],  // x軸標籤
        "datasets": [
            {
                "label": "數據集名稱",
                "data": [...],  // 或 [{x: 1, y: 2}, ...] 用於散點圖和氣泡圖
                "backgroundColor": "rgba(0,0,0,0.5)",  // 選填
                "borderColor": "rgba(0,0,0,1)"  // 選填
            }
        ],
        "chartTitle": "圖表標題"  // 選填
    }
    
    Returns:
        JSONResponse: 成功處理的 Chart.js 格式數據
    """
    try:
        # 使用 ChartJSAdapter 驗證和處理 JSON 數據
        adapter = ChartJSAdapter(data)
        chart_data = adapter.convert_to_chartjs()
        
        # 返回處理後的數據
        return JSONResponse(content=chart_data)
        
    except Exception as e:
        logger.error(f"處理 JSON 數據時發生錯誤: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "error": f"處理 JSON 數據失敗: {str(e)}",
                "info": "請提供符合 Chart.js 格式的 JSON 數據"
            }
        )


@app.get("/api/file-content/")
async def get_file_content(
    filename: str = Query(..., description="文件名"),
    file_type: str = Query(..., description="文件類型 (csv, json, excel, persistence, uploaded)")
):
    """
    讀取指定的數據文件並返回原始內容
    
    Args:
        filename (str): 文件名
        file_type (str): 文件類型
        
    Returns:
        dict: 包含文件原始內容的字典
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
        
        # 讀取文件內容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            return {"data": content, "filename": filename}
        except json.JSONDecodeError as e:
            return JSONResponse(
                status_code=400,
                content={"error": f"JSON 解析錯誤: {str(e)}"}
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"文件讀取錯誤: {str(e)}"}
            )
        
    except Exception as e:
        logger.error(f"獲取文件內容錯誤: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"獲取文件內容錯誤: {str(e)}"}
        )


# 導入並註冊 Excel 匯出 API
try:
    import sys
    sys.path.append(str(BASE_DIR / "app"))
    from apis import excel_export
    app.include_router(excel_export_router, prefix="/api", tags=["Excel Export"])
except Exception as e:
    logger.error(f"導入 Excel 匯出 API 時發生錯誤: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

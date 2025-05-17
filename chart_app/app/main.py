#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FastAPI 主應用程式。
提供網頁渲染、靜態檔案服務、API 端點等功能。
"""

import os
import shutil
import json
import logging
import glob
import pickle
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request, Query
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import re
from unicodedata import normalize

# 導入數據處理相關模組
try:
    import pandas as pd
    import numpy as np
except ImportError:
    logging.error("缺少必要的數據處理套件。請確保 pandas 和 numpy 已正確安裝。")
    pd = None
    np = None
    
# 導入API路由模組
try:
    from app.apis.example_router import example_router
except ImportError:
    logging.warning("無法導入 example_router 模組，API 端點可能無法正常工作")

# 添加本地模組導入
try:
    from app import file_checker
except ImportError:
    # 創建一個簡單的文件檢查器作為替代，避免系統崩潰
    class FileCheckerStub:
        def fix_file_path(self, path):
            return path
            
        def check_file_exists(self, filename):
            return False, f"模組 file_checker 不可用，無法檢查文件: {filename}"
            
        def get_file_content(self, path):
            return False, "模組 file_checker 不可用，無法讀取文件內容"
            
        def list_uploaded_files(self, file_type=None):
            return []
    
    file_checker = FileCheckerStub()
    logging.warning("無法導入 file_checker 模組，使用替代實作")

# 自行實作 secure_filename 函數
def secure_filename(filename):
    """
    安全處理檔案名稱，替代 werkzeug.utils.secure_filename
    
    透過移除不安全字符和路徑遍歷部分來確保檔案名稱安全
    """
    if not filename:
        return ''
        
    # 移除控制字符、斜線和空格
    filename = normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    filename = re.sub(r'[^\w\.\-]', '_', filename)
    
    # 移除開頭的點號(.)，避免隱藏檔案
    filename = filename.lstrip('.')
    
    # 如果結果為空，返回安全預設值
    if not filename:
        return 'unnamed_file'
        
    return filename

# 設置基本日誌配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("chart_app")

# 建立 FastAPI 應用實例
app = FastAPI(
    title="Chart App",
    description="FastAPI + TailwindCSS + ChartJS 整合應用",
    version="1.0.0"
)

# 掛載靜態檔案目錄
app.mount("/static", StaticFiles(directory="static"), name="static")

# 包含API路由模組
try:
    app.include_router(example_router)
    logger.info("已成功載入範例檔案API路由")
except NameError as e:
    logger.warning(f"無法包含範例檔案API路由: {e}")

# 設定目錄路徑
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path("/Users/aaron/Projects/DataScout/data")
DATA_CSV_DIR = DATA_DIR / "csv"
DATA_JSON_DIR = DATA_DIR / "json"
DATA_EXCEL_DIR = DATA_DIR / "excel"
PERSISTENCE_DIR = Path("/Users/aaron/Projects/DataScout/persistence")
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
# 添加缺少的上傳子目錄
UPLOAD_CSV_DIR = UPLOAD_DIR / "csv"
UPLOAD_JSON_DIR = UPLOAD_DIR / "json" 
UPLOAD_EXCEL_DIR = UPLOAD_DIR / "excel"
TEMP_DIR = BASE_DIR / "static" / "temp"
EXAMPLES_DIR = BASE_DIR / "static" / "examples"  # 添加範例檔案目錄

# 確保所有需要的目錄存在
os.makedirs(DATA_CSV_DIR, exist_ok=True)
os.makedirs(DATA_JSON_DIR, exist_ok=True)
os.makedirs(DATA_EXCEL_DIR, exist_ok=True)
os.makedirs(EXAMPLES_DIR, exist_ok=True)  # 確保範例目錄存在
# 確保上傳子目錄存在
os.makedirs(UPLOAD_CSV_DIR, exist_ok=True)
os.makedirs(UPLOAD_JSON_DIR, exist_ok=True)
os.makedirs(UPLOAD_EXCEL_DIR, exist_ok=True)

# 設定模板引擎
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# 自定義模板上下文處理器，用於修復靜態文件路徑問題
@app.middleware("http")
async def add_templates_context(request: Request, call_next):
    # 將 request 物件注入到所有模板的上下文中
    request.state.static_url = lambda path: f"/static/{path}"
    response = await call_next(request)
    return response

# 建立上傳資料夾（如果不存在）
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

# 在現有的 add_templates_context 中間件後面添加以下函數

def convert_df_to_chartjs(df):
    """
    將 DataFrame 轉換為 Chart.js 格式
    
    Args:
        df (pd.DataFrame): 待轉換的數據框
        
    Returns:
        dict: Chart.js 格式的數據
    """
    try:
        # 檢測日期列
        date_column = None
        for col in ['Date', 'DATE', 'date', 'datetime', 'time', 'timestamp', 'Time', 'Timestamp']:
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
                
                # 過濾掉 NaN 值
                valid_data = df_values[column].ffill().bfill().tolist()
                
                datasets.append({
                    "label": str(column),
                    "data": valid_data,
                    "backgroundColor": color,
                    "borderColor": color.replace("0.6", "1.0"),
                    "borderWidth": 1
                })
        
        # 返回 Chart.js 格式的資料
        return {
            "labels": labels,
            "datasets": datasets,
            "chartTitle": "資料視覺化"
        }
    except Exception as e:
        logger.exception("DataFrame 轉換為 Chart.js 格式時出錯")
        return {
            "labels": [],
            "datasets": [],
            "chartTitle": "無法載入資料",
            "error": str(e)
        }


def get_data_files(data_type: str) -> list[dict]:
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
    # 獲取所有範例檔案
    try:
        examples = []
        for file_path in glob.glob(str(EXAMPLES_DIR / "*.json")):
            file_name = os.path.basename(file_path)
            display_name = file_name.replace("_", " ").replace(".json", "")
            
            # 嘗試獲取圖表類型
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    chart_type = data.get('type', 'unknown')
            except Exception:
                chart_type = 'unknown'
                
            examples.append({
                "filename": file_name,
                "display_name": display_name,
                "chart_type": chart_type,
                "path": file_path
            })
        
        # 依文件名排序
        examples.sort(key=lambda x: x["display_name"])
        
    except Exception as e:
        logger.error(f"獲取範例列表時發生錯誤: {e}")
        examples = []
    
    return templates.TemplateResponse(
        "examples.html", 
        {
            "request": request, 
            "title": "圖表範例檔案", 
            "examples": examples
        }
    )


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


@app.get("/file-diagnostics")
async def file_diagnostics(request: Request):
    """檔案診斷工具頁面"""
    return templates.TemplateResponse("file_diagnostics.html", {"request": request, "title": "檔案系統診斷"})


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
async def get_file_data(filename: str, type: str, is_upload: Optional[bool] = False):
    """獲取指定檔案的資料，並轉換為 Chart.js 格式"""
    try:
        # 修正：檢查檔案路徑並修復
        if is_upload:
            # 如果是上傳檔案，嘗試修復路徑
            filename = file_checker.fix_file_path(filename)
            
        logging.info(f"獲取檔案資料: {filename}, 類型: {type}, 是否為上傳檔案: {is_upload}")
        
        # 檢查文件是否存在
        exists, path_or_error = file_checker.check_file_exists(filename)
        if not exists:
            return JSONResponse(
                status_code=404,
                content={"detail": f"找不到檔案: {filename}", "error": path_or_error}
            )
        
        # 實際的檔案路徑
        actual_path = path_or_error
        
        # 根據不同檔案類型處理
        if type == "json":
            # 獲取 JSON 檔案內容
            exists, content = file_checker.get_file_content(actual_path)
            if not exists:
                return JSONResponse(
                    status_code=500,
                    content={"detail": f"無法讀取JSON檔案: {content}"}
                )
            
            # 直接返回 JSON 內容
            return content
            
        elif type == "csv":
            # 讀取 CSV 並轉換為 Chart.js 格式
            try:
                df = pd.read_csv(actual_path)
                # CSV 轉換為 Chart.js 格式的邏輯
                chart_data = convert_df_to_chartjs(df)
                return chart_data
            except Exception as e:
                logging.exception(f"處理 CSV 檔案 {filename} 時出錯")
                return JSONResponse(
                    status_code=500,
                    content={"detail": f"處理 CSV 檔案出錯: {str(e)}"}
                )
                
        elif type == "excel":
            # 讀取 Excel 並轉換為 Chart.js 格式
            try:
                df = pd.read_excel(actual_path)
                # Excel 轉換為 Chart.js 格式的邏輯
                chart_data = convert_df_to_chartjs(df)
                return chart_data
            except Exception as e:
                logging.exception(f"處理 Excel 檔案 {filename} 時出錯")
                return JSONResponse(
                    status_code=500,
                    content={"detail": f"處理 Excel 檔案出錯: {str(e)}"}
                )
        else:
            return JSONResponse(
                status_code=400,
                content={"detail": f"不支援的檔案類型: {type}"}
            )
    except Exception as e:
        logging.exception(f"獲取檔案資料時出錯: {filename}")
        return JSONResponse(
            status_code=500, 
            content={"detail": f"處理檔案時發生錯誤: {str(e)}"}
        )


@app.post("/api/upload-file/")
async def upload_file(file: UploadFile = File(...), file_type: str = Form(...)):
    """處理檔案上傳請求"""
    logger.info(f"接收到上傳請求，檔案: {file.filename}, 類型: {file_type}")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供檔案名稱")
    
    try:
        # 確保檔案名稱安全
        safe_filename = secure_filename(file.filename)
        
        # 根據檔案類型決定存放路徑
        if file_type == "csv":
            save_dir = UPLOAD_CSV_DIR
            file_extension = ".csv"
        elif file_type == "json":
            save_dir = UPLOAD_JSON_DIR
            file_extension = ".json"
        elif file_type == "excel":
            save_dir = UPLOAD_EXCEL_DIR
            file_extension = ".xlsx"
        else:
            raise HTTPException(status_code=400, detail=f"不支援的檔案類型: {file_type}")
        
        # 確保存儲目錄存在
        os.makedirs(save_dir, exist_ok=True)
        
        # 確保副檔名正確
        if not safe_filename.endswith(file_extension):
            base_name = os.path.splitext(safe_filename)[0]
            safe_filename = f"{base_name}{file_extension}"
        
        # 構建完整儲存路徑
        file_path = os.path.join(save_dir, safe_filename)
        
        # 儲存檔案
        with open(file_path, "wb") as buffer:
            content = await file.read()  # 一次讀取所有內容
            buffer.write(content)
            
        logger.info(f"檔案 '{safe_filename}' 已保存到 '{file_path}'")
        
        # 返回檔案資訊
        return {
            "filename": safe_filename,
            "file_path": safe_filename,  # 為了前端兼容性，只返回檔案名稱
            "content_type": file.content_type,
            "file_type": file_type
        }
        
    except Exception as e:
        logger.error(f"上傳檔案時發生錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上傳檔案時發生錯誤: {str(e)}")


# 新增一個 API 端點來檢查和列出已上傳的檔案
@app.get("/api/list-uploads/")
async def list_uploaded_files(file_type: Optional[str] = None):
    """列出已上傳的檔案"""
    try:
        files = file_checker.list_uploaded_files(file_type)
        return {
            "total": len(files),
            "files": files
        }
    except Exception as e:
        logging.exception("列出上傳檔案時發生錯誤")
        return JSONResponse(
            status_code=500,
            content={"error": f"列出上傳檔案時發生錯誤: {str(e)}"}
        )

# 新增一個 API 端點來檢查檔案是否存在
@app.get("/api/check-file/")
async def check_file_exists(filename: str):
    """檢查檔案是否存在"""
    try:
        exists, path_or_error = file_checker.check_file_exists(filename)
        if exists:
            return {
                "exists": True,
                "path": path_or_error
            }
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "exists": False,
                    "error": path_or_error
                }
            )
    except Exception as e:
        logging.exception(f"檢查檔案時發生錯誤: {filename}")
        return JSONResponse(
            status_code=500,
            content={"error": f"檢查檔案時發生錯誤: {str(e)}"}
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


@app.get("/api/examples/chart-types/")
async def api_chart_types():
    """
    獲取所有可用的圖表類型
    
    Returns:
        dict: 包含圖表類型的字典
    """
    chart_types = {
        "line": "折線圖",
        "bar": "長條圖",
        "pie": "圓餅圖",
        "doughnut": "環狀圖",
        "radar": "雷達圖",
        "polarArea": "極座標圖",
        "scatter": "散點圖",
        "bubble": "氣泡圖",
        "candlestick": "蠟燭圖",
        "mixed": "混合圖表"
    }
    
    return {"chart_types": chart_types}


@app.get("/api/examples/list/")
async def api_list_examples(chart_type: Optional[str] = None):
    """
    API 路徑別名：列出可用的範例檔案
    
    Args:
        chart_type (str, optional): 如果提供，只返回指定圖表類型的範例
        
    Returns:
        dict: 範例檔案列表
    """
    return await list_examples(chart_type)


@app.get("/api/examples/get/")
async def api_get_example(filename: str = Query(..., description="範例檔案名稱")):
    """
    API 路徑別名：獲取特定的範例檔案內容
    
    Args:
        filename (str): 範例檔案名稱
        
    Returns:
        JSON: 範例檔案內容
    """
    return await get_example(filename)
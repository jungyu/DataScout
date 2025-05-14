#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FastAPI 主應用程式。
提供網頁渲染、靜態檔案服務、API 端點等功能。
"""

import os
import pandas as pd
import numpy as np
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import datetime

# 建立 FastAPI 應用實例
app = FastAPI(
    title="Chart App",
    description="FastAPI + TailwindCSS + ChartJS 整合應用",
    version="1.0.0"
)

# 取得基礎目錄路徑
BASE_DIR = Path(__file__).resolve().parent.parent

# 設定模板引擎
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# 設定靜態檔案目錄
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# 建立上傳資料夾（如果不存在）
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@app.get("/")
async def root(request: Request):
    """
    渲染首頁 HTML 模板。

    Args:
        request (Request): FastAPI 請求物件。

    Returns:
        TemplateResponse: 渲染後的 HTML 頁面。
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Chart.js 圖表展示"}
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

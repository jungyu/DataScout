#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
範例檔案 API 路由
負責管理和提供範例檔案
"""

import os
import json
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pathlib import Path
import logging
import glob

# 配置日誌
logger = logging.getLogger("chart_app.example_api")

# 建立路由
example_router = APIRouter(
    prefix="/api/examples",
    tags=["examples"],
)

# 取得基礎目錄路徑
BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXAMPLES_DIR = BASE_DIR / "static" / "examples"

# 確保範例目錄存在
if not os.path.exists(EXAMPLES_DIR):
    os.makedirs(EXAMPLES_DIR, exist_ok=True)

@example_router.get("/list/")
async def list_example_files(chart_type: str = None):
    """
    獲取所有範例檔案列表，如果指定了圖表類型，則只返回該類型的範例
    
    Args:
        chart_type (str, optional): 圖表類型. Defaults to None.
        
    Returns:
        dict: 包含範例檔案列表的字典
    """
    try:
        # 獲取所有 JSON 檔案
        example_files = []
        for file_path in glob.glob(str(EXAMPLES_DIR / "*.json")):
            file_name = os.path.basename(file_path)
            # 只加入以 example_ 開頭的檔案
            if file_name.startswith("example_"):
                example_files.append(file_name)
        
        # 如果指定了圖表類型，過濾檔案
        if chart_type:
            filtered_files = []
            pattern = f"example_{chart_type}_"
            for file_name in example_files:
                if file_name.startswith(pattern):
                    filtered_files.append(file_name)
            example_files = filtered_files
        
        # 按照分類組織檔案
        categorized = {}
        chart_types = ["bar", "line", "pie", "radar", "scatter", "bubble", "doughnut", "candlestick", "mixed"]
        
        for chart_type in chart_types:
            type_files = []
            for file_name in example_files:
                if file_name.startswith(f"example_{chart_type}_"):
                    # 創建檔案信息
                    display_name = file_name.replace(f"example_{chart_type}_", "").replace(".json", "").replace("_", " ")
                    type_files.append({
                        "filename": file_name,
                        "display_name": display_name.title(),
                        "chart_type": chart_type
                    })
            if type_files:
                categorized[chart_type] = type_files
        
        # 返回結果
        return {
            "examples": example_files,
            "categorized": categorized,
            "total": len(example_files)
        }
    
    except Exception as e:
        logger.error(f"獲取範例檔案錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取範例檔案錯誤: {str(e)}")


@example_router.get("/get/")
async def get_example_data(filename: str = Query(..., description="範例檔案名稱")):
    """
    獲取特定範例檔案的內容
    
    Args:
        filename (str): 範例檔案名稱
        
    Returns:
        dict: 範例檔案的內容
    """
    file_path = EXAMPLES_DIR / filename
    
    # 檢查檔案是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"範例檔案不存在: {filename}")
    
    try:
        # 讀取JSON檔案
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"讀取範例檔案錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"讀取範例檔案錯誤: {str(e)}")


@example_router.get("/chart-types/")
async def get_chart_types():
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


from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class ExampleUploadRequest(BaseModel):
    """範例檔案上傳請求模型"""
    chart_type: str
    name: str
    data: Dict[str, Any]


@example_router.post("/upload/")
async def upload_example_file(request: ExampleUploadRequest):
    """
    上傳新的範例檔案
    
    Args:
        request (ExampleUploadRequest): 上傳請求
        
    Returns:
        dict: 上傳結果
    """
    try:
        # 清理檔案名稱，移除不需要的字符
        clean_name = request.name.strip().replace(" ", "_")
        filename = f"example_{request.chart_type}_{clean_name}.json"
        file_path = EXAMPLES_DIR / filename
        
        # 檢查檔案是否已存在
        if os.path.exists(file_path):
            raise HTTPException(status_code=400, detail=f"範例檔案已存在: {filename}")
        
        # 檢查和修正數據格式
        data = request.data
        
        # 確保有 type 字段
        if "type" not in data:
            data["type"] = request.chart_type
            
        # 確保有 datasets 字段
        if "datasets" not in data and "data" in data and "datasets" in data["data"]:
            data["datasets"] = data["data"]["datasets"]
            del data["data"]
            
        # 保存檔案
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        # 返回成功結果
        return {
            "status": "success",
            "filename": filename,
            "path": str(file_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上傳範例檔案錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上傳範例檔案錯誤: {str(e)}")

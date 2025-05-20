#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DataScout FastAPI 服務主入口

此模組提供基於 FastAPI 的 Web 服務主入口，包括：
1. API 路由管理
2. 圖表渲染功能
3. 靜態文件服務
4. 數據處理和爬蟲任務執行
"""

import os
import json
import logging
import argparse
import uvicorn
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

# FastAPI 相關導入
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request, Query, Depends
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# 系統路徑處理
BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"
DEBUG_DIR = DATA_DIR / "debug"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
CHART_APP_DIR = BASE_DIR / "chart_app"
STATIC_DIR = CHART_APP_DIR / "static"
TEMPLATES_DIR = CHART_APP_DIR / "templates"

# 確保必要的目錄存在
for dir_path in [OUTPUT_DIR, DEBUG_DIR, SCREENSHOTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("datascout")

# 創建 FastAPI 應用
app = FastAPI(
    title="DataScout",
    description="網頁數據採集與圖表渲染 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載靜態文件
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 設置模板引擎
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# 全局配置字典
app_config = {}

def load_config(config_path):
    """加載配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 設置調試模式（運行時設定）
        if app_config.get("debug"):
            config["debug"] = config.get("debug", {})
            config["debug"]["screenshot"] = True
            config["debug"]["save_page_source"] = True
            config["debug"]["error_page_dir"] = str(DEBUG_DIR)
        
        # 設置截圖目錄
        if "screenshot" in config:
            config["screenshot"]["directory"] = str(SCREENSHOTS_DIR)
        
        return config
    except Exception as e:
        logger.error(f"加載配置文件失敗: {str(e)}")
        raise

def save_results(data, output_path=None):
    """保存結果"""
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"results_{timestamp}.json"
    else:
        output_path = Path(output_path)
    
    output_dir = output_path.parent
    if output_dir and not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"數據已保存到: {output_path}")
    return str(output_path)

# API 路由

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """首頁"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/config", response_model=Dict[str, Any])
async def get_config():
    """獲取當前配置信息"""
    return app_config

@app.post("/api/config")
async def update_config(config: Dict[str, Any]):
    """更新配置信息"""
    global app_config
    app_config.update(config)
    return {"status": "success", "message": "配置已更新"}

@app.get("/api/chart/{chart_type}")
async def get_chart_data(chart_type: str, name: Optional[str] = None):
    """獲取圖表數據"""
    try:
        if name:
            # 嘗試加載指定的圖表數據
            file_path = STATIC_DIR / "examples" / f"{name}.json"
        else:
            # 加載默認圖表數據
            file_path = STATIC_DIR / "examples" / f"example_{chart_type}_chart.json"
            
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"找不到圖表數據: {file_path.name}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return data
    except Exception as e:
        logger.error(f"讀取圖表數據時發生錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/charts/{chart_name}", response_class=HTMLResponse)
async def show_chart(request: Request, chart_name: str):
    """顯示指定圖表"""
    return templates.TemplateResponse("chart_demo.html", {
        "request": request,
        "chart_name": chart_name
    })

@app.get("/examples", response_class=HTMLResponse)
async def list_examples(request: Request):
    """顯示可用圖表範例清單"""
    try:
        # 獲取範例目錄中的所有 JSON 文件
        example_files = list(Path(STATIC_DIR / "examples").glob("*.json"))
        examples = []
        
        for file_path in example_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    chart_type = data.get("type", "unknown")
                    chart_title = data.get("chartTitle", file_path.stem)
                    
                    examples.append({
                        "name": file_path.stem,
                        "type": chart_type,
                        "title": chart_title
                    })
            except Exception as e:
                logger.warning(f"無法讀取範例文件 {file_path.name}: {str(e)}")
        
        return templates.TemplateResponse("examples.html", {
            "request": request,
            "examples": examples
        })
    except Exception as e:
        logger.error(f"列出範例時發生錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/run-task")
async def run_task(config_file: str = Form(...)):
    """執行爬蟲任務"""
    try:
        config_path = Path(CONFIG_DIR) / config_file
        if not config_path.exists():
            raise HTTPException(status_code=404, detail=f"找不到配置文件: {config_file}")
        
        # 加載配置
        config = load_config(str(config_path))
        
        # 執行爬蟲任務 (這裡應該調用您的爬蟲邏輯)
        # TODO: 實現爬蟲邏輯
        
        # 生成結果文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"results_{timestamp}.json"
        
        # 保存結果 (這裡只是示例，實際應該返回爬蟲的結果)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"status": "success", "timestamp": timestamp}, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "success", 
            "message": "任務已完成", 
            "output_file": str(output_path)
        }
    except Exception as e:
        logger.error(f"執行任務時發生錯誤: {str(e)}")
        return {"status": "error", "message": str(e)}

# 集成其他應用的路由
# 這裡可以導入並集成 chart_app 的路由
try:
    from chart_app.app.apis.example_router import example_router
    app.include_router(example_router, prefix="/api")
except ImportError:
    logger.warning("無法導入 chart_app 的 API 路由")

def parse_args():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description="DataScout API 服務")
    parser.add_argument("-c", "--config", help="配置文件路徑")
    parser.add_argument("-p", "--port", type=int, default=8000, help="服務器端口")
    parser.add_argument("-H", "--host", default="127.0.0.1", help="服務器主機地址")
    parser.add_argument("-d", "--debug", action="store_true", help="啟用調試模式")
    return parser.parse_args()

def main():
    """主函數 - 啟動 FastAPI 服務"""
    args = parse_args()
    
    # 設置日誌級別
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger.setLevel(log_level)
    
    # 如果指定了配置文件，則加載配置
    if args.config:
        try:
            global app_config
            app_config = load_config(args.config)
        except Exception as e:
            logger.error(f"加載配置文件失敗: {str(e)}")
    
    # 啟動 FastAPI 服務
    logger.info(f"啟動 DataScout API 服務 在 http://{args.host}:{args.port}")
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.debug,
        log_level="debug" if args.debug else "info"
    )

if __name__ == "__main__":
    main()
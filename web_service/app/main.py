#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FastAPI 主應用程式。
提供網頁渲染、靜態檔案服務、API 端點等功能。
"""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# 導入核心配置
from app.core.config import settings
# 導入API路由模組
from app.apis.chart_router import chart_router

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用實例
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載靜態文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 設置模板引擎
templates = Jinja2Templates(directory="templates")

# 註冊路由
app.include_router(chart_router, prefix="/api", tags=["chart"])

# 根路由 - 渲染儀表板
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": settings.PROJECT_NAME}
    )

# 圖表範例頁面
@app.get("/chart-examples", response_class=HTMLResponse)
async def chart_examples(request: Request):
    return templates.TemplateResponse(
        "chart_examples.html",
        {"request": request, "title": f"{settings.PROJECT_NAME} - 圖表範例"}
    )

# 健康檢查端點
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "version": settings.PROJECT_VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

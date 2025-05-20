#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FastAPI 依賴注入模組。
提供路由處理程序所需的共享依賴功能。
"""

import logging
from typing import Generator, Dict, Any, List, Optional
from fastapi import Depends, HTTPException, status

# 導入核心配置
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_data_processor() -> Generator:
    """
    提供資料處理依賴
    """
    # 這裡可以初始化資料處理器
    try:
        # 初始化資料處理所需的資源
        data_processor = {"initialized": True}
        yield data_processor
    finally:
        # 清理資源
        pass

def get_chart_manager() -> Generator:
    """
    提供圖表管理器依賴
    """
    try:
        # 初始化圖表管理器
        chart_manager = {
            "theme": settings.DEFAULT_CHART_THEME,
            "supported_types": ["line", "bar", "pie", "radar", "scatter", "bubble"]
        }
        yield chart_manager
    finally:
        # 清理資源
        pass

async def get_current_user(
    # 可以添加 JWT 或 OAuth 認證
) -> Dict[str, Any]:
    """
    驗證並返回當前用戶。
    可以與 JWT 或 OAuth2 集成。
    """
    # 這裡只是一個示例實現
    user = {"id": "sample_user", "username": "demo_user", "is_admin": False}
    return user

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    驗證文件副檔名是否在允許列表中
    """
    if not filename:
        return False
    extension = filename.split(".")[-1].lower() if "." in filename else ""
    return extension in allowed_extensions

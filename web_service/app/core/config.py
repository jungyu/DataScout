#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
應用配置模組。
管理所有環境變數和應用配置項。
"""

import os
import json
import secrets
from typing import List, Dict, Any, Optional
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """應用配置設置。使用 pydantic 進行環境變數校驗和管理。"""
    
    # 基本項目資訊
    PROJECT_NAME: str = "DataScout Web Service"
    PROJECT_DESCRIPTION: str = "DataScout 專案的 Web 服務和儀表板"
    PROJECT_VERSION: str = "1.0.0"
    
    # API 與安全配置
    API_PREFIX: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天
    
    # CORS 配置
    CORS_ORIGINS: List[str] = ["*"]
    
    # 伺服器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # 資料存儲配置
    DATA_DIR: str = "data"
    UPLOAD_DIR: str = "static/uploads"
    
    # 圖表配置
    DEFAULT_CHART_THEME: str = "light"
    
    # 資料庫配置 (如需要)
    DATABASE_URL: Optional[str] = None
    
    class Config:
        """Pydantic 配置類別"""
        case_sensitive = True
        env_file = ".env"
        
    def ensure_directories(self) -> None:
        """確保必要的目錄存在"""
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.DATA_DIR, exist_ok=True)
        
    def load_custom_config(self, config_path: str) -> Dict[str, Any]:
        """從 JSON 文件加載自定義配置"""
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"無法加載配置文件 {config_path}: {e}")
        return {}


# 實例化設置
settings = Settings()

# 確保必要目錄存在
settings.ensure_directories()

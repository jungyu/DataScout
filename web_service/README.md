# Web Service API 模組

## 專案概述

Web Service API 模組提供了 RESTful API 服務，用於處理數據請求、圖表生成和數據存儲等功能。本模組基於 FastAPI 框架，提供高效的非同步 API 服務。

## 環境設置

### 1. 創建虛擬環境

```bash
# 進入 web_service 目錄
cd web_service

# 創建虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. 安裝依賴

```bash
# 安裝依賴套件
pip install -r requirements.txt
```

### 3. 環境變數設置

在專案根目錄創建 `.env` 文件，添加以下配置：

```env
# API 配置
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Supabase 配置
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
```

## 目錄結構

```
web_service/
├── api/           # API 路由
├── core/          # 核心組件
├── models/        # 數據模型
├── services/      # 業務邏輯
└── utils/         # 工具函數
```

## 使用方式

### 啟動服務

```bash
# 開發環境
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生產環境
uvicorn main:app --host 0.0.0.0 --port 8000
```

### API 文檔

啟動服務後，可以訪問以下地址查看 API 文檔：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要功能

1. 數據處理 API
2. 圖表生成服務
3. 數據存儲管理
4. 用戶認證授權
5. 錯誤處理和日誌記錄

## 注意事項

1. 確保在執行前已啟動虛擬環境
2. 檢查環境變數是否正確設置
3. 確保所有依賴都已正確安裝
4. 注意 API 安全性設置

## 依賴套件說明

- `fastapi`: Web 框架
- `uvicorn`: ASGI 服務器
- `python-dotenv`: 環境變數管理
- `supabase`: Supabase 資料庫客戶端
- `pandas`: 數據處理
- `aiohttp`: 非同步 HTTP 客戶端
- `httpx`: 現代 HTTP 客戶端
- `python-multipart`: 文件上傳處理
- `pydantic`: 數據驗證

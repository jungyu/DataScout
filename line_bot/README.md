# Line Bot 模組

## 專案概述

Line Bot 模組提供了與 Line 平台整合的機器人服務，支援多種消息類型和互動功能。本模組基於 Line Bot SDK 和 Flask 框架，提供穩定可靠的機器人服務。

## 環境設置

### 1. 創建虛擬環境

```bash
# 進入 line_bot 目錄
cd line_bot

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
# Line Bot 配置
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
LINE_CHANNEL_SECRET=your_channel_secret

# Web 服務配置
WEBHOOK_URL=your_webhook_url
PORT=5000

# Supabase 配置
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## 目錄結構

```
line_bot/
├── core/           # 核心組件
├── handlers/       # 消息處理器
├── services/       # 業務邏輯
├── templates/      # 消息模板
└── utils/          # 工具函數
```

## 使用方式

### 開發環境

```bash
# 啟動開發服務器
python app.py
```

### 生產環境

```bash
# 使用 gunicorn 啟動
gunicorn app:app -b 0.0.0.0:5000
```

## 主要功能

1. 消息處理
   - 文字消息
   - 圖片消息
   - 貼圖消息
   - 位置消息
   - 檔案消息

2. 互動功能
   - 按鈕選單
   - 輪播訊息
   - 快速回覆
   - 彈性訊息

3. 用戶管理
   - 用戶資訊獲取
   - 群組管理
   - 好友管理

4. 數據存儲
   - 用戶對話記錄
   - 使用統計
   - 設定管理

## 注意事項

1. 確保在執行前已啟動虛擬環境
2. 檢查環境變數是否正確設置
3. 確保所有依賴都已正確安裝
4. 注意 Line 平台的限制和規範

## 依賴套件說明

- `line-bot-sdk`: Line Bot SDK
- `flask`: Web 框架
- `gunicorn`: WSGI 服務器
- `python-dotenv`: 環境變數管理
- `supabase`: Supabase 資料庫客戶端
- `pandas`: 數據處理
- `aiohttp`: 非同步 HTTP 客戶端
- `httpx`: 現代 HTTP 客戶端 
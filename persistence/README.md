# Persistence 資料存儲模組

## 專案概述

Persistence 模組提供了統一的資料存儲接口，支援多種存儲後端，包括 Supabase、本地文件系統等。本模組採用分層設計，實現了基礎存儲層和業務層的分離。

## 環境設置

### 1. 創建虛擬環境

```bash
# 進入 persistence 目錄
cd persistence

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
# Supabase 配置
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
```

## 目錄結構

```
persistence/
├── core/           # 核心組件
├── handlers/       # 存儲處理器
└── docs/          # 文檔
```

## 使用方式

### 基本使用

```python
from persistence.handlers.supabase_handler import SupabaseHandler
from persistence.core.config import SupabaseConfig

# 初始化配置
config = SupabaseConfig(
    url=os.getenv('SUPABASE_URL'),
    key=os.getenv('SUPABASE_KEY')
)

# 創建處理器
handler = SupabaseHandler(config)

# 使用處理器
await handler.create('table_name', data)
```

### 開發新的存儲處理器

1. 在 `handlers/` 目錄下創建新的處理器文件
2. 繼承 `StorageHandler` 基類
3. 實現必要的方法
4. 在 `core/config.py` 中添加配置類

## 注意事項

1. 確保在執行前已啟動虛擬環境
2. 檢查環境變數是否正確設置
3. 確保所有依賴都已正確安裝
4. 注意資料庫連接的安全性

## 依賴套件說明

- `python-dotenv`: 環境變數管理
- `supabase`: Supabase 資料庫客戶端
- `aiohttp`: 非同步 HTTP 客戶端
- `asyncio`: 非同步 IO 支援
- `httpx`: 現代 HTTP 客戶端

## 模組簡介

Persistence 是一個通用的數據持久化模組，支援多種存儲後端和數據格式，並提供統一的數據存取接口。其設計強調模組化、可擴展性與易用性，適合用於各類型的數據管理場景。

## 主要功能

- 數據存儲：支援本地文件、MongoDB、Notion 等多種存儲後端
- 數據備份：自動備份與版本控制
- 數據恢復：從備份中恢復數據
- 數據驗證：確保數據完整性與一致性
- 錯誤處理：統一的錯誤處理機制
- 日誌記錄：詳細的操作日誌

## 擴展性

- 支援自定義存儲後端
- 支援自定義數據格式
- 支援自定義驗證規則
- 可與其他基礎模組（如 selenium_base, api_base）整合

## 快速使用範例

```python
from persistence import StorageHandler
from persistence.handlers import LocalStorageHandler

# 創建存儲處理器
handler = LocalStorageHandler(config={
    'base_dir': './data',
    'format': 'json'
})

# 存儲數據
handler.save(data={'key': 'value'}, path='example.json')

# 讀取數據
data = handler.load(path='example.json')
```

## 版本資訊

- 版本：2.0.0
- 授權：MIT
- 作者：Aaron Yu (https://github.com/jungyu), Claude AI, Cursor AI
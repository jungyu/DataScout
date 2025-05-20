# DataScout

<div align="center">

![DataScout Logo](docs/images/logo.png)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-orange)](docs/README.md)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](tests/)

</div>

## 📖 目錄

- [專案簡介](#-專案簡介)
- [核心功能](#-核心功能)
- [快速開始](#-快速開始)
- [前後端開發](#-前後端開發)
- [API 服務](#-api-服務)
- [圖表渲染功能](#-圖表渲染功能)
- [自動化方案選擇](#-自動化方案選擇)
- [API 客戶端選擇](#-api-客戶端選擇)
- [使用範例](#-使用範例)
- [專案結構](#-專案結構)
- [開發指南](#-開發指南)
- [注意事項](#-注意事項)
- [貢獻指南](#-貢獻指南)
- [授權協議](#-授權協議)
- [常見問題](#-常見問題)
- [更新日誌](#-更新日誌)

## 🎯 專案簡介

DataScout 是一個資料科學學習的輔助工具，專注於提供完整的資料處理流程，從資料收集、清理、轉換到儲存。本專案採用模組化設計，讓使用者可以根據需求靈活組合不同的功能模組。

### ✨ 主要特點

- 🚀 完整的資料處理流程
  - 自動化資料收集
  - 智能資料清理
  - 靈活資料轉換
  - 多樣化資料儲存
- 🔄 模組化設計
  - 獨立功能模組
  - 可擴展架構
  - 即插即用組件
- 🛠 靈活的功能組合
  - 自定義處理流程
  - 多種自動化方案
  - 豐富的整合選項
- 📊 豐富的資料處理能力
  - 結構化資料處理
  - 非結構化資料處理
  - 即時資料處理
- 🔌 廣泛的系統整合
  - 雲端服務整合
  - 資料庫整合
  - API 整合

### 🎯 適用場景

1. **資料科學學習**
   - 資料收集練習
   - 資料清理實作
   - 資料分析實驗

2. **自動化資料處理**
   - 網站資料爬取
   - API 資料收集
   - 資料格式轉換

3. **系統整合**
   - 雲端服務對接
   - 資料庫整合
   - 第三方 API 整合

## 🛠 核心功能

### 1. 資料收集 (Data Collection)

#### Playwright 自動化
- 🌐 瀏覽器自動化控制
  - 頁面導航控制
  - 元素操作
  - 事件處理
  - 網路請求攔截
- 🛡️ 反偵測功能
  - WebGL 指紋偽造
  - User-Agent 管理
  - Cookie 管理
  - IP 代理
- ✅ 驗證碼處理
  - reCAPTCHA 處理
  - hCaptcha 處理
  - 圖片驗證碼
  - 滑塊驗證碼
- 👤 人類行為模擬
  - 滑鼠移動
  - 鍵盤輸入
  - 滾動行為
  - 點擊模式

#### Selenium 自動化
- 🎮 瀏覽器控制與元素操作
  - 元素定位
  - 元素操作
  - 頁面控制
  - 視窗管理
- ⏱️ 等待機制與事件處理
  - 顯式等待
  - 隱式等待
  - 自定義等待
  - 事件監聽
- 🌍 代理 IP 管理
  - 代理池管理
  - 代理切換
  - 代理驗證
  - 代理輪換
- ✅ 驗證碼處理
  - 驗證碼識別
  - 驗證碼處理
  - 驗證碼繞過
  - 驗證碼重試

#### API 客戶端
- 🔄 RESTful API 整合
  - HTTP 方法支援
  - 請求/響應處理
  - 錯誤處理
  - 重試機制
- 📡 GraphQL 支援
  - 查詢構建
  - 變數處理
  - 響應解析
  - 錯誤處理
- 🔌 WebSocket 連接
  - 連接管理
  - 訊息處理
  - 心跳機制
  - 重連機制
- 🔐 認證管理
  - OAuth 認證
  - API Key 認證
  - JWT 認證
  - 基本認證
- ☁️ 雲端服務整合
  - Make.com 自動化流程
  - n8n 工作流程
  - MQTT 訊息佇列
  - AI MCP 服務

### 2. 資料清理與提取
- 📝 網頁內容提取
  - HTML 解析
  - CSS 選擇器
  - XPath 查詢
  - 正則表達式
- 🔍 結構化資料解析
  - JSON 解析
  - XML 解析
  - CSV 解析
  - Excel 解析
- 🔎 正則表達式處理
  - 模式匹配
  - 文字替換
  - 資料提取
  - 格式驗證
- ✅ 資料驗證
  - 型別檢查
  - 格式驗證
  - 範圍檢查
  - 邏輯驗證

### 3. 資料轉換
- 🔄 格式轉換
  - JSON 轉換
  - XML 轉換
  - CSV 轉換
  - Excel 轉換
- 📊 資料標準化
  - 日期格式
  - 數字格式
  - 文字格式
  - 單位轉換
- 🔗 資料整合
  - 資料合併
  - 資料關聯
  - 資料聚合
  - 資料分組
- 🧹 資料過濾
  - 條件過濾
  - 重複去除
  - 異常值處理
  - 缺失值處理
- 📋 欄位映射
  - 欄位對應
  - 欄位轉換
  - 欄位驗證
  - 欄位預設值
- 💾 資料庫適配
  - SQL 適配
  - NoSQL 適配
  - 時間序列適配
  - 圖資料庫適配

### 4. 資料儲存
- 📁 檔案儲存
  - JSON 檔案
  - CSV 檔案
  - Excel 檔案
  - Parquet 檔案
- 💾 資料庫整合
  - 關聯式資料庫
  - NoSQL 資料庫
  - 時間序列資料庫
  - 圖資料庫
- ☁️ 雲端儲存
  - AWS S3
  - Google Cloud Storage
  - Azure Blob Storage
- ⚡ 快取管理
  - 記憶體快取
  - 檔案快取
  - 分散式快取
  - 快取策略

## 🚀 快速開始

### 1. 系統需求

- Python 3.8 或更高版本
- 作業系統：Windows、macOS、Linux
- 記憶體：至少 4GB RAM
- 硬碟空間：至少 1GB 可用空間

### 2. 安裝依賴

```bash
# 安裝 Python 依賴
pip install -r requirements.txt

# 安裝 Playwright（如果需要）
pip install playwright
playwright install

# 安裝 Selenium（如果需要）
pip install selenium==4.18.1
```

### 3. 環境設定

```bash
# 驗證碼服務
export CAPTCHA_API_KEY=your-api-key

# 資料庫連接
export DB_HOST=localhost
export DB_PORT=27017
export DB_NAME=datascout

# API 金鑰
export API_KEY=your-api-key

# 代理設定
export PROXY_HOST=proxy.example.com
export PROXY_PORT=8080
export PROXY_USERNAME=user
export PROXY_PASSWORD=pass
```

### 4. 啟動 API 服務

```bash
# 使用默認設定啟動 (本地 127.0.0.1:8000)
./run_server.sh

# 指定主機和端口
./run_server.sh --host=0.0.0.0 --port=8888

# 啟用調試模式
./run_server.sh --debug

# 指定配置文件
./run_server.sh --config=config/my_config.json
```

### 5. 訪問 API 服務

- API 文檔: `http://127.0.0.1:8000/docs`
- ReDoc 文檔: `http://127.0.0.1:8000/redoc`
- 圖表範例頁面: `http://127.0.0.1:8000/examples`

### 6. 基本使用

```python
from playwright_base import PlaywrightBase

async def main():
    # 初始化瀏覽器
    browser = PlaywrightBase(
        headless=False,
        proxy={
            "server": "http://proxy.example.com:8080",
            "username": "user",
            "password": "pass"
        }
    )
    
    # 訪問網頁
    await browser.goto("https://example.com")
    
    # 等待元素出現
    await browser.wait_for_selector(".content")
    
    # 提取資料
    data = await browser.extract_data()
    
    # 儲存資料
    await browser.save_data(data, "output.json")
```

## 🔄 前後端開發

DataScout 提供了現代化的前後端分離架構，方便開發者分別進行前端和後端的開發與部署。詳細信息請參見[前後端開發完整指南](docs/frontend_backend_guide.md)。

### 1. 前端開發（DaisyUI + ApexCharts + Alpine.js）

前端使用 Alpine.js 作為輕量級框架，結合 DaisyUI 和 ApexCharts 提供美觀的使用者介面和資料視覺化功能。

```bash
# 進入前端目錄
cd web_frontend

# 啟動開發伺服器（監視 JS 和 CSS 變更）
./scripts/start_dev.sh

# 或使用 npm 命令
npm run start
```

啟動後，可透過 `http://localhost:8080` 訪問前端應用。

### 2. 後端開發（FastAPI）

後端使用 FastAPI 提供高效能的 API 服務，支援非同步處理和自動生成 API 文檔。

```bash
# 進入後端目錄
cd web_service

# 啟動開發伺服器
./scripts/start_dev.sh
```

啟動後，可透過以下網址訪問：

- API 服務：`http://localhost:8000`
- API 文檔：`http://localhost:8000/docs`
- ReDoc 文檔：`http://localhost:8000/redoc`

### 3. 整合開發流程

若要同時進行前後端開發，建議使用以下流程：

#### 使用 VS Code 統一開發環境

如果你使用 VS Code，我們提供了預配置的任務和調試設置：

1. 按 `F1` (或 `Cmd+Shift+P` 在 macOS)，輸入 "Tasks: Run Task"
2. 選擇 `構建前端資源並複製到後端`
3. 選擇 `啟動前端開發服務`
4. 選擇 `啟動後端開發服務`

這些任務讓您可以輕鬆地構建和運行前後端應用。

#### 手動啟動開發環境

1. 首先啟動前端開發伺服器

```bash
cd web_frontend
./scripts/start_dev.sh
```

2. 在另一個終端視窗啟動後端伺服器

```bash
cd web_service
./scripts/start_dev.sh
```

3. 當需要構建前端並整合到後端時，可使用構建腳本

```bash
./scripts/build_frontend.sh --output ./web_service/static
```

### 4. 常見問題排解

- **前端構建失敗**：確認已安裝所有 Node.js 依賴 `cd web_frontend && npm install`
- **後端啟動失敗**：確認已安裝所有 Python 依賴 `cd web_service && pip install -r requirements.txt`
- **靜態文件無法加載**：
  - 檢查 `web_service/static` 目錄是否包含前端構建的文件
  - 執行 `./scripts/build_frontend.sh --output ./web_service/static` 重新構建前端資源
- **API 無法訪問**：確認後端服務正在運行，且運行在正確的主機和端口上
- **DaisyUI 樣式不正確**：
  - 檢查 `web_service/static/css/output.css` 是否存在
  - 確認瀏覽器載入後沒有 CSS 錯誤

## 📚 使用範例

### 1. 原型程式（不依賴核心模組）

```python
# examples/prototype/basic_crawler/simple_crawler.py
import requests
from bs4 import BeautifulSoup

def crawl_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find_all('div', class_='content')
```

### 2. 正式範例（使用核心模組）

#### Playwright 範例（MomoShop 爬蟲）
```python
from examples.formal.momoshop import MomoShopScraper

async def main():
    scraper = MomoShopScraper(
        headless=False,
        proxy=None,
        user_agent=None
    )
    
    products = await scraper.search_products(
        keyword="RTX5080",
        max_pages=1,
        save_to_file=True
    )
```

#### Selenium 範例（PChome 爬蟲）
```python
from examples.formal.pchome import PChomeScraper

def main():
    scraper = PChomeScraper()
    products = scraper.search_products("iPhone")
    scraper.save_results(products)
```

#### API 客戶端範例（股票資料）
```python
from examples.formal.stock import StockDataClient

async def main():
    client = StockDataClient()
    data = await client.get_stock_data("2330")
    client.save_to_database(data)
```

## 📁 專案結構

```
DataScout/
├── playwright_base/     # Playwright 自動化基礎
│   ├── anti_detection/  # 反偵測功能
│   ├── captcha/        # 驗證碼處理
│   └── utils/          # 工具函數
├── selenium_base/       # Selenium 自動化基礎
│   ├── anti_detection/  # 反偵測功能
│   ├── captcha/        # 驗證碼處理
│   └── utils/          # 工具函數
├── api_client/          # API 客戶端
│   ├── rest/           # RESTful API
│   ├── graphql/        # GraphQL
│   └── websocket/      # WebSocket
├── extractors/          # 資料提取器
│   ├── html/           # HTML 提取
│   ├── json/           # JSON 提取
│   └── xml/            # XML 提取
├── adapter/             # 資料轉換器
│   ├── format/         # 格式轉換
│   ├── mapping/        # 欄位映射
│   └── validation/     # 資料驗證
├── persistence/         # 資料儲存管理器
│   ├── file/           # 檔案儲存
│   ├── database/       # 資料庫儲存
│   └── cloud/          # 雲端儲存
└── examples/           # 使用範例
    ├── prototype/      # 原型程式（獨立運作）
    │   ├── basic_crawler/    # 基礎爬蟲示例
    │   └── api_client/       # API 客戶端示例
    └── formal/         # 正式範例（依賴核心模組）
        ├── momoshop/         # MomoShop 爬蟲
        ├── pchome/           # PChome 爬蟲
        └── stock/            # 股票資料
```

## 👨‍💻 開發指南

### 1. 新增功能
- 📋 遵循模組化設計原則
  - 單一職責原則
  - 開放封閉原則
  - 依賴反轉原則
- 🔄 確保向後相容性
  - 版本控制
  - 介面穩定
  - 向下相容
- ✅ 添加適當的單元測試
  - 測試覆蓋率
  - 測試案例
  - 測試自動化
- 📝 更新文檔
  - 功能說明
  - 使用範例
  - API 文檔

### 2. 程式碼風格
- 📏 遵循 PEP 8 規範
  - 命名規範
  - 縮排規範
  - 註解規範
- 📝 使用型別提示
  - 變數型別
  - 函數參數
  - 返回值型別
- 📚 添加詳細的文檔字串
  - 模組文檔
  - 類別文檔
  - 函數文檔
- 📊 使用 loguru 進行日誌記錄
  - 日誌級別
  - 日誌格式
  - 日誌輸出

### 3. 測試
- ✅ 單元測試：`pytest tests/unit`
  - 功能測試
  - 邊界測試
  - 異常測試
- 🔄 整合測試：`pytest tests/integration`
  - 模組整合
  - 系統整合
  - 外部整合
- ⚡ 性能測試：`pytest tests/performance`
  - 響應時間
  - 資源消耗
  - 並發處理

## ⚠️ 注意事項

1. 📜 請遵守網站的使用條款和爬蟲規則
   - 爬蟲協議
   - 使用限制
   - 資料使用規範
2. ⏱️ 建議設定適當的爬取間隔，避免對目標網站造成負擔
   - 請求頻率
   - 並發數量
   - 資源使用
3. 🌐 使用代理 IP 時請確保代理的可用性和穩定性
   - 代理品質
   - 代理切換
   - 代理驗證
4. 🔒 注意資料安全和隱私保護
   - 資料加密
   - 存取控制
   - 資料備份

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 提交 Issue
1. 使用 Issue 模板
2. 提供詳細的問題描述
3. 附上相關的錯誤訊息
4. 提供重現步驟

### 提交 Pull Request
1. Fork 專案
2. 建立功能分支
3. 提交變更
4. 發起 Pull Request

## 📄 授權協議

本專案採用 MIT 授權協議。

## ❓ 常見問題

### 1. 安裝問題
Q: 如何解決依賴安裝失敗？
A: 請確保使用最新版本的 pip，並嘗試使用 `--no-cache-dir` 選項。

### 2. 使用問題
Q: 如何處理驗證碼？
A: 本專案提供內建的驗證碼處理模組，支援多種驗證碼類型。

### 3. 效能問題
Q: 如何提升爬蟲效能？
A: 可以透過調整並發數量、使用代理池、優化選擇器等方式提升效能。

## 📝 更新日誌

### v1.0.0 (2024-03-20)
- 🎉 首次發布
- ✨ 新增核心功能
- 📚 完善文檔
- 🐛 修復已知問題

### v0.9.0 (2024-03-10)
- 🚀 新增自動化功能
- 🔧 優化效能
- 📝 更新文檔
- 🐛 修復錯誤
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

### 4. 基本使用

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

## 🤔 自動化方案選擇

### Playwright vs Selenium

#### Playwright 優勢
- 🆕 更現代的架構
  - 專為現代網頁設計
  - 支援最新的網頁技術
  - 更好的非同步處理
- 💪 更強大的自動化能力
  - 內建等待機制
  - 更好的網路控制
  - 更精確的元素定位
- 🛡️ 更好的反偵測
  - 內建指紋偽造
  - 更真實的瀏覽器環境
  - 更好的 Cookie 管理
- 🌐 跨瀏覽器支援
  - 單一 API
  - 更好的相容性
  - 更少的程式碼差異
- ⚡ 更快的執行速度
  - 更輕量級的架構
  - 更少的資源消耗
  - 更好的並發處理

#### Selenium 優勢
- 🏢 更成熟的生態系統
  - 更多的第三方套件
  - 更豐富的學習資源
  - 更大的社群支援
- 🌍 更廣泛的瀏覽器支援
  - 支援更多版本
  - 更好的向後相容性
  - 更多的瀏覽器選項
- 🎓 更簡單的入門門檻
  - 更直觀的 API
  - 更少的配置需求
  - 更簡單的學習曲線
- 💪 更好的穩定性
  - 經過長期驗證
  - 更少的版本問題
  - 更好的錯誤處理

### 選擇建議

1. **使用 Playwright 的情況**
   - 📱 需要處理現代網頁應用
   - 🛡️ 需要更好的反偵測能力
   - ⚡ 需要更快的執行速度
   - 🌐 需要跨瀏覽器支援
   - 🔄 需要更好的非同步處理
   - 🎯 需要更精確的元素定位

2. **使用 Selenium 的情況**
   - 🏢 需要支援舊版瀏覽器
   - 🛠️ 需要使用特定的第三方套件
   - 👥 需要更好的社群支援
   - 🎓 需要更簡單的入門門檻
   - 🔄 需要更好的同步處理
   - 💪 需要更好的穩定性

## 🔌 API 客戶端選擇

### HTTPX vs Requests

#### HTTPX 優勢
- 🔄 同步和異步支援
  - 支援同步操作
  - 支援異步操作
  - 混合使用模式
- 🌐 HTTP/2 支援
  - 原生 HTTP/2
  - 連接複用
  - 更低的延遲
- 🆕 更現代的特性
  - WebSocket 支援
  - HTTP/2 Server Push
  - HTTP/3 (QUIC) 支援
- 📝 更好的型別提示
  - 完整的型別註解
  - 更好的 IDE 支援
  - 更容易進行靜態型別檢查
- ⚙️ 更靈活的配置
  - 細緻的超時控制
  - 更好的代理支援
  - 更靈活的 SSL/TLS 配置

### 使用範例

```python
# 同步請求
from api_client import APIClient

def sync_example():
    client = APIClient()
    response = client.get("https://api.example.com/data")
    return response.json()

# 異步請求
async def async_example():
    client = APIClient()
    async with client as ac:
        response = await ac.get("https://api.example.com/data")
        return await response.json()

# HTTP/2 請求
async def http2_example():
    client = APIClient(http2=True)
    async with client as ac:
        response = await ac.get("https://api.example.com/data")
        return await response.json()

# WebSocket 連接
async def websocket_example():
    client = APIClient()
    async with client.websocket_connect("wss://api.example.com/ws") as websocket:
        await websocket.send("Hello!")
        response = await websocket.receive()
        return response
```

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
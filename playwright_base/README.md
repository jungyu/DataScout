# Playwright Base 模組

## 專案概述

Playwright Base 模組提供了基於 Playwright 的自動化測試和爬蟲基礎框架。本模組封裝了常用的自動化操作，提供了統一的接口來處理瀏覽器自動化任務，並包含強大的反檢測功能。

## 環境設置

### 1. 創建虛擬環境

```bash
# 進入專案根目錄
cd /Users/aaron/Projects/DataScout

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
# 進入 playwright_base 目錄
cd playwright_base

# 安裝依賴套件
pip install -e .

# 安裝 Playwright 瀏覽器
playwright install
```

### 3. 環境變數設置

在專案根目錄創建 `.env` 文件，添加以下配置：

```env
# Playwright 配置
HEADLESS=true
SLOW_MO=100
TIMEOUT=30000

# 代理配置（可選）
PROXY_SERVER=
PROXY_USERNAME=
PROXY_PASSWORD=
```

## 目錄結構

```
playwright_base/
├── core/           # 核心組件
├── anti_detection/ # 反檢測功能
├── auth/          # 認證模組
├── config/        # 配置管理
├── services/      # 外部服務整合
├── storage/       # 存儲模組
├── utils/         # 工具函數
├── examples/      # 使用範例
└── scripts/       # 實用腳本
```

## 使用方式

### 基本使用

```python
from playwright_base import PlaywrightBase

# 創建瀏覽器實例
browser = PlaywrightBase()

# 啟動瀏覽器
async with browser.launch() as page:
    # 訪問網頁
    await page.goto('https://example.com')
    
    # 執行操作
    await page.click('#button')
    
    # 獲取數據
    data = await page.text_content('#content')
```

### 反檢測功能

```python
from playwright_base import PlaywrightBase
from playwright_base.anti_detection import HumanLikeBehavior

# 創建瀏覽器實例
browser = PlaywrightBase()

# 啟用反檢測
browser.enable_stealth_mode()

# 使用人類行為模擬
human = HumanLikeBehavior()

async with browser.launch() as page:
    # 模擬人類行為
    await human.scroll_page(page)
    await human.random_delay()
```

## 主要功能

1. 瀏覽器管理
   - 多瀏覽器支援
   - 上下文管理
   - 頁面管理

2. 反檢測功能
   - 瀏覽器指紋偽裝
   - 人類行為模擬
   - 代理管理
   - 用戶代理管理

3. 自動化操作
   - 元素定位
   - 事件處理
   - 表單操作
   - 文件上傳

4. 數據處理
   - 文本提取
   - 圖片下載
   - 表格數據
   - JSON 解析

## 注意事項

1. 確保在執行前已啟動虛擬環境
2. 檢查環境變數是否正確設置
3. 確保所有依賴都已正確安裝
4. 注意網站的使用條款和爬蟲規範

## 依賴套件說明

### 核心依賴
- `playwright`: 瀏覽器自動化框架
- `python-dotenv`: 環境變數管理
- `user-agents`: 用戶代理管理
- `requests`: HTTP 客戶端
- `pillow`: 圖像處理
- `loguru`: 日誌管理
- `beautifulsoup4`: HTML 解析

### 開發依賴
- `aiohttp`: 非同步 HTTP 客戶端
- `httpx`: 現代 HTTP 客戶端
- `pandas`: 數據處理
- `numpy`: 數值計算
- `pytest`: 測試框架
- `pytest-asyncio`: 非同步測試支援
- `pytest-playwright`: Playwright 測試插件
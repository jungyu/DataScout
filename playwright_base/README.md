# Playwright Base 模組

## 專案概述

Playwright Base 模組提供了基於 Playwright 的自動化測試和爬蟲基礎框架。本模組封裝了常用的自動化操作，提供了統一的接口來處理瀏覽器自動化任務。

## 環境設置

### 1. 創建虛擬環境

```bash
# 進入 playwright_base 目錄
cd playwright_base

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
├── pages/          # 頁面對象
├── tests/          # 測試用例
├── utils/          # 工具函數
└── examples/       # 使用範例
```

## 使用方式

### 基本使用

```python
from playwright_base import BrowserManager

# 創建瀏覽器管理器
browser = BrowserManager()

# 啟動瀏覽器
async with browser.launch() as page:
    # 訪問網頁
    await page.goto('https://example.com')
    
    # 執行操作
    await page.click('#button')
    
    # 獲取數據
    data = await page.text_content('#content')
```

### 測試用例

```python
import pytest
from playwright_base import BrowserManager

@pytest.mark.asyncio
async def test_example():
    browser = BrowserManager()
    async with browser.launch() as page:
        await page.goto('https://example.com')
        assert await page.title() == 'Example Domain'
```

## 主要功能

1. 瀏覽器管理
   - 多瀏覽器支援
   - 上下文管理
   - 頁面管理

2. 自動化操作
   - 元素定位
   - 事件處理
   - 表單操作
   - 文件上傳

3. 數據提取
   - 文本提取
   - 圖片下載
   - 表格數據
   - JSON 解析

4. 測試功能
   - 單元測試
   - 集成測試
   - 端到端測試
   - 性能測試

## 注意事項

1. 確保在執行前已啟動虛擬環境
2. 檢查環境變數是否正確設置
3. 確保所有依賴都已正確安裝
4. 注意網站的使用條款和爬蟲規範

## 依賴套件說明

- `playwright`: 瀏覽器自動化框架
- `pytest`: 測試框架
- `pytest-asyncio`: 非同步測試支援
- `pytest-playwright`: Playwright 測試插件
- `python-dotenv`: 環境變數管理
- `pandas`: 數據處理
- `numpy`: 數值計算
- `aiohttp`: 非同步 HTTP 客戶端
- `httpx`: 現代 HTTP 客戶端
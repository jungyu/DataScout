# Selenium 爬蟲專案架構說明

## 專案概述

此專案使用 Selenium 實現網頁爬蟲功能，主要用於自動化網頁數據擷取。採用模組化設計，確保代碼的可維護性、可擴展性和可重用性。

## 完整目錄結構

```
crawler-selenium/
├── src/                # 源碼目錄
│   ├── core/           # 核心模組
│   │   ├── webdriver_manager.py
│   │   ├── template_crawler.py
│   │   └── crawler_engine.py
│   ├── anti_detection/ # 反爬蟲模組
│   ├── captcha/        # 驗證碼處理模組
│   ├── persistence/    # 數據持久化模組
│   ├── models/         # 資料模型
│   └── utils/          # 工具函數
├── tests/              # 測試檔案
└── docs/               # 文件說明
```

## 核心元件說明

### 1. WebDriver 管理器 (`src/core/webdriver_manager.py`)
- 負責初始化和管理 Selenium WebDriver
- 處理瀏覽器設定和會話管理

### 2. 爬蟲核心 (`src/core/`)
- template_crawler.py: 模板化爬蟲核心類
- crawler_engine.py: 爬蟲引擎
- 實現頁面導覽和數據擷取邏輯

### 3. 反爬蟲模組 (`src/anti_detection/`)
- 提供反爬蟲策略
- 處理瀏覽器指紋
- 管理代理和 IP 輪替

### 4. 驗證碼處理模組 (`src/captcha/`)
- 支援多種驗證碼類型
- 整合機器學習解決方案
- 驗證碼識別和自動處理

### 5. 數據持久化模組 (`src/persistence/`)
- 支援多種存儲方式
- 數據格式轉換
- 備份機制

## 系統工作流程

1. **初始化階段**
   - 載入配置文件
   - 初始化 WebDriver
   - 設置反爬蟲參數

2. **爬蟲執行**
   - 模板解析
   - 頁面導覽
   - 元素定位與互動
   - 數據擷取

3. **數據處理**
   - 數據清理和驗證
   - 格式轉換
   - 持久化存儲

## 錯誤處理機制

- 網路異常重試機制
- 元素定位失敗處理
- 驗證碼處理失敗處理
- 狀態保存和恢復機制

## 配置管理

### 主要配置文件
```json
{
    "base_url": "https://example.com",
    "headless": true,
    "max_pages": 10,
    "max_items": 200
    // ...其他配置項
}
```

### 爬蟲模板格式
```json
{
    "site_name": "範例網站",
    "base_url": "https://example.com",
    "encoding": "utf-8",
    // ...其他模板設定
}
```

## 使用範例

```python
from src.core.template_crawler import TemplateCrawler

# 初始化爬蟲
crawler = TemplateCrawler(
    template_file="templates/example.json",
    config_file="config/config.json"
)

# 執行爬蟲
data = crawler.crawl(max_pages=5)
```

## 系統特點

1. 高度模組化設計
2. 強大的反爬蟲能力
3. 完整的驗證碼處理
4. 可靠的狀態管理
5. 靈活的數據持久化
6. 模板化配置支援
7. 詳細的日誌記錄

## 注意事項

1. 遵守網站的爬蟲政策
2. 實作請求延遲機制
3. 定期維護選擇器
4. 注意數據備份
5. 監控系統資源使用

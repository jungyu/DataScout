# Selenium 模板化爬蟲框架 - 目錄結構和模組說明


## 目錄結構

```
crawler-selenium/
│
├── main.py                      # 爬蟲程式主入口
│
├── examples/                    # 爬蟲範例目錄
│   ├── formal_1_google_search.py  # Google 搜尋爬蟲範例
│   ├── basic_google_search.json   # Google 搜尋爬蟲配置
│   └── other_examples.py          # 其他爬蟲範例
│
├── config/                      # 配置文件目錄
│   ├── config.json              # 主配置文件
│   ├── credentials.json         # 憑證配置（不應納入版本控制）
│   └── captcha_config.json      # 驗證碼處理配置
│
├── templates/                   # 爬蟲模板目錄
│   ├── gov_procurement.json     # 政府採購網模板
│   ├── real_estate.json         # 實價登錄模板
│   ├── shopee.json              # 蝦皮網站模板
│   ├── ubereats.json            # UberEats 模板
│   └── example.json             # 示例模板
│
├── src/                         # 源代碼目錄
│   ├── core/                    # 核心模塊
│   │   ├── __init__.py
│   │   ├── config_loader.py     # 配置加載器
│   │   ├── template_crawler.py  # 模板化爬蟲核心類
│   │   └── webdriver_manager.py # WebDriver 管理器
│   │
│   ├── extractors/              # 數據提取模塊
│   │   ├── __init__.py
│   │   ├── config.py            # 提取配置類
│   │   ├── list_extractor.py    # 列表頁提取器
│   │   ├── captcha_handler.py   # 驗證碼處理器 
│   │   ├── pagination_handler.py # 分頁處理器
│   │   ├── storage_handler.py   # 存儲處理器
│   │   └── core/                # 提取核心模塊
│   │       ├── __init__.py
│   │       ├── base_extractor.py # 基礎提取器
│   │       ├── detail_extractor.py # 詳情頁提取器
│   │       └── element_extractor.py # 元素提取器
│   │
│   ├── anti_detection/          # 反爬蟲模塊
│   │   ├── __init__.py
│   │   ├── stealth_mode.py      # WebDriver隱身模式
│   │   ├── proxy_manager.py     # 代理伺服器管理
│   │   └── behavior_simulator.py # 人類行為模擬
│   │
│   ├── navigation/              # 頁面導航模塊【建議新增】
│   │   ├── __init__.py
│   │   ├── navigator.py         # 頁面導航控制器
│   │   ├── wait_strategies.py   # 等待策略
│   │   └── scroll_manager.py    # 滾動管理器
│   │
│   ├── interaction/             # 頁面互動模塊【建議新增】
│   │   ├── __init__.py
│   │   ├── form_handler.py      # 表單處理器
│   │   ├── search_handler.py    # 搜尋處理器
│   │   └── element_interactor.py # 元素互動器
│   │
│   ├── persistence/             # 數據持久化模塊
│   │   ├── __init__.py
│   │   ├── data_manager.py      # 數據管理器
│   │   ├── file_storage.py      # 文件存儲
│   │   └── database.py          # 資料庫存儲
│   │
│   └── utils/                   # 工具模塊
│       ├── __init__.py
│       ├── logger.py            # 日誌工具
│       ├── text_cleaner.py      # 文本清理工具
│       ├── url_utils.py         # URL處理工具
│       └── error_handler.py     # 錯誤處理工具
│
├── output/                      # 輸出目錄
│   ├── google_搜尋_results_*.json # Google搜尋結果
│   └── google_搜尋_details_*.json # Google詳情頁結果
│
├── data/                        # 數據儲存目錄
│   ├── raw/                     # 原始數據
│   └── processed/               # 處理後數據
│
├── logs/                        # 日誌目錄
│
├── tests/                       # 測試代碼目錄
│   ├── __init__.py
│   ├── test_core.py
│   ├── test_extractors.py
│   └── test_utils.py
│
└── docs/                        # 文檔目錄
    ├── architecture.md          # 架構說明
    ├── anti_detection.md        # 反偵測機制說明
    ├── captcha_handling.md      # 驗證碼處理說明
    ├── template_format.md       # 模板格式說明
    ├── structures.md            # 目錄結構說明
    └── api_reference.md         # API參考文檔
```

## 模組說明

### 1. 核心模組 (`src/core/`)

- **app.py**：應用程式主類
  - 爬蟲應用程式入口
  - 配置管理和初始化
  - 模組協調和生命週期管理

- **crawler_engine.py**：爬蟲引擎
  - 爬蟲流程控制
  - 任務調度和執行
  - 錯誤處理和恢復

- **template_crawler.py**：模板化爬蟲核心類
  - 模板解析和驗證
  - 爬蟲邏輯生成
  - 模板繼承和覆蓋

- **webdriver_manager.py**：WebDriver 管理器
  - 瀏覽器實例管理
  - 瀏覽器配置和選項
  - 會話生命週期管理

### 2. 資料擷取模組 (`src/extractors/`)

- **base.py**：基礎擷取器
  - 統一的擷取介面
  - 資料清理和驗證
  - 錯誤處理和重試

- **list_extractor.py**：列表頁擷取器
  - 列表頁元素定位
  - 列表資料擷取
  - 分頁處理

- **detail_extractor.py**：詳情頁擷取器
  - 詳情頁元素定位
  - 詳情資料擷取
  - 動態內容處理

### 3. 導航模組 (`src/navigation/`)

- **navigator.py**：頁面導航管理
  - URL 處理和導航
  - 等待策略管理
  - 導航錯誤處理

- **pagination.py**：分頁處理
  - 分頁策略實現
  - 分頁元素定位
  - 分頁狀態管理

### 4. 互動模組 (`src/interaction/`)

- **form_handler.py**：表單處理
  - 表單元素定位
  - 表單填寫和提交
  - 表單驗證

- **search_handler.py**：搜尋處理
  - 搜尋參數設置
  - 搜尋表單處理
  - 搜尋結果驗證

- **element_handler.py**：元素互動
  - 元素點擊和輸入
  - 元素等待和重試
  - 元素狀態檢查

### 5. 反爬蟲模組 (`src/anti_detection/`)

- **stealth.py**：隱身模式
  - WebDriver 特徵消除
  - User-Agent 管理
  - 自動化痕跡隱藏

- **behavior.py**：行為模擬
  - 人類行為模擬
  - 隨機延遲和等待
  - 鼠標和鍵盤模擬

### 6. 資料持久化模組 (`src/persistence/`)

- **state.py**：狀態管理
  - 爬蟲狀態保存
  - 斷點續爬支援
  - 狀態恢復機制

- **storage.py**：存儲管理
  - 多格式資料存儲
  - 資料快取管理
  - 存儲策略實現

- **exporters/**：資料匯出器
  - JSON 匯出器
  - CSV 匯出器
  - 資料庫匯出器

### 7. 工具模組 (`src/utils/`)

- **text.py**：文本處理
  - 文本清理和標準化
  - 特殊字符處理
  - 文本格式化

- **url.py**：URL處理
  - URL 解析和構建
  - 參數處理
  - 相對路徑轉換

- **retry.py**：重試機制
  - 自動重試策略
  - 退避算法實現
  - 重試條件配置

- **validation.py**：資料驗證
  - 資料格式驗證
  - 必填欄位檢查
  - 資料類型轉換

## 設計原則

### 模板驅動設計
- 所有爬蟲邏輯通過 JSON 模板配置
- 模板繼承和覆蓋機制
- 模板驗證和錯誤檢查

### 擴展性設計
- 插件式架構
- 自定義擷取器支援
- 自定義存儲後端

### 錯誤處理
- 分層錯誤處理
- 自動重試機制
- 詳細錯誤日誌

### 效能考慮
- 併發爬取支援
- 資源使用優化
- 快取機制

## 使用建議

1. 新增網站爬蟲時：
   - 在 `templates/sites/` 建立新模板
   - 在 `config/sites/` 加入配置
   - 在 `examples/` 提供範例

2. 開發新功能時：
   - 遵循模組化設計
   - 編寫單元測試
   - 更新文檔

3. 維護建議：
   - 定期更新依賴
   - 監控錯誤日誌
   - 更新反檢測機制

# 排除實際配置檔案，但保留範例檔案
/config/*.json
!/config/_*.json

# 憑證和敏感資訊
/config/credentials.json
/certs/
/keys/

# 資料和日誌
/data/
/logs/
/captchas/
```



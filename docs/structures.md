# Selenium 模板化爬蟲框架 - 目錄結構和模組說明


## 目錄結構

```
crawler-selenium/
│
├── main.py                      # 爬蟲程式主入口
│
├── config/                      # 配置文件目錄
│   ├── config.json              # 主配置文件
│   ├── credentials.json         # 憑證配置（不應納入版本控制）
│   └── captcha_config.json      # 驗證碼處理配置
│
├── templates/                   # 爬蟲模板目錄
│   ├── gov_procurement.json     # 政府採購網模板
│   └── example.json             # 示例模板
│
├── src/                         # 源代碼目錄
│   ├── core/                    # 核心模塊
│   │   ├── __init__.py
│   │   ├── crawler_engine.py    # 爬蟲引擎
│   │   ├── template_crawler.py  # 模板化爬蟲核心類
│   │   └── webdriver_manager.py # WebDriver 管理器
│   │
│   ├── anti_detection/          # 反爬蟲模塊
│   │   ├── __init__.py
│   │   ├── stealth_mode.py      # WebDriver隱身模式
│   │   ├── proxy_manager.py     # 代理伺服器管理
│   │   └── behavior_simulator.py # 人類行為模擬
│   │
│   ├── captcha/                 # 驗證碼處理模塊
│   │   ├── __init__.py
│   │   ├── captcha_manager.py   # 驗證碼管理器
│   │   ├── image_captcha.py     # 圖形驗證碼處理
│   │   └── recaptcha.py         # Google reCAPTCHA 處理
│   │
│   ├── persistence/             # 數據持久化模塊
│   │   ├── __init__.py
│   │   ├── data_manager.py      # 數據管理器
│   │   ├── file_storage.py      # 文件存儲
│   │   └── database.py          # 資料庫存儲
│   │
│   ├── models/                  # 資料模型
│   │   ├── __init__.py
│   │   ├── crawl_result.py      # 爬蟲結果模型
│   │   └── page_template.py     # 頁面模板模型
│   │
│   └── utils/                   # 工具模塊
│       ├── __init__.py
│       ├── logger.py            # 日誌工具
│       ├── config_loader.py     # 配置加載工具
│       └── url_utils.py         # URL處理工具
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

## 模組詳細說明

### 1. 核心模塊 (`src/core/`)

- **crawler_engine.py**：爬蟲引擎，負責執行網頁爬取的核心邏輯
  - 頁面導航和交互操作實現
  - 元素定位和數據提取
  - 異常處理機制
  - 執行爬取流程控制

- **template_crawler.py**：模板化爬蟲實現
  - 解析 JSON 格式的爬蟲模板
  - 將模板轉換為爬取指令
  - 提供模板自定義擴展功能
  - 支援多種數據格式處理

- **webdriver_manager.py**：WebDriver 管理器
  - 自動下載和配置 WebDriver
  - 瀏覽器選項和參數管理
  - 瀏覽器會話生命週期管理
  - 支援多種瀏覽器類型

### 2. 反爬蟲模塊 (`src/anti_detection/`)

- **stealth_mode.py**：WebDriver 隱身模式
  - 消除 WebDriver 特徵
  - 修改 User-Agent
  - 隱藏自動化痕跡

- **proxy_manager.py**：代理伺服器管理
  - 支援 HTTP、SOCKS 等多種代理
  - 代理伺服器輪替機制
  - 代理有效性驗證

- **behavior_simulator.py**：人類行為模擬
  - 隨機等待時間
  - 仿真鼠標移動軌跡
  - 逼真的頁面滾動行為
  - 鍵盤輸入速度隨機化

### 3. 驗證碼處理模塊 (`src/captcha/`)

- **captcha_manager.py**：驗證碼管理器
  - 自動檢測頁面驗證碼類型
  - 協調不同類型驗證碼處理
  - 驗證碼解決失敗後的重試策略

- **image_captcha.py**：圖形驗證碼處理
  - 圖片驗證碼識別
  - 整合 OCR 功能
  - 支援基本的圖像處理

- **recaptcha.py**：Google reCAPTCHA 處理
  - 支援 reCAPTCHA v2/v3
  - 音頻驗證碼解決
  - 整合第三方服務

### 4. 數據持久化模塊 (`src/persistence/`)

- **data_manager.py**：數據管理器
  - 統一數據存取介面
  - 多種存儲方式的協調
  - 數據轉換和導出功能

- **file_storage.py**：文件存儲
  - JSON、CSV、Excel 等多種格式支援
  - 文件命名和目錄管理
  - 增量式數據存儲

- **database.py**：資料庫存儲
  - 關聯式資料庫連接管理
  - SQL 查詢構建
  - ORM 映射支援

### 5. 工具模塊 (`src/utils/`)

- **logger.py**：日誌工具
  - 分層次日誌記錄
  - 日誌檔案輪替
  - 錯誤通知機制

- **config_loader.py**：配置加載工具
  - 配置檔案解析
  - 環境變量整合
  - 敏感信息保護

- **url_utils.py**：URL處理工具
  - URL 生成和解析
  - 參數處理
  - 相對路徑轉絕對路徑
```
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



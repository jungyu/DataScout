# 網站爬蟲專案 - 目錄結構及說明

## 專案概述

本專案是一個基於 Selenium 的模組化網站爬蟲系統，專門設計用於處理需要動態渲染、互動式操作的網站爬取任務。特別適合政府採購網等具有複雜驗證機制的網站。

### 主要特色

- 模板化設計：透過 JSON 配置檔案定義爬蟲行為
- 強大的反偵測功能：自動處理瀏覽器指紋、代理設定
- 驗證碼處理：支援多種驗證碼類型的自動化解決方案
- 分散式架構：支援多機器parallel爬取
- 狀態管理：支援斷點續爬

```
crawler-selenium/
│
├── config/                      # 配置文件目錄
│   ├── config.json              # 主配置文件
│   ├── persistence_config.json  # 數據持久化配置
│   ├── credentials.json         # 憑證配置（不應納入版本控制）
│   ├── anti_detection_config.json # 反爬蟲配置
│   ├── captcha_config.json      # 驗證碼處理配置
│   └── field_mappings.json      # 字段映射配置
│
├── templates/                   # 爬蟲模板目錄
│   ├── gov_procurement.json     # 網站模板
│   └── example.json             # 示例模板
│
├── src/                         # 源代碼目錄
│   ├── core/                    # 核心模塊
│   │   ├── __init__.py
│   │   ├── template_crawler.py  # 模板化爬蟲核心類
│   │   ├── webdriver_manager.py # WebDriver 管理器
│   │   └── crawler_engine.py    # 爬蟲引擎
│   │
│   ├── utils/                   # 工具模塊
│   │   ├── __init__.py
│   │   ├── config_loader.py     # 配置載入工具
│   │   ├── cookie_manager.py    # Cookie 管理工具
│   │   ├── error_handler.py     # 錯誤處理工具
│   │   ├── logger.py            # 日誌工具
│   │   ├── auth_manager.py      # 權限管理工具
│   │   └── rate_limiter.py      # 請求頻率限制工具
│   │
│   ├── anti_detection/          # 反爬蟲模塊
│   │   ├── __init__.py
│   │   ├── anti_detection_manager.py  # 反爬蟲管理器
│   │   └── stealth_scripts/     # 隱身腳本
│   │       └── browser_fp.js    # 瀏覽器指紋修改腳本
│   │
│   ├── captcha/                 # 驗證碼處理模塊
│   │   ├── __init__.py
│   │   ├── captcha_manager.py   # 驗證碼管理器
│   │   ├── solvers/             # 各類驗證碼解決器
│   │   │   ├── __init__.py
│   │   │   ├── base_solver.py   # 基礎解決器類
│   │   │   ├── text_solver.py   # 文字驗證碼解決器
│   │   │   ├── slider_solver.py # 滑塊驗證碼解決器
│   │   │   ├── click_solver.py  # 點擊驗證碼解決器
│   │   │   └── recaptcha_solver.py # ReCAPTCHA 解決器
│   │   └── ml/                  # 機器學習相關
│   │       ├── __init__.py
│   │       └── model_loader.py  # 模型載入工具
│   │
│   ├── state/                   # 狀態管理模塊
│   │   ├── __init__.py
│   │   ├── crawler_state_manager.py  # 爬蟲狀態管理器
│   │   └── multi_storage.py     # 多重儲存機制
│   │
│   └── persistence/             # 數據持久化模塊
│       ├── __init__.py
│       ├── data_persistence_manager.py # 數據持久化管理器
│       ├── mongodb_handler.py   # MongoDB 處理器
│       ├── notion_handler.py    # Notion 處理器
│       └── local_storage.py     # 本地存儲處理器
│
├── data/                        # 數據儲存目錄
│   ├── raw/                     # 原始數據
│   ├── processed/               # 處理後數據
│   └── exports/                 # 導出數據
│
├── logs/                        # 日誌目錄
│
├── states/                      # 狀態儲存目錄
│   └── backups/                 # 狀態備份
│
├── captchas/                    # 驗證碼樣本目錄
│   ├── text/                    # 文字驗證碼
│   ├── slider/                  # 滑塊驗證碼
│   ├── click/                   # 點擊驗證碼
│   └── recaptcha/               # ReCAPTCHA
│
├── cookies/                     # Cookie 儲存目錄
│
├── models/                      # 機器學習模型目錄
│
├── tests/                       # 測試代碼目錄
│   ├── __init__.py
│   ├── test_template_crawler.py
│   ├── test_anti_detection.py
│   └── test_captcha.py
│
├── scripts/                     # 腳本目錄
│   ├── setup.py                 # 環境設置腳本
│   ├── run_crawler.py           # 運行爬蟲腳本
│   └── analyze_results.py       # 結果分析腳本
│
├── examples/                    # 示例代碼目錄
│   ├── basic_usage.py           # 基本使用示例
│   └── advanced_usage.py        # 高級使用示例
│
├── docs/                        # 文檔目錄
│   ├── architecture.md          # 架構說明
│   ├── modules.md               # 模塊說明
│   ├── templates.md             # 模板格式說明
│   ├── anti_detection.md        # 反爬蟲機制說明
│   └── captcha.md               # 驗證碼處理說明
│
├── main.py                      # 主程序入口
├── requirements.txt             # 依賴項列表
├── Dockerfile                   # Docker 配置
├── docker-compose.yml           # Docker Compose 配置
├── .gitignore                   # Git 忽略文件
└── README.md                    # 項目說明
```

## 部署與執行

### 環境需求

- Python 3.8+
- Chrome/Firefox 瀏覽器
- Docker (選用)

### 快速開始

1. 安裝相依套件：
```bash
pip install -r requirements.txt
```

2. 設定配置檔：
```bash
cp config/config.example.json config/config.json
# 編輯 config.json 設定爬蟲參數
```

3. 執行爬蟲：
```bash
python main.py --template templates/gov_procurement.json
```

### Docker 部署

```bash
# 建立映像檔
docker build -t crawler-selenium .

# 執行容器
docker run -v $(pwd)/data:/app/data crawler-selenium
```

## 使用案例

### 1. 基本爬取流程

```python
from src.core.template_crawler import TemplateCrawler
from src.utils.config import Config

# 載入配置
config = Config.from_file('config/config.json')

# 初始化爬蟲
crawler = TemplateCrawler(config)

# 開始爬取
results = crawler.crawl(
    max_pages=5,
    save_to_db=True,
    export_format='csv'
)
```

### 2. 自定義驗證碼處理

```python
from src.captcha.solvers import CustomCaptchaSolver

class MyCaptchaSolver(CustomCaptchaSolver):
    def solve(self, image):
        # 實作驗證碼處理邏輯
        return result

# 註冊自定義解決器
crawler.register_captcha_solver(MyCaptchaSolver())
```

## 故障排除

### 常見問題

1. **驗證碼識別失敗**
   - 檢查 `captcha_config.json` 設定
   - 確認模型檔案存在
   
2. **瀏覽器自動化失敗**
   - 更新 WebDriver
   - 檢查瀏覽器版本相容性

3. **資料儲存異常**
   - 確認資料庫連線設定
   - 檢查磁碟空間

### 除錯模式

啟用詳細日誌：
```bash
python main.py --debug --log-level DEBUG
```

## 專案維護

### 代碼品質

- 使用 pre-commit hooks 確保代碼品質
- 遵循 PEP 8 規範
- 單元測試覆蓋率 > 80%

### 貢獻指南

1. Fork 專案
2. 建立 feature 分支
3. 提交變更
4. 發起 Pull Request

## 資安考量

- 所有敏感資訊應存放於 `credentials.json`
- 使用環境變數注入敏感資訊
- 定期更新相依套件
- 實作請求頻率限制

## 主要模塊說明

### 1. 核心模塊 (`src/core/`)

- **crawler_base.py**：爬蟲基礎類別，定義共用介面與基本功能
  - 提供爬蟲生命週期管理
  - 實作重試機制與錯誤處理
  - 整合記錄器與監控功能

- **template_crawler.py**：模板化爬蟲實作
  - 繼承自 crawler_base.py
  - 解析並執行 JSON 模板定義的爬取邏輯
  - 支援動態配置與即時調整

- **crawler_engine.py**：爬蟲引擎
  - 管理爬蟲實例池
  - 協調資源分配
  - 提供任務排程與負載平衡

- **webdriver_manager.py**：瀏覽器驅動管理
  - 智能代理選擇
  - 瀏覽器配置優化
  - WebDriver 生命週期管理

### 2. 工具模塊 (`src/utils/`)

- **config_loader.py**：安全地載入和管理配置文件，處理敏感信息。
- **cookie_manager.py**：管理 Cookie 的保存、載入和更新。
- **error_handler.py**：提供錯誤處理機制，包括重試邏輯。
- **logger.py**：提供統一的日誌記錄功能。
- **auth_manager.py**：提供統一的權限驗證機制，管理不同來源的認證資訊，支援多重認證方式（Basic Auth, Token, OAuth等）。
- **rate_limiter.py**：實現自適應的請求頻率控制，支援多級別的限流策略，提供分布式限流能力。

### 3. 反爬蟲模塊 (`src/anti_detection/`)

- **anti_detection_manager.py**：提供全面的反爬蟲策略，檢測和應對各種反爬機制。
- **stealth_scripts/**：包含用於隱藏爬蟲特徵的 JavaScript 腳本。

### 4. 驗證碼處理模塊 (`src/captcha/`)

- **captcha_manager.py**：驗證碼處理的核心類，協調各類驗證碼解決器。
- **solvers/**：包含各種類型的驗證碼解決器實現。
- **ml/**：包含機器學習相關的驗證碼處理功能。

### 5. 狀態管理模塊 (`src/state/`)

- **crawler_state_manager.py**：管理爬蟲狀態，支持任務的中斷和恢復。
- **multi_storage.py**：實現狀態的多重備份機制，提高可靠性。

### 6. 數據持久化模塊 (`src/persistence/`)

- **data_persistence_manager.py**：數據持久化的核心類，協調各種存儲方式。
- **mongodb_handler.py**：處理 MongoDB 數據存儲。
- **notion_handler.py**：處理 Notion 數據存儲。
- **local_storage.py**：處理本地文件系統存儲。

### 7. 日誌處理模塊 (`src/logs/`)

- **log_formatter.py**：自定義日誌格式化
- **log_rotator.py**：日誌文件輪轉管理
- **handlers/**：多樣化的日誌輸出處理

## 配置文件說明

### 1. 主配置文件 (`config/config.json`)

包含爬蟲的基本配置，如目標 URL、請求參數、爬取設置等。

```json
{
    "base_url": "https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic",
    "query_params": {
        "pageSize": 100,
        "firstSearch": "true",
        "searchType": "basic",
        "isBinding": "N",
        "isLogIn": "N",
        "level_1": "on",
        "orgName": "",
        "orgId": "3.10.3",
        "tenderName": "",
        "tenderId": "",
        "tenderType": "TENDER_DECLARATION",
        "tenderWay": "TENDER_WAY_ALL_DECLARATION",
        "dateType": "isDate",
        "tenderStartDate": "2023/09/01",
        "tenderEndDate": "2023/09/30",
        "radProctrgCate": "",
        "policyAdvocacy": ""
    },
    "headless": true,
    "max_pages": 10,
    "max_items": 200
}
```

### 2. 爬蟲模板 (`templates/gov_procurement.json`)

定義如何爬取特定網站的模板，包含選擇器、參數和延遲設置。

```json
{
  "site_name": "網站",
  "base_url": "https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic",
  "encoding": "utf-8",
  
  "request": {
    "method": "GET",
    "params": {
      "fixed": {
        "firstSearch": "true",
        "searchType": "basic"
      },
      "variable": {
        "pageSize": {
          "description": "每頁顯示數量",
          "default": "100",
          "type": "integer"
        },
        "tenderStartDate": {
          "description": "發布日期起始",
          "type": "date",
          "format": "yyyy/MM/dd"
        }
      },
      "pagination": {
        "page_param": "pageIndex",
        "base_index": 1
      }
    }
  },
  
  "delays": {
    "page_load": {"min": 3, "max": 7},
    "between_pages": {"min": 5, "max": 10},
    "between_items": {"min": 2, "max": 5}
  },
  
  "list_page": {
    "container_xpath": "//table[@id='tpam']/tbody",
    "item_xpath": "./tr",
    "fields": {
      "tender_case_no": {"xpath": "./td[3]", "type": "text"},
      "tender_name": {"xpath": "./td[3]/a/span", "type": "text"},
      "detail_link": {"xpath": "./td[3]/a", "type": "attribute", "attribute_name": "href"}
    }
  },
  
  "pagination": {
    "next_button_xpath": "//span[@id='pagelinks']/a[contains(text(), '下一頁')]",
    "has_next_page_check": "//span[@id='pagelinks']/a[contains(text(), '下一頁')]"
  },
  
  "detail_page": {
    "container_xpath": "//div[@id='printRange']",
    "tables_xpath": "//div[@id='printRange']/table"
  }
}
```

### 3. 日誌配置 (`config/logging_config.json`)

```json
{
    "version": 1,
    "disable_existing_loggers": false,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/crawler.log",
            "maxBytes": 10485760,
            "backupCount": 5
        },
        "slack": {
            "class": "logs.handlers.slack_handler.SlackHandler",
            "level": "ERROR",
            "channel": "#crawler-alerts"
        }
    }
}
```

## 使用示例

### 基本使用

```python
from src.core.template_crawler import TemplateCrawler

# 初始化爬蟲
crawler = TemplateCrawler(
    template_file="templates/gov_procurement.json",
    config_file="config/config.json"
)

# 執行爬蟲
data = crawler.crawl(max_pages=5)

# 輸出結果
print(f"已爬取 {len(data)} 筆資料")
```

### 斷點續爬

```python
from src.core.template_crawler import TemplateCrawler

# 初始化爬蟲
crawler = TemplateCrawler(
    template_file="templates/gov_procurement.json",
    config_file="config/config.json"
)

# 從上次中斷點恢復爬取
data = crawler.resume_crawl()

print(f"已恢復爬取 {len(data)} 筆資料")
```

## 特點與優勢

1. **高度模塊化**：各功能模塊獨立封裝，便於維護和擴展。

2. **強大的反爬蟲能力**：包含多層次的反爬蟲防禦和檢測機制。

3. **全面的驗證碼處理**：支援多種類型的驗證碼，並預留了機器學習整合接口。

4. **可靠的狀態管理**：採用多重備份策略，確保爬蟲狀態的可靠性。

5. **靈活的數據持久化**：支援多種存儲方式，並採用元數據設計提高適應性。

6. **模板化設計**：通過 JSON 模板配置，同一套代碼可適用於不同網站。

7. **詳細的日誌和錯誤處理**：提供詳細的日誌記錄和健壯的錯誤處理機制。

此目錄結構和模塊設計不僅適用於網站的爬取，也可以通過修改模板文件輕鬆擴展到其他網站，是一個功能完備、架構清晰的通用爬蟲系統。
````
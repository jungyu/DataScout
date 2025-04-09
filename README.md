# Crawler-Selenium 爬蟲系統使用指南

這個爬蟲系統使用模板化設計，讓您可以通過簡單的 JSON 配置來爬取不同的網站，而無需修改核心代碼。本指南將介紹如何設置環境、編輯爬蟲 JSON 範本，以及執行和管理爬蟲任務。

## 目錄
- [系統架構](#系統架構)
- [環境配置](#環境配置)
- [配置設定](#配置設定)
- [爬蟲 JSON 範本](#爬蟲-json-範本)
- [執行爬蟲任務](#執行爬蟲任務)
- [管理爬蟲任務](#管理爬蟲任務)
- [斷點續爬功能](#斷點續爬功能)
- [數據持久化](#數據持久化)
- [常見問題處理](#常見問題處理)

## 系統架構

本系統主要由以下幾個部分組成：

1. **核心模組**：應用程式主類、爬蟲引擎、模板化爬蟲核心類和 WebDriver 管理器
2. **資料擷取模組**：基礎擷取器、列表頁擷取器和詳情頁擷取器
3. **導航模組**：頁面導航管理和分頁處理
4. **互動模組**：表單處理、搜尋處理和元素互動
5. **反爬蟲模組**：隱身模式和行為模擬
6. **資料持久化模組**：狀態管理、存儲管理和資料匯出器
7. **工具模組**：文本處理、URL處理、重試機制和資料驗證

## 環境配置

### 1. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 2. 創建並配置憑證文件

創建 `config/credentials.json` 文件，配置 MongoDB 和 Notion 的憑證：

```json
{
  "mongodb": {
    "username": "your_mongodb_username",
    "password": "your_mongodb_password",
    "host": "mongodb.example.com",
    "port": 27017,
    "auth_source": "admin",
    "ssl": true
  },
  "notion": {
    "api_key": "your_notion_api_key",
    "database_id": "your_notion_database_id"
  }
}
```

> **安全提示**: 不要將此文件加入版本控制系統，建議添加到 `.gitignore` 中。更安全的做法是使用環境變數。

### 3. 配置數據持久化

創建 `config/persistence_config.json` 文件：

```json
{
  "local_storage": {
    "enabled": true,
    "base_path": "data",
    "format": "json"
  },
  "mongodb": {
    "enabled": true,
    "database": "web_crawler",
    "collection_prefix": "procurement_",
    "batch_size": 100
  },
  "notion": {
    "enabled": true,
    "field_mappings": {
      "tender_case_no": {
        "field": "案號",
        "type": "title"
      },
      "org_name": {
        "field": "機關名稱",
        "type": "rich_text"
      }
    }
  }
}
```

### 4. 建立目錄結構

確保以下目錄存在：

```
crawler-selenium/
│
├── main.py                      # 爬蟲程式主入口
├── cli.py                       # 命令行介面處理
│
├── config/                      # 配置文件目錄
│   ├── _config.json            # 基礎配置範例
│   ├── _credentials.json       # 憑證配置範例
│   ├── _anti_detection.json    # 反檢測配置範例
│   └── sites/                  # 各網站專用配置
│
├── templates/                   # 爬蟲模板目錄
│   ├── base/                   # 基礎模板
│   └── sites/                  # 網站專用模板
│
├── src/                        # 源代碼目錄
│   ├── core/                   # 核心模塊
│   ├── extractors/             # 資料擷取模組
│   ├── navigation/             # 導航模組
│   ├── interaction/            # 互動模組
│   ├── anti_detection/         # 反爬蟲模組
│   ├── persistence/            # 資料持久化模組
│   └── utils/                  # 工具模組
│
├── examples/                   # 範例程式目錄
├── tests/                      # 測試代碼目錄
└── docs/                       # 文檔目錄
```

## 配置設定

本專案使用 JSON 格式的配置檔案來管理各種設定。在 `/config` 目錄下，您可以找到以下範例配置檔案：

- `_config.json` - 主配置範例
- `_anti_detection_config.json` - 反檢測配置範例
- `_captcha_config.json` - 驗證碼處理配置範例
- `_credentials.json` - 憑證範例
- `_persistence_config.json` - 資料持久化配置範例
- `_field_mappings.json` - 欄位映射配置範例

### 首次設定

1. 複製每個範例配置檔案，移除檔名開頭的底線字符：
   ```bash
   cd config
   for file in _*.json; do
     cp "$file" "${file#_}"
   done
   ```

## 爬蟲 JSON 範本

爬蟲 JSON 範本是系統的核心配置，它定義了如何爬取特定網站。下面詳細介紹各個部分如何配置：

### 1. 基本配置

```json
{
  "site_name": "Google 搜尋",
  "base_url": "https://www.google.com",
  "encoding": "utf-8",
  "description": "Google 搜尋結果爬取模板",
  "version": "1.0.0",
  "browser": {
    "browser_type": "chrome",
    "headless": false,
    "disable_images": false,
    "page_load_timeout": 30,
    "implicit_wait": 10
  }
}
```

### 2. 請求配置

```json
{
  "request": {
    "method": "GET",
    "headers": {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }
  },
  "search": {
    "keyword": "地震 site:news.pts.org.tw",
    "language": "zh-TW"
  }
}
```

### 3. 延遲配置

為了避免過快訪問而被網站識別為機器人，需要配置各階段的延遲時間：

```json
{
  "delays": {
    "page_load": 3,
    "between_pages": 2,
    "between_items": 1,
    "scroll": 1,
    "finish": 3
  }
}
```

### 4. 搜尋頁配置

```json
{
  "search_page": {
    "search_box_xpath": "//textarea[@name='q']",
    "result_container_xpath": "//div[@id='search']"
  }
}
```

### 5. 列表頁配置

列表頁配置定義如何從列表頁提取數據：

```json
{
  "list_page": {
    "container_xpath": "//div[@id='search']",
    "item_xpath": "//div[contains(@class, 'N54PNb')]",
    "fields": {
      "title": {
        "xpath": ".//h3",
        "type": "text"
      },
      "link": {
        "xpath": ".//a[h3]/@href",
        "fallback_xpath": ".//a/@href",
        "type": "attribute"
      },
      "description": {
        "xpath": ".//div[contains(@class, 'VwiC3b')]",
        "type": "text",
        "max_length": 300
      }
    }
  }
}
```

### 6. 詳情頁配置

詳情頁配置定義如何從詳情頁提取數據：

```json
{
  "detail_page": {
    "enabled": true,
    "max_details_per_page": 3,
    "page_load_delay": 3,
    "between_details_delay": 2,
    "check_captcha": true,
    "container_xpath": "//body",
    "fields": {
      "title": {
        "xpath": "//h1",
        "type": "text",
        "fallback_xpath": "//title"
      },
      "content": {
        "xpath": "//article | //div[contains(@class, 'article')] | //div[@role='main']",
        "type": "text",
        "fallback_xpath": "//div[contains(@class, 'content')]"
      },
      "published_date": {
        "xpath": "//time | //span[contains(@class, 'date')] | //meta[@property='article:published_time']/@content",
        "type": "date",
        "fallback_xpath": "//div[contains(@class, 'date')] | //p[contains(@class, 'date')]"
      },
      "category": {
        "xpath": "//div[contains(@class, 'category')] | //a[contains(@href, 'category')]",
        "type": "text",
        "fallback_xpath": "//meta[@property='article:section']/@content"
      },
      "author": {
        "xpath": "//div[contains(@class, 'author')] | //span[contains(@class, 'author')] | //meta[@name='author']/@content",
        "type": "text"
      },
      "tags": {
        "xpath": "//a[contains(@href, 'tag')] | //div[contains(@class, 'tag')]//a",
        "type": "text",
        "multiple": true
      }
    },
    "expand_sections": [
      {
        "name": "閱讀更多",
        "button_selector": "//button[contains(text(), '閱讀更多') or contains(@class, 'more')]",
        "target_selector": "//div[contains(@class, 'expanded')]",
        "wait_time": 1
      }
    ],
    "extract_tables": {
      "xpath": "//table",
      "title_xpath": ".//caption | .//th[1]"
    },
    "extract_images": true,
    "images_container_xpath": "//article | //div[contains(@class, 'article')]"
  }
}
```

### 7. 分頁配置

分頁配置定義如何處理多頁數據：

```json
{
  "pagination": {
    "next_button_xpath": "//a[@id='pnnext']",
    "has_next_page_check": "boolean(//a[@id='pnnext'])",
    "page_number_xpath": "//td[contains(@class,'YyVfkd')]/text()",
    "max_pages": 2
  }
}
```

### 8. 進階設定

```json
{
  "advanced_settings": {
    "detect_captcha": true,
    "captcha_detection_xpath": "//div[contains(@class, 'g-recaptcha')]",
    "save_error_page": true,
    "error_page_dir": "../debug",
    "max_results_per_page": 10,
    "text_cleaning": {
      "remove_extra_whitespace": true,
      "trim_strings": true
    }
  }
}
```

## 執行爬蟲任務

### 基本用法

```bash
python main.py --template templates/sites/gov_procurement.json --config config/config.json
```

### 參數說明

- `--template`: 爬蟲模板文件路徑
- `--config`: 爬蟲配置文件路徑
- `--resume`: 是否恢復上次中斷的任務
- `--max-pages`: 最大爬取頁數
- `--max-items`: 最大處理詳情項目數

### 配置參數

除了在命令行中指定參數外，也可以在配置文件中設置：

```json
{
  "template_path": "templates/sites/gov_procurement.json",
  "headless": true,
  "max_pages": 10,
  "max_items": 200,
  "query_params": {
    "tenderStartDate": "2023/10/01",
    "tenderEndDate": "2023/10/31",
    "orgId": "3.10.3"
  }
}
```

## 管理爬蟲任務

### 查看任務狀態

使用爬蟲任務管理器來查看和管理任務：

```python
from src.persistence.data_manager import DataManager

# 初始化任務管理器
task_manager = DataManager()

# 獲取任務列表
tasks = task_manager.list_tasks(crawler_name="gov_procurement")

# 獲取統計信息
stats = task_manager.get_statistics(crawler_name="gov_procurement", days=30)
```

### 清理舊任務

```python
# 清理 30 天前的任務記錄
task_manager.clean_old_tasks(days=30)
```

## 斷點續爬功能

本系統支援斷點續爬功能，當爬蟲中斷時（無論是手動中斷還是出錯），系統會記錄當前狀態，下次可以從中斷點繼續爬取。

### 恢復中斷任務

```bash
python main.py --resume
```

或者在程式中：

```python
# 獲取可恢復的任務
resumable_task = task_manager.get_resumable_task("gov_procurement")

if resumable_task:
    # 獲取檢查點
    checkpoint = task_manager.get_checkpoint(resumable_task['task_id'])
    
    # 從檢查點恢復爬取
    # ...
```

## 數據持久化

系統支援將數據保存到多個位置：

### 1. 本地文件

爬取的數據默認保存為 JSON 文件，位於 `data` 目錄下。

### 2. MongoDB

如果配置了 MongoDB，數據會自動保存到指定的集合中。

```json
{
  "mongodb": {
    "enabled": true,
    "database": "web_crawler",
    "collection_prefix": "procurement_"
  }
}
```

### 3. Notion

如果配置了 Notion，數據會保存到指定的 Notion 數據庫中。

```json
{
  "notion": {
    "enabled": true,
    "field_mappings": {
      "tender_case_no": {
        "field": "案號",
        "type": "title"
      }
    }
  }
}
```

字段映射定義了爬蟲數據字段如何映射到 Notion 屬性。

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

## 常見問題處理

### 1. 爬蟲被網站阻擋

- 增加延遲時間
- 配置代理伺服器
- 啟用人類行為模擬

### 2. 數據提取錯誤

- 檢查 XPath 是否正確
- 確認網站結構是否變更
- 查看日誌文件獲取詳細錯誤信息

### 3. 資料庫連接失敗

- 確認憑證是否正確
- 檢查網絡連接
- 查看防火牆設置

### 4. 任務管理問題

- 使用 `task_manager.get_task_summary(task_id)` 查看任務詳情
- 檢查 `states` 目錄下的狀態文件
- 如果有需要，可以手動刪除狀態文件重新開始
# 模板化爬蟲系統使用指南

這個爬蟲系統使用模板化設計，讓您可以通過簡單的 JSON 配置來爬取不同的網站，而無需修改核心代碼。本指南將介紹如何設置環境、編輯爬蟲 JSON 範本，以及執行和管理爬蟲任務。

## 目錄
- [系統架構](#系統架構)
- [環境配置](#環境配置)
- [爬蟲 JSON 範本](#爬蟲-json-範本)
- [執行爬蟲任務](#執行爬蟲任務)
- [管理爬蟲任務](#管理爬蟲任務)
- [斷點續爬功能](#斷點續爬功能)
- [數據持久化](#數據持久化)
- [常見問題處理](#常見問題處理)

## 系統架構

本系統主要由以下幾個部分組成：

1. **模板化爬蟲引擎**：核心爬蟲邏輯，使用 Selenium 實現
2. **配置和憑證管理**：安全地載入和管理配置和敏感信息
3. **爬蟲狀態管理**：記錄和管理爬蟲任務的狀態
4. **數據持久化**：將爬取的數據保存到本地、MongoDB 和 Notion

## 環境配置

### 1. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 2. 創建並配置憑證文件

創建 `credentials.json` 文件，配置 MongoDB 和 Notion 的憑證：

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

創建 `persistence_config.json` 文件：

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
/
├── templates/        # 爬蟲模板文件
├── data/             # 爬取的數據
├── logs/             # 日誌文件
├── states/           # 爬蟲狀態文件
└── cookies/          # Cookie 文件
```

## 爬蟲 JSON 範本

爬蟲 JSON 範本是系統的核心配置，它定義了如何爬取特定網站。下面詳細介紹各個部分如何配置：

### 1. 基本配置

```json
{
  "site_name": "政府電子採購網",
  "base_url": "https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic",
  "encoding": "utf-8"
}
```

### 2. 請求配置

```json
{
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
        "orgId": {
          "description": "機關代碼",
          "default": "3.10.3",
          "type": "string"
        },
        "tenderStartDate": {
          "description": "發布日期起始",
          "default": "",
          "type": "date",
          "format": "yyyy/MM/dd"
        }
      },
      "pagination": {
        "page_param": "pageIndex",
        "base_index": 1
      }
    }
  }
}
```

請求配置中：
- `fixed`: 固定不變的參數
- `variable`: 可變參數，可以在運行時指定
- `pagination`: 分頁參數配置

### 3. 延遲配置

為了避免過快訪問而被網站識別為機器人，需要配置各階段的延遲時間：

```json
{
  "delays": {
    "page_load": {"min": 3, "max": 7},
    "between_pages": {"min": 5, "max": 10},
    "between_items": {"min": 2, "max": 5},
    "form_fill": {"min": 0.5, "max": 2},
    "after_click": {"min": 1, "max": 3},
    "scrolling": {"min": 0.3, "max": 1.5}
  }
}
```

### 4. 列表頁配置

列表頁配置定義如何從列表頁提取數據：

```json
{
  "list_page": {
    "container_xpath": "//table[@id='tpam']/tbody",
    "item_xpath": "./tr",
    "fields": {
      "tender_case_no": {"xpath": "./td[3]", "type": "text"},
      "org_name": {"xpath": "./td[2]", "type": "text"},
      "tender_name": {"xpath": "./td[3]/a/span", "type": "text"},
      "detail_link": {"xpath": "./td[3]/a", "type": "attribute", "attribute_name": "href"}
    },
    "wait_for": {"xpath": "//table[@id='tpam']/tbody/tr", "timeout": 15}
  }
}
```

其中：
- `container_xpath`: 列表容器的 XPath
- `item_xpath`: 列表項的 XPath（相對於容器）
- `fields`: 每個字段的提取規則
- `wait_for`: 等待元素出現的配置

### 5. 分頁配置

分頁配置定義如何處理多頁數據：

```json
{
  "pagination": {
    "type": "link_click",
    "next_button_xpath": "//span[@id='pagelinks']/a[contains(text(), '下一頁')]",
    "has_next_page_check": "//span[@id='pagelinks']/a[contains(text(), '下一頁')]",
    "current_page_xpath": "//span[@id='pagelinks']/span[@class='current']",
    "total_pages_xpath": "//span[@id='pagelinks']/a[last()-1]",
    "wait_after_pagination": {"min": 4, "max": 8},
    "alternative": {
      "type": "parameter",
      "param_name": "pageIndex",
      "base_index": 1
    }
  }
}
```

支援兩種分頁方式：
1. `link_click`: 點擊下一頁按鈕
2. `parameter`: 通過更改 URL 參數

### 6. 詳情頁配置

詳情頁配置定義如何從詳情頁提取數據：

```json
{
  "detail_page": {
    "container_xpath": "//div[@id='printRange']",
    "tables_xpath": "//div[@id='printRange']/table",
    "table_caption_xpath": "./caption",
    "table_row_xpath": ".//tr",
    "table_cell_label_xpath": ".//td[1]",
    "table_cell_value_xpath": ".//td[2]",
    "wait_for": {"xpath": "//div[@id='printRange']", "timeout": 20},
    "secondary_wait": {"xpath": "//div[@id='printRange']/table", "timeout": 10},
    "scroll_to_bottom": true,
    "custom_fields": {
      "tender_publication_date": "//td[contains(text(), '公告日期')]/following-sibling::td[1]"
    }
  }
}
```

### 7. 數據轉換配置

定義如何轉換提取到的原始數據：

```json
{
  "data_extraction": {
    "skip_duplicate": true,
    "duplicate_check_field": "tender_case_no",
    "data_transformations": {
      "budget": {
        "type": "number",
        "regex": "(\\d+(?:\\.\\d+)?)",
        "remove_commas": true,
        "default_value": 0
      },
      "announce_date": {
        "type": "date",
        "format": "yyyy/MM/dd",
        "timezone": "Asia/Taipei"
      }
    }
  }
}
```

### 8. 人類行為模擬

為了降低被檢測為機器人的風險，可以配置人類行為模擬：

```json
{
  "human_simulation": {
    "random_scrolling": true,
    "scroll_count": {"min": 1, "max": 3},
    "mouse_movement": false,
    "variable_typing_speed": true
  }
}
```

## 執行爬蟲任務

### 基本用法

```bash
python main.py --template templates/gov_procurement.json --config config.json
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
  "template_path": "templates/gov_procurement.json",
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
from crawler_task_manager import CrawlerTaskManager

# 初始化任務管理器
task_manager = CrawlerTaskManager()

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
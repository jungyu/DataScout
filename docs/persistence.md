# 數據持久化模組說明

本文檔詳細說明了爬蟲系統的數據持久化模組及其功能。

## 目錄

1. [概述](#概述)
2. [存儲配置](#存儲配置)
3. [存儲管理器](#存儲管理器)
4. [存儲處理器](#存儲處理器)
5. [使用示例](#使用示例)
6. [最佳實踐](#最佳實踐)

## 概述

持久化模組負責數據的存儲和管理，提供多種存儲處理器和統一的管理器。該模組依賴於核心模組，並使用 `CoreMixin` 提供的功能。

## 目錄結構

```
persistence/
├── config/         # 配置相關
│   └── storage_config.py
├── handlers/       # 存儲處理器
│   ├── base_handler.py
│   ├── local_handler.py
│   ├── mongodb_handler.py
│   ├── notion_handler.py
│   └── captcha_handler.py
├── manager/        # 管理器
│   └── storage_manager.py
├── utils/          # 工具類
│   ├── core_mixin.py
│   └── storage_utils.py
└── __init__.py
```

## 存儲處理器

### 基礎存儲處理器 (`StorageHandler`)

基礎存儲處理器是所有存儲處理器的基類，提供通用的功能和方法。

#### 主要方法

- `__init__(config)`: 初始化存儲處理器，設置配置和狀態。
- `_update_status(operation, success, error=None)`: 更新操作狀態，記錄成功和失敗次數。
- `save_data(data)`: 保存數據。
- `load_data(query=None)`: 加載數據，可選查詢條件。
- `delete_data(query)`: 刪除數據。
- `clear_data()`: 清空數據。
- `get_data_count(query=None)`: 獲取數據數量。
- `create_backup()`: 創建備份。
- `restore_backup(backup_name)`: 恢復備份。
- `list_backups()`: 列出所有備份。
- `delete_backup(backup_name)`: 刪除備份。

### 本地存儲處理器 (`LocalStorageHandler`)

本地存儲處理器用於將數據存儲在本地文件系統中。

#### 主要方法

- `__init__(config)`: 初始化本地存儲處理器，設置存儲路徑和備份路徑。
- `save_data(data)`: 將數據保存為 JSON 文件。
- `load_data(query=None)`: 從 JSON 文件加載數據。
- `delete_data(query)`: 根據查詢條件刪除數據。
- `clear_data()`: 清空所有數據。
- `get_data_count(query=None)`: 獲取數據數量。
- `create_backup()`: 創建數據備份。
- `restore_backup(backup_name)`: 從備份恢復數據。
- `list_backups()`: 列出所有備份。
- `delete_backup(backup_name)`: 刪除備份。

### MongoDB存儲處理器 (`MongoDBHandler`)

MongoDB存儲處理器用於將數據存儲在 MongoDB 數據庫中。

#### 主要方法

- `__init__(config)`: 初始化 MongoDB 存儲處理器，設置連接參數。
- `_connect()`: 連接到 MongoDB 數據庫。
- `save_data(data)`: 將數據保存到 MongoDB。
- `load_data(query=None)`: 從 MongoDB 加載數據。
- `delete_data(query)`: 根據查詢條件刪除數據。
- `clear_data()`: 清空所有數據。
- `get_data_count(query=None)`: 獲取數據數量。
- `create_backup()`: 創建數據備份。
- `restore_backup(backup_name)`: 從備份恢復數據。
- `list_backups()`: 列出所有備份。
- `delete_backup(backup_name)`: 刪除備份。

### Notion存儲處理器 (`NotionHandler`)

Notion存儲處理器用於將數據存儲在 Notion 數據庫中。

#### 主要方法

- `__init__(config)`: 初始化 Notion 存儲處理器，設置 API 參數。
- `_connect()`: 連接到 Notion API。
- `save_data(data)`: 將數據保存到 Notion。
- `load_data(query=None)`: 從 Notion 加載數據。
- `delete_data(query)`: 根據查詢條件刪除數據。
- `clear_data()`: 清空所有數據。
- `get_data_count(query=None)`: 獲取數據數量。
- `create_backup()`: 創建數據備份。
- `restore_backup(backup_name)`: 從備份恢復數據。
- `list_backups()`: 列出所有備份。
- `delete_backup(backup_name)`: 刪除備份。

### 驗證碼處理器 (`CaptchaHandler`)

驗證碼處理器用於處理和存儲驗證碼相關的數據。

#### 主要方法

- `__init__(config)`: 初始化驗證碼處理器。
- `save_detection_result(result)`: 保存驗證碼檢測結果。
- `save_solution_result(result)`: 保存驗證碼解決結果。
- `get_detection_history()`: 獲取檢測歷史。
- `get_solution_history()`: 獲取解決歷史。
- `clear_history()`: 清空歷史記錄。

## 存儲管理器

### 存儲管理器 (`StorageManager`)

存儲管理器用於統一管理多種存儲處理器，根據配置選擇合適的處理器。

#### 主要方法

- `__init__(config)`: 初始化存儲管理器，設置配置。
- `get_handler()`: 根據配置獲取合適的存儲處理器。
- `save_data(data)`: 保存數據。
- `load_data(query=None)`: 加載數據。
- `delete_data(query)`: 刪除數據。
- `clear_data()`: 清空數據。
- `get_data_count(query=None)`: 獲取數據數量。
- `create_backup()`: 創建備份。
- `restore_backup(backup_name)`: 恢復備份。
- `list_backups()`: 列出所有備份。
- `delete_backup(backup_name)`: 刪除備份。

## 工具類

### 核心功能混入 (`CoreMixin`)

核心功能混入提供通用的功能和方法，供存儲處理器使用。

#### 主要方法

- `_update_status(operation, success, error=None)`: 更新操作狀態。
- `_log_error(error)`: 記錄錯誤信息。

### 存儲工具 (`StorageUtils`)

存儲工具提供數據處理和轉換的功能。

#### 主要方法

- `process_data(data)`: 處理數據。
- `validate_data(data)`: 驗證數據。
- `convert_query(query)`: 轉換查詢條件。

## 存儲配置

存儲配置通過 `StorageConfig` 類進行管理，包含以下主要參數：

```python
{
    "storage_mode": "local",  # 存儲模式：local, mongodb, notion
    "data_dir": "data",  # 數據目錄（本地存儲）
    "default_collection": "crawl_data",  # 默認集合名稱
    "field_mappings": {},  # 字段映射
    "timestamp_field": "timestamp",  # 時間戳字段
    "id_field": "id",  # ID 字段
    "batch_size": 100,  # 批處理大小
    "retry_count": 3,  # 重試次數
    "retry_delay": 1,  # 重試延遲（秒）
    "backup_enabled": true,  # 啟用備份
    "auto_save": true,  # 自動保存
    "auto_save_interval": 300,  # 自動保存間隔（秒）
    "max_backups": 5,  # 最大備份數量
    "encoding": "utf-8",  # 編碼
    "indent": 2,  # 縮進
    
    # 本地存儲配置
    "local_formats": ["json", "pickle", "csv"],  # 本地存儲格式
    "local_indent": 2,  # 本地存儲縮進
    "local_csv_headers": [],  # CSV 表頭
    
    # MongoDB 配置
    "mongodb_host": "localhost",  # MongoDB 主機
    "mongodb_port": 27017,  # MongoDB 端口
    "mongodb_username": null,  # MongoDB 用戶名
    "mongodb_password": null,  # MongoDB 密碼
    "mongodb_database": "crawler_db",  # MongoDB 數據庫
    "mongodb_collection": "crawled_data",  # MongoDB 集合
    "mongodb_auth_source": "admin",  # MongoDB 認證源
    "mongodb_timeout": 5000,  # MongoDB 超時（毫秒）
    "mongodb_max_pool_size": 100,  # MongoDB 最大連接池大小
    
    # Notion 配置
    "notion_token": "",  # Notion API 令牌
    "notion_database_id": "",  # Notion 數據庫 ID
    "notion_page_size": 100  # Notion 頁面大小
}
```

## 使用示例

### 基本用法

```python
from src.persistence.config.storage_config import StorageConfig
from src.persistence.manager.storage_manager import StorageManager

# 創建存儲配置
config = StorageConfig(
    storage_mode="local",
    data_dir="data",
    backup_enabled=True
)

# 創建存儲管理器
with StorageManager(config) as storage:
    # 保存數據
    data = {
        "title": "示例標題",
        "content": "示例內容",
        "url": "https://example.com"
    }
    storage.save_data(data)
    
    # 批量保存數據
    data_list = [
        {"title": "標題1", "content": "內容1"},
        {"title": "標題2", "content": "內容2"}
    ]
    storage.save_batch(data_list)
    
    # 加載數據
    all_data = storage.load_data()
    print(f"總共加載了 {len(all_data)} 條數據")
    
    # 條件查詢
    query = {"title": "標題1"}
    filtered_data = storage.load_data(query)
    print(f"查詢到 {len(filtered_data)} 條匹配數據")
    
    # 創建備份
    storage.create_backup()
    
    # 列出備份
    backups = storage.list_backups()
    print(f"有 {len(backups)} 個備份")
```

### MongoDB 存儲示例

```python
from src.persistence.config.storage_config import StorageConfig
from src.persistence.manager.storage_manager import StorageManager

# 創建 MongoDB 存儲配置
config = StorageConfig(
    storage_mode="mongodb",
    mongodb_host="localhost",
    mongodb_port=27017,
    mongodb_database="crawler_db",
    mongodb_collection="crawled_data"
)

# 創建存儲管理器
with StorageManager(config) as storage:
    # 保存數據
    data = {
        "title": "MongoDB 示例",
        "content": "這是一個 MongoDB 存儲示例",
        "tags": ["mongodb", "example"]
    }
    storage.save_data(data)
    
    # 加載數據
    all_data = storage.load_data()
    print(f"MongoDB 中總共有 {len(all_data)} 條數據")
    
    # 條件查詢
    query = {"tags": "mongodb"}
    filtered_data = storage.load_data(query)
    print(f"查詢到 {len(filtered_data)} 條包含 'mongodb' 標籤的數據")
```

### Notion 存儲示例

```python
from src.persistence.config.storage_config import StorageConfig
from src.persistence.manager.storage_manager import StorageManager

# 創建 Notion 存儲配置
config = StorageConfig(
    storage_mode="notion",
    notion_token="your-notion-token",
    notion_database_id="your-database-id"
)

# 創建存儲管理器
with StorageManager(config) as storage:
    # 保存數據
    data = {
        "title": "Notion 示例",
        "content": "這是一個 Notion 存儲示例",
        "status": "已完成"
    }
    storage.save_data(data)
    
    # 加載數據
    all_data = storage.load_data()
    print(f"Notion 中總共有 {len(all_data)} 條數據")
    
    # 條件查詢
    query = {"status": "已完成"}
    filtered_data = storage.load_data(query)
    print(f"查詢到 {len(filtered_data)} 條狀態為 '已完成' 的數據")
```

## 最佳實踐

1. **選擇合適的存儲模式**：
   - 本地存儲：適合小型項目和快速原型開發
   - MongoDB：適合大型項目和需要複雜查詢的場景
   - Notion：適合需要可視化和協作的場景

2. **配置管理**：
   - 將敏感信息（如數據庫密碼、API 令牌）存儲在環境變數或安全的配置文件中
   - 使用 `StorageConfig.from_credentials()` 方法從 credentials.json 加載配置

3. **資源管理**：
   - 使用上下文管理器（with 語句）確保資源正確釋放
   - 對於大量數據，使用批量保存方法減少 I/O 操作

4. **備份策略**：
   - 定期創建備份
   - 設置合理的最大備份數量
   - 在重要操作前創建備份

5. **數據格式**：
   - 確保數據包含必要的字段（如 ID、時間戳）
   - 使用字段映射處理不同存儲介質的字段差異
   - 對於本地存儲，選擇合適的文件格式（JSON 適合人類閱讀，Pickle 適合複雜對象，CSV 適合表格數據）

6. **錯誤處理**：
   - 檢查操作返回值，確保數據正確保存
   - 實現適當的錯誤處理和重試機制
   - 記錄重要操作的日誌 
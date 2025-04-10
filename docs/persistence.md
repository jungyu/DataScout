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

數據持久化模組提供了將爬取的數據保存到不同存儲介質的功能，支持本地文件存儲、MongoDB 數據庫和 Notion 數據庫等多種存儲方式。該模組設計為可擴展的架構，允許輕鬆添加新的存儲處理器。

主要功能包括：
- 多種存儲介質的支持（本地文件、MongoDB、Notion）
- 統一的數據存取接口
- 自動備份和恢復功能
- 數據格式轉換和映射

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

## 存儲管理器

`StorageManager` 類提供了統一的存儲管理接口，負責創建和管理適當的存儲處理器。主要方法包括：

- `save_data(data)`: 保存單條數據
- `save_batch(data_list)`: 批量保存數據
- `load_data(query)`: 加載數據
- `delete_data(query)`: 刪除數據
- `clear_data()`: 清空數據
- `get_data_count(query)`: 獲取數據數量
- `create_backup()`: 創建備份
- `restore_backup(backup_id)`: 恢復備份
- `list_backups()`: 列出所有備份
- `delete_backup(backup_id)`: 刪除備份

## 存儲處理器

系統提供以下存儲處理器：

### 基礎存儲處理器

`StorageHandler` 是所有存儲處理器的基類，定義了所有存儲處理器必須實現的接口：

- `save_data(data)`: 保存單條數據
- `save_batch(data_list)`: 批量保存數據
- `load_data(query)`: 加載數據
- `delete_data(query)`: 刪除數據
- `clear_data()`: 清空數據
- `get_data_count(query)`: 獲取數據數量
- `create_backup()`: 創建備份
- `restore_backup(backup_id)`: 恢復備份
- `list_backups()`: 列出所有備份
- `delete_backup(backup_id)`: 刪除備份

### 本地存儲處理器

`LocalStorageHandler` 實現了本地文件存儲功能：

- 支持多種文件格式（JSON、Pickle、CSV）
- 內存緩存機制
- 自動備份和恢復
- 數據過濾和查詢

### MongoDB 存儲處理器

`MongoDBHandler` 實現了 MongoDB 數據庫存儲功能：

- 連接池管理
- 批量操作支持
- 查詢過濾
- 備份和恢復

### Notion 存儲處理器

`NotionHandler` 實現了 Notion 數據庫存儲功能：

- 數據類型轉換
- 屬性映射
- 分頁查詢
- 數據過濾

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
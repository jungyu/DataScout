# 存儲文檔

## 概述

本文檔提供系統存儲功能的詳細說明，包括存儲處理器、數據操作和使用示例。

## 目錄

1. [存儲處理器](#存儲處理器)
2. [數據操作](#數據操作)
3. [使用示例](#使用示例)
4. [最佳實踐](#最佳實踐)

## 存儲處理器

存儲處理器負責數據的存儲和檢索，支持多種存儲方式。

### 主要處理器

- **`LocalStorageHandler`**：本地文件存儲處理器。
- **`MongoDBHandler`**：MongoDB 數據庫存儲處理器。
- **`NotionHandler`**：Notion API 存儲處理器。

## 數據操作

系統提供多種數據操作方法，以支持數據的存儲和檢索。

### 主要操作

- **保存數據**：將數據保存到存儲中。
- **批量保存**：批量保存多條數據。
- **載入數據**：從存儲中載入數據。
- **刪除數據**：從存儲中刪除數據。
- **備份數據**：創建數據備份。
- **恢復數據**：從備份中恢復數據。

## 使用示例

### 使用存儲處理器

```python
from src.persistence.handlers.local_handler import LocalStorageHandler
from src.persistence.handlers.mongodb_handler import MongoDBHandler
from src.persistence.handlers.notion_handler import NotionHandler

# 初始化存儲處理器
local_handler = LocalStorageHandler()
mongodb_handler = MongoDBHandler()
notion_handler = NotionHandler()

# 保存數據
local_handler.save_data("data.json", data)
mongodb_handler.save_data("collection", data)
notion_handler.save_data("page_id", data)

# 批量保存數據
local_handler.save_batch("data.json", data_list)
mongodb_handler.save_batch("collection", data_list)
notion_handler.save_batch("page_id", data_list)

# 載入數據
data = local_handler.load_data("data.json")
data = mongodb_handler.load_data("collection", query)
data = notion_handler.load_data("page_id")

# 刪除數據
local_handler.delete_data("data.json")
mongodb_handler.delete_data("collection", query)
notion_handler.delete_data("page_id")

# 備份數據
local_handler.backup_data("data.json", "backup.json")
mongodb_handler.backup_data("collection", "backup_collection")
notion_handler.backup_data("page_id", "backup_page_id")

# 恢復數據
local_handler.restore_data("backup.json", "data.json")
mongodb_handler.restore_data("backup_collection", "collection")
notion_handler.restore_data("backup_page_id", "page_id")
```

## 最佳實踐

1. **選擇合適的存儲處理器**：根據數據的特性和需求，選擇合適的存儲處理器。
2. **數據備份**：定期備份數據，以防止數據丟失。
3. **錯誤處理**：在數據操作過程中，使用錯誤處理器，以捕獲和處理異常。
4. **數據驗證**：在數據存儲和檢索過程中，使用數據驗證工具，確保數據的正確性。
5. **安全管理**：使用安全管理工具，保護敏感數據。 
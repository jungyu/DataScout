# API 模組說明

本文檔詳細說明了爬蟲系統的 API 模組及其功能。

## 目錄

1. [概述](#概述)
2. [API 類型](#api-類型)
3. [認證類型](#認證類型)
4. [API 配置](#api-配置)
5. [API 處理器](#api-處理器)
6. [使用示例](#使用示例)
7. [最佳實踐](#最佳實踐)

## 概述

API 模組提供了與外部服務進行交互的功能，支持多種 API 類型和認證方式。該模組設計為可擴展的架構，允許輕鬆添加新的 API 處理器。

主要功能包括：
- 多種 API 類型的支持（REST、Webhook、自動化平台等）
- 靈活的認證機制
- 錯誤處理和重試機制
- 請求/響應數據結構標準化

## API 類型

系統支持以下 API 類型：

| 類型 | 說明 | 適用場景 |
|------|------|----------|
| REST | 標準 RESTful API | 與大多數 Web 服務交互 |
| WEBHOOK | Webhook 接收和發送 | 事件驅動的數據交換 |
| N8N | n8n 自動化平台 | 工作流程自動化 |
| MAKE | Make (原 Integromat) 平台 | 複雜工作流程自動化 |
| ZAPIER | Zapier 自動化平台 | 應用程序集成 |
| IFTTT | IFTTT 自動化平台 | 簡單自動化任務 |
| CUSTOM | 自定義 API | 特殊需求的 API 交互 |
| AUTOMATION | 自動化任務管理 | 任務調度和執行 |

## 認證類型

系統支持以下認證類型：

| 類型 | 說明 | 配置參數 |
|------|------|----------|
| NONE | 無認證 | 無需額外參數 |
| API_KEY | API 密鑰認證 | `api_key` |
| OAUTH | OAuth 認證 | `client_id`, `client_secret`, `token_url` |
| BASIC | 基本認證 | `username`, `password` |
| JWT | JWT 認證 | `token` |
| CUSTOM | 自定義認證 | 根據需求自定義 |

## API 配置

API 配置通過 `APIConfig` 類進行管理，包含以下主要參數：

```python
{
    "api_type": "rest",  # API 類型
    "base_url": "https://api.example.com",  # 基礎 URL
    "auth_type": "api_key",  # 認證類型
    "api_key": "your-api-key",  # API 密鑰（如果適用）
    "username": "username",  # 用戶名（如果適用）
    "password": "password",  # 密碼（如果適用）
    "headers": {},  # 自定義請求頭
    "timeout": 30,  # 超時時間（秒）
    "retry_count": 3,  # 重試次數
    "retry_delay": 1,  # 重試延遲（秒）
    "user_agent": "Crawler/1.0",  # 用戶代理
    "options": {}  # 其他選項
}
```

## API 處理器

系統提供以下 API 處理器：

### 基礎 API 處理器

`BaseAPIHandler` 是所有 API 處理器的基類，提供了通用的功能：

- 請求準備和發送
- 響應處理
- 錯誤處理
- 重試機制
- HTTP 方法封裝（GET、POST、PUT、DELETE）

### REST API 處理器

`RESTAPIHandler` 用於處理標準的 RESTful API 請求：

- 支持所有 HTTP 方法
- 自動處理 JSON 數據
- 標準的錯誤處理
- 會話管理

### Webhook API 處理器

`WebhookAPIHandler` 用於處理 Webhook 相關的請求：

- 接收 Webhook 事件
- 發送 Webhook 通知
- 事件驗證和處理

### 自動化平台處理器

系統支持多種自動化平台的 API 處理器：

- `N8NAPIHandler`：n8n 平台
- `MakeAPIHandler`：Make (原 Integromat) 平台
- `ZapierAPIHandler`：Zapier 平台
- `IFTTTAPIHandler`：IFTTT 平台

這些處理器提供了任務管理、工作流程執行等功能。

### 自動化 API 處理器

`AutomationAPIHandler` 提供了任務管理和執行的功能：

- 任務創建、更新、刪除
- 任務激活和停用
- 任務執行和監控
- 任務調度管理
- 自定義任務處理器註冊

### 自定義 API 處理器

`CustomAPIHandler` 允許用戶根據特定需求實現自定義的 API 處理邏輯。

## 使用示例

### REST API 示例

```python
from src.api.config import APIConfig, APIType, AuthType
from src.api.handlers import RESTAPIHandler

# 創建 API 配置
config = APIConfig(
    api_type=APIType.REST,
    base_url="https://api.example.com",
    auth_type=AuthType.API_KEY,
    api_key="your-api-key"
)

# 創建 API 處理器
with RESTAPIHandler(config) as api:
    # 發送 GET 請求
    response = api.get("users", params={"page": 1, "limit": 10})
    
    # 發送 POST 請求
    user_data = {"name": "John Doe", "email": "john@example.com"}
    response = api.post("users", data=user_data)
    
    # 處理響應
    if response.status_code == 200:
        users = response.data
        print(f"獲取到 {len(users)} 個用戶")
```

### 自動化 API 示例

```python
from src.api.config import APIConfig, APIType, AuthType
from src.api.handlers import AutomationAPIHandler

# 創建 API 配置
config = APIConfig(
    api_type=APIType.AUTOMATION,
    base_url="https://automation.example.com",
    auth_type=AuthType.API_KEY,
    api_key="your-api-key"
)

# 創建 API 處理器
api = AutomationAPIHandler(config)

# 創建任務
task_data = {
    "name": "數據抓取任務",
    "type": "crawler",
    "schedule": "0 0 * * *",  # 每天執行
    "config": {
        "url": "https://example.com",
        "selectors": {
            "title": "h1",
            "content": "article"
        }
    }
}
task = api.create_task(task_data)

# 激活任務
api.activate_task(task["id"])

# 執行任務
result = api.execute_task(task["id"], {"param": "value"})

# 獲取執行結果
executions = api.get_executions(task["id"])
```

## 最佳實踐

1. **錯誤處理**：始終檢查響應狀態碼和錯誤信息
   ```python
   response = api.get("endpoint")
   if response.error:
       print(f"錯誤: {response.error}")
   ```

2. **資源管理**：使用上下文管理器（with 語句）確保資源正確釋放
   ```python
   with RESTAPIHandler(config) as api:
       # API 操作
   ```

3. **配置管理**：將敏感信息（如 API 密鑰）存儲在環境變數或安全的配置文件中
   ```python
   import os
   config = APIConfig(
       api_type=APIType.REST,
       base_url="https://api.example.com",
       auth_type=AuthType.API_KEY,
       api_key=os.environ.get("API_KEY")
   )
   ```

4. **重試策略**：根據 API 的特性調整重試次數和延遲
   ```python
   config = APIConfig(
       # 其他配置...
       retry_count=5,
       retry_delay=2
   )
   ```

5. **日誌記錄**：使用內置的日誌功能記錄 API 操作
   ```python
   api.logger.info("開始 API 請求")
   response = api.get("endpoint")
   api.logger.info(f"請求完成，狀態碼: {response.status_code}")
   ``` 
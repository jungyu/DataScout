# API 文檔

## 概述

本文檔提供系統 API 的詳細說明，包括接口定義、參數說明和使用示例。

## 目錄

1. [API 概述](#api-概述)
2. [API 接口](#api-接口)
3. [請求和響應格式](#請求和響應格式)
4. [錯誤處理](#錯誤處理)
5. [使用示例](#使用示例)

## API 概述

系統提供 RESTful API，用於與外部系統進行交互。API 支持 JSON 格式的請求和響應。

## API 接口

### 1. 數據存儲接口

#### 1.1 保存數據

- **URL**: `/api/data/save`
- **方法**: `POST`
- **描述**: 保存數據到存儲系統。
- **請求體**:
  ```json
  {
    "data": {
      "title": "示例標題",
      "content": "示例內容",
      "url": "https://example.com"
    }
  }
  ```
- **響應**:
  ```json
  {
    "success": true,
    "message": "數據保存成功"
  }
  ```

#### 1.2 加載數據

- **URL**: `/api/data/load`
- **方法**: `GET`
- **描述**: 從存儲系統加載數據。
- **查詢參數**:
  - `query`: 查詢條件（可選）
- **響應**:
  ```json
  {
    "success": true,
    "data": [
      {
        "title": "示例標題",
        "content": "示例內容",
        "url": "https://example.com"
      }
    ]
  }
  ```

#### 1.3 刪除數據

- **URL**: `/api/data/delete`
- **方法**: `DELETE`
- **描述**: 從存儲系統刪除數據。
- **請求體**:
  ```json
  {
    "query": {
      "title": "示例標題"
    }
  }
  ```
- **響應**:
  ```json
  {
    "success": true,
    "message": "數據刪除成功"
  }
  ```

### 2. 備份接口

#### 2.1 創建備份

- **URL**: `/api/backup/create`
- **方法**: `POST`
- **描述**: 創建數據備份。
- **響應**:
  ```json
  {
    "success": true,
    "message": "備份創建成功",
    "backup_name": "backup_20230101_120000"
  }
  ```

#### 2.2 恢復備份

- **URL**: `/api/backup/restore`
- **方法**: `POST`
- **描述**: 從備份恢復數據。
- **請求體**:
  ```json
  {
    "backup_name": "backup_20230101_120000"
  }
  ```
- **響應**:
  ```json
  {
    "success": true,
    "message": "備份恢復成功"
  }
  ```

#### 2.3 列出備份

- **URL**: `/api/backup/list`
- **方法**: `GET`
- **描述**: 列出所有備份。
- **響應**:
  ```json
  {
    "success": true,
    "backups": [
      "backup_20230101_120000",
      "backup_20230102_120000"
    ]
  }
  ```

#### 2.4 刪除備份

- **URL**: `/api/backup/delete`
- **方法**: `DELETE`
- **描述**: 刪除指定備份。
- **請求體**:
  ```json
  {
    "backup_name": "backup_20230101_120000"
  }
  ```
- **響應**:
  ```json
  {
    "success": true,
    "message": "備份刪除成功"
  }
  ```

## 請求和響應格式

### 請求格式

所有請求應使用 JSON 格式，並設置 `Content-Type` 為 `application/json`。

### 響應格式

所有響應應使用 JSON 格式，包含以下字段：

- `success`: 布爾值，表示操作是否成功。
- `message`: 字符串，提供操作結果的描述。
- `data`: 對象或數組，包含請求的數據（如果適用）。

## 錯誤處理

API 使用標準的 HTTP 狀態碼來表示請求的結果：

- `200 OK`: 請求成功。
- `400 Bad Request`: 請求格式錯誤或參數無效。
- `404 Not Found`: 請求的資源不存在。
- `500 Internal Server Error`: 服務器內部錯誤。

錯誤響應示例：

```json
{
  "success": false,
  "message": "無效的請求參數"
}
```

## 使用示例

### 使用 Python 請求庫

```python
import requests

# 保存數據
response = requests.post(
    'http://localhost:5000/api/data/save',
    json={
        'data': {
            'title': '示例標題',
            'content': '示例內容',
            'url': 'https://example.com'
        }
    }
)
print(response.json())

# 加載數據
response = requests.get('http://localhost:5000/api/data/load')
print(response.json())

# 刪除數據
response = requests.delete(
    'http://localhost:5000/api/data/delete',
    json={
        'query': {
            'title': '示例標題'
        }
    }
)
print(response.json())
```

### 使用 curl 命令行工具

```bash
# 保存數據
curl -X POST http://localhost:5000/api/data/save \
  -H "Content-Type: application/json" \
  -d '{"data": {"title": "示例標題", "content": "示例內容", "url": "https://example.com"}}'

# 加載數據
curl http://localhost:5000/api/data/load

# 刪除數據
curl -X DELETE http://localhost:5000/api/data/delete \
  -H "Content-Type: application/json" \
  -d '{"query": {"title": "示例標題"}}'
``` 
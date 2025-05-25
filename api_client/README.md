# API Client 包

## 專案概述

API Client 包提供了一個統一的 API 調用接口，支持異步操作、錯誤處理、請求限流和緩存等功能。它旨在簡化 API 調用過程，提供更好的可維護性和可擴展性。

## 安裝

```bash
# 開發模式安裝
pip install -e .

# 或直接安裝
pip install api_client
```

## 使用方式

### 基本使用

```python
from api_client import APIClient, APIConfig

# 創建配置
config = APIConfig(
    base_url="https://api.example.com",
    timeout=30,
    max_retries=3
)

# 創建客戶端
client = APIClient(config)

# 發送請求
async def main():
    response = await client.get("/users")
    data = await response.json()
    print(data)

# 運行
import asyncio
asyncio.run(main())
```

### 使用處理器

```python
from api_client import APIClient, APIConfig
from api_client.handlers import RetryHandler, RateLimitHandler

# 創建配置
config = APIConfig(
    base_url="https://api.example.com",
    handlers=[
        RetryHandler(max_retries=3),
        RateLimitHandler(max_requests=100, time_window=60)
    ]
)

# 創建客戶端
client = APIClient(config)
```

## 目錄結構

```
api_client/
├── core/           # 核心組件
├── handlers/       # 請求處理器
└── utils/          # 工具函數
```

## 主要功能

1. 核心功能
   - 統一的 API 調用接口
   - 異步請求支持
   - 配置管理
   - 錯誤處理

2. 請求處理
   - 重試機制
   - 請求限流
   - 響應緩存
   - 日誌記錄

3. 工具支持
   - 請求驗證
   - 響應解析
   - 錯誤轉換
   - 工具函數

## 注意事項

1. 確保在虛擬環境中安裝
2. 檢查依賴版本兼容性
3. 注意異步操作的正確使用
4. 合理配置請求限流和重試策略

## 依賴套件

### 核心依賴
- aiohttp: 異步 HTTP 客戶端
- pydantic: 數據驗證
- loguru: 日誌管理
- typing-extensions: 類型提示擴展

### 開發依賴
- pytest: 測試框架
- black: 代碼格式化
- isort: 導入排序
- mypy: 類型檢查 
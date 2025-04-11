# 系統架構

## 目錄結構

```
src/
├── core/                 # 核心功能模組
│   ├── utils/           # 核心工具類
│   │   ├── config_utils.py
│   │   ├── logger.py
│   │   ├── path_utils.py
│   │   ├── data_processor.py
│   │   ├── error_handler.py
│   │   ├── time_utils.py
│   │   ├── validation_utils.py
│   │   └── security_utils.py
│   └── __init__.py
├── persistence/         # 數據持久化模組
│   ├── config/         # 配置相關
│   │   └── storage_config.py
│   ├── handlers/       # 存儲處理器
│   │   ├── base_handler.py
│   │   ├── local_handler.py
│   │   ├── mongodb_handler.py
│   │   ├── notion_handler.py
│   │   └── captcha_handler.py
│   ├── manager/        # 管理器
│   │   └── storage_manager.py
│   ├── utils/          # 工具類
│   │   ├── core_mixin.py
│   │   └── storage_utils.py
│   └── __init__.py
└── __init__.py

scripts/                 # 腳本目錄
├── setup.py            # 安裝腳本
├── test.py             # 測試腳本
└── utils/              # 腳本工具
    ├── test_utils.py
    └── setup_utils.py

tests/                  # 測試目錄
├── core/              # 核心模組測試
│   └── test_utils.py
├── persistence/       # 持久化模組測試
│   ├── test_handlers.py
│   └── test_manager.py
└── __init__.py
```

## 模組關係

### 核心模組 (core)
- 提供基礎工具類和通用功能
- 所有模組都依賴於核心模組
- 包含配置、日誌、路徑、數據處理等基礎功能

### 持久化模組 (persistence)
- 提供數據存儲和管理功能
- 依賴於核心模組
- 包含多種存儲處理器和統一的管理器

### 腳本模組 (scripts)
- 提供安裝和測試腳本
- 依賴於核心模組和持久化模組
- 用於系統設置和測試執行

### 測試模組 (tests)
- 提供單元測試和集成測試
- 依賴於所有其他模組
- 確保系統功能和穩定性

## 主要類別

### 核心工具類
- `ConfigUtils`: 配置管理
- `Logger`: 日誌記錄
- `PathUtils`: 路徑處理
- `DataProcessor`: 數據處理
- `ErrorHandler`: 錯誤處理
- `TimeUtils`: 時間處理
- `ValidationUtils`: 數據驗證
- `SecurityUtils`: 安全處理

### 存儲處理器
- `StorageHandler`: 基礎存儲處理器
- `LocalStorageHandler`: 本地存儲
- `MongoDBHandler`: MongoDB存儲
- `NotionHandler`: Notion存儲
- `CaptchaHandler`: 驗證碼處理

### 管理器
- `StorageManager`: 存儲管理器

### 工具類
- `CoreMixin`: 核心功能混入
- `StorageUtils`: 存儲工具

## 數據流

1. 應用層調用 `StorageManager`
2. `StorageManager` 根據配置選擇合適的 `StorageHandler`
3. `StorageHandler` 使用 `CoreMixin` 提供的功能
4. 數據通過 `StorageUtils` 進行處理
5. 結果返回給應用層

## 錯誤處理

1. 所有操作都通過 `ErrorHandler` 處理
2. 錯誤信息通過 `Logger` 記錄
3. 錯誤狀態通過 `_update_status` 追蹤
4. 異常通過 try-except 捕獲和處理

## 配置管理

1. 配置通過 `ConfigUtils` 加載
2. 存儲配置通過 `StorageConfig` 管理
3. 敏感信息通過 `SecurityUtils` 加密
4. 配置驗證通過 `ValidationUtils` 執行 
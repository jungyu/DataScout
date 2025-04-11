# 測試文檔

## 概述

測試模組負責提供單元測試和集成測試，確保系統功能和穩定性。該模組依賴於所有其他模組，並使用 `pytest` 進行測試。

## 目錄結構

```
tests/
├── core/              # 核心模組測試
│   └── test_utils.py
├── persistence/       # 持久化模組測試
│   ├── test_handlers.py
│   └── test_manager.py
└── __init__.py
```

## 測試工具

### 測試工具類 (`TestUtils`)

測試工具類提供測試過程中的各種工具方法。

#### 主要方法

- `setup_test_env()`: 設置測試環境。
- `run_tests()`: 執行測試。
- `generate_report()`: 生成測試報告。
- `run_specific_tests(test_paths)`: 執行指定的測試。
- `run_with_markers(markers)`: 執行帶有特定標記的測試。
- `cleanup_test_env()`: 清理測試環境。

## 測試用例

### 核心模組測試

核心模組測試包括對核心工具類的測試，如 `ConfigUtils`、`Logger`、`PathUtils` 等。

#### 主要測試類

- `TestConfigUtils`: 測試配置工具類。
- `TestLogger`: 測試日誌工具類。
- `TestPathUtils`: 測試路徑工具類。
- `TestDataProcessor`: 測試數據處理工具類。
- `TestErrorHandler`: 測試錯誤處理工具類。
- `TestTimeUtils`: 測試時間工具類。
- `TestValidationUtils`: 測試驗證工具類。
- `TestSecurityUtils`: 測試安全工具類。

### 持久化模組測試

持久化模組測試包括對存儲處理器和管理器的測試。

#### 主要測試類

- `TestBaseHandler`: 測試基礎存儲處理器。
- `TestLocalHandler`: 測試本地存儲處理器。
- `TestMongoDBHandler`: 測試 MongoDB 存儲處理器。
- `TestNotionHandler`: 測試 Notion 存儲處理器。
- `TestCaptchaHandler`: 測試驗證碼處理器。
- `TestStorageManager`: 測試存儲管理器。

## 測試執行

使用 `pytest` 執行測試，可以通過以下命令運行所有測試：

```bash
pytest
```

或者運行特定的測試文件：

```bash
pytest tests/core/test_utils.py
```

或者運行帶有特定標記的測試：

```bash
pytest -m "marker_name"
```

## 測試報告

測試報告可以通過以下命令生成：

```bash
pytest --cov=src --cov-report=html
```

這將生成一個 HTML 格式的覆蓋率報告，位於 `reports/coverage` 目錄下。
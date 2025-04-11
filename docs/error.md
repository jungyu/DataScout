# 錯誤文檔

## 概述

本文檔提供系統錯誤處理的詳細說明，包括錯誤工具、錯誤方法和使用示例。

## 目錄

1. [錯誤工具](#錯誤工具)
2. [錯誤方法](#錯誤方法)
3. [使用示例](#使用示例)
4. [最佳實踐](#最佳實踐)

## 錯誤工具

系統提供多種錯誤工具，以支持不同類型的錯誤處理。

### 主要錯誤工具

- **`ErrorHandler`**：錯誤處理工具類，提供錯誤處理功能。

## 錯誤方法

系統提供多種錯誤方法，以支持不同類型的錯誤處理。

### 主要錯誤方法

- **處理錯誤**：處理系統中的錯誤。
- **記錄錯誤**：記錄錯誤信息。
- **拋出錯誤**：拋出自定義錯誤。

## 使用示例

### 使用錯誤工具

```python
from src.persistence.utils.error_handler import ErrorHandler

# 初始化錯誤處理工具
error_handler = ErrorHandler()

# 處理錯誤
error_handler.handle_error("An error occurred")

# 記錄錯誤
error_handler.log_error("Error details")

# 拋出錯誤
error_handler.raise_error("Custom error message")
```

## 最佳實踐

1. **統一錯誤處理**：使用錯誤處理工具統一管理錯誤。
2. **詳細記錄錯誤**：記錄詳細的錯誤信息，以便於調試。
3. **自定義錯誤**：根據需要拋出自定義錯誤，以提高錯誤處理的靈活性。
4. **使用錯誤工具**：在代碼中使用錯誤工具，以統一管理錯誤處理。
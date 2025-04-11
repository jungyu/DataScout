# 驗證碼文檔

## 概述

本文檔提供系統驗證碼處理功能的詳細說明，包括驗證碼檢測、處理和使用示例。

## 目錄

1. [驗證碼處理器](#驗證碼處理器)
2. [驗證碼檢測](#驗證碼檢測)
3. [使用示例](#使用示例)
4. [最佳實踐](#最佳實踐)

## 驗證碼處理器

驗證碼處理器負責檢測和處理網頁中的驗證碼。

### 主要處理器

- **`CaptchaHandler`**：驗證碼處理器，負責檢測和處理驗證碼。

## 驗證碼檢測

系統提供多種驗證碼檢測方法，以支持驗證碼的檢測和處理。

### 主要檢測方法

- **檢測驗證碼**：檢測頁面中是否存在驗證碼。
- **處理驗證碼**：處理檢測到的驗證碼。
- **保存檢測結果**：保存驗證碼檢測結果。
- **獲取檢測歷史**：獲取驗證碼檢測歷史。
- **清除檢測歷史**：清除驗證碼檢測歷史。

## 使用示例

### 使用驗證碼處理器

```python
from src.persistence.handlers.captcha_handler import CaptchaHandler

# 初始化驗證碼處理器
captcha_handler = CaptchaHandler()

# 檢測驗證碼
result = captcha_handler.detect_captcha(driver)

# 處理驗證碼
if result.has_captcha:
    captcha_handler.handle_captcha(driver, result)

# 保存檢測結果
captcha_handler.save_detection_result(result)

# 獲取檢測歷史
history = captcha_handler.get_detection_history()

# 清除檢測歷史
captcha_handler.clear_detection_history()
```

## 最佳實踐

1. **定期檢測驗證碼**：在爬蟲過程中，定期檢測頁面中是否存在驗證碼。
2. **及時處理驗證碼**：一旦檢測到驗證碼，立即進行處理，以避免影響爬蟲效率。
3. **保存檢測結果**：保存驗證碼檢測結果，以便後續分析和處理。
4. **定期清理歷史**：定期清理驗證碼檢測歷史，以節省存儲空間。
5. **錯誤處理**：在驗證碼處理過程中，使用錯誤處理器，以捕獲和處理異常。
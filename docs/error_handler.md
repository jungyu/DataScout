# 錯誤處理模組 (Error Handler)

錯誤處理模組提供一套用於處理常見網頁爬取阻礙的工具，如 403 錯誤、驗證頁面等。

## 主要功能

### 處理 403 Forbidden 錯誤

403 Forbidden 錯誤是常見的網站反爬機制，此功能提供多種嘗試繞過 403 限制的方法：

- 清除 Cookies 後重試
- 修改 User-Agent 重試
- 等待後重試
- 使用 JavaScript fetch API 嘗試繞過

```python
from playwright_base.utils.error_handler import ErrorHandler

# 檢查並嘗試繞過 403 錯誤
if ErrorHandler.handle_403_error(page):
    print("成功處理 403 錯誤!")
```

### 處理按住不放驗證頁面

一些網站（如 Bloomberg）使用特殊的「按住不放」驗證機制，此功能可以自動識別並處理這類驗證：

- 通過文本識別驗證頁面
- 尋找並操作驗證按鈕
- 模擬人類按住滑鼠行為

```python
from playwright_base.utils.error_handler import ErrorHandler

# 檢查並嘗試處理按住驗證頁面
if ErrorHandler.handle_hold_button_verification(page):
    print("成功處理按住驗證頁面!")
```

## 整合使用

這些功能已被整合到 `PlaywrightBase` 類的 `goto_url_with_retry` 方法中，提供自動處理各種錯誤的能力：

```python
from playwright_base import PlaywrightBase

crawler = PlaywrightBase()
# 自動處理訪問過程中出現的各種阻礙
success = crawler.goto_url_with_retry(
    url="https://example.com",
    max_retries=3,
    wait_time=3,
    handle_popups=True,
    handle_errors=True
)
```

## 注意事項

- 這些方法不保證 100% 成功繞過限制，網站的防護機制可能會更新
- 應合理使用，避免對目標網站造成不必要的負擔
- 參考相關法律法規，確保合規爬取

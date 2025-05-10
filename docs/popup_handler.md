# 彈窗處理模組 (Popup Handler)

彈窗處理模組提供一套用於處理網頁爬取過程中常見彈窗的工具，如 Cookie 提示、登入提示、訂閱彈窗等。

## 主要功能

### 檢查並處理彈窗

提供通用的彈窗檢測和處理功能：

```python
from playwright_base.core.popup_handler import check_and_handle_popup

# 檢查並處理頁面上的彈窗
popup_handled = check_and_handle_popup(page)
if popup_handled:
    print("已處理頁面彈窗!")
```

### 通用彈窗處理

更高級的彈窗處理功能，支援自定義選擇器和各類型彈窗：

```python
from playwright_base.core.popup_handler import handle_popups

# 自定義選擇器
custom_selectors = {
    'popup': ['.my-modal', '.custom-popup'],
    'close': ['.my-close-button']
}

# 處理彈窗
popups_handled = handle_popups(
    page,
    auto_close_popups=True,
    custom_selectors=custom_selectors
)
```

## 支援的彈窗類型

模組支援多種常見彈窗類型：

- Cookie 同意彈窗
- 訂閱/註冊提示
- 付費牆
- 歡迎訊息
- 通知許可
- 廣告彈窗

## 整合使用

這些功能已被整合到 `PlaywrightBase` 類的 `goto_url_with_retry` 方法中：

```python
from playwright_base import PlaywrightBase

crawler = PlaywrightBase()
# 自動處理訪問過程中出現的彈窗
success = crawler.goto_url_with_retry(
    url="https://example.com",
    handle_popups=True  # 設置為 False 可禁用彈窗處理
)
```

## 自定義彈窗處理

若遇到特定網站的特殊彈窗，您可以擴展選擇器列表：

```python
from playwright_base.core.popup_handler import handle_popups

# 為特定網站定義自定義選擇器
my_site_selectors = {
    'popup': ['.special-modal', '#unique-popup'],
    'close': ['.site-specific-close'],
    'accept': ['#agree-button-special']
}

# 使用自定義選擇器處理彈窗
handle_popups(page, auto_close_popups=True, custom_selectors=my_site_selectors)
```

## 注意事項

- 自動彈窗處理可能會影響頁面功能，視情況使用
- 避免使用非標準 CSS 選擇器，如 `:contains()` 等 JQuery 選擇器
- 某些網站的彈窗可能需要特殊處理，應根據具體情況擴展本模組

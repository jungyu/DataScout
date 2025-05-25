# Selenium 基礎工具包

一個強大的基於 Selenium 的自動化測試和爬蟲工具包。

## 功能特點

- 瀏覽器自動化
- 反檢測機制
- 認證管理
- 配置管理
- 日誌記錄
- 命令行界面

## 安裝

```bash
pip install selenium_base
```

## 快速開始

### 命令行使用

```bash
# 使用 Chrome 訪問網頁
selenium-base browse https://example.com --browser chrome

# 執行自動化腳本
selenium-base run-script path/to/script.py --browser firefox --headless
```

### 作為包使用

```python
from selenium_base import Browser, BrowserConfig
from selenium_base.utils.logger import setup_logger

# 設置日誌
setup_logger()

# 創建配置
config = BrowserConfig(
    browser_type="chrome",
    headless=True
)

# 創建瀏覽器實例
browser = Browser(config)

# 訪問網頁
await browser.visit("https://example.com")

# 執行自動化操作
await browser.run_script("path/to/script.py")
```

## 開發

### 安裝開發依賴

```bash
pip install -e ".[dev]"
```

### 運行測試

```bash
pytest
```

### 代碼格式化

```bash
black .
isort .
```

## 文檔

詳細文檔請參見 [文檔目錄](docs/)。

## 許可證

MIT License 
# Captcha Manager

一個靈活的驗證碼管理系統，用於網頁自動化。

## 功能特點

- 支持多種驗證碼類型（reCAPTCHA、hCaptcha、圖片驗證碼等）
- 支持 Selenium 和 Playwright
- 可擴展的架構
- 簡單易用的 API

## 安裝

```bash
pip install captcha_manager
```

## 使用方法

### 基本用法

```python
from selenium import webdriver
from captcha_manager import CaptchaManagerFactory, CaptchaConfig

# 創建 WebDriver 實例
driver = webdriver.Chrome()

# 配置驗證碼管理器
config = CaptchaConfig(
    api_key="your_api_key",
    service="2captcha",
    timeout=120,
    retry_count=3
)

# 創建驗證碼管理器實例
manager = CaptchaManagerFactory.create_manager(driver, config)

# 解決 reCAPTCHA
result = manager.solve_recaptcha(
    site_key="your_site_key",
    url="https://example.com"
)
```

### 在專案中使用

在您的專案中，您可以使用相對導入來引用 `captcha_manager` 包：

```python
from ..captcha_manager import CaptchaManagerFactory, CaptchaConfig
```

### 配置選項

```python
config = CaptchaConfig(
    api_key="your_api_key",      # 驗證碼服務的 API 金鑰
    service="2captcha",          # 驗證碼服務提供商
    timeout=120,                 # 超時時間（秒）
    retry_count=3               # 重試次數
)

manager = CaptchaManagerFactory.create_manager(driver, config)
```

## 支持的驗證碼類型

1. reCAPTCHA
2. hCaptcha
3. 圖片驗證碼
4. 滑塊驗證碼
5. 文本驗證碼

## 貢獻

歡迎提交 Pull Request 或創建 Issue。

## 許可證

MIT License 
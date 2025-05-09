# Playwright Base

一個基於 Playwright 的通用網頁爬蟲框架，提供豐富的功能和靈活的擴展性。

## 功能特點

- 瀏覽器實例管理（啟動、關閉）
- 頁面導航與等待
- 元素選擇與操作（點擊、填寫、獲取內容）
- 防檢測機制（隨機延遲、模擬人類操作、UserAgent 管理）
- 代理支持
- 請求攔截與修改
- 例外處理

## 安裝

```bash
pip install playwright-base
```

安裝完成後，需要安裝 Playwright 瀏覽器：

```bash
playwright install
```

## 快速開始

```python
from playwright_base.core import PlaywrightBase

# 初始化爬蟲實例
scraper = PlaywrightBase()

# 訪問網頁
scraper.navigate("https://example.com")

# 等待元素出現並點擊
scraper.click("button.submit")

# 獲取頁面內容
content = scraper.get_text(".content")

# 關閉瀏覽器
scraper.close()
```

## 目錄結構

```
playwright_base/
├── core/           # 核心功能實現
├── config/         # 配置文件
├── anti_detection/ # 反檢測相關功能
├── utils/          # 工具函數
├── services/       # 服務層
├── auth/           # 認證相關
├── captcha/        # 驗證碼處理
└── scripts/        # 腳本文件
```

## 配置

在 `config` 目錄下創建 `.env` 文件：

```env
PROXY_SERVER=http://your-proxy-server:port
USER_AGENT_ROTATION=true
RANDOM_DELAY_MIN=1
RANDOM_DELAY_MAX=3
```

## 進階用法

### 使用代理

```python
scraper = PlaywrightBase(proxy="http://proxy-server:port")
```

### 自定義請求攔截

```python
async def handle_request(route, request):
    if request.resource_type == "image":
        await route.abort()
    else:
        await route.continue_()

scraper.add_request_handler(handle_request)
```

### 防檢測設置

```python
scraper.enable_anti_detection(
    random_delay=True,
    human_like=True,
    rotate_user_agent=True
)
```

## 開發

1. 克隆倉庫
2. 安裝開發依賴：`pip install -e ".[dev]"`
3. 運行測試：`pytest tests/`

## 貢獻

歡迎提交 Pull Request 或創建 Issue。

## 許可證

MIT License 
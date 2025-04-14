# DataScout

DataScout 是一個強大的數據採集和自動化工具，專注於提供穩定、高效且易於使用的數據採集解決方案。

## 功能特點

- **Selenium 自動化基礎**
  - 瀏覽器管理與控制
  - 元素定位與操作
  - 等待機制
  - 事件處理
  - 錯誤處理
  - 日誌記錄
  - 配置管理

- **反檢測功能**
  - 隱身模式
  - 行為模擬
  - 指紋管理
  - 檢測處理
  - 迴避機制
  - 代理管理
  - Cookie 管理
  - User-Agent 管理

- **驗證碼處理**
  - 文字驗證碼
  - 圖片驗證碼
  - 滑塊驗證碼
  - reCAPTCHA
  - hCaptcha
  - 機器學習模型支援

- **認證管理**
  - 登入管理
  - 會話管理
  - Token 管理
  - Cookie 管理

- **API 整合**
  - MQTT 支援
  - IFTTT 整合
  - Make.com 整合
  - n8n 整合
  - Swagger/OpenAPI 支援

- **數據處理**
  - 數據提取
  - 數據轉換
  - 數據驗證
  - 數據存儲

## 目錄結構

```
DataScout/
├── selenium_base/           # Selenium 自動化基礎
│   ├── core/               # 核心功能
│   ├── anti_detection/     # 反檢測功能
│   ├── captcha/           # 驗證碼處理
│   ├── auth/              # 認證管理
│   ├── config/            # 配置管理
│   ├── extractors/        # 數據提取
│   ├── scripts/           # 腳本工具
│   ├── services/          # 服務模組
│   └── utils/             # 工具類
│
├── api_client/            # API 客戶端
│   ├── core/             # 核心功能
│   ├── handlers/         # 處理器
│   └── utils/            # 工具類
│
├── persistence/          # 數據持久化
│   ├── handlers/        # 處理器
│   ├── manager/         # 管理器
│   └── utils/           # 工具類
│
├── tests/               # 測試
│   ├── unit/           # 單元測試
│   ├── integration/    # 整合測試
│   └── performance/    # 性能測試
│
└── docs/               # 文檔
    ├── api/            # API 文檔
    ├── guides/         # 使用指南
    └── examples/       # 示例代碼
```

## 安裝

```bash
# 克隆倉庫
git clone https://github.com/yourusername/datascout.git
cd datascout

# 安裝依賴
pip install -r requirements.txt

# 安裝開發依賴
pip install -r requirements-dev.txt
```

## 使用示例

### Selenium 自動化

```python
from selenium_base.core.browser import BrowserManager
from selenium_base.anti_detection.stealth import StealthManager

# 初始化瀏覽器
browser = BrowserManager()
browser.setup()

# 配置隱身模式
stealth = StealthManager(browser.driver)
stealth.apply_stealth()

# 訪問網頁
browser.get("https://example.com")
```

### API 整合

```python
from api_client.handlers.mqtt_handler import MQTTHandler
from api_client.handlers.ifttt_handler import IFTTTHandler

# MQTT 示例
mqtt = MQTTHandler({
    "broker": "localhost",
    "port": 1883,
    "topic": "test/topic"
})
mqtt.connect()
mqtt.publish("Hello, MQTT!")

# IFTTT 示例
ifttt = IFTTTHandler({
    "webhook_key": "your_key",
    "event_name": "test_event"
})
ifttt.trigger_event(value1="Hello", value2="IFTTT")
```

## 配置

配置文件位於 `selenium_base/config/` 目錄下：

- `default.yaml`: 默認配置
- `example.yaml`: 示例配置
- `schemas/`: 配置模式定義

## 測試

```bash
# 運行所有測試
pytest

# 運行單元測試
pytest tests/unit

# 運行整合測試
pytest tests/integration

# 運行性能測試
pytest tests/performance
```

## 文檔

詳細文檔請參考 `docs/` 目錄：

- API 文檔: `docs/api/`
- 使用指南: `docs/guides/`
- 示例代碼: `docs/examples/`

## 貢獻

歡迎提交 Pull Request 或創建 Issue。

## 許可證

本項目採用 MIT 許可證。詳見 [LICENSE](LICENSE) 文件。
# Playwright Base 框架功能架構

## 總覽
`playwright_base` 是一個基於 Playwright 的網頁爬蟲框架，提供多種功能模組，包括反檢測、瀏覽器操作、配置管理和工具函數等。

---

## 目錄結構

```
playwright_base/
├── README.md          # 框架的總體說明文件
├── __init__.py        # 封裝框架的主要模組
├── anti_detection/    # 反檢測功能模組
├── auth/              # 認證相關模組
├── config/            # 配置管理模組
├── core/              # 核心功能模組
├── examples/          # 使用範例
├── scripts/           # 腳本文件
├── services/          # 服務層模組
├── setup.py           # 安裝配置文件
├── storage/           # 存儲管理模組
└── utils/             # 工具函數模組
```

---

## 各模組詳細說明

### 1. `anti_detection/`
提供反檢測功能，幫助避免網站的反爬蟲機制。

- **`anti_detection_manager.py`**: 管理反檢測的主要邏輯。
- **`audio_spoofer.py`**: 音頻指紋偽裝。
- **`canvas_spoofer.py`**: Canvas 指紋偽裝。
- **`fingerprint.py`**: 指紋管理。
- **`human_like.py`**: 模擬人類行為。
- **`proxy_manager.py`**: 代理管理。
- **`user_agent_manager.py`**: 用戶代理管理。
- **`webgl_spoofer.py`**: WebGL 指紋偽裝。

### 2. `auth/`
處理認證相關功能（目前未提供具體檔案細節）。

### 3. `config/`
管理框架的配置。

- **`settings.py`**: 定義框架的各種配置參數，例如瀏覽器配置、代理配置等。

### 4. `core/`
框架的核心功能模組。

- **`base.py`**: 提供瀏覽器自動化的基礎類 `PlaywrightBase`，包含瀏覽器啟動、關閉、導航等功能。
- **`page_operations.py`**: 定義頁面操作的相關方法，例如獲取頁面內容、執行 JavaScript 腳本等。

### 5. `examples/`
提供框架的使用範例（目前未提供具體檔案細節）。

### 6. `scripts/`
包含腳本文件（目前未提供具體檔案細節）。

### 7. `services/`
服務層模組（目前未提供具體檔案細節）。

### 8. `storage/`
管理存儲相關功能。

- **`storage_manager.py`**: 提供存儲管理功能，例如保存和讀取數據。

### 9. `utils/`
提供工具函數和異常類。

- **`exceptions.py`**: 定義框架的異常類，例如 `PlaywrightBaseException`、`BrowserException` 等。
- **`logger.py`**: 提供日誌設置功能。

---

## 關鍵類與函式

### `PlaywrightBase`
位於 `core/base.py`，是框架的核心類，提供以下功能：
- 瀏覽器啟動與關閉。
- 頁面導航與操作。
- 請求攔截與反檢測設置。

### `setup_logger`
位於 `utils/logger.py`，用於設置日誌記錄器，支持自定義日誌級別和輸出格式。

### 反檢測功能
- **`HumanLikeBehavior`**: 模擬人類行為，例如鼠標移動、鍵盤輸入等。
- **`ProxyManager`**: 管理代理池，支持代理輪換。
- **`UserAgentManager`**: 管理用戶代理，支持用戶代理輪換。

---

## 安裝與使用

請參考 `README.md` 文件以獲取詳細的安裝與使用說明。
# Selenium 爬蟲框架

一個基於 Selenium 的強大爬蟲框架，提供完整的反檢測、驗證碼處理、數據持久化等功能。

## 功能特性

- 🚀 **高性能爬蟲**：基於 Selenium 的穩定爬蟲引擎
- 🛡️ **反檢測機制**：完整的瀏覽器指紋偽裝和人類行為模擬
- 🔒 **安全防護**：內建代理管理和請求限制
- 📝 **驗證碼處理**：支援自動和手動驗證碼處理
- 💾 **數據持久化**：支援多種存儲方式（本地、MongoDB、Notion）
- 🔄 **斷點續爬**：支援任務中斷和恢復
- 📊 **數據處理**：強大的數據提取和處理能力
- 📈 **監控報告**：完整的日誌和監控系統

## 框架架構

```
crawler-selenium/
├── src/                    # 核心框架代碼
│   ├── api/               # API 處理模組
│   │   └── handlers/     # API 處理器
│   ├── core/              # 核心功能模組
│   │   └── utils/        # 工具類
│   ├── persistence/       # 數據持久化模組
│   │   ├── handlers/     # 存儲處理器
│   │   └── utils/        # 存儲工具
│   └── extractors/        # 數據提取器
├── examples/              # 示例代碼
│   ├── prototype/        # 原型示例（不依賴框架）
│   │   ├── google/       # Google 搜尋爬蟲
│   │   └── amazon/       # Amazon 商品爬蟲
│   ├── formal/           # 正式示例（使用框架）
│   │   └── shopee/       # 蝦皮爬蟲示例
│   └── config/           # 示例配置文件
│       ├── prototype/    # 原型示例配置
│       │   ├── google/   # Google 爬蟲配置
│       │   └── amazon/   # Amazon 爬蟲配置
│       └── formal/       # 正式示例配置
│           └── shopee/   # 蝦皮爬蟲配置
├── tests/                 # 測試代碼
├── docs/                  # 文檔
├── config/               # 框架配置文件
└── scripts/              # 腳本
```

### 原型程式

本專案提供了兩種版本的爬蟲程式實作方式：

1. **原型版本** (`/examples/prototype/`)：不依賴框架的獨立爬蟲程式，展示了基本的爬蟲實作方式。
2. **框架版本** (`/examples/formal/`)：使用框架的爬蟲程式，展示了如何利用框架提供的功能。

### 原型程式說明

原型程式位於 `/examples/prototype/` 目錄下，包含以下爬蟲：

- Google 搜尋爬蟲
- UberEats 爬蟲
- 實價登錄爬蟲
- 政府電子採購網爬蟲

詳細說明請參考 [原型程式說明文件](/docs/prototype.md)。

### 框架版本說明

框架版本位於 `/examples/formal/` 目錄下，展示了如何使用框架提供的功能：

- 模組化設計
- 錯誤處理機制
- 配置管理
- 瀏覽器控制
- 資料處理流程

詳細說明請參考 [使用指南](/docs/guide.md)。

## 系統要求

- Python 3.8 或更高版本
- Chrome 瀏覽器
- 足夠的硬碟空間用於數據存儲

## 快速開始

### 1. 安裝

```bash
# 克隆專案
git clone https://github.com/yourusername/crawler-selenium.git
cd crawler-selenium

# 安裝依賴
pip install -r requirements.txt

# 初始化配置
python scripts/setup.py
```

### 2. 配置

複製示例配置文件並根據需要修改：

```bash
# 框架配置
cp config/_crawler.json config/crawler.json
cp config/_storage.json config/storage.json
cp config/_security.json config/security.json

# 示例配置
cp examples/config/prototype/google/config.json examples/config/prototype/google/my_config.json
cp examples/config/formal/shopee/config.json examples/config/formal/shopee/my_config.json
```

### 3. 運行

```bash
# 運行原型示例
python examples/prototype/google/main.py --config examples/config/prototype/google/my_config.json

# 運行正式示例
python examples/formal/shopee/main.py --config examples/config/formal/shopee/my_config.json

# 運行測試
python scripts/test.py
```

## 文檔

詳細文檔位於 `/docs` 目錄：

### 核心文檔
- [架構說明](docs/architecture.md)：系統架構和模組說明
- [使用指南](docs/guide.md)：基本使用方法和示例
- [配置說明](docs/config.md)：配置文件詳細說明
- [API 文檔](docs/api.md)：API 接口說明

### 功能文檔
- [反檢測機制](docs/anti_detection.md)：反爬蟲策略說明
- [驗證碼處理](docs/captcha.md)：驗證碼處理方法
- [數據存儲](docs/storage.md)：數據存儲方案
- [數據提取](docs/extractors.md)：數據提取方法

### 工具文檔
- [工具類說明](docs/utils.md)：通用工具類使用說明
- [模板使用](docs/templates.md)：爬蟲模板使用說明
- [錯誤處理](docs/error.md)：錯誤處理機制
- [日誌系統](docs/logging.md)：日誌配置和使用

### 進階文檔
- [持久化方案](docs/persistence.md)：數據持久化詳細說明
- [安全機制](docs/security.md)：安全相關配置
- [備份恢復](docs/backup.md)：數據備份和恢復
- [測試指南](docs/testing.md)：測試方法和規範

### 其他文檔
- [常見問題](docs/faq.md)：常見問題解答
- [提示詞指南](docs/prompt.md)：AI 提示詞使用指南

## 示例：蝦皮爬蟲

這是一個基於本框架的蝦皮爬蟲示例，提供商品搜尋、產品詳情爬取和購物車操作功能。

### 使用方法

```bash
# 搜尋商品
python -m examples.formal.shopee.main --keyword "手機" --config examples/config/formal/shopee/my_config.json

# 爬取指定產品
python -m examples.formal.shopee.main --product-ids "123456" --config examples/config/formal/shopee/my_config.json
```

更多蝦皮爬蟲的使用說明請參考 [使用指南](docs/guide.md)。

## 貢獻指南

歡迎提交 Issue 和 Pull Request！

## 授權協議

本專案採用 MIT 授權協議，詳見 [LICENSE](LICENSE) 文件。
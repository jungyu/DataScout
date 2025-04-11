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
cp config/_crawler.json config/crawler.json
cp config/_storage.json config/storage.json
cp config/_security.json config/security.json
```

### 3. 運行

```bash
# 運行示例爬蟲
python examples/shopee/main.py

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

## 貢獻指南

歡迎提交 Issue 和 Pull Request！

## 授權協議

本專案採用 MIT 授權協議，詳見 [LICENSE](LICENSE) 文件。
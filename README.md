# Crawler Selenium

基於 Selenium 的網頁爬蟲框架，提供模組化的爬蟲開發環境。

## 功能特點

- 模組化設計
- 配置化管理
- 自動化測試
- 錯誤處理
- 日誌記錄
- 數據備份
- 安全機制

## 快速開始

### 安裝

1. 克隆專案：
```bash
git clone https://github.com/yourusername/crawler-selenium.git
cd crawler-selenium
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

3. 安裝 Chrome 和 ChromeDriver：
```bash
# macOS
brew install --cask google-chrome
brew install chromedriver

# Ubuntu
sudo apt-get install google-chrome-stable
sudo apt-get install chromium-chromedriver
```

### 使用示例

#### 蝦皮爬蟲

```bash
# 搜尋商品
python -m examples.src.shopee.main --keyword "手機"

# 爬取指定產品
python -m examples.src.shopee.main --product-ids "123456"
```

更多使用說明請參考 [使用指南](docs/guide.md)。

## 專案結構

```
crawler-selenium/
├── src/                    # 核心代碼
│   ├── api/               # API 處理
│   ├── core/              # 核心功能
│   ├── persistence/       # 數據持久化
│   └── extractors/        # 數據提取器
├── examples/              # 示例代碼
│   └── src/
│       └── shopee/        # 蝦皮爬蟲示例
├── tests/                 # 測試代碼
├── docs/                  # 文檔
├── config/               # 配置文件
└── scripts/              # 腳本
```

## 文檔

- [架構說明](docs/architecture.md)
- [使用指南](docs/guide.md)
- [配置說明](docs/config.md)
- [錯誤處理](docs/error.md)
- [日誌記錄](docs/logging.md)
- [備份說明](docs/backup.md)
- [安全說明](docs/security.md)

## 開發

### 環境設置

```bash
# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安裝開發依賴
pip install -r requirements-dev.txt
```

### 運行測試

```bash
pytest
```

## 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 文件。
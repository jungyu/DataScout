# Shopee 爬蟲框架

這是一個用於爬取蝦皮購物網站資料的爬蟲框架，提供了豐富的功能和靈活的配置選項。

## 功能特點

- 商品搜尋和詳情爬取
- 自動處理驗證碼
- 瀏覽器指紋偽裝
- 請求頻率控制
- 批次處理功能
- 完整的錯誤處理
- 詳細的日誌記錄

## 安裝

1. 克隆專案：
```bash
git clone https://github.com/yourusername/shopee-crawler.git
cd shopee-crawler
```

2. 安裝依賴：
```bash
make install
```

## 使用方法

### 基本使用

```python
from config import BaseConfig
from crawler import ShopeeCrawler

# 建立配置
config = BaseConfig()

# 建立爬蟲
crawler = ShopeeCrawler(config)

# 搜尋商品
products = crawler.search_products("手機")

# 獲取商品詳情
details = crawler.get_product_details(products[0]["url"])
```

### 進階使用

```python
from config import BaseConfig
from crawler import ShopeeCrawler
from core.browser_fingerprint import BrowserFingerprint
from core.request_controller import RequestController

# 建立配置
config = BaseConfig()

# 自定義瀏覽器指紋
browser_fingerprint = BrowserFingerprint(config)
browser_fingerprint.webgl_params = {...}
browser_fingerprint.canvas_noise = {...}

# 自定義請求控制
request_controller = RequestController(config)
request_controller.user_agents = [...]
request_controller.referers = [...]

# 建立爬蟲
crawler = ShopeeCrawler(config)
crawler.browser_fingerprint = browser_fingerprint
crawler.request_controller = request_controller

# 批次處理商品
products = crawler.search_products("手機")
details = crawler.batch_process_products(products)
```

## 範例

專案提供了兩個使用範例：

1. 基本範例 (`examples/basic_usage.py`)：
   - 展示基本的爬蟲功能
   - 包含搜尋商品和獲取商品詳情
   - 提供完整的日誌記錄

2. 進階範例 (`examples/advanced_usage.py`)：
   - 展示自定義瀏覽器指紋
   - 展示自定義請求控制
   - 實現批次處理商品
   - 提供錯誤處理和重試機制

執行範例：
```bash
# 執行基本範例
make run-example-basic

# 執行進階範例
make run-example-advanced
```

## 開發

### 目錄結構

```
shopee-crawler/
├── config/
│   ├── __init__.py
│   └── base_config.py
├── core/
│   ├── __init__.py
│   ├── base_crawler.py
│   ├── browser_fingerprint.py
│   └── request_controller.py
├── examples/
│   ├── basic_usage.py
│   └── advanced_usage.py
├── tests/
│   ├── __init__.py
│   ├── test_crawler.py
│   ├── test_browser_profile.py
│   ├── test_request_controller.py
│   └── test_browser_fingerprint.py
├── logs/
├── results/
├── Makefile
├── README.md
└── requirements.txt
```

### 開發命令

```bash
# 安裝依賴
make install

# 執行測試
make test

# 檢查程式碼風格
make lint

# 格式化程式碼
make format

# 清理暫存檔案
make clean
```

## 注意事項

1. 請遵守網站的使用條款和爬蟲規則
2. 建議使用代理伺服器避免 IP 被封鎖
3. 適當設定請求頻率避免對伺服器造成負擔
4. 定期更新瀏覽器指紋和請求標頭

## 授權

本專案採用 MIT 授權條款，詳見 [LICENSE](LICENSE) 檔案。 
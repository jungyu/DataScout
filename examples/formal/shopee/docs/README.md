# Shopee 爬蟲模組文檔

## 目錄結構

```
shopee/
├── __init__.py          # 模組初始化
├── browser_profile.py   # 瀏覽器配置
├── request_controller.py # 請求控制
├── browser_fingerprint.py # 瀏覽器指紋
├── crawler.py           # 爬蟲核心
├── main.py             # 主程式
├── config.py           # 配置管理
├── tests/              # 測試目錄
│   ├── __init__.py
│   └── test_crawler.py
└── docs/               # 文檔目錄
    └── README.md
```

## 模組說明

### browser_profile.py
瀏覽器配置模組，負責管理瀏覽器的基本設定，包括：
- 視窗大小
- 語言設定
- 時區設定
- 地理位置模擬
- 代理設定
- 擴充功能管理

### request_controller.py
請求控制模組，負責管理 API 請求的頻率和重試機制，包括：
- 請求頻率限制
- 請求重試策略
- 請求標頭管理
- 請求日誌記錄

### browser_fingerprint.py
瀏覽器指紋模組，負責管理瀏覽器指紋偽裝和環境模擬功能，包括：
- WebGL 參數修改
- Canvas 指紋偽裝
- 音訊指紋偽裝
- 字體列表偽裝
- WebRTC 設定
- 硬體並行數偽裝
- 時區設定
- 語言設定

### crawler.py
爬蟲核心模組，提供商品爬取功能，包括：
- 關鍵字搜尋
- 商品詳情爬取
- 驗證碼處理
- 進階反爬蟲技術

### main.py
主程式模組，提供命令列介面，包括：
- 參數解析
- 配置載入
- 日誌設定
- 錯誤處理

### config.py
配置管理模組，負責管理爬蟲的配置，包括：
- 瀏覽器配置
- 請求配置
- 儲存配置
- 代理配置

## 使用範例

### 基本使用

```python
from shopee.crawler import ShopeeCrawler
from shopee.config import BaseConfig

# 建立配置
config = BaseConfig()

# 建立爬蟲
crawler = ShopeeCrawler(config)

# 搜尋商品
products = crawler.search_products("手機")

# 取得商品詳情
details = crawler.get_product_details("https://shopee.tw/product/123456")
```

### 命令列使用

```bash
# 搜尋商品
python -m shopee.main search "手機" --limit 10

# 取得商品詳情
python -m shopee.main detail "https://shopee.tw/product/123456"
```

## 配置說明

### 瀏覽器配置

```python
browser_config = {
    "headless": False,  # 無頭模式
    "window_size": {"width": 1920, "height": 1080},  # 視窗大小
    "user_agent": "Mozilla/5.0 ...",  # 使用者代理
    "language": "zh-TW",  # 語言
    "timezone": "Asia/Taipei",  # 時區
    "geolocation": {  # 地理位置
        "latitude": 25.0330,
        "longitude": 121.5654
    },
    "proxy": None,  # 代理
    "extensions": []  # 擴充功能
}
```

### 請求配置

```python
request_config = {
    "retry_count": 3,  # 重試次數
    "retry_delay": 1,  # 重試延遲
    "retry_backoff": 2,  # 重試退避
    "retry_statuses": [500, 502, 503, 504],  # 重試狀態碼
    "rate_limit_minute": 60,  # 每分鐘請求限制
    "rate_limit_hour": 1000,  # 每小時請求限制
    "rate_limit_day": 10000  # 每天請求限制
}
```

### 儲存配置

```python
storage_config = {
    "result_dir": "results",  # 結果目錄
    "compress": True  # 壓縮結果
}
```

## 注意事項

1. 請遵守網站的爬蟲政策
2. 適當設定請求頻率限制
3. 使用代理時注意代理的可用性
4. 定期更新瀏覽器指紋
5. 注意驗證碼處理機制 
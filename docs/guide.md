# Selenium 模板化爬蟲框架使用指南

## 簡介

Selenium 模板化爬蟲框架是一套高效、靈活且強大的網頁數據擷取工具，專為需要處理複雜網站結構、動態加載內容和嚴格反爬蟲機制的情境設計。此框架採用模板驅動方式，讓非技術人員也能輕鬆配置和使用網頁爬蟲，無需深入理解程式碼結構。

核心特色包括：
- **模板驅動**：通過 JSON 格式的模板文件定義爬取邏輯，無需修改核心代碼
- **強大的反偵測**：內建多種反爬蟲機制，如隱身模式、代理伺服器、人類行為模擬
- **高度模組化**：所有功能都以模組化方式設計，易於擴展和維護
- **驗證碼處理**：集成多種驗證碼解決方案，包括圖形驗證碼和 reCAPTCHA
- **斷點續爬**：支援從中斷點恢復爬取，確保長時間爬取任務的穩定性
- **多格式輸出**：支援多種數據輸出格式，如 JSON、CSV、Excel 等
- **完善的錯誤處理**：全面的錯誤處理和日誌記錄機制

本框架特別適合具有認證機制、動態內容和複雜表單的網站，讓數據採集工作變得簡單高效。

## 快速入門

### 安裝

```bash
# 克隆專案
git clone https://github.com/aaron-yu/crawler-selenium.git
cd crawler-selenium

# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 基本使用

1. **建立配置文件**

在 `config/config.json` 中設置基本參數：

```json
{
  "webdriver": {
    "browser": "chrome",
    "headless": false
  },
  "logging": {
    "level": "info"
  }
}
```

2. **建立網站模板**

在 `templates/` 目錄下創建網站模板，例如 `example.json`：

```json
{
  "site_name": "範例網站",
  "base_url": "https://example.com",
  "list_page": {
    "url": "https://example.com/items?page={page}",
    "item_selector": ".item"
  },
  "detail_page": {
    "link_selector": ".item-link",
    "data": {
      "title": {
        "selector": ".title",
        "attribute": "text"
      }
    }
  }
}
```

3. **執行爬蟲**

```bash
python main.py -t templates/example.json
```

### 命令行參數

```bash
# 設定最大爬取頁數和項目數
python main.py -t templates/example.json -p 5 -i 100

# 啟用詳細日誌和調試模式
python main.py -t templates/example.json -v -d

# 使用代理和隱身模式
python main.py -t templates/example.json --stealth --proxy http://proxy_ip:port

# 從中斷點恢復爬取
python main.py -t templates/example.json -r

# 指定輸出位置
python main.py -t templates/example.json -o data/results.json
```

## 詳細特性介紹

### 1. 核心模組功能

- **WebDriver 管理器** (`src/core/webdriver_manager.py`)
  - 自動下載和配置 WebDriver
  - 支援 Chrome、Firefox、Edge 等主流瀏覽器
  - 提供彈性的瀏覽器選項配置

- **模板爬蟲引擎** (`src/core/template_crawler.py`)
  - 解析 JSON 模板並轉換成爬蟲指令
  - 處理頁面導航和元素交互
  - 實現數據提取和處理

### 2. 反爬蟲機制

- **WebDriver 隱身模式**
  - 消除 navigator.webdriver 特徵
  - 修改 User-Agent
  - 隱藏自動化特徵

- **代理伺服器**
  - 支援 HTTP、SOCKS 代理
  - 代理伺服器輪替機制
  - 代理有效性檢測

- **人類行為模擬**
  - 隨機等待和延遲
  - 自然鼠標移動軌跡
  - 逼真頁面滾動行為
  - 輸入速度隨機化

### 3. 驗證碼處理

- **圖形驗證碼**
  - 整合 OCR 技術
  - 支援第三方驗證碼識別服務

- **reCAPTCHA 處理**
  - 支援 reCAPTCHA v2/v3
  - 提供音頻驗證碼解決方案

### 4. 數據持久化

- **文件存儲**
  - JSON、CSV、Excel 格式
  - 增量更新
  - 數據清洗和驗證

- **數據庫存儲**
  - 關聯式數據庫 (SQLite、MySQL)
  - NoSQL 解決方案 (MongoDB)

### 5. 狀態管理與錯誤處理

- **斷點恢復**
  - 爬取進度保存
  - 從上次中斷點恢復

- **錯誤處理**
  - 網絡異常重試
  - 元素定位失敗處理
  - 詳細的錯誤日誌

## 配置文件詳解

### 1. 主配置文件 (`config/config.json`)

```json
{
  "webdriver": {
    "browser": "chrome",        // 瀏覽器類型: chrome, firefox, edge
    "headless": false,          // 是否使用無頭模式
    "executable_path": null,    // WebDriver 路徑，null 表示自動下載
    "implicit_wait": 10         // 元素等待時間 (秒)
  },
  
  "anti_detection": {
    "stealth_mode": true,       // 啟用隱身模式
    "user_agent": null,         // 自定義 User-Agent，null 表示使用隨機值
    "proxy": null,              // 代理伺服器，格式: http://ip:port
    "human_like": true,         // 啟用人類行為模擬
    "random_delay": [2, 5]      // 隨機延遲範圍 (秒)
  },
  
  "persistence": {
    "type": "file",             // 存儲類型: file, database
    "format": "json",           // 文件格式: json, csv, excel
    "path": "data/"             // 存儲路徑
  },
  
  "captcha": {
    "service": "2captcha",      // 驗證碼服務: 2captcha, anticaptcha
    "api_key": "YOUR_API_KEY",  // API 密鑰
    "timeout": 120              // 等待超時 (秒)
  },
  
  "logging": {
    "level": "info",            // 日誌級別: debug, info, warning, error
    "file": "logs/crawler.log"  // 日誌文件路徑
  }
}
```

### 2. 爬蟲模板 (`templates/example.json`)

```json
{
  "site_name": "範例網站",            // 網站名稱
  "base_url": "https://example.com", // 網站基礎 URL
  "encoding": "utf-8",               // 網站編碼
  
  "login": {                         // 登入設定 (可選)
    "url": "https://example.com/login",
    "username_selector": "#username",
    "password_selector": "#password",
    "submit_selector": "button[type='submit']",
    "username": "YOUR_USERNAME",      // 可放在 credentials.json
    "password": "YOUR_PASSWORD",      // 可放在 credentials.json
    "success_check": {                // 登入成功檢查
      "selector": ".user-info",
      "attribute": "text",
      "pattern": ".*歡迎.*"
    }
  },
  
  "list_page": {                     // 列表頁設定
    "url": "https://example.com/items?page={page}",
    "item_selector": ".item",        // 項目選擇器
    "next_page_selector": ".pagination .next",
    "max_pages": 10                  // 最大頁數
  },
  
  "detail_page": {                   // 詳情頁設定
    "link_selector": ".item-link",   // 詳情頁連結選擇器
    "data": {                        // 需要擷取的數據
      "title": {
        "selector": ".title",
        "attribute": "text"
      },
      "price": {
        "selector": ".price",
        "attribute": "text",
        "processor": "extract_number" // 數據處理函數
      },
      "image": {
        "selector": ".image img",
        "attribute": "src"
      },
      "description": {
        "selector": ".description",
        "attribute": "text"
      }
    }
  }
}
```

### 3. 憑證配置 (`config/credentials.json`)

```json
{
  "example.com": {
    "username": "your_username",
    "password": "your_password"
  },
  "another-site.com": {
    "username": "another_username",
    "password": "another_password"
  }
}
```

## 進階使用

### 1. 程式碼調用

將爬蟲整合到其他應用程式中：

```python
from src.core.template_crawler import TemplateCrawler

# 初始化爬蟲
crawler = TemplateCrawler(
    template_file="templates/example.json",
    config_file="config/config.json",
    log_level="debug"
)

# 執行爬蟲
data = crawler.crawl(max_pages=5, max_items=100)

# 資料處理
processed_data = [item for item in data if float(item.get("price", 0)) > 100]

# 保存資料
crawler.data_manager.save_data(processed_data, "filtered_results")
```

### 2. 自定義驗證碼處理

```python
from src.captcha.captcha_manager import CaptchaManager

class CustomCaptchaManager(CaptchaManager):
    def solve_captcha(self, element, captcha_type="image"):
        # 自定義驗證碼處理邏輯
        if captcha_type == "image":
            img_src = element.get_attribute("src")
            # 使用自定義OCR處理
            return my_ocr_solution(img_src)
        return None

# 使用自定義驗證碼處理
crawler.set_captcha_manager(CustomCaptchaManager())
```

### 3. 自定義資料處理器

```python
def clean_price(item_data):
    # 清理價格數據
    if "price" in item_data:
        price_text = item_data["price"]
        # 移除貨幣符號和千位分隔符
        price_text = price_text.replace("$", "").replace(",", "")
        item_data["price"] = float(price_text)
    return item_data

def add_timestamp(item_data):
    # 添加處理時間戳
    from datetime import datetime
    item_data["processed_at"] = datetime.now().isoformat()
    return item_data

# 將處理器添加到爬蟲
crawler.add_data_processor(clean_price)
crawler.add_data_processor(add_timestamp)
```

### 4. 多步驟交互操作

處理需要複雜交互的頁面：

```json
{
  "interactions": [
    {
      "name": "選擇下拉選單",
      "selector": "select#category",
      "action": "select",
      "value": "electronics",
      "wait_time": 2
    },
    {
      "name": "點擊篩選按鈕",
      "selector": "button.filter",
      "action": "click",
      "wait_time": 3,
      "wait_for": ".results-container"
    },
    {
      "name": "滾動到頁面底部",
      "action": "scroll_to",
      "position": "bottom",
      "wait_time": 1
    },
    {
      "name": "輸入搜索詞",
      "selector": "input#search",
      "action": "input",
      "value": "智能手機",
      "human_typing": true
    }
  ]
}
```

### 5. 使用代理伺服器輪換

建立代理伺服器池，提高爬蟲的穩定性和隱蔽性：

```json
{
  "anti_detection": {
    "proxy_rotation": true,
    "proxy_list": [
      "http://proxy1:port",
      "http://proxy2:port",
      "http://proxy3:port"
    ],
    "proxy_change_interval": 10
  }
}
```

程式碼實現：

```python
from src.anti_detection.proxy_manager import ProxyManager

# 初始化代理管理器
proxy_manager = ProxyManager(
    proxy_list=["http://proxy1:port", "http://proxy2:port"],
    rotation_interval=10
)

# 設置到爬蟲
crawler.set_proxy_manager(proxy_manager)
```

### 6. 分布式爬取

對於大規模爬取，可以實現分布式處理：

```python
# worker.py
from src.core.template_crawler import TemplateCrawler

def crawl_chunk(template_file, start_page, end_page):
    crawler = TemplateCrawler(template_file=template_file)
    return crawler.crawl(start_page=start_page, end_page=end_page)

# 主控程序
if __name__ == "__main__":
    import concurrent.futures
    
    template_file = "templates/large_site.json"
    total_pages = 100
    workers = 5
    pages_per_worker = total_pages // workers
    
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = []
        for i in range(workers):
            start = i * pages_per_worker + 1
            end = start + pages_per_worker - 1
            futures.append(
                executor.submit(crawl_chunk, template_file, start, end)
            )
        
        for future in concurrent.futures.as_completed(futures):
            results.extend(future.result())
    
    # 合併結果
    print(f"總共爬取了 {len(results)} 條數據")
```
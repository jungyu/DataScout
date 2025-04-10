# Selenium 爬蟲使用指南

## 目錄
- [系統架構](#系統架構)
- [環境配置](#環境配置)
- [配置設定](#配置設定)
- [爬蟲模板](#爬蟲模板)
- [執行爬蟲任務](#執行爬蟲任務)
- [管理爬蟲任務](#管理爬蟲任務)
- [斷點續爬功能](#斷點續爬功能)
- [數據持久化](#數據持久化)
- [常見問題處理](#常見問題處理)

## 系統架構

本系統採用模組化設計，主要由以下幾個部分組成：

### 1. 核心模組
- **TemplateCrawler**：基於模板的爬蟲核心類，提供通用的爬蟲功能
- **WebDriverManager**：瀏覽器實例管理和設定，支援多種瀏覽器
- **ConfigLoader**：配置文件的載入、合併和驗證
- **CrawlerStateManager**：爬蟲狀態管理，支援斷點續爬

### 2. 資料擷取模組
- **DataExtractor**：負責從頁面提取數據
- **ListExtractor**：列表頁數據提取
- **DetailExtractor**：詳情頁數據提取
- **CaptchaHandler**：驗證碼處理

### 3. 導航模組
- **PageNavigator**：頁面導航和 URL 構建
- **PaginationHandler**：分頁處理

### 4. 互動模組
- **FormHandler**：表單處理和搜尋參數處理

### 5. 反爬蟲模組
- **AntiDetection**：防止被網站偵測為爬蟲的設定
- **BrowserFingerprint**：瀏覽器指紋偽裝
- **HumanBehavior**：模擬人類行為

### 6. 資料持久化模組
- **StorageHandler**：數據存儲管理
- **OutputFormatter**：輸出格式處理

### 7. 工具模組
- **TextProcessor**：文本處理
- **URLProcessor**：URL 處理
- **RetryMechanism**：重試機制
- **DataValidator**：數據驗證

## 環境配置

### 1. 安裝依賴套件

```bash
pip install -r requirements.txt
```

主要依賴套件包括：
- selenium：瀏覽器自動化
- requests：HTTP 請求
- lxml：XML/HTML 處理
- beautifulsoup4：HTML 解析
- jsonschema：JSON 驗證
- webdriver-manager：WebDriver 管理
- fake-useragent：隨機用戶代理
- retry：重試機制
- python-dotenv：環境變數管理

### 2. 瀏覽器驅動程式

系統支援多種瀏覽器，包括 Chrome、Firefox 和 Edge。您需要安裝相應的瀏覽器和驅動程式：

#### Chrome
1. 安裝 Chrome 瀏覽器
2. 使用 webdriver-manager 自動下載驅動程式：
   ```python
   from webdriver_manager.chrome import ChromeDriverManager
   from selenium.webdriver.chrome.service import Service
   
   service = Service(ChromeDriverManager().install())
   driver = webdriver.Chrome(service=service)
   ```

#### Firefox
1. 安裝 Firefox 瀏覽器
2. 使用 webdriver-manager 自動下載驅動程式：
   ```python
   from webdriver_manager.firefox import GeckoDriverManager
   from selenium.webdriver.firefox.service import Service
   
   service = Service(GeckoDriverManager().install())
   driver = webdriver.Firefox(service=service)
   ```

#### Edge
1. 安裝 Edge 瀏覽器
2. 使用 webdriver-manager 自動下載驅動程式：
   ```python
   from webdriver_manager.microsoft import EdgeChromiumDriverManager
   from selenium.webdriver.edge.service import Service
   
   service = Service(EdgeChromiumDriverManager().install())
   driver = webdriver.Edge(service=service)
   ```

### 3. 建立目錄結構

確保以下目錄存在：

```
crawler-selenium/
│
├── main.py                      # 爬蟲程式主入口
├── requirements.txt             # 依賴套件列表
├── config/                      # 配置文件目錄
│   ├── credentials.json         # 憑證文件
│   └── persistence_config.json  # 持久化配置
│
├── src/                         # 源代碼目錄
│   ├── core/                    # 核心模組
│   ├── extractors/              # 資料擷取模組
│   ├── anti_detection/          # 反爬蟲模組
│   ├── captcha/                 # 驗證碼處理模組
│   ├── persistence/             # 資料持久化模組
│   └── utils/                   # 工具模組
│
├── examples/                    # 範例目錄
│   ├── src/                     # 範例源代碼
│   ├── config/                  # 範例配置
│   └── data/                    # 範例數據
│
├── docs/                        # 文檔目錄
│   ├── templates.md             # 模板格式說明
│   └── guide.md                 # 使用指南
│
└── data/                        # 數據目錄
    ├── output/                  # 輸出結果
    ├── debug/                   # 調試信息
    └── state/                   # 狀態文件
```

## 配置設定

### 1. 基本配置

基本配置包含網站的基本信息和請求設定：

```json
{
  "site_name": "網站名稱",
  "base_url": "https://example.com",
  "encoding": "utf-8",
  "description": "模板描述",
  "version": "1.0.0",
  "request": {
    "method": "GET",
    "headers": {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }
  }
}
```

### 2. 瀏覽器配置

瀏覽器配置用於設定 WebDriver 的行為：

```json
{
  "browser_type": "chrome",
  "headless": false,
  "disable_images": false,
  "disable_javascript": false,
  "window_size": {
    "width": 1920,
    "height": 1080
  },
  "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
  "proxy": {
    "enabled": false,
    "type": "http",
    "host": "proxy.example.com",
    "port": 8080,
    "username": "username",
    "password": "password"
  }
}
```

### 3. 反爬蟲配置

反爬蟲配置用於防止被網站偵測為爬蟲：

```json
{
  "browser_fingerprint": {
    "user_agent": {
      "enabled": true,
      "rotation": {
        "enabled": true,
        "interval": 300,
        "max_uses": 10
      }
    },
    "webgl": {
      "enabled": true,
      "noise": 0.1
    },
    "canvas": {
      "enabled": true,
      "noise": 0.1
    }
  },
  "human_behavior": {
    "enabled": true,
    "mouse_movement": {
      "enabled": true,
      "speed": "natural",
      "pattern": "random"
    },
    "typing": {
      "enabled": true,
      "speed": "natural",
      "mistakes": true
    },
    "scrolling": {
      "enabled": true,
      "speed": "natural",
      "pattern": "random"
    }
  }
}
```

### 4. 錯誤處理配置

錯誤處理配置用於處理爬取過程中可能出現的錯誤：

```json
{
  "error_types": {
    "network": {
      "retry": true,
      "max_retries": 3,
      "retry_delay": 5,
      "error_codes": [500, 502, 503, 504]
    },
    "timeout": {
      "retry": true,
      "max_retries": 3,
      "retry_delay": 5
    },
    "captcha": {
      "retry": true,
      "max_retries": 3,
      "retry_delay": 5
    },
    "blocked": {
      "retry": true,
      "max_retries": 3,
      "retry_delay": 30,
      "actions": ["rotate_proxy", "rotate_user_agent"]
    }
  },
  "recovery": {
    "save_state": {
      "enabled": true,
      "interval": 10,
      "path": "state/crawler_state.json"
    },
    "resume": {
      "enabled": true,
      "max_attempts": 3
    }
  }
}
```

### 5. 輸出配置

輸出配置用於設定爬取結果的輸出格式和儲存方式：

```json
{
  "formats": {
    "json": {
      "enabled": true,
      "structure": {
        "query": {
          "type": "string",
          "description": "搜尋關鍵字"
        },
        "results": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "title": {
                "type": "string",
                "description": "搜尋結果標題"
              },
              "url": {
                "type": "string",
                "description": "搜尋結果連結"
              },
              "snippet": {
                "type": "string",
                "description": "搜尋結果摘要"
              }
            }
          }
        }
      }
    },
    "csv": {
      "enabled": true,
      "columns": [
        "title",
        "url",
        "snippet"
      ],
      "delimiter": ",",
      "encoding": "utf-8"
    }
  },
  "output_settings": {
    "base_directory": "data/output",
    "file_naming": {
      "pattern": "{query}_{timestamp}",
      "timestamp_format": "%Y%m%d_%H%M%S"
    },
    "compression": {
      "enabled": true,
      "format": "zip"
    }
  }
}
```

## 爬蟲模板

爬蟲模板採用 JSON 格式，用於定義如何爬取特定網站的結構化數據。模板有兩種組織方式：

### 1. 基本配置（Basic）

所有配置集中在單一 JSON 檔案中：

```json
{
  "site_name": "網站名稱",
  "base_url": "https://example.com",
  "encoding": "utf-8",
  "description": "模板描述",
  "version": "1.0.0",
  "request": {},
  "search": {},
  "delays": {},
  "search_page": {},
  "list_page": {},
  "detail_page": {},
  "pagination": {},
  "advanced_settings": {}
}
```

### 2. 正規化配置（Formal）

根據功能將配置分拆到多個 JSON 檔案中：

- `config.json`：基本配置和共用設定
- `detail.json`：詳情頁面設定
- `pagination.json`：分頁設定
- `anti_detection.json`：反偵測設定
- `error_handling.json`：錯誤處理設定
- `output.json`：輸出格式設定
- `rate_limit.json`：速率限制設定
- `captcha.json`：驗證碼處理設定
- `list.json`：列表頁面設定

詳細的模板格式說明請參考 [templates.md](templates.md)。

## 執行爬蟲任務

### 1. 使用範例程式

系統提供了多個範例程式，展示如何使用爬蟲系統：

#### 基本範例

```bash
# 執行 Google 搜尋基本爬蟲
python examples/src/google/basic/search.py
```

#### 正規化範例

```bash
# 執行 Google 搜尋正規化爬蟲
python examples/src/google/formal/search.py
```

### 2. 使用主程式

您也可以使用主程式執行爬蟲任務：

```bash
python main.py -c examples/config/google/basic/search.json -o data/output/google_search.json
```

參數說明：
- `-c, --config`：配置文件路徑
- `-o, --output`：輸出文件路徑
- `-v, --verbose`：顯示詳細日誌
- `-d, --debug`：啟用調試模式

### 3. 自定義爬蟲

您可以繼承 `TemplateCrawler` 類來創建自定義爬蟲：

```python
from src.core.template_crawler import TemplateCrawler
from src.core.webdriver_manager import WebDriverManager
from src.core.config_loader import ConfigLoader

class CustomCrawler(TemplateCrawler):
    def __init__(self, config_path):
        # 設置日誌記錄器
        self.logger = self._setup_logger()
        
        # 載入配置
        self.config_loader = ConfigLoader(logger=self.logger)
        self.config = self.config_loader.load_config(config_path)
        
        # 初始化 WebDriver 管理器
        self.webdriver_manager = WebDriverManager(self.config, logger=self.logger)
        
        # 調用父類初始化
        super().__init__(config_path, self.webdriver_manager, self.logger)
    
    def _setup_logger(self):
        # 設置日誌記錄器
        pass
    
    def setup(self):
        # 設置爬蟲環境
        pass
    
    def run(self):
        # 執行爬蟲任務
        pass
    
    def cleanup(self):
        # 清理資源
        pass

# 使用自定義爬蟲
crawler = CustomCrawler("config/custom_crawler.json")
crawler.setup()
crawler.run()
crawler.cleanup()
```

## 管理爬蟲任務

### 1. 爬蟲狀態管理

系統提供了 `CrawlerStateManager` 類來管理爬蟲狀態：

```python
from src.core.crawler_state_manager import CrawlerStateManager

# 初始化狀態管理器
state_manager = CrawlerStateManager(
    crawler_id="custom_crawler",
    config=config,
    state_dir="data/state",
    log_level=logging.INFO
)

# 保存狀態
state_manager.save_state({
    "current_page": 5,
    "processed_items": 100,
    "last_item_id": "item_123"
})

# 載入狀態
state = state_manager.load_state()
```

### 2. 錯誤處理

系統提供了多種錯誤處理機制：

```python
# 處理網路錯誤
try:
    # 爬蟲操作
except Exception as e:
    # 記錄錯誤
    logger.error(f"爬蟲操作失敗: {str(e)}")
    
    # 保存錯誤頁面
    if config.get("debug", {}).get("save_error_page", False):
        webdriver_manager.take_screenshot(f"data/debug/error_{timestamp}.png")
        with open(f"data/debug/error_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(webdriver_manager.get_page_source())
    
    # 重試
    if config.get("error_types", {}).get("network", {}).get("retry", False):
        max_retries = config.get("error_types", {}).get("network", {}).get("max_retries", 3)
        retry_delay = config.get("error_types", {}).get("network", {}).get("retry_delay", 5)
        
        for i in range(max_retries):
            logger.info(f"重試第 {i+1} 次...")
            time.sleep(retry_delay)
            # 重試爬蟲操作
```

### 3. 驗證碼處理

系統提供了 `CaptchaHandler` 類來處理驗證碼：

```python
from src.captcha import CaptchaHandler

# 初始化驗證碼處理器
captcha_handler = CaptchaHandler(webdriver_manager, logger)

# 檢測驗證碼
if captcha_handler.detect_captcha(["//div[contains(@class, 'g-recaptcha')]"]):
    # 處理驗證碼
    if captcha_handler.handle_captcha("//div[contains(@class, 'g-recaptcha')]"):
        logger.info("驗證碼處理成功")
    else:
        logger.error("驗證碼處理失敗")
```

## 斷點續爬功能

系統提供了斷點續爬功能，可以在爬蟲中斷後從上次的位置繼續爬取：

### 1. 保存爬蟲狀態

```python
# 保存爬蟲狀態
state_manager.save_state({
    "current_page": current_page,
    "processed_items": processed_items,
    "last_item_id": last_item_id,
    "timestamp": datetime.now().isoformat()
})
```

### 2. 載入爬蟲狀態

```python
# 載入爬蟲狀態
state = state_manager.load_state()
if state:
    current_page = state.get("current_page", 1)
    processed_items = state.get("processed_items", 0)
    last_item_id = state.get("last_item_id", None)
    logger.info(f"從第 {current_page} 頁繼續爬取，已處理 {processed_items} 個項目")
else:
    current_page = 1
    processed_items = 0
    last_item_id = None
    logger.info("開始新的爬蟲任務")
```

### 3. 定期保存狀態

```python
# 定期保存狀態
save_interval = config.get("recovery", {}).get("save_state", {}).get("interval", 10)
if processed_items % save_interval == 0:
    state_manager.save_state({
        "current_page": current_page,
        "processed_items": processed_items,
        "last_item_id": last_item_id,
        "timestamp": datetime.now().isoformat()
    })
    logger.info(f"已保存爬蟲狀態，當前頁: {current_page}，已處理項目: {processed_items}")
```

## 數據持久化

系統提供了多種數據持久化方式：

### 1. 本地文件存儲

```python
# 保存為 JSON 文件
def save_results(results, output_path=None):
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join("data/output", f"results_{timestamp}.json")
    
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"數據已保存到: {output_path}")
    return output_path
```

### 2. 資料庫存儲

系統支援 MongoDB 存儲：

```python
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# 連接 MongoDB
client = MongoClient(
    host=config.get("mongodb", {}).get("host", "localhost"),
    port=config.get("mongodb", {}).get("port", 27017),
    username=config.get("mongodb", {}).get("username"),
    password=config.get("mongodb", {}).get("password"),
    authSource=config.get("mongodb", {}).get("auth_source", "admin")
)

# 選擇資料庫和集合
db = client[config.get("mongodb", {}).get("database", "web_crawler")]
collection = db[config.get("mongodb", {}).get("collection_prefix", "") + "results"]

# 插入數據
try:
    result = collection.insert_many(results)
    logger.info(f"已將 {len(result.inserted_ids)} 條數據插入到 MongoDB")
except ConnectionFailure as e:
    logger.error(f"MongoDB 連接失敗: {str(e)}")
```

### 3. 雲端存儲

系統支援 Notion 存儲：

```python
from notion_client import Client

# 初始化 Notion 客戶端
notion = Client(auth=config.get("notion", {}).get("api_key"))

# 插入數據
database_id = config.get("notion", {}).get("database_id")
field_mappings = config.get("notion", {}).get("field_mappings", {})

for item in results:
    properties = {}
    for field, mapping in field_mappings.items():
        if field in item:
            properties[mapping["field"]] = {
                mapping["type"]: item[field]
            }
    
    try:
        notion.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        logger.info(f"已將數據插入到 Notion")
    except Exception as e:
        logger.error(f"Notion 插入失敗: {str(e)}")
```

## 常見問題處理

### 1. 瀏覽器驅動程式問題

**問題**：無法找到瀏覽器驅動程式。

**解決方案**：
- 使用 webdriver-manager 自動下載驅動程式：
  ```python
  from webdriver_manager.chrome import ChromeDriverManager
  from selenium.webdriver.chrome.service import Service
  
  service = Service(ChromeDriverManager().install())
  driver = webdriver.Chrome(service=service)
  ```
- 手動下載驅動程式並指定路徑：
  ```python
  from selenium.webdriver.chrome.service import Service
  
  service = Service("/path/to/chromedriver")
  driver = webdriver.Chrome(service=service)
  ```

### 2. 元素定位問題

**問題**：無法找到頁面元素。

**解決方案**：
- 使用多種定位方式：
  ```python
  # 使用 XPath
  element = driver.find_element(By.XPATH, "//div[@id='search']")
  
  # 使用 CSS 選擇器
  element = driver.find_element(By.CSS_SELECTOR, "#search")
  
  # 使用 ID
  element = driver.find_element(By.ID, "search")
  ```
- 等待元素出現：
  ```python
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.support import expected_conditions as EC
  
  wait = WebDriverWait(driver, 10)
  element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='search']")))
  ```

### 3. 驗證碼問題

**問題**：遇到驗證碼無法繼續爬取。

**解決方案**：
- 使用驗證碼處理器：
  ```python
  from src.captcha import CaptchaHandler
  
  captcha_handler = CaptchaHandler(webdriver_manager, logger)
  if captcha_handler.detect_captcha(["//div[contains(@class, 'g-recaptcha')]"]):
      captcha_handler.handle_captcha("//div[contains(@class, 'g-recaptcha')]")
  ```
- 增加延遲時間：
  ```python
  # 增加頁面載入延遲
  delays = config.get("delays", {})
  page_load_delay = delays.get("page_load", 3)
  time.sleep(page_load_delay)
  ```

### 4. 反爬蟲問題

**問題**：被網站偵測為爬蟲。

**解決方案**：
- 使用反爬蟲設定：
  ```python
  # 啟用反爬蟲設定
  anti_detection = config.get("anti_detection", {})
  if anti_detection.get("enabled", False):
      # 應用反爬蟲設定
      webdriver_manager._apply_stealth_techniques()
  ```
- 使用代理伺服器：
  ```python
  # 使用代理伺服器
  proxy = config.get("proxy", {})
  if proxy.get("enabled", False):
      chrome_options.add_argument(f"--proxy-server={proxy.get('type', 'http')}://{proxy.get('host')}:{proxy.get('port')}")
  ```
- 模擬人類行為：
  ```python
  # 模擬人類行為
  human_behavior = config.get("human_behavior", {})
  if human_behavior.get("enabled", False):
      # 模擬滑鼠移動
      if human_behavior.get("mouse_movement", {}).get("enabled", False):
          webdriver_manager.simulate_mouse_movement()
      
      # 模擬滾動
      if human_behavior.get("scrolling", {}).get("enabled", False):
          webdriver_manager.scroll_page()
  ```

### 5. 斷點續爬問題

**問題**：爬蟲中斷後無法從上次的位置繼續爬取。

**解決方案**：
- 使用狀態管理器：
  ```python
  from src.core.crawler_state_manager import CrawlerStateManager
  
  state_manager = CrawlerStateManager(
      crawler_id="custom_crawler",
      config=config,
      state_dir="data/state",
      log_level=logging.INFO
  )
  
  # 保存狀態
  state_manager.save_state({
      "current_page": current_page,
      "processed_items": processed_items,
      "last_item_id": last_item_id
  })
  
  # 載入狀態
  state = state_manager.load_state()
  if state:
      current_page = state.get("current_page", 1)
      processed_items = state.get("processed_items", 0)
      last_item_id = state.get("last_item_id", None)
  ```
- 定期保存狀態：
  ```python
  # 定期保存狀態
  save_interval = config.get("recovery", {}).get("save_state", {}).get("interval", 10)
  if processed_items % save_interval == 0:
      state_manager.save_state({
          "current_page": current_page,
          "processed_items": processed_items,
          "last_item_id": last_item_id
      })
  ```

### 6. 數據持久化問題

**問題**：無法將爬取的數據保存到本地或資料庫。

**解決方案**：
- 使用本地文件存儲：
  ```python
  # 保存為 JSON 文件
  def save_results(results, output_path=None):
      if not output_path:
          timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
          output_path = os.path.join("data/output", f"results_{timestamp}.json")
      
      output_dir = os.path.dirname(output_path)
      if output_dir and not os.path.exists(output_dir):
          os.makedirs(output_dir, exist_ok=True)
      
      with open(output_path, 'w', encoding='utf-8') as f:
          json.dump(results, f, ensure_ascii=False, indent=2)
  ```
- 使用資料庫存儲：
  ```python
  # 使用 MongoDB 存儲
  from pymongo import MongoClient
  
  client = MongoClient(
      host=config.get("mongodb", {}).get("host", "localhost"),
      port=config.get("mongodb", {}).get("port", 27017),
      username=config.get("mongodb", {}).get("username"),
      password=config.get("mongodb", {}).get("password"),
      authSource=config.get("mongodb", {}).get("auth_source", "admin")
  )
  
  db = client[config.get("mongodb", {}).get("database", "web_crawler")]
  collection = db[config.get("mongodb", {}).get("collection_prefix", "") + "results"]
  
  collection.insert_many(results)
  ```
# Selenium 爬蟲使用指南

## 目錄
- [系統概述](#系統概述)
- [環境配置](#環境配置)
- [執行範例程式](#執行範例程式)
  - [基本範例 (Basic)](#基本範例-basic)
  - [正規化範例 (Formal)](#正規化範例-formal)
- [自定義爬蟲](#自定義爬蟲)
- [常見問題處理](#常見問題處理)

## 系統概述

本系統提供兩種爬蟲實現方式：

1. **基本範例 (Basic)**：獨立執行的爬蟲程式，不依賴核心模組，適合簡單的爬蟲任務。
2. **正規化範例 (Formal)**：依賴核心模組的爬蟲程式，提供更多功能和更好的可維護性，適合複雜的爬蟲任務。

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

## 執行範例程式

系統提供了多個範例程式，展示如何使用爬蟲系統。這些範例分為兩種類型：基本範例 (Basic) 和正規化範例 (Formal)。

### 基本範例 (Basic)

基本範例是獨立執行的爬蟲程式，不依賴核心模組，適合簡單的爬蟲任務。

#### Google 搜尋爬蟲

```bash
# 執行 Google 搜尋基本爬蟲
python examples/src/google/basic/search.py
```

這個範例會使用 `examples/config/google/basic/search.json` 配置文件，爬取 Google 搜尋結果。

#### Google 搜尋點數爬蟲

```bash
# 執行 Google 搜尋點數基本爬蟲
python examples/src/google/basic/search_pts.py
```

這個範例會使用 `examples/config/google/basic/search_pts.json` 配置文件，爬取 Google 搜尋結果並計算點數。

#### 公視新聞爬蟲

```bash
# 執行公視新聞基本爬蟲
python examples/src/pts/basic/news.py
```

這個範例會使用 `examples/config/pts/basic/news.json` 配置文件，爬取公視新聞網站的內容。

#### 公視新聞列表爬蟲

```bash
# 執行公視新聞列表基本爬蟲
python examples/src/pts/basic/news_list.py
```

這個範例會使用 `examples/config/pts/basic/news_list.json` 配置文件，爬取公視新聞網站的列表頁面。

#### 公視新聞詳情爬蟲

```bash
# 執行公視新聞詳情基本爬蟲
python examples/src/pts/basic/news_detail.py
```

這個範例會使用 `examples/config/pts/basic/news_detail.json` 配置文件，爬取公視新聞網站的詳情頁面。

### 正規化範例 (Formal)

正規化範例是依賴核心模組的爬蟲程式，提供更多功能和更好的可維護性，適合複雜的爬蟲任務。

#### Google 搜尋爬蟲

```bash
# 執行 Google 搜尋正規化爬蟲
python examples/src/google/formal/search.py
```

這個範例會使用 `examples/config/google/formal/search/` 目錄下的配置文件，爬取 Google 搜尋結果。

#### 公視新聞爬蟲

```bash
# 執行公視新聞正規化爬蟲
python examples/src/pts/formal/news.py
```

這個範例會使用 `examples/config/pts/formal/news/` 目錄下的配置文件，爬取公視新聞網站的內容。

#### 公視新聞列表爬蟲

```bash
# 執行公視新聞列表正規化爬蟲
python examples/src/pts/formal/news_list.py
```

這個範例會使用 `examples/config/pts/formal/news_list/` 目錄下的配置文件，爬取公視新聞網站的列表頁面。

#### 公視新聞詳情爬蟲

```bash
# 執行公視新聞詳情正規化爬蟲
python examples/src/pts/formal/news_detail.py
```

這個範例會使用 `examples/config/pts/formal/news_detail/` 目錄下的配置文件，爬取公視新聞網站的詳情頁面。

## 自定義爬蟲

您可以根據自己的需求，創建自定義的爬蟲程式。以下是兩種方式：

### 1. 基本爬蟲 (Basic)

基本爬蟲是獨立執行的爬蟲程式，不依賴核心模組，適合簡單的爬蟲任務。

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import os

def setup_driver():
    """設置 WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def search_google(driver, query):
    """搜尋 Google"""
    driver.get("https://www.google.com")
    
    # 等待搜尋框出現
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    
    # 輸入搜尋關鍵字
    search_box.send_keys(query)
    search_box.submit()
    
    # 等待搜尋結果出現
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "search"))
    )
    
    # 提取搜尋結果
    results = []
    search_results = driver.find_elements(By.CSS_SELECTOR, "div.g")
    
    for result in search_results:
        try:
            title_element = result.find_element(By.CSS_SELECTOR, "h3")
            link_element = result.find_element(By.CSS_SELECTOR, "a")
            snippet_element = result.find_element(By.CSS_SELECTOR, "div.VwiC3b")
            
            title = title_element.text
            link = link_element.get_attribute("href")
            snippet = snippet_element.text
            
            results.append({
                "title": title,
                "url": link,
                "snippet": snippet
            })
        except Exception as e:
            print(f"提取搜尋結果時出錯: {str(e)}")
    
    return results

def save_results(results, output_path=None):
    """保存搜尋結果"""
    if not output_path:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join("data/output", f"google_search_{timestamp}.json")
    
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"搜尋結果已保存到: {output_path}")
    return output_path

def main():
    """主函數"""
    # 設置 WebDriver
    driver = setup_driver()
    
    try:
        # 搜尋 Google
        query = "Python Selenium 爬蟲"
        results = search_google(driver, query)
        
        # 保存搜尋結果
        save_results(results)
    finally:
        # 關閉 WebDriver
        driver.quit()

if __name__ == "__main__":
    main()
```

### 2. 正規化爬蟲 (Formal)

正規化爬蟲是依賴核心模組的爬蟲程式，提供更多功能和更好的可維護性，適合複雜的爬蟲任務。

```python
import sys
import os
import json
import logging
from datetime import datetime

# 添加 src 目錄到 Python 路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.core.template_crawler import TemplateCrawler
from src.core.webdriver_manager import WebDriverManager
from src.core.config_loader import ConfigLoader

# 設置日誌記錄器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

class GoogleSearchCrawler(TemplateCrawler):
    """Google 搜尋爬蟲"""
    
    def __init__(self, config_path):
        """初始化爬蟲"""
        # 設置日誌記錄器
        self.logger = logger
        
        # 載入配置
        self.config_loader = ConfigLoader(logger=self.logger)
        self.config = self.config_loader.load_config(config_path)
        
        # 初始化 WebDriver 管理器
        self.webdriver_manager = WebDriverManager(self.config, logger=self.logger)
        
        # 調用父類初始化
        super().__init__(config_path, self.webdriver_manager, self.logger)
    
    def setup(self):
        """設置爬蟲環境"""
        self.logger.info("設置爬蟲環境")
        self.webdriver_manager.setup()
    
    def run(self):
        """執行爬蟲任務"""
        self.logger.info("執行爬蟲任務")
        
        # 獲取搜尋關鍵字
        query = self.config.get("search", {}).get("query", "Python Selenium 爬蟲")
        self.logger.info(f"搜尋關鍵字: {query}")
        
        # 搜尋 Google
        results = self.search_google(query)
        
        # 保存搜尋結果
        output_path = self.save_results(results)
        
        self.logger.info(f"爬蟲任務完成，結果已保存到: {output_path}")
        return output_path
    
    def search_google(self, query):
        """搜尋 Google"""
        self.logger.info(f"搜尋 Google: {query}")
        
        # 構建搜尋 URL
        search_url = f"https://www.google.com/search?q={query}"
        self.logger.info(f"搜尋 URL: {search_url}")
        
        # 訪問搜尋頁面
        self.webdriver_manager.driver.get(search_url)
        
        # 等待搜尋結果出現
        self.webdriver_manager.wait_for_element(By.ID, "search")
        
        # 提取搜尋結果
        results = []
        search_results = self.webdriver_manager.driver.find_elements(By.CSS_SELECTOR, "div.g")
        
        for result in search_results:
            try:
                title_element = result.find_element(By.CSS_SELECTOR, "h3")
                link_element = result.find_element(By.CSS_SELECTOR, "a")
                snippet_element = result.find_element(By.CSS_SELECTOR, "div.VwiC3b")
                
                title = title_element.text
                link = link_element.get_attribute("href")
                snippet = snippet_element.text
                
                results.append({
                    "title": title,
                    "url": link,
                    "snippet": snippet
                })
            except Exception as e:
                self.logger.error(f"提取搜尋結果時出錯: {str(e)}")
        
        self.logger.info(f"提取到 {len(results)} 條搜尋結果")
        return results
    
    def save_results(self, results):
        """保存搜尋結果"""
        self.logger.info("保存搜尋結果")
        
        # 獲取輸出路徑
        output_path = self.config.get("output", {}).get("path")
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join("data/output", f"google_search_{timestamp}.json")
        
        # 確保輸出目錄存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 保存搜尋結果
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"搜尋結果已保存到: {output_path}")
        return output_path
    
    def cleanup(self):
        """清理資源"""
        self.logger.info("清理資源")
        self.webdriver_manager.cleanup()

def main():
    """主函數"""
    # 配置文件路徑
    config_path = "examples/config/google/formal/search/config.json"
    
    # 創建爬蟲實例
    crawler = GoogleSearchCrawler(config_path)
    
    try:
        # 設置爬蟲環境
        crawler.setup()
        
        # 執行爬蟲任務
        output_path = crawler.run()
        
        print(f"爬蟲任務完成，結果已保存到: {output_path}")
    finally:
        # 清理資源
        crawler.cleanup()

if __name__ == "__main__":
    main()
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
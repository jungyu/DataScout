# Nikkei Asia 爬蟲程式實作說明

本文檔詳細說明如何使用 VS Code 的 GitHub Copilot 與 PlaywrightBase 框架建立一個高級的 Nikkei Asia 新聞爬蟲。此爬蟲能夠模擬真實人類行為，自動登入、搜尋關鍵詞、爬取新聞列表與文章內容，同時具備出色的反爬蟲能力與狀態管理。

## 目錄結構

```
nikkei/
├── config/                      # 配置文件目錄
│   ├── credentials.ini          # 登入帳號密碼
│   ├── keywords.json            # 搜尋關鍵詞列表
│   └── nikkei_config.json       # 爬蟲配置
├── logs/                        # 日誌文件目錄
├── storage/                     # 存儲目錄
│   ├── nikkei_articles.json     # 爬取的文章內容
│   ├── nikkei_lists.json        # 爬取的文章列表
│   ├── nikkei_results.json      # 爬取進度記錄
│   ├── nikkei_storage.json      # 瀏覽器 Cookie 與狀態
│   └── screenshots/             # 網頁截圖目錄
└── nikkei.py                    # 主程式
```

## 1. 如何使用 VS Code GitHub Copilot 的 agent 模式創建爬蟲程式

### 初始化提示詞 (Initial Prompt)

使用 VS Code 的 GitHub Copilot 聊天功能，輸入以下初始提示詞啟動 agent 模式：

```
我需要使用 PlaywrightBase 框架開發一個 Nikkei Asia 新聞爬蟲。
請幫我設計一個完整的結構，包含以下功能：
1. 自動登入 Nikkei Asia 網站
2. 從配置文件中讀取關鍵詞進行搜尋
3. 爬取搜尋結果列表並保存
4. 爬取文章詳情頁面內容
5. 實現中斷後的續爬功能
6. 添加防爬蟲檢測能力
```

### 漸進式開發步驟

1. **請 Copilot 設計基本結構**：
   ```
   請設計 nikkei.py 的基本類和函數結構
   ```

2. **定義配置文件結構**：
   ```
   幫我定義 nikkei_config.json、keywords.json 和 credentials.ini 的結構
   ```

3. **逐步實現功能**：
   ```
   現在請實現 NikkeiScraper 類的初始化和登入功能
   ```

4. **改進與優化**：
   ```
   請添加異常處理和人類行為模擬功能，確保爬蟲不易被檢測
   ```

## 2. 描述 Prompt 編寫爬蟲具體功能

### 自動登入模組

為了實現自動登入功能，使用以下提示詞：

```
請幫我實現 Nikkei Asia 網站的自動登入功能。需要處理:
1. 訪問網站首頁
2. 點擊登入按鈕
3. 在登入框中填寫郵箱和密碼
4. 保存登入狀態到 storage 文件
```

關鍵實現：

```python
def login(self) -> None:
    """登入 Nikkei 網站"""
    logger.info("自動登入 Nikkei 帳號...")
    
    # 訪問首頁
    self.crawler.goto(self.base_url, wait_until="domcontentloaded")
    
    # 點擊登入按鈕
    self.crawler.page.wait_for_selector('button[data-trackable="login-link"]', timeout=20000)
    self.crawler.page.click('button[data-trackable="login-link"]')
    
    # 隨機延遲模擬真實用戶
    self.human_like.random_delay(1.0, 2.0)
    
    # 切換到登入 iframe
    self.crawler.page.wait_for_selector('iframe[src*="auth.asia.nikkei.com/id/"]', timeout=20000)
    iframe_elem = self.crawler.page.query_selector('iframe[src*="auth.asia.nikkei.com/id/"]')
    login_frame = iframe_elem.content_frame()
    
    # 輸入郵箱和密碼
    login_frame.wait_for_selector('input#email-field', timeout=20000)
    login_frame.fill('input#email-field', self.email)
    login_frame.click('button[type="submit"].btn.prime')
    
    self.human_like.random_delay(1.0, 2.0)
    
    login_frame.wait_for_selector('input[type="password"]', timeout=20000)
    login_frame.fill('input[type="password"]', self.password)
    login_frame.click('button[type="submit"].btn.prime')
    
    # 儲存 session
    self.crawler.save_storage(str(self.storage_file))
```

### 搜尋與列表爬取

要爬取搜尋結果頁面元素，使用以下提示詞：

```
請幫我實現 Nikkei 搜尋功能和列表頁面爬取。需要:
1. 構建搜尋URL，使用關鍵詞參數
2. 定義列表頁面的選擇器，如文章標題、類別、發佈時間等
3. 分頁爬取，每頁結果保存到 nikkei_lists.json
```

選擇器配置示例（在 nikkei_config.json 中）：

```json
"selectors": {
  "search_results": {
    "article": ".article-list-container article",
    "title": ".article-header a",
    "category": ".article-category",
    "publish_time": ".article-date",
    "description": ".article-description",
    "next_page": "a.pagination-next"
  }
}
```

### 文章內容爬取

使用以下提示詞獲取文章詳情頁面元素：

```
請幫我實現 Nikkei 文章內容頁面爬取功能。需要:
1. 根據列表中的URL訪問文章詳情頁
2. 設計選擇器獲取文章標題、作者、發佈時間、正文等
3. 處理可能的彈窗和付費牆
4. 將完整內容保存到 nikkei_articles.json
```

## 3. 完善儲存 Cookie、記錄 Log 和螢幕擷圖

### Cookie 儲存實現

使用以下提示詞：

```
請幫我實現完善的 Cookie 管理功能，包含:
1. 首次登入時儲存 Cookie 到文件
2. 後續啟動時自動載入 Cookie
3. 定期更新 Cookie 以維持登入狀態
```

關鍵實現：

```python
# 初始化爬蟲實例
self.crawler = PlaywrightBase(
    headless=browser_config["headless"],
    browser_type=browser_config["browser_type"],
    user_agent=browser_config["user_agent"],
    viewport=browser_config["viewport"],
    storage_state=str(self.storage_file) if self.storage_file.exists() else None
)

# 保存 Cookie 與瀏覽器狀態
self.crawler.save_storage(str(self.storage_file))
```

### 日誌記錄系統

使用以下提示詞：

```
請幫我設計一個完整的日誌系統，需要記錄:
1. 爬蟲啟動和關閉
2. 網頁訪問和導航
3. 元素操作與提取
4. 錯誤和異常處理
5. 每個操作階段的進度
```

關鍵實現：

```python
# 設置日誌
logger = setup_logger(
    name="nikkei_scraper",
    log_file=f"logs/nikkei_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

# 使用示例
logger.info(f"正在訪問搜尋頁面: {search_url}")
logger.warning(f"處理網頁彈窗時出錯: {str(e)}")
logger.error(f"爬取文章內容時發生錯誤: {str(e)}")
```

### 螢幕擷圖功能

使用以下提示詞：

```
請幫我實現網頁截圖功能，需求:
1. 爬取每篇文章後進行截圖保存
2. 使用時間戳和 URL 命名截圖文件
3. 截圖保存到指定的 screenshots 目錄
```

關鍵實現：

```python
# 截圖保存
screenshot_dir = STORAGE_DIR / "screenshots"
screenshot_dir.mkdir(exist_ok=True)
filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{url.split('/')[-1]}.png"
self.crawler.screenshot(path=str(screenshot_dir / filename))
```

## 4. 完善數據儲存與續傳功能

### 數據結構設計

使用以下提示詞：

```
請設計三種數據結構，分別用於:
1. nikkei_lists.json: 儲存所有爬取的文章列表
2. nikkei_articles.json: 儲存文章詳細內容
3. nikkei_results.json: 記錄爬取進度，支持續傳
```

核心實現：

```python
# 列表數據結構
list_item = {
    "url": url,
    "title": title,
    "category": category,
    "publish_time": publish_time,
    "description": description,
    "content_fetched": False,  # 標記是否已爬取內容
    "last_fetch_time": None    # 記錄爬取時間
}

# 文章內容數據結構
article_data = {
    "url": url,
    "category": category,
    "title": title,
    "subtitle": subtitle,
    "image_url": image_url,
    "image_caption": image_caption,
    "author": author,
    "publish_time": publish_time,
    "update_time": update_time,
    "content": content,
    "scraped_at": datetime.now().isoformat()
}

# 爬取進度記錄結構
results_record = {
    "fetch_date": today,
    "records": [
        {"keyword": keywords, "page": current_page}
    ]
}
```

### 續傳機制

使用以下提示詞：

```
請實現爬蟲中斷後的續傳功能:
1. 記錄每組關鍵詞的搜尋進度
2. 記錄每篇文章的爬取狀態
3. 重啟爬蟲時能夠讀取進度繼續爬取
```

關鍵實現：

```python
# 檢查關鍵詞頁面是否已爬取
if any(r["keyword"] == keywords and r["page"] == current_page for r in results_record["records"]):
    logger.info(f"已爬過 {query} 第 {current_page} 頁，略過")
    current_page += 1
    continue

# 檢查文章是否已爬取
pending_articles = [item for item in self.lists if not item.get("content_fetched")]
```

## 5. 反爬蟲技術實現

### 隱身模式與瀏覽器指紋處理

使用以下提示詞：

```
請幫我實現高級的反爬蟲技術，包含:
1. 啟用 PlaywrightBase 的隱身模式
2. 自定義瀏覽器指紋和特徵
3. 添加人類行為模擬，如滾動、停頓、隨機延遲等
```

關鍵實現：

```python
# 啟用隱身模式
self.crawler.enable_stealth_mode()

# 模擬人類滾動頁面
self.human_like.scroll_page(self.crawler.page)

# 隨機延遲
delay = random.uniform(3, 6)
time.sleep(delay)

# 自然滾動和閱讀行為
self.human_like.scroll_page(self.crawler.page)
self.human_like.random_delay(1.5, 3)
self.human_like.scroll_page(self.crawler.page)
```

### 彈窗處理

使用以下提示詞：

```
請實現網頁彈窗自動處理功能:
1. 處理 Cookie 同意彈窗
2. 處理訂閱和付費牆彈窗
3. 處理各種廣告和提示彈窗
```

關鍵實現：

```python
# 使用 check_and_handle_popup 處理可能存在的彈窗
popup_selectors = {
    'cookie': ['.cookie-banner', '.cookie-policy', '[class*="cookie"]'],
    'paywall': ['.paywall-panel', '.registration-panel', '.subscription-banner'],
    'popup': ['.modal', '.popup', '[id*="popup"]', '[class*="popup"]'],
    'newsletter': ['.newsletter-signup', '.subscription-form'],
    'close': ['.close', '.dismiss', '.close-button', '.btn-close'],
    'accept': ['.accept-cookies', '.accept-button', '.agree-button']
}

popups_handled = check_and_handle_popup(self.crawler.page, popup_selectors)
if popups_handled:
    logger.info("自動關閉了網頁彈窗")
```

### 使用者代理與請求間隔

使用以下提示詞：

```
請實現請求控制和使用者代理設定:
1. 使用合理的請求間隔，避免頻繁請求
2. 在頁面切換和操作間添加自然延遲
3. 配置真實的使用者代理(User-Agent)
```

關鍵實現：

```python
# 配置正常的 User-Agent
browser_config = {
    "headless": False,
    "browser_type": "chromium",
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "viewport": {"width": 1280, "height": 800}
}

# 隨機延遲，避免頻繁搜尋
delay = random.uniform(3, 6)
logger.info(f"等待 {delay:.1f} 秒後處理下一組關鍵詞...")
time.sleep(delay)
```

## 運行方式

1. 在 `config` 目錄中配置以下文件：
   - `credentials.ini`：設置您的 Nikkei Asia 帳號密碼
   - `keywords.json`：設置您要搜尋的關鍵詞
   - `nikkei_config.json`：配置爬蟲選項和選擇器

2. 執行爬蟲：
   ```bash
   python nikkei.py
   ```

3. 結果將存儲在以下文件中：
   - `storage/nikkei_lists.json`：所有文章列表
   - `storage/nikkei_articles.json`：文章詳細內容
   - `storage/screenshots/`：網頁截圖
   - `logs/`：爬蟲運行日誌

## 效能與注意事項

1. 爬取速度設置了適當的延遲，以避免被檢測和封鎖
2. 完整實現了中斷續爬功能，支持長時間分段爬取
3. 使用 `PlaywrightBase` 的隱身模式和人類行為模擬，顯著降低被檢測風險
4. 注意定期更新配置文件中的選擇器，適應網站可能的變化

---

此爬蟲程式展示了如何使用 PlaywrightBase 框架構建高級網頁爬蟲，結合了 GitHub Copilot 的強大能力，快速實現包含自動登入、反爬蟲、數據管理等複雜功能。

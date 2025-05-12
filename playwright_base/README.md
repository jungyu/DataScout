# Playwright Base

Playwright Base 是一個高級的網頁自動化與數據採集框架，專注於**反爬蟲檢測**和**人類行為模擬**。基於 Playwright 構建，提供多層次的防檢測機制，讓您的網頁爬蟲能夠像真實用戶一樣與網站互動，避免被封鎖或識別為機器人。

## 主要功能與優勢

- **強大的反檢測系統**：
  - WebGL 與 Canvas 指紋偽裝
  - JavaScript 特徵修改
  - Navigator 屬性自定義
  - 瀏覽器特徵隱藏
  
- **人類行為精確模擬**：
  - 自然的滑鼠移動軌跡與加速度
  - 漸進式頁面滾動
  - 人性化打字速度與隨機錯誤
  - 真實的停頓與閱讀行為

- **全方位資源管理**：
  - 智能代理伺服器輪換
  - 用戶代理標識動態切換
  - Cookie 與瀏覽器狀態持久化
  - 黑名單與失敗處理機制

- **高度可定制化**：
  - 透過 JSON 配置快速自訂行為
  - 模組化設計便於擴展
  - 完整的日誌與錯誤追蹤
  - 支持多種瀏覽器引擎

## 安裝指南

### 第一步：安裝核心依賴

```bash
pip install playwright python-dotenv user-agents requests pillow
```

### 第二步：安裝 Playwright 瀏覽器

```bash
playwright install
```

### 第三步：安裝 PlaywrightBase 框架

從本地安裝（推薦開發模式）：

```bash
pip install -e /path/to/playwright_base
```

或在專案中直接引用：

```python
import sys
from pathlib import Path
sys.path.append(str(Path('/path/to/playwright_base').absolute()))
```

## 快速入門

### 基本使用

```python
from playwright_base import PlaywrightBase, setup_logger

# 設置日誌記錄器
logger = setup_logger(name="my_crawler")

# 創建爬蟲實例
crawler = PlaywrightBase(
    headless=False,
    browser_type="chromium"
)

# 啟動瀏覽器
crawler.start()

try:
    # 訪問網頁
    crawler.goto("https://www.example.com")
    
    # 等待頁面載入完成
    crawler.wait_for_load_state("networkidle")
    
    # 獲取頁面標題
    title = crawler.page.title()
    logger.info(f"頁面標題: {title}")
    
    # 保存截圖
    crawler.screenshot(path="example.png")
    
    # 儲存當前 Cookie
    crawler.save_storage(path="storage.json")
    
finally:
    # 關閉瀏覽器
    crawler.close()
```

### 啟用反檢測功能

```python
from playwright_base import PlaywrightBase
from playwright_base.anti_detection import HumanLikeBehavior, UserAgentManager

# 創建實例
crawler = PlaywrightBase(headless=False)
crawler.start()

# 啟用隱身模式以減少特徵指紋
crawler.enable_stealth_mode()

# 創建人類行為模擬器
human_like = HumanLikeBehavior()

try:
    crawler.goto("https://bot.sannysoft.com/")  # 檢測機器人的網站
    crawler.wait_for_load_state("networkidle")
    
    # 模擬人類滾動頁面
    human_like.scroll_page(crawler.page)
    
    # 隨機滑鼠移動
    human_like.move_mouse_randomly(crawler.page)
    
    # 截圖查看檢測結果
    crawler.screenshot(path="bot_detection_test.png")
    
finally:
    crawler.close()
```

### 使用代理服務器

```python
from playwright_base import PlaywrightBase
from playwright_base.anti_detection import ProxyManager

# 創建代理管理器
proxy_manager = ProxyManager()

# 添加代理
proxy_manager.add_proxy_from_string("http://user:pass@proxy.example.com:8080")

# 獲取 Playwright 格式的代理配置
proxy = proxy_manager.get_playwright_proxy()

# 創建爬蟲實例並使用代理
crawler = PlaywrightBase(
    headless=False,
    proxy=proxy
)

crawler.start()
# ...後續操作...
crawler.close()
```

### 使用配置檔案

```python
from playwright_base import PlaywrightBase
from playwright_base.config.settings import ConfigManager

# 創建配置管理器並載入配置
config = ConfigManager("my_config.json")

# 使用配置創建爬蟲實例
crawler = PlaywrightBase(
    headless=config.get('browser.headless', False),
    browser_type=config.get('browser.browser_type', 'chromium'),
    slow_mo=config.get('browser.slow_mo', 0)
)

crawler.start()
# ...後續操作...
crawler.close()
```

## 主要模組

- **core**: 核心功能模組
- **anti_detection**: 反檢測相關模組
- **storage**: 存儲管理模組
- **config**: 配置管理模組
- **utils**: 工具函數模組

## 進階功能

### 管理多個頁面

```python
from playwright_base import PlaywrightBase

crawler = PlaywrightBase()
crawler.start()

# 註冊頁面事件處理器
crawler.register_page_event_handlers()

# 獲取頁面列表
pages = crawler.pages

# 關閉多餘頁面，保留主頁面
crawler.close_pages(keep_main=True)
```

### 使用上下文管理器

```python
from playwright_base import PlaywrightBase

# 使用 with 語句自動處理資源釋放
with PlaywrightBase(headless=False) as crawler:
    crawler.goto("https://www.example.com")
    content = crawler.page.content()
    print(f"頁面長度: {len(content)}")
    # 自動調用 crawler.close()
```

## 自訂開發

若要擴展框架功能，可以繼承 `PlaywrightBase` 類並添加自定義方法：

```python
from playwright_base import PlaywrightBase

class MyCrawler(PlaywrightBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def extract_prices(self, selector):
        """提取價格數據的自定義方法"""
        elements = self.page.query_selector_all(selector)
        return [float(el.inner_text().replace('$', '')) for el in elements]

# 使用自定義爬蟲
crawler = MyCrawler(headless=False)
crawler.start()
crawler.goto("https://example-shop.com")
prices = crawler.extract_prices(".product-price")
print(f"找到 {len(prices)} 個價格，平均: {sum(prices)/len(prices)}")
crawler.close()
```

## 注意事項

- 請遵守目標網站的使用條款和爬蟲規則
- 建議設置合理的請求間隔，避免對目標網站造成壓力
- 在生產環境中，應處理各種可能的異常和錯誤情況
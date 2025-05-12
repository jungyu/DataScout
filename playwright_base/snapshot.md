# PlaywrightBase 框架 - 技術快照

## 模組結構總覽

PlaywrightBase 是一個基於 Playwright 的網頁自動化與數據採集框架，提供強大的反檢測功能，適用於高級網頁數據抓取與處理。框架設計遵循模組化原則，主要包含以下核心模組：

```
playwright_base/
│
├── __init__.py           # 框架入口點，匯出核心類別與函數
├── README.md             # 使用文檔與範例說明
├── setup.py              # 安裝配置與依賴管理
│
├── core/                 # 核心功能模組
│   ├── base.py           # PlaywrightBase 基礎爬蟲類，提供瀏覽器自動化功能
│   ├── popup_handler.py  # 處理網站常見彈窗，如 Cookie 通知、訂閱彈窗、付費牆等
│   └── stealth.py        # 實現隱身模式，修改瀏覽器特徵以避免被檢測
│
├── anti_detection/       # 反檢測功能
│   ├── __init__.py
│   ├── advanced_detection.py  # 高級反檢測技術，包含代理池與指紋管理
│   ├── human_like.py          # 模擬人類行為，包括滑鼠移動、滾動頁面與打字延遲
│   ├── platform_spoofer.py    # 平台指紋偽裝，模擬不同系統與瀏覽器特徵
│   ├── proxy_manager.py       # 代理管理，輪換、檢測與黑名單功能
│   └── user_agent_manager.py  # User-Agent 管理，自動生成與切換用戶代理
│
├── auth/                 # 認證模組，處理網站登入與權限
│
├── config/               # 配置管理
│   └── settings.py       # 全局配置設置，管理瀏覽器、網絡、存儲等參數
│
├── services/             # 外部服務整合模組
│
├── storage/              # 存儲模組
│   └── storage_manager.py # 管理瀏覽器狀態、Cookies 與 localStorage
│
├── utils/                # 工具類
│   ├── __init__.py
│   ├── error_handler.py  # 處理網頁爬取中的常見錯誤，如 403、驗證碼等
│   ├── exceptions.py     # 自定義異常類型，提供詳細錯誤上下文
│   └── logger.py         # 日誌管理工具，支持多級記錄與輸出格式化
│
├── examples/             # 示例代碼與使用案例
│
└── scripts/              # 實用腳本與自動化工具
```

## 核心功能介紹

### 主要類別與方法

#### PlaywrightBase 類 (core/base.py)

這是框架的核心類別，提供瀏覽器自動化的基礎功能。

##### 初始化參數

```python
def __init__(
    self,
    headless: bool = False,
    browser_type: str = "chromium",
    storage_state: str = None,
    user_agent: str = None,
    proxy: Dict[str, str] = None,
    viewport: Dict[str, int] = None,
    args: List[str] = None,
    ignore_https_errors: bool = True,
    slow_mo: int = 0
):
```

| 參數 | 說明 |
|------|------|
| headless | 是否以無頭模式運行瀏覽器 |
| browser_type | 瀏覽器類型，可選值: 'chromium', 'firefox', 'webkit' |
| storage_state | 存儲狀態檔案路徑，包含 cookies 和 localStorage |
| user_agent | 自定義 User-Agent |
| proxy | 代理設置，例如 {'server': 'http://proxy.com:8080'} |
| viewport | 視窗大小，例如 {'width': 1920, 'height': 1080} |
| args | 瀏覽器啟動參數 |
| ignore_https_errors | 是否忽略 HTTPS 錯誤 |
| slow_mo | 減慢操作的毫秒數，用於調試 |

##### 主要方法

- **start()**: 啟動瀏覽器和創建上下文
- **close()**: 關閉瀏覽器和釋放資源
- **goto(url, timeout=30000, wait_until="domcontentloaded")**: 導航到指定 URL
- **wait_for_load_state(state="networkidle", timeout=30000)**: 等待頁面達到指定加載狀態
- **screenshot(path=None, full_page=True)**: 截取當前頁面截圖
- **save_storage(path)**: 保存當前瀏覽器狀態（cookies、localStorage 等）
- **enable_stealth_mode()**: 啟用隱身模式，降低被檢測風險
- **wait_for_selector(selector, state="visible", timeout=30000)**: 等待元素出現
- **click(selector, **kwargs)**: 點擊元素
- **fill(selector, value, **kwargs)**: 填充表單
- **get_text(selector, timeout=5000)**: 獲取元素文本
- **get_attribute(selector, attribute_name, timeout=5000)**: 獲取元素屬性
- **evaluate(expression, arg=None)**: 執行 JavaScript 表達式
- **extract_all_text()**: 提取頁面所有文本
- **retry(func, retries=3, delay=1, backoff=2, exceptions=None)**: 自動重試機制

### 反檢測功能 (anti_detection/)

#### HumanLikeBehavior 類 (human_like.py)

提供模擬人類瀏覽行為的功能，例如滾動頁面、移動滑鼠、隨機延遲等。

##### 主要方法

- **random_delay(min_delay=1.0, max_delay=3.0)**: 隨機延遲
- **scroll_page(page, **kwargs)**: 模擬滾動頁面
- **move_mouse_randomly(page, **kwargs)**: 隨機滑鼠移動
- **type_with_human_like_delay(page, selector, text, **kwargs)**: 模擬人類打字

#### AdvancedAntiDetection 類 (advanced_detection.py)

提供更複雜的反檢測功能，包含代理池管理、用戶代理池管理和黑名單管理。

##### 主要方法

- **load_proxy_pool(proxies)**: 載入代理池
- **load_ua_pool(user_agents)**: 載入用戶代理池
- **get_random_proxy()**: 獲取隨機代理
- **get_random_ua()**: 獲取隨機用戶代理
- **ban_proxy(proxy, reason="unknown", duration=86400)**: 將代理加入黑名單
- **ban_ua(ua, reason="unknown", duration=86400)**: 將用戶代理加入黑名單

#### PlatformSpoofer 類 (platform_spoofer.py)

提供平台指紋偽裝功能，模擬不同的操作系統、瀏覽器和硬體特徵。

##### 主要方法

- **apply_platform_profile(page, profile_name=None)**: 應用平台配置
- **generate_random_profile()**: 生成隨機平台配置
- **customize_webgl_fingerprint(page)**: 自訂 WebGL 指紋
- **override_hardware_concurrency(page, cores=None)**: 覆寫硬體並發特徵
- **override_screen_resolution(page, width=None, height=None)**: 覆寫螢幕解析度

### 工具類 (utils/)

#### 異常處理 (exceptions.py)

定義框架中使用的自訂異常類別，所有異常繼承自 `PlaywrightBaseException`：

- **BrowserException**: 瀏覽器操作相關異常
- **PageException**: 頁面相關異常
- **ElementException**: 元素相關異常
- **ProxyException**: 代理相關異常
- **CaptchaException**: 驗證碼相關異常
- **AuthenticationException**: 認證相關異常
- **ConfigException**: 配置相關異常
- **NavigationException**: 導航相關異常
- **RequestException**: 請求相關異常
- **AntiDetectionException**: 反檢測相關異常
- **TimeoutException**: 超時相關異常

## 特色功能亮點

1. **強大的反檢測機制**:
   - 瀏覽器指紋偽裝
   - WebGL 和 Canvas 指紋隱藏
   - 平台特徵模擬
   - 自動規避常見的爬蟲檢測技術

2. **人類行為模擬**:
   - 自然的滑鼠移動軌跡
   - 真實的滾動和點擊行為
   - 人類化的打字延遲和錯誤
   - 隨機暫停與瀏覽行為

3. **完整的資源管理**:
   - 自動管理代理池
   - 智能切換用戶代理
   - 瀏覽器狀態存儲和恢復
   - 錯誤重試與自修復機制

4. **高度可配置性**:
   - 簡單的 JSON 配置
   - 多層級日誌記錄
   - 可插拔的模組設計
   - 靈活的擴展接口

## 使用範例

### 基礎使用

```python
from playwright_base import PlaywrightBase, setup_logger

# 設置日誌
logger = setup_logger(name="my_crawler")

# 初始化並啟動
crawler = PlaywrightBase(headless=False)
crawler.start()

try:
    # 訪問網頁
    crawler.goto("https://www.example.com")
    
    # 等待頁面載入
    crawler.wait_for_load_state("networkidle")
    
    # 獲取頁面標題
    title = crawler.page.title()
    logger.info(f"頁面標題: {title}")
    
    # 截取截圖
    crawler.screenshot("example.png")
finally:
    crawler.close()
```

### 反檢測與人類行為模擬

```python
from playwright_base import PlaywrightBase
from playwright_base.anti_detection.human_like import HumanLikeBehavior

crawler = PlaywrightBase(headless=False)
crawler.start()

# 啟用隱身模式
crawler.enable_stealth_mode()

# 創建人類行為模擬器
human = HumanLikeBehavior()

try:
    crawler.goto("https://bot.sannysoft.com")
    
    # 等待載入
    crawler.wait_for_load_state("networkidle")
    
    # 模擬滾動頁面
    human.scroll_page(crawler.page)
    
    # 隨機延遲
    human.random_delay(1.0, 3.0)
    
    # 模擬點擊
    crawler.click("button.test-button")
    
    # 模擬人類打字
    human.type_with_human_like_delay(
        crawler.page,
        "input#search",
        "testing human behavior"
    )
    
    # 截圖檢查反檢測效果
    crawler.screenshot("anti_detect_test.png")
finally:
    crawler.close()
```

## 進階功能整合

PlaywrightBase 框架提供了豐富的功能組合，可以根據不同的需求場景靈活整合：

1. **數據提取與存儲集成**
2. **驗證碼破解系統連接**
3. **多級代理輪換策略**
4. **IP 封鎖自動檢測與恢復**
5. **分布式爬蟲協作**

## 效能與穩定性

框架經過優化設計，在以下方面提供卓越表現：

- **資源效率**: 智能管理瀏覽器實例
- **並發能力**: 支持多頁面並行操作
- **穩定性**: 完善的錯誤處理與自修復功能
- **可擴展性**: 模組化設計便於擴展

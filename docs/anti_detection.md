# 反爬蟲技術文檔

## 概述

本文檔介紹了爬蟲系統中的反爬蟲技術模組，該模組提供了一系列功能來避免被目標網站檢測為自動化爬蟲。反爬蟲技術模組包含多個子模組，每個子模組專注於特定的反爬蟲策略。

## 目錄結構

```
src/anti_detection/
├── __init__.py                  # 模組初始化文件
├── anti_detection_manager.py    # 反爬蟲管理器
├── base_config.py               # 基礎配置類
├── base_error.py                # 基礎錯誤類
├── base_manager.py              # 基礎管理器類
├── browser_fingerprint.py       # 瀏覽器指紋模組
├── browser_fingerprint_manager.py # 瀏覽器指紋管理器
├── cookie_manager.py            # Cookie 管理器
├── detection_handler.py         # 檢測處理器
├── honeypot_detector.py         # 蜜罐檢測器
├── human_behavior.py            # 人類行為模擬
├── proxy_manager.py             # 代理管理器
├── user_agent_manager.py        # User-Agent 管理器
├── configs/                     # 配置文件目錄
│   ├── __init__.py              # 配置初始化文件
│   ├── anti_detection_config.py # 反爬蟲配置
│   ├── browser_fp_config.py     # 瀏覽器指紋配置
│   ├── cookie_config.py         # Cookie 配置
│   ├── delay_config.py          # 延遲配置
│   ├── human_behavior_config.py # 人類行為配置
│   ├── proxy_config.py          # 代理配置
│   └── user_agent_config.py     # User-Agent 配置
└── stealth_scripts/             # 隱藏腳本目錄
    ├── browser_fp.js            # 瀏覽器指紋隱藏腳本
    └── config.js                # 隱藏腳本配置
└── captcha/                     # 驗證碼處理模組
    ├── __init__.py              # 驗證碼模組初始化文件
    ├── handlers/                # 驗證碼處理器目錄
    │   ├── __init__.py          # 處理器初始化文件
    │   ├── poker_captcha.py     # 撲克牌驗證碼處理器
    │   └── advanced_poker_captcha.py # 高級撲克牌驗證碼處理器
    └── utils/                   # 驗證碼工具目錄
        ├── __init__.py          # 工具初始化文件
        └── image_utils.py       # 圖像處理工具
```

## 核心模組

### 反爬蟲管理器 (AntiDetectionManager)

反爬蟲管理器是整個反爬蟲模組的核心，它協調各個子模組的工作，提供統一的介面來應用反爬蟲策略。

主要功能：
- 創建和配置 WebDriver
- 應用隱藏腳本
- 管理代理切換
- 管理 User-Agent 輪換
- 檢測和處理反爬蟲機制
- 檢測和處理蜜罐

### 瀏覽器指紋模組 (BrowserFingerprint)

瀏覽器指紋模組提供了完整的瀏覽器指紋管理功能，包括生成、驗證、應用和管理瀏覽器指紋。該模組分為以下三個主要部分：

### 1. 核心功能 (core.py)

核心功能模組提供基礎的指紋處理功能：

```python
from src.anti_detection.fingerprint import BrowserFingerprint

# 創建指紋實例
fingerprint = BrowserFingerprint()

# 生成完整的指紋數據
fingerprint_data = fingerprint.generate()

# 驗證指紋數據
is_valid = fingerprint.validate()

# 應用指紋到瀏覽器
fingerprint.apply(driver)

# 生成指紋報告
report = fingerprint.generate_report()
```

主要功能：
- 統一的指紋數據結構管理
- 完整的指紋參數生成
- CDP 命令和 JavaScript 注入
- 指紋驗證和報告生成

### 2. 指紋管理 (manager.py)

指紋管理模組負責管理多個指紋配置：

```python
from src.anti_detection.fingerprint import BrowserFingerprintManager

# 創建指紋管理器
manager = BrowserFingerprintManager()

# 添加指紋
manager.add_fingerprint(fingerprint_data)

# 獲取指紋
current_fp = manager.get_fingerprint()

# 輪換指紋
next_fp = manager.rotate_fingerprint()

# 驗證所有指紋
manager.validate_all()
```

主要功能：
- 指紋存儲和檢索
- 指紋輪換策略
- 批量指紋驗證
- 指紋數據持久化

### 3. 工具函數 (utils.py)

工具函數模組提供常用的指紋處理工具：

```python
from src.anti_detection.fingerprint.utils import (
    generate_fingerprint,
    validate_fingerprint,
    apply_fingerprint,
    generate_fingerprint_report
)

# 快速生成指紋
fp_data = generate_fingerprint()

# 驗證指紋數據
is_valid = validate_fingerprint(fp_data)

# 應用指紋到瀏覽器
apply_fingerprint(driver, fp_data)

# 生成指紋報告
report = generate_fingerprint_report(fp_data)
```

主要功能：
- 快速指紋生成
- 指紋數據驗證
- 指紋應用輔助
- 報告生成工具

### 配置系統

指紋模組使用專門的配置類來管理設置：

```python
from src.anti_detection.configs import BrowserFingerprintConfig

# 創建默認配置
config = BrowserFingerprintConfig()

# 從字典創建配置
config = BrowserFingerprintConfig.from_dict({
    "user_agent": {
        "browser": "chrome",
        "version": "120.0.0",
        "platform": "windows"
    },
    "screen": {
        "width": 1920,
        "height": 1080,
        "color_depth": 24
    }
})

# 驗證配置
is_valid = config.validate()

# 轉換為字典
config_dict = config.to_dict()
```

配置類別包含：
- 用戶代理配置
- 螢幕參數配置
- 瀏覽器功能配置
- 硬體特徵配置
- 語言和時區配置

### 人類行為模擬 (HumanBehaviorSimulator)

人類行為模擬模組負責模擬人類的瀏覽行為，使爬蟲的行為更接近真實用戶。

主要功能：
- 模擬鼠標移動
- 模擬點擊操作
- 模擬滾動操作
- 模擬文本輸入
- 生成隨機延遲

### 代理管理器 (ProxyManager)

代理管理器負責管理代理服務器，包括代理的配置、驗證、輪換和健康檢查。

主要功能：
- 配置和驗證代理服務器
- 管理代理池
- 輪換代理服務器
- 健康檢查
- 性能監控
- 自動切換

### User-Agent 管理器 (UserAgentManager)

User-Agent 管理器負責管理 User-Agent，包括生成、驗證和輪換 User-Agent。

主要功能：
- 生成 User-Agent
- 驗證 User-Agent
- 管理 User-Agent 池
- 輪換 User-Agent
- 統計分析

### Cookie 管理器 (CookieManager)

Cookie 管理器負責管理 Cookie，包括生成、驗證、輪換和加密存儲 Cookie。

主要功能：
- 生成 Cookie
- 驗證 Cookie
- 管理 Cookie 池
- 輪換 Cookie
- 加密存儲
- 過期管理
- 並發控制

### 檢測處理器 (DetectionHandler)

檢測處理器負責檢測和處理反爬蟲機制，包括分析檢測結果、調整檢測策略和迴避檢測。

主要功能：
- 檢測結果分析
- 檢測策略調整
- 檢測迴避
- 檢測報告

### 蜜罐檢測器 (HoneypotDetector)

蜜罐檢測器負責檢測和處理蜜罐，包括檢測蜜罐元素、分析蜜罐特徵和迴避蜜罐。

主要功能：
- 蜜罐元素檢測
- 蜜罐行為檢測
- 蜜罐特徵分析
- 蜜罐迴避

## 隱藏腳本

隱藏腳本是一系列 JavaScript 腳本，用於在瀏覽器中隱藏自動化特徵。

### 瀏覽器指紋隱藏腳本 (browser_fp.js)

瀏覽器指紋隱藏腳本用於修改瀏覽器的指紋，使其更接近真實瀏覽器。

主要功能：
- 修改 navigator 物件
- 修改螢幕屬性
- 偽裝 WebGL
- 修改 Canvas
- 修改音頻
- 修改字體
- 修改性能
- 隱藏自動化特徵

### 隱藏腳本配置 (config.js)

隱藏腳本配置文件，包含各種隱藏腳本的配置參數。

主要配置：
- 螢幕配置
- 語言配置
- WebGL 配置
- Canvas 配置
- 音頻配置
- 字體配置

## 配置系統

反爬蟲模組使用配置系統來管理各種參數和設置。

### 基礎配置 (base_config.py)

基礎配置類，提供配置的基礎功能。

主要功能：
- 加載配置
- 保存配置
- 驗證配置
- 合併配置

### 反爬蟲配置 (anti_detection_config.py)

反爬蟲配置，包含反爬蟲模組的各種參數和設置。

主要配置：
- 延遲設置
- 重試設置
- 檢測設置
- 處理設置

### 瀏覽器指紋配置 (browser_fp_config.py)

瀏覽器指紋配置，包含瀏覽器指紋模組的各種參數和設置。

主要配置：
- 指紋生成設置
- 指紋驗證設置
- 指紋應用設置

### 人類行為配置 (human_behavior_config.py)

人類行為配置，包含人類行為模擬模組的各種參數和設置。

主要配置：
- 鼠標移動設置
- 點擊操作設置
- 滾動操作設置
- 文本輸入設置

### 代理配置 (proxy_config.py)

代理配置，包含代理管理器的各種參數和設置。

主要配置：
- 代理類型設置
- 代理驗證設置
- 代理輪換設置
- 健康檢查設置

### User-Agent 配置 (user_agent_config.py)

User-Agent 配置，包含 User-Agent 管理器的各種參數和設置。

主要配置：
- 瀏覽器類型設置
- 版本設置
- 平台設置
- 設備設置

### Cookie 配置 (cookie_config.py)

Cookie 配置，包含 Cookie 管理器的各種參數和設置。

主要配置：
- Cookie 生成設置
- Cookie 驗證設置
- Cookie 輪換設置
- 加密設置

## 驗證碼處理模組

驗證碼處理模組提供了一系列功能來處理各種類型的驗證碼。

### 撲克牌驗證碼處理器 (PokerCaptchaSolver)

撲克牌驗證碼處理器負責處理撲克牌類型的驗證碼，包括識別和匹配卡牌。

主要功能：
- 提取卡牌圖片
- 識別卡牌顏色
- 匹配卡牌
- 自動點擊匹配的卡牌

### 高級撲克牌驗證碼處理器 (AdvancedPokerCaptchaSolver)

高級撲克牌驗證碼處理器提供更進階的撲克牌驗證碼處理功能。

主要功能：
- 識別卡牌花色
- 更精確的卡牌匹配
- 支援模板匹配
- 更強大的圖像處理

## 使用方式

### 基本使用

```python
from src.anti_detection import AntiDetectionManager

# 創建反爬蟲管理器
anti_detection = AntiDetectionManager()

# 創建 WebDriver
driver = anti_detection.create_webdriver(headless=True)

# 訪問網站
driver.get("https://example.com")

# 檢測反爬蟲機制
if anti_detection.detected_anti_crawling(driver):
    # 處理反爬蟲機制
    anti_detection.handle_detection(driver)

# 檢測蜜罐
if anti_detection.detect_honeypots(driver):
    # 處理蜜罐
    pass

# 關閉 WebDriver
driver.quit()
```

### 高級使用

```python
from src.anti_detection import AntiDetectionManager
from src.anti_detection.utils.browser_fingerprint import BrowserFingerprint
from src.anti_detection.utils.human_behavior import HumanBehaviorSimulator
from src.anti_detection.proxy_manager import ProxyManager
from src.anti_detection.user_agent_manager import UserAgentManager

# 創建反爬蟲管理器
anti_detection = AntiDetectionManager()

# 創建 WebDriver
driver = anti_detection.create_webdriver(headless=True)

# 應用隱藏模式
anti_detection.enable_stealth_mode(driver)

# 訪問網站
driver.get("https://example.com")

# 模擬人類行為
human_behavior = HumanBehaviorSimulator()
element = driver.find_element_by_id("search-input")
human_behavior.move_to_element(driver, element)
human_behavior.type_text(driver, element, "search query")
human_behavior.click_element(driver, element)

# 檢測反爬蟲機制
if anti_detection.detected_anti_crawling(driver):
    # 處理反爬蟲機制
    anti_detection.handle_detection(driver)

# 檢測蜜罐
if anti_detection.detect_honeypots(driver):
    # 處理蜜罐
    pass

# 關閉 WebDriver
driver.quit()
```

## 最佳實踐

1. **使用隱藏模式**：在創建 WebDriver 後，立即應用隱藏模式。
2. **模擬人類行為**：在與頁面交互時，使用人類行為模擬。
3. **定期切換代理**：定期切換代理，避免 IP 被封鎖。
4. **定期切換 User-Agent**：定期切換 User-Agent，避免被識別為同一用戶。
5. **檢測和處理反爬蟲機制**：定期檢測反爬蟲機制，並及時處理。
6. **檢測和處理蜜罐**：在點擊元素前，檢測是否為蜜罐。
7. **使用 Cookie 管理**：使用 Cookie 管理器管理 Cookie，避免 Cookie 過期。
8. **使用瀏覽器指紋**：使用瀏覽器指紋模組修改瀏覽器指紋，避免被識別為自動化工具。

## 注意事項

1. **遵守網站的使用條款**：在使用反爬蟲技術時，請遵守網站的使用條款。
2. **避免過度請求**：避免對目標網站發送過多請求，以免對網站造成負擔。
3. **定期更新配置**：定期更新配置，以適應網站的變化。
4. **監控反爬蟲機制**：定期監控反爬蟲機制，及時調整策略。
5. **使用適當的延遲**：使用適當的延遲，避免請求過於頻繁。
6. **使用適當的代理**：使用適當的代理，避免 IP 被封鎖。
7. **使用適當的 User-Agent**：使用適當的 User-Agent，避免被識別為自動化工具。
8. **使用適當的 Cookie**：使用適當的 Cookie，避免 Cookie 過期。
9. **使用適當的瀏覽器指紋**：使用適當的瀏覽器指紋，避免被識別為自動化工具。

# 反檢測模組

## 人類行為模擬

人類行為模擬模組提供以下功能：

1. 滑鼠移動
   - 隨機移動
   - 貝塞爾曲線
   - 點擊延遲

2. 鍵盤輸入
   - 隨機延遲
   - 輸入速度
   - 錯誤修正

3. 頁面滾動
   - 隨機滾動
   - 滾動速度
   - 滾動方向

4. 隨機延遲
   - 頁面加載
   - 操作之間
   - 點擊之前

### 使用示例

```python
from src.anti_detection.human_behavior import HumanBehavior

# 創建行為模擬器
behavior = HumanBehavior(driver)

# 模擬滑鼠移動
behavior.move_to_element(element)

# 模擬鍵盤輸入
behavior.type_text(element, "Hello World")

# 模擬頁面滾動
behavior.scroll_page()

# 添加隨機延遲
behavior.random_delay()
```

## 代理管理

代理管理模組提供以下功能：

1. 代理獲取
   - 代理池管理
   - 代理質量檢測
   - 代理輪換

2. 代理驗證
   - 可用性檢查
   - 速度測試
   - 匿名度檢測

3. 代理配置
   - 代理設置
   - 認證信息
   - 超時設置

### 使用示例

```python
from src.anti_detection.proxy_manager import ProxyManager

# 創建代理管理器
proxy_manager = ProxyManager()

# 獲取代理
proxy = proxy_manager.get_proxy()

# 驗證代理
is_valid = proxy_manager.validate_proxy(proxy)

# 設置代理
proxy_manager.set_proxy(driver, proxy)
```

## 請求控制

請求控制模組提供以下功能：

1. 請求頻率
   - 請求限制
   - 時間間隔
   - 並發控制

2. 請求頭管理
   - 頭部生成
   - 頭部驗證
   - 頭部輪換

3. 請求重試
   - 重試策略
   - 錯誤處理
   - 超時控制

### 使用示例

```python
from src.anti_detection.request_controller import RequestController

# 創建請求控制器
controller = RequestController()

# 添加請求
controller.add_request()

# 檢查是否可以請求
can_request = controller.can_request()

# 設置請求頭
controller.set_headers(headers)
```

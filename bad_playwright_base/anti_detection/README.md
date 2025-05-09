# Playwright 反檢測模組

這個模組提供了一系列功能來幫助避免網站的反爬蟲檢測，包括指紋偽裝、代理管理、人類行為模擬和用戶代理管理。

## 功能特點

1. 指紋偽裝
   - WebGL 指紋偽裝
   - Canvas 指紋偽裝
   - Audio 指紋偽裝
   - Font 指紋偽裝
   - Screen 指紋偽裝
   - Platform 指紋偽裝

2. 代理管理
   - 代理配置
   - 代理輪換
   - 代理黑名單
   - 代理池管理

3. 人類行為模擬
   - 鼠標移動軌跡
   - 鍵盤輸入模式
   - 頁面滾動行為
   - 點擊行為
   - 表單填寫行為

4. 用戶代理管理
   - 用戶代理生成
   - 用戶代理輪換
   - 用戶代理黑名單
   - 用戶代理池管理

## 安裝

```bash
pip install playwright-base
```

## 基本使用

```python
from playwright_base.anti_detection import AntiDetectionManager

# 初始化反檢測管理器
anti_detection = AntiDetectionManager()

# 配置反檢測選項
config = {
    "enabled": True,
    "fingerprint": {
        "enabled": True,
        "webgl": True,
        "canvas": True,
        "audio": True,
        "font": True,
        "screen": True,
        "platform": True
    },
    "proxy": {
        "enabled": True,
        "rotation_interval": 300,  # 5分鐘
        "blacklist_duration": 3600  # 1小時
    },
    "behavior": {
        "enabled": True,
        "mouse_speed": {
            "min": 0.5,
            "max": 2.0
        },
        "typing_speed": {
            "min": 100,
            "max": 300
        },
        "scroll_speed": {
            "min": 100,
            "max": 500
        },
        "click_delay": {
            "min": 0.1,
            "max": 0.5
        },
        "form_delay": {
            "min": 0.5,
            "max": 2.0
        }
    },
    "user_agent": {
        "enabled": True,
        "rotation_interval": 3600,  # 1小時
        "blacklist_duration": 86400  # 24小時
    }
}
anti_detection.set_config(config)

# 添加代理
proxy = {
    "server": "http://proxy.example.com:8080",
    "username": "user",
    "password": "pass"
}
anti_detection.add_proxy(proxy)

# 在 Playwright 頁面中使用
async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    
    # 應用反檢測功能
    await anti_detection.apply_anti_detection(page)
    
    # 訪問目標網站
    await page.goto('https://example.com')
    
    # 模擬人類行為
    await anti_detection.scroll_page(page)
    await anti_detection.move_mouse(page, (100, 100))
    await anti_detection.click_element(page, '#submit-button')
```

## 高級使用

```python
from playwright_base.anti_detection import AdvancedAntiDetection

# 初始化高級反檢測
anti_detection = AdvancedAntiDetection()

# 載入代理池
proxies = [
    {
        "server": "http://proxy1.example.com:8080",
        "username": "user1",
        "password": "pass1"
    },
    {
        "server": "http://proxy2.example.com:8080",
        "username": "user2",
        "password": "pass2"
    }
]
anti_detection.load_proxy_pool(proxies)

# 載入用戶代理池
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]
anti_detection.load_ua_pool(user_agents)

# 運行高級反檢測
await anti_detection.run('https://example.com')
```

## 配置選項

### 指紋偽裝配置

```python
fingerprint_config = {
    "enabled": True,
    "webgl": True,
    "canvas": True,
    "audio": True,
    "font": True,
    "screen": True,
    "platform": True
}
```

### 代理配置

```python
proxy_config = {
    "enabled": True,
    "rotation_interval": 300,  # 5分鐘
    "blacklist_duration": 3600  # 1小時
}
```

### 行為模擬配置

```python
behavior_config = {
    "enabled": True,
    "mouse_speed": {
        "min": 0.5,
        "max": 2.0
    },
    "typing_speed": {
        "min": 100,
        "max": 300
    },
    "scroll_speed": {
        "min": 100,
        "max": 500
    },
    "click_delay": {
        "min": 0.1,
        "max": 0.5
    },
    "form_delay": {
        "min": 0.5,
        "max": 2.0
    }
}
```

### 用戶代理配置

```python
ua_config = {
    "enabled": True,
    "rotation_interval": 3600,  # 1小時
    "blacklist_duration": 86400  # 24小時
}
```

## 注意事項

1. 使用代理時，請確保代理服務器的可用性和穩定性。
2. 建議定期清理黑名單，以避免資源浪費。
3. 行為模擬的速度和延遲可以根據實際需求調整。
4. 用戶代理輪換間隔建議不要設置太短，以避免被檢測。
5. 指紋偽裝可能會影響某些網站的功能，請根據實際情況調整配置。

## 貢獻

歡迎提交 Issue 和 Pull Request 來幫助改進這個模組。

## 許可證

MIT License 
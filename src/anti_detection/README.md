# 蝦皮(Shopee)網站爬蟲反檢測模組

這個模組提供了用於繞過蝦皮網站反爬蟲機制的功能。

## 主要功能

1. 瀏覽器指紋偽裝
   - 隨機 User-Agent
   - WebGL 指紋偽裝
   - Canvas 指紋偽裝
   - 字體列表偽裝
   - 插件列表偽裝

2. 自動化檢測繞過
   - 隱藏 Selenium 特徵
   - 繞過 WebDriver 檢測
   - 繞過自動化工具檢測

3. 人類行為模擬
   - 隨機滑鼠移動
   - 滾動行為模擬
   - 點擊行為模擬

4. 驗證碼處理
   - 滑塊驗證碼處理
   - reCAPTCHA 處理
   - 圖像驗證碼處理

5. Cookie 管理
   - Cookie 保護
   - Cookie 持久化
   - Cookie 驗證

## 使用方法

```python
from anti_detection import ShopeeAntiFingerprint

# 創建反檢測實例
anti_fp = ShopeeAntiFingerprint({
    'user_agent': 'Mozilla/5.0 ...',
    'proxy': 'http://your-proxy:port',
    'headless': False,
    'window_size': (1920, 1080),
    'webgl_noise': 0.1,
    'canvas_noise': 0.1,
    'mouse_movement': True,
    'cookie_protection': True
})

# 設置 WebDriver
driver = anti_fp.setup_driver()

# 訪問蝦皮網站
anti_fp.navigate_to_shopee('https://shopee.tw')

# 保存 cookies
anti_fp.save_cookies('cookies.json')

# 加載 cookies
anti_fp.load_cookies('cookies.json')

# 關閉瀏覽器
anti_fp.close()
```

## 配置選項

- `user_agent`: 瀏覽器 User-Agent
- `proxy`: 代理服務器地址
- `headless`: 是否使用無頭模式
- `window_size`: 窗口大小，格式為 (width, height)
- `webgl_noise`: WebGL 指紋噪聲值
- `canvas_noise`: Canvas 指紋噪聲值
- `mouse_movement`: 是否啟用滑鼠移動模擬
- `cookie_protection`: 是否啟用 Cookie 保護

## 注意事項

1. 本模組僅用於學習和研究目的
2. 請遵守網站的使用條款和爬蟲協議
3. 建議使用代理 IP 輪換
4. 適當設置請求間隔，避免過度請求
5. 定期更新瀏覽器指紋和 User-Agent 
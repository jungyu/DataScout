# 爬蟲反偵測機制說明

## 常見的爬蟲偵測方式

1. User-Agent 檢查
   - 網站會檢查請求標頭中的 User-Agent 是否來自正常瀏覽器
   - 若使用預設的 WebDriver User-Agent，容易被識別為爬蟲

2. WebDriver 特徵檢測
   - 檢查 navigator.webdriver 屬性
   - 檢查瀏覽器特定的自動化控制接口
   - 檢測瀏覽器插件、語言設定等異常
   
3. 行為模式分析
   - 點擊與操作過於規律
   - 請求速度異常快
   - 缺乏正常使用者的隨機性

4. 指紋識別
   - Canvas 指紋識別
   - WebGL 指紋識別
   - 字體列表檢測
   - 硬件指紋識別

5. Cookie 和 Session 檢測
   - 檢查 Cookie 存在性及合法性
   - 跟踪 Session 行為一致性

## 解決方案

### 1. User-Agent 偽裝
```python
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
```

### 2. 移除 WebDriver 特徵
```python
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)

# 執行前的隱藏特徵腳本
stealth_script = """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
"""
driver.execute_script(stealth_script)
```

### 3. 模擬真實使用者行為

#### 隨機時間延遲
```python
import random
import time

# 隨機等待，模擬人類思考和操作時間
time.sleep(random.uniform(2, 5))
```

#### 模擬滑鼠移動軌跡
```python
from selenium.webdriver.common.action_chains import ActionChains

# 模擬漸進式滑鼠移動
def move_to_element_realistic(driver, element):
    actions = ActionChains(driver)
    
    # 目標元素位置
    target_x, target_y = element.location['x'], element.location['y']
    
    # 當前滑鼠位置 (假設在視窗中間)
    current_x, current_y = driver.execute_script("return [window.innerWidth/2, window.innerHeight/2];")
    
    # 計算多個中間點
    steps = random.randint(5, 10)
    for i in range(steps):
        ratio = (i + 1) / steps
        x = current_x + (target_x - current_x) * ratio
        y = current_y + (target_y - current_y) * ratio
        
        # 增加少許隨機性
        x += random.randint(-5, 5)
        y += random.randint(-5, 5)
        
        actions.move_by_offset(x - current_x, y - current_y)
        current_x, current_y = x, y
        actions.pause(random.uniform(0.05, 0.1))
    
    actions.move_to_element(element)
    actions.perform()
```

#### 頁面滾動行為
```python
# 模擬人類閱讀頁面的滾動行為
def realistic_scroll(driver):
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    
    current_position = 0
    while current_position < total_height:
        # 計算下一個滾動位置 (不規則的滾動量)
        scroll_amount = random.randint(100, 300)
        current_position += scroll_amount
        
        # 執行滾動
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        
        # 隨機暫停，模擬閱讀
        time.sleep(random.uniform(0.5, 2.0))
        
        # 偶爾上滾一點，模擬重新查看內容
        if random.random() < 0.2 and current_position > viewport_height:
            back_scroll = random.randint(50, 100)
            current_position -= back_scroll
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(random.uniform(0.5, 1.0))
```

### 4. 使用代理伺服器
```python
options.add_argument('--proxy-server=http://proxy_ip:port')

# 代理伺服器輪換
proxies = [
    "http://proxy1:port1",
    "http://proxy2:port2",
    "http://proxy3:port3"
]
options.add_argument(f'--proxy-server={random.choice(proxies)}')
```

### 5. 瀏覽器指紋隨機化

```python
# 添加擴展程式以修改canvas和WebGL指紋
options.add_extension('path_to_canvas_defender_extension.crx')

# 設置語言和時區
options.add_argument('--lang=zh-TW,zh,en-US,en')
options.add_argument('--timezone=Asia/Taipei')

# 設置屏幕分辨率
options.add_argument('--window-size=1920,1080')
```

## 本專案實現方式

在本框架中，反偵測機制被封裝到以下幾個模組中：

1. `src/anti_detection/stealth_mode.py` - 實現WebDriver特徵隱藏和User-Agent偽裝
2. `src/anti_detection/proxy_manager.py` - 處理代理伺服器配置和輪換
3. `src/anti_detection/behavior_simulator.py` - 模擬人類行為模式

### 使用方法

在命令行中使用反偵測功能：

```bash
# 基本使用
python main.py -t templates/example.json --stealth --human-like

# 使用代理伺服器
python main.py -t templates/example.json --stealth --proxy http://proxy_ip:port

# 自定義User-Agent
python main.py -t templates/example.json --user-agent "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
```

在配置文件中設定：

```json
{
  "anti_detection": {
    "stealth_mode": true,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "proxy": "http://proxy_ip:port",
    "human_like": true,
    "random_delay": [2, 5]
  }
}
```

## 注意事項

1. 不同網站可能採用不同的偵測機制，需要針對性調整
2. 建議在程式中加入錯誤處理機制
3. 遵守網站的 robots.txt 規則，避免違反網站服務條款
4. 適當的請求間隔，避免對目標網站造成負擔
5. 定期更新反偵測策略，因為網站的防護機制也在不斷更新
6. 在一個爬蟲會話中保持行為一致性，避免突然改變瀏覽模式

## 高級技巧

1. **無頭瀏覽器檢測規避**
```python
# 設置多種參數避免無頭瀏覽器被檢測
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
```

2. **Cookie和Session管理**
```python
# 保存認證狀態，用於後續請求
cookies = driver.get_cookies()
with open('cookies.json', 'w') as f:
    json.dump(cookies, f)

# 加載之前保存的cookies
with open('cookies.json', 'r') as f:
    cookies = json.load(f)
for cookie in cookies:
    driver.add_cookie(cookie)
```

3. **處理驗證碼和人機驗證**
   - 與驗證碼識別服務集成
   - 當遇到複雜的驗證時，可以考慮人工介入

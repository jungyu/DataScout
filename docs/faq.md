# Selenium 模板化爬蟲框架 - 常見問題 (FAQ)

## 一般問題

### Q: 如何快速開始使用這個爬蟲系統？
**A:** 最快的入門方式是：
1. 安裝依賴套件 `pip install -r requirements.txt`
2. 複製範例模板 `templates/example.json` 並按需修改
3. 執行 `python main.py -t templates/your_template.json`

### Q: 這個爬蟲系統支援哪些網站？
**A:** 理論上支援任何基於 HTML 的網站。由於使用了 Selenium，即使是動態加載的內容也能爬取。不過，需要為每個網站創建對應的 JSON 模板。

### Q: 如何判斷我的爬蟲是否成功運行？
**A:** 檢查以下幾點：
1. 日誌文件中有 "爬取完成" 和相關資訊記錄
2. 數據文件已生成並包含預期的數據
3. 程序正常結束，沒有拋出異常

### Q: 我應該選擇哪種瀏覽器？
**A:** 系統支援多種瀏覽器，但各有優缺點：
- **Chrome**：兼容性最好，功能最完整，是預設選擇
- **Firefox**：開源選項，某些情況下更不容易被識別為爬蟲
- **Edge**：Windows 系統整合較好

通常建議使用 Chrome，除非有特殊需求。

## 模板配置問題

### Q: 如何找到正確的選擇器？
**A:** 您可以使用瀏覽器的開發者工具：
1. 右鍵點擊目標元素，選擇「檢查」或「Inspect」
2. 在元素上右鍵點擊，選擇「Copy」>「Copy selector」(CSS) 或「Copy XPath」
3. 對於複雜頁面，可使用 SelectorGadget、XPath Helper 或 ChroPath 等瀏覽器擴展

### Q: CSS 選擇器和 XPath 選擇器有什麼區別？
**A:** 兩者都可用於定位元素，但有不同特點：
- **CSS 選擇器**：通常更簡潔、執行速度更快，但不能選擇父元素或前兄弟元素
- **XPath**：更強大靈活，可以導航元素樹的任何部分，但可能較複雜且執行較慢

在模板中，您可以混用兩種選擇器，根據需要選擇合適的類型。

### Q: 分頁機制不工作，怎麼辦？
**A:** 常見原因有：
1. `next_page_selector` 不正確，確認下一頁按鈕的選擇器
2. 網站使用 AJAX 加載，嘗試切換到 `url` 分頁方式（使用 `{page}` 參數）
3. 增加 `wait_time` 的值，給頁面更多加載時間
4. 確認是否有翻頁上限或到達了最後一頁

### Q: 如何處理需要登入的網站？
**A:** 在模板中添加登入配置：
```json
{
  "login": {
    "url": "https://example.com/login",
    "username_selector": "#username",
    "password_selector": "#password",
    "submit_selector": "button[type='submit']",
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD",
    "success_check": {
      "selector": ".user-info",
      "attribute": "text",
      "pattern": ".*歡迎.*"
    }
  }
}
```
最好將敏感的登入資訊存放在 `config/credentials.json` 文件中。

### Q: 如何處理彈出視窗或警告？
**A:** 在模板中添加彈窗處理配置：
```json
{
  "interactions": [
    {
      "name": "處理彈窗",
      "type": "popup",
      "action": "close",
      "selector": ".modal-close"
    },
    {
      "name": "接受 Cookie 同意",
      "type": "button",
      "action": "click",
      "selector": "button[id='accept-cookies']",
      "optional": true
    },
    {
      "name": "處理瀏覽器警告",
      "type": "alert",
      "action": "accept"
    }
  ]
}
```

## 資料處理問題

### Q: 爬取的數據格式不正確，如何轉換？
**A:** 使用數據處理器：
1. 在模板中添加數據處理器：
```json
{
  "detail_page": {
    "data": {
      "price": {
        "selector": ".price",
        "attribute": "text",
        "processor": "extract_number"
      },
      "date": {
        "selector": ".date",
        "attribute": "text",
        "processor": "format_date"
      }
    }
  }
}
```

2. 或者使用自定義數據處理器：
```python
def clean_price(value):
    if value:
        return float(value.replace('$', '').replace(',', ''))
    return 0.0

crawler.register_processor('clean_price', clean_price)
```

### Q: 如何過濾不需要的數據？
**A:** 在模板中添加過濾規則：
```json
{
  "filters": {
    "include_only": {
      "price": "> 100"
    },
    "exclude": {
      "status": "已截止"
    }
  }
}
```

或者在代碼中進行過濾：
```python
data = crawler.crawl()
filtered_data = [item for item in data if item.get('price', 0) > 100]
```

### Q: 如何將爬取的數據存儲到數據庫？
**A:** 配置數據庫存儲：
```json
{
  "persistence": {
    "type": "database",
    "database": {
      "type": "mysql",
      "host": "localhost",
      "port": 3306,
      "database": "crawler_data",
      "table": "items",
      "username": "root",
      "password": "password"
    }
  }
}
```

或者使用代碼：
```python
from src.persistence.database import DatabaseStorage

# 初始化數據庫存儲
db_storage = DatabaseStorage(
    db_type="mysql",
    host="localhost", 
    database="crawler_data",
    username="user",
    password="pass"
)

# 保存數據
db_storage.save(data, "my_table")
```

## 性能和穩定性問題

### Q: 爬蟲執行太慢，如何優化？
**A:** 可以嘗試以下方法：
1. 減少延遲時間：調整 `"anti_detection": {"random_delay": [1, 2]}` 配置
2. 關閉人類行為模擬：設置 `"anti_detection": {"human_like": false}`
3. 使用無頭模式：設置 `"webdriver": {"headless": true}`
4. 限制詳情頁處理數量：使用 `--items <數量>` 參數
5. 禁用不必要的瀏覽器功能：添加 `"disable_images": true` 和 `"disable_javascript": false`

### Q: 爬蟲經常被中斷，如何提高穩定性？
**A:** 改善穩定性的方法：
1. 使用隱身模式：添加 `--stealth` 參數
2. 使用代理服務器：添加 `--proxy http://proxy_ip:port` 參數
3. 模擬真實用戶行為：設置 `"anti_detection": {"human_like": true}`
4. 隨機化 User-Agent：提供多個 User-Agent 選項
5. 增加等待時間：調整 `implicit_wait` 值和 `random_delay` 範圍

### Q: 如何處理驗證碼問題？
**A:** 系統提供多種驗證碼處理方案：

1. 對於簡單圖形驗證碼，使用內建 OCR：
```json
{
  "captcha": {
    "service": "local_ocr",
    "selector": "img.captcha",
    "input_selector": "input[name='captcha']",
    "submit_selector": "button[type='submit']"
  }
}
```

2. 對於複雜驗證碼，使用第三方服務：
```json
{
  "captcha": {
    "service": "2captcha",
    "api_key": "YOUR_API_KEY",
    "selector": "#recaptcha",
    "type": "recaptcha"
  }
}
```

3. 特殊情況可能需要人工干預：
```json
{
  "captcha": {
    "service": "manual",
    "timeout": 300,
    "selector": "img.captcha",
    "input_selector": "input[name='captcha']"
  }
}
```

### Q: 如何處理複雜的反爬蟲機制？
**A:** 針對進階的反爬蟲機制，可以：
1. 使用隱身模式：移除 WebDriver 特徵
2. 模擬真實用戶行為：隨機延遲、自然滾動、真實點擊
3. 使用高質量代理：輪換 IP 地址
4. 配置瀏覽器指紋：使其看起來像正常用戶

範例配置：
```json
{
  "anti_detection": {
    "stealth_mode": true,
    "human_like": true,
    "random_delay": [2, 5],
    "fingerprint": {
      "timezone": "Asia/Taipei",
      "screen_resolution": "1920x1080",
      "language": "zh-TW,en-US;q=0.9"
    }
  }
}
```

## 錯誤和調試問題

### Q: 為什麼爬蟲沒有提取到任何數據？
**A:** 可能的原因：
1. 選擇器不正確：驗證選擇器是否還能匹配目標元素
2. 網站結構變更：檢查網站是否更新了 HTML 結構
3. 等待時間不足：增加 `implicit_wait` 值
4. 被反爬機制阻擋：檢查是否需要模擬登入或使用代理

### Q: 如何診斷元素定位失敗的問題？
**A:** 
1. 啟用調試模式：使用 `--debug` 參數
2. 查看詳細日誌：使用 `--verbose` 參數
3. 截圖確認：設置 `"debug": {"screenshot": true}`
4. 使用多種選擇器：同時提供 CSS 和 XPath 選擇器
5. 檢查網站是否使用動態 ID 或類名

### Q: 日誌中顯示 "TimeoutException"，如何解決？
**A:** 解決超時問題：
1. 增加 `implicit_wait` 時間：調整配置中的值
2. 使用更精確的選擇器：避免使用太通用的選擇器
3. 檢查元素是否在 iframe 中：需要先切換 frame
4. 確認頁面是否完全加載：添加特定等待條件
5. 檢查網絡連接：確保網絡穩定

### Q: Chrome 啟動失敗怎麼辦？
**A:**
1. 檢查 Chrome 和 ChromeDriver 版本是否匹配
2. 嘗試指定 ChromeDriver 路徑：`"executable_path": "/path/to/chromedriver"`
3. 更新 Chrome：確保使用最新版本
4. 檢查系統依賴：Linux 系統可能需要額外庫
5. 查看詳細錯誤信息：使用 `--verbose` 參數

## 進階問題

### Q: 如何處理動態生成的內容？
**A:** 處理動態內容的方法：
1. 增加隱式等待時間：設置適當的 `implicit_wait` 值
2. 使用顯式等待：配置特定元素的等待條件
3. 執行 JavaScript：使用 `execute_script` 處理動態內容
4. 監聽 AJAX 請求完成：等待網絡空閒狀態

### Q: 如何處理無限滾動頁面？
**A:** 對於無限滾動的網站：
1. 在模板中設置滾動處理：
```json
{
  "scroll": {
    "enabled": true,
    "max_scrolls": 10,
    "scroll_delay": 2,
    "wait_for_selector": ".item"
  }
}
```

2. 或使用代碼：
```python
def scroll_page(driver, times=5):
    for i in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 等待內容加載
```

### Q: 如何設置定時爬取？
**A:** 使用系統排程器：

**Linux/Mac (cron):**
```bash
# 每天凌晨 3 點執行
0 3 * * * cd /path/to/your/crawler && python main.py -t templates/your_template.json
```

**Windows (Task Scheduler):**
1. 創建批處理文件 `run_crawler.bat`：
```batch
cd C:\path\to\your\crawler
python main.py -t templates/your_template.json
```
2. 使用 Windows 工作排程器設置定時執行

### Q: 如何使用 Docker 部署爬蟲系統？
**A:** 
1. 創建 Dockerfile：
```dockerfile
FROM python:3.9

# 安裝 Chrome 和 ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# 安裝依賴
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# 複製專案文件
COPY . .

# 運行
ENTRYPOINT ["python", "main.py"]
```

2. 建立和運行容器：
```bash
# 建立映像
docker build -t crawler-selenium .

# 運行爬蟲
docker run -v $(pwd)/data:/app/data -v $(pwd)/templates:/app/templates crawler-selenium -t templates/your_template.json
```

### Q: 爬蟲如何處理大型數據集？
**A:**
1. 使用增量爬取：只處理新數據
2. 實施數據分頁：限制每次爬取的數量
3. 優化數據存儲：使用合適的數據庫
4. 定期清理內存：避免內存泄漏
5. 使用異步處理：分離爬取和處理

### Q: 如何避免 IP 被封禁？
**A:**
1. 減慢爬取速度：增加請求間隔
2. 使用代理池：輪換多個 IP 地址
3. 模擬真實用戶行為：添加隨機暫停
4. 遵循 robots.txt 規則：尊重網站限制
5. 分散爬取時間：避免短時間內大量請求

## 整合與擴展問題

### Q: 如何將爬蟲數據導出為 CSV 或 Excel？
**A:** 使用配置或命令行參數：

1. 命令行：
```bash
python main.py -t templates/example.json -o data/output.csv
```

2. 配置文件：
```json
{
  "persistence": {
    "type": "file",
    "format": "excel",
    "path": "data/output.xlsx",
    "options": {
      "sheet_name": "Crawl Results",
      "include_header": true
    }
  }
}
```

3. 代碼方式：
```python
from src.persistence.file_storage import FileStorage

data = crawler.crawl()
storage = FileStorage()
storage.save_as_csv(data, "data/output.csv")
storage.save_as_excel(data, "data/output.xlsx")
```

### Q: 如何擴展爬蟲功能？
**A:** 系統提供多種擴展點：

1. 自定義數據處理器：
```python
from src.core.template_crawler import TemplateCrawler

def custom_processor(data):
    # 處理資料
    return processed_data

crawler = TemplateCrawler(template_file="templates/example.json")
crawler.register_processor("my_processor", custom_processor)
```

2. 自定義驗證碼處理：
```python
from src.captcha.captcha_manager import CaptchaManager

class CustomCaptchaManager(CaptchaManager):
    def solve_captcha(self, image_element):
        # 驗證碼處理邏輯
        return solution

crawler.set_captcha_manager(CustomCaptchaManager())
```

3. 自定義存儲方式：
```python
from src.persistence.data_manager import DataManager

class CustomDataManager(DataManager):
    def save_data(self, data, name):
        # 自定義存儲邏輯
        pass

crawler.set_data_manager(CustomDataManager())
```

### Q: 如何整合到現有系統中？
**A:** 有多種整合方式：

1. 作為模組導入：
```python
from src.core.template_crawler import TemplateCrawler

def get_data_from_website(url, max_items=100):
    crawler = TemplateCrawler(template_file="templates/example.json")
    return crawler.crawl(max_items=max_items)
```

2. 使用 API 模式：
   - 開發一個簡單的 Flask 或 FastAPI 應用
   - 將爬蟲作為後端服務
   - 通過 REST API 調用爬蟲功能

3. 使用消息佇列整合：
   - 爬蟲將結果發送到 RabbitMQ 或 Kafka
   - 其他系統從佇列中消費數據

4. 設置文件監控：
   - 爬蟲將結果保存到指定位置
   - 其他系統監控該位置的文件變化

### Q: 爬蟲失敗後如何重試？
**A:** 使用內建重試機制：

1. 命令行參數：
```bash
python main.py -t templates/example.json -r
```

2. 配置文件：
```json
{
  "error_handling": {
    "max_retries": 3,
    "retry_delay": 5,
    "save_state": true,
    "state_file": "data/crawler_state.json"
  }
}
```

3. 代碼方式：
```python
try:
    data = crawler.crawl()
except Exception as e:
    print(f"爬取失敗: {e}")
    data = crawler.resume_crawl()  # 從中斷點恢復
```

## 故障排除和最佳實踐

### Q: 爬蟲常見錯誤和解決方法？
**A:**

| 錯誤 | 可能原因 | 解決方法 |
|------|---------|---------|
| ElementNotInteractableException | 元素不可見或被遮擋 | 使用 JavaScript 點擊或確保元素在視窗內 |
| NoSuchElementException | 選擇器錯誤或元素未加載 | 檢查選擇器、增加等待時間 |
| StaleElementReferenceException | 頁面已更新，元素不再附加到 DOM | 重新定位元素、使用 WebDriverWait |
| TimeoutException | 元素未在指定時間內出現 | 增加超時設置、檢查選擇器 |
| WebDriverException | WebDriver 問題或瀏覽器崩潰 | 重啟瀏覽器、更新 WebDriver |

### Q: 爬蟲開發最佳實踐有哪些？
**A:**
1. **尊重網站規則**
   - 遵循 robots.txt
   - 設置合理的請求延遲
   - 避免過度抓取

2. **代碼和模板管理**
   - 使模板可重用
   - 避免硬編碼
   - 將敏感數據與代碼分離

3. **穩定性考量**
   - 實施錯誤處理
   - 記錄詳細日誌
   - 定期保存爬取狀態

4. **效能最佳化**
   - 精確定位元素
   - 適度使用等待
   - 釋放不需要的資源

5. **安全性考量**
   - 保護憑證和API金鑰
   - 安全處理和存儲數據
   - 避免在公共環境暴露敏感信息

### Q: 如何持續維護爬蟲？
**A:**
1. **定期檢查**
   - 監控爬蟲日誌
   - 驗證數據質量
   - 檢查爬蟲性能

2. **適應網站變化**
   - 更新選擇器
   - 調整爬取策略
   - 優化反偵測機制

3. **版本控制**
   - 保留模板的歷史版本
   - 文檔變更
   - 設置回滾機制

4. **測試驗證**
   - 建立自動化測試
   - 模擬各種情況
   - 在非生產環境測試

5. **系統升級**
   - 更新依賴庫
   - 升級WebDriver
   - 跟進瀏覽器版本
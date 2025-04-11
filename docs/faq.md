# 爬蟲系統常見問題解答

## 一般問題

### Q: 如何快速開始使用爬蟲系統？
**A:** 快速開始的步驟：
1. 安裝依賴：`pip install -r requirements.txt`
2. 複製範例模板：從 `templates/` 目錄選擇合適的模板
3. 修改配置：根據目標網站調整模板設定
4. 執行爬蟲：`python main.py -t templates/your_template.json`

### Q: 爬蟲系統支援哪些網站？
**A:** 系統理論上支援任何基於 HTML 的網站：
1. 靜態網站：直接使用選擇器提取數據
2. 動態網站：支援 Selenium 處理 JavaScript 渲染的內容
3. 需要登入的網站：支援 Cookie 管理和會話保持
4. 有驗證碼的網站：整合多種驗證碼解決方案

### Q: 如何判斷爬蟲是否正常運作？
**A:** 可以通過以下方式確認：
1. 檢查日誌輸出：查看 `logs/` 目錄下的日誌文件
2. 確認數據輸出：檢查 `data/` 目錄是否生成數據文件
3. 監控進度：觀察控制台輸出的進度信息
4. 驗證數據質量：檢查提取的數據是否符合預期

### Q: 應該選擇哪個瀏覽器？
**A:** 系統支援多種瀏覽器，各有優勢：
1. Chrome：最穩定且功能完整，推薦首選
2. Firefox：較難被檢測，適合需要隱蔽性的場景
3. Edge：Windows 系統整合性好，性能優良
4. 無頭模式：適合不需要視覺反饋的場景

## 配置和模板問題

### Q: 如何處理數據格式轉換？
**A:** 使用數據處理器：
1. 內建處理器：
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

2. 自定義處理器：
```python
def clean_price(value):
    if value:
        return float(value.replace('$', '').replace(',', ''))
    return 0.0

crawler.register_processor('clean_price', clean_price)
```

### Q: 如何過濾不需要的數據？
**A:** 提供多種過濾方式：
1. 模板配置：
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

2. 程式碼過濾：
```python
data = crawler.crawl()
filtered_data = [item for item in data if item.get('price', 0) > 100]
```

### Q: 如何配置數據存儲？
**A:** 支援多種存儲方式：
1. 本地文件：
```json
{
  "persistence": {
    "type": "local",
    "format": "json",
    "path": "data/output.json"
  }
}
```

2. MongoDB：
```json
{
  "persistence": {
    "type": "mongodb",
    "uri": "mongodb://localhost:27017",
    "database": "crawler_data",
    "collection": "items"
  }
}
```

3. Notion：
```json
{
  "persistence": {
    "type": "notion",
    "api_key": "your_api_key",
    "database_id": "your_database_id"
  }
}
```

## 性能和穩定性問題

### Q: 如何優化爬蟲性能？
**A:** 多種優化方法：
1. 調整反偵測設置：
```json
{
  "anti_detection": {
    "random_delay": [1, 2],
    "human_like": false,
    "headless": true
  }
}
```

2. 限制處理數量：使用 `--items <數量>` 參數
3. 禁用不必要的功能：設置 `"disable_images": true`
4. 使用多線程：配置 `"max_workers": 4`
5. 啟用緩存：設置 `"cache_enabled": true`

### Q: 如何提高爬蟲穩定性？
**A:** 改善穩定性的方法：
1. 使用隱身模式：添加 `--stealth` 參數
2. 配置代理：添加 `--proxy http://proxy_ip:port`
3. 模擬真實用戶：設置 `"human_like": true`
4. 隨機化 User-Agent：提供多個選項
5. 增加等待時間：調整 `implicit_wait` 值

### Q: 如何處理驗證碼？
**A:** 系統提供多種驗證碼處理方案：
1. 本地 OCR：
```json
{
  "captcha": {
    "service": "local_ocr",
    "selector": "img.captcha",
    "input_selector": "input[name='captcha']"
  }
}
```

2. 第三方服務：
```json
{
  "captcha": {
    "service": "2captcha",
    "api_key": "YOUR_API_KEY",
    "type": "recaptcha"
  }
}
```

3. 人工處理：
```json
{
  "captcha": {
    "service": "manual",
    "timeout": 300
  }
}
```

### Q: 如何處理反爬蟲機制？
**A:** 進階反爬蟲處理：
1. 隱身模式配置：
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

2. 代理池配置：
```json
{
  "proxy": {
    "type": "pool",
    "urls": [
      "http://proxy1:port",
      "http://proxy2:port"
    ],
    "rotation": "random"
  }
}
```

## 錯誤和調試問題

### Q: 為什麼沒有提取到數據？
**A:** 可能的原因和解決方法：
1. 選擇器問題：驗證選擇器是否正確
2. 網站結構變更：更新選擇器
3. 等待時間不足：增加 `implicit_wait`
4. 被反爬阻擋：檢查是否需要登入或代理

### Q: 如何診斷元素定位問題？
**A:** 診斷步驟：
1. 啟用調試模式：使用 `--debug`
2. 查看詳細日誌：使用 `--verbose`
3. 截圖確認：設置 `"debug": {"screenshot": true}`
4. 使用多種選擇器：同時提供 CSS 和 XPath
5. 檢查動態元素：確認元素是否在 iframe 中

### Q: 如何處理超時問題？
**A:** 解決超時問題：
1. 增加等待時間：調整 `implicit_wait`
2. 使用更精確的選擇器
3. 檢查 iframe：需要先切換 frame
4. 確認頁面加載：添加特定等待條件
5. 檢查網絡連接：確保網絡穩定

### Q: 瀏覽器啟動失敗怎麼辦？
**A:** 故障排除步驟：
1. 檢查版本匹配：Chrome 和 ChromeDriver
2. 指定 ChromeDriver 路徑
3. 更新瀏覽器：確保使用最新版本
4. 檢查系統依賴：Linux 可能需要額外庫
5. 查看詳細錯誤：使用 `--verbose`

## 進階問題

### Q: 如何處理動態內容？
**A:** 動態內容處理方法：
1. 增加隱式等待：設置 `implicit_wait`
2. 使用顯式等待：配置特定元素等待條件
3. 執行 JavaScript：使用 `execute_script`
4. 監聽 AJAX 請求：等待網絡空閒

### Q: 如何處理無限滾動？
**A:** 無限滾動處理：
1. 模板配置：
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

2. 程式碼實現：
```python
def scroll_page(driver, times=5):
    for i in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
```

### Q: 如何設置定時爬取？
**A:** 定時任務設置：

**Linux/Mac (cron):**
```bash
0 3 * * * cd /path/to/crawler && python main.py -t templates/your_template.json
```

**Windows (Task Scheduler):**
```batch
cd C:\path\to\crawler
python main.py -t templates/your_template.json
```

### Q: 如何使用 Docker 部署？
**A:** Docker 部署步驟：
1. 建立 Dockerfile：
```dockerfile
FROM python:3.9

# 安裝 Chrome 和依賴
RUN apt-get update && apt-get install -y \
    wget gnupg unzip xvfb libxi6 libgconf-2-4 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# 設置工作目錄
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# 運行
ENTRYPOINT ["python", "main.py"]
```

2. 運行容器：
```bash
docker build -t crawler-selenium .
docker run -v $(pwd)/data:/app/data -v $(pwd)/templates:/app/templates crawler-selenium -t templates/your_template.json
```

### Q: 如何處理大型數據集？
**A:** 大型數據處理策略：
1. 增量爬取：只處理新數據
2. 數據分頁：限制每次爬取數量
3. 優化存儲：使用合適的數據庫
4. 定期清理：避免內存泄漏
5. 異步處理：分離爬取和處理

### Q: 如何避免 IP 被封？
**A:** IP 保護策略：
1. 控制爬取速度：增加請求間隔
2. 使用代理池：輪換多個 IP
3. 模擬真實用戶：添加隨機暫停
4. 遵循 robots.txt：尊重網站限制
5. 分散爬取時間：避免短時間大量請求

## 整合與擴展問題

### Q: 如何導出數據？
**A:** 多種導出方式：
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
    "path": "data/output.xlsx"
  }
}
```

3. 程式碼方式：
```python
from src.persistence.file_storage import FileStorage

data = crawler.crawl()
storage = FileStorage()
storage.save_as_csv(data, "data/output.csv")
```

### Q: 如何擴展功能？
**A:** 系統擴展點：
1. 自定義處理器：
```python
def custom_processor(data):
    return processed_data

crawler.register_processor("my_processor", custom_processor)
```

2. 自定義驗證碼處理：
```python
class CustomCaptchaManager(CaptchaManager):
    def solve_captcha(self, image_element):
        return solution

crawler.set_captcha_manager(CustomCaptchaManager())
```

3. 自定義存儲：
```python
class CustomDataManager(DataManager):
    def save_data(self, data, name):
        pass

crawler.set_data_manager(CustomDataManager())
```

### Q: 如何整合到現有系統？
**A:** 整合方式：
1. 模組導入：
```python
from src.core.template_crawler import TemplateCrawler

def get_data_from_website(url, max_items=100):
    crawler = TemplateCrawler(template_file="templates/example.json")
    return crawler.crawl(max_items=max_items)
```

2. API 模式：
   - 開發 Flask/FastAPI 應用
   - 將爬蟲作為後端服務
   - 通過 REST API 調用

3. 消息佇列：
   - 爬蟲發送到 RabbitMQ/Kafka
   - 其他系統消費數據

4. 文件監控：
   - 爬蟲保存到指定位置
   - 其他系統監控文件變化

### Q: 如何處理爬蟲失敗？
**A:** 失敗處理機制：
1. 命令行重試：
```bash
python main.py -t templates/example.json -r
```

2. 配置文件：
```json
{
  "error_handling": {
    "max_retries": 3,
    "retry_delay": 5,
    "save_state": true
  }
}
```

3. 程式碼處理：
```python
try:
    data = crawler.crawl()
except Exception as e:
    print(f"爬取失敗: {e}")
    data = crawler.resume_crawl()
```

## 故障排除和最佳實踐

### Q: 常見錯誤和解決方法？
**A:** 錯誤處理指南：

| 錯誤 | 可能原因 | 解決方法 |
|------|---------|---------|
| ElementNotInteractableException | 元素不可見或被遮擋 | 使用 JavaScript 點擊或確保元素在視窗內 |
| NoSuchElementException | 選擇器錯誤或元素未加載 | 檢查選擇器、增加等待時間 |
| StaleElementReferenceException | 頁面已更新，元素不再附加到 DOM | 重新定位元素、使用 WebDriverWait |
| TimeoutException | 元素未在指定時間內出現 | 增加超時設置、檢查選擇器 |
| WebDriverException | WebDriver 問題或瀏覽器崩潰 | 重啟瀏覽器、更新 WebDriver |

### Q: 爬蟲開發最佳實踐？
**A:** 最佳實踐指南：
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
**A:** 維護指南：
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

## 常見問題

## 概述

本文檔提供系統使用過程中常見問題的解答。

## 安裝問題

### 1. 無法安裝依賴套件

**問題**：在安裝依賴套件時出現錯誤。

**解決方案**：
- 確保 Python 和 pip 版本正確。
- 檢查網絡連接。
- 嘗試使用 `--no-cache-dir` 選項：
  ```bash
  pip install -r requirements.txt --no-cache-dir
  ```

### 2. 安裝腳本執行失敗

**問題**：運行 `setup.py` 時出現錯誤。

**解決方案**：
- 檢查 Python 環境變數設置。
- 確保所有依賴套件已正確安裝。
- 查看日誌文件以獲取詳細錯誤信息。

## 配置問題

### 1. 配置文件無法載入

**問題**：系統無法載入配置文件。

**解決方案**：
- 確保配置文件路徑正確。
- 檢查配置文件格式是否正確。
- 使用 `ConfigUtils` 的 `load_config` 方法載入配置。

### 2. 配置參數無效

**問題**：配置參數不符合預期。

**解決方案**：
- 檢查配置文件中的參數名稱和類型。
- 使用 `ValidationUtils` 驗證配置參數。

## 運行問題

### 1. 主程序無法啟動

**問題**：運行 `main.py` 時出現錯誤。

**解決方案**：
- 檢查日誌文件以獲取詳細錯誤信息。
- 確保所有依賴服務（如數據庫）已啟動。
- 檢查環境變數設置。

### 2. 腳本執行失敗

**問題**：運行腳本時出現錯誤。

**解決方案**：
- 檢查腳本路徑和參數。
- 查看日誌文件以獲取詳細錯誤信息。
- 確保所有依賴套件已正確安裝。

## 測試問題

### 1. 測試無法運行

**問題**：運行測試時出現錯誤。

**解決方案**：
- 確保 `pytest` 已正確安裝。
- 檢查測試文件路徑和名稱。
- 查看日誌文件以獲取詳細錯誤信息。

### 2. 測試報告生成失敗

**問題**：無法生成測試報告。

**解決方案**：
- 確保 `pytest-cov` 已正確安裝。
- 檢查報告生成路徑和權限。
- 使用 `TestUtils` 的 `generate_report` 方法生成報告。

## 錯誤處理問題

### 1. 錯誤未被正確記錄

**問題**：系統錯誤未被記錄到日誌文件。

**解決方案**：
- 確保 `Logger` 已正確配置。
- 檢查日誌文件路徑和權限。
- 使用 `ErrorHandler` 處理和記錄錯誤。

### 2. 錯誤狀態未被更新

**問題**：錯誤狀態未被正確更新。

**解決方案**：
- 使用 `_update_status` 方法更新錯誤狀態。
- 檢查狀態更新邏輯。

## 日誌記錄問題

### 1. 日誌文件無法寫入

**問題**：無法寫入日誌文件。

**解決方案**：
- 檢查日誌文件路徑和權限。
- 確保 `Logger` 已正確配置。
- 檢查磁盤空間。

### 2. 日誌級別設置不正確

**問題**：日誌級別不符合預期。

**解決方案**：
- 檢查 `logging.json` 配置文件中的日誌級別設置。
- 使用 `Logger` 的 `setLevel` 方法設置日誌級別。

## 備份和恢復問題

### 1. 備份創建失敗

**問題**：無法創建數據備份。

**解決方案**：
- 檢查備份路徑和權限。
- 使用 `StorageHandler` 的 `create_backup` 方法創建備份。
- 查看日誌文件以獲取詳細錯誤信息。

### 2. 備份恢復失敗

**問題**：無法恢復數據備份。

**解決方案**：
- 檢查備份文件路徑和權限。
- 使用 `StorageHandler` 的 `restore_backup` 方法恢復備份。
- 查看日誌文件以獲取詳細錯誤信息。
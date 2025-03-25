# 爬蟲系統常見問題 (FAQ)

## 一般問題

### Q: 如何快速開始使用這個爬蟲系統？
**A:** 最快的入門方式是：
1. 安裝依賴套件 `pip install -r requirements.txt`
2. 複製範例模板 `templates/example.json` 並按需修改
3. 執行 `python main.py --template templates/your_template.json`

### Q: 這個爬蟲系統支援哪些網站？
**A:** 理論上支援任何基於 HTML 的網站。由於使用了 Selenium，即使是動態加載的內容也能爬取。不過，需要為每個網站創建對應的 JSON 模板。

### Q: 如何判斷我的爬蟲是否成功運行？
**A:** 檢查以下幾點：
1. 日誌文件中有 "爬蟲任務完成" 的記錄
2. 數據文件已生成並包含預期的數據
3. 任務管理器中該任務狀態為 "completed"

## 模板配置問題

### Q: 如何找到正確的 XPath？
**A:** 您可以使用瀏覽器的開發者工具：
1. 右鍵點擊目標元素，選擇 "檢查" 或 "Inspect"
2. 在元素上右鍵點擊，選擇 "Copy" > "Copy XPath"
3. 對於複雜頁面，可使用 XPath Helper 或 ChroPath 等瀏覽器擴展

### Q: 分頁機制不工作，怎麼辦？
**A:** 常見原因有：
1. `next_button_xpath` 不正確，確認下一頁按鈕的 XPath
2. 網站使用 AJAX 加載，嘗試切換到 `"type": "parameter"` 分頁方式
3. 增加 `wait_after_pagination` 的時間，給頁面更多加載時間

### Q: 如何處理需要登入的網站？
**A:** 在模板中添加登入配置：
```json
{
  "login": {
    "required": true,
    "url": "https://example.com/login",
    "username_xpath": "//input[@id='username']",
    "password_xpath": "//input[@id='password']",
    "submit_xpath": "//button[@type='submit']",
    "success_xpath": "//div[@class='user-info']"
  }
}
```
然後在憑證文件中添加登入信息。

### Q: 如何處理彈出視窗或警告？
**A:** 在模板中添加彈窗處理配置：
```json
{
  "popup_handling": {
    "enabled": true,
    "accept_alert": true,
    "close_button_xpath": "//button[@class='close']",
    "cookie_consent_xpath": "//button[contains(text(), 'Accept')]"
  }
}
```

## 資料處理問題

### Q: 爬取的數據格式不正確，如何轉換？
**A:** 使用數據轉換配置：
```json
{
  "data_transformations": {
    "price": {
      "type": "number",
      "regex": "(\\d+[,\\d]*\\.?\\d*)",
      "remove_commas": true
    },
    "publish_date": {
      "type": "date",
      "format": "yyyy-MM-dd"
    }
  }
}
```

### Q: 如何過濾不需要的數據？
**A:** 在模板中添加過濾規則：
```json
{
  "data_filtering": {
    "include_only": {
      "tender_type": ["公開招標", "限制性招標"]
    },
    "exclude": {
      "budget": "0"
    }
  }
}
```

### Q: MongoDB 中如何查詢保存的數據？
**A:** 使用 MongoDB 查詢語法：
```javascript
// 連接到數據庫
use web_crawler
// 查詢所有採購項目
db.procurement_items.find({})
// 查詢特定機關的採購項目
db.procurement_items.find({"org_name": "臺北市政府"})
// 查詢預算大於 100 萬的項目
db.procurement_items.find({"budget": {$gt: 1000000}})
```

## 性能和穩定性問題

### Q: 爬蟲執行太慢，如何優化？
**A:** 可以嘗試以下方法：
1. 減少延遲時間：調整 `delays` 配置
2. 關閉人類行為模擬：設置 `"human_simulation": {"enabled": false}`
3. 限制詳情頁處理數量：使用 `--max-items` 參數
4. 啟用並行處理：在配置中設置 `"parallel_processing": {"enabled": true, "max_workers": 4}`

### Q: 爬蟲經常被中斷，如何提高穩定性？
**A:** 改善穩定性的方法：
1. 增加重試次數：調整 `retry_config.max_retries`
2. 使用代理服務器：配置 `proxy` 設置
3. 隨機化 User-Agent：啟用 `"random_user_agent": true`
4. 定期保存進度：減少 `checkpoint_interval`
5. 增加超時時間：調整 `wait_for.timeout` 值

### Q: 如何處理驗證碼問題？
**A:** 對於簡單驗證碼，可以使用 OCR 解決：
```json
{
  "captcha_handling": {
    "enabled": true,
    "captcha_xpath": "//img[@class='captcha']",
    "input_xpath": "//input[@name='captcha']",
    "use_ocr": true,
    "ocr_service": "tesseract",
    "wait_time": 5
  }
}
```
對於複雜驗證碼，可能需要人工干預或使用專業驗證碼解決服務。

### Q: 如何處理複雜的反爬蟲機制？
**A:** 針對進階的反爬蟲機制，可以：
1. 模擬視窗操作：配置 `window_operations`
2. 隨機化滾動行為：設置 `scroll_behavior`
3. 模擬滑鼠移動：啟用 `mouse_movement`
4. 模擬鍵盤輸入：設置 `keyboard_simulation`

範例配置：
```json
{
  "anti_detection": {
    "window_operations": {
      "enabled": true,
      "actions": [
        {
          "type": "resize",
          "width_range": [1024, 1920],
          "height_range": [768, 1080],
          "frequency": 0.1
        },
        {
          "type": "switch_tab",
          "probability": 0.05
        }
      ]
    },
    "scroll_behavior": {
      "enabled": true,
      "mode": "natural",
      "speed_range": [100, 300],
      "pause_range": [1, 3]
    }
  }
}
```

## 整合問題

### Q: 如何將爬蟲數據導出為 CSV 或 Excel？
**A:** 在數據持久化配置中設置：
```json
{
  "local_storage": {
    "enabled": true,
    "formats": ["json", "csv", "excel"],
    "excel_config": {
      "sheet_name": "爬蟲數據",
      "include_header": true
    }
  }
}
```
然後系統會自動生成多種格式的數據文件。

### Q: 如何設置定時爬取？
**A:** 使用 cron 或系統排程器：

**Linux/Mac (cron):**
```bash
# 每天凌晨 3 點執行
0 3 * * * cd /path/to/your/crawler && python main.py --template templates/your_template.json
```

**Windows (Task Scheduler):**
1. 創建批處理文件 `run_crawler.bat`：
```batch
cd C:\path\to\your\crawler
python main.py --template templates/your_template.json
```
2. 使用 Windows 工作排程器設置定時執行

### Q: 如何使用 Docker 部署爬蟲系統？
**A:** 使用提供的 Dockerfile：
```bash
# 建立映像
docker build -t crawler-system .

# 執行爬蟲
docker run -v $(pwd)/data:/app/data -v $(pwd)/templates:/app/templates crawler-system --template templates/your_template.json
```

## 故障排除

### Q: 為什麼爬蟲沒有提取到任何數據？
**A:** 可能的原因：
1. XPath 不正確：驗證選擇器是否還能匹配目標元素
2. 網站結構變更：檢查網站是否更新了 HTML 結構
3. 等待時間不足：增加 `wait_for.timeout` 值
4. 被反爬機制阻擋：檢查是否需要模擬登入或使用代理

### Q: 為什麼 Notion 整合失敗？
**A:** 常見問題：
1. API 令牌無效：確認 `credentials.json` 中的 `notion.api_key` 是否正確
2. 數據庫 ID 錯誤：檢查 `notion.database_id` 是否正確
3. 字段映射問題：確認 Notion 數據庫中已創建了對應的屬性
4. 權限問題：確保 API 令牌具有對該數據庫的寫入權限

### Q: 日誌中顯示 "TimeoutException"，如何解決？
**A:** 解決超時問題：
1. 增加等待時間：調整相關的 `timeout` 值
2. 檢查網絡連接：確保網絡穩定
3. 減少網站負載：調整請求頻率，增加延遲時間
4. 使用更具體的等待條件：調整 `wait_for` 的 XPath

### Q: 爬蟲在處理大量數據時內存溢出，如何解決？
**A:** 內存優化方法：
1. 啟用增量處理：設置 `"incremental_processing": true`
2. 減少批處理大小：調整 `batch_size` 參數
3. 定期釋放內存：設置 `"memory_optimization": {"enabled": true, "gc_interval": 100}`
4. 限制爬取數量：使用 `--max-items` 和 `--max-pages` 參數

### Q: 如何除錯爬蟲程式？
**A:** 除錯建議：
1. 開啟詳細日誌：設置 `"logging": {"level": "DEBUG"}`
2. 使用視覺化除錯：設置 `"debug_mode": {"enabled": true, "screenshot": true}`
3. 檢查網路請求：使用瀏覽器開發者工具的網路面板
4. 單步執行：使用 `--debug` 參數啟動爬蟲

### Q: 如何處理動態生成的內容？
**A:** 處理動態內容的方法：
1. 增加等待時間：設置適當的 `wait_for.timeout`
2. 使用動態等待：配置 `wait_for.condition` 為特定元素出現
3. 監聽 AJAX 請求：啟用 `"ajax_monitoring": true`
4. 使用 JavaScript 執行器：通過 `execute_script` 處理

### Q: 系統資源使用過高怎麼辦？
**A:** 優化資源使用：
1. 限制同時開啟的瀏覽器數：調整 `max_concurrent_browsers`
2. 定期關閉瀏覽器：設置 `"browser_cleanup": {"interval": 10}`
3. 使用無頭模式：設置 `"headless": true`
4. 禁用不必要的功能：如圖片載入、JavaScript 執行等

### Q: 如何整合到現有的系統中？
**A:** 整合方式：
1. 使用 API 模式：啟用 `"api_mode": {"enabled": true, "port": 5000}`
2. 監聽事件：訂閱 `crawler_events` 進行處理
3. 使用訊息佇列：配置 `message_queue` 進行非同步處理
4. 實作回調介面：設置 `callback_url` 接收結果
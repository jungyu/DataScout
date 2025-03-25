# 爬蟲 JSON 模板測試與調試指南

開發新的爬蟲模板或修改現有模板時，良好的測試和調試策略可以大幅提高效率。本指南介紹如何測試和調試爬蟲 JSON 模板。

## 目錄
- [模板語法檢查](#模板語法檢查)
- [XPath 選擇器測試](#xpath-選擇器測試)
- [模板段落測試](#模板段落測試)
- [調試模式運行](#調試模式運行)
- [常見錯誤修復](#常見錯誤修復)
- [性能優化](#性能優化)

## 模板語法檢查

在開始測試爬蟲功能前，先確保 JSON 模板語法正確：

### 使用內置檢查工具

```bash
python validate_template.py templates/your_template.json
```

### 使用 JSON Schema 驗證

```bash
pip install jsonschema
python validate_schema.py templates/your_template.json schema/crawler_template_schema.json
```

### 常見語法錯誤

1. **缺少逗號或多餘逗號**：JSON 中每個鍵值對後面需要逗號，但最後一個不需要
2. **引號問題**：JSON 中字符串必須使用雙引號 `"` 而非單引號 `'`
3. **註釋問題**：標準 JSON 不支持註釋，請移除所有註釋

## XPath 選擇器測試

XPath 是爬蟲模板中最容易出錯的部分，專門測試 XPath 可以節省大量時間：

### 使用 XPath 測試工具

```bash
python test_xpath.py --url "https://example.com" --xpath "//div[@class='product']"
```

### 常見 XPath 問題

1. **絕對路徑與相對路徑**：
   - 絕對路徑以 `/` 開頭 (如 `/html/body/div`)
   - 相對路徑不以 `/` 開頭 (如 `./div` 或 `div`)

2. **屬性選擇器**：
   - 精確匹配：`[@class='product']`
   - 部分匹配：`[contains(@class, 'product')]`

3. **索引問題**：
   - XPath 索引從 1 開始，如 `//table[1]` 是第一個表格
   - CSS 選擇器索引從 0 開始，請注意區分

### 調試 XPath 技巧

1. **使用瀏覽器開發者工具**：
   - 在 Chrome 中，右鍵檢查元素，在 Console 中測試 XPath：
   ```javascript
   $x("//your/xpath/here")
   ```

2. **逐步簡化 XPath**：
   如果 `//div[@id='content']/table/tbody/tr[3]/td[2]` 不工作，逐步簡化：
   - 先測試 `//div[@id='content']`
   - 然後 `//div[@id='content']/table`
   - 依此類推

3. **使用通配符和函數**：
   - `//table//td` 選擇任何表格中的任何單元格，不管嵌套多少層
   - `//td[contains(text(), '價格')]` 選擇包含 "價格" 文本的單元格
   - `//td[text()='價格']/following-sibling::td[1]` 選擇後續的第一個兄弟元素

## 模板段落測試

爬蟲模板包含多個功能段落，可以分段測試：

### 1. 列表頁測試

使用以下命令僅測試列表頁爬取功能：

```bash
python test_crawler.py --template templates/your_template.json --test-section list_page
```

這會執行爬蟲但只爬取列表頁，並輸出提取到的數據以供檢查。

### 2. 分頁測試

測試分頁功能：

```bash
python test_crawler.py --template templates/your_template.json --test-section pagination --max-pages 3
```

這會嘗試遍歷 3 頁並檢查分頁是否正常工作。

### 3. 詳情頁測試

針對特定詳情頁 URL 進行測試：

```bash
python test_crawler.py --template templates/your_template.json --test-section detail_page --url "https://example.com/item/123"
```

這會直接爬取指定的詳情頁並顯示結果。

## 調試模式運行

啟用調試模式可以獲得更多信息和可視化結果：

### 1. 啟用詳細日誌

```bash
python main.py --template templates/your_template.json --verbose --debug
```

這會輸出詳細的日誌信息，包括每一步操作和數據提取結果。

### 2. 可視化運行

```bash
python main.py --template templates/your_template.json --headless false --screenshot
```

這會在非無頭模式下運行，你可以看到瀏覽器操作，並生成截圖。

### 3. 慢速模式

```bash
python main.py --template templates/your_template.json --slow-mode
```

這會增加所有延遲時間，便於觀察爬蟲行為。

### 4. 生成元素標記版截圖

```bash
python debug_crawler.py --template templates/your_template.json --highlight-elements
```

這會生成包含元素高亮標記的截圖，幫助確認 XPath 選擇的是否是預期元素。

## 常見錯誤修復

### 1. 無法找到元素

如果日誌顯示 "Element not found" 或類似錯誤：

1. **檢查 XPath**：
   - 確認 XPath 是否正確
   - 網站可能已更新結構

2. **增加等待時間**：
   ```json
   "wait_for": {"xpath": "//your/element", "timeout": 30}
   ```

3. **檢查框架**：
   - 如果元素在 iframe 中，需要先切換到框架：
   ```json
   "frames": {
     "switch_to": "//iframe[@id='content']"
   }
   ```

### 2. 分頁問題

如果分頁不工作：

1. **檢查分頁類型**：
   - 嘗試切換 `"type"` 從 `"link_click"` 到 `"parameter"`

2. **動態加載內容**：
   - 添加滾動操作：
   ```json
   "pagination": {
     "scroll_before_next": true,
     "scroll_to": "bottom"
   }
   ```

3. **禁用 JavaScript**：
   某些情況下動態分頁可能受 JavaScript 影響：
   ```json
   "browser": {
     "disable_javascript": true
   }
   ```

### 3. 數據提取不完整

如果僅獲取部分數據：

1. **檢查條件提取**：
   - 某些元素可能是條件出現的
   ```json
   "fields": {
     "price": {
       "xpath": "//span[@class='price']",
       "optional": true,
       "default": "0"
     }
   }
   ```

2. **處理多種格式**：
   - 使用多個 XPath：
   ```json
   "fields": {
     "price": {
       "xpaths": [
         "//div[@class='new-price']/span",
         "//span[@class='regular-price']",
         "//div[@class='price-box']//span[@class='price']"
       ]
     }
   }
   ```

## 性能優化

在確保爬蟲正常工作後，可以進行性能優化：

### 1. 減少等待時間

調整延遲時間到安全的最小值：

```json
"delays": {
  "page_load": {"min": 1.5, "max": 3},
  "between_pages": {"min": 2, "max": 4},
  "between_items": {"min": 1, "max": 2}
}
```

### 2. 選擇性爬取

只爬取需要的頁面和數據：

```json
"data_filtering": {
  "list_filter": "//tr[contains(@class, 'important')]",
  "detail_condition": "count(//div[@class='specifications']) > 0"
}
```

### 3. 並行處理

啟用並行處理詳情頁：

```json
"parallel_processing": {
  "enabled": true,
  "max_workers": 4,
  "mode": "detail_pages_only"
}
```

### 4. 緩存機制

啟用緩存避免重複爬取：

```json
"caching": {
  "enabled": true,
  "ttl_hours": 24,
  "cache_dir": "cache",
  "check_modified": true
}
```

## 進階調試技巧

### 1. 模擬 API 調用

有些網站使用 AJAX/API 獲取數據，可以直接模擬 API 調用：

```json
"api_mode": {
  "enabled": true,
  "url": "https://example.com/api/products",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest"
  },
  "data": {
    "page": "{page_number}",
    "category": "electronics"
  },
  "response_type": "json",
  "data_path": "response.items"
}
```

### 2. 動態 CSS 選擇器

有時 CSS 選擇器比 XPath 更簡潔：

```json
"list_page": {
  "selector_mode": "css",
  "container_selector": ".product-list",
  "item_selector": ".product-item",
  "fields": {
    "title": {
      "selector": ".product-title",
      "type": "text"
    }
  }
}
```

### 3. 自定義腳本

對於複雜情況，可以使用自定義 JavaScript：

```json
"custom_scripts": {
  "before_extract": "window.scrollTo(0, document.body.scrollHeight); return true;",
  "process_data": "return items.filter(i => parseFloat(i.price) > 100);"
}
```

## 模板版本控制

當您修改和優化模板時，保持版本控制非常重要：

```json
{
  "metadata": {
    "version": "1.2.3",
    "last_updated": "2023-12-15",
    "author": "Your Name",
    "change_log": [
      {"version": "1.2.3", "date": "2023-12-15", "changes": ["修正分頁問題", "優化詳情頁提取"]},
      {"version": "1.2.2", "date": "2023-12-10", "changes": ["添加新字段", "增加錯誤處理"]}
    ]
  }
}
```

通過這種方式，您可以跟踪模板的變更歷史，並在需要時回滾到先前的版本。
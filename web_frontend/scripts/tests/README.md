# Web Frontend 測試腳本

這個目錄包含了用於測試 DataScout Web 前端功能的各種測試腳本。

## 測試腳本說明

### comprehensive_chart_test.py
完整的圖表功能測試腳本，測試新建立的圖表頁面是否能正確載入資料並渲染圖表。

**功能**：
- 使用 Selenium 測試圖表載入
- 測試 data-loader.js 功能
- 生成完整測試報告

**使用方式**：
```bash
cd /Users/aaron/Projects/DataScout/web_frontend
python scripts/tests/comprehensive_chart_test.py
```

### final_chart_test.py
最終圖表功能測試腳本，測試所有修復後的圖表頁面。

**功能**：
- 測試開發服務器可用性
- 驗證所有圖表頁面可訪問性
- 檢查 JSON 範例檔案完整性

### simple_chart_test.py
簡化版圖表功能測試腳本，專注於核心功能測試。

### test_chart_loading.py
圖表資料載入測試腳本，驗證每個圖表頁面是否能正確從 index.json 載入對應的範例資料。

### test_new_chart_pages.py
測試新建立的圖表頁面功能，檢查頁面是否能正確載入和渲染圖表。

## 執行所有測試

```bash
# 確保前端開發服務器正在運行
cd /Users/aaron/Projects/DataScout/web_frontend
npm run dev

# 在另一個終端視窗執行測試
python scripts/tests/comprehensive_chart_test.py
```

## 測試要求

- 需要安裝 `requests` 套件
- 如需進行 Selenium 測試，需要安裝 `selenium` 和 Chrome WebDriver
- 測試前請確保前端開發服務器 (http://localhost:5173) 正在運行

## 注意事項

- 某些測試可能需要較長時間執行
- 建議在穩定的網絡環境下進行測試
- 測試結果會保存在相應的報告檔案中

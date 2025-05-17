# DataScout Chart App JavaScript 程式碼

本目錄包含 DataScout Chart App 的前端 JavaScript 程式碼。

## 檔案說明

* `main.js` - 應用程式的主要入口點，處理頁面初始化、事件監聽和使用者互動
* `utils.js` - 通用工具函數，提供錯誤處理、訊息顯示和資料獲取等功能
* `chart-helpers.js` - 圖表相關輔助函數，處理圖表資料的準備和轉換
* `chart-renderer.js` - 負責圖表的創建、渲染和更新
* `data-exporter.js` - 提供將圖表資料匯出為 CSV、JSON 和 Excel 格式的功能
* `theme-handler.js` - 處理圖表主題和頁面主題的同步
* `file-handler.js` - 處理檔案上傳、解析和管理
* `example-loader.js` - 載入示例圖表和資料
* `chart-date-adapter.js` - Chart.js 日期適配器，提供時間軸處理功能
* `candlestick-helper.js` - 蠟燭圖專用的輔助函數
* `chart-themes.js` - 定義和管理圖表主題
* `json-validator.js` - 驗證和修復 JSON 資料格式
* `example-functions.js` - 提供示例圖表功能
* `example-loader-functions.js` - 範例資料載入器的輔助函數
* `chart-fix.js` - 修復特殊圖表類型的渲染問題，在 HTML 中直接引用

## 已移除冗餘檔案

* `chart-fallback.js` - 原為圖表降級處理模組，已移至 `/tests/js/` 目錄
* `chart-test.js` - 原為測試特定圖表功能的程式碼，已移除（參考不存在）
* `temp-code.js` - 臨時程式碼，已不存在

## 建置資訊

主要 JavaScript 檔案通過 webpack 打包，入口點為：
* `main.js` - 主應用程式邏輯
* `chart-date-adapter.js` - 日期時間處理適配器

部分檔案（如 `chart-fix.js`）直接從 `src/js` 複製到 `static/js` 並通過 HTML 的 script 標籤引用。

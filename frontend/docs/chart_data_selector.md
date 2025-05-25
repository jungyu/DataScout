# 圖表數據選擇器組件使用指南

本文檔提供了關於 `ChartDataSelector` 組件的使用指南，包括如何在不同圖表類型中使用它，以及如何整合自定義數據。

## 組件概述

`ChartDataSelector` 是一個可重複使用的組件，負責處理圖表數據的選擇。它支援以下功能：

- 根據圖表類型顯示不同的數據選項
- 點擊加載按鈕從 JSON 文件加載數據
- 切換開關以選擇使用範例數據或上傳自定義數據
- 支援用戶上傳自定義數據文件

## 支援的圖表類型

目前，`ChartDataSelector` 組件支援以下圖表類型：

1. **折線圖 (Line Chart)**
2. **區域圖 (Area Chart)**
3. **柱狀圖 (Column Chart)**
4. **蠟燭圖 (Candlestick Chart)**

## 如何在頁面中使用

要在頁面中使用 `ChartDataSelector` 組件，只需添加以下 HTML 代碼：

```html
<div class="col-span-1" data-component="components/ui/ChartDataSelector.html"></div>
```

此外，還需確保以下腳本被引入頁面：

```html
<script src="/chart-data-loader.js" defer></script>
<script src="/example-toggle.js" defer></script>
<script src="/file-upload-handler.js" defer></script>
```

## 組件結構

`ChartDataSelector.html` 組件由以下部分組成：

1. **頂部標題和切換開關**
   - 標題："範例數據"
   - 切換開關：用於切換顯示範例數據或上傳自定義數據

2. **不同圖表類型的數據選項**
   - 每個圖表類型都有對應的數據選項區塊
   - 使用 `data-chart-type` 屬性標記不同類型的數據選項
   - 使用 CSS 類（例如 `.line-chart-data`）組織不同類型的數據

3. **文件上傳區域**
   - 支援拖放上傳
   - 支援 CSV、JSON 和 Excel 文件格式

## 數據加載流程

當用戶點擊"點擊載入"按鈕時，系統會執行以下步驟：

1. 根據數據項 ID 確定要載入的 JSON 文件路徑
2. 使用 `fetch` API 加載 JSON 數據
3. 根據當前圖表類型創建適當的圖表選項
4. 渲染圖表並顯示通知消息

## 自定義數據格式

上傳的自定義數據應遵循 ApexCharts 的數據格式。基本格式如下：

```json
{
  "series": [
    {
      "name": "系列名稱",
      "data": [數據點數組]
    }
  ],
  "categories": ["類別1", "類別2", "類別3", ...]
}
```

不同圖表類型可能需要不同的數據格式：

- **折線圖/區域圖**：需要 `series` 和 `categories` 或 `xaxis`
- **柱狀圖**：需要 `series` 和 `categories`
- **蠟燭圖**：需要 OHLC (Open-High-Low-Close) 格式的數據

## 與後端 API 整合

要從 FastAPI 後端 API 加載數據，可以修改 `chart-data-loader.js` 中的數據加載邏輯：

```javascript
// 從API加載數據範例
fetch('/api/charts/data?type=' + chartType + '&source=' + sourceId)
  .then(response => response.json())
  .then(data => {
    initChart(chartType, data, sourceId);
  })
  .catch(error => {
    console.error('載入API數據失敗:', error);
  });
```

## 擴展支持更多圖表類型

要添加新的圖表類型支持，需要：

1. 在 `ChartDataSelector.html` 中添加新的數據選項區塊
2. 在 `chart-data-loader.js` 中添加新圖表類型的初始化函數
3. 更新頁面檢測邏輯以識別新的圖表類型
4. 創建對應的圖表內容組件和HTML頁面

## 故障排除

常見問題和解決方案：

1. **圖表不顯示數據**
   - 確認 JSON 文件格式正確
   - 檢查控制台是否有錯誤消息
   - 確認圖表容器 ID 正確

2. **數據選項不顯示**
   - 確認 `ChartDataSelector.html` 已正確加載
   - 檢查當前頁面路徑是否能正確識別圖表類型

3. **切換開關不工作**
   - 確認 `example-toggle.js` 已正確加載
   - 檢查元素 ID 是否匹配

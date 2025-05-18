# index.js 文件導出順序指南

## 概述
本文檔詳細說明了 `index.js` 文件中模組導出的順序安排及其背後的設計原因。正確的導出順序對於避免命名衝突和確保模組正確加載至關重要。

## 當前導出順序

`index.js` 中的模組導出按以下順序排列：

1. **工具模組** (避免被其他模組覆寫同名函數)
   - `chart-themes.js`
   - `utils.js`
   - `theme-handler.js`
   - `dependency-checker.js`
   - `file-handler.js`
   - `json-validator.js`

2. **核心模組**
   - `app-initializer.js`
   - `state-manager.js`
   - `ui-controller.js`
   - `chart-manager.js`

3. **資料處理模組**
   - `data-loader.js`
   - `data-processor.js`
   - `data-exporter.js`
   - `examples/index.js` (整合後的範例模組)

4. **轉接器模組**
   - `chart-type-adapters.js`
   - `chart-renderer.js`
   - `chart-date-adapter.js`
   - `chart-fix.js`
   - `candlestick-helper.js`
   - 選擇性匯入的 `chart-helpers.js` 函數

5. **主入口模組**
   - `main.js`

## 排序原理

這種排序方式基於以下考量：

1. **依賴關係**：較底層的工具模組先導出，確保其他依賴它們的模組可以正確使用這些函數。

2. **命名衝突處理**：某些模組（如 `utils.js` 和 `chart-helpers.js`）可能包含同名函數。透過優先導出 `utils.js` 並有選擇地導出 `chart-helpers.js` 的特定函數，我們避免了衝突。

3. **可預測性**：按照功能分層導出幫助開發者更容易理解和預測模組間的關係。

4. **最小化打破變更**：此排序方式設計為最小化對現有代碼的影響，同時修復潛在的衝突問題。

## 導出方法

對於大多數模組，我們使用 `export *` 來重新導出所有導出的成員。但對於可能引起命名衝突的模組，我們使用選擇性導出：

```javascript
// 選擇性匯入 chart-helpers.js 中的函數，避免命名衝突
import { showChartLegend, createChartTooltip } from './adapters/chart-helpers.js';
export { showChartLegend, createChartTooltip };
```

## 注意事項

1. 修改導出順序時要格外小心，因為這可能會導致微妙的命名衝突問題。
2. 添加新模組時，應遵循上述分層結構並考慮潛在的命名衝突。
3. 如有疑問，使用選擇性導出而非通配符導出 (`export *`)。

## 最後更新
2025年5月19日

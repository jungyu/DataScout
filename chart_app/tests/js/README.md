# DataScout Chart App 測試程式碼

此目錄包含 DataScout Chart App 的測試相關程式碼。

## 檔案說明

### JavaScript 測試檔案 (/tests/js/)

* `chart-fallback.js` - 圖表降級處理模組，提供當特定圖表類型無法顯示時的替代方案。
  - 包含將 OHLC 資料轉換為折線圖格式的函數
  - 提供基本折線圖配置生成功能
  - 包含測試用範例蠟燭圖資料生成函數

## 使用說明

這些檔案主要用於開發和測試環境，不應在生產環境中直接使用。測試時可以通過以下方式引入：

```javascript
import { convertOHLCToLineData, createBasicLineChart, generateSampleOHLCData } from '../../tests/js/chart-fallback.js';
```

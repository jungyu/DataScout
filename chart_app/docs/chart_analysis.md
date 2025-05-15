# Chart.js 與 CSV 資料適用性分析

## CSV 資料分類與適用圖表類型

依據分析檔案結構和資料性質，我們將 CSV 資料分為以下幾類：

### 1. 金融市場資料
- **資料檔案**: AAPL_stock_data、Gold_price、SP500_price、Copper_price、VIX_price、USDTWD_exchange_rate、Gold_TWD_price
- **資料特性**: 通常有 OHLC (開高低收) 結構，或者是時間序列價格資料
- **適用圖表**:
  - 蠟燭圖 (Candlestick Chart): 適用於有完整 OHLC 資料的檔案
  - 折線圖 (Line Chart): 適用於所有金融時間序列資料，特別是需要顯示趨勢
  - 區域圖 (Area Chart): 適合顯示成交量或價格變化區間

### 2. 經濟指標資料
- **資料檔案**: fred_GDP、fred_GDPC1、fred_UNRATE 等 fred_ 開頭的檔案
- **資料特性**: 單一或多個經濟指標的時間序列資料
- **適用圖表**:
  - 折線圖 (Line Chart): 適合顯示指標趨勢變化
  - 長條圖 (Bar Chart): 適合 GDP、債務等總量資料
  - 混合圖表: 如 GDP 和失業率的複合圖表

### 3. 新聞與關鍵字資料
- **資料檔案**: news_bloomberg_logs、news_ft_logs、news_reuters_logs、news_nikkei_logs
- **資料特性**: 關鍵字出現頻率、搜尋結果統計
- **適用圖表**:
  - 圓餅圖 (Pie Chart): 適合顯示不同關鍵字的分布比例
  - 長條圖 (Bar Chart): 適合比較不同關鍵字的出現頻率
  - 雷達圖 (Radar Chart): 適合多維度關鍵字分析

### 4. 政策與分析資料
- **資料檔案**: fiscal_stimulus_analysis、monetary_easing_indicators、trade_protectionism_indicators
- **資料特性**: 多維指標、多時間點的綜合數據
- **適用圖表**:
  - 複合圖表: 長條圖+折線圖，用於展示不同指標間的關聯
  - 熱力圖 (Heatmap): 適合顯示不同政策強度
  - 散點圖 (Scatter Plot): 適合顯示不同指標的相關性

## 轉換成果

我們已完成將所有 CSV 檔案轉換為適合的 Chart.js JSON 格式。主要轉換了以下圖表類型：

1. **蠟燭圖 (Candlestick Chart)**: 對於包含完整 OHLC 資料的金融時間序列
2. **折線圖 (Line Chart)**: 對於大多數時間序列資料，特別是價格、匯率和經濟指標
3. **長條圖 (Bar Chart)**: 適用於經濟指標和政策分析資料
4. **圓餅圖 (Pie Chart)**: 用於新聞關鍵字分析

## 進階優化建議

為了進一步增強資料視覺化效果，建議考慮：

1. **自適應時間單位**: 根據資料跨度自動選擇適合的時間單位（天、週、月、季度、年）
2. **多指標動態比較**: 增加使用者可選擇比較不同指標的功能
3. **資料粒度調整**: 提供資料聚合選項（如日、週、月平均）
4. **技術分析指標**: 為金融數據加入移動平均線、RSI 等技術指標
5. **跨資料集相關性分析**: 如黃金價格與美元指數的關聯圖表

## 結論

依據資料特性，我們已將 CSV 檔案轉換為最適合的 Chart.js JSON 格式。這些 JSON 檔案可以直接用於 Chart.js 繪製圖表，並提供基於資料特性的最佳視覺化效果。

# DataScout 數據可視化儀表板

DataScout 是一個功能豐富的數據可視化儀表板專案，基於 ApexCharts、Alpine.js 和 DaisyUI (Tailwind CSS) 構建。專案採用多頁應用(MPA)架構設計，提供多種圖表呈現方式，並可與 FastAPI 後端整合。

## 專案架構

```
frontend/
├── public/              # 靜態資源及主要程式碼
│   ├── index.html       # 主頁面 (蠟燭圖)
│   ├── *.html           # 各種圖表類型頁面
│   ├── *.js             # 各類圖表處理和工具腳本
│   ├── assets/          # 資源文件（範例數據、圖片）
│   └── components/      # HTML 組件
│       ├── charts/      # 圖表組件
│       ├── layout/      # 布局組件
│       └── ui/          # UI 組件
├── src/                 # 源代碼
│   ├── components/      # React/Vue 組件 (未來擴展用)
│   ├── data/            # 數據源文件
│   ├── pages/           # 頁面組件
│   ├── styles/          # 樣式文件
│   └── utils/           # 工具函數
├── docs/                # 文檔
└── package.json         # 項目依賴
```

## 主要功能

- **多種圖表類型**：支援折線圖、區域圖、柱狀圖、蠟燭圖等多種圖表類型
- **組件化設計**：使用原生 JavaScript 實現的組件系統，方便頁面組合與復用
- **數據選擇器**：允許用戶在不同數據源之間切換或上傳自定義數據
- **主題切換**：支援淺色/深色主題切換
- **錯誤處理**：完善的圖表錯誤處理與復原機制
- **自適應界面**：基於 Tailwind CSS 實現的響應式設計

## 安裝與啟動

1. **安裝依賴**
   ```bash
   npm install
   ```

2. **啟動開發服務器**
   ```bash
   npm start
   ```
   或使用提供的啟動腳本
   ```bash
   ./start.sh
   ```

3. **構建生產版本**
   ```bash
   npm run build
   ```

## 圖表類型

DataScout 目前支援以下圖表類型：

- 蠟燭圖 (Candlestick) - 適用於金融數據
- 折線圖 (Line) - 適用於趨勢數據
- 區域圖 (Area) - 適用於數值區間與趨勢
- 柱狀圖 (Column) - 適用於類別比較
- 條形圖 (Bar) - 適用於水平類別比較
- 餅圖 (Pie) - 適用於比例數據
- 環形圖 (Donut) - 適用於比例數據
- 雷達圖 (Radar) - 適用於多維度比較
- 散點圖 (Scatter) - 適用於相關性數據
- 熱圖 (Heatmap) - 適用於矩陣強度數據
- 樹狀圖 (Treemap) - 適用於層次結構數據
- 極座標圖 (PolarArea) - 適用於循環數據

## 使用方式

### 訪問不同圖表

每種圖表類型都有獨立的 HTML 頁面，可以通過直接訪問對應頁面查看：

- `/index.html` - 蠟燭圖（首頁）
- `/line.html` - 折線圖
- `/area.html` - 區域圖
- `/column.html` - 柱狀圖
- 更多圖表頁面...

### 切換數據源

1. 在數據選擇器面板中，可以點擊不同的數據源
2. 可以切換「範例數據」開關，上傳自己的 JSON 數據文件
3. 數據格式請參考 `docs/apex_formats.md` 文件

### 自定義圖表

可以根據需要自定義圖表配置：

```javascript
// 示例：初始化一個新的圖表
const options = {
  chart: { type: 'line', height: 350 },
  series: [{ name: '數據', data: [10, 41, 35, 51, 49, 62, 69] }],
  xaxis: { categories: ['週一', '週二', '週三', '週四', '週五', '週六', '週日'] }
};

const chart = new ApexCharts(document.querySelector('#chart'), options);
chart.render();
```

## 資料來源

DataScout 支持多種資料來源，包括：

- AAPL (蘋果) 股票數據
- TSMC (台積電) 股票數據
- BTC/USD (比特幣/美元) 交易數據

## 文檔

詳細的文檔可以在 `docs/` 目錄下找到：

- `apex_formats.md` - ApexCharts JSON 格式詳解
- `apex_types.md` - 各類圖表所需的數據結構
- `chart_data_selector.md` - 數據選擇器組件使用指南
- `fastapi_integration.md` - 與 FastAPI 後端整合指南

## 詳細資訊

有關本專案的完整檔案清單、功能說明和使用方式，請參考 [Snapshot.md](Snapshot.md)。
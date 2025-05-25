# DataScout 專案快照

本文件提供了 DataScout 前端專案的詳細概述，包括檔案結構、主要元件、工具腳本的用途與使用方式。

## 目錄

1. [專案概述](#專案概述)
2. [專案架構](#專案架構)
3. [核心檔案說明](#核心檔案說明)
4. [組件系統](#組件系統)
5. [圖表處理機制](#圖表處理機制)
6. [數據管理](#數據管理)
7. [錯誤處理](#錯誤處理)
8. [文檔資源](#文檔資源)
9. [最佳實踐](#最佳實踐)

## 專案概述

DataScout 是一個基於 ApexCharts、Alpine.js 和 DaisyUI (Tailwind CSS) 的數據視覺化儀表板，採用多頁應用 (MPA) 架構設計。專案提供各種類型的圖表展示，並支援數據源切換、自定義數據上傳、主題切換等功能。

**技術棧：**
- JavaScript (主要邏輯)
- Alpine.js (輕量級前端框架)
- ApexCharts (圖表庫)
- Tailwind CSS + DaisyUI (UI 框架)
- Vite (構建工具)

## 專案架構

```
frontend/
├── public/                  # 靜態資源及主要程式碼
│   ├── components/          # HTML 組件
│   │   ├── charts/          # 圖表組件
│   │   ├── layout/          # 布局組件
│   │   └── ui/              # UI 組件
│   ├── assets/              # 資源文件
│   │   ├── examples/        # 示例數據文件
│   │   └── images/          # 圖片
│   ├── *.html               # 各種圖表頁面
│   └── *.js                 # 各類圖表處理和工具腳本
├── src/                     # 源代碼
│   ├── components/          # 元件
│   ├── data/                # 數據源
│   ├── pages/               # 頁面
│   ├── styles/              # 樣式文件
│   ├── utils/               # 工具函數
│   ├── App.js               # 主應用
│   └── index.js             # 入口文件
├── docs/                    # 文檔
├── package.json             # 項目依賴
├── vite.config.js           # Vite 配置
└── README.md                # 項目說明
```

## 核心檔案說明

### HTML 頁面

| 檔案名稱 | 說明 |
|---------|------|
| `index.html` | 主頁面，展示蠟燭圖 |
| `line.html` | 折線圖頁面 |
| `area.html` | 區域圖頁面 |
| `column.html` | 柱狀圖頁面 |
| `bar.html` | 條形圖頁面 |
| `pie.html` | 餅圖頁面 |
| `donut.html` | 環形圖頁面 |
| `radar.html` | 雷達圖頁面 |
| `scatter.html` | 散點圖頁面 |
| `heatmap.html` | 熱圖頁面 |
| `treemap.html` | 樹狀圖頁面 |
| `polararea.html` | 極座標圖頁面 |
| `chart-test.html` | 圖表測試頁面 |
| `selector-test.html` | 選擇器測試頁面 |

### 核心腳本文件

| 檔案名稱 | 用途 | 重要特點 |
|---------|------|---------|
| `component-loader.js` | 組件加載工具 | 動態載入 HTML 組件，處理組件通信 |
| `unified-chart-handler.js` | 統一圖表處理器 | 提供各類圖表渲染的統一接口 |
| `chart-data-loader.js` | 圖表數據加載器 | 從 JSON 文件加載數據並初始化圖表 |
| `chart-error-handler.js` | 圖表錯誤處理 | 處理圖表渲染錯誤，提供錯誤提示 |
| `chart-error-handler-enhanced.js` | 增強版錯誤處理 | 提供更詳細的錯誤診斷和修復建議 |
| `chart-recovery-tool.js` | 圖表恢復工具 | 從圖表渲染失敗中恢復 |
| `chart-fix.js` | 圖表修復工具 | 修復常見的圖表配置問題 |
| `chart-navigator.js` | 圖表導航工具 | 提供圖表頁面間的導航功能 |
| `example-toggle.js` | 範例切換工具 | 切換範例數據和自定義數據 |
| `file-upload-handler.js` | 文件上傳處理 | 處理用戶上傳的數據文件 |
| `data-loader.js` | 數據加載工具 | 從多種來源加載數據 |
| `json-enhancer.js` | JSON 增強工具 | 增強 JSON 處理功能 |
| `json-formatter-fix.js` | JSON 格式修復 | 修復格式錯誤的 JSON |
| `json-function-processor.js` | JSON 函數處理 | 處理 JSON 中的函數字符串 |

### 圖表處理器

| 檔案名稱 | 用途 | 重要特點 |
|---------|------|---------|
| `line-chart-handler.js` | 折線圖處理器 | 處理折線圖相關的配置和渲染 |
| `area-chart-handler.js` | 區域圖處理器 | 處理區域圖相關的配置和渲染 |
| `bar-chart-handler.js` | 條形圖處理器 | 處理條形圖相關的配置和渲染 |
| `column-chart-handler.js` | 柱狀圖處理器 | 處理柱狀圖相關的配置和渲染 |
| `pie-chart-handler.js` | 餅圖處理器 | 處理餅圖相關的配置和渲染 |
| `donut-chart-handler.js` | 環形圖處理器 | 處理環形圖相關的配置和渲染 |
| `radar-chart-handler.js` | 雷達圖處理器 | 處理雷達圖相關的配置和渲染 |
| `scatter-chart-handler.js` | 散點圖處理器 | 處理散點圖相關的配置和渲染 |
| `heatmap-chart-handler.js` | 熱圖處理器 | 處理熱圖相關的配置和渲染 |
| `treemap-chart-handler.js` | 樹狀圖處理器 | 處理樹狀圖相關的配置和渲染 |
| `polararea-chart-handler.js` | 極座標圖處理器 | 處理極座標圖相關的配置和渲染 |
| `mixed-chart-handler.js` | 混合圖表處理器 | 處理多種圖表類型組合的配置和渲染 |
| `enhanced-line-chart-handler.js` | 增強型折線圖處理器 | 提供更多折線圖特性和交互功能 |

### 工具和輔助腳本

| 檔案名稱 | 用途 | 重要特點 |
|---------|------|---------|
| `chart-compat.js` | 圖表兼容性處理 | 解決不同瀏覽器的兼容性問題 |
| `chart-verification.js` | 圖表驗證工具 | 驗證圖表配置是否正確 |
| `chart-testing-tool.js` | 圖表測試工具 | 提供圖表測試功能 |
| `debug-control-panel.js` | 調試控制面板 | 提供調試工具和選項 |
| `component-debug.js` | 組件調試工具 | 調試組件加載和渲染 |
| `component-inspect.js` | 組件檢查工具 | 檢查組件結構和屬性 |
| `red-box-inspector.js` | 紅框檢查器 | 顯示元素邊界和間距 |
| `selector-debug.js` | 選擇器調試 | 調試數據選擇器組件 |
| `selector-fix.js` | 選擇器修復 | 修復選擇器相關問題 |
| `toggle-debug.js` | 切換開關調試 | 調試切換開關元素 |
| `toggle-check.js` | 切換開關檢查 | 檢查切換開關狀態 |
| `data-toggle.js` | 數據切換工具 | 在不同數據集間切換 |
| `manual-toggle.js` | 手動切換工具 | 提供手動切換數據的功能 |

### 文件修復和更新腳本

| 檔案名稱 | 用途 | 重要特點 |
|---------|------|---------|
| `area-fix.js` | 區域圖修復 | 修復區域圖渲染問題 |
| `candlestick-fix.js` | 蠟燭圖修復 | 修復蠟燭圖特定問題 |
| `line-chart-fix.js` | 折線圖修復 | 修復折線圖特定問題 |
| `update_scripts.sh` | 腳本更新工具 | Shell 腳本，用於批量更新 JS 文件 |

## 組件系統

DataScout 使用原生 JavaScript 實現的組件系統，通過 `component-loader.js` 動態載入 HTML 組件。

### 使用方式

在 HTML 中使用 `data-component` 屬性指定組件路徑：

```html
<div id="sidebar" data-component="components/layout/Sidebar.html"></div>
```

### 主要組件

#### 布局組件

- `components/layout/Sidebar.html` - 側邊欄導航
- `components/layout/Topbar.html` - 頂部工具欄
- `components/layout/Footer.html` - 頁腳

#### 圖表組件

- `components/charts/ChartHeader.html` - 圖表標題區域
- `components/charts/LineChartContent.html` - 折線圖內容
- `components/charts/AreaChartContent.html` - 區域圖內容
- `components/charts/ColumnChartContent.html` - 柱狀圖內容
- 其他圖表組件...

#### UI 組件

- `components/ui/ChartDataSelector.html` - 圖表數據選擇器
- `components/ui/ThemeToggle.html` - 主題切換開關
- `components/ui/FileUploader.html` - 文件上傳器

## 圖表處理機制

### 統一圖表處理流程

1. **獲取圖表類型** - 從頁面路徑或指定元素中獲取圖表類型
2. **加載對應數據** - 使用 `chart-data-loader.js` 加載數據
3. **渲染圖表** - 使用 `unified-chart-handler.js` 調用對應的圖表處理器
4. **錯誤處理** - 使用 `chart-error-handler.js` 處理可能的錯誤

### 數據格式

圖表數據使用標準的 ApexCharts 格式，詳見 `docs/apex_formats.md`。

### 圖表類型識別

```javascript
// 檢測當前頁面的圖表類型
const currentPath = window.location.pathname;
let chartType = 'candlestick'; // 默認為蠟燭圖

if (currentPath.endsWith('/') || currentPath.endsWith('/index.html')) {
  chartType = 'candlestick';
} else if (currentPath.includes('/line')) {
  chartType = 'line';
} else if (currentPath.includes('/area')) {
  chartType = 'area';
}
// 其他類型...
```

## 數據管理

### 數據來源

- **預設範例** - 存放在 `assets/examples/` 目錄
- **用戶上傳** - 通過 `file-upload-handler.js` 處理
- **外部 API** - 通過 `data-loader.js` 加載

### 數據選擇器使用方式

數據選擇器組件 (`ChartDataSelector.html`) 提供了切換數據源的界面：

1. 使用切換開關選擇範例數據或自定義數據
2. 點擊數據卡片切換數據源
3. 使用文件上傳功能上傳自定義數據

詳細文檔請參考 `docs/chart_data_selector.md`。

## 錯誤處理

### 常見錯誤類型

- **數據格式錯誤** - 數據結構不符合 ApexCharts 要求
- **元素不存在** - 找不到指定的圖表容器
- **配置錯誤** - 圖表配置參數不正確
- **渲染超時** - 圖表渲染時間過長

### 錯誤處理流程

```javascript
window.chartErrorHandler = {
  // 顯示錯誤訊息
  showError: function(elementId, errorMsg, errorType = 'error') {
    console.error(`圖表錯誤 (${elementId}): ${errorMsg}`);
    
    const container = document.getElementById(elementId);
    if (!container) {
      console.error(`找不到圖表容器: #${elementId}`);
      return;
    }
    
    // 顯示錯誤界面
    container.innerHTML = `
      <div class="flex flex-col items-center justify-center h-full p-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 ${colorClass} mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-base ${colorClass} font-medium text-center mb-2">${errorMsg}</p>
        <button class="btn btn-sm btn-outline btn-primary mt-4" onclick="location.reload()">重新整理頁面</button>
      </div>
    `;
  }
};
```

### 恢復機制

`chart-recovery-tool.js` 提供了從圖表渲染失敗中恢復的功能：

1. 嘗試清理圖表實例
2. 重置圖表配置
3. 使用簡化設置重新渲染
4. 提供用戶手動修復選項

## 文檔資源

### 技術文檔

- `docs/apex_formats.md` - ApexCharts JSON 格式規範
- `docs/apex_types.md` - 圖表座標軸與資料需求表
- `docs/chart_data_selector.md` - 圖表數據選擇器組件使用指南
- `docs/fastapi_integration.md` - DataScout 與 FastAPI 後端整合指南

### 開發文檔

- `docs/chart-fixes-documentation.md` - 圖表修復文檔
- `docs/chart-rendering-test-guide.md` - 圖表渲染測試指南

## 最佳實踐

### 添加新圖表類型

1. 創建新的 HTML 頁面 (例如 `bubble.html`)
2. 創建對應的圖表處理器 (例如 `bubble-chart-handler.js`)
3. 在 `unified-chart-handler.js` 中註冊新的圖表類型
4. 在 `chart-data-loader.js` 中添加對應的數據處理邏輯
5. 在側邊欄導航中添加新頁面的連結

### 自定義圖表配置

```javascript
// 基本配置
const baseOptions = {
  chart: {
    height: 350,
    type: 'line',
    toolbar: {
      show: true
    },
    zoom: {
      enabled: true
    }
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    curve: 'straight'
  },
  grid: {
    row: {
      colors: ['#f3f3f3', 'transparent'],
      opacity: 0.5
    }
  },
  xaxis: {
    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
  }
};

// 合併自定義配置
const options = Object.assign({}, baseOptions, customOptions);
```

### 數據格式轉換

使用 `json-enhancer.js` 和 `json-formatter-fix.js` 處理不同格式的數據源，轉換為 ApexCharts 所需格式。

```javascript
function convertToApexFormat(data, chartType) {
  switch (chartType) {
    case 'line':
      return {
        series: [{
          name: data.title || 'Series 1',
          data: data.values
        }],
        xaxis: {
          categories: data.labels
        }
      };
    // 其他類型的轉換...
  }
}
```

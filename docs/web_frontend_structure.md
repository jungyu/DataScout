# DataScout Web Frontend 目錄結構說明

## 專案概述

DataScout Web Frontend 是一個混合架構的網頁數據可視化儀表板，目前同時存在兩套不同的實現方式：
1. **Alpine.js 架構** (`/src`): 使用 Alpine.js + Vite 的現代化組件系統
2. **傳統 HTML 架構** (`/public`): 基於原生 HTML + 組件載入器的靜態頁面系統

⚠️ **重要提醒**: 專案目前存在兩套不同的前端架構，需要重構統一以提高可維護性和組件重用性。

## 技術棧

- **構建工具**: Vite 6.3.5
- **前端框架**: Alpine.js 3.14.9 (現代架構) / 原生 HTML+JS (傳統架構)
- **樣式框架**: TailwindCSS 3.3.3 + DaisyUI 4.10.3
- **圖表庫**: ApexCharts 4.7.0
- **包管理器**: NPM

---

## 雙架構並存現狀

### 架構一：Alpine.js 現代架構 (`/src`)

這是基於 Vite + Alpine.js 的現代化單頁應用架構：

```plaintext
src/
├── App.js                 # Alpine.js 主應用程式
├── index.js              # 應用入口點（含重定向邏輯）
├── component-loader.js    # Alpine.js 組件載入器
├── components/           # Alpine.js 組件
│   ├── charts/          # 圖表組件（Alpine.js 版）
│   ├── layout/          # 布局組件（Alpine.js 版）
│   └── ui/              # UI 組件（Alpine.js 版）
├── pages/               # 頁面級組件
│   ├── ChartExamples.js # 圖表範例頁面
│   └── DataSelector.js  # 資料選擇頁面
├── data/                # 示範資料
│   ├── stockData.js     # 股票資料
│   └── cryptoData.js    # 加密貨幣資料
├── styles/              # CSS 樣式
│   └── main.css         # 主樣式表
└── utils/               # 工具函數
```

**特點**:
- 使用 Alpine.js 的響應式資料綁定
- 組件化架構，便於維護
- 支援 ES6 模組系統
- 整合 Vite 熱重載

### 架構二：傳統 HTML 頁面架構 (`/public`)

這是基於獨立 HTML 頁面 + 組件載入器的傳統架構：

```plaintext
public/
├── line.html             # 折線圖頁面
├── bar.html              # 條形圖頁面
├── area.html             # 區域圖頁面
├── candlestick.html      # K線圖頁面
├── pie.html              # 圓餅圖頁面
├── donut.html            # 環形圖頁面
├── ... （其他圖表頁面）
├── component-loader.js   # HTML 組件載入器
├── components/           # HTML 組件庫
│   ├── layout/          # 布局組件（HTML 版）
│   │   ├── Sidebar.html # 側邊欄組件
│   │   └── Topbar.html  # 頂部導航組件
│   ├── charts/          # 圖表組件（HTML 版）
│   └── ui/              # UI 組件（HTML 版）
├── assets/              # 靜態資源
│   └── examples/        # 圖表範例 JSON 檔案
└── [大量JS腳本]         # 各種處理器和工具
    ├── line-chart-handler.js
    ├── bar-chart-handler.js
    ├── chart-error-handler.js
    ├── data-loader.js
    └── ... （80+ JS 檔案）
```

**特點**:
- 每個圖表類型有獨立的 HTML 頁面
- 使用 `data-component` 屬性動態載入組件
- 大量專門化的 JS 處理器
- 傳統的多頁面應用結構

---

## 雙架構對比分析

| 層面 | Alpine.js 架構 (`/src`) | 傳統 HTML 架構 (`/public`) |
|------|-------------------------|--------------------------|
| **頁面結構** | 單頁應用 (SPA) | 多頁面應用 (MPA) |
| **組件系統** | Alpine.js 響應式組件 | HTML 模板 + 動態載入 |
| **資料綁定** | 雙向資料綁定 | 手動 DOM 操作 |
| **路由** | 程式化路由 | 檔案系統路由 |
| **模組化** | ES6 import/export | 全域 script 標籤 |
| **開發體驗** | 熱重載、現代工具鏈 | 傳統開發流程 |
| **維護性** | 高（組件化） | 中等（大量獨立檔案） |
| **效能** | 單頁快速切換 | 頁面間完整重載 |
| **完整度** | 部分實現 | 功能完整 |

---

## 重構建議

### 現狀問題

1. **程式碼重複**: 兩套架構實現了相似的功能
2. **維護困難**: 需要同時維護兩套不同的系統
3. **組件不通用**: 無法在兩個架構間共享組件
4. **開發複雜**: 新功能需要在兩處實現

### 重構方向

#### 選項 1: 統一到 Alpine.js 架構 (推薦)

**優點**:
- 現代化的開發體驗
- 更好的組件重用性
- 統一的狀態管理
- 更容易維護和擴展

**步驟**:
1. 完善 Alpine.js 架構中缺失的圖表類型
2. 將 `/public` 中的圖表處理邏輯移植到 Alpine.js 組件
3. 統一資料流和狀態管理
4. 逐步淘汰 `/public` 架構

#### 選項 2: 保留混合架構但規範化

**優點**:
- 風險較低
- 可以保持現有功能完整性

**步驟**:
1. 建立明確的架構使用規範
2. 提取共用組件和工具函數
3. 統一樣式和 UI 組件
4. 建立架構間的資料共享機制

---

## 目前目錄結構

```plaintext
web_frontend/
├── index.html            # Vite 入口（指向 Alpine.js 架構）
├── package.json          # 專案配置
├── vite.config.js        # Vite 配置
├── src/                  # Alpine.js 現代架構
│   ├── App.js           # 主應用
│   ├── index.js         # 入口點
│   ├── components/      # Alpine.js 組件
│   ├── pages/           # 頁面組件
│   ├── data/            # 示範資料
│   ├── styles/          # 樣式
│   └── utils/           # 工具函數
├── public/               # 傳統 HTML 架構
│   ├── *.html           # 各種圖表頁面
│   ├── component-loader.js
│   ├── components/      # HTML 組件
│   ├── assets/          # 靜態資源
│   └── [80+ JS files]   # 各種處理器
├── scripts/              # 自動化腳本
│   ├── tests/           # 測試腳本
│   ├── deploy_to_web_service.sh
│   └── chart_diagnosis_and_fix.py
├── docs/                # 文件
└── dist/                # 建置輸出（npm run build 產生）
```

---

## 開發與部署流程

### 開發環境

```bash
cd web_frontend
npm install              # 安裝依賴
npm run dev             # 啟動 Vite 開發服務器 (http://localhost:5173)
```

**注意**: 
- Vite 開發服務器預設提供 Alpine.js 架構
- 訪問根路徑會自動重定向到 `/line.html`（傳統架構）
- 可以直接訪問 `/bar.html`, `/pie.html` 等頁面使用傳統架構

### 生產環境建置

```bash
npm run build           # 建置到 dist/ 目錄
npm run preview         # 預覽建置結果
```

### 部署

```bash
./scripts/deploy_to_web_service.sh
```

部署腳本會：
1. 執行 `npm run build`
2. 備份現有的 `web_service/static` 內容
3. 複製 `dist/` 內容到 `web_service/static/`
4. 生成部署報告

---

## 重構行動計劃

### 第一階段：分析與準備
- [x] 完成雙架構現狀分析
- [ ] 確定目標架構（Alpine.js）
- [ ] 制定組件遷移計劃
- [ ] 設計統一的組件介面

### 第二階段：核心組件統一
- [ ] 統一圖表組件 API
- [ ] 遷移佈局組件到 Alpine.js
- [ ] 統一資料載入邏輯
- [ ] 建立共用的樣式系統

### 第三階段：功能遷移
- [ ] 遷移所有圖表類型到 Alpine.js
- [ ] 統一路由系統
- [ ] 整合檔案上傳功能
- [ ] 完善錯誤處理

### 第四階段：清理與優化
- [ ] 移除冗餘的傳統架構檔案
- [ ] 優化建置流程
- [ ] 更新文件和測試
- [ ] 效能優化

---

## 相關文件

- 部署腳本說明：`/scripts/README.md`
- 測試腳本說明：`/scripts/tests/README.md`
- 前端開發指南：待建立
- 組件設計規範：待建立

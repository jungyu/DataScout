# DataScout Chart App 快照文件

## 概述

Chart App 是 DataScout 專案的視覺化元件，整合了 FastAPI 後端、Jinja2 模板渲染、Tailwind CSS、Chart.js 以及 canvas 截圖功能，提供強大的資料視覺化解決方案。該應用支援多種資料來源和圖表類型，使用標準化的 JSON 資料格式，確保圖表正確顯示。

> 更新時間：2025年5月20日

## 核心功能

- **多樣化圖表類型**：支援折線圖、長條圖、雷達圖、圓餅圖、環形圖、極座標圖、氣泡圖、散點圖等
- **多種資料來源**：CSV、JSON、Excel 與持久化存儲
- **OLAP 操作**：分組聚合、透視表、滾動視窗計算
- **圖表診斷工具**：幫助排查和修復圖表渲染問題
- **檔案上傳與驗證**：支援文件上傳功能，自動驗證 JSON 格式
- **圖表匯出**：支援將圖表下載為 PNG 或 WebP 格式，或上傳至伺服器

## 技術架構

### 前端

- **模組化 JavaScript 架構**：
  - 主入口點 (main.js)
  - 應用程式初始化 (app-initializer.js)
  - 狀態管理 (state-manager.js)
  - UI 控制 (ui-controller.js)
  - 資料載入 (data-loader.js)
  - 圖表管理 (chart-manager.js)
  - 依賴檢查 (dependency-checker.js)
- **Tailwind CSS**：用於現代化 UI 設計
- **Chart.js**：用於互動式圖表渲染

### 後端

- **FastAPI**：提供高性能 API 服務
- **Jinja2**：處理伺服器端模板渲染
- **Pandas & NumPy**：用於數據處理與分析
- **OpenPyXL & XLRD**：用於 Excel 檔案處理

## 項目結構

```
chart_app/
├── app/                    # FastAPI 應用主目錄
│   ├── main.py             # 主應用程式
│   ├── json_adapter.py     # JSON 格式轉換適配器
│   └── __init__.py         # Python 模組標識
├── templates/              # HTML 模板目錄
├── static/                 # 靜態檔案目錄
│   ├── css/                # CSS 檔案
│   ├── js/                 # JavaScript 檔案
│   └── uploads/            # 上傳檔案存放目錄
├── docs/                   # 文件目錄
├── frontend/               # 前端開發檔案
├── tests/                  # 測試目錄
└── scripts/                # 腳本文件目錄
```

## API 端點

| 端點 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 主頁面 |
| `/docs/chart-format` | GET | 查看 Chart.js JSON 格式文檔 |
| `/api/chart-data/` | GET | 獲取示例圖表數據 |
| `/api/data-files/` | GET | 獲取所有可用數據文件 |
| `/api/file-data/` | GET | 獲取特定文件的數據 |
| `/api/file-content/` | GET | 獲取原始文件內容 |
| `/api/file-structure/` | GET | 獲取文件結構信息 |
| `/api/upload-file/` | POST | 上傳數據文件 |
| `/api/chart-from-json/` | POST | 從 JSON 數據直接生成圖表 |
| `/api/olap-operation/` | POST | 執行 OLAP 操作 |
| `/upload-chart-image/` | POST | 上傳圖表截圖 |
| `/chart-diagnostics` | GET | 圖表診斷工具 |

## 最近更新

- **模組化重構**：前端代碼已完成重構，從單一大型文件分割為多個職責明確的模組，提高了可維護性和可擴展性
- **圖表診斷工具**：新增圖表診斷工具，幫助排查和修復圖表渲染問題，特別是時間軸相關問題
- **日期適配器**：新增穩定的日期和時間軸處理功能

## 安裝與啟動

### 快速啟動

```bash
# 安裝 Python 相依套件
pip install -r requirements.txt

# 安裝 npm 相依套件
npm install

# 一鍵啟動開發環境
npm run dev
```

### 訪問應用

打開瀏覽器訪問: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## 整合與相依性

作為 DataScout 專案的一部分，Chart App 與其他元件有以下整合點：

1. 接受 DataScout 核心提供的數據源
2. 透過標準化的 JSON 格式進行數據交換
3. 支援與 DataScout 的資料採集組件進行整合
4. 提供標準 API 端點以供其他組件呼叫

## 未來計畫

- 增強數據分析能力，整合機器學習模型
- 增加更多高級圖表類型 (例如：桑基圖、樹狀圖等)
- 改進圖表主題與樣式自定義選項
- 優化大型數據集的處理效能

## 參考資源

- [使用指南](docs/usage_guide.md)
- [圖表格式文檔](docs/chart_formats.md)
- [重構文檔](docs/refactoring.md)
- [測試計劃](docs/test-plan.md)

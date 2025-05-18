# Chart App

整合 FastAPI 後端、Jinja2 模板渲染、Tailwind CSS、Chart.js 以及 canvas 截圖功能的資料視覺化應用，支援多種資料來源和圖表類型。使用標準化的 JSON 資料格式，確保圖表正確顯示。

**重要更新**: 前端代碼已經完成重構，從單一大型文件分割為多個職責明確的模組，提高了可維護性和可擴展性。詳細資訊請參閱 [重構文檔](docs/refactoring.md)。

## 模組化架構

本專案採用模組化設計，前端代碼經過重構，分為以下核心模組：

- **main.js**: 應用程式主入口，匯入和匯出其他模組功能
- **state-manager.js**: 集中管理應用程式狀態，提供存取介面
- **app-initializer.js**: 處理應用程式初始化和配置邏輯
- **ui-controller.js**: 管理所有用戶界面交互和事件處理
- **data-loader.js**: 處理資料載入和格式轉換
- **chart-manager.js**: 管理圖表創建、更新和銷毀
- **dependency-checker.js**: 檢查必要依賴項目是否正確載入

關於重構的詳細資訊：
- [重構文檔](docs/refactoring.md)
- [變更記錄](docs/refactoring-changelog.md)
- [測試計劃](docs/test-plan.md)

## 功能

- FastAPI 後端提供 API 端點和網頁渲染
- Jinja2 模板引擎處理前端頁面
- Tailwind CSS 進行頁面美化
- Chart.js 繪製互動式圖表
- 多種資料來源支援：CSV、JSON (符合 Chart.js 標準格式)、Excel 與持久化存儲
- 支援文件上傳功能，自動驗證 JSON 格式
- 豐富的圖表類型：折線圖、長條圖、雷達圖、圓餅圖、環形圖、極座標圖、氣泡圖、散點圖
- 多種圖表主題選項
- 進階 OLAP 操作：分組聚合、透視表、滾動視窗計算
- 支持圖表下載為 PNG 或 WebP 格式
- 支持將圖表上傳到伺服器
- 標準化的 JSON 資料處理，自動轉換和驗證
- **圖表診斷工具**：幫助排查和修復圖表渲染問題，特別是時間軸相關問題
- **日期適配器**：提供穩定的日期和時間軸處理功能

## 圖表診斷工具

應用內建診斷工具可幫助開發者和用戶解決圖表渲染問題：

- **圖表庫診斷**：檢查 Chart.js 的載入狀態、版本和必要組件
- **日期適配器診斷**：診斷和修復時間軸相關問題
- **自動修復功能**：自動修復常見問題，如缺少日期適配器或時間軸格式配置
- **時間軸測試**：專門測試圖表時間軸功能
- **一般圖表測試**：測試基本圖表類型的渲染

訪問路徑：`/chart-diagnostics`

## 專案結構

```text
chart_app/
├── app/                    # FastAPI 應用主目錄
│   ├── main.py             # 主應用程式
│   ├── json_adapter.py     # JSON 格式轉換適配器
│   └── __init__.py         # Python 模組標識
├── templates/              # HTML 模板目錄
│   └── index.html          # 主頁面模板
├── static/                 # 靜態檔案目錄
│   ├── css/                # CSS 檔案
│   │   └── output.css      # 編譯後的 Tailwind CSS
│   ├── js/                 # JavaScript 檔案
│   │   ├── dist/           # 編譯後的 JS 檔案
│   │   └── src/            # 源碼 JS 檔案
│   │       ├── main.js                # 主入口點
│   │       ├── app-initializer.js     # 應用程式初始化
│   │       ├── state-manager.js       # 狀態管理
│   │       ├── ui-controller.js       # UI 控制
│   │       ├── data-loader.js         # 資料載入
│   │       ├── chart-manager.js       # 圖表管理
│   │       ├── dependency-checker.js  # 依賴檢查
│   │       └── ...                    # 其他輔助模組
│   └── uploads/            # 上傳檔案存放目錄
├── docs/                   # 文件目錄
│   ├── chart_formats.md    # Chart.js JSON 格式文檔
│   ├── refactoring.md      # 重構文檔
│   ├── refactoring-changelog.md # 重構變更記錄
│   └── test-plan.md        # 測試計劃
├── frontend/               # 前端開發檔案
│   ├── input.css           # Tailwind CSS 輸入檔案
│   └── tailwind.config.js  # Tailwind 設定檔
├── tests/                  # 測試目錄
│   └── test_refactored_modules.js # 重構模組測試
├── requirements.txt        # Python 相依性列表
└── package.json            # npm 相依性及指令
```

## 安裝與啟動

### 1. 安裝 Python 相依套件

```bash
pip install -r requirements.txt
```

### 2. 安裝 npm 相依套件

```bash
npm install
```

### 3. 一鍵啟動開發環境

我們提供了一個簡便的指令，可同時啟動 Tailwind CSS 編譯和 FastAPI 應用程式：

```bash
npm run dev
```

或者，您也可以分別執行以下步驟：

#### 3.1. 編譯 Tailwind CSS

```bash
# 開發模式（監視文件變化）
npm run build:css

# 或生產模式（最小化）
npm run build:css:prod
```

#### 3.2. 啟動 FastAPI 應用

```bash
npm run start
# 或直接使用 uvicorn
python -m uvicorn app.main:app --reload --port 8000
```

### 4. 執行測試

```bash
# 執行 JavaScript 模組測試
npm run test

# 產生測試覆蓋率報告
npm run test:coverage
```

### 5. 訪問應用

打開瀏覽器訪問: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## API 端點

- `GET /`: 主頁面
- `GET /docs/chart-format`: 查看 Chart.js JSON 格式文檔
- `GET /api/chart-data/`: 獲取示例圖表數據
- `GET /api/data-files/`: 獲取所有可用數據文件
- `GET /api/file-data/`: 獲取特定文件的數據（轉換為 Chart.js 格式）
- `GET /api/file-content/`: 獲取原始文件內容（特別用於 JSON 檔案）
- `GET /api/file-structure/`: 獲取文件結構信息
- `POST /api/upload-file/`: 上傳數據文件（包含 JSON 格式驗證）
- `POST /api/chart-from-json/`: 從 JSON 數據直接生成圖表
- `POST /api/olap-operation/`: 執行 OLAP 操作
- `POST /upload-chart-image/`: 上傳圖表截圖

## 技術堆疊

- **後端**
  - FastAPI: 提供高性能 API 服務
  - Pandas & NumPy: 數據處理與分析
  - OpenPyXL & XLRD: Excel 檔案處理
  - Scikit-learn: 數據分析（可選）
  
- **前端**
  - Tailwind CSS: 現代化 UI 設計
  - Chart.js: 互動式圖表渲染
  - JavaScript: 前端邏輯處理
  
- **模板引擎**
  - Jinja2: 伺服器端模板渲染
  
- **開發工具**
  - Node.js & npm: 前端資源管理
  - Concurrently: 同時運行多個命令
  - UVicorn: ASGI 伺服器
  
## 更多資訊

查看 [使用指南](docs/usage_guide.md) 了解如何使用本應用程式的詳細功能。

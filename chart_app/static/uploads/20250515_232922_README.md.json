# Chart App

整合 FastAPI 後端、Jinja2 模板渲染、Tailwind CSS、Chart.js 以及 canvas 截圖功能的資料視覺化應用，支援多種資料來源和圖表類型。使用標準化的 JSON 資料格式，確保圖表正確顯示。

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
│   │   ├── script.js       # 前端主要功能實現
│   │   └── chart-json.js   # JSON 格式處理工具
│   └── uploads/            # 上傳檔案存放目錄
├── docs/                   # 文檔目錄
│   └── chart_formats.md    # Chart.js JSON 格式文檔
├── frontend/               # 前端開發檔案
│   ├── input.css           # Tailwind CSS 輸入檔案
│   └── tailwind.config.js  # Tailwind 設定檔
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

### 4. 訪問應用

打開瀏覽器訪問: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### 5. 資料目錄

應用程式會從以下目錄讀取數據文件：

- CSV 檔案: `/Users/aaron/Projects/DataScout/data/csv/`
- JSON 檔案: `/Users/aaron/Projects/DataScout/data/json/`
- Excel 檔案: `/Users/aaron/Projects/DataScout/data/excel/`
- 持久化檔案: `/Users/aaron/Projects/DataScout/persistence/`
- 上傳檔案: `/Users/aaron/Projects/DataScout/chart_app/static/uploads/`

請確保這些目錄存在，或者在 `app/main.py` 中修改這些路徑。

## JSON 資料標準格式

從 1.1.0 版本開始，本應用程式僅接受符合 Chart.js 標準的 JSON 格式，以確保圖表可靠顯示。這是為了解決之前因為靈活的資料格式處理導致的圖表顯示錯誤問題。

### 標準 Chart.js JSON 格式

```json
{
  "type": "line",
  "labels": ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05"],
  "datasets": [
    {
      "label": "銷售額",
      "data": [12800, 19500, 15200, 18100, 23000],
      "backgroundColor": "rgba(75, 192, 192, 0.6)",
      "borderColor": "rgba(75, 192, 192, 1.0)",
      "borderWidth": 2
    }
  ],
  "chartTitle": "2025年銷售表現"
}
```

### 格式驗證與轉換

- 上傳的 JSON 檔案會自動進行格式驗證
- 如果格式無效，會顯示詳細的錯誤訊息
- 系統提供 `ChartJSAdapter` 類別和前端處理工具，自動標準化資料格式
- 在 `/docs/chart-format` 路徑可查看完整格式文檔

### 提供的範例檔案

我們在 `/data/json/` 目錄下提供了幾個標準的 JSON 範例檔案：

- `example_line_chart.json`: 折線圖範例
- `example_bar_chart.json`: 長條圖範例
- `example_pie_chart.json`: 圓餅圖範例

您可以參考這些檔案來建立自己的 Chart.js JSON 資料。

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

- **後端**: 
  - FastAPI: 提供高性能 API 服務
  - Pandas & NumPy: 數據處理與分析
  - OpenPyXL & XLRD: Excel 檔案處理
  - Scikit-learn: 數據分析（可選）
  
- **前端**: 
  - Tailwind CSS: 現代化 UI 設計
  - Chart.js: 互動式圖表渲染
  - JavaScript: 前端邏輯處理
  
- **模板引擎**: 
  - Jinja2: 伺服器端模板渲染
  
- **開發工具**: 
  - Node.js & npm: 前端資源管理
  - Concurrently: 同時運行多個命令
  - UVicorn: ASGI 伺服器
  
## 更多資訊

查看 [使用指南](docs/usage_guide.md) 了解如何使用本應用程式的詳細功能。

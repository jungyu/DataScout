# Chart App

整合 FastAPI 後端、Jinja2 模板渲染、Tailwind CSS、Chart.js 以及 canvas 截圖功能的資料視覺化應用，支援多種資料來源和圖表類型。

## 功能

- FastAPI 後端提供 API 端點和網頁渲染
- Jinja2 模板引擎處理前端頁面
- Tailwind CSS 進行頁面美化
- Chart.js 繪製互動式圖表
- 多種資料來源支援：CSV、JSON、Excel 與持久化存儲
- 支援文件上傳功能
- 豐富的圖表類型：折線圖、長條圖、雷達圖、圓餅圖、環形圖、極座標圖、氣泡圖、散點圖
- 多種圖表主題選項
- 進階 OLAP 操作：分組聚合、透視表、滾動視窗計算
- 支持圖表下載為 PNG 或 WebP 格式
- 支持將圖表上傳到伺服器

## 專案結構

```
chart_app/
├── app/                    # FastAPI 應用主目錄
│   ├── main.py             # 主應用程式
│   └── __init__.py         # Python 模組標識
├── templates/              # HTML 模板目錄
│   └── index.html          # 主頁面模板
├── static/                 # 靜態檔案目錄
│   ├── css/                # CSS 檔案
│   │   └── output.css      # 編譯後的 Tailwind CSS
│   ├── js/                 # JavaScript 檔案
│   │   └── script.js       # 前端功能實現
│   └── uploads/            # 上傳檔案存放目錄
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

## API 端點

- `GET /`: 主頁面
- `GET /api/chart-data/`: 獲取示例圖表數據
- `GET /api/data-files/`: 獲取所有可用數據文件
- `GET /api/file-data/`: 獲取特定文件的數據
- `GET /api/file-structure/`: 獲取文件結構信息
- `POST /api/upload-file/`: 上傳數據文件
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

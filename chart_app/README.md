# Chart App

整合 FastAPI 後端、Jinja2 模板渲染、Tailwind CSS、Chart.js 以及 canvas 截圖功能的資料視覺化應用。

## 功能

- FastAPI 後端提供 API 端點和網頁渲染
- Jinja2 模板引擎處理前端頁面
- Tailwind CSS 進行頁面美化
- Chart.js 繪製互動式圖表
- 支持圖表類型切換（長條圖、折線圖、圓餅圖、雷達圖）
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
cd frontend
npm install
```

### 3. 編譯 Tailwind CSS

```bash
# 開發模式（監視文件變化）
npm run build:css

# 或生產模式（最小化）
npm run build:css:prod
```

### 4. 啟動 FastAPI 應用

```bash
uvicorn app.main:app --reload
```

### 5. 訪問應用

打開瀏覽器訪問: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## API 端點

- `GET /`: 主頁面
- `GET /api/chart-data/`: 獲取圖表數據
- `POST /upload-chart-image/`: 上傳圖表截圖

## 技術堆疊

- 後端: FastAPI, Pandas, NumPy
- 前端: Tailwind CSS, Chart.js, JavaScript
- 模板引擎: Jinja2
- 開發工具: Node.js, npm (用於 Tailwind CSS 編譯)

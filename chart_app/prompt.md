請建置整合了 FastAPI 後端、Jinja2 模板渲染、靜態檔案服務、資料 API、前端使用 Tailwind CSS、Chart.js 以及 JavaScript 進行圖表展示和 canvas 截圖的專案快速建立提詞 (Prompt)。

API 的資料來源可以是 JSON, CSV, Excel 等格式，或從專案中的 persistence (folder)layer 獲取資料，並使用 Pandas 進行 OLAP 操作 (例如 pivot_table 或 groupby)，然後將結果轉換為 Chart.js 可用的格式。


**Prompt for Python Project Setup: FastAPI + Tailwind + Chart.js + Canvas Capture**

請建立一個 Python Web 專案，使用 FastAPI 作為後端框架，實現以下功能：

1.  **後端 (FastAPI):**

      * 提供一個根目錄 (`/`) 的網頁服務，渲染一個 HTML 頁面。
      * 使用 Jinja2 模板引擎渲染 HTML 頁面。
      * 服務靜態檔案 (Static Files)，包括編譯後的 Tailwind CSS 檔案和前端 JavaScript 檔案。靜態檔案目錄結構應為 `static/css/` 和 `static/js/`。
      * 提供一個 API 端點 (例如 `/api/chart-data/`)，返回 JSON 格式的圖表資料。此資料可以模擬 OLAP 操作後的結果 (例如使用 Pandas)。
      * 提供一個 API 端點 (例如 `/upload-chart-image/`)，接收前端上傳的圖片檔案 (來自 canvas 截圖)。

2.  **前端:**

      * 使用 HTML 作為頁面結構。
      * 使用 Tailwind CSS 進行頁面樣式美化 (需要有一個 Tailwind 的編譯過程，後端只服務編譯後的 CSS)。
      * 使用 Chart.js 庫來繪製圖表。
      * 使用 JavaScript 從後端 `/api/chart-data/` API 獲取資料。
      * 使用獲取的資料初始化並渲染 Chart.js 圖表到 HTML 中的 `<canvas>` 元素上。
      * 提供按鈕觸發 JavaScript 函數，該函數使用 `<canvas>` 元素的 `toDataURL()` 或 `toBlob()` 方法來擷取圖表內容，並提供下載為 PNG 或 WebP 格式檔案的功能。

3.  **專案結構:**
    建立以下目錄和檔案結構：

    ```
    chart_app/
    ├── app/
    │   ├── main.py         # FastAPI 應用主檔案
    │   └── __init__.py     # Python 模組標識 (可選)
    ├── templates/
    │   └── index.html      # Jinja2 HTML 模板檔案
    ├── static/
    │   ├── css/
    │   │   └── output.css  # 編譯後的 Tailwind CSS 輸出檔案
    │   └── js/
    │       └── script.js   # 前端 JavaScript 檔案
    ├── frontend/           # 前端資源原始檔案 (用於 Tailwind 編譯等)
    │   ├── input.css       # Tailwind CSS 輸入檔案
    │   └── tailwind.config.js # Tailwind 設定檔
    ├── requirements.txt    # Python 相依性列表
    └── package.json        # npm 相依性及指令 (用於 Tailwind)
    ```

4.  **程式碼細節要求:**

      * `requirements.txt` 應包含 `fastapi`, `uvicorn[standard]`, `jinja2`, `python-multipart`, `pandas`, `numpy` (用於資料模擬)。
      * `package.json` 應包含 `tailwindcss`, `postcss`, `autoprefixer` 作為開發相依，並設定一個 build script (例如 `npm run build:css`) 來執行 Tailwind CLI 編譯。
      * `frontend/tailwind.config.js` 需要配置 `content` 來掃描 `templates/index.html` 以偵測使用的 class。
      * `frontend/input.css` 應包含基本的 `@tailwind` 指令。
      * `app/main.py` 中：
          * 初始化 FastAPI app。
          * 設定 `Jinja2Templates` 指向 `templates/` 目錄。
          * 設定 `StaticFiles` 指向 `static/` 目錄，掛載路徑為 `/static`。
          * 編寫根路由 (`/`) 函數，返回 `TemplatesResponse` 渲染 `index.html`。
          * 編寫 `/api/chart-data/` 路由函數，生成簡單的 Pandas DataFrame，執行 `pivot_table` 或 `groupby` 模擬 OLAP 聚合，轉換為適合 Chart.js 的 JSON 格式並返回 (例如包含 `labels` 和 `datasets`)。
          * 編寫 `/upload-chart-image/` 路由函數，接收 `UploadFile` 類型參數，將接收到的檔案儲存到伺服器上的某個位置 (例如 `static/uploads/`)。
      * `templates/index.html` 中：
          * 引用編譯後的 Tailwind CSS：`<link href="{{ url_for('static', path='/css/output.css') }}" rel="stylesheet">`
          * 引用 Chart.js (可使用 CDN)：`<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`
          * 創建一個 `<canvas id="myChart">` 元素作為圖表容器。
          * 創建兩個按鈕用於觸發截圖：`<button id="capturePngBtn">下載 PNG</button>` 和 `<button id="captureWebpBtn">下載 WebP</button>`。
          * 引用自定義的 JavaScript 檔案：`<script src="{{ url_for('static', path='/js/script.js') }}"></script>`
      * `static/js/script.js` 中：
          * 編寫一個異步函數 `WorkspaceChartData()`，使用 `Workspace` API 調用 `/api/chart-data/`，獲取 JSON 資料。
          * 編寫一個函數 `renderChart(data)`，獲取 canvas 元素，初始化一個 `Chart` 物件，並儲存 Chart 實例或 canvas 參考。
          * 在頁面載入後呼叫 `WorkspaceChartData()` 並將獲取的資料傳給 `renderChart()`。
          * 編寫一個函數 `captureChart(format)`，獲取 canvas 元素，使用 `canvas.toDataURL(format, quality)` 獲取 Data URL，創建一個 `<a>` 元素，設定 `href` 和 `download` 屬性，並觸發點擊。需要處理 WebP 的瀏覽器相容性檢查。
          * 給截圖按鈕添加事件監聽器，呼叫 `captureChart` 函數並傳入對應的格式 (`'image/png'`, `'image/webp'`)。
          * (可選) 編寫一個函數 `uploadChart(format)`，使用 `canvas.toBlob(callback, type, quality)` 獲取 Blob，使用 `FormData` 包裝，再使用 `Workspace` 發送到 `/upload-chart-image/` API。

5.  **操作步驟指南:**
    提供一個簡單的步驟說明，指導使用者如何：

      * 建立上述專案結構。
      * 安裝 Python 相依：`pip install -r requirements.txt`
      * 進入 `frontend/` 目錄。
      * 安裝 npm 相依：`npm install`
      * 編譯 Tailwind CSS：`npm run build:css` (或其他設定的指令)。
      * 返回專案根目錄。
      * 運行 FastAPI 應用：`uvicorn app.main:app --reload`
      * 在瀏覽器中訪問 `http://127.0.0.1:8000/`。
      * 說明點擊按鈕進行截圖。

確保提供的程式碼和配置是基本的、可運行的，並且包含了上述所有要求的關鍵部分。

# DataScout 數據可視化儀表板

DataScout是一個使用ApexCharts構建的數據可視化儀表板，採用多頁應用(MPA)架構設計，方便與FastAPI後端整合。

## 專案架構

```
frontend/
├── public/                  # 靜態資源
│   ├── components/          # 頁面組件
│   │   ├── charts/          # 圖表組件
│   │   ├── layout/          # 布局組件
│   │   └── ui/              # UI組件
│   ├── assets/              # 資源文件
│   │   ├── examples/        # 示例數據文件
│   │   └── images/          # 圖片
│   ├── *.html               # 各種圖表頁面
│   └── component-loader.js  # 組件加載器
├── src/                     # 源代碼(未來可用於前端構建)
└── docs/                    # 文檔
```

## 多頁面應用架構

本項目使用多頁應用(MPA)架構，每種圖表類型都有獨立的HTML頁面，便於通過URL直接訪問。主要頁面包括：

- `index.html` - 蠟燭圖(主頁)
- `line.html` - 折線圖
- `area.html` - 區域圖
- `column.html` - 柱狀圖
- 更多圖表頁面...

## 組件系統

組件系統使用原生JavaScript實現，通過`component-loader.js`加載HTML組件：

```html
<div id="sidebar" data-component="components/layout/Sidebar.html"></div>
```

主要組件包括：

- 布局組件：`Sidebar.html`, `Topbar.html`
- 圖表組件：`LineChartContent.html`, `AreaChartContent.html`等
- UI組件：圖表標題、數據選擇器等

## 數據模型

圖表數據使用JSON格式，存放在`/assets/examples/`目錄中，文件命名格式為：

```
apexcharts_圖表類型_內容.json
```

例如：`apexcharts_line_sales.json`

## FastAPI 整合指南

### 1. 後端API結構

為整合FastAPI，建議創建以下API端點：

```
/api/charts/{chart_type}     # 獲取特定類型的圖表數據
/api/data/{dataset_name}     # 獲取特定數據集
/api/upload                  # 上傳自定義數據文件
```

### 2. 前端整合

前端整合主要需要修改：

1. 數據加載函數，從靜態JSON改為API請求
2. 圖表初始化邏輯，使用從API獲取的數據
3. 檔案上傳功能，發送到FastAPI端點

### 3. 加載數據示例

目前的模擬加載數據功能：

```javascript
function loadLineData(dataType) {
  console.log(`Loading ${dataType} line chart data...`);
  fetch(`/assets/examples/apexcharts_line_sales.json`)
    .then(response => response.json())
    .then(data => {
      console.log("Loaded chart data:", data);
      // 使用數據更新圖表
    });
}
```

改為FastAPI調用：

```javascript
function loadLineData(dataType) {
  console.log(`Loading ${dataType} line chart data...`);
  fetch(`/api/charts/line?type=${dataType}`)
    .then(response => response.json())
    .then(data => {
      console.log("Loaded chart data:", data);
      // 使用數據更新圖表
    });
}
```

### 4. 文件上傳整合

需要修改文件上傳處理邏輯，將表單數據發送到FastAPI端點：

```javascript
const formData = new FormData();
formData.append('file', file);

fetch('/api/upload', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  // 處理上傳成功後的圖表更新
});
```

### 5. FastAPI 後端示例

```python
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import json

app = FastAPI()

@app.get("/api/charts/{chart_type}")
async def get_chart_data(chart_type: str, type: str = None):
    # 讀取對應的JSON文件或數據庫數據
    try:
        with open(f"data/{chart_type}_{type}.json", "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"message": f"Data for {chart_type} not found"}
        )

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    # 處理上傳的文件
    contents = await file.read()
    
    # 保存文件或處理數據
    # ...
    
    return {"filename": file.filename, "status": "success"}
```

### 6. 部署整合建議

1. 將前端靜態文件放在FastAPI的static目錄中
2. 使用FastAPI的靜態文件服務功能
3. 為了便於開發，可設置CORS允許前端開發服務器訪問API

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

通過以上步驟，可以輕易地將現有的多頁應用與FastAPI後端整合，實現從靜態JSON數據過渡到動態API數據的轉換。

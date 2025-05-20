# 前後端開發

DataScout 採用現代化的前後端架構，提供強大的數據視覺化和互動式儀表板功能。

## 架構概述

- **後端**: FastAPI + Pydantic + Jinja2
- **前端**: Alpine.js + DaisyUI (Tailwind CSS) + ApexCharts
- **構建工具**: Webpack + Tailwind CSS

## 快速開始

### 方法 1: 使用 VS Code 任務

在 VS Code 中，可以使用預先配置的任務來啟動開發環境：

1. 按下 `F1` 鍵，輸入 `Tasks: Run Task`
2. 選擇 `構建前端資源並複製到後端`
3. 選擇 `啟動前端開發服務`
4. 選擇 `啟動後端開發服務`

### 方法 2: 使用命令行

#### 構建前端資源

```bash
# 在專案根目錄執行
./scripts/build_frontend.sh
```

#### 啟動前端開發服務

```bash
cd web_frontend
./scripts/start_dev.sh
```

#### 啟動後端開發服務

```bash
cd web_service
./scripts/start_dev.sh
```

## 前端開發

前端使用現代化技術棧，包含：

- **Alpine.js**: 輕量級 JavaScript 框架，提供聲明式交互功能
- **DaisyUI**: 基於 Tailwind CSS 的組件庫，提供美觀的 UI 元素
- **ApexCharts**: 高度可定制的圖表庫，支持多種圖表類型
- **Tailwind CSS**: 實用優先的 CSS 框架

### 目錄結構

```
web_frontend/
├── src/
│   ├── css/           # CSS 文件
│   └── js/            
│       ├── main.js    # 主入口文件
│       ├── components/ # 組件文件
│       └── services/  # 服務 API 等
├── public/            # 靜態資源
└── dist/              # 構建輸出目錄
```

### 可用腳本

- `npm run build` - 構建生產環境資源
- `npm run dev` - 以開發模式監控 JS 文件變化
- `npm run build:css` - 以開發模式監控 CSS 文件變化
- `npm run start` - 同時啟動 JS 和 CSS 監控

## 後端開發

後端使用 FastAPI 提供高性能的 API 服務和模板渲染：

- **FastAPI**: 高性能的 Python API 框架
- **Pydantic**: 資料驗證和設定管理
- **Jinja2**: 模板引擎

### 目錄結構

```
web_service/
├── app/
│   ├── main.py       # 主程序入口
│   ├── apis/         # API 路由
│   └── core/         # 核心配置和依賴
├── static/           # 靜態檔案
└── templates/        # HTML 模板
```

## 頁面導航

- `/` - 主儀表板頁面
- `/chart-examples` - 圖表範例與組件展示
- `/api/docs` - API 文檔 (Swagger UI)
- `/api/redoc` - 替代 API 文檔 (ReDoc)

## 開發建議

1. **前後端協作**:
   - 修改前端代碼後，需要構建並複製到後端的 static 目錄
   - 使用 `構建前端資源並複製到後端` 任務可自動完成此過程

2. **新增圖表**:
   - 在 `web_frontend/src/js/components` 目錄下創建新的圖表組件
   - 使用 `advancedChart` Alpine 組件可快速創建互動式圖表

3. **添加新頁面**:
   - 在 `web_service/templates` 目錄下創建新的 HTML 模板
   - 在 `web_service/app/main.py` 中添加新的路由

4. **故障排除**:
   - 如果靜態資源未正確加載，請檢查構建輸出路徑
   - 確保 `web_service/static` 目錄中包含所需的 CSS 和 JS 文件

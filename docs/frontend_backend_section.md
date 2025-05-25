## 🔄 前後端開發

DataScout 提供了現代化的前後端分離架構，方便開發者分別進行前端和後端的開發與部署。

### 1. 前端開發（DaisyUI + ApexCharts + Alpine.js）

前端使用 Alpine.js 作為輕量級框架，結合 DaisyUI 和 ApexCharts 提供美觀的使用者介面和資料視覺化功能。

```bash
# 進入前端目錄
cd web_frontend

# 啟動開發伺服器（監視 JS 和 CSS 變更）
./scripts/start_dev.sh

# 或使用 npm 命令
npm run start
```

啟動後，可透過 `http://localhost:8080` 訪問前端應用。

### 2. 後端開發（FastAPI）

後端使用 FastAPI 提供高效能的 API 服務，支援非同步處理和自動生成 API 文檔。

```bash
# 進入後端目錄
cd web_service

# 啟動開發伺服器
./scripts/start_dev.sh
```

啟動後，可透過以下網址訪問：

- API 服務：`http://localhost:8000`
- API 文檔：`http://localhost:8000/docs`
- ReDoc 文檔：`http://localhost:8000/redoc`

### 3. 整合開發流程

若要同時進行前後端開發，建議使用以下流程：

1. 首先啟動前端開發伺服器

```bash
cd web_frontend
./scripts/start_dev.sh
```

2. 在另一個終端視窗啟動後端伺服器

```bash
cd web_service
./scripts/start_dev.sh
```

3. 當需要構建前端並整合到後端時，可使用構建腳本

```bash
./scripts/build_frontend.sh --output ./web_service/static
```

### 4. 常見問題排解

- **前端構建失敗**：確認已安裝所有 Node.js 依賴 `cd web_frontend && npm install`
- **後端啟動失敗**：確認已安裝所有 Python 依賴 `cd web_service && pip install -r requirements.txt`
- **靜態文件無法加載**：檢查 `web_service/static` 目錄是否包含前端構建的文件
- **API 無法訪問**：確認後端服務正在運行，且運行在正確的主機和端口上

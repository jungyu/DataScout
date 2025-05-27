# DataScout Web 開發技術手冊

**更新日期**: 2025年5月27日  
**版本**: v3.0 - 智能組件載入與自動化部署完整解決方案

---

## 目錄
1. [開發環境建置](#開發環境建置)
2. [前後端協作流程](#前後端協作流程)
3. [熱載入開發模式](#熱載入開發模式)
4. [智能組件載入系統](#智能組件載入系統)
5. [智能路徑處理](#智能路徑處理)
6. [首頁重定向機制](#首頁重定向機制)
7. [增強部署流程](#增強部署流程)
8. [自動化測試驗證](#自動化測試驗證)
9. [多環境支援](#多環境支援)
10. [常見問題排查](#常見問題排查)

---

## 一、開發環境建置

### 目的
確保每位開發者能快速啟動本地端前後端服務，並享有一致的開發體驗。

### 步驟
1. **安裝 Node.js (建議 LTS 版)**
2. **安裝 Python 3.9+ 與 venv**
3. **安裝前端依賴**
   ```bash
   cd web_frontend
   npm install
   ```
4. **安裝後端依賴**
   ```bash
   cd ../web_service
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

## 二、前後端協作流程

### 目標
- 前端專注於 UI/UX 與互動，後端專注於 API 與資料服務。
- 透過 API 介面協作，降低耦合。

### 溝通重點
- API 規格以 OpenAPI (Swagger) 文件為準。
- 前端開發時，API 路徑統一走 `/api` 前綴，方便 proxy。

---

## 三、熱載入開發模式

### 目的
提升開發效率，前端變更即時反映，後端 API 可獨立重啟。

### 操作步驟
1. **啟動前端 Vite Dev Server**
   ```bash
   cd web_frontend
   npm run dev
   ```
   - 開啟 [http://localhost:5173](http://localhost:5173/)
   - 支援 HMR（Hot Module Replacement）
2. **啟動後端 FastAPI**
   ```bash
   cd ../web_service
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```
   - API 文件：[http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)
3. **前端 API 請求自動 proxy 到後端**
   - 已於 `vite.config.js` 設定 `/api` 代理。

### 注意事項
- 前端開發時請勿直接修改 web_service/static 內容。
- 後端僅需專注 API，靜態資源由 Vite Dev Server 處理。
- **多頁應用（MPA）開發時，請用 `/static/xxx.html` 路徑測試各頁面。**
- **Sidebar 及所有靜態頁面連結，請加上 `/static/` 前綴。**
- **前端 fetch 範例資料時，請用 `/static/assets/examples/xxx.json` 路徑。**

---

## 四、正式部署流程

### 目的
將前端編譯產物與後端服務整合，供正式環境使用。

### 步驟
1. **前端編譯**
   ```bash
   cd web_frontend
   npm run build
   ```
2. **自動部署腳本**
   ```bash
   ./deploy_to_web_service.sh
   ```
   - 產物會自動複製到 `web_service/static` 與 `web_service/templates/index.html`
   - **所有 public/assets/examples/ 下的範例資料會強制同步到 `web_service/static/assets/examples/`，確保 fetch 不會 404。**
   - 靜態資源會自動備份到 `web_service/static/backup_YYYYMMDD_HHMMSS/`。
3. **後端服務靜態資源**
   - FastAPI 會自動服務 `/static/` 路徑下所有檔案。
   - **MPA 路徑請用 `/static/xxx.html` 存取。**
   - 根路由建議渲染 `index.html`：
     ```python
     @app.get("/", response_class=HTMLResponse)
     async def root(request: Request):
         return templates.TemplateResponse("index.html", {"request": request})
     ```
4. **SPA 路由支援（可選）**
   - 可加 fallback 路由，讓所有未知路徑都回傳 `index.html`。

---

## 五、自動化與最佳實踐

### 部署自動化腳本
- `web_frontend/deploy_to_web_service.sh` 範例（已自動備份、同步範例資料）：
  ```bash
  #!/bin/bash
  set -e
  npm run build
  WEB_SERVICE_PATH="../web_service"
  STATIC_PATH="$WEB_SERVICE_PATH/static"
  TEMPLATES_PATH="$WEB_SERVICE_PATH/templates"
  echo "📦 備份現有的靜態資源..."
  BACKUP_DIR="$STATIC_PATH/backup_$(date +%Y%m%d_%H%M%S)"
  mkdir -p "$BACKUP_DIR"
  mv "$STATIC_PATH"/* "$BACKUP_DIR" 2>/dev/null || true
  mkdir -p "$STATIC_PATH"
  mkdir -p "$TEMPLATES_PATH"
  cp -r dist/* "$STATIC_PATH/"
  # 額外複製範例資料
  mkdir -p "$STATIC_PATH/assets/examples"
  cp -r public/assets/examples/* "$STATIC_PATH/assets/examples/" 2>/dev/null || true
  cp dist/index.html "$TEMPLATES_PATH/index.html"
  echo "✅ 前端已成功部署到 web_service！"
  echo "- 靜態資源：$STATIC_PATH"
  echo "- 首頁模板：$TEMPLATES_PATH/index.html"
  echo "- 備份目錄：$BACKUP_DIR"
  ```

### 進階同步/監控
- 可用 `npm run build -- --watch` 或 `entr` 工具自動同步 build 結果到 static。
  ```bash
  find dist | entr -r ./deploy_to_web_service.sh
  ```

### 最佳實踐
- 開發時前後端分離，部署時靜態整合。
- API 路徑統一，方便 proxy 與部署。
- 版本控管：前後端分支命名一致，便於追蹤。
- **MPA 路徑、Sidebar 連結、fetch 路徑都需加 `/static/` 前綴。**

---

## 六、常見問題排查

### 啟動失敗
- 檢查 Python、Node.js 版本與依賴安裝。
- 檢查 venv 是否正確啟動。
- 檢查 port 是否被佔用。

### 靜態資源無法載入
- 確認 `deploy_to_web_service.sh` 是否正確執行。
- 檢查 FastAPI 靜態路徑設定。
- **確認所有 fetch 路徑、Sidebar 連結都加上 `/static/` 前綴。**
- **範例資料缺漏請補齊於 public/assets/examples/。**

### API 跨域問題
- 確認 FastAPI 已正確設定 CORS middleware。

### 其他
- 如遇特殊錯誤，請將終端訊息貼給團隊或 AI 助理協助排查。

---

> 本手冊適用於 DataScout 專案全體開發者，請依照章節指引進行開發與部署，確保團隊協作順暢。
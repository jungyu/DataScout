# DataScout Web 開發技術手冊

**更新日期**: 2025年5月28日  
**版本**: v3.1 - 智能組件載入與自動化部署完整解決方案

---

## 目錄

1. [開發環境建置](#開發環境建置)
2. [前端目錄結構說明](#前端目錄結構說明)
3. [前後端協作流程](#前後端協作流程)
4. [熱載入開發模式](#熱載入開發模式)
5. [智能組件載入系統](#智能組件載入系統)
6. [智能路徑處理](#智能路徑處理)
7. [首頁重定向機制](#首頁重定向機制)
8. [增強部署流程](#增強部署流程)
9. [自動化測試驗證](#自動化測試驗證)
10. [多環境支援](#多環境支援)
11. [常見問題排查](#常見問題排查)

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

## 二、前端目錄結構說明

### 核心資料夾功能

在 Vue.js 專案中，`public/` 和 `src/` 兩個資料夾都是原始檔案，但用途完全不同：

#### `src/` 資料夾 - 動態程式碼
**這是主要的原始程式碼資料夾**，包含：

```
src/
├── components/     # Vue 元件 (.vue 檔案)
├── views/         # 頁面元件
├── router/        # 路由配置
├── store/         # 狀態管理 (Vuex/Pinia)
├── assets/        # 需要編譯處理的資源
├── utils/         # 工具函數
├── styles/        # 全域樣式檔案
├── component-loader.js  # 智能組件載入系統
├── index.js       # 首頁重定向邏輯
└── main.js        # 應用程式入口點
```

**特性**：
- ✅ 會被 Webpack/Vite 編譯和優化
- ✅ 可用 `import` 語法導入
- ✅ 支援模組化開發
- ✅ 檔案會被重新命名 (添加 hash)
- ✅ 支援 tree-shaking、壓縮等優化

#### `public/` 資料夾 - 靜態資源
**靜態資源資料夾**，包含：

```
public/
├── index.html     # HTML 模板 (會被注入編譯後的資源)
├── favicon.ico    # 網站圖示
├── components/    # 靜態 HTML 組件
│   ├── layout/
│   │   ├── Sidebar.html
│   │   └── Header.html
│   └── charts/
│       ├── LineChart.html
│       └── AreaChart.html
├── images/        # 靜態圖片
├── fonts/         # 字體檔案
├── line.html      # 線圖頁面
├── area.html      # 面積圖頁面
└── robots.txt     # SEO 相關檔案
```

**特性**：
- ❌ 不會被編譯處理，直接複製到輸出目錄
- ❌ 需要使用絕對路徑引用
- 🔒 保持原始檔案名稱
- 🔒 適合大型靜態檔案或第三方庫

### 關鍵差異對比

| 特性 | `src/` | `public/` |
|------|--------|-----------|
| **編譯處理** | ✅ 會被 Webpack/Vite 編譯 | ❌ 直接複製到輸出目錄 |
| **模組導入** | ✅ 可用 `import` 導入 | ❌ 需要絕對路徑引用 |
| **檔案名稱** | 📝 會被重新命名 (hash) | 🔒 保持原始名稱 |
| **優化處理** | ✅ 壓縮、tree-shaking | ❌ 不處理 |
| **開發用途** | 動態程式邏輯 | 靜態資源檔案 |

### 使用建議

#### 放在 `src/assets/` 的情況：
- 需要編譯優化的圖片
- 元件專用的樣式檔案  
- 需要 tree-shaking 的資源
- JavaScript/TypeScript 模組

#### 放在 `public/` 的情況：
- 大型靜態檔案 (影片、PDF、大圖片)
- 第三方庫的靜態檔案
- 需要固定路徑的檔案
- SEO 相關檔案 (robots.txt, sitemap.xml)
- HTML 模板和靜態組件

### 建置結果

執行 `npm run build` 後產生的 `dist/` 目錄：

```bash
dist/
├── index.html          # 從 public/index.html 複製並注入編譯資源
├── assets/            # 從 src/ 編譯的檔案
│   ├── index-abc123.js    # 主要 JavaScript (含 hash)
│   ├── index-def456.css   # 主要 CSS (含 hash)
│   └── logo-ghi789.png    # 優化後的圖片
├── components/        # 從 public/components/ 直接複製
│   └── layout/
│       └── Sidebar.html
├── line.html          # 從 public/ 直接複製
├── area.html          # 從 public/ 直接複製
└── favicon.ico        # 從 public/ 直接複製
```

**總結**：兩個資料夾都很重要，`src/` 負責動態程式邏輯，`public/` 負責靜態資源，各司其職且不可混淆。

---

## 三、前後端協作流程

### 目標

- 前端專注於 UI/UX 與互動，後端專注於 API 與資料服務。
- 透過 API 介面協作，降低耦合。

### 溝通重點

- API 規格以 OpenAPI (Swagger) 文件為準。
- 前端開發時，API 路徑統一走 `/api` 前綴，方便 proxy。

---

## 四、熱載入開發模式

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
   - 支援多端口開發 (5173-5177, 3000, 8080)

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
- **開發環境會自動重定向首頁到 line.html**
- **側邊欄連結在開發環境不需 `/static/` 前綴**

---

## 五、智能組件載入系統

### 概述

新的組件載入系統支援智能環境檢測和路徑處理，能自動適應開發和正式環境。

### 核心特性

1. **智能環境檢測**
   
   ```javascript
   // 自動檢測開發環境端口
   const isDevelopment = ['5173', '5174', '5175', '5176', '5177', '3000', '8080']
     .includes(window.location.port);
   
   // 自動檢測正式環境
   const isProduction = window.location.pathname.includes('/static/') || 
     (!isDevelopment && window.location.port === '8000');
   ```

2. **動態路徑生成**
   
   ```javascript
   // 根據環境自動生成正確路徑
   const basePath = isDevelopment ? '' : '/static';
   const componentPath = `${basePath}/components/${component}.html`;
   ```

3. **增強錯誤處理**
   
   - 載入失敗時顯示友善錯誤訊息
   - 詳細的日誌記錄協助排錯
   - 載入狀態指示器

### 使用方式

在 HTML 中使用 `data-component` 屬性：

```html
<div data-component="layout/Sidebar"></div>
<div data-component="charts/LineChart"></div>
```

系統會自動載入對應的組件並插入到指定位置。

---

## 六、智能路徑處理

### 環境差異處理

系統自動處理開發環境和正式環境的路徑差異：

| 環境 | 首頁路徑 | 頁面路徑 | 組件路徑 |
|------|----------|----------|----------|
| 開發環境 | `/line.html` | `/area.html` | `/components/xxx.html` |
| 正式環境 | `/static/line.html` | `/static/area.html` | `/static/components/xxx.html` |

### 自動路徑轉換

部署腳本會自動處理路徑轉換：

```bash
# 側邊欄連結轉換
sed 's|href="/\([^s][^/]*\.html\)"|href="/static/\1"|g' \
    "$STATIC_PATH/components/layout/Sidebar.html"

# 重定向邏輯轉換
sed 's|window\.location\.href = .*/line\.html.*|window.location.href = "/static/line.html";|g' \
    "$STATIC_PATH/index.js"
```

---

## 七、首頁重定向機制

### 功能說明

系統會自動將首頁重定向到 line.html，並根據環境選擇正確路徑。

### 實現邏輯

```javascript
function checkAndRedirectToLine() {
  if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
    const isDevelopment = ['5173', '5174', '5175', '5176', '5177', '3000', '8080']
      .includes(window.location.port);
    const targetUrl = isDevelopment ? '/line.html' : '/static/line.html';
    window.location.href = targetUrl;
    return true;
  }
  return false;
}
```

### 測試驗證

可使用以下命令測試重定向功能：

```bash
# 開發環境測試
curl -I http://localhost:5173/

# 正式環境測試  
curl -I http://localhost:8000/
```

---

## 八、增強部署流程

### 自動化部署腳本

使用增強版部署腳本 `deploy_to_web_service_enhanced.sh`：

```bash
#!/bin/bash
set -e

echo "🚀 開始增強版部署流程..."

# 前端編譯
cd web_frontend
echo "📦 編譯前端..."
npm run build

# 設定路徑
WEB_SERVICE_PATH="../web_service"
STATIC_PATH="$WEB_SERVICE_PATH/static"
TEMPLATES_PATH="$WEB_SERVICE_PATH/templates"

# 備份現有檔案
echo "💾 備份現有檔案..."
BACKUP_DIR="$STATIC_PATH/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
if [ -d "$STATIC_PATH" ] && [ "$(ls -A $STATIC_PATH)" ]; then
    mv "$STATIC_PATH"/* "$BACKUP_DIR/" 2>/dev/null || true
fi

# 複製編譯產物
echo "📋 複製編譯產物..."
mkdir -p "$STATIC_PATH" "$TEMPLATES_PATH"
cp -r dist/* "$STATIC_PATH/"

# 路徑轉換處理
echo "🔄 處理路徑轉換..."
# [詳細的路徑轉換邏輯]

echo "✅ 部署完成！"
```

### 主要改進

1. **智能路徑轉換** - 自動處理開發/正式環境路徑差異
2. **完整備份機制** - 避免部署失敗時資料遺失  
3. **錯誤處理** - 部署過程中的錯誤會被捕獲並報告
4. **詳細日誌** - 每個步驟都有清楚的進度指示

---

## 九、自動化測試驗證

### 測試腳本

系統提供三個級別的測試驗證：

1. **快速測試** (`quick_test.sh`)
   
   ```bash
   ./scripts/quick_test.sh
   ```
   
   - 測試基本功能和組件載入
   - 驗證重定向機制
   - 檢查核心頁面可訪問性

2. **完整測試** (`final_test.sh`)
   
   ```bash
   ./scripts/final_test.sh
   ```
   
   - 包含所有快速測試項目
   - 測試複雜互動功能
   - 驗證數據載入和圖表渲染

3. **正式環境測試** (`test_production_deployment.sh`)
   
   ```bash
   ./scripts/test_production_deployment.sh
   ```
   
   - 測試正式環境部署結果
   - 驗證路徑轉換正確性
   - 檢查靜態資源可用性

### 測試涵蓋範圍

- ✅ 組件載入功能
- ✅ 路徑處理正確性  
- ✅ 首頁重定向機制
- ✅ 側邊欄導航連結
- ✅ 圖表頁面渲染
- ✅ 靜態資源載入
- ✅ API 端點響應
- ✅ 錯誤處理機制

---

## 十、多環境支援

### 支援的環境

| 環境類型 | 端口範圍 | 路徑前綴 | 用途 |
|----------|----------|----------|------|
| Vite 開發 | 5173-5177 | 無 | 主要開發環境 |
| 其他開發 | 3000, 8080 | 無 | 備用開發環境 |
| 正式環境 | 8000 | `/static` | 生產部署 |

### 環境檢測邏輯

```javascript
const PORT_DETECTION = {
  development: ['5173', '5174', '5175', '5176', '5177', '3000', '8080'],
  production: ['8000']
};

function detectEnvironment() {
  const port = window.location.port;
  
  if (PORT_DETECTION.development.includes(port)) {
    return 'development';
  }
  
  if (PORT_DETECTION.production.includes(port) || 
      window.location.pathname.includes('/static/')) {
    return 'production';
  }
  
  return 'unknown';
}
```

### 切換環境

開發者可以在不同環境間自由切換：

```bash
# 切換到開發環境
cd web_frontend && npm run dev

# 切換到正式環境  
cd web_service && source venv/bin/activate && uvicorn app.main:app --reload
```

---

## 十一、常見問題排查

### 組件載入失敗

**症狀**: 頁面顯示 CSS 但缺少動態內容

**解決方案**:
1. 檢查瀏覽器控制台是否有組件載入錯誤
2. 確認組件檔案路徑正確
3. 檢查 `component-loader.js` 是否正確載入

```bash
# 檢查組件檔案是否存在
ls -la web_frontend/public/components/

# 測試組件載入
./scripts/quick_test.sh
```

### 路徑問題

**症狀**: 頁面 404 或資源載入失敗

**解決方案**:
1. 確認當前環境 (開發/正式)
2. 檢查路徑前綴是否正確
3. 驗證部署腳本是否正確執行

```bash
# 檢查環境檢測
echo "當前端口: $(curl -s http://localhost:5173 > /dev/null && echo '5173' || echo '其他')"

# 重新部署
./web_frontend/deploy_to_web_service_enhanced.sh
```

### 重定向不工作

**症狀**: 首頁沒有自動跳轉到 line.html

**解決方案**:
1. 檢查 `index.js` 中的重定向邏輯
2. 確認頁面載入順序正確
3. 驗證環境檢測功能

```bash
# 測試重定向功能
./scripts/test_redirect_and_links.sh
```

### 部署後功能異常

**症狀**: 開發環境正常，正式環境有問題

**解決方案**:
1. 檢查路徑轉換是否正確執行
2. 驗證靜態檔案是否完整複製  
3. 確認環境變數和配置

```bash
# 檢查部署結果
ls -la web_service/static/

# 運行正式環境測試
./scripts/test_production_deployment.sh
```

### 效能問題

**症狀**: 頁面載入緩慢或響應遲緩

**解決方案**:
1. 檢查是否有大量 404 請求
2. 確認資源是否正確快取
3. 優化組件載入順序

```bash
# 檢查網路請求
curl -I http://localhost:8000/static/index.js

# 監控載入時間
time curl http://localhost:8000/static/line.html
```

---

## 附錄: 重要檔案說明

### 核心檔案

- `web_frontend/src/component-loader.js` - 智能組件載入系統
- `web_frontend/src/index.js` - 首頁重定向邏輯
- `web_frontend/deploy_to_web_service_enhanced.sh` - 增強部署腳本

### 測試檔案

- `scripts/quick_test.sh` - 快速功能測試
- `scripts/final_test.sh` - 完整功能測試  
- `scripts/test_production_deployment.sh` - 正式環境測試

### 文檔檔案

- `docs/frontend_fix_completion_report.md` - 組件載入修復報告
- `docs/redirect_and_links_modification_report.md` - 導航變更報告
- `docs/production_deployment_success_report.md` - 部署成功報告

---

> **本手冊記錄了 DataScout 前端系統的完整解決方案，包括智能組件載入、自動路徑處理、增強部署流程等。所有功能都經過完整測試驗證，可安全在生產環境使用。**

# DataScout Web Frontend 目錄結構說明

本文件說明 `/web_frontend` 目錄的標準結構、各資料夾用途，以及開發與部署流程。

---

## 目錄結構

```plaintext
web_frontend/
├── src/                  # 源代碼目錄
│   ├── components/       # React 組件
│   │   ├── charts/      # 圖表相關組件
│   │   ├── layout/      # 布局組件
│   │   └── ui/          # UI 組件
│   ├── pages/           # 頁面組件
│   ├── styles/          # CSS 樣式
│   └── utils/           # 工具函數
├── public/              # 靜態資源
│   ├── assets/
│   │   └── examples/    # 圖表範例 JSON 檔案
│   ├── components/      # 舊版組件（待遷移）
│   │   ├── charts/     # 圖表相關組件
│   │   └── layout/     # 頁面布局組件
│   └── ...（其他靜態檔案）
├── scripts/             # 自動化腳本
│   ├── start_dev.sh    # 開發服務器啟動腳本
│   ├── deploy_to_web_service.sh  # 部署腳本
│   └── chart_diagnosis_and_fix.py  # 圖表診斷工具
├── tests/              # 測試腳本（pytest 格式）
├── package.json        # 專案配置與依賴
├── vite.config.js     # Vite 配置
├── tsconfig.json      # TypeScript 配置
└── README.md          # 專案說明
```

---

## 各目錄用途

### src/

源代碼目錄，包含所有 React 組件與業務邏輯：

- **components/**：React 組件
  - **charts/**：各種圖表組件實現（BarChart、LineChart、CandlestickChart 等）
  - **layout/**：頁面布局組件（Navbar、Sidebar、Footer）
  - **ui/**：通用 UI 組件（Button、Card、DataSelector 等）
- **pages/**：頁面級組件（Dashboard、ChartExamples、ApiDocs 等）
- **styles/**：CSS 樣式文件
- **utils/**：工具函數與 helpers（如 chartHelpers.js）

### public/

靜態資源目錄：

- **assets/examples/**：圖表範例的 JSON 配置檔案
- **components/**：舊版組件（計劃遷移至 src/components）
  - **charts/**：圖表相關組件
  - **layout/**：頁面布局組件
- 其他靜態資源（JS、CSS、圖片等）

### scripts/

核心自動化腳本：

- **start_dev.sh**：
  - 啟動 Vite 開發伺服器
  - 自動檢查並安裝依賴
  - 提供本地開發環境 (`http://localhost:5173`)
  
- **deploy_to_web_service.sh**：
  - 編譯前端資源
  - 自動備份現有靜態檔案
  - 複製到後端服務目錄
  - 處理生產環境路徑差異
  - 生成部署報告
  
- **chart_diagnosis_and_fix.py**：
  - 診斷圖表配置問題
  - 自動修復常見錯誤
  - 支援 `--diagnose` 和 `--fix` 模式

### tests/

前端測試腳本存放目錄：

- 使用 pytest 框架
- 檔名以 `test_` 開頭
- 包含圖表功能、組件載入等測試

---

## 開發與部署流程

### 1. 開發準備

```bash
cd /web_frontend
npm install              # 安裝依賴
./scripts/start_dev.sh   # 啟動開發服務器
```

### 2. 開發與測試

- 訪問 `http://localhost:5173` 進行開發
- 使用 `tests/` 下的測試腳本驗證功能
- 需要時使用 `chart_diagnosis_and_fix.py` 檢查圖表

### 3. 部署

```bash
./scripts/deploy_to_web_service.sh
```

- 自動執行編譯、備份、部署
- 檢查部署報告確認狀態
- 驗證生產環境功能

---

## 注意事項

### 清理規範

- 移除所有暫存檔案（`*_bak`、`*_old`、`*_tmp`）
- 測試檔案統一放在 `tests/`
- 說明文件統一放在 `docs/`
- `public/components` 下的組件逐步遷移至 `src/components`

### 依賴管理

- 使用 `package.json` 管理 npm 依賴
- 使用 `requirements.txt` 管理 Python 依賴
- 定期更新依賴版本

### 安全性

- 部署前備份重要檔案
- 確保生產環境路徑正確
- 注意靜態資源的訪問權限

---

## 相關文件

- 詳細開發規範：`/docs/frontend_development_guide.md`
- API 文件：`/docs/api.md`
- 組件說明：`/docs/frontend_component_guide.md`
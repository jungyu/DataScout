# Web Frontend 模組

## 專案概述

Web Frontend 模組提供了現代化的用戶界面，用於數據可視化和交互。本模組使用 React 和 TypeScript 構建，並採用 Tailwind CSS 進行樣式設計。

## 環境設置

### 1. 安裝 Node.js

確保已安裝 Node.js 和 npm：
```bash
# 檢查 Node.js 版本
node --version  # 應為 v20.11.1 或更高

# 檢查 npm 版本
npm --version   # 應為 v10.2.4 或更高
```

### 2. 安裝依賴

```bash
# 進入 web_frontend 目錄
cd web_frontend

# 安裝依賴套件
npm install
```

### 3. 環境變數設置

在專案根目錄創建 `.env` 文件，添加以下配置：

```env
# API 配置
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_VERSION=v1

# 其他配置
REACT_APP_ENV=development
```

## 目錄結構

```
web_frontend/
├── src/           # 源代碼
│   ├── components/  # React 組件
│   ├── pages/      # 頁面組件
│   ├── services/   # API 服務
│   ├── styles/     # 樣式文件
│   └── utils/      # 工具函數
├── public/        # 靜態資源
└── tests/         # 測試文件
```

## 使用方式

### 開發環境

```bash
# 啟動開發服務器
npm start
```

### 生產環境

```bash
# 構建生產版本
npm run build

# 預覽生產版本
npm run preview
```

## 主要功能

1. 數據可視化儀表板
2. 圖表展示
3. 數據過濾和搜索
4. 響應式設計
5. 主題切換

## 技術棧

- **前端框架**: React 18
- **語言**: TypeScript
- **樣式**: Tailwind CSS
- **圖表**: Chart.js
- **HTTP 客戶端**: Axios
- **構建工具**: Vite

## 注意事項

1. 確保 Node.js 版本符合要求
2. 檢查環境變數是否正確設置
3. 確保所有依賴都已正確安裝
4. 注意跨域請求配置

## 開發指南

### 代碼風格

```bash
# 運行代碼檢查
npm run lint

# 運行類型檢查
npm run type-check
```

### 測試

```bash
# 運行單元測試
npm run test

# 運行端到端測試
npm run test:e2e
```

### 構建優化

```bash
# 分析構建大小
npm run analyze
```

## 依賴套件說明

- `react`: 前端框架
- `typescript`: 類型系統
- `tailwindcss`: CSS 框架
- `chart.js`: 圖表庫
- `axios`: HTTP 客戶端
- `postcss`: CSS 處理器
- `autoprefixer`: CSS 前綴處理 
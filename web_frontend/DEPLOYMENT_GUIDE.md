# DataScout 前端部署指南

## 概述

本指南說明如何將 DataScout Web 前端從開發環境部署到生產環境（web_service）。

## 部署腳本

### 增強版部署腳本
- **位置**: `/web_frontend/deploy_to_web_service_enhanced.sh`
- **版本**: v3.1
- **功能**: 智能路徑轉換、環境檢測、備份機制

### 使用方法

```bash
# 1. 進入前端目錄
cd /Users/aaron/Projects/DataScout/web_frontend

# 2. 執行增強部署腳本
chmod +x deploy_to_web_service_enhanced.sh
./deploy_to_web_service_enhanced.sh
```

## 部署流程

### 自動化步驟
1. **前端編譯**: 執行 `npm run build` 編譯前端資源
2. **備份創建**: 自動備份現有靜態檔案
3. **目錄創建**: 確保必要目錄存在
4. **檔案複製**: 複製編譯產物和額外檔案
5. **路徑轉換**: 智能轉換開發環境路徑為生產環境路徑
6. **驗證檢查**: 驗證部署完整性
7. **報告生成**: 生成詳細部署報告

### 智能功能

#### 路徑轉換
```bash
# 側邊欄連結轉換
href="/line.html" → href="/static/line.html"
href="/scatter.html" → href="/static/scatter.html"

# 重定向邏輯轉換  
window.location.href = "/line.html" → window.location.href = "/static/line.html"
```

#### 環境檢測
- 自動檢測開發/生產環境
- 支援多種開發端口 (5173, 3000, 8080 等)
- 根據環境調整路徑處理策略

## 驗證步驟

### 部署後檢查
```bash
# 1. 啟動 web_service
cd ../web_service
source venv/bin/activate  
uvicorn app.main:app --reload

# 2. 測試關鍵頁面
curl http://localhost:8000/
curl http://localhost:8000/static/line.html
curl http://localhost:8000/static/scatter.html

# 3. 檢查組件載入
# 在瀏覽器開發者工具中確認無 404 錯誤
```

### 功能驗證
- [ ] 首頁自動重定向
- [ ] 側邊欄導航正常
- [ ] 圖表頁面載入正常
- [ ] 組件動態載入正常
- [ ] 靜態資源服務正常

## 故障排除

### 常見問題

#### 404 錯誤 (組件載入失敗)
```bash
# 檢查組件檔案是否存在
ls -la web_service/static/components/

# 檢查路徑轉換是否正確
grep "href=" web_service/static/components/layout/Sidebar.html
```

#### 重定向失效
```bash  
# 檢查 index.js 中的重定向邏輯
grep "window.location.href" web_service/static/index.js
```

#### 靜態資源 404
```bash
# 檢查 FastAPI 靜態檔案配置
grep "StaticFiles" web_service/app/main.py
```

### 恢復方法

#### 從備份恢復
```bash
cd web_service/static
cp -r backup_YYYYMMDD_HHMMSS/* .
```

#### 重新部署
```bash
cd web_frontend  
./deploy_to_web_service_enhanced.sh
```

## 最佳實踐

### 部署前準備
1. 確認前端代碼無錯誤
2. 測試開發環境功能正常
3. 備份重要設定檔案

### 部署中注意事項
1. 檢查腳本執行日誌
2. 確認路徑轉換結果
3. 驗證關鍵檔案存在

### 部署後維護
1. 監控服務運行狀態
2. 檢查錯誤日誌
3. 定期清理備份檔案

## 相關檔案

### 關鍵檔案位置
```
web_frontend/
├── deploy_to_web_service_enhanced.sh    # 增強部署腳本
├── scripts/deploy_to_web_service.sh     # 原始部署腳本
├── src/component-loader.js              # 智能組件載入器
└── src/index.js                         # 重定向邏輯

web_service/
├── static/                              # 靜態資源目錄
├── templates/                           # 模板目錄
├── DEPLOYMENT_VERIFICATION_REPORT.md    # 驗證報告
└── deployment_enhanced_report_*.md      # 部署報告
```

### 設定檔案
- `web_service/app/main.py`: FastAPI 主應用
- `web_frontend/vite.config.js`: Vite 編譯設定
- `web_frontend/package.json`: NPM 腳本設定

---
**文件版本**: v3.1  
**最後更新**: 2025年5月28日  
**適用版本**: DataScout Web v3.1+

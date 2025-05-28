# Web Frontend 腳本

這個目錄包含了用於開發和維護 DataScout Web 前端的各種工具腳本。

## 腳本說明

### 開發工具

#### start_dev.sh
啟動前端開發服務器的腳本。

**使用方式**：
```bash
cd /Users/aaron/Projects/DataScout/web_frontend
./scripts/start_dev.sh
```

### 部署工具

#### deploy_to_web_service.sh
自動化部署腳本，將 web_frontend 編譯產物部署到 web_service。  

**功能**：
- 編譯前端資源
- 備份舊有靜態檔案
- 複製到後端服務目錄
- 清理暫存檔案
- 詳細部署過程資訊

**使用方式**：
```bash
cd /Users/aaron/Projects/DataScout/web_frontend
./scripts/deploy_to_web_service.sh
```

### 診斷和修復工具

#### chart_diagnosis_and_fix.py
整合診斷與修復功能的單一入口腳本，建議優先使用。

**功能**：
- 診斷 pie、donut、treemap、polar 圖表的 HTML、JSON 結構與資料正確性
- 自動修復常見問題（如 chart.type 缺失、polararea→polar）
- 支援 CLI 參數：
  - `--diagnose` 僅診斷（預設）
  - `--fix` 執行自動修復

**使用方式**：
```bash
cd /Users/aaron/Projects/DataScout/web_frontend
python scripts/chart_diagnosis_and_fix.py --diagnose  # 僅診斷
python scripts/chart_diagnosis_and_fix.py --fix       # 診斷並自動修復
```

> 本腳本已整合原 `chart_diagnosis_final.py`、`chart_type_fixes.py` 之功能，原檔案已刪除。

## 使用指南

### 開發流程
1. 使用 `start_dev.sh` 啟動開發服務器
2. 進行開發和測試
3. 使用 `tests/` 目錄中的測試腳本驗證功能
4. 使用部署腳本將變更部署到生產環境

### 問題排除
1. 使用診斷腳本檢查問題
2. 執行修復腳本解決常見問題
3. 使用測試腳本驗證修復結果

## 注意事項

- 執行腳本前請確保有適當的執行權限
- 某些腳本可能需要特定的環境依賴
- 建議在執行修復腳本前備份重要檔案

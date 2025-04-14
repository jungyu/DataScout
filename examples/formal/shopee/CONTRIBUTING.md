# 貢獻指南

感謝您對 Shopee 爬蟲模組的興趣！我們歡迎任何形式的貢獻，包括但不限於：

- 報告問題
- 提交功能建議
- 改進文檔
- 提交程式碼修改

## 如何貢獻

### 報告問題

1. 在提交問題前，請先搜尋是否已經存在相關問題
2. 使用問題模板提交問題
3. 提供詳細的問題描述和重現步驟
4. 附上相關的錯誤訊息和日誌

### 提交功能建議

1. 描述您想要的功能
2. 說明為什麼需要這個功能
3. 提供使用場景和示例
4. 如果可以，提供實現思路

### 改進文檔

1. 修正錯別字和語法錯誤
2. 改進文檔結構和格式
3. 添加更多示例和說明
4. 翻譯文檔到其他語言

### 提交程式碼修改

1. Fork 專案
2. 創建功能分支
3. 提交修改
4. 發起 Pull Request

## 開發指南

### 環境設置

```bash
# 克隆專案
git clone https://github.com/datascout/shopee-crawler.git

# 進入專案目錄
cd shopee-crawler

# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt

# 安裝開發依賴
pip install -r requirements-dev.txt
```

### 程式碼風格

- 遵循 PEP 8 規範
- 使用 Black 進行程式碼格式化
- 使用 isort 進行導入排序
- 使用 flake8 進行程式碼檢查

### 提交規範

提交訊息格式：

```
<類型>: <描述>

[可選的詳細描述]

[可選的相關問題]
```

類型包括：
- feat: 新功能
- fix: 修復問題
- docs: 文檔修改
- style: 程式碼格式修改
- refactor: 程式碼重構
- test: 測試相關
- chore: 其他修改

### 測試

- 編寫單元測試
- 確保所有測試通過
- 保持測試覆蓋率

## 行為準則

- 尊重他人
- 友善交流
- 理性討論
- 遵守規範

## 授權

貢獻的程式碼將採用與專案相同的 MIT 授權條款。 
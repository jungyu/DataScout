# 原型程式說明

本目錄包含不依賴框架的獨立爬蟲程式，這些程式展示了基本的爬蟲實作方式，可以與框架版本進行對比。

## 目錄結構

```
examples/prototype/
├── google/          # Google 搜尋爬蟲
├── ubereats/        # UberEats 爬蟲
├── price_house/     # 實價登錄爬蟲
└── pcc/             # 政府電子採購網爬蟲
```

## Google 搜尋爬蟲

### 功能說明
- 基本搜尋功能
- 搜尋結果擷取
- 分頁處理
- 結果儲存

### 執行指令
```bash
# 基本搜尋
python examples/prototype/google/search.py

# 使用 PTS 搜尋
python examples/prototype/google/search_pts.py
```

## UberEats 爬蟲

### 功能說明
- 餐廳搜尋
- 餐點選擇
- 購物車操作
- 訂單處理

### 執行指令
```bash
# 搜尋餐廳
python examples/prototype/ubereats/search.py

# 處理訂單
python examples/prototype/ubereats/order.py
```

## 實價登錄爬蟲

### 功能說明
- 地區選擇
- 建物類型篩選
- 價格區間設定
- 資料擷取與儲存

### 執行指令
```bash
# 查詢實價登錄
python examples/prototype/price_house/query.py
```

## 政府電子採購網爬蟲

### 功能說明
- 決標公告查詢
- 招標公告查詢
- 資料擷取與儲存

### 執行指令
```bash
# 查詢決標公告
python examples/prototype/pcc/award.py

# 查詢招標公告
python examples/prototype/pcc/tender.py
```

## 與框架版本的差異

1. **程式結構**
   - 原型版本：單一檔案，所有功能集中實作
   - 框架版本：模組化設計，功能分散於不同類別

2. **錯誤處理**
   - 原型版本：基本的 try-except 處理
   - 框架版本：完整的錯誤處理機制，包含重試、記錄等

3. **配置管理**
   - 原型版本：直接讀取 JSON 配置檔
   - 框架版本：使用配置管理類別，支援多環境

4. **瀏覽器控制**
   - 原型版本：直接使用 Selenium WebDriver
   - 框架版本：封裝瀏覽器控制，提供更多功能

5. **資料處理**
   - 原型版本：基本的資料擷取與儲存
   - 框架版本：完整的資料處理流程，包含驗證、轉換等

## 使用建議

1. 建議先執行原型版本，了解基本的爬蟲實作方式
2. 再參考框架版本，學習如何優化程式結構
3. 可以對比兩種版本的差異，理解框架帶來的優勢
4. 根據需求選擇合適的實作方式 
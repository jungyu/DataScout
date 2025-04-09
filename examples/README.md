# 爬蟲範例目錄

本目錄包含各種網頁爬蟲的範例程式和配置。

## 目錄結構

```
examples/
├── src/                    # 爬蟲程式碼
│   ├── google/            # Google 搜尋爬蟲
│   ├── price_house/       # 實價登錄爬蟲
│   ├── gov_procurement/   # 政府採購網爬蟲
│   ├── shopee/            # Shopee 爬蟲
│   └── ubereats/          # Uber Eats 爬蟲
│
├── templates/             # 爬蟲配置模板
│   ├── google/            # Google 搜尋模板
│   │   ├── basic/        # 基本配置
│   │   └── formal/       # 正式配置
│   ├── price_house/      # 實價登錄模板
│   │   ├── basic/        # 基本配置
│   │   └── formal/       # 正式配置
│   ├── gov_procurement/  # 政府採購網模板
│   │   ├── basic/        # 基本配置
│   │   └── formal/       # 正式配置
│   ├── shopee/           # Shopee 模板
│   │   ├── basic/        # 基本配置
│   │   └── formal/       # 正式配置
│   └── ubereats/         # Uber Eats 模板
│       ├── basic/        # 基本配置
│       └── formal/       # 正式配置
│
└── data/                 # 爬蟲輸出數據
    ├── google/           # Google 搜尋結果
    ├── price_house/      # 實價登錄數據
    ├── gov_procurement/  # 政府採購網數據
    ├── shopee/           # Shopee 商品數據
    └── ubereats/         # Uber Eats 餐廳數據
```

## 配置檔案說明

每個爬蟲範例都包含以下配置檔案：

1. `config.json`：基本配置檔案，包含：
   - 瀏覽器設定
   - 反爬蟲設定
   - 代理設定
   - 驗證碼設定
   - 日誌設定
   - 輸出設定
   - 重試機制

2. `query_params.json`：查詢參數檔案，包含：
   - 搜尋條件
   - 日期範圍
   - 批次大小
   - 延遲時間

## 使用方式

1. 選擇適當的模板目錄（basic 或 formal）
2. 複製所需的配置檔案到專案目錄
3. 根據需求修改配置
4. 執行爬蟲程式

範例：
```bash
# 執行 Google 搜尋範例
python src/google/search.py --config templates/google/basic/config.json
```

## 數據輸出

爬蟲的輸出數據將保存在 `/examples/data/` 目錄下，按照不同的爬蟲類型分類：

1. 每個爬蟲都有獨立的子目錄
2. 數據以 JSON 或 CSV 格式保存
3. 檔名包含時間戳記，方便追蹤
4. 錯誤日誌和截圖也會保存在相應目錄

## 注意事項

1. 請遵守網站的使用條款和爬蟲政策
2. 建議使用適當的請求間隔，避免對目標網站造成負擔
3. 使用代理服務時，請確保代理服務的可用性
4. 定期更新配置檔案以適應網站的變化

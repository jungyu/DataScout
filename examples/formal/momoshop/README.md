# MomoShop 爬蟲

MomoShop 爬蟲是一個專門用於爬取 Momo 購物網站的爬蟲工具，提供多種搜尋和資料擷取功能。

## 功能特點

- 🔍 關鍵字搜尋：支援商品關鍵字搜尋
- 📑 分類瀏覽：支援按分類瀏覽商品
- 📦 商品詳情：支援獲取商品詳細資訊
- 🔄 分頁支援：支援多頁資料擷取
- 📝 詳細日誌：提供完整的執行日誌

## 安裝需求

- Python 3.8+
- Playwright
- 其他依賴套件（見 requirements.txt）

## 使用方法

### 1. 關鍵字搜尋

使用關鍵字搜尋商品：

```bash
python -m examples.formal.momoshop -method search -keyword "筆電" -page 1
```

參數說明：
- `-method search`：指定使用搜尋功能
- `-keyword`：搜尋關鍵字
- `-page`：頁碼（選填，預設為 1）

### 2. 分類瀏覽

瀏覽特定分類的商品：

```bash
python -m examples.formal.momoshop -method category -category_id "3c" -page 1
```

參數說明：
- `-method category`：指定使用分類瀏覽功能
- `-category_id`：分類 ID
- `-page`：頁碼（選填，預設為 1）

### 3. 商品詳情

獲取特定商品的詳細資訊：

```bash
python -m examples.formal.momoshop -method product -product_id "123456"
```

參數說明：
- `-method product`：指定使用商品詳情功能
- `-product_id`：商品 ID

## 輸出格式

### 搜尋結果格式

```json
{
    "name": "商品名稱",
    "price": "商品價格",
    "link": "商品連結",
    "image": "商品圖片連結"
}
```

### 商品詳情格式

```json
{
    "name": "商品名稱",
    "price": "商品價格",
    "description": "商品描述",
    "specs": [
        {
            "key": "規格項目",
            "value": "規格值"
        }
    ]
}
```

## 注意事項

1. 請確保網路連線穩定
2. 建議使用代理伺服器以避免 IP 被封鎖
3. 遵守網站的爬蟲政策和使用規範
4. 適當控制爬取頻率，避免對目標網站造成負擔

## 錯誤處理

程式會處理以下錯誤情況：
- 網路連線錯誤
- 頁面載入超時
- 元素未找到
- 驗證碼處理失敗

所有錯誤都會記錄在日誌中，方便追蹤和除錯。

## 開發者資訊

- 作者：DataScout Team
- 版本：1.0.0
- 最後更新：2024-04-16 
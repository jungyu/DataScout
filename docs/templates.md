# 爬蟲模板格式說明

## 簡介

本文檔說明爬蟲系統的模板格式。模板採用 JSON 格式，用於定義如何爬取特定網站的結構化數據。

## 模板基本結構

```json
{
  "site_name": "網站名稱",
  "base_url": "https://example.com",
  "encoding": "utf-8",
  "request": {},
  "login": {},
  "delays": {},
  "list_page": {},
  "pagination": {},
  "detail_page": {},
  "data_processing": {}
}
```

## 模板字段說明

### 基本資訊
- `site_name`：網站名稱
- `base_url`：網站基礎URL
- `encoding`：網站編碼格式（如 utf-8、big5）
- `description`：模板描述（選填）
- `version`：版本號（選填）
- `author`：作者（選填）
- `created_at`/`updated_at`：建立/更新日期（選填）

### 請求設定 (request)
請求相關配置，包含：
- HTTP 方法（GET/POST）
- 固定與可變參數
- 請求標頭
- Cookie 設定

### 登入設定 (login)
如需登入才能爬取，可配置：
- 登入頁面 URL
- 表單元素定位與操作方式
- 登入成功檢查條件

### 延遲設定 (delays)
各種操作間的延遲時間：
- 頁面載入後等待
- 頁面間跳轉
- 項目處理間隔

### 列表頁設定 (list_page)
定義如何從列表頁面擷取資料：
- 列表容器定位
- 項目選擇器
- 欄位擷取規則
- 排除條件

### 分頁設定 (pagination)
處理多頁資料的方式：
- 下一頁按鈕定位
- 頁數判斷方式
- 最大頁數限制

### 詳情頁設定 (detail_page)
定義詳情頁面的資料擷取：
- 內容區塊定位
- 欄位擷取規則
- 頁面操作（如展開、切換分頁）

### 資料處理 (data_processing)
資料後處理相關設定：
- 資料清理規則
- 欄位對應
- 後處理邏輯

## 使用範例

完整範例請參考 `examples/` 目錄下的模板檔案：
- `basic_template.json`：基礎爬蟲模板
- `login_template.json`：需登入網站的模板
- `pagination_template.json`：多頁面爬取模板
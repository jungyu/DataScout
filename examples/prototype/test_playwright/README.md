# Nikkei Asia 爬蟲程式

這是一個使用 Playwright 開發的爬蟲程式，用於爬取 Nikkei Asia 網站的新聞內容。

## 功能特點

- 支援關鍵字搜尋
- 自動翻頁爬取搜尋結果
- 爬取文章詳細內容
- 包含 meta 數據（URL、爬取時間、分類、作者等）
- 結果保存為 JSON 格式

## 安裝步驟

1. 安裝 Python 依賴：
```bash
pip install -r requirements.txt
```

2. 安裝 Playwright 瀏覽器：
```bash
playwright install
```

## 使用方法

直接運行 Python 腳本：
```bash
python nikkei_scraper.py
```

預設會搜尋 "fed usd" 關鍵字，並將結果保存在 `nikkei_results.json` 檔案中。

## 自定義搜尋

要修改搜尋關鍵字，可以編輯 `nikkei_scraper.py` 中的 `main()` 函數：

```python
def main():
    scraper = NikkeiScraper()
    results = scraper.scrape_search_results("你的關鍵字")  # 修改這裡
    scraper.save_results()
```

## 注意事項

- 程式預設最多爬取 5 頁搜尋結果
- 每次請求之間有 2 秒的延遲，以避免對伺服器造成過大負擔
- 爬取的結果會包含以下欄位：
  - title: 文章標題
  - publish_time: 發布時間
  - content: 文章內容
  - meta_data: 包含 URL、爬取時間、分類、作者等額外資訊 
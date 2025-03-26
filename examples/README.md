# Selenium 爬蟲框架使用範例

這個目錄包含了使用 Selenium 爬蟲框架的範例程式碼，幫助使用者快速上手。

## 範例說明

### 1. 基礎 Selenium 使用 (`basic_usage.py`)

這個範例展示了如何使用 Selenium WebDriver 完成基本的網頁爬取任務：
- 開啟 Google 搜尋頁面
- 執行關鍵字搜尋
- 提取搜尋結果的標題、連結和描述
- 將結果保存為 JSON 格式

執行方式：
```bash
python examples/basic_usage.py
```

### 2. 模板化爬蟲 (`template_crawler_example.py`)

這個範例展示了如何使用框架的模板化爬蟲功能：
- 使用 JSON 模板定義爬取規則
- 自動處理頁面導航和元素提取
- 將爬取結果保存為結構化數據

執行方式：
```bash
python examples/template_crawler_example.py
```

使用的模板文件為 `basic_template.json`，展示了如何定義網頁元素的選擇器和提取規則。

### 3. 其他範例

更多進階範例將陸續添加，包括：
- 自動處理驗證碼
- 處理動態加載內容
- 模擬用戶登入
- 自動填寫表單
- 多頁面爬取與導航

## 快速開始

1. 確保已安裝所有依賴：
```bash
pip install -r requirements.txt
```

2. 確保已安裝與您的 Chrome 瀏覽器版本匹配的 ChromeDriver

3. 執行範例：
```bash
python examples/basic_usage.py
```

## 客製化範例

您可以修改範例中的 URL、選擇器和其他參數來適應您的爬取需求。對於模板化爬蟲，只需修改 JSON 模板文件，無需修改 Python 代碼即可爬取不同網站。

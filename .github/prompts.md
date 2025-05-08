# DataScout 提示與上下文

## 專案背景
DataScout 是一個高級網頁自動化與數據採集框架，專注於提供強大的反檢測功能，適用於開發者進行網頁數據抓取與處理。

## 提示設計
以下是適合本專案的提示設計，幫助開發者更好地使用 DataScout 框架：

### 基本功能提示
- **如何初始化框架**：
  提供初始化瀏覽器、設置代理、配置反檢測功能的範例。
- **如何抓取網頁內容**：
  提供同步與異步 API 的使用範例，展示如何抓取標題、內容等。

### 進階功能提示
- **反檢測功能**：
  提供如何啟用隱身模式、模擬人類行為（如鼠標移動、隨機延遲）的範例。
- **驗證碼處理**：
  提供如何處理 reCAPTCHA、hCaptcha 等驗證碼的範例。

### 錯誤處理與日誌提示
- **如何處理異常**：
  提供異常捕獲與上下文記錄的範例，幫助開發者快速定位問題。
- **如何設置日誌**：
  提供統一日誌格式與記錄關鍵操作的範例。

### 測試與調試提示
- **如何撰寫測試**：
  提供基於 pytest 的測試範例，展示如何測試爬蟲功能。
- **如何調試爬蟲**：
  提供調試技巧，如使用瀏覽器開發者工具檢查 XPath。

## 使用範例
- **基本範例**：
  ```python
  from playwright.sync_api import sync_playwright

  def fetch_page_title(url: str) -> str:
      with sync_playwright() as p:
          browser = p.chromium.launch(headless=True)
          page = browser.new_page()
          page.goto(url)
          title = page.title()
          browser.close()
          return title

  print(fetch_page_title("https://example.com"))
  ```

- **進階範例**：
  ```python
  from playwright.async_api import async_playwright
  import asyncio

  async def fetch_titles(urls: list[str]) -> list[str]:
      async with async_playwright() as p:
          browser = await p.chromium.launch(headless=True)
          page = await browser.new_page()
          titles = []
          for url in urls:
              await page.goto(url)
              titles.append(await page.title())
          await browser.close()
          return titles

  asyncio.run(fetch_titles(["https://example.com", "https://example.org"]))
  ```

## 文件與資源
- **官方文件**：參考 `docs/` 資料夾中的詳細說明。
- **範例程式**：參考 `examples/` 資料夾中的範例程式，涵蓋基本與進階用法。

## 貢獻指南
- **程式碼風格**：遵循 PEP 8，使用 `black` 格式化程式碼。
- **提交規範**：提交訊息應清楚描述更改內容，並遵循專案規範。

## 常見問題
- **如何處理動態內容？**
  使用顯式等待或監聽 AJAX 請求，確保內容加載完成。
- **如何處理驗證碼？**
  使用內建的驗證碼處理模組，或整合第三方服務如 2Captcha。
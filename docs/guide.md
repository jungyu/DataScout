# 使用 AI 開發網頁爬蟲的完整指南

本指南將教您如何通過有效的 Prompt 設計，逐步引導 AI 生成高質量的網頁爬蟲程式。按照這些步驟，您將能夠獲得一個功能完整、結構良好且可重用的爬蟲系統。

## 為什麼需要結構化 Prompt?

開發網頁爬蟲需要考慮多個層面：效能、反爬蟲機制、錯誤處理、數據存儲等。通過結構化的 Prompt，您可以引導 AI 逐步思考並實現這些功能，而不是一次性獲得可能缺少關鍵元素的解決方案。

## 第一階段：定義基本需求

**Prompt 示例：**

```markdown
請設計一個爬取政府電子採購網的爬蟲程式，需求如下：
- 使用 Selenium 進行網頁自動化
- 能夠處理登入機制
- 需要防止被網站封鎖
- 要有錯誤處理機制
- 需要記錄日誌
- 支援數據保存功能
```

這個初始 Prompt 提供了爬蟲的基本需求，明確指出了技術選擇（Selenium）和必需功能。通過具體的需求列表，AI 能夠理解您的期望。

## 第二階段：規劃專案結構

**Prompt 示例：**

```markdown
請為這個爬蟲專案設計合適的檔案結構，包括：
- 主程式檔案
- Cookie 管理模組
- 爬蟲核心運轉模組
- 錯誤處理模組
- 設定檔
- 數據處理與儲存模組

並說明每個模組的主要功能和責任。
```

此 Prompt 引導 AI 思考專案的整體架構，確保代碼組織良好且易於維護。模組化設計可以提高代碼的可讀性和可重用性。

## 第三階段：核心功能設計

**Prompt 示例：**

```markdown
請設計爬蟲的核心功能流程：
1. WebDriver 配置與初始化
2. Cookie 管理機制
3. 登入處理流程
4. 數據爬取邏輯
5. 錯誤重試機制

每個功能都需要：
- 適當的錯誤處理
- 詳細的日誌記錄
- 參數可配置性
```

透過這個 Prompt，您引導 AI 深入思考核心功能的實現細節，確保這些功能具有適當的錯誤處理和可配置性。

## 第四階段：反爬蟲機制

**Prompt 示例：**

```markdown
加入以下反爬蟲防護機制：
1. 隨機 User-Agent 切換
2. 代理伺服器支援
3. WebDriver 特徵隱藏
4. 隨機等待時間
5. Cookie 管理
6. 爬取頻率限制

並說明每種機制如何實現和配置。
```

反爬蟲機制是爬蟲穩定運行的關鍵。此 Prompt 確保 AI 考慮到各種防止被目標網站檢測和封鎖的技術。

## 第五階段：模板化爬蟲設計

**Prompt 示例：**

```markdown
不同的網站其實爬取資料的流程邏輯都接近：
1.取得列表
2.取得下一列表分頁
3.取得內容

重點在取得列表、分頁、內容的 HTML XPath，可參考 Scrapy 的作法。

可否將這 3 個步驟的 XPath 及解讀程序，以 JSON 格式儲存在一個 templates 中？
如此，即能用同樣的程式爬取不同的網站。
```

這是一個關鍵的優化 Prompt，引導 AI 將特定網站的選擇器（XPath）與爬蟲核心邏輯分離，創建可重用的模板系統。通過這種方式，相同的爬蟲程式可以通過不同的配置文件爬取不同的網站。

## 第六階段：數據處理與儲存

**Prompt 示例：**

```markdown
請設計數據處理與儲存模組，要求：
1. 支援多種數據格式（CSV、JSON、Excel）
2. 數據清洗與驗證功能
3. 可選的數據庫整合（SQLite、MongoDB）
4. 增量更新機制
```

此 Prompt 確保爬取的數據能夠被正確處理、驗證和儲存，為後續的數據分析做好準備。

## 第七階段：部署與維護

**Prompt 示例：**

```markdown
請提供爬蟲程式的部署與維護方案：
1. Docker 容器化配置
2. 排程執行設定
3. 錯誤監控與警報機制
4. 日誌分析工具
5. 性能優化建議
```

好的爬蟲不僅僅是能夠運行，還需要考慮長期維護和穩定運行的問題。此 Prompt 引導 AI 考慮部署、監控和優化的方案。

## 完整的模板化爬蟲系統示例

以下是一個基於模板的爬蟲系統示例，展示如何實現第五階段中的模板化設計：

### 網站模板格式 (website_template.json)

```json
{
  "name": "政府電子採購網",
  "base_url": "https://example.gov.tw",
  "login": {
    "required": true,
    "url": "https://example.gov.tw/login",
    "username_xpath": "//input[@id='username']",
    "password_xpath": "//input[@id='password']",
    "submit_xpath": "//button[@type='submit']",
    "success_xpath": "//div[@class='user-info']"
  },
  "list_page": {
    "url": "https://example.gov.tw/tenders",
    "container_xpath": "//div[@class='tender-list']",
    "item_xpath": "//div[@class='tender-item']",
    "title_xpath": ".//h3[@class='title']",
    "link_xpath": ".//a[@class='detail-link']",
    "date_xpath": ".//span[@class='publish-date']",
    "custom_fields": {
      "budget": ".//div[@class='budget']",
      "category": ".//span[@class='category']"
    }
  },
  "pagination": {
    "has_next_page_xpath": "//a[@class='next-page' and not(@disabled)]",
    "next_button_xpath": "//a[@class='next-page']",
    "wait_for_xpath": "//div[@class='tender-list']"
  },
  "detail_page": {
    "container_xpath": "//div[@class='tender-detail']",
    "title_xpath": "//h1[@class='detail-title']",
    "date_xpath": "//div[@class='publish-date']",
    "content_xpath": "//div[@class='tender-content']",
    "custom_fields": {
      "closing_date": "//div[@class='closing-date']",
      "contact": "//div[@class='contact-info']",
      "requirements": "//div[@class='requirements']"
    },
    "attachment_xpath": "//a[@class='attachment']",
    "image_xpath": "//div[@class='gallery']//img"
  }
}
```

### 爬蟲配置文件 (config.json)

```json
{
  "template_path": "templates/gov_procurement.json",
  "headless": false,
  "log_level": "INFO",
  "log_file": "crawler.log",
  "max_pages": 5,
  "output_format": ["json", "csv"],
  "output_path": "data/",
  "random_user_agent": true,
  "user_agents": [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
  ],
  "use_proxy": false,
  "proxies": [],
  "min_delay": 1.0,
  "max_delay": 3.0,
  "credentials": {
    "username": "your_username",
    "password": "your_password"
  }
}
```

### 使用這個系統

有了這個系統，為新網站創建爬蟲只需：

1. 分析網站結構
2. 創建對應的 JSON 模板文件
3. 調整配置文件
4. 執行爬蟲程式

無需修改核心代碼，即可爬取不同的網站。

## 小結：有效的 Prompt 設計原則

1. **階段性提問**：將複雜問題分解為多個階段，逐步深入。
2. **具體需求**：清晰列出功能需求和技術選擇。
3. **考慮全面**：包括核心功能、錯誤處理、反爬蟲、數據處理等各個方面。
4. **尋求優化**：不止於基本功能，進一步尋求架構和性能的優化。
5. **可擴展性**：鼓勵 AI 設計可擴展、可重用的解決方案。

通過遵循這些原則和步驟，您可以引導 AI 生成高品質的網頁爬蟲程式，滿足不同網站的爬取需求，同時確保代碼的可維護性和擴展性。
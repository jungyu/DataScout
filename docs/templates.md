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

```json
"request": {
  "method": "GET",
  "headers": {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
  },
  "params": {
    "fixed": {
      "type": "article"
    },
    "variable": {
      "q": "search_query"
    }
  },
  "cookies": {
    "session_id": "value"
  },
  "timeout": 30
}
```

### 登入設定 (login)
如需登入才能爬取，可配置：
- 登入頁面 URL
- 表單元素定位與操作方式
- 登入成功檢查條件

```json
"login": {
  "required": true,
  "url": "https://example.com/login",
  "form": {
    "username_selector": "input[name='username']",
    "username_value": "your_username",
    "password_selector": "input[name='password']",
    "password_value": "your_password",
    "submit_selector": "button[type='submit']"
  },
  "success_check": {
    "type": "element_exists",
    "selector": "a.logout-button"
  }
}
```

### 延遲設定 (delays)
各種操作間的延遲時間：
- 頁面載入後等待
- 頁面間跳轉
- 項目處理間隔

```json
"delays": {
  "page_load": [1, 3],
  "between_requests": [2, 5],
  "after_login": 3,
  "between_paginations": [1, 2],
  "before_action": 0.5
}
```

### 列表頁設定 (list_page)
定義如何從列表頁面擷取資料：
- 列表容器定位
- 項目選擇器
- 欄位擷取規則
- 排除條件

```json
"list_page": {
  "url": "https://example.com/list",
  "container": "div.article-list",
  "item_selector": "article.item",
  "fields": {
    "title": {
      "selector": "h2.title a",
      "attribute": "text"
    },
    "link": {
      "selector": "h2.title a",
      "attribute": "href"
    },
    "date": {
      "selector": "span.date",
      "attribute": "text",
      "processor": "date_format"
    }
  },
  "exclude": {
    "selector": ".sponsored-content",
    "attribute": "class",
    "pattern": "sponsored|ad|promotion"
  }
}
```

### 分頁設定 (pagination)
處理多頁資料的方式：
- 下一頁按鈕定位
- 頁數判斷方式
- 最大頁數限制

```json
"pagination": {
  "type": "click",
  "selector": "a.next-page",
  "max_pages": 10,
  "wait_after_click": 2,
  "has_next_page_check": {
    "selector": "a.next-page:not(.disabled)"
  },
  "alternative": {
    "type": "url_pattern",
    "pattern": "https://example.com/list?page={page}",
    "start_page": 1
  }
}
```

### 詳情頁設定 (detail_page)
定義詳情頁面的資料擷取：
- 內容區塊定位
- 欄位擷取規則
- 頁面操作（如展開、切換分頁）

```json
"detail_page": {
  "enabled": true,
  "container": "div.article-content",
  "fields": {
    "author": {
      "selector": "span.author",
      "attribute": "text"
    },
    "content": {
      "selector": "div.content",
      "attribute": "html"
    },
    "tags": {
      "selector": "ul.tags li",
      "attribute": "text",
      "multiple": true
    },
    "images": {
      "selector": "div.gallery img",
      "attribute": "src",
      "multiple": true
    }
  },
  "actions": [
    {
      "type": "click",
      "selector": "button.read-more",
      "wait_after": 1
    },
    {
      "type": "scroll_to",
      "selector": "div.comments",
      "wait_after": 0.5
    }
  ]
}
```

### 資料處理 (data_processing)
資料後處理相關設定：
- 資料清理規則
- 欄位對應
- 後處理邏輯

```json
"data_processing": {
  "output": "json",
  "field_mapping": {
    "article_title": "title",
    "article_link": "link",
    "publish_date": "date",
    "article_content": "content"
  },
  "cleaning_rules": {
    "title": [
      {"pattern": "\\[.*?\\]", "replacement": ""},
      {"pattern": "\\s{2,}", "replacement": " "}
    ],
    "date": {"processor": "date_standardize", "format": "%Y-%m-%d"}
  },
  "filters": [
    {"field": "date", "operator": ">=", "value": "2023-01-01"},
    {"field": "title", "operator": "contains_not", "value": ["廣告", "贊助"]}
  ]
}
```

## 使用範例

完整範例請參考 `examples/templates/` 目錄下的模板檔案：
- `basic_template.json`：基礎爬蟲模板
- `login_template.json`：需登入網站的模板
- `pagination_template.json`：多頁面爬取模板

## 模板驗證工具

使用以下命令驗證模板格式是否正確：

```bash
python -m src.utils.template_validator path/to/your_template.json
```

## 模板測試

測試模板的爬取效果：

```bash
python -m src.crawler --template path/to/your_template.json --output results.json --debug
```
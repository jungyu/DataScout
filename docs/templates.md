# 爬蟲模板格式說明

## 簡介

本文檔說明爬蟲系統的模板格式。模板採用 JSON 格式，用於定義如何爬取特定網站的結構化數據。

## 模板基本結構

爬蟲模板有兩種組織方式：

1. **基本配置（Basic）**：所有配置集中在單一 JSON 檔案中
2. **正規化配置（Formal）**：根據功能將配置分拆到多個 JSON 檔案中

### 基本配置（Basic）結構

```json
{
  "site_name": "網站名稱",
  "base_url": "https://example.com",
  "encoding": "utf-8",
  "description": "模板描述",
  "version": "1.0.0",
  "request": {},
  "search": {},
  "delays": {},
  "search_page": {},
  "list_page": {},
  "detail_page": {},
  "pagination": {},
  "advanced_settings": {}
}
```

### 正規化配置（Formal）結構

正規化配置將不同功能的設定分散到多個檔案中：

- `config.json`：基本配置和共用設定
- `detail.json`：詳情頁面設定
- `pagination.json`：分頁設定
- `anti_detection.json`：反偵測設定
- `error_handling.json`：錯誤處理設定
- `output.json`：輸出格式設定
- `rate_limit.json`：速率限制設定
- `captcha.json`：驗證碼處理設定
- `list.json`：列表頁面設定

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
- 請求標頭
- Cookie 設定

```json
"request": {
  "method": "GET",
  "headers": {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
  }
}
```

### 搜尋設定 (search)
搜尋相關配置，包含：
- 關鍵字
- 語言設定
- 搜尋頁面元素定位

```json
"search": {
  "keyword": "地震 site:news.pts.org.tw",
  "language": "zh-TW",
  "search_page": {
    "search_box_xpath": "//textarea[@name='q']",
    "result_container_xpath": "//div[@id='search']"
  },
  "list_page": {
    "container_xpath": "//div[@id='search']",
    "item_xpath": "//div[contains(@class, 'N54PNb')]",
    "fields": {
      "title": {
        "xpath": ".//h3",
        "type": "text"
      },
      "link": {
        "xpath": ".//a[h3]/@href",
        "fallback_xpath": ".//a/@href",
        "type": "attribute"
      },
      "description": {
        "xpath": ".//div[contains(@class, 'VwiC3b')]",
        "type": "text",
        "max_length": 300
      }
    }
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
  "page_load": 3,
  "between_pages": 2,
  "between_items": 1,
  "scroll": 1,
  "finish": 3
}
```

### 列表頁設定 (list_page)
定義如何從列表頁面擷取資料：
- 列表容器定位
- 項目選擇器
- 欄位擷取規則

```json
"list_page": {
  "container_xpath": "//div[@id='search']",
  "item_xpath": "//div[contains(@class, 'N54PNb')]",
  "fields": {
    "title": {
      "xpath": ".//h3",
      "type": "text"
    },
    "link": {
      "xpath": ".//a[h3]/@href",
      "fallback_xpath": ".//a/@href",
      "type": "attribute"
    },
    "description": {
      "xpath": ".//div[contains(@class, 'VwiC3b')]",
      "type": "text",
      "max_length": 300
    }
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
  "next_button_xpath": "//a[@id='pnnext']",
  "has_next_page_check": "boolean(//a[@id='pnnext'])",
  "page_number_xpath": "//td[contains(@class,'YyVfkd')]/text()",
  "max_pages": 2
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
  "max_details_per_page": 3,
  "page_load_delay": 3,
  "between_details_delay": 2,
  "check_captcha": true,
  "container_xpath": "//body",
  "fields": {
    "title": {
      "xpath": "//h1",
      "type": "text",
      "fallback_xpath": "//title"
    },
    "content": {
      "xpath": "//article | //div[contains(@class, 'article')] | //div[@role='main']",
      "type": "text",
      "fallback_xpath": "//div[contains(@class, 'content')]"
    },
    "published_date": {
      "xpath": "//time | //span[contains(@class, 'date')] | //meta[@property='article:published_time']/@content",
      "type": "date",
      "fallback_xpath": "//div[contains(@class, 'date')] | //p[contains(@class, 'date')]"
    },
    "category": {
      "xpath": "//div[contains(@class, 'category')] | //a[contains(@href, 'category')]",
      "type": "text",
      "fallback_xpath": "//meta[@property='article:section']/@content"
    },
    "author": {
      "xpath": "//div[contains(@class, 'author')] | //span[contains(@class, 'author')] | //meta[@name='author']/@content",
      "type": "text"
    },
    "tags": {
      "xpath": "//a[contains(@href, 'tag')] | //div[contains(@class, 'tag')]//a",
      "type": "text",
      "multiple": true
    }
  },
  "expand_sections": [
    {
      "name": "閱讀更多",
      "button_selector": "//button[contains(text(), '閱讀更多') or contains(@class, 'more')]",
      "target_selector": "//div[contains(@class, 'expanded')]",
      "wait_time": 1
    }
  ],
  "extract_tables": {
    "xpath": "//table",
    "title_xpath": ".//caption | .//th[1]"
  },
  "extract_images": true,
  "images_container_xpath": "//article | //div[contains(@class, 'article')]"
}
```

### 反偵測設定 (anti_detection)
防止被網站偵測為爬蟲的設定：
- 瀏覽器指紋偽裝
- 代理伺服器設定
- Cookie 管理
- 模擬人類行為

```json
"browser_fingerprint": {
  "user_agent": {
    "enabled": true,
    "rotation": {
      "enabled": true,
      "interval": 300,
      "max_uses": 10
    },
    "custom_agents": [
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
    ]
  },
  "webgl": {
    "enabled": true,
    "noise": 0.1,
    "vendor": "Google Inc. (NVIDIA)",
    "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 6GB Direct3D11 vs_5_0 ps_5_0, D3D11)"
  },
  "canvas": {
    "enabled": true,
    "noise": 0.1,
    "mode": "readback"
  },
  "audio": {
    "enabled": true,
    "noise": 0.1,
    "sample_rate": 44100
  },
  "fonts": {
    "enabled": true,
    "noise": 0.1,
    "custom_fonts": [
      "Arial",
      "Helvetica",
      "Times New Roman",
      "Courier New"
    ]
  }
},
"proxy": {
  "enabled": true,
  "type": "http",
  "rotation": {
    "enabled": true,
    "interval": 300,
    "max_failures": 3
  },
  "authentication": {
    "required": true,
    "username": "${PROXY_USERNAME}",
    "password": "${PROXY_PASSWORD}"
  }
},
"cookies": {
  "enabled": true,
  "storage": {
    "type": "file",
    "path": "cookies/google.json"
  },
  "rotation": {
    "enabled": true,
    "interval": 3600
  }
},
"human_behavior": {
  "enabled": true,
  "mouse_movement": {
    "enabled": true,
    "speed": "natural",
    "pattern": "random"
  },
  "typing": {
    "enabled": true,
    "speed": "natural",
    "mistakes": true
  },
  "scrolling": {
    "enabled": true,
    "speed": "natural",
    "pattern": "random"
  }
},
"headers": {
  "custom_headers": {
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "DNT": "1"
  }
}
```

### 錯誤處理設定 (error_handling)
處理爬取過程中可能出現的錯誤：
- 網路錯誤
- 超時錯誤
- 驗證碼錯誤
- 被封鎖錯誤
- 解析錯誤

```json
"error_types": {
  "network": {
    "retry": true,
    "max_retries": 3,
    "retry_delay": 5,
    "error_codes": [500, 502, 503, 504]
  },
  "timeout": {
    "retry": true,
    "max_retries": 3,
    "retry_delay": 5,
    "timeout_values": {
      "connection": 30,
      "read": 30
    }
  },
  "captcha": {
    "retry": true,
    "max_retries": 3,
    "retry_delay": 5,
    "handlers": ["recaptcha", "image_captcha"]
  },
  "blocked": {
    "retry": true,
    "max_retries": 3,
    "retry_delay": 30,
    "actions": ["rotate_proxy", "rotate_user_agent"]
  },
  "parsing": {
    "retry": false,
    "save_error_page": true,
    "error_page_dir": "debug/parsing_errors"
  }
},
"recovery": {
  "save_state": {
    "enabled": true,
    "interval": 10,
    "path": "state/google_search.json"
  },
  "resume": {
    "enabled": true,
    "max_attempts": 3
  }
},
"notifications": {
  "email": {
    "enabled": true,
    "recipients": ["${ADMIN_EMAIL}"],
    "error_levels": ["ERROR", "CRITICAL"]
  },
  "slack": {
    "enabled": true,
    "webhook_url": "${SLACK_WEBHOOK_URL}",
    "error_levels": ["ERROR", "CRITICAL"]
  }
},
"debug": {
  "save_screenshots": {
    "enabled": true,
    "dir": "debug/screenshots",
    "on_error": true
  },
  "save_html": {
    "enabled": true,
    "dir": "debug/html",
    "on_error": true
  },
  "save_network_logs": {
    "enabled": true,
    "dir": "debug/network",
    "on_error": true
  }
}
```

### 輸出設定 (output)
定義爬取結果的輸出格式和儲存方式：
- JSON 格式
- CSV 格式
- Excel 格式

```json
"formats": {
  "json": {
    "enabled": true,
    "structure": {
      "query": {
        "type": "string",
        "description": "搜尋關鍵字"
      },
      "total_results": {
        "type": "integer",
        "description": "搜尋結果總數"
      },
      "results": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "title": {
              "type": "string",
              "description": "搜尋結果標題"
            },
            "url": {
              "type": "string",
              "description": "搜尋結果連結"
            },
            "snippet": {
              "type": "string",
              "description": "搜尋結果摘要"
            },
            "date": {
              "type": "string",
              "description": "搜尋結果日期"
            },
            "source": {
              "type": "string",
              "description": "搜尋結果來源"
            }
          }
        }
      }
    }
  },
  "csv": {
    "enabled": true,
    "columns": [
      "title",
      "url",
      "snippet",
      "date",
      "source"
    ],
    "delimiter": ",",
    "encoding": "utf-8"
  },
  "excel": {
    "enabled": true,
    "sheets": {
      "search_results": {
        "columns": [
          "title",
          "url",
          "snippet",
          "date",
          "source"
        ]
      }
    }
  }
},
"output_settings": {
  "base_directory": "output/google",
  "file_naming": {
    "pattern": "{query}_{timestamp}",
    "timestamp_format": "%Y%m%d_%H%M%S"
  },
  "compression": {
    "enabled": true,
    "format": "zip"
  },
  "metadata": {
    "include_query": true,
    "include_timestamp": true,
    "include_version": true
  }
}
```

### 進階設定 (advanced_settings)
其他進階設定：
- 驗證碼偵測
- 錯誤頁面儲存
- 文字清理

```json
"advanced_settings": {
  "detect_captcha": true,
  "captcha_detection_xpath": "//div[contains(@class, 'g-recaptcha')]",
  "save_error_page": true,
  "error_page_dir": "../debug",
  "max_results_per_page": 10,
  "text_cleaning": {
    "remove_extra_whitespace": true,
    "trim_strings": true
  }
}
```

## 使用範例

完整範例請參考 `examples/config/` 目錄下的配置文件：
- `google/basic/search.json`：Google 搜尋基本配置
- `google/formal/`：Google 搜尋正規化配置

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
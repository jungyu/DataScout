# 核心模組說明

## 目錄
- [概述](#概述)
- [配置載入器 (ConfigLoader)](#配置載入器-configloader)
- [WebDriver 管理器 (WebDriverManager)](#webdriver-管理器-webdrivermanager)
- [模板爬蟲 (TemplateCrawler)](#模板爬蟲-templatecrawler)
- [爬蟲引擎 (CrawlerEngine)](#爬蟲引擎-crawlerengine)
- [爬蟲狀態管理器 (CrawlerStateManager)](#爬蟲狀態管理器-crawlerstatemanager)
- [使用範例](#使用範例)

## 概述

核心模組是爬蟲系統的基礎，提供了配置載入、瀏覽器管理、爬蟲邏輯和任務協調等功能。這些模組共同構成了一個完整的爬蟲框架，支援各種複雜的爬蟲任務。

主要核心模組包括：

1. **ConfigLoader**：負責載入、合併和驗證配置文件
2. **WebDriverManager**：管理瀏覽器實例和設定
3. **TemplateCrawler**：實現基於模板的爬蟲邏輯
4. **CrawlerEngine**：協調多個爬蟲任務的執行
5. **CrawlerStateManager**：管理爬蟲狀態，支援斷點續爬

## 配置載入器 (ConfigLoader)

`ConfigLoader` 是配置管理模組，負責載入、合併和驗證配置文件，支援模板繼承和覆蓋機制。

### 主要功能

- 載入和解析 JSON 配置文件
- 支援配置模板繼承
- 配置驗證和快取
- 配置合併和覆蓋
- 配置保存

### 使用範例

```python
from src.core import ConfigLoader

# 創建配置載入器
config_loader = ConfigLoader()

# 載入配置文件
config = config_loader.load_config('config.json')

# 載入模板
template = config_loader.load_template('template.json')

# 載入並驗證配置
validated_config = config_loader.load_and_validate('config.json', 'schema.json')

# 載入帶覆蓋的配置
merged_config = config_loader.load_with_override('base.json', 'override.json')

# 保存配置
config_loader.save_config(config, 'new_config.json')
```

### 配置模板繼承

配置模板繼承允許您創建基礎模板，然後在特定爬蟲中覆蓋或擴展這些模板：

```python
# 載入模板並應用配置
template_with_config = config_loader.load_template_with_config(
    'template.json',
    'config.json',
    'schema.json'
)
```

## WebDriver 管理器 (WebDriverManager)

`WebDriverManager` 負責創建、配置和管理 WebDriver 實例，提供豐富的瀏覽器設定和反爬蟲功能。

### 主要功能

- 支援多種瀏覽器（Chrome、Firefox、Edge）
- 用戶代理管理和隨機化
- 代理伺服器設定
- 反爬蟲技術（隱身模式、隨機延遲等）
- Cookie 管理
- 頁面導航和元素等待
- 截圖和調試功能

### 使用範例

```python
from src.core import WebDriverManager

# 創建 WebDriver 管理器
driver_manager = WebDriverManager(config)

# 創建 WebDriver 實例
driver = driver_manager.create_driver()

# 導航到指定 URL
driver_manager.navigate_to('https://example.com')

# 等待元素出現
element = driver_manager.wait_for_element(By.ID, 'search')

# 安全點擊元素
driver_manager.safe_click(element)

# 隨機延遲
driver_manager.random_delay(1.0, 3.0)

# 頁面滾動
driver_manager.scroll_page('down', 500)

# 截圖
driver_manager.take_screenshot('screenshot.png')

# 保存和載入 Cookie
driver_manager.save_cookies('cookies.json')
driver_manager.load_cookies('cookies.json')

# 關閉 WebDriver
driver_manager.close_driver()
```

### 反爬蟲設定

WebDriverManager 提供了多種反爬蟲設定：

```python
# 配置反爬蟲設定
config = {
    "browser_type": "chrome",
    "enable_stealth": True,
    "randomize_user_agent": True,
    "proxy": {
        "enabled": True,
        "type": "http",
        "host": "proxy.example.com",
        "port": 8080
    },
    "headless": False,
    "disable_images": True,
    "arguments": [
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars"
    ]
}

driver_manager = WebDriverManager(config)
```

## 模板爬蟲 (TemplateCrawler)

`TemplateCrawler` 是基於模板的爬蟲實現，根據配置文件定義的模板執行爬蟲任務。

### 主要功能

- 基於 XPath 的數據提取
- 頁面導航和 URL 構建
- 表單處理和搜索參數設置
- 分頁處理
- 詳情頁爬取
- 數據合併和處理
- 隨機延遲和反爬蟲

### 使用範例

```python
from src.core import TemplateCrawler, WebDriverManager, ConfigLoader

# 載入配置
config_loader = ConfigLoader()
config = config_loader.load_config('config.json')

# 創建 WebDriver 管理器
driver_manager = WebDriverManager(config)

# 創建模板爬蟲
crawler = TemplateCrawler('template.json', driver_manager)

# 開始爬取
results = crawler.start(max_pages=5, max_items=100)

# 停止爬取
crawler.stop()
```

### 模板配置示例

```json
{
  "site_name": "Example Site",
  "base_url": "https://example.com",
  "encoding": "utf-8",
  "description": "Example site crawler",
  "request": {
    "headers": {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
  },
  "delays": {
    "page_load": 2,
    "action": 1,
    "between_items": 0.5
  },
  "search_page": {
    "url": "https://example.com/search",
    "form": {
      "search_input": {
        "xpath": "//input[@name='q']",
        "value": "search term"
      },
      "search_button": {
        "xpath": "//button[@type='submit']"
      }
    }
  },
  "list_page": {
    "container_xpath": "//div[@class='results']",
    "item_xpath": ".//div[@class='item']",
    "fields": {
      "title": {
        "xpath": ".//h2",
        "type": "text"
      },
      "link": {
        "xpath": ".//a",
        "type": "attribute",
        "attribute": "href"
      },
      "description": {
        "xpath": ".//p",
        "type": "text"
      }
    },
    "pagination": {
      "enabled": true,
      "next_button_xpath": "//a[@class='next']",
      "max_pages": 10
    }
  },
  "detail_page": {
    "enabled": true,
    "url_pattern": "https://example.com/detail/{pk}",
    "fields": {
      "content": {
        "xpath": "//div[@class='content']",
        "type": "text"
      },
      "date": {
        "xpath": "//span[@class='date']",
        "type": "text"
      }
    }
  }
}
```

## 爬蟲引擎 (CrawlerEngine)

`CrawlerEngine` 負責協調多個爬蟲任務，提供任務隊列、多線程支持和狀態管理。

### 主要功能

- 多線程爬蟲任務執行
- 任務隊列管理
- 斷點續爬支援
- 統計信息收集
- 錯誤處理和重試
- 數據持久化

### 使用範例

```python
from src.core import CrawlerEngine

# 創建爬蟲引擎
engine = CrawlerEngine(
    config_file="config/config.json",
    max_workers=3,
    resume_crawling=True
)

# 添加單個任務
engine.add_task("templates/google_search.json", {"query": "Python Selenium"})

# 添加多個任務
engine.add_tasks_from_directory("templates/", "*.json")

# 啟動引擎
engine.start(wait=True)

# 獲取結果
results = engine.get_results()

# 獲取狀態
status = engine.get_status()

# 停止引擎
engine.stop()
```

### 引擎配置示例

```json
{
  "engine_config": {
    "max_threads": 3,
    "resume_crawling": true,
    "retry_on_failure": true,
    "max_retries": 3,
    "retry_delay": 5,
    "save_interval": 10,
    "output_format": "json",
    "output_dir": "data/output"
  },
  "persistence_config": {
    "type": "file",
    "format": "json",
    "directory": "data/output",
    "filename_pattern": "{crawler_id}_{timestamp}.json"
  }
}
```

## 爬蟲狀態管理器 (CrawlerStateManager)

`CrawlerStateManager` 負責管理爬蟲狀態，支援斷點續爬和多重備份策略。

### 主要功能

- 爬蟲狀態的保存和載入
- 自動保存機制
- 多重備份策略
- 多種存儲格式支援（JSON、Pickle）
- 狀態清理和重置

### 使用範例

```python
from src.core import CrawlerStateManager

# 創建狀態管理器
state_manager = CrawlerStateManager(
    crawler_id="google_search",
    config={
        "auto_save_interval": 60,
        "auto_save_enabled": True,
        "max_backups": 5,
        "backup_on_save": True
    },
    state_dir="data/state"
)

# 保存狀態
state_manager.save_state({
    "current_page": 5,
    "processed_items": 100,
    "last_item_id": "item123"
})

# 獲取狀態
state = state_manager.get_state()

# 標記完成
state_manager.mark_completed()

# 檢查是否完成
is_completed = state_manager.is_completed()

# 清理狀態
state_manager.clear_state()

# 使用上下文管理器
with CrawlerStateManager("google_search") as manager:
    # 保存狀態
    manager.save_state({"current_page": 5})
    
    # 獲取狀態
    state = manager.get_state()
```

### 狀態配置示例

```python
state_config = {
    "auto_save_interval": 60,  # 自動保存間隔（秒）
    "auto_save_enabled": True,  # 是否啟用自動保存
    "max_backups": 5,  # 最大備份數量
    "backup_on_save": True,  # 保存時是否創建備份
    "storage_formats": ["json", "pickle"],  # 存儲格式
    "compression": False,  # 是否壓縮
    "encoding": "utf-8"  # 文件編碼
}
```

## 使用範例

以下是一個完整的爬蟲應用範例，展示了如何使用核心模組：

```python
import os
import logging
from src.core import (
    ConfigLoader,
    WebDriverManager,
    TemplateCrawler,
    CrawlerEngine,
    CrawlerStateManager
)

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # 載入配置
    config_loader = ConfigLoader()
    config = config_loader.load_config('config/config.json')
    
    # 創建狀態管理器
    state_manager = CrawlerStateManager(
        crawler_id="google_search",
        config=config.get("state_config", {}),
        state_dir="data/state"
    )
    
    # 檢查是否有未完成的任務
    state = state_manager.get_state()
    if state and not state.completed:
        logger.info(f"發現未完成的任務: {state.crawler_id}")
        # 從上次的位置繼續爬取
        start_page = state.data.get("current_page", 1)
        processed_items = state.data.get("processed_items", 0)
    else:
        start_page = 1
        processed_items = 0
    
    # 創建爬蟲引擎
    engine = CrawlerEngine(
        config_file="config/config.json",
        max_workers=config.get("engine_config", {}).get("max_threads", 1),
        resume_crawling=True
    )
    
    # 添加任務
    engine.add_task(
        "templates/google_search.json",
        {
            "query": "Python Selenium",
            "start_page": start_page,
            "processed_items": processed_items
        }
    )
    
    try:
        # 啟動引擎
        engine.start(wait=True)
        
        # 獲取結果
        results = engine.get_results()
        
        # 標記任務完成
        state_manager.mark_completed()
        
        logger.info(f"爬蟲任務完成，共爬取 {len(results)} 條數據")
    except Exception as e:
        logger.error(f"爬蟲任務失敗: {str(e)}")
    finally:
        # 停止引擎
        engine.stop()

if __name__ == "__main__":
    main()
```

這個範例展示了如何結合使用各個核心模組，實現一個完整的爬蟲應用，包括配置載入、狀態管理、任務執行和結果處理。 
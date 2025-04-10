# 提取器模組說明

## 目錄
- [概述](#概述)
- [核心提取器](#核心提取器)
  - [基礎提取器 (BaseExtractor)](#基礎提取器-baseextractor)
  - [數據提取器 (DataExtractor)](#數據提取器-dataextractor)
  - [列表提取器 (ListExtractor)](#列表提取器-listextractor)
  - [詳情提取器 (DetailExtractor)](#詳情提取器-detailextractor)
  - [複合提取器 (CompoundExtractor)](#複合提取器-compoundextractor)
- [處理器](#處理器)
  - [驗證碼處理器 (CaptchaHandler)](#驗證碼處理器-captchahandler)
  - [分頁處理器 (PaginationHandler)](#分頁處理器-paginationhandler)
  - [API處理器 (ApiHandler)](#api處理器-apihandler)
  - [存儲處理器 (StorageHandler)](#存儲處理器-storagehandler)
- [使用範例](#使用範例)

## 概述

提取器模組是爬蟲系統的核心組件之一，負責從網頁中提取結構化數據。該模組提供了一系列專門的提取器和處理器，用於處理不同類型的數據提取任務。

主要組件包括：

1. **核心提取器**：
   - BaseExtractor：基礎提取器，提供共用功能
   - DataExtractor：通用數據提取器
   - ListExtractor：列表頁面提取器
   - DetailExtractor：詳情頁面提取器
   - CompoundExtractor：複合數據提取器

2. **處理器**：
   - CaptchaHandler：驗證碼處理
   - PaginationHandler：分頁處理
   - ApiHandler：API 調用處理
   - StorageHandler：數據存儲處理

## 核心提取器

### 基礎提取器 (BaseExtractor)

`BaseExtractor` 是所有提取器的基類，提供了共用的功能和抽象接口。

#### 主要功能

- 元素等待和查找
- 頁面導航和滾動
- 截圖和源碼保存
- 統計信息收集
- 工具類整合

#### 使用範例

```python
from src.extractors.core import BaseExtractor

class MyExtractor(BaseExtractor):
    def extract(self, config):
        # 等待元素出現
        element = self.wait_for_element(By.ID, "target")
        
        # 提取數據
        data = element.text
        
        # 返回結果
        return data
```

### 數據提取器 (DataExtractor)

`DataExtractor` 是通用數據提取器，支持多種數據類型的提取。

#### 主要功能

- 文本提取
- 屬性提取
- HTML提取
- 數字提取
- 日期提取
- URL提取
- 複合字段提取

#### 使用範例

```python
from src.extractors.core import DataExtractor
from src.extractors.config import ExtractionConfig

# 創建提取器
extractor = DataExtractor(driver, base_url="https://example.com")

# 配置提取
config = {
    "title": ExtractionConfig(xpath="//h1", type="text"),
    "price": ExtractionConfig(xpath="//span[@class='price']", type="number"),
    "description": ExtractionConfig(xpath="//p[@class='description']", type="text"),
    "images": ExtractionConfig(xpath="//img", type="attribute", attribute="src", multiple=True)
}

# 提取數據
data = extractor.extract_from_page(config)
```

### 列表提取器 (ListExtractor)

`ListExtractor` 專門用於處理列表頁面的數據提取。

#### 主要功能

- 列表項目定位和提取
- 並行數據提取
- 自動滾動加載
- 字段數據提取
- 元數據添加

#### 使用範例

```python
from src.extractors.core import ListExtractor
from src.extractors.config import ListExtractionConfig, ExtractionConfig

# 創建提取器
extractor = ListExtractor(driver, base_url="https://example.com")

# 配置提取
config = ListExtractionConfig(
    container_xpath="//div[@class='list-container']",
    item_xpath=".//div[@class='item']",
    field_configs={
        "title": ExtractionConfig(type="text", xpath=".//h2"),
        "link": ExtractionConfig(type="url", xpath=".//a")
    }
)

# 提取數據
items = extractor.extract(config)
```

### 詳情提取器 (DetailExtractor)

`DetailExtractor` 專門用於處理詳情頁面的數據提取。

#### 主要功能

- 詳情頁字段提取
- 表格數據提取
- 圖片提取
- 可折疊區塊展開
- 備用選擇器支持
- 錯誤處理和恢復

#### 使用範例

```python
from src.extractors.core import DetailExtractor

# 創建提取器
extractor = DetailExtractor(driver, base_url="https://example.com")

# 配置提取
detail_config = {
    "container_xpath": "//article",
    "fields": {
        "title": {
            "xpath": "//h1",
            "type": "text",
            "fallback_xpath": "//title"
        },
        "content": {
            "xpath": "//div[@class='content']",
            "type": "text"
        },
        "published_date": {
            "xpath": "//time",
            "type": "date"
        }
    }
}

# 提取數據
data = extractor.extract_detail_page(detail_config)
```

### 複合提取器 (CompoundExtractor)

`CompoundExtractor` 用於處理複雜的嵌套數據結構。

#### 主要功能

- 複合字段提取
- 嵌套數據結構處理
- JSON數據提取
- 表格數據提取
- 結構化數據提取
- 表單數據提取

#### 使用範例

```python
from src.extractors.core import CompoundExtractor
from src.extractors.config import ExtractionConfig

# 創建提取器
extractor = CompoundExtractor(driver, base_url="https://example.com")

# 配置提取
config = ExtractionConfig(
    xpath="//div[@class='product']",
    type="compound",
    multiple=True,
    nested_fields={
        "title": ExtractionConfig(xpath=".//h2", type="text"),
        "price": ExtractionConfig(xpath=".//span[@class='price']", type="number"),
        "description": ExtractionConfig(xpath=".//p", type="text"),
        "specifications": ExtractionConfig(
            xpath=".//table",
            type="table",
            headers_xpath=".//th",
            rows_xpath=".//tr[td]"
        )
    }
)

# 提取數據
data = extractor.extract(element, config)
```

## 處理器

### 驗證碼處理器 (CaptchaHandler)

`CaptchaHandler` 用於處理網頁中的驗證碼。

#### 主要功能

- 驗證碼檢測
- 驗證碼識別
- 驗證碼繞過
- 驗證碼處理策略

#### 使用範例

```python
from src.extractors.handlers import CaptchaHandler

# 創建處理器
handler = CaptchaHandler()

# 檢測驗證碼
if handler.detect_captcha():
    # 處理驗證碼
    handler.solve_captcha()
```

### 分頁處理器 (PaginationHandler)

`PaginationHandler` 用於處理分頁相關的操作。

#### 主要功能

- 分頁導航
- 分頁URL構建
- 分頁狀態管理
- 分頁錯誤處理

#### 使用範例

```python
from src.extractors.handlers import PaginationHandler, PaginationConfig

# 創建處理器
handler = PaginationHandler(
    config=PaginationConfig(
        next_button_xpath="//a[@class='next']",
        page_number_xpath="//span[@class='current']",
        max_pages=10
    )
)

# 處理分頁
while handler.has_next_page():
    # 提取當前頁數據
    data = extractor.extract()
    
    # 下一頁
    handler.next_page()
```

### API處理器 (ApiHandler)

`ApiHandler` 用於處理 API 調用相關的操作。

#### 主要功能

- API 請求發送
- 響應處理
- 錯誤處理
- 重試機制
- 速率限制

#### 使用範例

```python
from src.extractors.handlers import ApiHandler, ApiConfig

# 創建處理器
handler = ApiHandler(
    config=ApiConfig(
        base_url="https://api.example.com",
        headers={
            "Authorization": "Bearer token"
        },
        rate_limit=60,  # 每分鐘請求數
        retry_count=3
    )
)

# 發送請求
response = handler.send_request("GET", "/endpoint")

# 處理響應
data = handler.process_response(response)
```

### 存儲處理器 (StorageHandler)

`StorageHandler` 用於處理數據的存儲操作。

#### 主要功能

- 文件存儲
- 數據庫存儲
- 緩存管理
- 備份策略
- 格式轉換

#### 使用範例

```python
from src.extractors.handlers import StorageHandler, StorageConfig

# 創建處理器
handler = StorageHandler(
    config=StorageConfig(
        storage_type="file",
        output_dir="data",
        file_format="json",
        compression=True
    )
)

# 存儲數據
handler.save_data(data, "output.json")

# 讀取數據
loaded_data = handler.load_data("output.json")
```

## 使用範例

以下是一個完整的爬蟲示例，展示了如何組合使用各種提取器和處理器：

```python
import logging
from src.extractors.core import (
    ListExtractor,
    DetailExtractor,
    CompoundExtractor
)
from src.extractors.handlers import (
    CaptchaHandler,
    PaginationHandler,
    StorageHandler
)
from src.extractors.config import (
    ListExtractionConfig,
    ExtractionConfig,
    PaginationConfig,
    StorageConfig
)

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # 創建提取器
    list_extractor = ListExtractor(driver, base_url="https://example.com")
    detail_extractor = DetailExtractor(driver)
    compound_extractor = CompoundExtractor(driver)
    
    # 創建處理器
    captcha_handler = CaptchaHandler()
    pagination_handler = PaginationHandler(
        config=PaginationConfig(
            next_button_xpath="//a[@class='next']",
            max_pages=10
        )
    )
    storage_handler = StorageHandler(
        config=StorageConfig(
            storage_type="file",
            output_dir="data"
        )
    )
    
    try:
        # 檢查驗證碼
        if captcha_handler.detect_captcha():
            captcha_handler.solve_captcha()
        
        # 配置列表提取
        list_config = ListExtractionConfig(
            container_xpath="//div[@class='list']",
            item_xpath=".//div[@class='item']",
            field_configs={
                "title": ExtractionConfig(xpath=".//h2", type="text"),
                "link": ExtractionConfig(xpath=".//a", type="url")
            }
        )
        
        all_items = []
        
        # 處理分頁
        while pagination_handler.has_next_page():
            # 提取列表數據
            items = list_extractor.extract(list_config)
            
            # 提取詳情數據
            for item in items:
                # 配置詳情提取
                detail_config = {
                    "fields": {
                        "content": {
                            "xpath": "//div[@class='content']",
                            "type": "text"
                        },
                        "specs": {
                            "xpath": "//table[@class='specs']",
                            "type": "table"
                        }
                    }
                }
                
                # 提取詳情
                detail_data = detail_extractor.extract_detail_page(
                    detail_config,
                    item["link"]
                )
                
                # 合併數據
                item.update(detail_data)
                all_items.append(item)
            
            # 下一頁
            pagination_handler.next_page()
        
        # 存儲數據
        storage_handler.save_data(all_items, "output.json")
        
        logger.info(f"爬取完成，共獲取 {len(all_items)} 條數據")
        
    except Exception as e:
        logger.error(f"爬取過程中發生錯誤: {str(e)}")
        raise
    finally:
        # 清理資源
        driver.quit()

if __name__ == "__main__":
    main()
```

這個範例展示了如何結合使用各種提取器和處理器來實現一個完整的爬蟲任務，包括：

1. 列表頁面提取
2. 詳情頁面提取
3. 驗證碼處理
4. 分頁處理
5. 數據存儲
6. 錯誤處理
7. 資源清理 
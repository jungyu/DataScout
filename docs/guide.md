# 使用指南

## 概述

本指南提供系統的使用說明，包括安裝、配置、運行和測試等步驟。

## 安裝

### 環境要求

- Python 3.8 或更高版本
- pip 包管理器

### 安裝步驟

1. 克隆項目到本地：

   ```bash
   git clone https://github.com/yourusername/DataScout.git
   cd DataScout
   ```

2. 安裝依賴：

   ```bash
   pip install -r requirements.txt
   ```

3. 運行安裝腳本：

   ```bash
   python scripts/setup.py
   ```

## 配置

### 配置文件

系統使用以下配置文件：

- `config/storage.json`: 存儲配置
- `config/logging.json`: 日誌配置
- `config/security.json`: 安全配置

### 配置示例

#### 存儲配置

```json
{
  "mode": "local",
  "local": {
    "path": "data",
    "backup_path": "backups"
  },
  "mongodb": {
    "uri": "",
    "database": "",
    "collection": ""
  },
  "notion": {
    "token": "",
    "database_id": "",
    "parent_page_id": ""
  }
}
```

#### 日誌配置

```json
{
  "level": "INFO",
  "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  "file": "logs/app.log"
}
```

#### 安全配置

```json
{
  "encryption_key": "",
  "jwt_secret": "",
  "allowed_origins": []
}
```

## 運行

### 主程序

運行主程序：

```bash
python src/main.py
```

### 腳本

#### 安裝腳本

```bash
python scripts/setup.py
```

#### 測試腳本

```bash
python scripts/test.py
```

## 測試

### 運行測試

使用 `pytest` 運行測試：

```bash
pytest
```

### 生成測試報告

生成測試報告：

```bash
pytest --cov=src --cov-report=html
```

## 錯誤處理

系統使用 `ErrorHandler` 處理錯誤，並通過 `Logger` 記錄錯誤信息。錯誤狀態通過 `_update_status` 追蹤。

## 日誌記錄

系統使用 `Logger` 記錄日誌，日誌文件位於 `logs/app.log`。

## 備份和恢復

系統支持數據備份和恢復，使用 `StorageHandler` 的 `create_backup` 和 `restore_backup` 方法。

## 蝦皮爬蟲

這是一個基於 Selenium 的蝦皮爬蟲專案，提供商品搜尋、產品詳情爬取和購物車操作功能。

### 功能特點

- 商品搜尋
- 產品詳情爬取
- 購物車操作
- 自動處理驗證碼
- 配置化管理
- 錯誤處理和日誌記錄

### 安裝需求

- Python 3.8+
- Chrome 瀏覽器
- ChromeDriver

### 安裝步驟

1. 克隆專案：
```bash
git clone https://github.com/yourusername/crawler-selenium.git
cd crawler-selenium
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

3. 安裝 Chrome 和 ChromeDriver：
```bash
# macOS
brew install --cask google-chrome
brew install chromedriver

# Ubuntu
sudo apt-get install google-chrome-stable
sudo apt-get install chromium-chromedriver
```

### 使用方法

#### 1. 搜尋商品

```bash
# 基本搜尋
python -m examples.src.shopee.main --keyword "手機"

# 指定爬取頁數
python -m examples.src.shopee.main --keyword "手機" --max-pages 3

# 指定配置文件和輸出
python -m examples.src.shopee.main --keyword "手機" \
    --config "examples/config/shopee/formal/search.json" \
    --output "data/products.json"
```

#### 2. 爬取指定產品

```bash
# 爬取單個產品
python -m examples.src.shopee.main --product-ids "123456"

# 爬取多個產品
python -m examples.src.shopee.main --product-ids "123456,789012"
```

#### 3. 購物車操作

```python
from examples.src.shopee.order import ShopeeOrder

# 初始化
order = ShopeeOrder("examples/config/shopee/formal/search.json")

# 加入購物車
order.add_to_cart(
    product_id="123456",
    quantity=2,
    variants={"顏色": "紅色", "尺寸": "L"}
)

# 查看購物車
cart_items = order.view_cart()
for item in cart_items:
    print(f"商品: {item['title']}")
    print(f"數量: {item['quantity']}")
    print(f"規格: {item['variants']}")

# 更新購物車
order.update_cart_item(
    product_id="123456",
    quantity=3
)

# 移除商品
order.remove_from_cart("123456")

# 結帳
order.checkout()
```

### 配置說明

配置文件位於 `examples/config/shopee/formal/` 目錄下：

- `search.json`: 搜尋相關配置
- `order.json`: 購物車相關配置

#### 搜尋配置示例

```json
{
    "search": {
        "selectors": {
            "product_list": ".product-list",
            "product_item": ".product-item",
            "title": ".product-title",
            "price": ".product-price",
            "shop": ".shop-name",
            "location": ".location"
        },
        "timeouts": {
            "search_load": 10,
            "page_load": 5
        }
    }
}
```

#### 購物車配置示例

```json
{
    "order": {
        "selectors": {
            "add_to_cart_button": ".add-to-cart",
            "cart_button": ".cart-icon",
            "cart_container": ".cart-container",
            "cart_item": ".cart-item",
            "checkout_button": ".checkout-button"
        },
        "timeouts": {
            "add_to_cart": 5,
            "cart_load": 10,
            "checkout_load": 15
        }
    }
}
```

### 注意事項

1. 請遵守蝦皮的使用條款和爬蟲規範
2. 建議設置適當的爬取間隔，避免對目標網站造成負擔
3. 使用代理 IP 時請確保代理的可用性和穩定性
4. 定期更新配置文件中的選擇器，以適應網站的變化

### 錯誤處理

- 驗證碼錯誤：自動重試或切換代理
- 網絡錯誤：自動重試
- 解析錯誤：記錄錯誤並繼續下一個項目
- 配置錯誤：提供詳細的錯誤信息

### 日誌記錄

日誌文件位於 `examples/data/logs/` 目錄下：

- `crawler.log`: 爬蟲運行日誌
- `error.log`: 錯誤日誌
- `access.log`: 訪問日誌
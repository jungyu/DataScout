# Shopee 爬蟲核心功能 API

## 模組說明

`ShopeeCrawler` 類別提供蝦皮商品爬蟲的核心功能，包括商品搜尋、商品詳情爬取等功能。

## 類別

### ShopeeCrawler

#### 初始化

```python
def __init__(self, config: Dict[str, Any]) -> None:
    """
    初始化爬蟲物件
    
    Args:
        config: 配置字典，包含瀏覽器、請求、儲存等設定
    """
```

#### 方法

##### search_products

```python
def search_products(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    搜尋商品
    
    Args:
        keyword: 搜尋關鍵字
        limit: 搜尋結果數量限制，預設為 10
        
    Returns:
        商品列表，每個商品包含 id、name、price、rating、sold 等資訊
        
    Raises:
        CrawlerException: 搜尋失敗時拋出
    """
```

##### get_product_details

```python
def get_product_details(self, product_id: str) -> Dict[str, Any]:
    """
    爬取商品詳情
    
    Args:
        product_id: 商品 ID
        
    Returns:
        商品詳情，包含 id、name、price、rating、sold、description、specifications、images 等資訊
        
    Raises:
        CrawlerException: 爬取失敗時拋出
    """
```

##### _parse_search_results

```python
def _parse_search_results(self, page: Any) -> List[Dict[str, Any]]:
    """
    解析搜尋結果頁面
    
    Args:
        page: 頁面物件
        
    Returns:
        商品列表，每個商品包含 id、name、price、rating、sold 等資訊
    """
```

##### _parse_product_details

```python
def _parse_product_details(self, page: Any) -> Dict[str, Any]:
    """
    解析商品詳情頁面
    
    Args:
        page: 頁面物件
        
    Returns:
        商品詳情，包含 id、name、price、rating、sold、description、specifications、images 等資訊
    """
```

## 範例

### 搜尋商品

```python
from src.core.shopee_crawler import ShopeeCrawler

# 建立爬蟲物件
crawler = ShopeeCrawler(config)

# 搜尋商品
results = crawler.search_products("手機", limit=5)

# 輸出結果
for product in results:
    print(f"商品 ID: {product['id']}")
    print(f"商品名稱: {product['name']}")
    print(f"商品價格: {product['price']}")
    print(f"商品評分: {product['rating']}")
    print(f"商品銷量: {product['sold']}")
    print("---")
```

### 爬取商品詳情

```python
from src.core.shopee_crawler import ShopeeCrawler

# 建立爬蟲物件
crawler = ShopeeCrawler(config)

# 爬取商品詳情
details = crawler.get_product_details("123456")

# 輸出結果
print(f"商品 ID: {details['id']}")
print(f"商品名稱: {details['name']}")
print(f"商品價格: {details['price']}")
print(f"商品評分: {details['rating']}")
print(f"商品銷量: {details['sold']}")
print(f"商品描述: {details['description']}")
print("商品規格:")
for key, value in details['specifications'].items():
    print(f"  {key}: {value}")
print("商品圖片:")
for image in details['images']:
    print(f"  {image}")
```

## 錯誤處理

爬蟲在執行過程中可能會遇到以下錯誤：

- `CrawlerException`: 爬蟲執行錯誤，例如搜尋失敗、爬取失敗等

範例：

```python
from src.core.shopee_crawler import ShopeeCrawler
from src.core.exceptions import CrawlerException

try:
    # 建立爬蟲物件
    crawler = ShopeeCrawler(config)
    
    # 搜尋商品
    results = crawler.search_products("手機", limit=5)
    
    # 輸出結果
    for product in results:
        print(f"商品 ID: {product['id']}")
        print(f"商品名稱: {product['name']}")
        print(f"商品價格: {product['price']}")
        print(f"商品評分: {product['rating']}")
        print(f"商品銷量: {product['sold']}")
        print("---")
except CrawlerException as e:
    print(f"爬蟲執行錯誤: {e}") 
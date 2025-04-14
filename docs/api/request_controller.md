# 請求控制 API

## 模組說明

`RequestController` 類別提供請求控制功能，包括請求限制、請求重試、請求記錄等功能。

## 類別

### RequestController

#### 初始化

```python
def __init__(self, config: Dict[str, Any]) -> None:
    """
    初始化請求控制物件
    
    Args:
        config: 配置字典，包含請求控制設定
    """
```

#### 方法

##### create_session

```python
def create_session(self) -> Session:
    """
    建立請求會話
    
    Returns:
        請求會話物件
        
    Raises:
        RequestException: 建立會話失敗時拋出
    """
```

##### check_rate_limit

```python
def check_rate_limit(self, limit_type: str) -> bool:
    """
    檢查請求限制
    
    Args:
        limit_type: 限制類型，可為 "minute"、"hour" 或 "day"
        
    Returns:
        是否超過限制
        
    Raises:
        RequestException: 檢查限制失敗時拋出
    """
```

##### record_request

```python
def record_request(self, limit_type: str) -> None:
    """
    記錄請求
    
    Args:
        limit_type: 限制類型，可為 "minute"、"hour" 或 "day"
        
    Raises:
        RequestException: 記錄請求失敗時拋出
    """
```

##### cleanup_records

```python
def cleanup_records(self) -> None:
    """
    清理過期記錄
    
    Raises:
        RequestException: 清理記錄失敗時拋出
    """
```

##### get

```python
def get(self, url: str, **kwargs) -> Response:
    """
    發送 GET 請求
    
    Args:
        url: 請求網址
        **kwargs: 請求參數
        
    Returns:
        回應物件
        
    Raises:
        RequestException: 請求失敗時拋出
    """
```

##### post

```python
def post(self, url: str, **kwargs) -> Response:
    """
    發送 POST 請求
    
    Args:
        url: 請求網址
        **kwargs: 請求參數
        
    Returns:
        回應物件
        
    Raises:
        RequestException: 請求失敗時拋出
    """
```

##### put

```python
def put(self, url: str, **kwargs) -> Response:
    """
    發送 PUT 請求
    
    Args:
        url: 請求網址
        **kwargs: 請求參數
        
    Returns:
        回應物件
        
    Raises:
        RequestException: 請求失敗時拋出
    """
```

##### delete

```python
def delete(self, url: str, **kwargs) -> Response:
    """
    發送 DELETE 請求
    
    Args:
        url: 請求網址
        **kwargs: 請求參數
        
    Returns:
        回應物件
        
    Raises:
        RequestException: 請求失敗時拋出
    """
```

##### head

```python
def head(self, url: str, **kwargs) -> Response:
    """
    發送 HEAD 請求
    
    Args:
        url: 請求網址
        **kwargs: 請求參數
        
    Returns:
        回應物件
        
    Raises:
        RequestException: 請求失敗時拋出
    """
```

##### options

```python
def options(self, url: str, **kwargs) -> Response:
    """
    發送 OPTIONS 請求
    
    Args:
        url: 請求網址
        **kwargs: 請求參數
        
    Returns:
        回應物件
        
    Raises:
        RequestException: 請求失敗時拋出
    """
```

##### patch

```python
def patch(self, url: str, **kwargs) -> Response:
    """
    發送 PATCH 請求
    
    Args:
        url: 請求網址
        **kwargs: 請求參數
        
    Returns:
        回應物件
        
    Raises:
        RequestException: 請求失敗時拋出
    """
```

##### close

```python
def close(self) -> None:
    """
    關閉會話
    
    Raises:
        RequestException: 關閉會話失敗時拋出
    """
```

## 範例

### 建立請求會話

```python
from src.core.request_controller import RequestController

# 建立請求控制物件
request_controller = RequestController(config)

# 建立請求會話
session = request_controller.create_session()

# 使用會話
response = session.get("https://www.example.com")

# 關閉會話
request_controller.close()
```

### 檢查請求限制

```python
from src.core.request_controller import RequestController

# 建立請求控制物件
request_controller = RequestController(config)

# 檢查分鐘限制
if request_controller.check_rate_limit("minute"):
    print("超過分鐘限制")
else:
    print("未超過分鐘限制")

# 檢查小時限制
if request_controller.check_rate_limit("hour"):
    print("超過小時限制")
else:
    print("未超過小時限制")

# 檢查天數限制
if request_controller.check_rate_limit("day"):
    print("超過天數限制")
else:
    print("未超過天數限制")
```

### 記錄請求

```python
from src.core.request_controller import RequestController

# 建立請求控制物件
request_controller = RequestController(config)

# 記錄分鐘請求
request_controller.record_request("minute")

# 記錄小時請求
request_controller.record_request("hour")

# 記錄天數請求
request_controller.record_request("day")
```

### 清理過期記錄

```python
from src.core.request_controller import RequestController

# 建立請求控制物件
request_controller = RequestController(config)

# 清理過期記錄
request_controller.cleanup_records()
```

### 發送請求

```python
from src.core.request_controller import RequestController

# 建立請求控制物件
request_controller = RequestController(config)

# 發送 GET 請求
response = request_controller.get("https://www.example.com")

# 發送 POST 請求
response = request_controller.post("https://www.example.com", json={"key": "value"})

# 發送 PUT 請求
response = request_controller.put("https://www.example.com", json={"key": "value"})

# 發送 DELETE 請求
response = request_controller.delete("https://www.example.com")

# 發送 HEAD 請求
response = request_controller.head("https://www.example.com")

# 發送 OPTIONS 請求
response = request_controller.options("https://www.example.com")

# 發送 PATCH 請求
response = request_controller.patch("https://www.example.com", json={"key": "value"})
```

## 錯誤處理

請求控制在執行過程中可能會遇到以下錯誤：

- `RequestException`: 請求控制錯誤，例如建立會話失敗、檢查限制失敗、記錄請求失敗、清理記錄失敗、請求失敗、關閉會話失敗等

範例：

```python
from src.core.request_controller import RequestController
from src.core.exceptions import RequestException

try:
    # 建立請求控制物件
    request_controller = RequestController(config)
    
    # 建立請求會話
    session = request_controller.create_session()
    
    # 使用會話
    response = session.get("https://www.example.com")
    
    # 關閉會話
    request_controller.close()
except RequestException as e:
    print(f"請求控制錯誤: {e}") 
# 瀏覽器配置 API

## 模組說明

`BrowserProfile` 類別提供瀏覽器配置功能，包括瀏覽器選項設定、瀏覽器驅動建立、擴充功能管理等功能。

## 類別

### BrowserProfile

#### 初始化

```python
def __init__(self, config: Dict[str, Any]) -> None:
    """
    初始化瀏覽器配置物件
    
    Args:
        config: 配置字典，包含瀏覽器設定
    """
```

#### 方法

##### create_options

```python
def create_options(self) -> Options:
    """
    建立瀏覽器選項
    
    Returns:
        瀏覽器選項物件
        
    Raises:
        BrowserException: 建立選項失敗時拋出
    """
```

##### create_driver

```python
def create_driver(self) -> Any:
    """
    建立瀏覽器驅動
    
    Returns:
        瀏覽器驅動物件
        
    Raises:
        BrowserException: 建立驅動失敗時拋出
    """
```

##### add_extensions

```python
def add_extensions(self, options: Options, extensions: List[str]) -> None:
    """
    新增擴充功能
    
    Args:
        options: 瀏覽器選項物件
        extensions: 擴充功能路徑列表
        
    Raises:
        BrowserException: 新增擴充功能失敗時拋出
    """
```

##### set_proxy

```python
def set_proxy(self, options: Options, proxy: str) -> None:
    """
    設定代理
    
    Args:
        options: 瀏覽器選項物件
        proxy: 代理伺服器地址
    """
```

##### set_user_agent

```python
def set_user_agent(self, options: Options, user_agent: str) -> None:
    """
    設定使用者代理
    
    Args:
        options: 瀏覽器選項物件
        user_agent: 使用者代理字串
    """
```

##### set_language

```python
def set_language(self, options: Options, language: str) -> None:
    """
    設定語言
    
    Args:
        options: 瀏覽器選項物件
        language: 語言代碼
    """
```

##### set_timezone

```python
def set_timezone(self, options: Options, timezone: str) -> None:
    """
    設定時區
    
    Args:
        options: 瀏覽器選項物件
        timezone: 時區名稱
    """
```

##### set_geolocation

```python
def set_geolocation(self, options: Options, geolocation: Dict[str, float]) -> None:
    """
    設定地理位置
    
    Args:
        options: 瀏覽器選項物件
        geolocation: 地理位置字典，包含 latitude 和 longitude
    """
```

## 範例

### 建立瀏覽器選項

```python
from src.core.browser_profile import BrowserProfile

# 建立瀏覽器配置物件
browser_profile = BrowserProfile(config)

# 建立瀏覽器選項
options = browser_profile.create_options()

# 設定代理
browser_profile.set_proxy(options, "http://proxy.example.com:8080")

# 設定使用者代理
browser_profile.set_user_agent(options, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# 設定語言
browser_profile.set_language(options, "zh-TW")

# 設定時區
browser_profile.set_timezone(options, "Asia/Taipei")

# 設定地理位置
browser_profile.set_geolocation(options, {"latitude": 25.0330, "longitude": 121.5654})
```

### 建立瀏覽器驅動

```python
from src.core.browser_profile import BrowserProfile

# 建立瀏覽器配置物件
browser_profile = BrowserProfile(config)

# 建立瀏覽器驅動
driver = browser_profile.create_driver()

# 使用驅動
driver.get("https://www.example.com")

# 關閉驅動
driver.quit()
```

### 新增擴充功能

```python
from src.core.browser_profile import BrowserProfile

# 建立瀏覽器配置物件
browser_profile = BrowserProfile(config)

# 建立瀏覽器選項
options = browser_profile.create_options()

# 新增擴充功能
browser_profile.add_extensions(options, ["extension1.crx", "extension2.crx"])

# 建立瀏覽器驅動
driver = browser_profile.create_driver()

# 使用驅動
driver.get("https://www.example.com")

# 關閉驅動
driver.quit()
```

## 錯誤處理

瀏覽器配置在執行過程中可能會遇到以下錯誤：

- `BrowserException`: 瀏覽器配置錯誤，例如建立選項失敗、建立驅動失敗、新增擴充功能失敗等

範例：

```python
from src.core.browser_profile import BrowserProfile
from src.core.exceptions import BrowserException

try:
    # 建立瀏覽器配置物件
    browser_profile = BrowserProfile(config)
    
    # 建立瀏覽器選項
    options = browser_profile.create_options()
    
    # 建立瀏覽器驅動
    driver = browser_profile.create_driver()
    
    # 使用驅動
    driver.get("https://www.example.com")
    
    # 關閉驅動
    driver.quit()
except BrowserException as e:
    print(f"瀏覽器配置錯誤: {e}") 
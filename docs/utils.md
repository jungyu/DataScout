# 工具模組說明

本文檔詳細說明了爬蟲系統的工具模組及其功能。

## 目錄

1. [概述](#概述)
2. [日誌記錄模組](#日誌記錄模組)
3. [錯誤處理模組](#錯誤處理模組)
4. [Cookie 管理模組](#cookie-管理模組)
5. [配置載入模組](#配置載入模組)
6. [使用示例](#使用示例)
7. [最佳實踐](#最佳實踐)

## 概述

工具模組提供了爬蟲系統中常用的功能，包括日誌記錄、錯誤處理、Cookie 管理和配置載入等。這些工具模組設計為可重用的組件，可以在系統的不同部分使用，提高代碼的可維護性和可讀性。

主要功能包括：
- 統一的日誌記錄機制
- 全面的錯誤處理和報告
- Cookie 的保存、載入和管理
- 配置文件的載入、合併和驗證

## 日誌記錄模組

日誌記錄模組 (`logger.py`) 提供了統一的日誌記錄功能，支持輸出到控制台和文件。

### 主要類和函數

#### `Logger` 類

```python
class Logger:
    def __init__(
        self, 
        name: str, 
        level: int = logging.INFO,
        log_to_console: bool = True,
        log_to_file: bool = False,
        log_dir: str = "logs",
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ):
        # 初始化日誌記錄器
        ...
    
    def get_logger(self) -> logging.Logger:
        # 獲取記錄器實例
        ...
```

#### `setup_logger` 函數

```python
def setup_logger(
    name: str = "crawler", 
    level: int = logging.INFO,
    log_to_file: bool = False
) -> logging.Logger:
    # 設置並獲取記錄器
    ...
```

### 使用示例

```python
from src.utils.logger import setup_logger

# 創建記錄器
logger = setup_logger(name="my_crawler", log_to_file=True)

# 記錄不同級別的日誌
logger.info("開始爬取任務")
logger.debug("詳細調試信息")
logger.warning("警告信息")
logger.error("錯誤信息")
```

## 錯誤處理模組

錯誤處理模組 (`error_handler.py`) 提供了全面的錯誤處理、記錄和報告功能，支持異常捕獲、重試機制和錯誤分類。

### 主要類和函數

#### `ErrorHandler` 類

```python
class ErrorHandler:
    def __init__(self, logger: Optional[logging.Logger] = None):
        # 初始化錯誤處理器
        ...
    
    def handle_exception(
        self, 
        exception: Exception, 
        driver: Optional[webdriver.Remote] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        # 處理異常
        ...
    
    def log_error(self, message: str, error: Optional[Exception] = None) -> None:
        # 記錄錯誤
        ...
```

#### 錯誤類

```python
class RetryableError(Exception):
    # 可重試的錯誤
    pass

class FatalError(Exception):
    # 致命錯誤
    pass

class CrawlerError(Exception):
    # 爬蟲錯誤基類
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        # 初始化爬蟲錯誤
        ...
    
    def to_dict(self) -> Dict:
        # 轉換為字典
        ...

class NetworkError(CrawlerError, RetryableError):
    # 網絡錯誤
    pass

class AuthenticationError(CrawlerError, FatalError):
    # 認證錯誤
    pass

class CaptchaError(CrawlerError, RetryableError):
    # 驗證碼錯誤
    pass

class DataExtractionError(CrawlerError):
    # 數據提取錯誤
    pass

class AntiCrawlingError(CrawlerError, RetryableError):
    # 反爬蟲錯誤
    pass

class ConfigurationError(CrawlerError, FatalError):
    # 配置錯誤
    pass
```

#### 裝飾器函數

```python
def retry_on_exception(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    on_retry: Callable[[Exception, int, float], None] = None,
    logger_name: str = None
):
    # 重試裝飾器
    ...

def handle_exception(
    func: Callable = None,
    error_map: Dict[Type[Exception], Type[CrawlerError]] = None,
    default_error: Type[CrawlerError] = CrawlerError,
    log_traceback: bool = True,
    error_callback: Callable[[Exception], None] = None,
    logger_name: str = None
):
    # 異常處理裝飾器
    ...

def safe_execute(
    func: Callable,
    *args,
    default_return: Any = None,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    log_error: bool = True,
    error_message: str = None,
    logger_name: str = None,
    **kwargs
) -> Any:
    # 安全執行函數
    ...

def error_boundary(
    default_return: Any = None,
    log_error: bool = True,
    error_callback: Callable[[Exception], None] = None
):
    # 錯誤邊界裝飾器
    ...
```

#### `ErrorCollector` 類

```python
class ErrorCollector:
    def __init__(self, logger_name: str = None, raise_on_error: bool = False):
        # 初始化錯誤收集器
        ...
    
    def collect(self, func: Callable, *args, error_context: Dict = None, **kwargs) -> Any:
        # 收集錯誤
        ...
    
    def has_errors(self) -> bool:
        # 檢查是否有錯誤
        ...
    
    def get_errors(self) -> List[Dict]:
        # 獲取所有錯誤
        ...
    
    def clear_errors(self):
        # 清空錯誤
        ...
    
    def raise_if_errors(self, error_class: Type[Exception] = Exception):
        # 如果有錯誤則拋出異常
        ...
    
    def __enter__(self):
        # 上下文管理器入口
        ...
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 上下文管理器出口
        ...
```

### 使用示例

```python
from src.utils.error_handler import (
    ErrorHandler, 
    retry_on_exception, 
    handle_exception, 
    NetworkError, 
    CaptchaError
)
from src.utils.logger import setup_logger

# 創建記錄器和錯誤處理器
logger = setup_logger("my_crawler")
error_handler = ErrorHandler(logger)

# 使用重試裝飾器
@retry_on_exception(retries=3, delay=1.0, exceptions=(NetworkError, CaptchaError))
def fetch_page(url):
    # 獲取頁面
    ...

# 使用異常處理裝飾器
@handle_exception(error_map={ValueError: NetworkError})
def parse_data(html):
    # 解析數據
    ...

# 使用錯誤收集器
with ErrorCollector(logger_name="my_crawler") as collector:
    # 執行可能出錯的操作
    result = collector.collect(fetch_page, "https://example.com")
    
    # 檢查是否有錯誤
    if collector.has_errors():
        errors = collector.get_errors()
        print(f"發生 {len(errors)} 個錯誤")
```

## Cookie 管理模組

Cookie 管理模組 (`cookie_manager.py`) 提供了 Cookie 的保存、載入、更新和管理功能，支持多種格式的 Cookie 儲存和不同瀏覽器的 Cookie 轉換。

### 主要類

#### `CookieManager` 類

```python
class CookieManager:
    def __init__(
        self,
        cookie_dir: str = "cookies",
        cookie_expiry: int = 86400,  # 1天
        auto_save: bool = True,
        log_level: int = logging.INFO
    ):
        # 初始化Cookie管理器
        ...
    
    def _get_cookie_path(self, domain: str, format: str = "json") -> str:
        # 獲取Cookie文件路徑
        ...
    
    def save_cookies(
        self,
        driver: WebDriver,
        domain: str = None,
        format: str = "json",
        metadata: Dict = None
    ) -> bool:
        # 保存瀏覽器中的Cookie
        ...
    
    def load_cookies(
        self,
        driver: WebDriver,
        domain: str = None,
        format: str = "json",
        check_expiry: bool = True
    ) -> int:
        # 載入Cookie到瀏覽器
        ...
    
    def delete_cookies(self, domain: str, format: str = "json") -> bool:
        # 刪除Cookie
        ...
    
    def update_cookies(
        self, 
        driver: WebDriver,
        domain: str = None,
        format: str = "json",
        merge: bool = True
    ) -> bool:
        # 更新Cookie
        ...
    
    def get_cookies(self, domain: str, format: str = "json") -> List[Dict]:
        # 獲取Cookie
        ...
    
    def get_cookie_metadata(self, domain: str, format: str = "json") -> Dict:
        # 獲取Cookie元數據
        ...
    
    def is_cookie_valid(self, domain: str, format: str = "json") -> bool:
        # 檢查Cookie是否有效
        ...
    
    def list_domains(self, format: str = "json") -> List[str]:
        # 列出所有域名
        ...
    
    def serialize_cookies_to_string(self, domain: str, format: str = "json") -> str:
        # 將Cookie序列化為字符串
        ...
```

### 使用示例

```python
from src.utils.cookie_manager import CookieManager
from selenium import webdriver

# 創建Cookie管理器
cookie_manager = CookieManager(cookie_dir="my_cookies")

# 初始化WebDriver
driver = webdriver.Chrome()

# 訪問網站
driver.get("https://example.com")

# 保存Cookie
cookie_manager.save_cookies(driver, domain="example.com")

# 關閉瀏覽器
driver.quit()

# 重新初始化WebDriver
driver = webdriver.Chrome()

# 載入Cookie
cookie_manager.load_cookies(driver, domain="example.com")

# 訪問需要登錄的頁面
driver.get("https://example.com/profile")
```

## 配置載入模組

配置載入模組 (`config_loader.py`) 提供了從 JSON 或 YAML 文件載入配置的功能，支持敏感信息的加密/解密，以及配置合併和驗證。

### 主要類

#### `ConfigLoader` 類

```python
class ConfigLoader:
    @classmethod
    def load_config(cls, config_file: str, default_config: Dict = None) -> Dict:
        # 從文件載入配置
        ...
    
    @classmethod
    def _load_config_file(cls, file_path: str) -> Dict:
        # 從文件載入配置，支持JSON和YAML格式
        ...
    
    @classmethod
    def _load_credentials(cls, credentials_file: str) -> Dict:
        # 載入憑證
        ...
    
    @classmethod
    def _encrypt_config(cls, config: Dict, password: str = None) -> Dict:
        # 加密配置
        ...
    
    @classmethod
    def _decrypt_config(cls, config: Dict, password: str = None) -> Dict:
        # 解密配置
        ...
    
    @classmethod
    def _merge_configs(cls, target: Dict, source: Dict, override: bool = True) -> Dict:
        # 合併配置
        ...
    
    @classmethod
    def save_config(cls, config: Dict, file_path: str, encrypt: bool = False, password: str = None) -> bool:
        # 保存配置
        ...
    
    @classmethod
    def validate_config(cls, config: Dict, schema: Dict) -> Dict:
        # 驗證配置
        ...
    
    @classmethod
    def get_nested_value(cls, config: Dict, path: str, default: Any = None) -> Any:
        # 獲取嵌套值
        ...
```

### 使用示例

```python
from src.utils.config_loader import ConfigLoader

# 載入配置
config = ConfigLoader.load_config("config.json")

# 載入配置並合併默認配置
default_config = {
    "timeout": 30,
    "retries": 3,
    "user_agent": "Mozilla/5.0"
}
config = ConfigLoader.load_config("config.json", default_config)

# 保存配置
ConfigLoader.save_config(config, "new_config.json")

# 加密保存配置
ConfigLoader.save_config(config, "secure_config.json", encrypt=True, password="my_password")

# 驗證配置
schema = {
    "type": "object",
    "properties": {
        "timeout": {"type": "integer"},
        "retries": {"type": "integer"},
        "user_agent": {"type": "string"}
    },
    "required": ["timeout", "retries"]
}
validated_config = ConfigLoader.validate_config(config, schema)

# 獲取嵌套值
timeout = ConfigLoader.get_nested_value(config, "browser.timeout", default=30)
```

## 使用示例

### 綜合使用示例

```python
from src.utils.logger import setup_logger
from src.utils.error_handler import ErrorHandler, retry_on_exception, NetworkError
from src.utils.cookie_manager import CookieManager
from src.utils.config_loader import ConfigLoader
from selenium import webdriver

# 載入配置
config = ConfigLoader.load_config("crawler_config.json")

# 設置日誌
logger = setup_logger(
    name="my_crawler",
    level=config.get("log_level", "INFO"),
    log_to_file=config.get("log_to_file", True)
)

# 創建錯誤處理器
error_handler = ErrorHandler(logger)

# 創建Cookie管理器
cookie_manager = CookieManager(
    cookie_dir=config.get("cookie_dir", "cookies"),
    cookie_expiry=config.get("cookie_expiry", 86400),
    auto_save=config.get("auto_save_cookies", True)
)

# 初始化WebDriver
driver = webdriver.Chrome()

# 使用重試裝飾器
@retry_on_exception(retries=3, delay=1.0, exceptions=(NetworkError,))
def crawl_page(url):
    try:
        # 載入Cookie
        cookie_manager.load_cookies(driver, domain="example.com")
        
        # 訪問頁面
        driver.get(url)
        
        # 提取數據
        data = extract_data(driver)
        
        # 更新Cookie
        cookie_manager.update_cookies(driver, domain="example.com")
        
        return data
    except Exception as e:
        # 處理異常
        error_details = error_handler.handle_exception(e, driver)
        logger.error(f"爬取頁面失敗: {error_details['error_message']}")
        raise

# 執行爬蟲
try:
    data = crawl_page("https://example.com")
    logger.info(f"成功爬取數據: {len(data)} 條記錄")
except Exception as e:
    logger.error(f"爬蟲執行失敗: {str(e)}")
finally:
    # 關閉瀏覽器
    driver.quit()
```

## 最佳實踐

1. **日誌記錄**：
   - 使用適當的日誌級別（DEBUG, INFO, WARNING, ERROR, CRITICAL）
   - 在生產環境中啟用文件日誌
   - 定期輪換日誌文件以避免佔用過多磁盤空間

2. **錯誤處理**：
   - 使用適當的錯誤類型進行異常分類
   - 對於可恢復的錯誤使用重試機制
   - 記錄詳細的錯誤信息和上下文
   - 使用錯誤收集器批量處理多個操作

3. **Cookie 管理**：
   - 定期更新 Cookie 以保持會話有效
   - 在重要操作前檢查 Cookie 有效性
   - 使用元數據記錄 Cookie 的來源和時間戳

4. **配置管理**：
   - 將敏感信息存儲在單獨的憑證文件中
   - 使用配置驗證確保配置的正確性
   - 提供合理的默認配置
   - 支持配置的繼承和覆蓋

5. **資源管理**：
   - 使用上下文管理器（with 語句）確保資源正確釋放
   - 在不需要時關閉 WebDriver 實例
   - 定期清理過期的 Cookie 和日誌文件

6. **代碼組織**：
   - 將工具模組與業務邏輯分離
   - 使用裝飾器減少重複代碼
   - 提供清晰的文檔和示例 
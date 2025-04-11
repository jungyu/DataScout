"""
爬蟲系統異常處理模組

定義了爬蟲系統中使用的所有自定義異常類，包括：
- 配置相關異常
- 網絡相關異常
- 解析相關異常
- 資源相關異常
- 狀態相關異常
- 數據相關異常
"""

from typing import Optional, Any, Dict

class CrawlerException(Exception):
    """爬蟲基礎異常類"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        初始化異常
        
        Args:
            message: 錯誤訊息
            details: 詳細信息
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        """返回異常的字符串表示"""
        if self.details:
            return f"{self.message} - 詳細信息: {self.details}"
        return self.message

class ConfigError(CrawlerException):
    """配置錯誤"""
    pass

class InvalidConfigError(ConfigError):
    """無效的配置"""
    pass

class MissingConfigError(ConfigError):
    """缺少配置"""
    pass

class NetworkError(CrawlerException):
    """網絡錯誤"""
    pass

class ConnectionError(NetworkError):
    """連接錯誤"""
    pass

class TimeoutError(NetworkError):
    """超時錯誤"""
    pass

class ProxyError(NetworkError):
    """代理錯誤"""
    pass

class SSLError(NetworkError):
    """SSL錯誤"""
    pass

class ParseError(CrawlerException):
    """解析錯誤"""
    pass

class HTMLParseError(ParseError):
    """HTML解析錯誤"""
    pass

class JSONParseError(ParseError):
    """JSON解析錯誤"""
    pass

class XPathError(ParseError):
    """XPath錯誤"""
    pass

class ResourceError(CrawlerException):
    """資源錯誤"""
    pass

class WebDriverError(ResourceError):
    """WebDriver錯誤"""
    pass

class BrowserError(ResourceError):
    """瀏覽器錯誤"""
    pass

class CookieError(ResourceError):
    """Cookie錯誤"""
    pass

class StateError(CrawlerException):
    """狀態錯誤"""
    pass

class TaskStateError(StateError):
    """任務狀態錯誤"""
    pass

class CheckpointError(StateError):
    """檢查點錯誤"""
    pass

class DataError(CrawlerException):
    """數據錯誤"""
    pass

class ValidationError(DataError):
    """驗證錯誤"""
    pass

class StorageError(DataError):
    """存儲錯誤"""
    pass

class ProcessingError(DataError):
    """處理錯誤"""
    pass

class NavigationError(CrawlerException):
    """導航錯誤"""
    pass

class ExtractionError(CrawlerException):
    """提取錯誤"""
    pass

def handle_exception(error: Exception, logger: Any) -> None:
    """
    處理異常的通用函數
    
    Args:
        error: 異常對象
        logger: 日誌記錄器
    """
    if isinstance(error, CrawlerException):
        # 處理自定義異常
        logger.error(f"爬蟲異常: {str(error)}")
        if error.details:
            logger.debug(f"異常詳細信息: {error.details}")
    else:
        # 處理其他異常
        logger.error(f"未處理的異常: {str(error)}")
        logger.exception(error) 
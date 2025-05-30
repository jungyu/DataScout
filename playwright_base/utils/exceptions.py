"""
異常處理模組

定義框架中使用的自訂異常類別。
"""

class PlaywrightBaseException(Exception):
    """
    爬蟲框架基礎異常類

    所有其他異常類都繼承自此類
    """
    def __init__(self, message: str = None, cause: Exception = None):
        """
        初始化異常

        Args:
            message: 錯誤訊息
            cause: 導致此異常的原始異常
        """
        self.message = message or "發生爬蟲框架錯誤"
        self.cause = cause
        super().__init__(self.message)

    def __str__(self) -> str:
        """格式化異常訊息，包含原始異常信息"""
        if self.cause:
            return f"{self.message} (原因: {type(self.cause).__name__}: {str(self.cause)})"
        return self.message


class BrowserException(PlaywrightBaseException):
    """
    瀏覽器操作相關異常

    包括瀏覽器啟動、關閉、配置等操作中的錯誤
    """
    def __init__(self, message: str = None, cause: Exception = None, details: dict = None):
        """
        初始化瀏覽器異常

        Args:
            message: 錯誤訊息
            cause: 導致此異常的原始異常
            details: 額外的錯誤詳情字典
        """
        message = message or "瀏覽器操作錯誤"
        self.details = details or {}
        super().__init__(message, cause)

    def __str__(self) -> str:
        """格式化異常訊息，加入詳細信息"""
        base_msg = super().__str__()
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{base_msg} [詳情: {details_str}]"
        return base_msg


class PageException(PlaywrightBaseException):
    """頁面相關異常"""
    def __init__(self, message: str = None, url: str = None, selector: str = None, cause: Exception = None):
        """
        初始化頁面異常

        Args:
            message: 錯誤訊息
            url: 當前頁面 URL
            selector: 相關的元素選擇器
            cause: 導致此異常的原始異常
        """
        self.url = url
        self.selector = selector
        context_info = f"URL: {url}, Selector: {selector}" if url or selector else ""
        full_message = f"{message} ({context_info})" if context_info else message
        super().__init__(full_message, cause)


class ElementException(PlaywrightBaseException):
    """元素相關異常"""
    pass


class ProxyException(PlaywrightBaseException):
    """代理相關異常"""
    pass


class CaptchaException(PlaywrightBaseException):
    """驗證碼相關異常"""
    pass


class AuthenticationException(PlaywrightBaseException):
    """認證相關異常"""
    pass


class ConfigException(PlaywrightBaseException):
    """配置相關異常"""
    pass


class StorageException(PlaywrightBaseException):
    """存儲相關異常"""
    pass


class NavigationException(PlaywrightBaseException):
    """導航相關異常"""
    pass


class RequestException(PlaywrightBaseException):
    """請求相關異常"""
    pass


class AntiDetectionException(PlaywrightBaseException):
    """反偵測相關異常"""
    pass


class TimeoutException(PlaywrightBaseException):
    """超時相關異常"""
    pass
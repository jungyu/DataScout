"""
錯誤處理模組

定義所有自定義異常類別
"""

class DataScoutError(Exception):
    """基礎異常類別"""
    pass

class ConfigError(DataScoutError):
    """配置錯誤"""
    pass

class LoggerError(DataScoutError):
    """日誌錯誤"""
    pass

class BrowserError(DataScoutError):
    """瀏覽器錯誤"""
    pass

class RequestError(DataScoutError):
    """請求錯誤"""
    pass

class StorageError(DataScoutError):
    """儲存錯誤"""
    pass

class ValidationError(DataScoutError):
    """驗證錯誤"""
    pass

class AuthenticationError(DataScoutError):
    """認證錯誤"""
    pass

class CaptchaError(DataScoutError):
    """驗證碼錯誤"""
    pass

class ProxyError(DataScoutError):
    """代理錯誤"""
    pass

class RateLimitError(DataScoutError):
    """速率限制錯誤"""
    pass

class TimeoutError(DataScoutError):
    """超時錯誤"""
    pass

class NetworkError(DataScoutError):
    """網路錯誤"""
    pass

class DatabaseError(DataScoutError):
    """資料庫錯誤"""
    pass

class FileError(DataScoutError):
    """檔案錯誤"""
    pass

class PermissionError(DataScoutError):
    """權限錯誤"""
    pass

class ResourceError(DataScoutError):
    """資源錯誤"""
    pass

class StateError(DataScoutError):
    """狀態錯誤"""
    pass

class InitializationError(DataScoutError):
    """初始化錯誤"""
    pass

class CleanupError(DataScoutError):
    """清理錯誤"""
    pass 
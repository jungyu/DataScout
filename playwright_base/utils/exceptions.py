"""
異常處理模組

定義框架中使用的自訂異常類別。
"""

class PlaywrightBaseException(Exception):
    """PlaywrightBase 框架基礎異常，所有其他異常都繼承自此類"""
    pass

class BrowserException(PlaywrightBaseException):
    """瀏覽器相關操作異常"""
    pass

class NavigationException(PlaywrightBaseException):
    """頁面導航異常"""
    pass

class ElementNotFoundException(PlaywrightBaseException):
    """元素未找到異常"""
    pass

class TimeoutException(PlaywrightBaseException):
    """操作超時異常"""
    pass

class CaptchaException(PlaywrightBaseException):
    """驗證碼相關異常"""
    pass

class ProxyException(PlaywrightBaseException):
    """代理服務器相關異常"""
    pass

class FingerprintException(PlaywrightBaseException):
    """指紋偽裝相關異常"""
    pass

class ConfigException(PlaywrightBaseException):
    """配置相關異常"""
    pass

class StorageException(PlaywrightBaseException):
    """存儲相關異常"""
    pass

class AuthenticationException(PlaywrightBaseException):
    """認證相關異常"""
    pass
"""
定義 Playwright Base 的異常類
"""

class PlaywrightBaseException(Exception):
    """基礎異常類"""
    pass


class BrowserException(PlaywrightBaseException):
    """瀏覽器相關異常"""
    pass


class PageException(PlaywrightBaseException):
    """頁面相關異常"""
    pass


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


class AntiDetectionException(Exception):
    """反偵測相關異常"""
    pass 
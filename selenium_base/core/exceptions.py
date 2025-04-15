#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
異常類模組

此模組定義了爬蟲系統中使用的各種異常類。
"""

from typing import Dict, Any, Optional

class DataScoutError(Exception):
    """基礎異常類"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化異常
        
        Args:
            message: 錯誤消息
            details: 錯誤詳情
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

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

class AuthenticationError(DataScoutError):
    """認證錯誤"""
    pass

class ProxyError(DataScoutError):
    """代理錯誤"""
    pass

class RateLimitError(DataScoutError):
    """速率限制錯誤"""
    pass

class CrawlerTimeoutError(DataScoutError):
    """超時異常"""
    pass

class NetworkError(DataScoutError):
    """網絡異常"""
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

class CrawlerException(DataScoutError):
    """爬蟲異常"""
    pass

class BrowserException(DataScoutError):
    """瀏覽器異常"""
    pass

class RequestException(DataScoutError):
    """請求異常"""
    pass

class ValidationError(DataScoutError):
    """驗證異常"""
    pass

class CaptchaError(DataScoutError):
    """驗證碼異常"""
    pass 
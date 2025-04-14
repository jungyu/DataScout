#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
持久化模組異常類

定義所有持久化相關的異常類型
"""

class PersistenceError(Exception):
    """持久化基礎異常類"""
    
    def __init__(self, message: str = None, code: int = None):
        self.message = message or "持久化操作發生錯誤"
        self.code = code or 500
        super().__init__(self.message)

class StorageError(PersistenceError):
    """存儲操作異常"""
    
    def __init__(self, message: str = None, code: int = None):
        super().__init__(
            message or "存儲操作失敗",
            code or 501
        )

class ValidationError(PersistenceError):
    """數據驗證異常"""
    
    def __init__(self, message: str = None, code: int = None):
        super().__init__(
            message or "數據驗證失敗",
            code or 400
        )

class ConfigError(PersistenceError):
    """配置錯誤異常"""
    
    def __init__(self, message: str = None, code: int = None):
        super().__init__(
            message or "配置參數無效",
            code or 400
        )

class ConnectionError(PersistenceError):
    """連接異常"""
    
    def __init__(self, message: str = None, code: int = None):
        super().__init__(
            message or "無法連接到存儲服務",
            code or 503
        )

class AuthenticationError(PersistenceError):
    """認證異常"""
    
    def __init__(self, message: str = None, code: int = None):
        super().__init__(
            message or "認證失敗",
            code or 401
        )

class PermissionError(PersistenceError):
    """權限異常"""
    
    def __init__(self, message: str = None, code: int = None):
        super().__init__(
            message or "沒有操作權限",
            code or 403
        )

class NotFoundError(PersistenceError):
    """資源不存在異常"""
    
    def __init__(self, message: str = None, code: int = None):
        super().__init__(
            message or "請求的資源不存在",
            code or 404
        )

class DuplicateError(PersistenceError):
    """資源重複異常"""
    
    def __init__(self, message: str = None, code: int = None):
        super().__init__(
            message or "資源已存在",
            code or 409
        )

class TimeoutError(PersistenceError):
    """超時異常"""
    
    def __init__(self, message: str = None, code: int = None):
        super().__init__(
            message or "操作超時",
            code or 504
        ) 
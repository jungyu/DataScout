#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自定義異常模組

定義數據提取過程中可能發生的各種異常
"""

class ExtractionError(Exception):
    """提取器基礎異常類，所有其他提取器異常的父類"""
    
    def __init__(self, message: str = "提取操作失敗", details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message} - {self.details}"
        return self.message


class ConfigurationError(ExtractionError):
    """配置錯誤，當提供的配置無效或缺少必要參數時引發"""
    
    def __init__(self, message: str = "配置錯誤", field: str = None, details: dict = None):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, details)


class ElementNotFoundError(ExtractionError):
    """元素不存在異常，當無法找到目標元素時引發"""
    
    def __init__(self, message: str = "找不到目標元素", selector: str = None, details: dict = None):
        details = details or {}
        if selector:
            details["selector"] = selector
        super().__init__(message, details)


class ElementAccessError(ExtractionError):
    """元素訪問異常，當無法訪問元素屬性或執行操作時引發"""
    
    def __init__(self, message: str = "無法訪問元素", operation: str = None, details: dict = None):
        details = details or {}
        if operation:
            details["operation"] = operation
        super().__init__(message, details)


class ParseError(ExtractionError):
    """解析錯誤，當無法解析數據時引發"""
    
    def __init__(self, message: str = "數據解析失敗", data_type: str = None, details: dict = None):
        details = details or {}
        if data_type:
            details["data_type"] = data_type
        super().__init__(message, details)


class CaptchaDetectedError(ExtractionError):
    """驗證碼檢測異常，當檢測到驗證碼時引發"""
    
    def __init__(self, message: str = "檢測到驗證碼", page_url: str = None, details: dict = None):
        details = details or {}
        if page_url:
            details["page_url"] = page_url
        super().__init__(message, details)


class NetworkError(ExtractionError):
    """網絡異常，當網絡連接出現問題時引發"""
    
    def __init__(self, message: str = "網絡連接錯誤", url: str = None, details: dict = None):
        details = details or {}
        if url:
            details["url"] = url
        super().__init__(message, details)


class TimeoutError(ExtractionError):
    """超時異常，當操作超時時引發"""
    
    def __init__(self, message: str = "操作超時", operation: str = None, timeout: int = None, details: dict = None):
        details = details or {}
        if operation:
            details["operation"] = operation
        if timeout:
            details["timeout"] = timeout
        super().__init__(message, details)


class NavigationError(ExtractionError):
    """導航異常，當頁面導航失敗時引發"""
    
    def __init__(self, message: str = "頁面導航失敗", url: str = None, details: dict = None):
        details = details or {}
        if url:
            details["url"] = url
        super().__init__(message, details)


class InvalidPageError(ExtractionError):
    """無效頁面異常，當頁面內容無效或不符合預期時引發"""
    
    def __init__(self, message: str = "無效的頁面內容", url: str = None, details: dict = None):
        details = details or {}
        if url:
            details["url"] = url
        super().__init__(message, details)


class RetryExceededError(ExtractionError):
    """重試次數超限異常，當重試次數超過限制時引發"""
    
    def __init__(self, message: str = "重試次數超過限制", max_retries: int = None, details: dict = None):
        details = details or {}
        if max_retries:
            details["max_retries"] = max_retries
        super().__init__(message, details)


class StorageError(ExtractionError):
    """存儲異常，當數據存儲失敗時引發"""
    
    def __init__(self, message: str = "數據存儲失敗", filepath: str = None, details: dict = None):
        details = details or {}
        if filepath:
            details["filepath"] = filepath
        super().__init__(message, details)


class TransformationError(ExtractionError):
    """轉換異常，當數據轉換失敗時引發"""
    
    def __init__(self, message: str = "數據轉換失敗", field: str = None, details: dict = None):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, details)


class ScriptExecutionError(ExtractionError):
    """腳本執行異常，當執行JavaScript腳本失敗時引發"""
    
    def __init__(self, message: str = "JavaScript腳本執行失敗", script: str = None, details: dict = None):
        details = details or {}
        if script:
            # 防止腳本過長
            script_excerpt = script[:100] + '...' if len(script) > 100 else script
            details["script"] = script_excerpt
        super().__init__(message, details)


class DataValidationError(ExtractionError):
    """數據驗證異常，當數據不符合預期格式或約束時引發"""
    
    def __init__(self, message: str = "數據驗證失敗", validation_rule: str = None, details: dict = None):
        details = details or {}
        if validation_rule:
            details["validation_rule"] = validation_rule
        super().__init__(message, details)
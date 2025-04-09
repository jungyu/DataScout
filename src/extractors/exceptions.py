#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自定義異常模組

定義數據提取過程中可能發生的各種異常。

主要異常類：
- ExtractionError: 提取器基礎異常類
- ConfigurationError: 配置錯誤
- ElementNotFoundError: 元素不存在異常
- ElementAccessError: 元素訪問異常
- ParseError: 解析錯誤
- CaptchaDetectedError: 驗證碼檢測異常
- NetworkError: 網絡異常
- TimeoutError: 超時異常
- NavigationError: 導航異常
- InvalidPageError: 無效頁面異常
- RetryExceededError: 重試超限異常
- StorageError: 存儲異常
- TransformationError: 轉換異常
- ScriptExecutionError: 腳本執行異常
- DataValidationError: 數據驗證異常

使用示例：
    try:
        # 嘗試提取數據
        extractor.extract_data()
    except ElementNotFoundError as e:
        print(f"找不到元素: {e.selector}")
    except CaptchaDetectedError as e:
        print(f"檢測到驗證碼: {e.page_url}")
    except ExtractionError as e:
        print(f"提取失敗: {e.message}")
"""

from typing import Dict, Optional, Any


class ExtractionError(Exception):
    """提取器基礎異常類
    
    所有其他提取器異常的父類，提供基本的錯誤信息和詳細信息存儲。
    
    Attributes:
        message: 錯誤信息
        details: 詳細信息字典
    """
    
    def __init__(self, message: str = "提取操作失敗", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - {self.details}"
        return self.message


class ConfigurationError(ExtractionError):
    """配置錯誤
    
    當提供的配置無效或缺少必要參數時引發。
    
    Attributes:
        message: 錯誤信息
        field: 出錯的配置字段
        details: 詳細信息字典
    """
    
    def __init__(self, message: str = "配置錯誤", field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, details)


class ElementNotFoundError(ExtractionError):
    """元素不存在異常
    
    當無法找到目標元素時引發。
    
    Attributes:
        message: 錯誤信息
        selector: 未找到的元素選擇器
        details: 詳細信息字典
    """
    
    def __init__(self, message: str = "找不到目標元素", selector: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if selector:
            details["selector"] = selector
        super().__init__(message, details)


class ElementAccessError(ExtractionError):
    """元素訪問異常
    
    當無法訪問元素屬性或執行操作時引發。
    
    Attributes:
        message: 錯誤信息
        operation: 失敗的操作
        details: 詳細信息字典
    """
    
    def __init__(self, message: str = "無法訪問元素", operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if operation:
            details["operation"] = operation
        super().__init__(message, details)


class ParseError(ExtractionError):
    """解析錯誤
    
    當無法解析數據時引發。
    
    Attributes:
        message: 錯誤信息
        data_type: 數據類型
        details: 詳細信息字典
    """
    
    def __init__(self, message: str = "數據解析失敗", data_type: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if data_type:
            details["data_type"] = data_type
        super().__init__(message, details)


class CaptchaDetectedError(ExtractionError):
    """驗證碼檢測異常
    
    當檢測到驗證碼時引發。
    
    Attributes:
        message: 錯誤信息
        page_url: 頁面URL
        details: 詳細信息字典
    """
    
    def __init__(self, message: str = "檢測到驗證碼", page_url: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if page_url:
            details["page_url"] = page_url
        super().__init__(message, details)


class NetworkError(ExtractionError):
    """網絡異常
    
    當網絡連接出現問題時引發。
    
    Attributes:
        message: 錯誤信息
        url: 請求的URL
        details: 詳細信息字典
    """
    
    def __init__(self, message: str = "網絡連接錯誤", url: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if url:
            details["url"] = url
        super().__init__(message, details)


class TimeoutError(ExtractionError):
    """超時異常
    
    當操作超時時引發。
    
    Attributes:
        message: 錯誤信息
        operation: 超時的操作
        timeout: 超時時間
        details: 詳細信息字典
    """
    
    def __init__(self, message: str = "操作超時", operation: Optional[str] = None, timeout: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if operation:
            details["operation"] = operation
        if timeout:
            details["timeout"] = timeout
        super().__init__(message, details)


class NavigationError(ExtractionError):
    """導航異常
    
    當頁面導航失敗時引發。
    
    Attributes:
        message: 錯誤信息
        url: 目標URL
        details: 詳細信息字典
    """
    
    def __init__(self, message: str = "頁面導航失敗", url: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if url:
            details["url"] = url
        super().__init__(message, details)


class InvalidPageError(ExtractionError):
    """無效頁面異常
    
    當頁面內容無效或不符合預期時引發。
    
    Attributes:
        message: 錯誤信息
        url: 頁面URL
        details: 詳細信息字典
    """
    
    def __init__(self, message: str = "無效的頁面內容", url: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if url:
            details["url"] = url
        super().__init__(message, details)


class RetryExceededError(ExtractionError):
    """重試超限異常
    
    當重試次數超過限制時引發。
    
    Attributes:
        message: 錯誤信息
        max_retries: 最大重試次數
        details: 詳細信息字典
    """
    
    def __init__(self, message: str = "重試次數超過限制", max_retries: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if max_retries:
            details["max_retries"] = max_retries
        super().__init__(message, details)


class StorageError(ExtractionError):
    """存儲異常
    
    當數據存儲失敗時引發。
    
    Attributes:
        message: 錯誤信息
        filepath: 文件路徑
        details: 詳細信息字典
    """
    
    def __init__(self, message: str = "數據存儲失敗", filepath: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if filepath:
            details["filepath"] = filepath
        super().__init__(message, details)


class TransformationError(ExtractionError):
    """轉換異常
    
    當數據轉換失敗時引發。
    
    Attributes:
        message: 錯誤信息
        field: 轉換失敗的字段
        details: 詳細信息字典
    """
    
    def __init__(self, message: str = "數據轉換失敗", field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, details)


class ScriptExecutionError(ExtractionError):
    """腳本執行異常
    
    當JavaScript腳本執行失敗時引發。
    
    Attributes:
        message: 錯誤信息
        script: 執行的腳本
        details: 詳細信息字典
    """
    
    def __init__(self, message: str = "JavaScript腳本執行失敗", script: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if script:
            details["script"] = script
        super().__init__(message, details)


class DataValidationError(ExtractionError):
    """數據驗證異常
    
    當數據驗證失敗時引發。
    
    Attributes:
        message: 錯誤信息
        validation_rule: 驗證規則
        details: 詳細信息字典
    """
    
    def __init__(self, message: str = "數據驗證失敗", validation_rule: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if validation_rule:
            details["validation_rule"] = validation_rule
        super().__init__(message, details)
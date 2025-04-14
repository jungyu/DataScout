#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置異常模組

提供以下異常類：
1. ConfigError: 基礎配置異常
2. ConfigLoadError: 配置加載異常
3. ConfigSaveError: 配置保存異常
4. ConfigValidationError: 配置驗證異常
"""

class ConfigError(Exception):
    """基礎配置異常"""
    def __init__(self, message: str, code: int = 2000):
        self.message = message
        self.code = code
        super().__init__(message)

class ConfigLoadError(ConfigError):
    """配置加載異常"""
    def __init__(self, message: str = "加載配置失敗", code: int = 2001):
        super().__init__(message, code)

class ConfigSaveError(ConfigError):
    """配置保存異常"""
    def __init__(self, message: str = "保存配置失敗", code: int = 2002):
        super().__init__(message, code)

class ConfigValidationError(ConfigError):
    """配置驗證異常"""
    def __init__(self, message: str = "配置驗證失敗", code: int = 2003):
        super().__init__(message, code) 
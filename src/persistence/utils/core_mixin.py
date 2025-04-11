#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
核心工具 Mixin 模組
提供核心工具類的統一初始化
"""

from src.core.utils import (
    ConfigUtils,
    Logger,
    PathUtils,
    DataProcessor,
    ErrorHandler,
    TimeUtils,
    ValidationUtils,
    SecurityUtils
)


class CoreMixin:
    """核心工具 Mixin 類"""
    
    def init_core_utils(self):
        """
        初始化核心工具類
        
        此方法應在子類的 __init__ 中調用
        """
        # 基礎工具
        self.config_utils = ConfigUtils()
        self.logger = Logger()
        self.path_utils = PathUtils()
        self.data_processor = DataProcessor()
        self.error_handler = ErrorHandler()
        
        # 額外工具
        self.time_utils = TimeUtils()
        self.validation_utils = ValidationUtils()
        self.security_utils = SecurityUtils()
        
    def log_info(self, message: str) -> None:
        """記錄信息日誌"""
        self.logger.info(message)
        
    def log_error(self, message: str) -> None:
        """記錄錯誤日誌"""
        self.logger.error(message)
        
    def log_warning(self, message: str) -> None:
        """記錄警告日誌"""
        self.logger.warning(message)
        
    def handle_error(self, error: Exception) -> None:
        """處理錯誤"""
        self.error_handler.handle_error(error)
        
    def validate_data(self, data: dict) -> bool:
        """驗證數據"""
        return self.validation_utils.validate_data(data)
        
    def process_data(self, data: dict) -> dict:
        """處理數據"""
        return self.data_processor.process_data(data)
        
    def get_path(self, path: str) -> str:
        """獲取路徑"""
        return self.path_utils.get_absolute_path(path)
        
    def get_timestamp(self) -> float:
        """獲取時間戳"""
        return self.time_utils.get_timestamp()
        
    def encrypt_data(self, data: str) -> str:
        """加密數據"""
        return self.security_utils.encrypt(data)
        
    def decrypt_data(self, data: str) -> str:
        """解密數據"""
        return self.security_utils.decrypt(data) 
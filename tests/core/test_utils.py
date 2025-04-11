#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
核心工具類測試
測試核心模組中的各種工具類
"""

import os
import sys
import pytest
from pathlib import Path
from datetime import datetime

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.core.utils.config_utils import ConfigUtils
from src.core.utils.logger import Logger
from src.core.utils.path_utils import PathUtils
from src.core.utils.data_processor import DataProcessor
from src.core.utils.error_handler import ErrorHandler
from src.core.utils.time_utils import TimeUtils
from src.core.utils.validation_utils import ValidationUtils
from src.core.utils.security_utils import SecurityUtils

class TestConfigUtils:
    """配置工具類測試"""
    
    def test_load_config(self):
        """測試加載配置"""
        config_utils = ConfigUtils()
        config = config_utils.load_config("test_config.json")
        assert isinstance(config, dict)
    
    def test_save_config(self):
        """測試保存配置"""
        config_utils = ConfigUtils()
        test_config = {"test": "value"}
        success = config_utils.save_config(test_config, "test_config.json")
        assert success is True

class TestLogger:
    """日誌工具類測試"""
    
    def test_log_info(self):
        """測試信息日誌"""
        logger = Logger()
        logger.info("測試信息")
        assert True
    
    def test_log_error(self):
        """測試錯誤日誌"""
        logger = Logger()
        logger.error("測試錯誤")
        assert True

class TestPathUtils:
    """路徑工具類測試"""
    
    def test_get_absolute_path(self):
        """測試獲取絕對路徑"""
        path_utils = PathUtils()
        path = path_utils.get_absolute_path("test.txt")
        assert isinstance(path, Path)
    
    def test_ensure_directory(self):
        """測試確保目錄存在"""
        path_utils = PathUtils()
        test_dir = Path("test_dir")
        path_utils.ensure_directory(test_dir)
        assert test_dir.exists()
        test_dir.rmdir()

class TestDataProcessor:
    """數據處理工具類測試"""
    
    def test_process_data(self):
        """測試數據處理"""
        data_processor = DataProcessor()
        test_data = {"key": "value"}
        processed_data = data_processor.process_data(test_data)
        assert isinstance(processed_data, dict)
    
    def test_validate_data(self):
        """測試數據驗證"""
        data_processor = DataProcessor()
        test_data = {"key": "value"}
        is_valid = data_processor.validate_data(test_data)
        assert is_valid is True

class TestErrorHandler:
    """錯誤處理工具類測試"""
    
    def test_handle_error(self):
        """測試錯誤處理"""
        error_handler = ErrorHandler()
        try:
            raise ValueError("測試錯誤")
        except Exception as e:
            error_handler.handle_error(e)
            assert True
    
    def test_log_error(self):
        """測試錯誤日誌"""
        error_handler = ErrorHandler()
        error_handler.log_error("測試錯誤")
        assert True

class TestTimeUtils:
    """時間工具類測試"""
    
    def test_get_timestamp(self):
        """測試獲取時間戳"""
        time_utils = TimeUtils()
        timestamp = time_utils.get_timestamp()
        assert isinstance(timestamp, str)
    
    def test_format_time(self):
        """測試格式化時間"""
        time_utils = TimeUtils()
        now = datetime.now()
        formatted_time = time_utils.format_time(now)
        assert isinstance(formatted_time, str)

class TestValidationUtils:
    """驗證工具類測試"""
    
    def test_validate_string(self):
        """測試字符串驗證"""
        validation_utils = ValidationUtils()
        is_valid = validation_utils.validate_string("test")
        assert is_valid is True
    
    def test_validate_number(self):
        """測試數字驗證"""
        validation_utils = ValidationUtils()
        is_valid = validation_utils.validate_number(123)
        assert is_valid is True

class TestSecurityUtils:
    """安全工具類測試"""
    
    def test_encrypt_data(self):
        """測試數據加密"""
        security_utils = SecurityUtils()
        test_data = "test"
        encrypted_data = security_utils.encrypt_data(test_data)
        assert isinstance(encrypted_data, str)
    
    def test_decrypt_data(self):
        """測試數據解密"""
        security_utils = SecurityUtils()
        test_data = "test"
        encrypted_data = security_utils.encrypt_data(test_data)
        decrypted_data = security_utils.decrypt_data(encrypted_data)
        assert decrypted_data == test_data 
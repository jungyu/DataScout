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
from datascout_core.core.utils import Utils

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.core.utils.config_utils import ConfigUtils
from src.core.utils.logger import Logger
from src.core.utils.path_utils import PathUtils
from src.core.utils.data_processor import SimpleDataProcessor
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
        data_processor = SimpleDataProcessor()
        test_data = {"key": "value"}
        processed_data = data_processor.process_data(test_data)
        assert isinstance(processed_data, dict)
    
    def test_validate_data(self):
        """測試數據驗證"""
        data_processor = SimpleDataProcessor()
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

@pytest.fixture
def test_data():
    """測試資料"""
    return {
        'string': 'test_string',
        'number': 123,
        'list': [1, 2, 3],
        'dict': {'key': 'value'}
    }

@pytest.fixture
def test_dir(tmp_path):
    """測試目錄"""
    return str(tmp_path)

def test_generate_id():
    """測試生成隨機ID"""
    # 測試預設長度
    id1 = Utils.generate_id()
    assert len(id1) == 8
    assert isinstance(id1, str)
    
    # 測試自訂長度
    id2 = Utils.generate_id(12)
    assert len(id2) == 12
    assert isinstance(id2, str)

def test_generate_timestamp():
    """測試生成時間戳"""
    timestamp = Utils.generate_timestamp()
    assert isinstance(timestamp, str)
    assert len(timestamp) == 15  # YYYYMMDD_HHMMSS

def test_calculate_md5():
    """測試計算MD5雜湊值"""
    # 測試字串
    md5_str = Utils.calculate_md5('test')
    assert isinstance(md5_str, str)
    assert len(md5_str) == 32
    
    # 測試位元組
    md5_bytes = Utils.calculate_md5(b'test')
    assert isinstance(md5_bytes, str)
    assert len(md5_bytes) == 32

def test_json_operations(test_data, test_dir):
    """測試JSON操作"""
    # 測試儲存JSON
    json_path = os.path.join(test_dir, 'test.json')
    Utils.save_json(test_data, json_path)
    assert os.path.exists(json_path)
    
    # 測試載入JSON
    loaded_data = Utils.load_json(json_path)
    assert loaded_data == test_data

def test_yaml_operations(test_data, test_dir):
    """測試YAML操作"""
    # 測試儲存YAML
    yaml_path = os.path.join(test_dir, 'test.yaml')
    Utils.save_yaml(test_data, yaml_path)
    assert os.path.exists(yaml_path)
    
    # 測試載入YAML
    loaded_data = Utils.load_yaml(yaml_path)
    assert loaded_data == test_data

def test_sleep():
    """測試睡眠功能"""
    import time
    start_time = time.time()
    Utils.sleep(0.1)
    end_time = time.time()
    assert end_time - start_time >= 0.1

def test_file_operations(test_dir):
    """測試檔案操作"""
    # 測試建立目錄
    test_subdir = os.path.join(test_dir, 'subdir')
    Utils.ensure_dir(test_subdir)
    assert os.path.exists(test_subdir)
    
    # 測試建立檔案
    test_file = os.path.join(test_subdir, 'test.txt')
    with open(test_file, 'w') as f:
        f.write('test')
    
    # 測試取得檔案大小
    file_size = Utils.get_file_size(test_file)
    assert file_size == 4
    
    # 測試列出檔案
    files = Utils.list_files(test_subdir)
    assert len(files) == 1
    assert files[0] == test_file
    
    # 測試列出特定模式檔案
    txt_files = Utils.list_files(test_subdir, '.txt')
    assert len(txt_files) == 1
    assert txt_files[0] == test_file
    
    # 測試刪除檔案
    Utils.delete_file(test_file)
    assert not os.path.exists(test_file)

def test_error_handling(test_dir):
    """測試錯誤處理"""
    # 測試載入不存在的JSON檔案
    with pytest.raises(Exception):
        Utils.load_json(os.path.join(test_dir, 'nonexistent.json'))
    
    # 測試載入不存在的YAML檔案
    with pytest.raises(Exception):
        Utils.load_yaml(os.path.join(test_dir, 'nonexistent.yaml'))
    
    # 測試取得不存在的檔案大小
    with pytest.raises(Exception):
        Utils.get_file_size(os.path.join(test_dir, 'nonexistent.txt'))
    
    # 測試列出不存在的目錄
    with pytest.raises(Exception):
        Utils.list_files(os.path.join(test_dir, 'nonexistent')) 
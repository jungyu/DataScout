"""
日誌記錄模組測試

測試日誌記錄類別的各項功能
"""

import os
import logging
import pytest
from selenium_base.core.logger import Logger
from selenium_base.core.exceptions import LoggerError

@pytest.fixture
def test_dir(tmp_path):
    """測試目錄"""
    return str(tmp_path)

@pytest.fixture
def logger(test_dir):
    """測試日誌記錄器"""
    return Logger('test', test_dir)

def test_init(test_dir):
    """測試初始化"""
    # 測試基本初始化
    logger = Logger('test', test_dir)
    assert logger.name == 'test'
    assert logger.log_dir == test_dir
    assert logger.level == 'INFO'
    assert isinstance(logger.logger, logging.Logger)
    
    # 測試自訂日誌等級
    logger = Logger('test', test_dir, 'DEBUG')
    assert logger.level == 'DEBUG'
    
    # 測試無效的日誌等級
    with pytest.raises(LoggerError):
        Logger('test', test_dir, 'INVALID')

def test_log_messages(logger, test_dir):
    """測試日誌訊息"""
    # 測試各種日誌等級
    logger.debug('Debug message')
    logger.info('Info message')
    logger.warning('Warning message')
    logger.error('Error message')
    logger.critical('Critical message')
    
    # 檢查日誌檔案是否存在
    log_file = os.path.join(test_dir, 'test.log')
    assert os.path.exists(log_file)
    
    # 檢查日誌檔案內容
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'Debug message' in content
        assert 'Info message' in content
        assert 'Warning message' in content
        assert 'Error message' in content
        assert 'Critical message' in content

def test_set_level(logger):
    """測試設定日誌等級"""
    # 測試設定有效等級
    logger.set_level('DEBUG')
    assert logger.get_level() == 'DEBUG'
    
    logger.set_level('INFO')
    assert logger.get_level() == 'INFO'
    
    # 測試設定無效等級
    with pytest.raises(LoggerError):
        logger.set_level('INVALID')

def test_add_file_handler(logger, test_dir):
    """測試添加檔案處理器"""
    # 測試添加檔案處理器
    logger.add_file_handler('test2.log')
    log_file = os.path.join(test_dir, 'test2.log')
    assert os.path.exists(log_file)
    
    # 測試添加特定等級的檔案處理器
    logger.add_file_handler('test3.log', 'ERROR')
    log_file = os.path.join(test_dir, 'test3.log')
    assert os.path.exists(log_file)
    
    # 測試添加無效等級的檔案處理器
    with pytest.raises(LoggerError):
        logger.add_file_handler('test4.log', 'INVALID')

def test_remove_handler(logger):
    """測試移除處理器"""
    # 測試移除處理器
    handler = logging.StreamHandler()
    logger.logger.addHandler(handler)
    logger.remove_handler(handler)
    assert handler not in logger.logger.handlers

def test_clear_handlers(logger):
    """測試清除處理器"""
    # 測試清除所有處理器
    logger.clear_handlers()
    assert len(logger.logger.handlers) == 0

def test_exception_logging(logger, test_dir):
    """測試異常日誌記錄"""
    try:
        raise ValueError('Test error')
    except Exception:
        logger.exception('Exception occurred')
    
    # 檢查日誌檔案內容
    log_file = os.path.join(test_dir, 'test.log')
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'Exception occurred' in content
        assert 'ValueError: Test error' in content
        assert 'Traceback' in content 
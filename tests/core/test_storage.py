"""
存儲模組測試

測試各種存儲類型的功能，包括：
1. 文件存儲（JSON、YAML、CSV）
2. SQLite 存儲
3. Redis 存儲
"""

import os
import json
import yaml
import csv
import sqlite3
import pytest
from unittest.mock import MagicMock, patch
from datascout_core.core.storage import (
    Storage,
    FileStorage,
    SqliteStorage,
    RedisStorage,
    StorageFactory
)
from datascout_core.core.exceptions import StorageError

@pytest.fixture
def base_config():
    """基本配置"""
    return {
        'test_key': 'test_value'
    }

@pytest.fixture
def temp_dir(tmp_path):
    """臨時目錄"""
    return tmp_path

@pytest.fixture
def json_file(temp_dir):
    """JSON 文件路徑"""
    return os.path.join(temp_dir, 'test.json')

@pytest.fixture
def yaml_file(temp_dir):
    """YAML 文件路徑"""
    return os.path.join(temp_dir, 'test.yaml')

@pytest.fixture
def csv_file(temp_dir):
    """CSV 文件路徑"""
    return os.path.join(temp_dir, 'test.csv')

@pytest.fixture
def sqlite_file(temp_dir):
    """SQLite 文件路徑"""
    return os.path.join(temp_dir, 'test.db')

def test_base_storage(base_config):
    """測試基類存儲"""
    storage = Storage(base_config)
    assert storage.config == base_config
    
    # 基類方法應該拋出 NotImplementedError
    with pytest.raises(NotImplementedError):
        storage.save({})
    
    with pytest.raises(NotImplementedError):
        storage.load()
    
    with pytest.raises(NotImplementedError):
        storage.delete()

def test_file_storage_json(base_config, json_file):
    """測試 JSON 文件存儲"""
    storage = FileStorage({
        **base_config,
        'path': json_file,
        'format': 'json'
    })
    
    # 測試保存
    data = {'key': 'value'}
    storage.save(data)
    assert os.path.exists(json_file)
    
    # 測試讀取
    loaded_data = storage.load()
    assert loaded_data == data
    
    # 測試刪除
    storage.delete()
    assert not os.path.exists(json_file)

def test_file_storage_yaml(base_config, yaml_file):
    """測試 YAML 文件存儲"""
    storage = FileStorage({
        **base_config,
        'path': yaml_file,
        'format': 'yaml'
    })
    
    # 測試保存
    data = {'key': 'value'}
    storage.save(data)
    assert os.path.exists(yaml_file)
    
    # 測試讀取
    loaded_data = storage.load()
    assert loaded_data == data
    
    # 測試刪除
    storage.delete()
    assert not os.path.exists(yaml_file)

def test_file_storage_csv(base_config, csv_file):
    """測試 CSV 文件存儲"""
    storage = FileStorage({
        **base_config,
        'path': csv_file,
        'format': 'csv'
    })
    
    # 測試保存列表
    data = [['header1', 'header2'], ['value1', 'value2']]
    storage.save(data)
    assert os.path.exists(csv_file)
    
    # 測試讀取
    loaded_data = storage.load()
    assert loaded_data == data
    
    # 測試保存單行
    data = ['value1', 'value2']
    storage.save(data)
    loaded_data = storage.load()
    assert loaded_data == [data]
    
    # 測試刪除
    storage.delete()
    assert not os.path.exists(csv_file)

def test_file_storage_error(base_config, json_file):
    """測試文件存儲錯誤"""
    storage = FileStorage({
        **base_config,
        'path': json_file,
        'format': 'invalid'
    })
    
    # 測試不支持的格式
    with pytest.raises(StorageError) as exc_info:
        storage.save({'key': 'value'})
    
    assert '不支持的文件格式' in str(exc_info.value)
    
    # 測試讀取不存在的文件
    assert storage.load() is None

def test_sqlite_storage(base_config, sqlite_file):
    """測試 SQLite 存儲"""
    storage = SqliteStorage({
        **base_config,
        'path': sqlite_file,
        'table': 'test_table',
        'schema': '(id INTEGER PRIMARY KEY, name TEXT, value TEXT)'
    })
    
    # 測試保存單條數據
    data = {'id': 1, 'name': 'test', 'value': 'value'}
    storage.save(data)
    
    # 測試保存多條數據
    data_list = [
        {'id': 2, 'name': 'test2', 'value': 'value2'},
        {'id': 3, 'name': 'test3', 'value': 'value3'}
    ]
    storage.save(data_list)
    
    # 測試讀取所有數據
    loaded_data = storage.load()
    assert len(loaded_data) == 3
    
    # 測試條件查詢
    loaded_data = storage.load(
        where='name = ?',
        params=['test2']
    )
    assert len(loaded_data) == 1
    assert loaded_data[0]['name'] == 'test2'
    
    # 測試排序和限制
    loaded_data = storage.load(
        order_by='id DESC',
        limit=2
    )
    assert len(loaded_data) == 2
    assert loaded_data[0]['id'] == 3
    
    # 測試刪除
    storage.delete(where='id = ?', params=[1])
    loaded_data = storage.load()
    assert len(loaded_data) == 2

def test_sqlite_storage_error(base_config, sqlite_file):
    """測試 SQLite 存儲錯誤"""
    storage = SqliteStorage({
        **base_config,
        'path': sqlite_file,
        'table': 'test_table'
    })
    
    # 測試無效的 SQL
    with pytest.raises(StorageError) as exc_info:
        storage.load(where='invalid sql')
    
    assert '讀取數據錯誤' in str(exc_info.value)

@patch('redis.Redis')
def test_redis_storage(mock_redis, base_config):
    """測試 Redis 存儲"""
    mock_client = MagicMock()
    mock_redis.return_value = mock_client
    
    storage = RedisStorage({
        **base_config,
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'prefix': 'test'
    })
    
    # 測試保存
    data = {'key': 'value'}
    storage.save(data, 'test_key')
    mock_client.set.assert_called_once()
    
    # 測試設置過期時間
    storage.save(data, 'test_key', expire=3600)
    mock_client.expire.assert_called_once()
    
    # 測試讀取
    mock_client.get.return_value = json.dumps(data)
    loaded_data = storage.load('test_key')
    assert loaded_data == data
    
    # 測試讀取不存在的鍵
    mock_client.get.return_value = None
    assert storage.load('nonexistent') is None
    
    # 測試刪除
    storage.delete('test_key')
    mock_client.delete.assert_called_once()

@patch('redis.Redis')
def test_redis_storage_error(mock_redis, base_config):
    """測試 Redis 存儲錯誤"""
    mock_client = MagicMock()
    mock_redis.return_value = mock_client
    
    storage = RedisStorage(base_config)
    
    # 測試連接錯誤
    mock_client.set.side_effect = Exception('Redis error')
    
    with pytest.raises(StorageError) as exc_info:
        storage.save({'key': 'value'}, 'test_key')
    
    assert '保存數據錯誤' in str(exc_info.value)

def test_storage_factory(base_config):
    """測試存儲工廠"""
    # 測試文件存儲
    storage = StorageFactory.create('file', {
        **base_config,
        'path': 'test.json'
    })
    assert isinstance(storage, FileStorage)
    
    # 測試 SQLite 存儲
    storage = StorageFactory.create('sqlite', {
        **base_config,
        'path': 'test.db',
        'table': 'test_table'
    })
    assert isinstance(storage, SqliteStorage)
    
    # 測試 Redis 存儲
    storage = StorageFactory.create('redis', base_config)
    assert isinstance(storage, RedisStorage)
    
    # 測試不支持的類型
    with pytest.raises(StorageError) as exc_info:
        StorageFactory.create('unsupported', base_config)
    
    assert '不支持的存儲類型' in str(exc_info.value) 
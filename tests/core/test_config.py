"""
配置管理模組測試

測試配置管理類別的各項功能
"""

import os
import pytest
from datascout_core.core.config import Config
from datascout_core.core.exceptions import ConfigError

@pytest.fixture
def test_config():
    """測試配置"""
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

def test_init():
    """測試初始化"""
    # 測試無配置檔案
    config = Config()
    assert config.config_data == {}
    
    # 測試無效的配置檔案路徑
    with pytest.raises(ConfigError):
        Config('nonexistent.json')
    
    # 測試不支援的檔案格式
    with pytest.raises(ConfigError):
        Config('test.txt')

def test_json_operations(test_config, test_dir):
    """測試JSON操作"""
    # 建立測試配置檔案
    json_path = os.path.join(test_dir, 'test.json')
    config = Config()
    config.config_data = test_config
    config.save(json_path)
    
    # 測試載入JSON配置
    loaded_config = Config(json_path)
    assert loaded_config.config_data == test_config

def test_yaml_operations(test_config, test_dir):
    """測試YAML操作"""
    # 建立測試配置檔案
    yaml_path = os.path.join(test_dir, 'test.yaml')
    config = Config()
    config.config_data = test_config
    config.save(yaml_path)
    
    # 測試載入YAML配置
    loaded_config = Config(yaml_path)
    assert loaded_config.config_data == test_config

def test_get_set(test_config):
    """測試取得和設定配置"""
    config = Config()
    
    # 測試設定配置
    for key, value in test_config.items():
        config.set(key, value)
    
    # 測試取得配置
    for key, value in test_config.items():
        assert config.get(key) == value
    
    # 測試取得不存在的配置
    assert config.get('nonexistent') is None
    assert config.get('nonexistent', 'default') == 'default'

def test_update(test_config):
    """測試更新配置"""
    config = Config()
    
    # 測試更新配置
    config.update(test_config)
    assert config.config_data == test_config
    
    # 測試更新部分配置
    new_config = {'new_key': 'new_value'}
    config.update(new_config)
    assert config.get('new_key') == 'new_value'
    assert config.get('string') == 'test_string'

def test_validate(test_config):
    """測試驗證配置"""
    config = Config()
    config.config_data = test_config
    
    # 測試驗證成功
    schema = {
        'string': str,
        'number': int,
        'list': list,
        'dict': dict
    }
    assert config.validate(schema) is True
    
    # 測試驗證失敗 - 缺少必要配置
    schema['new_key'] = str
    with pytest.raises(ConfigError):
        config.validate(schema)
    
    # 測試驗證失敗 - 配置類型錯誤
    config.set('number', '123')
    with pytest.raises(ConfigError):
        config.validate(schema)

def test_merge(test_config):
    """測試合併配置"""
    config1 = Config()
    config1.config_data = test_config
    
    config2 = Config()
    config2.config_data = {'new_key': 'new_value'}
    
    # 測試合併配置
    config1.merge(config2)
    assert config1.get('new_key') == 'new_value'
    assert config1.get('string') == 'test_string'

def test_clear(test_config):
    """測試清除配置"""
    config = Config()
    config.config_data = test_config
    
    # 測試清除配置
    config.clear()
    assert config.config_data == {}

def test_special_methods(test_config):
    """測試特殊方法"""
    config = Config()
    config.config_data = test_config
    
    # 測試 __getitem__
    assert config['string'] == 'test_string'
    
    # 測試 __setitem__
    config['new_key'] = 'new_value'
    assert config.get('new_key') == 'new_value'
    
    # 測試 __contains__
    assert 'string' in config
    assert 'nonexistent' not in config
    
    # 測試 __len__
    assert len(config) == len(test_config) + 1
    
    # 測試 __iter__
    keys = list(config)
    assert 'string' in keys
    assert 'new_key' in keys 
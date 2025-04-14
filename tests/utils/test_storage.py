"""
儲存工具測試模組

此模組提供了儲存工具的測試案例，包含以下功能：
- 資料儲存測試
- 資料壓縮測試
- 結果管理測試
- 錯誤處理測試
"""

import os
import json
import gzip
import pytest
from unittest.mock import MagicMock, patch

from datascout_core.core.config import BaseConfig
from datascout_core.utils.storage import StorageUtils

@pytest.fixture
def config():
    """建立測試用的配置物件"""
    config = BaseConfig()
    config.storage.result_dir = "test_results"
    config.storage.compress = True
    return config

@pytest.fixture
def utils():
    """建立測試用的儲存工具"""
    return StorageUtils()

@pytest.fixture
def test_data():
    """建立測試用的資料"""
    return {
        "id": 1,
        "name": "test",
        "data": [1, 2, 3]
    }

def test_save_json(utils, config, test_data, tmp_path):
    """測試儲存 JSON 資料"""
    # 設定測試目錄
    config.storage.result_dir = str(tmp_path)
    
    # 儲存資料
    file_path = utils.save_json(test_data, "test.json", config)
    
    # 檢查檔案是否已建立
    assert os.path.exists(file_path)
    
    # 檢查檔案內容
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data == test_data

def test_load_json(utils, config, test_data, tmp_path):
    """測試載入 JSON 資料"""
    # 設定測試目錄
    config.storage.result_dir = str(tmp_path)
    
    # 儲存資料
    file_path = utils.save_json(test_data, "test.json", config)
    
    # 載入資料
    data = utils.load_json(file_path)
    
    # 檢查資料內容
    assert data == test_data

def test_save_text(utils, config, tmp_path):
    """測試儲存文字資料"""
    # 設定測試目錄
    config.storage.result_dir = str(tmp_path)
    
    # 儲存資料
    file_path = utils.save_text("test data", "test.txt", config)
    
    # 檢查檔案是否已建立
    assert os.path.exists(file_path)
    
    # 檢查檔案內容
    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read()
        assert data == "test data"

def test_load_text(utils, config, tmp_path):
    """測試載入文字資料"""
    # 設定測試目錄
    config.storage.result_dir = str(tmp_path)
    
    # 儲存資料
    file_path = utils.save_text("test data", "test.txt", config)
    
    # 載入資料
    data = utils.load_text(file_path)
    
    # 檢查資料內容
    assert data == "test data"

def test_save_binary(utils, config, tmp_path):
    """測試儲存二進制資料"""
    # 設定測試目錄
    config.storage.result_dir = str(tmp_path)
    
    # 儲存資料
    file_path = utils.save_binary(b"test data", "test.bin", config)
    
    # 檢查檔案是否已建立
    assert os.path.exists(file_path)
    
    # 檢查檔案內容
    with open(file_path, "rb") as f:
        data = f.read()
        assert data == b"test data"

def test_load_binary(utils, config, tmp_path):
    """測試載入二進制資料"""
    # 設定測試目錄
    config.storage.result_dir = str(tmp_path)
    
    # 儲存資料
    file_path = utils.save_binary(b"test data", "test.bin", config)
    
    # 載入資料
    data = utils.load_binary(file_path)
    
    # 檢查資料內容
    assert data == b"test data"

def test_save_file(utils, config, tmp_path):
    """測試儲存檔案"""
    # 設定測試目錄
    config.storage.result_dir = str(tmp_path)
    
    # 建立測試檔案
    source_path = tmp_path / "source.txt"
    with open(source_path, "w", encoding="utf-8") as f:
        f.write("test data")
    
    # 儲存檔案
    file_path = utils.save_file(str(source_path), "test.txt", config)
    
    # 檢查檔案是否已建立
    assert os.path.exists(file_path)
    
    # 檢查檔案內容
    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read()
        assert data == "test data"

def test_load_file(utils, config, tmp_path):
    """測試載入檔案"""
    # 設定測試目錄
    config.storage.result_dir = str(tmp_path)
    
    # 建立測試檔案
    source_path = tmp_path / "source.txt"
    with open(source_path, "w", encoding="utf-8") as f:
        f.write("test data")
    
    # 儲存檔案
    file_path = utils.save_file(str(source_path), "test.txt", config)
    
    # 載入檔案
    target_path = utils.load_file(file_path, "target.txt")
    
    # 檢查檔案是否已建立
    assert os.path.exists(target_path)
    
    # 檢查檔案內容
    with open(target_path, "r", encoding="utf-8") as f:
        data = f.read()
        assert data == "test data"

def test_compress_data(utils, test_data):
    """測試壓縮資料"""
    # 壓縮資料
    compressed_data = utils._compress_data(json.dumps(test_data))
    
    # 檢查壓縮資料
    assert isinstance(compressed_data, bytes)
    
    # 解壓縮資料
    decompressed_data = gzip.decompress(compressed_data)
    
    # 檢查解壓縮資料
    assert json.loads(decompressed_data) == test_data

def test_decompress_data(utils, test_data):
    """測試解壓縮資料"""
    # 壓縮資料
    compressed_data = gzip.compress(json.dumps(test_data).encode())
    
    # 解壓縮資料
    decompressed_data = utils._decompress_data(compressed_data)
    
    # 檢查解壓縮資料
    assert json.loads(decompressed_data) == test_data

def test_save_result(utils, config, test_data, tmp_path):
    """測試儲存爬蟲結果"""
    # 設定測試目錄
    config.storage.result_dir = str(tmp_path)
    
    # 儲存結果
    file_path = utils.save_result(test_data, "test.json", config)
    
    # 檢查檔案是否已建立
    assert os.path.exists(file_path)
    
    # 檢查檔案內容
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data == test_data

def test_get_result_files(utils, config, tmp_path):
    """測試取得結果檔案列表"""
    # 設定測試目錄
    config.storage.result_dir = str(tmp_path)
    
    # 建立測試檔案
    for i in range(3):
        utils.save_json({"id": i}, f"test_{i}.json", config)
    
    # 取得檔案列表
    files = utils.get_result_files(config)
    
    # 檢查檔案列表
    assert len(files) == 3
    assert all(f.endswith(".json") for f in files)

def test_delete_result(utils, config, tmp_path):
    """測試刪除結果檔案"""
    # 設定測試目錄
    config.storage.result_dir = str(tmp_path)
    
    # 建立測試檔案
    file_path = utils.save_json({"id": 1}, "test.json", config)
    
    # 刪除檔案
    utils.delete_result(file_path)
    
    # 檢查檔案是否已刪除
    assert not os.path.exists(file_path)

def test_clear_results(utils, config, tmp_path):
    """測試清空結果目錄"""
    # 設定測試目錄
    config.storage.result_dir = str(tmp_path)
    
    # 建立測試檔案
    for i in range(3):
        utils.save_json({"id": i}, f"test_{i}.json", config)
    
    # 清空目錄
    utils.clear_results(config)
    
    # 檢查目錄是否已清空
    assert len(os.listdir(tmp_path)) == 0

def test_save_json_error(utils, config):
    """測試儲存 JSON 資料錯誤"""
    # 設定無效的資料
    invalid_data = MagicMock()
    invalid_data.__dict__ = {"__dict__": MagicMock()}
    
    # 檢查錯誤
    with pytest.raises(Exception) as exc_info:
        utils.save_json(invalid_data, "test.json", config)
    
    # 檢查錯誤訊息
    assert "Failed to save JSON data" in str(exc_info.value)

def test_load_json_error(utils):
    """測試載入 JSON 資料錯誤"""
    # 設定無效的檔案路徑
    invalid_path = "invalid.json"
    
    # 檢查錯誤
    with pytest.raises(Exception) as exc_info:
        utils.load_json(invalid_path)
    
    # 檢查錯誤訊息
    assert "Failed to load JSON data" in str(exc_info.value)

def test_compress_data_error(utils):
    """測試壓縮資料錯誤"""
    # 設定無效的資料
    invalid_data = MagicMock()
    
    # 檢查錯誤
    with pytest.raises(Exception) as exc_info:
        utils._compress_data(invalid_data)
    
    # 檢查錯誤訊息
    assert "Failed to compress data" in str(exc_info.value)

def test_decompress_data_error(utils):
    """測試解壓縮資料錯誤"""
    # 設定無效的資料
    invalid_data = b"invalid"
    
    # 檢查錯誤
    with pytest.raises(Exception) as exc_info:
        utils._decompress_data(invalid_data)
    
    # 檢查錯誤訊息
    assert "Failed to decompress data" in str(exc_info.value) 
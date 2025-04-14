"""
爬蟲核心測試模組

此模組提供了爬蟲核心的測試案例，包含以下功能：
- 爬蟲初始化測試
- 爬蟲執行測試
- 爬蟲暫停測試
- 爬蟲恢復測試
- 爬蟲停止測試
- 爬蟲狀態測試
- 爬蟲結果測試
- 爬蟲錯誤測試
"""

import time
import pytest
from unittest.mock import MagicMock, patch

from selenium_base.core.config import BaseConfig
from selenium_base.core.crawler import Crawler
from selenium_base.core.exceptions import CrawlerError

@pytest.fixture
def config():
    """建立測試用的配置物件"""
    config = BaseConfig()
    config.browser.headless = True
    config.browser.user_agent = "test"
    config.browser.language = "zh-TW"
    config.browser.timezone = "Asia/Taipei"
    config.browser.geolocation = {"latitude": 25.0330, "longitude": 121.5654}
    config.browser.proxy = None
    config.browser.extensions = []
    config.request.retry_count = 3
    config.request.retry_delay = 1
    config.request.retry_backoff = 2
    config.request.retry_statuses = [500, 502, 503, 504]
    config.request.rate_limit_minute = 60
    config.request.rate_limit_hour = 1000
    config.request.rate_limit_day = 10000
    config.storage.result_dir = "test_results"
    config.storage.compress = True
    return config

@pytest.fixture
def crawler(config):
    """建立測試用的爬蟲"""
    return Crawler(config)

@pytest.fixture
def mock_browser():
    """建立測試用的瀏覽器"""
    browser = MagicMock()
    browser.current_url = "http://example.com"
    browser.page_source = "<html><body>test</body></html>"
    browser.execute_script.return_value = None
    browser.find_element.return_value = MagicMock()
    browser.find_elements.return_value = [MagicMock()]
    return browser

@pytest.fixture
def mock_request():
    """建立測試用的請求"""
    request = MagicMock()
    request.get.return_value = MagicMock(status_code=200, text="test")
    request.post.return_value = MagicMock(status_code=200, text="test")
    request.put.return_value = MagicMock(status_code=200, text="test")
    request.delete.return_value = MagicMock(status_code=200, text="test")
    request.head.return_value = MagicMock(status_code=200)
    request.options.return_value = MagicMock(status_code=200)
    request.patch.return_value = MagicMock(status_code=200, text="test")
    return request

@pytest.fixture
def mock_storage():
    """建立測試用的儲存"""
    storage = MagicMock()
    storage.save_json.return_value = "test.json"
    storage.save_text.return_value = "test.txt"
    storage.save_binary.return_value = "test.bin"
    storage.save_file.return_value = "test.txt"
    storage.save_result.return_value = "test.json"
    storage.get_result_files.return_value = ["test.json"]
    return storage

def test_init(crawler, config):
    """測試爬蟲初始化"""
    # 檢查配置
    assert crawler.config == config
    
    # 檢查狀態
    assert crawler.is_running is False
    assert crawler.is_paused is False
    assert crawler.is_stopped is False
    
    # 檢查結果
    assert crawler.results == []

def test_start(crawler, mock_browser, mock_request, mock_storage):
    """測試爬蟲啟動"""
    # 設定模擬物件
    with patch("selenium_base.core.crawler.BrowserProfile") as mock_profile:
        with patch("selenium_base.core.crawler.RequestController") as mock_controller:
            with patch("selenium_base.core.crawler.StorageUtils") as mock_storage_utils:
                # 設定模擬物件回傳值
                mock_profile.return_value.create_driver.return_value = mock_browser
                mock_controller.return_value.create_session.return_value = mock_request
                mock_storage_utils.return_value = mock_storage
                
                # 啟動爬蟲
                crawler.start()
                
                # 檢查狀態
                assert crawler.is_running is True
                assert crawler.is_paused is False
                assert crawler.is_stopped is False
                
                # 檢查模擬物件是否被呼叫
                mock_profile.return_value.create_driver.assert_called_once()
                mock_controller.return_value.create_session.assert_called_once()
                mock_storage_utils.assert_called_once()

def test_pause(crawler):
    """測試爬蟲暫停"""
    # 設定狀態
    crawler.is_running = True
    crawler.is_paused = False
    crawler.is_stopped = False
    
    # 暫停爬蟲
    crawler.pause()
    
    # 檢查狀態
    assert crawler.is_running is True
    assert crawler.is_paused is True
    assert crawler.is_stopped is False

def test_resume(crawler):
    """測試爬蟲恢復"""
    # 設定狀態
    crawler.is_running = True
    crawler.is_paused = True
    crawler.is_stopped = False
    
    # 恢復爬蟲
    crawler.resume()
    
    # 檢查狀態
    assert crawler.is_running is True
    assert crawler.is_paused is False
    assert crawler.is_stopped is False

def test_stop(crawler, mock_browser, mock_request):
    """測試爬蟲停止"""
    # 設定模擬物件
    crawler.browser = mock_browser
    crawler.request = mock_request
    
    # 設定狀態
    crawler.is_running = True
    crawler.is_paused = False
    crawler.is_stopped = False
    
    # 停止爬蟲
    crawler.stop()
    
    # 檢查狀態
    assert crawler.is_running is False
    assert crawler.is_paused is False
    assert crawler.is_stopped is True
    
    # 檢查模擬物件是否被呼叫
    mock_browser.quit.assert_called_once()
    mock_request.close.assert_called_once()

def test_get_status(crawler):
    """測試取得爬蟲狀態"""
    # 設定狀態
    crawler.is_running = True
    crawler.is_paused = True
    crawler.is_stopped = False
    
    # 取得狀態
    status = crawler.get_status()
    
    # 檢查狀態
    assert status["is_running"] is True
    assert status["is_paused"] is True
    assert status["is_stopped"] is False
    assert status["result_count"] == 0

def test_add_result(crawler, mock_storage):
    """測試新增爬蟲結果"""
    # 設定模擬物件
    crawler.storage = mock_storage
    
    # 設定結果
    result = {"id": 1, "name": "test"}
    
    # 新增結果
    crawler.add_result(result)
    
    # 檢查結果
    assert len(crawler.results) == 1
    assert crawler.results[0] == result
    
    # 檢查模擬物件是否被呼叫
    mock_storage.save_result.assert_called_once_with(result, "result_1.json", crawler.config)

def test_get_results(crawler, mock_storage):
    """測試取得爬蟲結果"""
    # 設定模擬物件
    crawler.storage = mock_storage
    
    # 設定結果
    crawler.results = [{"id": 1, "name": "test"}]
    
    # 取得結果
    results = crawler.get_results()
    
    # 檢查結果
    assert len(results) == 1
    assert results[0] == {"id": 1, "name": "test"}

def test_clear_results(crawler, mock_storage):
    """測試清空爬蟲結果"""
    # 設定模擬物件
    crawler.storage = mock_storage
    
    # 設定結果
    crawler.results = [{"id": 1, "name": "test"}]
    
    # 清空結果
    crawler.clear_results()
    
    # 檢查結果
    assert len(crawler.results) == 0
    
    # 檢查模擬物件是否被呼叫
    mock_storage.clear_results.assert_called_once_with(crawler.config)

def test_start_error(crawler):
    """測試爬蟲啟動錯誤"""
    # 設定模擬物件
    with patch("selenium_base.core.crawler.BrowserProfile") as mock_profile:
        # 設定模擬物件回傳值
        mock_profile.return_value.create_driver.side_effect = Exception("test")
        
        # 檢查錯誤
        with pytest.raises(CrawlerError) as exc_info:
            crawler.start()
        
        # 檢查錯誤訊息
        assert "Failed to start crawler" in str(exc_info.value)

def test_stop_error(crawler, mock_browser, mock_request):
    """測試爬蟲停止錯誤"""
    # 設定模擬物件
    crawler.browser = mock_browser
    crawler.request = mock_request
    
    # 設定模擬物件回傳值
    mock_browser.quit.side_effect = Exception("test")
    
    # 檢查錯誤
    with pytest.raises(CrawlerError) as exc_info:
        crawler.stop()
    
    # 檢查錯誤訊息
    assert "Failed to stop crawler" in str(exc_info.value)

def test_add_result_error(crawler, mock_storage):
    """測試新增爬蟲結果錯誤"""
    # 設定模擬物件
    crawler.storage = mock_storage
    
    # 設定模擬物件回傳值
    mock_storage.save_result.side_effect = Exception("test")
    
    # 檢查錯誤
    with pytest.raises(CrawlerError) as exc_info:
        crawler.add_result({"id": 1, "name": "test"})
    
    # 檢查錯誤訊息
    assert "Failed to add result" in str(exc_info.value)

def test_clear_results_error(crawler, mock_storage):
    """測試清空爬蟲結果錯誤"""
    # 設定模擬物件
    crawler.storage = mock_storage
    
    # 設定模擬物件回傳值
    mock_storage.clear_results.side_effect = Exception("test")
    
    # 檢查錯誤
    with pytest.raises(CrawlerError) as exc_info:
        crawler.clear_results()
    
    # 檢查錯誤訊息
    assert "Failed to clear results" in str(exc_info.value) 
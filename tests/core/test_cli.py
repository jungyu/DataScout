"""
命令列介面測試模組

此模組提供了命令列介面的測試案例，包含以下功能：
- 命令列初始化測試
- 命令列執行測試
- 命令列參數測試
- 命令列錯誤測試
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

from selenium_base.core.config import BaseConfig
from selenium_base.core.cli import CLI
from selenium_base.core.exceptions import CLIError

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
def cli(config):
    """建立測試用的命令列介面"""
    return CLI(config)

@pytest.fixture
def mock_crawler():
    """建立測試用的爬蟲"""
    crawler = MagicMock()
    crawler.is_running = False
    crawler.is_paused = False
    crawler.is_stopped = False
    crawler.results = []
    crawler.get_status.return_value = {
        "is_running": False,
        "is_paused": False,
        "is_stopped": False,
        "result_count": 0
    }
    return crawler

def test_init(cli, config):
    """測試命令列介面初始化"""
    # 檢查配置
    assert cli.config == config
    
    # 檢查爬蟲
    assert cli.crawler is None

def test_start(cli, mock_crawler):
    """測試啟動爬蟲"""
    # 設定模擬物件
    with patch("selenium_base.core.cli.Crawler") as mock_crawler_class:
        with patch("selenium_base.core.cli.argparse.ArgumentParser") as mock_parser:
            # 設定模擬物件回傳值
            mock_crawler_class.return_value = mock_crawler
            mock_parser.return_value.parse_args.return_value = MagicMock(command="start")
            
            # 啟動爬蟲
            cli.start()
            
            # 檢查爬蟲
            assert cli.crawler == mock_crawler
            
            # 檢查模擬物件是否被呼叫
            mock_crawler_class.assert_called_once_with(cli.config)
            mock_crawler.start.assert_called_once()

def test_stop(cli, mock_crawler):
    """測試停止爬蟲"""
    # 設定爬蟲
    cli.crawler = mock_crawler
    
    # 停止爬蟲
    cli.stop()
    
    # 檢查模擬物件是否被呼叫
    mock_crawler.stop.assert_called_once()

def test_pause(cli, mock_crawler):
    """測試暫停爬蟲"""
    # 設定爬蟲
    cli.crawler = mock_crawler
    
    # 暫停爬蟲
    cli.pause()
    
    # 檢查模擬物件是否被呼叫
    mock_crawler.pause.assert_called_once()

def test_resume(cli, mock_crawler):
    """測試恢復爬蟲"""
    # 設定爬蟲
    cli.crawler = mock_crawler
    
    # 恢復爬蟲
    cli.resume()
    
    # 檢查模擬物件是否被呼叫
    mock_crawler.resume.assert_called_once()

def test_status(cli, mock_crawler):
    """測試取得爬蟲狀態"""
    # 設定爬蟲
    cli.crawler = mock_crawler
    
    # 取得狀態
    status = cli.status()
    
    # 檢查狀態
    assert status == {
        "is_running": False,
        "is_paused": False,
        "is_stopped": False,
        "result_count": 0
    }
    
    # 檢查模擬物件是否被呼叫
    mock_crawler.get_status.assert_called_once()

def test_results(cli, mock_crawler):
    """測試取得爬蟲結果"""
    # 設定爬蟲
    cli.crawler = mock_crawler
    mock_crawler.get_results.return_value = [{"id": 1, "name": "test"}]
    
    # 取得結果
    results = cli.results()
    
    # 檢查結果
    assert results == [{"id": 1, "name": "test"}]
    
    # 檢查模擬物件是否被呼叫
    mock_crawler.get_results.assert_called_once()

def test_clear(cli, mock_crawler):
    """測試清空爬蟲結果"""
    # 設定爬蟲
    cli.crawler = mock_crawler
    
    # 清空結果
    cli.clear()
    
    # 檢查模擬物件是否被呼叫
    mock_crawler.clear_results.assert_called_once()

def test_run(cli, mock_crawler):
    """測試執行命令列介面"""
    # 設定模擬物件
    with patch("selenium_base.core.cli.Crawler") as mock_crawler_class:
        with patch("selenium_base.core.cli.argparse.ArgumentParser") as mock_parser:
            # 設定模擬物件回傳值
            mock_crawler_class.return_value = mock_crawler
            mock_parser.return_value.parse_args.return_value = MagicMock(command="start")
            
            # 執行命令列介面
            cli.run()
            
            # 檢查模擬物件是否被呼叫
            mock_crawler_class.assert_called_once_with(cli.config)
            mock_crawler.start.assert_called_once()

def test_start_error(cli):
    """測試啟動爬蟲錯誤"""
    # 設定模擬物件
    with patch("selenium_base.core.cli.Crawler") as mock_crawler_class:
        # 設定模擬物件回傳值
        mock_crawler_class.return_value.start.side_effect = Exception("test")
        
        # 檢查錯誤
        with pytest.raises(CLIError) as exc_info:
            cli.start()
        
        # 檢查錯誤訊息
        assert "Failed to start crawler" in str(exc_info.value)

def test_stop_error(cli, mock_crawler):
    """測試停止爬蟲錯誤"""
    # 設定爬蟲
    cli.crawler = mock_crawler
    
    # 設定模擬物件回傳值
    mock_crawler.stop.side_effect = Exception("test")
    
    # 檢查錯誤
    with pytest.raises(CLIError) as exc_info:
        cli.stop()
    
    # 檢查錯誤訊息
    assert "Failed to stop crawler" in str(exc_info.value)

def test_pause_error(cli, mock_crawler):
    """測試暫停爬蟲錯誤"""
    # 設定爬蟲
    cli.crawler = mock_crawler
    
    # 設定模擬物件回傳值
    mock_crawler.pause.side_effect = Exception("test")
    
    # 檢查錯誤
    with pytest.raises(CLIError) as exc_info:
        cli.pause()
    
    # 檢查錯誤訊息
    assert "Failed to pause crawler" in str(exc_info.value)

def test_resume_error(cli, mock_crawler):
    """測試恢復爬蟲錯誤"""
    # 設定爬蟲
    cli.crawler = mock_crawler
    
    # 設定模擬物件回傳值
    mock_crawler.resume.side_effect = Exception("test")
    
    # 檢查錯誤
    with pytest.raises(CLIError) as exc_info:
        cli.resume()
    
    # 檢查錯誤訊息
    assert "Failed to resume crawler" in str(exc_info.value)

def test_status_error(cli, mock_crawler):
    """測試取得爬蟲狀態錯誤"""
    # 設定爬蟲
    cli.crawler = mock_crawler
    
    # 設定模擬物件回傳值
    mock_crawler.get_status.side_effect = Exception("test")
    
    # 檢查錯誤
    with pytest.raises(CLIError) as exc_info:
        cli.status()
    
    # 檢查錯誤訊息
    assert "Failed to get crawler status" in str(exc_info.value)

def test_results_error(cli, mock_crawler):
    """測試取得爬蟲結果錯誤"""
    # 設定爬蟲
    cli.crawler = mock_crawler
    
    # 設定模擬物件回傳值
    mock_crawler.get_results.side_effect = Exception("test")
    
    # 檢查錯誤
    with pytest.raises(CLIError) as exc_info:
        cli.results()
    
    # 檢查錯誤訊息
    assert "Failed to get crawler results" in str(exc_info.value)

def test_clear_error(cli, mock_crawler):
    """測試清空爬蟲結果錯誤"""
    # 設定爬蟲
    cli.crawler = mock_crawler
    
    # 設定模擬物件回傳值
    mock_crawler.clear_results.side_effect = Exception("test")
    
    # 檢查錯誤
    with pytest.raises(CLIError) as exc_info:
        cli.clear()
    
    # 檢查錯誤訊息
    assert "Failed to clear crawler results" in str(exc_info.value)

def test_run_error(cli):
    """測試執行命令列介面錯誤"""
    # 設定模擬物件
    with patch("selenium_base.core.cli.argparse.ArgumentParser") as mock_parser:
        # 設定模擬物件回傳值
        mock_parser.return_value.parse_args.side_effect = Exception("test")
        
        # 檢查錯誤
        with pytest.raises(CLIError) as exc_info:
            cli.run()
        
        # 檢查錯誤訊息
        assert "Failed to run CLI" in str(exc_info.value) 
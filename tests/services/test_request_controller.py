"""
請求控制服務測試模組

此模組提供了請求控制服務的測試案例，包含以下功能：
- 請求控制測試
- 請求重試測試
- 請求限制測試
- 請求記錄測試
"""

import time
import pytest
from unittest.mock import MagicMock, patch

from requests import Response, Session
from requests.exceptions import RequestException

from selenium_base.core.config import BaseConfig
from selenium_base.services.request_controller import RequestController

@pytest.fixture
def config():
    """建立測試用的配置物件"""
    config = BaseConfig()
    config.request.retry_count = 3
    config.request.retry_delay = 1
    config.request.retry_backoff = 2
    config.request.retry_statuses = [500, 502, 503, 504]
    config.request.rate_limit_minute = 60
    config.request.rate_limit_hour = 1000
    config.request.rate_limit_day = 10000
    return config

@pytest.fixture
def controller(config):
    """建立測試用的請求控制服務"""
    return RequestController(config)

@pytest.fixture
def session():
    """建立測試用的請求會話"""
    return MagicMock(spec=Session)

def test_create_session(controller):
    """測試建立請求會話"""
    session = controller.create_session()
    
    # 檢查會話類型
    assert isinstance(session, Session)
    
    # 檢查重試設定
    assert session.adapters["http://"].max_retries.total == 3
    assert session.adapters["https://"].max_retries.total == 3

def test_check_rate_limit_minute(controller):
    """測試檢查分鐘請求限制"""
    # 設定初始請求記錄
    controller.request_records = {
        "minute": [(time.time(), "http://example.com")] * 30,
        "hour": [],
        "day": []
    }
    
    # 檢查未超過限制
    assert controller._check_rate_limit("minute", "http://example.com")
    
    # 設定超過限制的請求記錄
    controller.request_records = {
        "minute": [(time.time(), "http://example.com")] * 60,
        "hour": [],
        "day": []
    }
    
    # 檢查超過限制
    assert not controller._check_rate_limit("minute", "http://example.com")

def test_check_rate_limit_hour(controller):
    """測試檢查小時請求限制"""
    # 設定初始請求記錄
    controller.request_records = {
        "minute": [],
        "hour": [(time.time(), "http://example.com")] * 500,
        "day": []
    }
    
    # 檢查未超過限制
    assert controller._check_rate_limit("hour", "http://example.com")
    
    # 設定超過限制的請求記錄
    controller.request_records = {
        "minute": [],
        "hour": [(time.time(), "http://example.com")] * 1000,
        "day": []
    }
    
    # 檢查超過限制
    assert not controller._check_rate_limit("hour", "http://example.com")

def test_check_rate_limit_day(controller):
    """測試檢查每日請求限制"""
    # 設定初始請求記錄
    controller.request_records = {
        "minute": [],
        "hour": [],
        "day": [(time.time(), "http://example.com")] * 5000
    }
    
    # 檢查未超過限制
    assert controller._check_rate_limit("day", "http://example.com")
    
    # 設定超過限制的請求記錄
    controller.request_records = {
        "minute": [],
        "hour": [],
        "day": [(time.time(), "http://example.com")] * 10000
    }
    
    # 檢查超過限制
    assert not controller._check_rate_limit("day", "http://example.com")

def test_record_request(controller):
    """測試記錄請求"""
    # 記錄請求
    controller._record_request("http://example.com")
    
    # 檢查記錄是否已新增
    assert len(controller.request_records["minute"]) == 1
    assert len(controller.request_records["hour"]) == 1
    assert len(controller.request_records["day"]) == 1
    
    # 檢查記錄內容
    assert controller.request_records["minute"][0][1] == "http://example.com"
    assert controller.request_records["hour"][0][1] == "http://example.com"
    assert controller.request_records["day"][0][1] == "http://example.com"

def test_cleanup_records(controller):
    """測試清理請求記錄"""
    # 設定過期的請求記錄
    old_time = time.time() - 61
    controller.request_records = {
        "minute": [(old_time, "http://example.com")],
        "hour": [(old_time, "http://example.com")],
        "day": [(old_time, "http://example.com")]
    }
    
    # 清理記錄
    controller._cleanup_records()
    
    # 檢查記錄是否已清理
    assert len(controller.request_records["minute"]) == 0
    assert len(controller.request_records["hour"]) == 0
    assert len(controller.request_records["day"]) == 0

def test_get_request(controller, session):
    """測試發送 GET 請求"""
    # 設定回應
    response = MagicMock(spec=Response)
    response.status_code = 200
    response.text = "test"
    session.get.return_value = response
    
    # 發送請求
    result = controller.get("http://example.com", session=session)
    
    # 檢查請求參數
    session.get.assert_called_once_with(
        "http://example.com",
        params=None,
        headers=None,
        timeout=30,
        allow_redirects=True
    )
    
    # 檢查回應
    assert result.status_code == 200
    assert result.text == "test"

def test_post_request(controller, session):
    """測試發送 POST 請求"""
    # 設定回應
    response = MagicMock(spec=Response)
    response.status_code = 200
    response.text = "test"
    session.post.return_value = response
    
    # 發送請求
    result = controller.post("http://example.com", data={"key": "value"}, session=session)
    
    # 檢查請求參數
    session.post.assert_called_once_with(
        "http://example.com",
        data={"key": "value"},
        json=None,
        headers=None,
        timeout=30,
        allow_redirects=True
    )
    
    # 檢查回應
    assert result.status_code == 200
    assert result.text == "test"

def test_put_request(controller, session):
    """測試發送 PUT 請求"""
    # 設定回應
    response = MagicMock(spec=Response)
    response.status_code = 200
    response.text = "test"
    session.put.return_value = response
    
    # 發送請求
    result = controller.put("http://example.com", data={"key": "value"}, session=session)
    
    # 檢查請求參數
    session.put.assert_called_once_with(
        "http://example.com",
        data={"key": "value"},
        json=None,
        headers=None,
        timeout=30,
        allow_redirects=True
    )
    
    # 檢查回應
    assert result.status_code == 200
    assert result.text == "test"

def test_delete_request(controller, session):
    """測試發送 DELETE 請求"""
    # 設定回應
    response = MagicMock(spec=Response)
    response.status_code = 200
    response.text = "test"
    session.delete.return_value = response
    
    # 發送請求
    result = controller.delete("http://example.com", session=session)
    
    # 檢查請求參數
    session.delete.assert_called_once_with(
        "http://example.com",
        params=None,
        headers=None,
        timeout=30,
        allow_redirects=True
    )
    
    # 檢查回應
    assert result.status_code == 200
    assert result.text == "test"

def test_head_request(controller, session):
    """測試發送 HEAD 請求"""
    # 設定回應
    response = MagicMock(spec=Response)
    response.status_code = 200
    session.head.return_value = response
    
    # 發送請求
    result = controller.head("http://example.com", session=session)
    
    # 檢查請求參數
    session.head.assert_called_once_with(
        "http://example.com",
        params=None,
        headers=None,
        timeout=30,
        allow_redirects=True
    )
    
    # 檢查回應
    assert result.status_code == 200

def test_options_request(controller, session):
    """測試發送 OPTIONS 請求"""
    # 設定回應
    response = MagicMock(spec=Response)
    response.status_code = 200
    session.options.return_value = response
    
    # 發送請求
    result = controller.options("http://example.com", session=session)
    
    # 檢查請求參數
    session.options.assert_called_once_with(
        "http://example.com",
        params=None,
        headers=None,
        timeout=30,
        allow_redirects=True
    )
    
    # 檢查回應
    assert result.status_code == 200

def test_patch_request(controller, session):
    """測試發送 PATCH 請求"""
    # 設定回應
    response = MagicMock(spec=Response)
    response.status_code = 200
    response.text = "test"
    session.patch.return_value = response
    
    # 發送請求
    result = controller.patch("http://example.com", data={"key": "value"}, session=session)
    
    # 檢查請求參數
    session.patch.assert_called_once_with(
        "http://example.com",
        data={"key": "value"},
        json=None,
        headers=None,
        timeout=30,
        allow_redirects=True
    )
    
    # 檢查回應
    assert result.status_code == 200
    assert result.text == "test"

def test_request_retry(controller, session):
    """測試請求重試"""
    # 設定失敗後成功的回應
    error_response = MagicMock(spec=Response)
    error_response.status_code = 500
    success_response = MagicMock(spec=Response)
    success_response.status_code = 200
    session.get.side_effect = [error_response, error_response, success_response]
    
    # 發送請求
    result = controller.get("http://example.com", session=session)
    
    # 檢查重試次數
    assert session.get.call_count == 3
    
    # 檢查最終回應
    assert result.status_code == 200

def test_request_rate_limit(controller, session):
    """測試請求限制"""
    # 設定超過限制的請求記錄
    controller.request_records = {
        "minute": [(time.time(), "http://example.com")] * 60,
        "hour": [],
        "day": []
    }
    
    # 發送請求
    with pytest.raises(Exception) as exc_info:
        controller.get("http://example.com", session=session)
    
    # 檢查錯誤訊息
    assert "Rate limit exceeded" in str(exc_info.value)

def test_close(controller, session):
    """測試關閉會話"""
    # 關閉會話
    controller.close(session)
    
    # 檢查會話是否已關閉
    session.close.assert_called_once() 
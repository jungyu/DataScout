"""
攔截器測試模組

測試攔截器的功能，包括各種攔截器的行為和攔截器鏈的執行
"""

import pytest
import time
from unittest.mock import MagicMock, patch
from datascout_core.core.request.interceptor import (
    RequestInterceptor,
    LoggingInterceptor,
    HeaderInterceptor,
    CookieInterceptor,
    RetryInterceptor,
    RateLimitInterceptor,
    InterceptorChain
)

@pytest.fixture
def base_config():
    """基本配置"""
    return {
        'test_key': 'test_value'
    }

@pytest.fixture
def logging_config():
    """日誌攔截器配置"""
    return {
        'log_level': 'INFO'
    }

@pytest.fixture
def header_config():
    """標頭攔截器配置"""
    return {
        'headers': {
            'X-Test-Header': 'test_value',
            'User-Agent': 'test_agent'
        }
    }

@pytest.fixture
def cookie_config():
    """Cookie 攔截器配置"""
    return {
        'cookies': {
            'session_id': 'test_session',
            'user_id': 'test_user'
        }
    }

@pytest.fixture
def retry_config():
    """重試攔截器配置"""
    return {
        'max_retries': 3
    }

@pytest.fixture
def rate_limit_config():
    """速率限制攔截器配置"""
    return {
        'max_requests': 2,
        'time_window': 1
    }

@pytest.fixture
def mock_response():
    """模擬回應"""
    response = MagicMock()
    response.status_code = 200
    return response

def test_base_interceptor(base_config):
    """測試基類攔截器"""
    interceptor = RequestInterceptor(base_config)
    assert interceptor.config == base_config
    
    # 基類方法應該不執行任何操作
    interceptor.before_request('GET', 'http://example.com')
    interceptor.after_response(MagicMock())
    interceptor.on_error(Exception('test error'))

@patch('datascout_core.core.logger.Logger')
def test_logging_interceptor(mock_logger, logging_config, mock_response):
    """測試日誌攔截器"""
    interceptor = LoggingInterceptor(logging_config)
    
    # 測試請求前處理
    interceptor.before_request('GET', 'http://example.com', data='test')
    mock_logger.return_value.info.assert_called_with('發送 GET 請求到 http://example.com')
    mock_logger.return_value.debug.assert_called_with("請求參數: {'data': 'test'}")
    
    # 測試回應後處理
    interceptor.after_response(mock_response)
    mock_logger.return_value.info.assert_called_with('收到回應，狀態碼: 200')
    
    # 測試錯誤處理
    interceptor.on_error(Exception('test error'))
    mock_logger.return_value.error.assert_called_with('請求錯誤: test error')

def test_header_interceptor(header_config):
    """測試標頭攔截器"""
    interceptor = HeaderInterceptor(header_config)
    kwargs = {'headers': {'Existing-Header': 'existing_value'}}
    
    # 測試標頭合併
    interceptor.before_request('GET', 'http://example.com', **kwargs)
    assert kwargs['headers']['X-Test-Header'] == 'test_value'
    assert kwargs['headers']['User-Agent'] == 'test_agent'
    assert kwargs['headers']['Existing-Header'] == 'existing_value'

def test_cookie_interceptor(cookie_config):
    """測試 Cookie 攔截器"""
    interceptor = CookieInterceptor(cookie_config)
    kwargs = {'cookies': {'existing_cookie': 'existing_value'}}
    
    # 測試 Cookie 合併
    interceptor.before_request('GET', 'http://example.com', **kwargs)
    assert kwargs['cookies']['session_id'] == 'test_session'
    assert kwargs['cookies']['user_id'] == 'test_user'
    assert kwargs['cookies']['existing_cookie'] == 'existing_value'

def test_retry_interceptor(retry_config):
    """測試重試攔截器"""
    interceptor = RetryInterceptor(retry_config)
    
    # 測試重試計數重置
    interceptor.retry_count = 2
    interceptor.before_request('GET', 'http://example.com')
    assert interceptor.retry_count == 0
    
    # 測試重試邏輯
    assert interceptor.on_error(Exception('test error')) is True
    assert interceptor.retry_count == 1
    
    assert interceptor.on_error(Exception('test error')) is True
    assert interceptor.retry_count == 2
    
    assert interceptor.on_error(Exception('test error')) is True
    assert interceptor.retry_count == 3
    
    assert interceptor.on_error(Exception('test error')) is False

def test_rate_limit_interceptor(rate_limit_config):
    """測試速率限制攔截器"""
    interceptor = RateLimitInterceptor(rate_limit_config)
    
    # 測試速率限制
    assert interceptor.before_request('GET', 'http://example.com') is True
    assert interceptor.before_request('GET', 'http://example.com') is True
    assert interceptor.before_request('GET', 'http://example.com') is False
    
    # 等待時間窗口過期
    time.sleep(1)
    assert interceptor.before_request('GET', 'http://example.com') is True

def test_interceptor_chain(
    logging_config,
    header_config,
    cookie_config,
    retry_config,
    rate_limit_config,
    mock_response
):
    """測試攔截器鏈"""
    # 創建攔截器列表
    interceptors = [
        LoggingInterceptor(logging_config),
        HeaderInterceptor(header_config),
        CookieInterceptor(cookie_config),
        RetryInterceptor(retry_config),
        RateLimitInterceptor(rate_limit_config)
    ]
    
    # 創建攔截器鏈
    chain = InterceptorChain(interceptors)
    
    # 測試請求前處理
    kwargs = {'headers': {}, 'cookies': {}}
    assert chain.before_request('GET', 'http://example.com', **kwargs) is True
    assert 'X-Test-Header' in kwargs['headers']
    assert 'session_id' in kwargs['cookies']
    
    # 測試回應後處理
    chain.after_response(mock_response)
    
    # 測試錯誤處理
    assert chain.on_error(Exception('test error')) is True

def test_interceptor_chain_error_handling(logging_config):
    """測試攔截器鏈錯誤處理"""
    # 創建一個會拋出異常的攔截器
    class ErrorInterceptor(RequestInterceptor):
        def before_request(self, method: str, url: str, **kwargs) -> None:
            raise Exception('test error')
    
    # 創建攔截器鏈
    chain = InterceptorChain([
        LoggingInterceptor(logging_config),
        ErrorInterceptor(logging_config)
    ])
    
    # 測試錯誤處理
    assert chain.before_request('GET', 'http://example.com') is False 
"""
請求客戶端測試模組

測試請求客戶端的功能，包括 User-Agent 和代理輪換
"""

import pytest
import requests
from unittest.mock import patch, MagicMock
from selenium_base.core.request.client import RequestClient
from selenium_base.utils.exceptions import RequestError

@pytest.fixture
def test_config():
    """測試配置"""
    return {
        'timeout': 30,
        'retry': {
            'total': 3,
            'backoff_factor': 0.5,
            'status_forcelist': [500, 502, 503, 504]
        },
        'headers': {
            'Accept': 'application/json'
        },
        'cookies': {
            'session': 'test_session'
        },
        'verify': True,
        'rate_limit': {
            'max_requests': 10,
            'time_window': 1
        },
        'browser': {
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'platform': 'Windows'
        },
        'anti_detection': {
            'random_delay': (1, 3),
            'rotate_user_agent': True,
            'rotate_proxy': True,
            'user_agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            ],
            'proxies': [
                {'http': 'http://proxy1.example.com:8080', 'https': 'https://proxy1.example.com:8080'},
                {'http': 'http://proxy2.example.com:8080', 'https': 'https://proxy2.example.com:8080'},
                {'http': 'http://proxy3.example.com:8080', 'https': 'https://proxy3.example.com:8080'}
            ]
        }
    }

@pytest.fixture
def client(test_config):
    """請求客戶端實例"""
    return RequestClient(test_config)

def test_init(test_config):
    """測試初始化"""
    client = RequestClient(test_config)
    assert client.config == test_config
    assert client.session.headers['Accept'] == 'application/json'
    assert client.session.cookies['session'] == 'test_session'
    assert client.session.proxies == test_config['anti_detection']['proxies'][0]
    assert client.user_agents == test_config['anti_detection']['user_agents']
    assert client.proxies == test_config['anti_detection']['proxies']
    assert client.current_user_agent_index == 0
    assert client.current_proxy_index == 0

def test_init_without_rotation(test_config):
    """測試無輪換功能的初始化"""
    test_config['anti_detection']['rotate_user_agent'] = False
    test_config['anti_detection']['rotate_proxy'] = False
    client = RequestClient(test_config)
    assert not hasattr(client, 'user_agents')
    assert not hasattr(client, 'proxies')

def test_init_without_user_agents(test_config):
    """測試無 User-Agent 列表的初始化"""
    test_config['anti_detection']['user_agents'] = []
    client = RequestClient(test_config)
    assert not hasattr(client, 'user_agents')

def test_init_without_proxies(test_config):
    """測試無代理列表的初始化"""
    test_config['anti_detection']['proxies'] = []
    client = RequestClient(test_config)
    assert not hasattr(client, 'proxies')

@patch('requests.Session.request')
def test_request_with_rotation(mock_request, client, test_config):
    """測試帶輪換的請求"""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_request.return_value = mock_response
    
    # 發送第一個請求
    client.request('GET', 'http://example.com')
    assert client.session.headers['User-Agent'] == test_config['anti_detection']['user_agents'][0]
    assert client.session.proxies == test_config['anti_detection']['proxies'][0]
    
    # 發送第二個請求
    client.request('GET', 'http://example.com')
    assert client.session.headers['User-Agent'] == test_config['anti_detection']['user_agents'][1]
    assert client.session.proxies == test_config['anti_detection']['proxies'][1]
    
    # 發送第三個請求
    client.request('GET', 'http://example.com')
    assert client.session.headers['User-Agent'] == test_config['anti_detection']['user_agents'][2]
    assert client.session.proxies == test_config['anti_detection']['proxies'][2]
    
    # 發送第四個請求（應該回到第一個）
    client.request('GET', 'http://example.com')
    assert client.session.headers['User-Agent'] == test_config['anti_detection']['user_agents'][0]
    assert client.session.proxies == test_config['anti_detection']['proxies'][0]

@patch('requests.Session.request')
def test_request_without_rotation(mock_request, test_config):
    """測試無輪換的請求"""
    test_config['anti_detection']['rotate_user_agent'] = False
    test_config['anti_detection']['rotate_proxy'] = False
    client = RequestClient(test_config)
    
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_request.return_value = mock_response
    
    # 發送多個請求
    for _ in range(3):
        client.request('GET', 'http://example.com')
        assert client.session.headers['User-Agent'] == test_config['browser']['user_agent']
        assert 'proxies' not in client.session.__dict__

@patch('requests.Session.request')
def test_request_error_handling(mock_request, client):
    """測試請求錯誤處理"""
    mock_request.side_effect = requests.exceptions.RequestException("測試錯誤")
    
    with pytest.raises(RequestError) as exc_info:
        client.request('GET', 'http://example.com')
    assert "請求失敗" in str(exc_info.value)

@patch('time.sleep')
def test_random_delay(mock_sleep, client):
    """測試隨機延遲"""
    with patch('requests.Session.request') as mock_request:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        client.request('GET', 'http://example.com')
        mock_sleep.assert_called_once()
        delay = mock_sleep.call_args[0][0]
        assert 1 <= delay <= 3

def test_close(client):
    """測試關閉會話"""
    client.close()
    assert client.session.closed

def test_context_manager(test_config):
    """測試上下文管理器"""
    with RequestClient(test_config) as client:
        assert isinstance(client, RequestClient)
        assert not client.session.closed
    assert client.session.closed 
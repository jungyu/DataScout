"""
請求客戶端類別測試

測試請求客戶端類別的各項功能
"""

import pytest
from unittest.mock import MagicMock, patch
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from selenium_base.core.request.client import RequestClient
from selenium_base.utils.exceptions import RequestError

@pytest.fixture
def client_config():
    """請求客戶端配置"""
    return {
        'timeout': 30,
        'retry': {
            'total': 3,
            'backoff_factor': 0.5,
            'status_forcelist': [500, 502, 503, 504]
        },
        'proxy': {
            'http': 'http://127.0.0.1:8080',
            'https': 'https://127.0.0.1:8080'
        },
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        'cookies': {
            'session': 'test_session'
        },
        'verify': True,
        'rate_limit': {
            'max_requests': 10,
            'time_window': 1.0
        }
    }

@pytest.fixture
def mock_response():
    """模擬回應"""
    response = MagicMock()
    response.status_code = 200
    response.headers = {
        'Content-Type': 'application/json',
        'Set-Cookie': 'session=test_session'
    }
    response.cookies = {'session': 'test_session'}
    response.content = b'{"test": "data"}'
    response.text = '{"test": "data"}'
    response.json.return_value = {'test': 'data'}
    return response

def test_init(client_config):
    """測試初始化"""
    client = RequestClient(client_config)
    assert client.config == client_config
    assert client.session is not None
    assert client.rate_limiter is not None

def test_create_session(client_config):
    """測試建立會話"""
    client = RequestClient(client_config)
    session = client._create_session()
    
    # 檢查重試策略
    assert session.adapters['http://'].max_retries.total == client_config['retry']['total']
    assert session.adapters['http://'].max_retries.backoff_factor == client_config['retry']['backoff_factor']
    assert session.adapters['https://'].max_retries.total == client_config['retry']['total']
    assert session.adapters['https://'].max_retries.backoff_factor == client_config['retry']['backoff_factor']
    
    # 檢查代理設定
    assert session.proxies == client_config['proxy']
    
    # 檢查標頭設定
    assert session.headers['User-Agent'] == client_config['headers']['User-Agent']
    
    # 檢查 Cookie 設定
    assert session.cookies['session'] == client_config['cookies']['session']

@patch('requests.Session.request')
def test_request(mock_request, client_config, mock_response):
    """測試請求發送"""
    client = RequestClient(client_config)
    mock_request.return_value = mock_response
    
    # 測試正常請求
    response = client.request('GET', 'http://example.com')
    assert response.status_code == 200
    assert response.json() == {'test': 'data'}
    
    # 測試請求失敗
    mock_request.side_effect = RequestException('Request Error')
    with pytest.raises(RequestError):
        client.request('GET', 'http://example.com')

@patch('requests.Session.get')
def test_get(mock_get, client_config, mock_response):
    """測試 GET 請求"""
    client = RequestClient(client_config)
    mock_get.return_value = mock_response
    
    # 測試正常請求
    response = client.get('http://example.com')
    assert response.status_code == 200
    assert response.json() == {'test': 'data'}
    
    # 測試請求失敗
    mock_get.side_effect = RequestException('Request Error')
    with pytest.raises(RequestError):
        client.get('http://example.com')

@patch('requests.Session.post')
def test_post(mock_post, client_config, mock_response):
    """測試 POST 請求"""
    client = RequestClient(client_config)
    mock_post.return_value = mock_response
    
    # 測試正常請求
    response = client.post('http://example.com', data={'test': 'data'})
    assert response.status_code == 200
    assert response.json() == {'test': 'data'}
    
    # 測試請求失敗
    mock_post.side_effect = RequestException('Request Error')
    with pytest.raises(RequestError):
        client.post('http://example.com', data={'test': 'data'})

@patch('requests.Session.put')
def test_put(mock_put, client_config, mock_response):
    """測試 PUT 請求"""
    client = RequestClient(client_config)
    mock_put.return_value = mock_response
    
    # 測試正常請求
    response = client.put('http://example.com', data={'test': 'data'})
    assert response.status_code == 200
    assert response.json() == {'test': 'data'}
    
    # 測試請求失敗
    mock_put.side_effect = RequestException('Request Error')
    with pytest.raises(RequestError):
        client.put('http://example.com', data={'test': 'data'})

@patch('requests.Session.delete')
def test_delete(mock_delete, client_config, mock_response):
    """測試 DELETE 請求"""
    client = RequestClient(client_config)
    mock_delete.return_value = mock_response
    
    # 測試正常請求
    response = client.delete('http://example.com')
    assert response.status_code == 200
    assert response.json() == {'test': 'data'}
    
    # 測試請求失敗
    mock_delete.side_effect = RequestException('Request Error')
    with pytest.raises(RequestError):
        client.delete('http://example.com')

def test_close(client_config):
    """測試關閉會話"""
    client = RequestClient(client_config)
    client.close()
    assert client.session.closed

def test_context_manager(client_config):
    """測試上下文管理器"""
    with RequestClient(client_config) as client:
        assert client.session is not None
        assert not client.session.closed
    assert client.session.closed 
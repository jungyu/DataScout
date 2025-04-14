"""
請求控制模組測試

測試請求控制類別的各項功能
"""

import os
import pytest
from unittest.mock import MagicMock, patch, mock_open
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from datascout_core.core.request import Request
from datascout_core.core.exceptions import RequestError, RateLimitError, TimeoutError, NetworkError

@pytest.fixture
def request_config():
    """請求配置"""
    return {
        'retry_count': 3,
        'retry_delay': 1,
        'timeout': 30,
        'rate_limit': 10,
        'rate_limit_burst': 20,
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
        'allow_redirects': True,
        'max_redirects': 5
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

def test_init(request_config):
    """測試初始化"""
    request = Request(request_config)
    assert request.config == request_config
    assert request.session is not None
    assert request.last_request_time == 0
    assert request.request_count == 0
    assert request.rate_limit_reset_time == 0

def test_create_session(request_config):
    """測試建立會話"""
    request = Request(request_config)
    session = request._create_session()
    
    # 檢查重試策略
    assert session.adapters['http://'].max_retries.total == request_config['retry_count']
    assert session.adapters['http://'].max_retries.backoff_factor == request_config['retry_delay']
    assert session.adapters['https://'].max_retries.total == request_config['retry_count']
    assert session.adapters['https://'].max_retries.backoff_factor == request_config['retry_delay']
    
    # 檢查代理設定
    assert session.proxies == request_config['proxy']
    
    # 檢查標頭設定
    assert session.headers['User-Agent'] == request_config['headers']['User-Agent']
    
    # 檢查 Cookie 設定
    assert session.cookies['session'] == request_config['cookies']['session']

def test_check_rate_limit(request_config):
    """測試速率限制"""
    request = Request(request_config)
    
    # 測試正常請求
    for _ in range(request_config['rate_limit']):
        request._check_rate_limit()
        assert request.request_count <= request_config['rate_limit']
    
    # 測試超過速率限制
    with pytest.raises(RateLimitError):
        for _ in range(request_config['rate_limit_burst'] + 1):
            request._check_rate_limit()

def test_handle_response(request_config, mock_response):
    """測試處理回應"""
    request = Request(request_config)
    
    # 測試正常回應
    result = request._handle_response(mock_response)
    assert result['status_code'] == 200
    assert result['headers'] == dict(mock_response.headers)
    assert result['cookies'] == dict(mock_response.cookies)
    assert result['content'] == mock_response.content
    assert result['text'] == mock_response.text
    assert result['json'] == mock_response.json()
    
    # 測試 HTTP 錯誤
    mock_response.raise_for_status.side_effect = HTTPError('HTTP Error')
    with pytest.raises(RequestError):
        request._handle_response(mock_response)
    
    # 測試網路錯誤
    mock_response.raise_for_status.side_effect = ConnectionError('Connection Error')
    with pytest.raises(NetworkError):
        request._handle_response(mock_response)
    
    # 測試超時錯誤
    mock_response.raise_for_status.side_effect = Timeout('Timeout Error')
    with pytest.raises(TimeoutError):
        request._handle_response(mock_response)
    
    # 測試請求錯誤
    mock_response.raise_for_status.side_effect = RequestException('Request Error')
    with pytest.raises(RequestError):
        request._handle_response(mock_response)

@patch('requests.Session.get')
def test_get(mock_get, request_config, mock_response):
    """測試 GET 請求"""
    request = Request(request_config)
    mock_get.return_value = mock_response
    
    # 測試正常請求
    result = request.get('http://example.com')
    assert result['status_code'] == 200
    assert result['json'] == {'test': 'data'}
    
    # 測試請求失敗
    mock_get.side_effect = RequestException('Request Error')
    with pytest.raises(RequestError):
        request.get('http://example.com')

@patch('requests.Session.post')
def test_post(mock_post, request_config, mock_response):
    """測試 POST 請求"""
    request = Request(request_config)
    mock_post.return_value = mock_response
    
    # 測試正常請求
    result = request.post('http://example.com', data={'test': 'data'})
    assert result['status_code'] == 200
    assert result['json'] == {'test': 'data'}
    
    # 測試請求失敗
    mock_post.side_effect = RequestException('Request Error')
    with pytest.raises(RequestError):
        request.post('http://example.com', data={'test': 'data'})

@patch('requests.Session.put')
def test_put(mock_put, request_config, mock_response):
    """測試 PUT 請求"""
    request = Request(request_config)
    mock_put.return_value = mock_response
    
    # 測試正常請求
    result = request.put('http://example.com', data={'test': 'data'})
    assert result['status_code'] == 200
    assert result['json'] == {'test': 'data'}
    
    # 測試請求失敗
    mock_put.side_effect = RequestException('Request Error')
    with pytest.raises(RequestError):
        request.put('http://example.com', data={'test': 'data'})

@patch('requests.Session.delete')
def test_delete(mock_delete, request_config, mock_response):
    """測試 DELETE 請求"""
    request = Request(request_config)
    mock_delete.return_value = mock_response
    
    # 測試正常請求
    result = request.delete('http://example.com')
    assert result['status_code'] == 200
    assert result['json'] == {'test': 'data'}
    
    # 測試請求失敗
    mock_delete.side_effect = RequestException('Request Error')
    with pytest.raises(RequestError):
        request.delete('http://example.com')

@patch('requests.Session.request')
def test_request(mock_request, request_config, mock_response):
    """測試自定義請求"""
    request = Request(request_config)
    mock_request.return_value = mock_response
    
    # 測試正常請求
    result = request.request('PATCH', 'http://example.com', data={'test': 'data'})
    assert result['status_code'] == 200
    assert result['json'] == {'test': 'data'}
    
    # 測試請求失敗
    mock_request.side_effect = RequestException('Request Error')
    with pytest.raises(RequestError):
        request.request('PATCH', 'http://example.com', data={'test': 'data'})

@patch('requests.Session.get')
def test_download(mock_get, request_config, mock_response, tmp_path):
    """測試下載檔案"""
    request = Request(request_config)
    mock_get.return_value = mock_response
    mock_response.iter_content.return_value = [b'test data']
    
    # 測試正常下載
    file_path = os.path.join(tmp_path, 'test.txt')
    with patch('builtins.open', mock_open()) as mock_file:
        request.download('http://example.com/file.txt', file_path)
        mock_file.assert_called_once_with(file_path, 'wb')
    
    # 測試下載失敗
    mock_get.side_effect = RequestException('Download Error')
    with pytest.raises(RequestError):
        request.download('http://example.com/file.txt', file_path)

@patch('requests.Session.post')
def test_upload(mock_post, request_config, mock_response, tmp_path):
    """測試上傳檔案"""
    request = Request(request_config)
    mock_post.return_value = mock_response
    
    # 建立測試檔案
    file_path = os.path.join(tmp_path, 'test.txt')
    with open(file_path, 'w') as f:
        f.write('test data')
    
    # 測試正常上傳
    result = request.upload('http://example.com/upload', file_path)
    assert result['status_code'] == 200
    assert result['json'] == {'test': 'data'}
    
    # 測試上傳失敗
    mock_post.side_effect = RequestException('Upload Error')
    with pytest.raises(RequestError):
        request.upload('http://example.com/upload', file_path)

def test_set_proxy(request_config):
    """測試設定代理"""
    request = Request(request_config)
    new_proxy = {
        'http': 'http://127.0.0.1:8081',
        'https': 'https://127.0.0.1:8081'
    }
    
    request.set_proxy(new_proxy)
    assert request.session.proxies == new_proxy
    assert request.config['proxy'] == new_proxy

def test_set_headers(request_config):
    """測試設定標頭"""
    request = Request(request_config)
    new_headers = {
        'User-Agent': 'New User Agent',
        'Accept': 'application/json'
    }
    
    request.set_headers(new_headers)
    assert request.session.headers['User-Agent'] == 'New User Agent'
    assert request.session.headers['Accept'] == 'application/json'
    assert request.config['headers'] == new_headers

def test_set_cookies(request_config):
    """測試設定 Cookie"""
    request = Request(request_config)
    new_cookies = {
        'session': 'new_session',
        'user': 'test_user'
    }
    
    request.set_cookies(new_cookies)
    assert request.session.cookies['session'] == 'new_session'
    assert request.session.cookies['user'] == 'test_user'
    assert request.config['cookies'] == new_cookies

def test_clear_cookies(request_config):
    """測試清除 Cookie"""
    request = Request(request_config)
    
    request.clear_cookies()
    assert len(request.session.cookies) == 0
    assert request.config['cookies'] == {}

def test_close(request_config):
    """測試關閉會話"""
    request = Request(request_config)
    
    request.close()
    request.session.close.assert_called_once() 
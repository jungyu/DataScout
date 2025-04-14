"""
速率限制器測試模組

測試速率限制器的功能，包括令牌桶和滑動窗口算法
"""

import pytest
import time
from datascout_core.core.request.rate_limit import RateLimiter
from datascout_core.core.exceptions import RateLimitError

@pytest.fixture
def token_bucket_config():
    """令牌桶算法配置"""
    return {
        'max_requests': 5,
        'time_window': 1,
        'algorithm': 'token_bucket',
        'bucket_size': 5,
        'refill_rate': 5
    }

@pytest.fixture
def sliding_window_config():
    """滑動窗口算法配置"""
    return {
        'max_requests': 5,
        'time_window': 1,
        'algorithm': 'sliding_window'
    }

@pytest.fixture
def token_bucket_limiter(token_bucket_config):
    """令牌桶限制器實例"""
    return RateLimiter(token_bucket_config)

@pytest.fixture
def sliding_window_limiter(sliding_window_config):
    """滑動窗口限制器實例"""
    return RateLimiter(sliding_window_config)

def test_init_token_bucket(token_bucket_config):
    """測試令牌桶限制器初始化"""
    limiter = RateLimiter(token_bucket_config)
    assert limiter.max_requests == token_bucket_config['max_requests']
    assert limiter.time_window == token_bucket_config['time_window']
    assert limiter.algorithm == 'token_bucket'
    assert limiter.bucket_size == token_bucket_config['bucket_size']
    assert limiter.refill_rate == token_bucket_config['refill_rate']
    assert limiter.tokens == token_bucket_config['bucket_size']

def test_init_sliding_window(sliding_window_config):
    """測試滑動窗口限制器初始化"""
    limiter = RateLimiter(sliding_window_config)
    assert limiter.max_requests == sliding_window_config['max_requests']
    assert limiter.time_window == sliding_window_config['time_window']
    assert limiter.algorithm == 'sliding_window'
    assert limiter.requests == []

def test_init_with_defaults():
    """測試使用預設值初始化"""
    limiter = RateLimiter({})
    assert limiter.max_requests == 10
    assert limiter.time_window == 1
    assert limiter.algorithm == 'sliding_window'
    assert limiter.requests == []

def test_token_bucket_acquire(token_bucket_limiter):
    """測試令牌桶算法獲取許可"""
    # 初始狀態應該可以獲取許可
    assert token_bucket_limiter.acquire() is True
    assert token_bucket_limiter.tokens == 4
    
    # 消耗所有令牌
    for _ in range(4):
        assert token_bucket_limiter.acquire() is True
    
    # 令牌用完，無法獲取許可
    assert token_bucket_limiter.acquire() is False
    
    # 等待令牌填充
    time.sleep(1)
    assert token_bucket_limiter.acquire() is True

def test_sliding_window_acquire(sliding_window_limiter):
    """測試滑動窗口算法獲取許可"""
    # 初始狀態應該可以獲取許可
    assert sliding_window_limiter.acquire() is True
    assert len(sliding_window_limiter.requests) == 1
    
    # 發送最大請求數
    for _ in range(4):
        assert sliding_window_limiter.acquire() is True
    
    # 超過限制，無法獲取許可
    assert sliding_window_limiter.acquire() is False
    
    # 等待窗口滑動
    time.sleep(1)
    assert sliding_window_limiter.acquire() is True

def test_token_bucket_wait(token_bucket_limiter):
    """測試令牌桶算法等待許可"""
    # 消耗所有令牌
    for _ in range(5):
        token_bucket_limiter.acquire()
    
    # 等待許可
    start_time = time.time()
    token_bucket_limiter.wait()
    wait_time = time.time() - start_time
    
    # 等待時間應該在合理範圍內
    assert 0.8 <= wait_time <= 1.2

def test_sliding_window_wait(sliding_window_limiter):
    """測試滑動窗口算法等待許可"""
    # 發送最大請求數
    for _ in range(5):
        sliding_window_limiter.acquire()
    
    # 等待許可
    start_time = time.time()
    sliding_window_limiter.wait()
    wait_time = time.time() - start_time
    
    # 等待時間應該在合理範圍內
    assert 0.8 <= wait_time <= 1.2

def test_wait_timeout(token_bucket_limiter):
    """測試等待超時"""
    # 消耗所有令牌
    for _ in range(5):
        token_bucket_limiter.acquire()
    
    # 設置較小的時間窗口
    token_bucket_limiter.time_window = 0.1
    token_bucket_limiter.refill_rate = 0
    
    # 等待應該超時
    with pytest.raises(RateLimitError) as exc_info:
        token_bucket_limiter.wait()
    assert "等待請求許可超時" in str(exc_info.value)

def test_reset_token_bucket(token_bucket_limiter):
    """測試重置令牌桶限制器"""
    # 消耗一些令牌
    token_bucket_limiter.acquire()
    token_bucket_limiter.acquire()
    
    # 重置
    token_bucket_limiter.reset()
    
    # 檢查狀態
    assert token_bucket_limiter.tokens == token_bucket_limiter.bucket_size
    assert token_bucket_limiter.acquire() is True

def test_reset_sliding_window(sliding_window_limiter):
    """測試重置滑動窗口限制器"""
    # 發送一些請求
    sliding_window_limiter.acquire()
    sliding_window_limiter.acquire()
    
    # 重置
    sliding_window_limiter.reset()
    
    # 檢查狀態
    assert sliding_window_limiter.requests == []
    assert sliding_window_limiter.acquire() is True 
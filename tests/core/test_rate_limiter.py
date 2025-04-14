"""
速率限制器類別測試

測試速率限制器類別的各項功能
"""

import time
import pytest
from datascout_core.core.request.rate import RateLimiter
from datascout_core.utils.exceptions import RateLimitError

def test_init():
    """測試初始化"""
    # 測試無限制
    limiter = RateLimiter()
    assert limiter.max_requests == 0
    assert limiter.time_window == 0.0
    assert len(limiter.requests) == 0
    
    # 測試有限制
    limiter = RateLimiter(max_requests=10, time_window=1.0)
    assert limiter.max_requests == 10
    assert limiter.time_window == 1.0
    assert len(limiter.requests) == 0

def test_wait():
    """測試等待機制"""
    # 測試無限制
    limiter = RateLimiter()
    start_time = time.time()
    limiter.wait()
    end_time = time.time()
    assert end_time - start_time < 0.1  # 應該幾乎不需要等待
    
    # 測試有限制
    limiter = RateLimiter(max_requests=2, time_window=1.0)
    
    # 第一次請求
    limiter.wait()
    assert len(limiter.requests) == 1
    
    # 第二次請求
    limiter.wait()
    assert len(limiter.requests) == 2
    
    # 第三次請求應該需要等待
    start_time = time.time()
    limiter.wait()
    end_time = time.time()
    assert end_time - start_time >= 1.0  # 應該等待至少1秒
    assert len(limiter.requests) == 3

def test_reset():
    """測試重置"""
    limiter = RateLimiter(max_requests=2, time_window=1.0)
    
    # 發送一些請求
    limiter.wait()
    limiter.wait()
    assert len(limiter.requests) == 2
    
    # 重置
    limiter.reset()
    assert len(limiter.requests) == 0
    
    # 重置後應該可以立即發送請求
    start_time = time.time()
    limiter.wait()
    end_time = time.time()
    assert end_time - start_time < 0.1

def test_get_remaining_requests():
    """測試獲取剩餘請求數"""
    # 測試無限制
    limiter = RateLimiter()
    assert limiter.get_remaining_requests() == -1
    
    # 測試有限制
    limiter = RateLimiter(max_requests=2, time_window=1.0)
    assert limiter.get_remaining_requests() == 2
    
    limiter.wait()
    assert limiter.get_remaining_requests() == 1
    
    limiter.wait()
    assert limiter.get_remaining_requests() == 0
    
    # 等待時間窗口過期
    time.sleep(1.1)
    assert limiter.get_remaining_requests() == 2

def test_get_next_request_time():
    """測試獲取下一個請求時間"""
    # 測試無限制
    limiter = RateLimiter()
    assert limiter.get_next_request_time() is None
    
    # 測試有限制
    limiter = RateLimiter(max_requests=2, time_window=1.0)
    assert limiter.get_next_request_time() is None
    
    limiter.wait()
    assert limiter.get_next_request_time() is None
    
    limiter.wait()
    next_time = limiter.get_next_request_time()
    assert next_time is not None
    assert next_time > time.time()
    assert next_time <= time.time() + 1.0 
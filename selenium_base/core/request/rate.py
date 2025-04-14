"""
速率限制器類別

提供請求速率限制功能，防止過度頻繁的請求
"""

import time
from typing import List, Optional
from selenium_base.utils.exceptions import RateLimitError
from selenium_base.utils.logger import Logger

class RateLimiter:
    """速率限制器類別"""
    
    def __init__(self, max_requests: int = 0, time_window: float = 0.0):
        """
        初始化速率限制器
        
        Args:
            max_requests: 時間窗口內最大請求數，0表示無限制
            time_window: 時間窗口大小（秒），0表示無限制
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.logger = Logger('rate_limiter')
        self.requests: List[float] = []
    
    def wait(self) -> None:
        """
        等待直到可以發送下一個請求
        
        Raises:
            RateLimitError: 達到速率限制
        """
        if self.max_requests <= 0 or self.time_window <= 0:
            return
        
        current_time = time.time()
        
        # 清理過期的請求記錄
        self.requests = [t for t in self.requests if current_time - t <= self.time_window]
        
        # 檢查是否達到速率限制
        if len(self.requests) >= self.max_requests:
            # 計算需要等待的時間
            wait_time = self.requests[0] + self.time_window - current_time
            if wait_time > 0:
                self.logger.info(f'達到速率限制，等待 {wait_time:.2f} 秒')
                time.sleep(wait_time)
                # 重新清理過期的請求記錄
                current_time = time.time()
                self.requests = [t for t in self.requests if current_time - t <= self.time_window]
        
        # 記錄當前請求
        self.requests.append(current_time)
    
    def reset(self) -> None:
        """
        重置速率限制器
        """
        self.requests.clear()
    
    def get_remaining_requests(self) -> int:
        """
        獲取剩餘可發送請求數
        
        Returns:
            int: 剩餘可發送請求數
        """
        if self.max_requests <= 0:
            return -1  # 無限制
        
        current_time = time.time()
        self.requests = [t for t in self.requests if current_time - t <= self.time_window]
        return max(0, self.max_requests - len(self.requests))
    
    def get_next_request_time(self) -> Optional[float]:
        """
        獲取下一個可發送請求的時間
        
        Returns:
            Optional[float]: 下一個可發送請求的時間，如果沒有限制則返回None
        """
        if self.max_requests <= 0 or len(self.requests) < self.max_requests:
            return None
        
        return self.requests[0] + self.time_window 
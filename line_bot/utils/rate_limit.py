"""
請求頻率限制工具函數
"""

import time
from collections import defaultdict
from line_bot.config import RATE_LIMIT

# 用於存儲用戶請求記錄
user_requests = defaultdict(list)

def check_rate_limit(user_id: str) -> bool:
    """檢查用戶請求頻率是否超過限制
    
    Args:
        user_id: 用戶 ID
        
    Returns:
        bool: 是否允許請求
    """
    current_time = time.time()
    window_seconds = RATE_LIMIT["window_seconds"]
    max_requests = RATE_LIMIT["max_requests"]
    
    # 清理過期的請求記錄
    user_requests[user_id] = [
        req_time for req_time in user_requests[user_id]
        if current_time - req_time < window_seconds
    ]
    
    # 檢查請求頻率
    if len(user_requests[user_id]) >= max_requests:
        return False
        
    # 記錄新的請求
    user_requests[user_id].append(current_time)
    return True 
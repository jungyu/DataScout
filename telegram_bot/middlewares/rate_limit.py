"""
請求頻率限制中介軟體
"""

import time
import logging
from typing import Any, Dict, List, Optional

from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.config import RATE_LIMIT, MESSAGES

logger = logging.getLogger(__name__)

# 用戶請求記錄
user_requests: Dict[int, List[float]] = {}


def is_rate_limited(user_id: int) -> bool:
    """檢查用戶是否超過請求頻率限制
    
    Args:
        user_id: 用戶的 Telegram ID
    
    Returns:
        是否超過限制
    """
    global user_requests
    
    # 獲取配置
    window_seconds = RATE_LIMIT["window_seconds"]
    max_requests = RATE_LIMIT["max_requests"]
    
    # 獲取當前時間
    current_time = time.time()
    
    # 初始化用戶請求記錄
    if user_id not in user_requests:
        user_requests[user_id] = []
    
    # 刪除時間窗口之外的請求記錄
    user_requests[user_id] = [
        timestamp for timestamp in user_requests[user_id]
        if current_time - timestamp <= window_seconds
    ]
    
    # 檢查是否超過限制
    if len(user_requests[user_id]) >= max_requests:
        return True
    
    # 記錄此次請求
    user_requests[user_id].append(current_time)
    return False


async def send_rate_limited_message(update: Update) -> None:
    """向被頻率限制的用戶發送提示訊息
    
    Args:
        update: Telegram 更新物件
    """
    if update.effective_message:
        await update.effective_message.reply_text(MESSAGES["rate_limited"])


async def check_rate_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[bool]:
    """請求頻率限制處理器
    
    作為處理器使用，限制用戶發送請求的頻率
    
    Args:
        update: 更新物件
        context: 上下文物件
        
    Returns:
        None 表示繼續處理，False 表示停止處理鏈
    """
    # 只處理來自用戶的訊息
    if not update.effective_user:
        return None
        
    user_id = update.effective_user.id
    
    # 檢查是否超過頻率限制
    if is_rate_limited(user_id):
        # 用戶超過頻率限制
        logger.warning(f"Rate limit exceeded for user ID {user_id}")
        await send_rate_limited_message(update)
        # 返回 False 表示停止處理鏈
        return False
        
    # 返回 None 表示繼續處理
    return None

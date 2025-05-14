"""
身份驗證中介軟體
"""

import logging
from typing import Any, Optional

from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext.filters import UpdateFilter

from telegram_bot.config import AUTHORIZED_USERS, REQUIRE_AUTH, ADMIN_USER_IDS, MESSAGES

logger = logging.getLogger(__name__)

# 全域變數
_allowed_users = set(AUTHORIZED_USERS + ADMIN_USER_IDS)


def is_user_authorized(user_id: int) -> bool:
    """檢查用戶是否被授權使用機器人
    
    Args:
        user_id: 用戶的 Telegram ID
    
    Returns:
        是否已授權
    """
    # 如果關閉了授權檢查，則所有用戶都被授權
    if not REQUIRE_AUTH:
        return True
    
    # 否則檢查用戶ID是否在已授權清單中
    return user_id in _allowed_users


async def send_unauthorized_message(update: Update) -> None:
    """向未授權用戶發送拒絕訊息
    
    Args:
        update: Telegram 更新物件
    """
    if update.effective_message:
        await update.effective_message.reply_text(MESSAGES["unauthorized"])


async def check_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[bool]:
    """身份驗證處理器
    
    作為處理器使用，檢查用戶是否有權使用機器人
    
    Args:
        update: 更新物件
        context: 上下文物件
        
    Returns:
        None 表示繼續處理，False 表示停止處理鏈
    """
    if not update.effective_user:
        return None
        
    user_id = update.effective_user.id
    
    # 檢查是否授權
    if is_user_authorized(user_id):
        # 用戶已授權，繼續處理
        return None
    else:
        # 用戶未授權，拒絕請求並發送拒絕訊息
        logger.warning(f"Unauthorized access attempt from user ID {user_id}")
        await send_unauthorized_message(update)
        # 返回 False 表示停止處理鏈
        return False

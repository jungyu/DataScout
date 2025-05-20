"""
身份驗證工具函數
"""

from line_bot.config import AUTHORIZED_USERS, ADMIN_USER_IDS

def check_auth(user_id: str) -> bool:
    """檢查用戶是否已授權
    
    Args:
        user_id: 用戶 ID
        
    Returns:
        bool: 是否已授權
    """
    return user_id in AUTHORIZED_USERS

def is_admin(user_id: str) -> bool:
    """檢查用戶是否為管理員
    
    Args:
        user_id: 用戶 ID
        
    Returns:
        bool: 是否為管理員
    """
    return user_id in ADMIN_USER_IDS 
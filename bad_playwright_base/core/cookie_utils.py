"""
cookie_utils.py - 共用初始 Cookie 設定工具
"""
from typing import List, Dict, Any
from loguru import logger

def add_initial_cookies(context, cookies: List[Dict[str, Any]]) -> None:
    """
    批量設置初始 Cookie
    Args:
        context: Playwright BrowserContext 物件
        cookies: Cookie 字典列表
    """
    try:
        context.add_cookies(cookies)
        logger.info(f"已批量設置初始 Cookie: {len(cookies)} 筆")
    except Exception as e:
        logger.warning(f"設置初始 Cookie 時發生錯誤: {str(e)}")

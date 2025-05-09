from typing import List, Dict, Any, Optional
from loguru import logger

def check_and_handle_popup(page, selectors: Dict[str, List[str]]) -> bool:
    """
    檢查並處理常見付費牆、cookie banner、彈窗
    Args:
        page: Playwright Page 物件
        selectors: dict，格式如 {'cookie': [...], 'popup': [...], 'paywall': [...]}，每個 value 為 selector list
    Returns:
        bool: 是否有成功自動處理
    """
    # 處理 cookie banner
    for selector in selectors.get('cookie', []):
        try:
            el = page.query_selector(selector)
            if el:
                logger.info(f"點擊 Cookie/同意按鈕: {selector}")
                el.click()
                return True
        except Exception as e:
            logger.warning(f"點擊 Cookie/同意按鈕 {selector} 失敗: {str(e)}")
    # 處理一般彈窗
    for selector in selectors.get('popup', []):
        try:
            el = page.query_selector(selector)
            if el:
                logger.info(f"點擊關閉彈窗按鈕: {selector}")
                el.click()
                return True
        except Exception as e:
            logger.warning(f"點擊彈窗按鈕 {selector} 失敗: {str(e)}")
    # 處理付費牆
    for selector in selectors.get('paywall', []):
        try:
            el = page.query_selector(selector)
            if el:
                logger.info(f"檢測到付費牆元素: {selector}")
                return True
        except Exception as e:
            logger.warning(f"檢查付費牆 {selector} 失敗: {str(e)}")
    return False

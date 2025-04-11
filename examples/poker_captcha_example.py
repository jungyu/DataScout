"""
撲克牌驗證碼解決器使用示例
"""

from selenium import webdriver
from src.captcha.handlers.poker_captcha import PokerCaptchaSolver
from src.captcha.handlers.advanced_poker_captcha import AdvancedPokerCaptchaSolver
from src.core.utils.logger import setup_logger

def solve_poker_captcha(url, use_advanced=False):
    """
    解決撲克牌驗證碼的示例函數
    
    Args:
        url: 目標網址
        use_advanced: 是否使用高級解決器
    """
    logger = setup_logger('poker_captcha_example')
    driver = None
    
    try:
        # 初始化瀏覽器
        driver = webdriver.Chrome()
        driver.get(url)
        
        # 初始化驗證碼解決器
        if use_advanced:
            solver = AdvancedPokerCaptchaSolver(driver)
        else:
            solver = PokerCaptchaSolver(driver)
        
        # 解決驗證碼
        if solver.solve_captcha():
            logger.info("成功解決驗證碼！")
        else:
            logger.error("解決驗證碼失敗")
        
    except Exception as e:
        logger.error(f"發生錯誤: {str(e)}")
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    # 使用基本解決器
    solve_poker_captcha("https://example.com/captcha")
    
    # 使用高級解決器
    solve_poker_captcha("https://example.com/captcha", use_advanced=True) 
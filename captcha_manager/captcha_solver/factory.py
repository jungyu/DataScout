from typing import Optional, Union

from selenium.webdriver.remote.webdriver import WebDriver
from playwright.sync_api import Page

from .base import BaseCaptchaSolver, CaptchaConfig
from .selenium_solver import SeleniumCaptchaSolver
from .playwright_solver import PlaywrightCaptchaSolver


class CaptchaSolverFactory:
    """驗證碼解決器工廠類"""
    
    @staticmethod
    def create_solver(
        driver: Union[WebDriver, Page],
        config: Optional[CaptchaConfig] = None
    ) -> BaseCaptchaSolver:
        """
        創建驗證碼解決器

        Args:
            driver: Selenium WebDriver 或 Playwright Page 實例
            config: 驗證碼解決器配置

        Returns:
            BaseCaptchaSolver: 驗證碼解決器實例

        Raises:
            ValueError: 如果驅動程序類型不支持
        """
        if isinstance(driver, WebDriver):
            return SeleniumCaptchaSolver(driver, config)
        elif isinstance(driver, Page):
            return PlaywrightCaptchaSolver(driver, config)
        else:
            raise ValueError("Unsupported driver type") 
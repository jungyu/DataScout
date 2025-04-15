from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

from selenium.webdriver.remote.webdriver import WebDriver
from playwright.sync_api import Page


class CaptchaConfig:
    """驗證碼解決器配置類"""
    
    def __init__(
        self,
        api_key: str,
        service: str = "2captcha",
        timeout: int = 120,
        retry_count: int = 3,
        **kwargs
    ):
        """
        初始化配置

        Args:
            api_key: 驗證碼解決服務的 API 密鑰
            service: 驗證碼解決服務名稱
            timeout: 超時時間（秒）
            retry_count: 重試次數
            **kwargs: 其他配置參數
        """
        this.api_key = api_key
        this.service = service
        this.timeout = timeout
        this.retry_count = retry_count
        this.extra_config = kwargs


class BaseCaptchaSolver(ABC):
    """驗證碼解決器基類"""
    
    def __init__(
        self,
        driver: Union[WebDriver, Page],
        config: Optional[CaptchaConfig] = None
    ):
        """
        初始化驗證碼解決器

        Args:
            driver: Selenium WebDriver 或 Playwright Page 實例
            config: 驗證碼解決器配置
        """
        this.driver = driver
        this.config = config or CaptchaConfig(api_key="")

    @abstractmethod
    def solve_recaptcha(
        self,
        site_key: str,
        url: str,
        action: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        解決 reCAPTCHA

        Args:
            site_key: reCAPTCHA 站點密鑰
            url: 網站 URL
            action: reCAPTCHA v3 動作名稱
            **kwargs: 其他參數

        Returns:
            Dict[str, Any]: 解決結果
        """
        pass

    @abstractmethod
    def solve_hcaptcha(
        self,
        site_key: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        解決 hCaptcha

        Args:
            site_key: hCaptcha 站點密鑰
            url: 網站 URL
            **kwargs: 其他參數

        Returns:
            Dict[str, Any]: 解決結果
        """
        pass

    @abstractmethod
    def solve_image_captcha(
        self,
        image_path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        解決圖片驗證碼

        Args:
            image_path: 圖片路徑
            **kwargs: 其他參數

        Returns:
            Dict[str, Any]: 解決結果
        """
        pass

    @abstractmethod
    def solve_slider_captcha(
        self,
        slider_element: Any,
        **kwargs
    ) -> Dict[str, Any]:
        """
        解決滑塊驗證碼

        Args:
            slider_element: 滑塊元素
            **kwargs: 其他參數

        Returns:
            Dict[str, Any]: 解決結果
        """
        pass 
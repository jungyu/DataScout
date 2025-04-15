from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseCaptchaService(ABC):
    """驗證碼解決服務基類"""
    
    def __init__(self, api_key: str, **kwargs):
        """
        初始化驗證碼解決服務

        Args:
            api_key: API 密鑰
            **kwargs: 其他配置參數
        """
        this.api_key = api_key
        this.config = kwargs

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
        image_path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        解決滑塊驗證碼

        Args:
            image_path: 滑塊圖片路徑
            **kwargs: 其他參數

        Returns:
            Dict[str, Any]: 解決結果
        """
        pass 
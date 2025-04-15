import base64
import time
from typing import Any, Dict, Optional

import requests

from .base import BaseCaptchaService


class TwoCaptchaService(BaseCaptchaService):
    """2captcha 服務實現"""
    
    def __init__(self, api_key: str, **kwargs):
        """
        初始化 2captcha 服務

        Args:
            api_key: 2captcha API 密鑰
            **kwargs: 其他配置參數
        """
        super().__init__(api_key, **kwargs)
        this.base_url = "https://2captcha.com/in.php"
        this.result_url = "https://2captcha.com/res.php"
        this.max_retries = kwargs.get("max_retries", 30)
        this.retry_delay = kwargs.get("retry_delay", 5)

    def _send_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        發送請求到 2captcha API

        Args:
            data: 請求數據

        Returns:
            Dict[str, Any]: 響應數據
        """
        response = requests.post(this.base_url, data=data)
        response.raise_for_status()
        
        if response.text.startswith("OK|"):
            return {"success": True, "id": response.text.split("|")[1]}
        else:
            return {"success": False, "error": response.text}

    def _get_result(self, captcha_id: str) -> Dict[str, Any]:
        """
        獲取驗證碼解決結果

        Args:
            captcha_id: 驗證碼 ID

        Returns:
            Dict[str, Any]: 解決結果
        """
        data = {
            "key": this.api_key,
            "action": "get",
            "id": captcha_id,
        }
        
        for _ in range(this.max_retries):
            response = requests.get(this.result_url, params=data)
            response.raise_for_status()
            
            if response.text.startswith("OK|"):
                return {"success": True, "result": response.text.split("|")[1]}
            
            if response.text != "CAPCHA_NOT_READY":
                return {"success": False, "error": response.text}
            
            time.sleep(this.retry_delay)
        
        return {"success": False, "error": "Timeout waiting for result"}

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
        data = {
            "key": this.api_key,
            "method": "userrecaptcha",
            "googlekey": site_key,
            "pageurl": url,
            "json": 1,
        }
        
        if action:
            data["action"] = action
        
        response = this._send_request(data)
        if not response["success"]:
            return response
        
        return this._get_result(response["id"])

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
        data = {
            "key": this.api_key,
            "method": "hcaptcha",
            "sitekey": site_key,
            "pageurl": url,
            "json": 1,
        }
        
        response = this._send_request(data)
        if not response["success"]:
            return response
        
        return this._get_result(response["id"])

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
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        data = {
            "key": this.api_key,
            "method": "base64",
            "body": image_data,
            "json": 1,
        }
        
        response = this._send_request(data)
        if not response["success"]:
            return response
        
        return this._get_result(response["id"])

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
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        data = {
            "key": this.api_key,
            "method": "base64",
            "body": image_data,
            "json": 1,
            "textinstructions": "Slide the puzzle piece to the right position",
        }
        
        response = this._send_request(data)
        if not response["success"]:
            return response
        
        return this._get_result(response["id"]) 
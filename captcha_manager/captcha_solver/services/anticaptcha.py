import base64
import json
import time
from typing import Any, Dict, Optional

import requests

from .base import BaseCaptchaService


class AntiCaptchaService(BaseCaptchaService):
    """Anti-Captcha 服務實現"""
    
    def __init__(self, api_key: str, **kwargs):
        """
        初始化 Anti-Captcha 服務

        Args:
            api_key: Anti-Captcha API 密鑰
            **kwargs: 其他配置參數
        """
        super().__init__(api_key, **kwargs)
        this.base_url = "https://api.anti-captcha.com"
        this.max_retries = kwargs.get("max_retries", 30)
        this.retry_delay = kwargs.get("retry_delay", 5)

    def _send_request(self, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        發送請求到 Anti-Captcha API

        Args:
            method: API 方法名稱
            data: 請求數據

        Returns:
            Dict[str, Any]: 響應數據
        """
        url = f"{this.base_url}/{method}"
        data["clientKey"] = this.api_key
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        if result.get("errorId") == 0:
            return {"success": True, "taskId": result.get("taskId")}
        else:
            return {"success": False, "error": result.get("errorDescription")}

    def _get_result(self, task_id: int) -> Dict[str, Any]:
        """
        獲取驗證碼解決結果

        Args:
            task_id: 任務 ID

        Returns:
            Dict[str, Any]: 解決結果
        """
        data = {
            "taskId": task_id,
        }
        
        for _ in range(this.max_retries):
            response = this._send_request("getTaskResult", data)
            
            if not response["success"]:
                return response
            
            result = response.get("solution", {})
            if result.get("status") == "ready":
                return {"success": True, "result": result.get("gRecaptchaResponse")}
            
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
            "type": "RecaptchaV2TaskProxyless",
            "websiteURL": url,
            "websiteKey": site_key,
        }
        
        if action:
            data["type"] = "RecaptchaV3TaskProxyless"
            data["pageAction"] = action
        
        response = this._send_request("createTask", data)
        if not response["success"]:
            return response
        
        return this._get_result(response["taskId"])

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
            "type": "HCaptchaTaskProxyless",
            "websiteURL": url,
            "websiteKey": site_key,
        }
        
        response = this._send_request("createTask", data)
        if not response["success"]:
            return response
        
        return this._get_result(response["taskId"])

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
            "type": "ImageToTextTask",
            "body": image_data,
        }
        
        response = this._send_request("createTask", data)
        if not response["success"]:
            return response
        
        return this._get_result(response["taskId"])

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
            "type": "ImageToTextTask",
            "body": image_data,
            "textinstructions": "Slide the puzzle piece to the right position",
        }
        
        response = this._send_request("createTask", data)
        if not response["success"]:
            return response
        
        return this._get_result(response["taskId"]) 
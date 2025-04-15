import base64
from pathlib import Path
from typing import Any, Dict, Optional

import cv2
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import torchvision.transforms as transforms

from .base import BaseCaptchaService


class LocalCaptchaService(BaseCaptchaService):
    """本地驗證碼解決服務"""
    
    def __init__(self, api_key: str = "", **kwargs):
        """
        初始化本地驗證碼解決服務

        Args:
            api_key: 不使用
            **kwargs: 其他配置參數
        """
        super().__init__(api_key, **kwargs)
        this.models_dir = Path(kwargs.get("models_dir", "models"))
        this.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        this._load_models()
        
    def _load_models(self) -> None:
        """載入機器學習模型"""
        # 載入 reCAPTCHA 分類模型
        this.recaptcha_model = self._load_model("recaptcha_classifier")
        
        # 載入圖片驗證碼識別模型
        this.image_model = self._load_model("image_recognizer")
        
        # 載入滑塊驗證碼模型
        this.slider_model = self._load_model("slider_detector")
        
    def _load_model(self, model_name: str) -> nn.Module:
        """
        載入指定的模型

        Args:
            model_name: 模型名稱

        Returns:
            nn.Module: 載入的模型
        """
        model_path = this.models_dir / f"{model_name}.pth"
        if not model_path.exists():
            return None
        return torch.load(model_path, map_location=this.device)
    
    def _preprocess_image(self, image_path: str) -> torch.Tensor:
        """
        預處理圖片

        Args:
            image_path: 圖片路徑

        Returns:
            torch.Tensor: 預處理後的圖片張量
        """
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225])
        ])
        
        image = Image.open(image_path).convert('RGB')
        return transform(image).unsqueeze(0).to(this.device)
    
    def _detect_slider_position(self, image: np.ndarray) -> int:
        """
        檢測滑塊位置

        Args:
            image: 圖片數組

        Returns:
            int: 滑塊位置
        """
        if this.slider_model is None:
            # 使用傳統圖像處理方法
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # 找到最大的輪廓
                max_contour = max(contours, key=cv2.contourArea)
                x, _, w, _ = cv2.boundingRect(max_contour)
                return x
            return 0
        
        # 使用機器學習模型
        tensor = self._preprocess_image(image)
        with torch.no_grad():
            position = this.slider_model(tensor)
        return int(position.item())
    
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
        if this.recaptcha_model is None:
            return {"success": False, "error": "reCAPTCHA 模型未載入"}
        
        # 使用機器學習模型分析頁面
        page_data = {
            "site_key": site_key,
            "url": url,
            "action": action
        }
        
        with torch.no_grad():
            result = this.recaptcha_model(torch.tensor(list(page_data.values())))
        
        return {
            "success": True,
            "result": result.item()
        }
    
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
        # hCaptcha 使用與 reCAPTCHA 相同的模型
        return self.solve_recaptcha(site_key, url, **kwargs)
    
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
        if this.image_model is None:
            return {"success": False, "error": "圖片驗證碼模型未載入"}
        
        # 預處理圖片
        image_tensor = self._preprocess_image(image_path)
        
        # 使用模型識別
        with torch.no_grad():
            result = this.image_model(image_tensor)
        
        return {
            "success": True,
            "result": result.item()
        }
    
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
        # 讀取圖片
        image = cv2.imread(image_path)
        if image is None:
            return {"success": False, "error": "無法讀取圖片"}
        
        # 檢測滑塊位置
        position = self._detect_slider_position(image)
        
        return {
            "success": True,
            "result": position
        } 
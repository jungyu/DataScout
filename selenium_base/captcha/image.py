#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
圖像驗證碼處理模組

提供圖像驗證碼的處理功能，包括：
1. 圖像驗證碼檢測
2. 圖像驗證碼識別
3. 圖像驗證碼驗證
"""

import os
import base64
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass
from PIL import Image
import io

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base.base_scraper import BaseScraper
from .base.base_error import CaptchaError, handle_error
from .base.base_config import CaptchaConfig

@dataclass
class ImageCaptchaConfig:
    """圖像驗證碼配置"""
    image_selector: str = "img.captcha-image"
    input_selector: str = "input[type='text']"
    submit_selector: str = "button[type='submit']"
    refresh_selector: str = "button.refresh-captcha"
    error_selector: str = ".error-message"
    success_selector: str = ".success-message"
    max_retries: int = 3
    retry_delay: int = 1
    timeout: int = 10
    image_save_path: str = "temp/captcha"
    min_image_size: int = 100  # 最小圖像尺寸（像素）
    max_image_size: int = 500  # 最大圖像尺寸（像素）

class ImageCaptcha(BaseScraper):
    """圖像驗證碼處理類別"""
    
    def __init__(
        self,
        driver: Any,
        config: Union[Dict[str, Any], CaptchaConfig],
        logger: Optional[Any] = None
    ):
        """
        初始化圖像驗證碼處理類別
        
        Args:
            driver: 瀏覽器驅動程式
            config: 配置字典或配置對象
            logger: 日誌記錄器
        """
        super().__init__(driver, config, logger)
        self.image_config = ImageCaptchaConfig()
        self._ensure_image_dir()
        
    def _ensure_image_dir(self) -> None:
        """確保圖像保存目錄存在"""
        os.makedirs(self.image_config.image_save_path, exist_ok=True)
        
    def setup(self) -> None:
        """設置爬取環境"""
        super().setup()
        self.logger.info("圖像驗證碼處理環境已設置")
        
    def cleanup(self) -> None:
        """清理爬取環境"""
        super().cleanup()
        self.logger.info("圖像驗證碼處理環境已清理")
        
    @handle_error()
    def detect_image_captcha(self) -> bool:
        """
        檢測圖像驗證碼
        
        Returns:
            是否存在圖像驗證碼
        """
        try:
            image_element = self.find_element(By.CSS_SELECTOR, self.image_config.image_selector)
            input_element = self.find_element(By.CSS_SELECTOR, self.image_config.input_selector)
            submit_element = self.find_element(By.CSS_SELECTOR, self.image_config.submit_selector)
            return bool(image_element and input_element and submit_element)
        except NoSuchElementException:
            return False
            
    @handle_error()
    def get_image_captcha(self) -> Optional[str]:
        """
        獲取圖像驗證碼
        
        Returns:
            圖像驗證碼的 base64 編碼
        """
        try:
            image_element = self.find_element(By.CSS_SELECTOR, self.image_config.image_selector)
            
            # 獲取圖像源
            image_src = image_element.get_attribute("src")
            if not image_src:
                return None
                
            # 如果是 base64 編碼的圖像
            if image_src.startswith("data:image"):
                return image_src.split(",")[1]
                
            # 如果是 URL，下載圖像
            return self._download_image(image_src)
            
        except NoSuchElementException:
            return None
            
    def _download_image(self, url: str) -> Optional[str]:
        """
        下載圖像並轉換為 base64
        
        Args:
            url: 圖像 URL
            
        Returns:
            base64 編碼的圖像
        """
        try:
            # 使用 requests 下載圖像
            import requests
            response = requests.get(url)
            if response.status_code == 200:
                return base64.b64encode(response.content).decode()
            return None
        except Exception as e:
            self.logger.error(f"下載圖像失敗：{str(e)}")
            return None
            
    @handle_error()
    def save_image_captcha(self, image_data: str, filename: Optional[str] = None) -> Optional[str]:
        """
        保存圖像驗證碼
        
        Args:
            image_data: base64 編碼的圖像數據
            filename: 文件名（可選）
            
        Returns:
            保存的文件路徑
        """
        try:
            # 解碼 base64 圖像
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # 驗證圖像尺寸
            width, height = image.size
            if width < self.image_config.min_image_size or height < self.image_config.min_image_size:
                self.logger.warning(f"圖像尺寸太小：{width}x{height}")
                return None
                
            if width > self.image_config.max_image_size or height > self.image_config.max_image_size:
                self.logger.warning(f"圖像尺寸太大：{width}x{height}")
                return None
                
            # 生成文件名
            if not filename:
                import time
                filename = f"captcha_{int(time.time())}.png"
                
            # 保存圖像
            filepath = os.path.join(self.image_config.image_save_path, filename)
            image.save(filepath)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"保存圖像失敗：{str(e)}")
            return None
            
    @handle_error()
    def solve_image_captcha(self, text: str) -> bool:
        """
        解決圖像驗證碼
        
        Args:
            text: 驗證碼文本
            
        Returns:
            是否解決成功
        """
        try:
            input_element = self.find_element(By.CSS_SELECTOR, self.image_config.input_selector)
            submit_element = self.find_element(By.CSS_SELECTOR, self.image_config.submit_selector)
            
            self.input_text(input_element, text)
            self.click(submit_element)
            
            return self.verify_image_captcha()
        except Exception as e:
            self.logger.error(f"解決圖像驗證碼失敗：{str(e)}")
            return False
            
    @handle_error()
    def verify_image_captcha(self) -> bool:
        """
        驗證圖像驗證碼
        
        Returns:
            是否驗證成功
        """
        try:
            # 等待錯誤或成功消息
            try:
                error_element = self.wait_for_element(
                    By.CSS_SELECTOR,
                    self.image_config.error_selector,
                    timeout=self.image_config.timeout
                )
                if error_element.is_displayed():
                    return False
            except TimeoutException:
                pass
                
            try:
                success_element = self.wait_for_element(
                    By.CSS_SELECTOR,
                    self.image_config.success_selector,
                    timeout=self.image_config.timeout
                )
                return success_element.is_displayed()
            except TimeoutException:
                return False
                
        except Exception as e:
            self.logger.error(f"驗證圖像驗證碼失敗：{str(e)}")
            return False
            
    @handle_error()
    def refresh_image_captcha(self) -> bool:
        """
        刷新圖像驗證碼
        
        Returns:
            是否刷新成功
        """
        try:
            refresh_button = self.find_element(By.CSS_SELECTOR, self.image_config.refresh_selector)
            self.click(refresh_button)
            
            # 等待新圖像加載
            import time
            time.sleep(1)
            
            return self.detect_image_captcha()
        except NoSuchElementException:
            return False
            
    @handle_error()
    def retry_image_captcha(self, max_retries: Optional[int] = None) -> bool:
        """
        重試圖像驗證碼
        
        Args:
            max_retries: 最大重試次數
            
        Returns:
            是否解決成功
        """
        max_retries = max_retries or self.image_config.max_retries
        
        for i in range(max_retries):
            self.logger.info(f"第 {i + 1} 次嘗試解決圖像驗證碼")
            
            # 獲取並保存圖像
            image_data = self.get_image_captcha()
            if not image_data:
                self.logger.error("獲取圖像驗證碼失敗")
                continue
                
            filepath = self.save_image_captcha(image_data)
            if not filepath:
                self.logger.error("保存圖像驗證碼失敗")
                continue
                
            # TODO: 調用圖像識別 API 或使用 OCR 識別驗證碼
            # 這裡需要實現具體的圖像識別邏輯
            text = "test"  # 臨時使用測試文本
            
            if self.solve_image_captcha(text):
                return True
                
            if i < max_retries - 1:
                self.logger.info(f"等待 {self.image_config.retry_delay} 秒後重試")
                import time
                time.sleep(self.image_config.retry_delay)
                
                # 刷新驗證碼
                self.refresh_image_captcha()
                
        return False
        
    @handle_error()
    def get_image_captcha_error(self) -> Optional[str]:
        """
        獲取圖像驗證碼錯誤信息
        
        Returns:
            錯誤信息
        """
        try:
            error_element = self.find_element(By.CSS_SELECTOR, self.image_config.error_selector)
            return error_element.text if error_element.is_displayed() else None
        except NoSuchElementException:
            return None
            
    @handle_error()
    def get_image_captcha_success(self) -> Optional[str]:
        """
        獲取圖像驗證碼成功信息
        
        Returns:
            成功信息
        """
        try:
            success_element = self.find_element(By.CSS_SELECTOR, self.image_config.success_selector)
            return success_element.text if success_element.is_displayed() else None
        except NoSuchElementException:
            return None 
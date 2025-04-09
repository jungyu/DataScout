#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
圖像驗證碼處理器模組

提供圖像驗證碼的檢測和處理功能，包括：
1. 圖像驗證碼檢測
2. 圖像驗證碼處理
3. 結果處理
"""

import os
import time
import logging
import base64
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..utils import (
    ImageProcessor,
    TextProcessor,
    CaptchaError,
    ImageProcessError,
    TextProcessError,
    handle_error,
    Logger
)

@dataclass
class ImageCaptchaResult:
    """圖像驗證碼處理結果數據類"""
    success: bool
    text: str
    confidence: float
    error: Optional[str] = None
    processing_time: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

class ImageCaptchaHandler:
    """圖像驗證碼處理器類"""
    
    def __init__(
        self,
        driver: WebDriver,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[Logger] = None
    ):
        """
        初始化圖像驗證碼處理器
        
        Args:
            driver: Selenium WebDriver實例
            config: 配置參數
            logger: 日誌記錄器
        """
        self.driver = driver
        self.config = config or {}
        self.logger = logger or Logger('image_captcha')
        
        # 初始化處理器
        self.image_processor = ImageProcessor(self.logger.get_logger())
        self.text_processor = TextProcessor(self.logger.get_logger())
        
        # 設置日誌上下文
        self.logger.add_context(
            handler='image_captcha',
            config=self.config
        )
        
    @handle_error(error_types=(CaptchaError,), retry_count=3)
    def detect_image_captcha(self) -> Optional[WebElement]:
        """
        檢測頁面中的圖像驗證碼
        
        Returns:
            驗證碼圖片元素，如果未找到則返回None
        """
        try:
            # 常見的圖像驗證碼選擇器
            selectors = [
                "//img[contains(@src, 'captcha')]",
                "//img[contains(@id, 'captcha')]",
                "//img[contains(@class, 'captcha')]",
                "//div[contains(@class, 'captcha')]//img"
            ]
            
            # 遍歷選擇器查找驗證碼
            for selector in selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    self.logger.info(f"檢測到圖像驗證碼元素: {selector}")
                    return element
                except:
                    continue
                    
            self.logger.info("未檢測到圖像驗證碼元素")
            return None
            
        except Exception as e:
            self.logger.error(f"圖像驗證碼檢測失敗: {str(e)}")
            raise CaptchaError(f"圖像驗證碼檢測失敗: {str(e)}")
            
    @handle_error(error_types=(CaptchaError,), retry_count=3)
    def solve_image_captcha(self, element: WebElement) -> ImageCaptchaResult:
        """
        解決圖像驗證碼
        
        Args:
            element: 驗證碼圖片元素
            
        Returns:
            處理結果
        """
        start_time = time.time()
        
        try:
            # 獲取圖片數據
            image_data = self._get_image_data(element)
            
            # 預處理圖像
            processed_image = self.image_processor.preprocess_image(image_data)
            
            # 增強圖像
            enhanced_image = self.image_processor.enhance_image(processed_image)
            
            # 分割圖像
            segments = self.image_processor.segment_image(enhanced_image)
            
            # 識別文字
            text = self.image_processor.recognize_text(enhanced_image)
            
            # 計算可信度
            confidence = self.text_processor.calculate_confidence(text)
            
            # 驗證結果
            if not self._validate_result(text, confidence):
                raise TextProcessError("驗證碼識別結果驗證失敗")
            
            return ImageCaptchaResult(
                success=True,
                text=text,
                confidence=confidence,
                processing_time=time.time() - start_time,
                metadata={
                    'segments_count': len(segments),
                    'image_size': enhanced_image.shape
                }
            )
            
        except Exception as e:
            self.logger.error(f"圖像驗證碼處理失敗: {str(e)}")
            return ImageCaptchaResult(
                success=False,
                text='',
                confidence=0.0,
                error=str(e),
                processing_time=time.time() - start_time
            )
            
    def _get_image_data(self, element: WebElement) -> bytes:
        """
        獲取圖片數據
        
        Args:
            element: 圖片元素
            
        Returns:
            圖片數據
        """
        try:
            # 獲取圖片URL
            image_url = element.get_attribute('src')
            
            # 如果是Base64編碼的圖片
            if image_url.startswith('data:image'):
                return base64.b64decode(image_url.split(',')[1])
                
            # 如果是URL
            import requests
            response = requests.get(image_url)
            return response.content
            
        except Exception as e:
            raise ImageProcessError(f"獲取圖片數據失敗: {str(e)}")
            
    def _validate_result(self, text: str, confidence: float) -> bool:
        """
        驗證處理結果
        
        Args:
            text: 識別文本
            confidence: 可信度
            
        Returns:
            是否有效
        """
        try:
            # 檢查文本
            if not self.text_processor.validate_text(text):
                return False
                
            # 檢查可信度
            if confidence < self.config.get('min_confidence', 0.5):
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"結果驗證失敗: {str(e)}")
            return False 
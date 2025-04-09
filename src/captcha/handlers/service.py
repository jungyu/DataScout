#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼服務模組

提供驗證碼處理的核心功能，包括：
1. 驗證碼檢測
2. 驗證碼識別
3. 驗證碼處理
4. 結果驗證
"""

import time
import logging
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..utils.image import ImageProcessor, ImageProcessResult
from ..utils.audio import AudioProcessor, AudioProcessResult
from ..utils.text import TextProcessor, TextProcessResult
from ..utils.error import (
    CaptchaError,
    ImageProcessError,
    AudioProcessError,
    TextProcessError,
    ValidationError,
    handle_error
)

@dataclass
class CaptchaResult:
    """驗證碼處理結果數據類"""
    success: bool
    text: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CaptchaService:
    """驗證碼服務類"""
    
    def __init__(
        self,
        driver: WebDriver,
        logger: Optional[logging.Logger] = None,
        wait_timeout: int = 10,
        retry_count: int = 3,
        retry_delay: float = 1.0
    ):
        """
        初始化驗證碼服務
        
        Args:
            driver: WebDriver實例
            logger: 日誌記錄器
            wait_timeout: 等待超時時間（秒）
            retry_count: 重試次數
            retry_delay: 重試延遲時間（秒）
        """
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        self.wait_timeout = wait_timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        
        # 初始化處理器
        self.image_processor = ImageProcessor(logger=self.logger)
        self.audio_processor = AudioProcessor(logger=self.logger)
        self.text_processor = TextProcessor(logger=self.logger)
        
    @handle_error(error_types=(CaptchaError,))
    def detect_captcha(
        self,
        selectors: List[str],
        timeout: Optional[int] = None
    ) -> Optional[WebElement]:
        """
        檢測驗證碼元素
        
        Args:
            selectors: 選擇器列表
            timeout: 超時時間（秒）
            
        Returns:
            驗證碼元素或None
        """
        try:
            timeout = timeout or self.wait_timeout
            wait = WebDriverWait(self.driver, timeout)
            
            for selector in selectors:
                try:
                    element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    return element
                except:
                    continue
                    
            return None
            
        except Exception as e:
            self.logger.error(f"驗證碼檢測失敗: {str(e)}")
            raise CaptchaError(f"驗證碼檢測失敗: {str(e)}")
            
    @handle_error(error_types=(ImageProcessError,))
    def _get_image_data(self, element: WebElement) -> bytes:
        """
        獲取圖像數據
        
        Args:
            element: 圖像元素
            
        Returns:
            圖像數據
        """
        try:
            # 獲取圖像源
            src = element.get_attribute('src')
            
            if src.startswith('data:image'):
                # Base64編碼的圖像
                import base64
                return base64.b64decode(src.split(',')[1])
            else:
                # URL圖像
                import requests
                response = requests.get(src)
                return response.content
                
        except Exception as e:
            self.logger.error(f"圖像數據獲取失敗: {str(e)}")
            raise ImageProcessError(f"圖像數據獲取失敗: {str(e)}")
            
    @handle_error(error_types=(AudioProcessError,))
    def _get_audio_data(self, element: WebElement) -> bytes:
        """
        獲取音頻數據
        
        Args:
            element: 音頻元素
            
        Returns:
            音頻數據
        """
        try:
            # 獲取音頻源
            src = element.get_attribute('src')
            
            if src.startswith('data:audio'):
                # Base64編碼的音頻
                import base64
                return base64.b64decode(src.split(',')[1])
            else:
                # URL音頻
                import requests
                response = requests.get(src)
                return response.content
                
        except Exception as e:
            self.logger.error(f"音頻數據獲取失敗: {str(e)}")
            raise AudioProcessError(f"音頻數據獲取失敗: {str(e)}")
            
    @handle_error(error_types=(CaptchaError,))
    def solve_image_captcha(
        self,
        element: WebElement,
        min_confidence: float = 0.8
    ) -> CaptchaResult:
        """
        處理圖像驗證碼
        
        Args:
            element: 驗證碼元素
            min_confidence: 最小可信度
            
        Returns:
            處理結果
        """
        try:
            # 獲取圖像數據
            image_data = self._get_image_data(element)
            
            # 處理圖像
            result = self.image_processor.process_image(image_data)
            
            if not result.success:
                return CaptchaResult(
                    success=False,
                    error=result.error
                )
                
            # 處理文本
            text_result = self.text_processor.process_text(result.text)
            
            if not text_result.success:
                return CaptchaResult(
                    success=False,
                    error=text_result.error
                )
                
            # 驗證結果
            if text_result.confidence < min_confidence:
                return CaptchaResult(
                    success=False,
                    error=f"可信度過低: {text_result.confidence}"
                )
                
            return CaptchaResult(
                success=True,
                text=text_result.text,
                confidence=text_result.confidence
            )
            
        except Exception as e:
            self.logger.error(f"圖像驗證碼處理失敗: {str(e)}")
            return CaptchaResult(
                success=False,
                error=str(e)
            )
            
    @handle_error(error_types=(CaptchaError,))
    def solve_audio_captcha(
        self,
        element: WebElement,
        min_confidence: float = 0.8
    ) -> CaptchaResult:
        """
        處理音頻驗證碼
        
        Args:
            element: 驗證碼元素
            min_confidence: 最小可信度
            
        Returns:
            處理結果
        """
        try:
            # 獲取音頻數據
            audio_data = self._get_audio_data(element)
            
            # 處理音頻
            result = self.audio_processor.process_audio(audio_data)
            
            if not result.success:
                return CaptchaResult(
                    success=False,
                    error=result.error
                )
                
            # 處理文本
            text_result = self.text_processor.process_text(result.text)
            
            if not text_result.success:
                return CaptchaResult(
                    success=False,
                    error=text_result.error
                )
                
            # 驗證結果
            if text_result.confidence < min_confidence:
                return CaptchaResult(
                    success=False,
                    error=f"可信度過低: {text_result.confidence}"
                )
                
            return CaptchaResult(
                success=True,
                text=text_result.text,
                confidence=text_result.confidence
            )
            
        except Exception as e:
            self.logger.error(f"音頻驗證碼處理失敗: {str(e)}")
            return CaptchaResult(
                success=False,
                error=str(e)
            )
            
    @handle_error(error_types=(ValidationError,))
    def validate_result(
        self,
        result: CaptchaResult,
        min_confidence: float = 0.8
    ) -> bool:
        """
        驗證處理結果
        
        Args:
            result: 處理結果
            min_confidence: 最小可信度
            
        Returns:
            是否有效
        """
        try:
            # 檢查成功標誌
            if not result.success:
                return False
                
            # 檢查文本
            if not result.text:
                return False
                
            # 檢查可信度
            if result.confidence < min_confidence:
                return False
                
            # 驗證文本
            if not self.text_processor.validate_text(result.text):
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"結果驗證失敗: {str(e)}")
            raise ValidationError(f"結果驗證失敗: {str(e)}") 
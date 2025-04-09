#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
音頻驗證碼處理器模組

提供音頻驗證碼的檢測和處理功能，包括：
1. 音頻驗證碼檢測
2. 音頻驗證碼處理
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
    AudioProcessor,
    TextProcessor,
    CaptchaError,
    AudioProcessError,
    TextProcessError,
    handle_error,
    Logger
)

@dataclass
class AudioCaptchaResult:
    """音頻驗證碼處理結果數據類"""
    success: bool
    text: str
    confidence: float
    error: Optional[str] = None
    processing_time: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

class AudioCaptchaHandler:
    """音頻驗證碼處理器類"""
    
    def __init__(
        self,
        driver: WebDriver,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[Logger] = None
    ):
        """
        初始化音頻驗證碼處理器
        
        Args:
            driver: Selenium WebDriver實例
            config: 配置參數
            logger: 日誌記錄器
        """
        self.driver = driver
        self.config = config or {}
        self.logger = logger or Logger('audio_captcha')
        
        # 初始化處理器
        self.audio_processor = AudioProcessor(self.logger.get_logger())
        self.text_processor = TextProcessor(self.logger.get_logger())
        
        # 設置日誌上下文
        self.logger.add_context(
            handler='audio_captcha',
            config=self.config
        )
        
    @handle_error(error_types=(CaptchaError,), retry_count=3)
    def detect_audio_captcha(self) -> Optional[WebElement]:
        """
        檢測頁面中的音頻驗證碼
        
        Returns:
            驗證碼音頻元素，如果未找到則返回None
        """
        try:
            # 常見的音頻驗證碼選擇器
            selectors = [
                "//audio[contains(@src, 'captcha')]",
                "//audio[contains(@id, 'captcha')]",
                "//audio[contains(@class, 'captcha')]",
                "//div[contains(@class, 'captcha')]//audio",
                "//button[contains(@class, 'audio')]",
                "//a[contains(@class, 'audio')]"
            ]
            
            # 遍歷選擇器查找驗證碼
            for selector in selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    self.logger.info(f"檢測到音頻驗證碼元素: {selector}")
                    return element
                except:
                    continue
                    
            self.logger.info("未檢測到音頻驗證碼元素")
            return None
            
        except Exception as e:
            self.logger.error(f"音頻驗證碼檢測失敗: {str(e)}")
            raise CaptchaError(f"音頻驗證碼檢測失敗: {str(e)}")
            
    @handle_error(error_types=(CaptchaError,), retry_count=3)
    def solve_audio_captcha(self, element: WebElement) -> AudioCaptchaResult:
        """
        解決音頻驗證碼
        
        Args:
            element: 驗證碼音頻元素
            
        Returns:
            處理結果
        """
        start_time = time.time()
        
        try:
            # 如果是按鈕或鏈接，需要點擊以獲取音頻
            if element.tag_name in ['button', 'a']:
                element.click()
                time.sleep(1)  # 等待音頻加載
                
            # 獲取音頻數據
            audio_data = self._get_audio_data(element)
            
            # 預處理音頻
            processed_audio = self.audio_processor.preprocess_audio(audio_data)
            
            # 增強音頻
            enhanced_audio = self.audio_processor.enhance_audio(processed_audio)
            
            # 分割音頻
            segments = self.audio_processor.segment_audio(enhanced_audio)
            
            # 識別語音
            text = self.audio_processor.recognize_speech(enhanced_audio)
            
            # 計算可信度
            confidence = self.text_processor.calculate_confidence(text)
            
            # 驗證結果
            if not self._validate_result(text, confidence):
                raise TextProcessError("驗證碼識別結果驗證失敗")
            
            return AudioCaptchaResult(
                success=True,
                text=text,
                confidence=confidence,
                processing_time=time.time() - start_time,
                metadata={
                    'segments_count': len(segments),
                    'audio_duration': len(enhanced_audio) / 22050  # 假設採樣率為22050
                }
            )
            
        except Exception as e:
            self.logger.error(f"音頻驗證碼處理失敗: {str(e)}")
            return AudioCaptchaResult(
                success=False,
                text='',
                confidence=0.0,
                error=str(e),
                processing_time=time.time() - start_time
            )
            
    def _get_audio_data(self, element: WebElement) -> bytes:
        """
        獲取音頻數據
        
        Args:
            element: 音頻元素
            
        Returns:
            音頻數據
        """
        try:
            # 獲取音頻URL
            audio_url = element.get_attribute('src')
            
            # 如果是Base64編碼的音頻
            if audio_url.startswith('data:audio'):
                return base64.b64decode(audio_url.split(',')[1])
                
            # 如果是URL
            import requests
            response = requests.get(audio_url)
            return response.content
            
        except Exception as e:
            raise AudioProcessError(f"獲取音頻數據失敗: {str(e)}")
            
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
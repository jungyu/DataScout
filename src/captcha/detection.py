#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼檢測模組

提供驗證碼檢測功能，包括：
1. 頁面元素檢測
2. 文本內容檢測
3. 圖像特徵檢測
4. 音頻特徵檢測
"""

import os
import time
import logging
import base64
import re
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum, auto

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

from .config import CaptchaType, CaptchaConfig
from .utils.logger import setup_logger
from .utils.error_handler import retry_on_exception, handle_exception


@dataclass
class CaptchaDetectionResult:
    """驗證碼檢測結果"""
    detected: bool
    captcha_type: CaptchaType
    element: Optional[Any] = None
    text: Optional[str] = None
    confidence: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


class CaptchaDetector:
    """
    驗證碼檢測器，用於檢測頁面上的驗證碼元素。
    支持多種驗證碼類型的檢測，包括圖像、音頻、reCAPTCHA等。
    """
    
    def __init__(
        self,
        driver: webdriver.Remote,
        config: Optional[CaptchaConfig] = None,
        logger: Optional[logging.Logger] = None,
        timeout: int = 10,
        screenshot_dir: str = "captcha_screenshots"
    ):
        """
        初始化驗證碼檢測器
        
        Args:
            driver: Selenium WebDriver實例
            config: 驗證碼配置
            logger: 日誌記錄器
            timeout: 等待超時時間（秒）
            screenshot_dir: 截圖保存目錄
        """
        self.driver = driver
        self.config = config or CaptchaConfig()
        self.logger = logger or logging.getLogger(__name__)
        self.timeout = timeout
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化選擇器
        self._init_selectors()
        
        self.logger.info("驗證碼檢測器初始化完成")
    
    def _init_selectors(self) -> None:
        """初始化選擇器"""
        # 圖像驗證碼選擇器
        self.image_selectors = [
            "//img[contains(@src, 'captcha')]",
            "//img[contains(@src, 'verify')]",
            "//img[contains(@src, 'code')]",
            "//img[contains(@id, 'captcha')]",
            "//img[contains(@id, 'verify')]",
            "//img[contains(@id, 'code')]",
            "//img[contains(@class, 'captcha')]",
            "//img[contains(@class, 'verify')]",
            "//img[contains(@class, 'code')]",
            "//div[contains(@class, 'captcha')]//img",
            "//div[contains(@class, 'verify')]//img",
            "//div[contains(@class, 'code')]//img"
        ]
        
        # 音頻驗證碼選擇器
        self.audio_selectors = [
            "//audio[contains(@src, 'captcha')]",
            "//audio[contains(@src, 'verify')]",
            "//audio[contains(@src, 'code')]",
            "//audio[contains(@id, 'captcha')]",
            "//audio[contains(@id, 'verify')]",
            "//audio[contains(@id, 'code')]",
            "//audio[contains(@class, 'captcha')]",
            "//audio[contains(@class, 'verify')]",
            "//audio[contains(@class, 'code')]",
            "//div[contains(@class, 'captcha')]//audio",
            "//div[contains(@class, 'verify')]//audio",
            "//div[contains(@class, 'code')]//audio"
        ]
        
        # reCAPTCHA 選擇器
        self.recaptcha_selectors = [
            "//iframe[contains(@src, 'recaptcha')]",
            "//div[contains(@class, 'g-recaptcha')]",
            "//div[contains(@class, 'recaptcha')]"
        ]
        
        # hCaptcha 選擇器
        self.hcaptcha_selectors = [
            "//iframe[contains(@src, 'hcaptcha')]",
            "//div[contains(@class, 'h-captcha')]",
            "//div[contains(@class, 'hcaptcha')]"
        ]
        
        # 滑塊驗證碼選擇器
        self.slider_selectors = [
            "//div[contains(@class, 'slider')]",
            "//div[contains(@class, 'slider-captcha')]",
            "//div[contains(@class, 'verify-slider')]",
            "//div[contains(@class, 'verify-move')]"
        ]
        
        # 旋轉驗證碼選擇器
        self.rotate_selectors = [
            "//div[contains(@class, 'rotate')]",
            "//div[contains(@class, 'rotate-captcha')]",
            "//div[contains(@class, 'verify-rotate')]"
        ]
        
        # 點擊驗證碼選擇器
        self.click_selectors = [
            "//div[contains(@class, 'click')]",
            "//div[contains(@class, 'click-captcha')]",
            "//div[contains(@class, 'verify-click')]",
            "//div[contains(@class, 'verify-img')]"
        ]
        
        # 文字驗證碼選擇器
        self.text_selectors = [
            "//input[contains(@name, 'captcha')]",
            "//input[contains(@name, 'verify')]",
            "//input[contains(@name, 'code')]",
            "//input[contains(@id, 'captcha')]",
            "//input[contains(@id, 'verify')]",
            "//input[contains(@id, 'code')]",
            "//input[contains(@class, 'captcha')]",
            "//input[contains(@class, 'verify')]",
            "//input[contains(@class, 'code')]"
        ]
        
        # 驗證碼關鍵詞
        self.captcha_keywords = {
            "captcha": 1.0,
            "verify": 0.9,
            "code": 0.8,
            "security": 0.7,
            "robot": 0.6,
            "human": 0.5,
            "check": 0.4,
            "validation": 0.3
        }
    
    def detect(self, check_text: bool = True) -> CaptchaDetectionResult:
        """
        檢測頁面上是否存在驗證碼
        
        Args:
            check_text: 是否檢查頁面文本
            
        Returns:
            驗證碼檢測結果
        """
        self.logger.info("開始檢測驗證碼")
        
        # 檢查圖像驗證碼
        result = self._detect_image_captcha()
        if result.detected:
            return result
        
        # 檢查音頻驗證碼
        result = self._detect_audio_captcha()
        if result.detected:
            return result
        
        # 檢查 reCAPTCHA
        result = self._detect_recaptcha()
        if result.detected:
            return result
        
        # 檢查 hCaptcha
        result = self._detect_hcaptcha()
        if result.detected:
            return result
        
        # 檢查滑塊驗證碼
        result = self._detect_slider_captcha()
        if result.detected:
            return result
        
        # 檢查旋轉驗證碼
        result = self._detect_rotate_captcha()
        if result.detected:
            return result
        
        # 檢查點擊驗證碼
        result = self._detect_click_captcha()
        if result.detected:
            return result
        
        # 檢查文字驗證碼
        result = self._detect_text_captcha()
        if result.detected:
            return result
        
        # 檢查頁面文本
        if check_text:
            result = self._detect_by_text()
            if result.detected:
                return result
        
        self.logger.info("未檢測到驗證碼")
        return CaptchaDetectionResult(
            detected=False,
            captcha_type=CaptchaType.NONE
        )
    
    def _detect_image_captcha(self) -> CaptchaDetectionResult:
        """檢測圖像驗證碼"""
        self.logger.debug("檢測圖像驗證碼")
        
        for selector in self.image_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    element = elements[0]
                    self.logger.info(f"檢測到圖像驗證碼: {selector}")
                    return CaptchaDetectionResult(
                        detected=True,
                        captcha_type=CaptchaType.IMAGE,
                        element=element,
                        confidence=0.9
                    )
            except Exception as e:
                self.logger.debug(f"檢測圖像驗證碼時發生錯誤: {str(e)}")
        
        return CaptchaDetectionResult(
            detected=False,
            captcha_type=CaptchaType.IMAGE
        )
    
    def _detect_audio_captcha(self) -> CaptchaDetectionResult:
        """檢測音頻驗證碼"""
        self.logger.debug("檢測音頻驗證碼")
        
        for selector in self.audio_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    element = elements[0]
                    self.logger.info(f"檢測到音頻驗證碼: {selector}")
                    return CaptchaDetectionResult(
                        detected=True,
                        captcha_type=CaptchaType.AUDIO,
                        element=element,
                        confidence=0.9
                    )
            except Exception as e:
                self.logger.debug(f"檢測音頻驗證碼時發生錯誤: {str(e)}")
        
        return CaptchaDetectionResult(
            detected=False,
            captcha_type=CaptchaType.AUDIO
        )
    
    def _detect_recaptcha(self) -> CaptchaDetectionResult:
        """檢測 reCAPTCHA"""
        self.logger.debug("檢測 reCAPTCHA")
        
        for selector in self.recaptcha_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    element = elements[0]
                    self.logger.info(f"檢測到 reCAPTCHA: {selector}")
                    return CaptchaDetectionResult(
                        detected=True,
                        captcha_type=CaptchaType.RECAPTCHA,
                        element=element,
                        confidence=0.95
                    )
            except Exception as e:
                self.logger.debug(f"檢測 reCAPTCHA 時發生錯誤: {str(e)}")
        
        return CaptchaDetectionResult(
            detected=False,
            captcha_type=CaptchaType.RECAPTCHA
        )
    
    def _detect_hcaptcha(self) -> CaptchaDetectionResult:
        """檢測 hCaptcha"""
        self.logger.debug("檢測 hCaptcha")
        
        for selector in self.hcaptcha_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    element = elements[0]
                    self.logger.info(f"檢測到 hCaptcha: {selector}")
                    return CaptchaDetectionResult(
                        detected=True,
                        captcha_type=CaptchaType.HCAPTCHA,
                        element=element,
                        confidence=0.95
                    )
            except Exception as e:
                self.logger.debug(f"檢測 hCaptcha 時發生錯誤: {str(e)}")
        
        return CaptchaDetectionResult(
            detected=False,
            captcha_type=CaptchaType.HCAPTCHA
        )
    
    def _detect_slider_captcha(self) -> CaptchaDetectionResult:
        """檢測滑塊驗證碼"""
        self.logger.debug("檢測滑塊驗證碼")
        
        for selector in self.slider_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    element = elements[0]
                    self.logger.info(f"檢測到滑塊驗證碼: {selector}")
                    return CaptchaDetectionResult(
                        detected=True,
                        captcha_type=CaptchaType.SLIDER,
                        element=element,
                        confidence=0.9
                    )
            except Exception as e:
                self.logger.debug(f"檢測滑塊驗證碼時發生錯誤: {str(e)}")
        
        return CaptchaDetectionResult(
            detected=False,
            captcha_type=CaptchaType.SLIDER
        )
    
    def _detect_rotate_captcha(self) -> CaptchaDetectionResult:
        """檢測旋轉驗證碼"""
        self.logger.debug("檢測旋轉驗證碼")
        
        for selector in self.rotate_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    element = elements[0]
                    self.logger.info(f"檢測到旋轉驗證碼: {selector}")
                    return CaptchaDetectionResult(
                        detected=True,
                        captcha_type=CaptchaType.ROTATE,
                        element=element,
                        confidence=0.9
                    )
            except Exception as e:
                self.logger.debug(f"檢測旋轉驗證碼時發生錯誤: {str(e)}")
        
        return CaptchaDetectionResult(
            detected=False,
            captcha_type=CaptchaType.ROTATE
        )
    
    def _detect_click_captcha(self) -> CaptchaDetectionResult:
        """檢測點擊驗證碼"""
        self.logger.debug("檢測點擊驗證碼")
        
        for selector in self.click_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    element = elements[0]
                    self.logger.info(f"檢測到點擊驗證碼: {selector}")
                    return CaptchaDetectionResult(
                        detected=True,
                        captcha_type=CaptchaType.CLICK,
                        element=element,
                        confidence=0.9
                    )
            except Exception as e:
                self.logger.debug(f"檢測點擊驗證碼時發生錯誤: {str(e)}")
        
        return CaptchaDetectionResult(
            detected=False,
            captcha_type=CaptchaType.CLICK
        )
    
    def _detect_text_captcha(self) -> CaptchaDetectionResult:
        """檢測文字驗證碼"""
        self.logger.debug("檢測文字驗證碼")
        
        for selector in self.text_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    element = elements[0]
                    self.logger.info(f"檢測到文字驗證碼: {selector}")
                    return CaptchaDetectionResult(
                        detected=True,
                        captcha_type=CaptchaType.TEXT,
                        element=element,
                        confidence=0.8
                    )
            except Exception as e:
                self.logger.debug(f"檢測文字驗證碼時發生錯誤: {str(e)}")
        
        return CaptchaDetectionResult(
            detected=False,
            captcha_type=CaptchaType.TEXT
        )
    
    def _detect_by_text(self) -> CaptchaDetectionResult:
        """通過頁面文本檢測驗證碼"""
        self.logger.debug("通過頁面文本檢測驗證碼")
        
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            # 計算關鍵詞匹配度
            max_confidence = 0.0
            matched_keyword = None
            
            for keyword, weight in self.captcha_keywords.items():
                if keyword in page_text:
                    if weight > max_confidence:
                        max_confidence = weight
                        matched_keyword = keyword
            
            if matched_keyword and max_confidence > 0.5:
                self.logger.info(f"通過文本檢測到驗證碼，關鍵詞: {matched_keyword}, 置信度: {max_confidence}")
                return CaptchaDetectionResult(
                    detected=True,
                    captcha_type=CaptchaType.UNKNOWN,
                    text=matched_keyword,
                    confidence=max_confidence,
                    details={"keyword": matched_keyword}
                )
        
        except Exception as e:
            self.logger.debug(f"通過文本檢測驗證碼時發生錯誤: {str(e)}")
        
        return CaptchaDetectionResult(
            detected=False,
            captcha_type=CaptchaType.UNKNOWN
        )
    
    def take_screenshot(self, element: Optional[Any] = None, filename: Optional[str] = None) -> Optional[str]:
        """
        截取驗證碼圖片
        
        Args:
            element: 要截圖的元素，如果為None則截取整個頁面
            filename: 文件名，如果為None則自動生成
            
        Returns:
            截圖文件路徑
        """
        try:
            if filename is None:
                timestamp = int(time.time() * 1000)
                filename = f"captcha_{timestamp}.png"
            
            filepath = self.screenshot_dir / filename
            
            if element:
                element.screenshot(str(filepath))
            else:
                self.driver.save_screenshot(str(filepath))
            
            self.logger.info(f"驗證碼截圖已保存: {filepath}")
            return str(filepath)
        
        except Exception as e:
            self.logger.error(f"截取驗證碼圖片時發生錯誤: {str(e)}")
            return None 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼處理模組

提供驗證碼檢測、識別和處理的功能，支援常見驗證碼類型和解決策略。
"""

import os
import time
import logging
import base64
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from datetime import datetime
from enum import Enum

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementNotInteractableException
)

from src.extractors.exceptions import CaptchaDetectedError


class CaptchaType(Enum):
    """驗證碼類型枚舉"""
    RECAPTCHA = "recaptcha"    # Google reCAPTCHA
    HCAPTCHA = "hcaptcha"      # hCaptcha
    IMAGE_CAPTCHA = "image"    # 傳統圖片驗證碼
    SLIDER_CAPTCHA = "slider"  # 滑塊驗證碼
    ROTATE_CAPTCHA = "rotate"  # 旋轉驗證碼
    CLICK_CAPTCHA = "click"    # 點擊驗證碼
    TEXT_CAPTCHA = "text"      # 文字問答驗證碼
    UNKNOWN = "unknown"        # 未知類型


class CaptchaDetectionResult:
    """驗證碼檢測結果類"""
    
    def __init__(
        self, 
        detected: bool = False, 
        captcha_type: CaptchaType = CaptchaType.UNKNOWN,
        element: Optional[Any] = None,
        screenshot_path: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化驗證碼檢測結果
        
        Args:
            detected: 是否檢測到驗證碼
            captcha_type: 驗證碼類型
            element: 驗證碼元素
            screenshot_path: 截圖路徑
            details: 詳細信息
        """
        self.detected = detected
        self.captcha_type = captcha_type
        self.element = element
        self.screenshot_path = screenshot_path
        self.details = details or {}
        self.detection_time = datetime.now()
    
    def __bool__(self):
        """檢測結果布爾值"""
        return self.detected
    
    def __str__(self):
        """檢測結果字符串表示"""
        if not self.detected:
            return "未檢測到驗證碼"
        
        result = f"檢測到 {self.captcha_type.value} 類型驗證碼"
        if self.screenshot_path:
            result += f", 截圖保存於 {self.screenshot_path}"
        
        return result


class CaptchaHandler:
    """驗證碼處理器，用於檢測和處理各種類型的驗證碼"""
    
    def __init__(
        self, 
        driver: webdriver.Remote, 
        logger: Optional[logging.Logger] = None,
        screenshot_dir: str = "captcha_screenshots",
        auto_solve: bool = False,
        service_providers: Optional[Dict[str, Dict[str, str]]] = None,
        custom_strategies: Optional[Dict[CaptchaType, Callable]] = None,
        max_wait_time: int = 60
    ):
        """
        初始化驗證碼處理器
        
        Args:
            driver: Selenium WebDriver實例
            logger: 日誌記錄器
            screenshot_dir: 驗證碼截圖保存目錄
            auto_solve: 是否嘗試自動解決驗證碼
            service_providers: 第三方驗證碼識別服務配置
            custom_strategies: 自定義處理策略
            max_wait_time: 等待驗證碼解決的最大時間(秒)
        """
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        self.screenshot_dir = screenshot_dir
        self.auto_solve = auto_solve
        self.service_providers = service_providers or {}
        self.custom_strategies = custom_strategies or {}
        self.max_wait_time = max_wait_time
        
        # 確保截圖目錄存在
        os.makedirs(screenshot_dir, exist_ok=True)
        
        # 初始化檢測模式
        self._init_detection_patterns()
        
        self.logger.info("驗證碼處理器初始化完成")
    
    def _init_detection_patterns(self) -> None:
        """初始化各類型驗證碼的檢測模式"""
        # reCAPTCHA檢測模式
        self.recaptcha_patterns = {
            "elements": [
                "//iframe[contains(@src, 'recaptcha')]",
                "//div[contains(@class, 'g-recaptcha')]",
                "//div[contains(@class, 'grecaptcha-badge')]"
            ],
            "text_patterns": [
                "recaptcha", "i'm not a robot", "我不是機器人"
            ]
        }
        
        # hCaptcha檢測模式
        self.hcaptcha_patterns = {
            "elements": [
                "//iframe[contains(@src, 'hcaptcha')]",
                "//div[contains(@class, 'h-captcha')]",
            ],
            "text_patterns": [
                "hcaptcha", "human verification", "人機驗證"
            ]
        }
        
        # 圖片驗證碼檢測模式
        self.image_captcha_patterns = {
            "elements": [
                "//img[contains(@src, 'captcha')]",
                "//img[contains(@alt, 'captcha')]",
                "//input[@id='captcha']",
                "//input[contains(@name, 'captcha')]"
            ],
            "text_patterns": [
                "驗證碼", "captcha code", "security code", "驗證碼圖片"
            ]
        }
        
        # 滑塊驗證碼檢測模式
        self.slider_captcha_patterns = {
            "elements": [
                "//div[contains(@class, 'slider')]",
                "//div[contains(@class, 'captcha-puzzle')]",
                "//div[contains(@class, 'drag')]",
                "//div[contains(@class, 'sliderContainer')]"
            ],
            "text_patterns": [
                "拖動滑塊", "滑動驗證", "拖動完成驗證", "slide to verify", "拼圖驗證"
            ]
        }
        
        # 旋轉驗證碼檢測模式
        self.rotate_captcha_patterns = {
            "elements": [
                "//div[contains(@class, 'rotate')]",
                "//img[contains(@class, 'rotate-captcha')]"
            ],
            "text_patterns": [
                "旋轉圖片", "rotate image", "轉動圖片", "旋轉驗證"
            ]
        }
        
        # 點擊驗證碼檢測模式
        self.click_captcha_patterns = {
            "elements": [
                "//div[contains(@class, 'click-captcha')]",
                "//img[contains(@class, 'click-verify')]"
            ],
            "text_patterns": [
                "點擊驗證", "click verification", "點選", "點擊圖片"
            ]
        }
        
        # 文字問答驗證碼檢測模式
        self.text_captcha_patterns = {
            "elements": [
                "//div[contains(@class, 'text-captcha')]",
                "//div[contains(text(), '請回答')]"
            ],
            "text_patterns": [
                "請回答問題", "answer the question", "安全問題", "文字驗證"
            ]
        }
        
        # 通用驗證碼檢測模式
        self.general_captcha_patterns = {
            "elements": [
                "//div[contains(@class, 'captcha')]",
                "//div[contains(@id, 'captcha')]",
                "//div[contains(@class, 'verify')]",
                "//div[contains(@class, 'verification')]"
            ],
            "text_patterns": [
                "captcha", "驗證碼", "人機驗證", "安全驗證", "security verification"
            ]
        }
    
    def detect_captcha(self, check_text: bool = True) -> CaptchaDetectionResult:
        """
        檢測頁面中是否存在驗證碼
        
        Args:
            check_text: 是否檢查頁面文本
            
        Returns:
            驗證碼檢測結果
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return CaptchaDetectionResult()
        
        try:
            # 檢測各類型驗證碼
            detection_methods = [
                (self._detect_recaptcha, CaptchaType.RECAPTCHA),
                (self._detect_hcaptcha, CaptchaType.HCAPTCHA),
                (self._detect_image_captcha, CaptchaType.IMAGE_CAPTCHA),
                (self._detect_slider_captcha, CaptchaType.SLIDER_CAPTCHA),
                (self._detect_rotate_captcha, CaptchaType.ROTATE_CAPTCHA),
                (self._detect_click_captcha, CaptchaType.CLICK_CAPTCHA),
                (self._detect_text_captcha, CaptchaType.TEXT_CAPTCHA),
                (self._detect_general_captcha, CaptchaType.UNKNOWN)
            ]
            
            for detect_method, captcha_type in detection_methods:
                element = detect_method(check_text)
                if element:
                    # 找到驗證碼元素，進行截圖
                    screenshot_path = self._take_captcha_screenshot(captcha_type)
                    
                    # 獲取驗證碼詳細信息
                    details = self._get_captcha_details(element, captcha_type)
                    
                    self.logger.warning(f"檢測到 {captcha_type.value} 類型驗證碼")
                    
                    return CaptchaDetectionResult(
                        detected=True,
                        captcha_type=captcha_type,
                        element=element,
                        screenshot_path=screenshot_path,
                        details=details
                    )
            
            return CaptchaDetectionResult()  # 未檢測到驗證碼
            
        except Exception as e:
            self.logger.error(f"檢測驗證碼時出錯: {str(e)}")
            return CaptchaDetectionResult()
    
    def _detect_recaptcha(self, check_text: bool = True) -> Optional[Any]:
        """檢測Google reCAPTCHA"""
        # 檢查reCAPTCHA元素
        for xpath in self.recaptcha_patterns["elements"]:
            elements = self.driver.find_elements(By.XPATH, xpath)
            if elements and elements[0].is_displayed():
                return elements[0]
        
        # 檢查頁面文本
        if check_text:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            for pattern in self.recaptcha_patterns["text_patterns"]:
                if pattern in page_text:
                    return self.driver.find_element(By.TAG_NAME, "body")
        
        return None
    
    def _detect_hcaptcha(self, check_text: bool = True) -> Optional[Any]:
        """檢測hCaptcha"""
        # 檢查hCaptcha元素
        for xpath in self.hcaptcha_patterns["elements"]:
            elements = self.driver.find_elements(By.XPATH, xpath)
            if elements and elements[0].is_displayed():
                return elements[0]
        
        # 檢查頁面文本
        if check_text:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            for pattern in self.hcaptcha_patterns["text_patterns"]:
                if pattern in page_text:
                    return self.driver.find_element(By.TAG_NAME, "body")
        
        return None
    
    def _detect_image_captcha(self, check_text: bool = True) -> Optional[Any]:
        """檢測傳統圖片驗證碼"""
        # 檢查圖片驗證碼元素
        for xpath in self.image_captcha_patterns["elements"]:
            elements = self.driver.find_elements(By.XPATH, xpath)
            if elements and elements[0].is_displayed():
                return elements[0]
        
        # 檢查頁面文本
        if check_text:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            for pattern in self.image_captcha_patterns["text_patterns"]:
                if pattern in page_text:
                    return self.driver.find_element(By.TAG_NAME, "body")
        
        return None
    
    def _detect_slider_captcha(self, check_text: bool = True) -> Optional[Any]:
        """檢測滑塊驗證碼"""
        # 檢查滑塊驗證碼元素
        for xpath in self.slider_captcha_patterns["elements"]:
            elements = self.driver.find_elements(By.XPATH, xpath)
            if elements and elements[0].is_displayed():
                return elements[0]
        
        # 檢查頁面文本
        if check_text:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            for pattern in self.slider_captcha_patterns["text_patterns"]:
                if pattern in page_text:
                    return self.driver.find_element(By.TAG_NAME, "body")
        
        return None
    
    def _detect_rotate_captcha(self, check_text: bool = True) -> Optional[Any]:
        """檢測旋轉驗證碼"""
        # 檢查旋轉驗證碼元素
        for xpath in self.rotate_captcha_patterns["elements"]:
            elements = self.driver.find_elements(By.XPATH, xpath)
            if elements and elements[0].is_displayed():
                return elements[0]
        
        # 檢查頁面文本
        if check_text:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            for pattern in self.rotate_captcha_patterns["text_patterns"]:
                if pattern in page_text:
                    return self.driver.find_element(By.TAG_NAME, "body")
        
        return None
    
    def _detect_click_captcha(self, check_text: bool = True) -> Optional[Any]:
        """檢測點擊驗證碼"""
        # 檢查點擊驗證碼元素
        for xpath in self.click_captcha_patterns["elements"]:
            elements = self.driver.find_elements(By.XPATH, xpath)
            if elements and elements[0].is_displayed():
                return elements[0]
        
        # 檢查頁面文本
        if check_text:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            for pattern in self.click_captcha_patterns["text_patterns"]:
                if pattern in page_text:
                    return self.driver.find_element(By.TAG_NAME, "body")
        
        return None
    
    def _detect_text_captcha(self, check_text: bool = True) -> Optional[Any]:
        """檢測文字問答驗證碼"""
        # 檢查文字驗證碼元素
        for xpath in self.text_captcha_patterns["elements"]:
            elements = self.driver.find_elements(By.XPATH, xpath)
            if elements and elements[0].is_displayed():
                return elements[0]
        
        # 檢查頁面文本
        if check_text:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            for pattern in self.text_captcha_patterns["text_patterns"]:
                if pattern in page_text:
                    return self.driver.find_element(By.TAG_NAME, "body")
        
        return None
    
    def _detect_general_captcha(self, check_text: bool = True) -> Optional[Any]:
        """檢測通用驗證碼"""
        # 檢查通用驗證碼元素
        for xpath in self.general_captcha_patterns["elements"]:
            elements = self.driver.find_elements(By.XPATH, xpath)
            if elements and elements[0].is_displayed():
                return elements[0]
        
        # 檢查頁面文本
        if check_text:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            for pattern in self.general_captcha_patterns["text_patterns"]:
                if pattern in page_text:
                    return self.driver.find_element(By.TAG_NAME, "body")
        
        return None
    
    def _take_captcha_screenshot(self, captcha_type: CaptchaType) -> str:
        """
        對驗證碼區域進行截圖
        
        Args:
            captcha_type: 驗證碼類型
            
        Returns:
            截圖保存路徑
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{captcha_type.value}_captcha_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            # 截取整個頁面
            self.driver.save_screenshot(filepath)
            self.logger.info(f"驗證碼截圖已保存: {filepath}")
            
            return filepath
        except Exception as e:
            self.logger.error(f"保存驗證碼截圖失敗: {str(e)}")
            return ""
    
    def _get_captcha_details(
        self, 
        element: Any, 
        captcha_type: CaptchaType
    ) -> Dict[str, Any]:
        """
        獲取驗證碼的詳細信息
        
        Args:
            element: 驗證碼元素
            captcha_type: 驗證碼類型
            
        Returns:
            驗證碼詳細信息
        """
        details = {
            "captcha_type": captcha_type.value,
            "url": self.driver.current_url,
            "title": self.driver.title,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # 嘗試獲取元素屬性
            if element:
                details["tag_name"] = element.tag_name
                
                # 獲取常見屬性
                for attr in ["id", "class", "name", "src"]:
                    attr_value = element.get_attribute(attr)
                    if attr_value:
                        details[f"element_{attr}"] = attr_value
            
            # 獲取特定類型的額外信息
            if captcha_type == CaptchaType.RECAPTCHA:
                site_key_element = self.driver.find_elements(
                    By.XPATH, "//div[@class='g-recaptcha' or @data-sitekey]"
                )
                if site_key_element:
                    site_key = site_key_element[0].get_attribute("data-sitekey")
                    if site_key:
                        details["recaptcha_site_key"] = site_key
                
            elif captcha_type == CaptchaType.HCAPTCHA:
                site_key_element = self.driver.find_elements(
                    By.XPATH, "//div[@class='h-captcha' or @data-sitekey]"
                )
                if site_key_element:
                    site_key = site_key_element[0].get_attribute("data-sitekey")
                    if site_key:
                        details["hcaptcha_site_key"] = site_key
            
            elif captcha_type == CaptchaType.IMAGE_CAPTCHA:
                # 嘗試找到驗證碼圖片
                img_elements = self.driver.find_elements(
                    By.XPATH, "//img[contains(@src, 'captcha') or contains(@alt, 'captcha')]"
                )
                if img_elements:
                    details["image_src"] = img_elements[0].get_attribute("src")
                    details["image_alt"] = img_elements[0].get_attribute("alt") or ""
                    
                    # 如果是base64編碼的圖片，不記錄太長的數據
                    if details["image_src"].startswith("data:image"):
                        details["image_src"] = "base64_image"
            
        except Exception as e:
            self.logger.warning(f"獲取驗證碼詳情時出錯: {str(e)}")
        
        return details
    
    def handle_captcha(self) -> Tuple[bool, dict]:
        """
        處理檢測到的驗證碼
        
        Returns:
            (是否成功處理, 處理結果詳情)
        """
        # 檢測驗證碼
        detection_result = self.detect_captcha()
        
        if not detection_result.detected:
            return True, {"message": "未檢測到驗證碼"}
        
        captcha_type = detection_result.captcha_type
        self.logger.warning(f"需要處理 {captcha_type.value} 類型的驗證碼")
        
        result = {
            "captcha_type": captcha_type.value,
            "screenshot_path": detection_result.screenshot_path,
            "details": detection_result.details,
            "message": f"檢測到 {captcha_type.value} 驗證碼"
        }
        
        # 如果不自動解決，則丟出異常或返回
        if not self.auto_solve:
            if self.custom_strategies.get("raise_exception", True):
                raise CaptchaDetectedError(
                    message=f"檢測到 {captcha_type.value} 驗證碼", 
                    page_url=self.driver.current_url
                )
            return False, result
        
        # 根據類型選擇處理策略
        success = False
        start_time = time.time()
        
        try:
            # 檢查是否有自定義處理策略
            if captcha_type in self.custom_strategies:
                self.logger.info(f"使用自定義策略處理 {captcha_type.value} 驗證碼")
                success = self.custom_strategies[captcha_type](self.driver, detection_result)
                
            # 使用內置處理方法
            else:
                if captcha_type == CaptchaType.RECAPTCHA:
                    success = self._handle_recaptcha()
                elif captcha_type == CaptchaType.HCAPTCHA:
                    success = self._handle_hcaptcha()
                elif captcha_type == CaptchaType.IMAGE_CAPTCHA:
                    success = self._handle_image_captcha()
                elif captcha_type == CaptchaType.SLIDER_CAPTCHA:
                    success = self._handle_slider_captcha()
                elif captcha_type == CaptchaType.ROTATE_CAPTCHA:
                    success = self._handle_rotate_captcha()
                elif captcha_type == CaptchaType.CLICK_CAPTCHA:
                    success = self._handle_click_captcha()
                elif captcha_type == CaptchaType.TEXT_CAPTCHA:
                    success = self._handle_text_captcha()
                else:
                    # 通用處理方法，如等待手動處理
                    success = self._handle_manual_captcha()
            
            elapsed_time = time.time() - start_time
            result["elapsed_time"] = elapsed_time
            result["success"] = success
            
            if success:
                result["message"] = f"{captcha_type.value} 驗證碼處理成功"
                self.logger.info(f"{captcha_type.value} 驗證碼處理成功，耗時 {elapsed_time:.1f} 秒")
            else:
                result["message"] = f"{captcha_type.value} 驗證碼處理失敗"
                self.logger.warning(f"{captcha_type.value} 驗證碼處理失敗，耗時 {elapsed_time:.1f} 秒")
            
            return success, result
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.logger.error(f"處理驗證碼時出錯: {str(e)}, 耗時 {elapsed_time:.1f} 秒")
            
            result["elapsed_time"] = elapsed_time
            result["success"] = False
            result["error"] = str(e)
            result["message"] = "處理驗證碼時發生錯誤"
            
            return False, result
    
    def _handle_recaptcha(self) -> bool:
        """處理Google reCAPTCHA"""
        self.logger.info("正在處理reCAPTCHA驗證碼")
        
        # 使用2captcha等第三方服務處理reCAPTCHA
        if "2captcha" in self.service_providers:
            try:
                # 在這裡實現2captcha API調用
                return False  # 暫未實現
            except Exception as e:
                self.logger.error(f"使用2captcha處理reCAPTCHA失敗: {str(e)}")
        
        # 提示手動處理
        self.logger.warning("無法自動處理reCAPTCHA，請手動處理")
        return self._wait_for_detection_to_clear(CaptchaType.RECAPTCHA)
    
    def _handle_hcaptcha(self) -> bool:
        """處理hCaptcha"""
        self.logger.info("正在處理hCaptcha驗證碼")
        
        # 使用第三方服務處理hCaptcha
        if "2captcha" in self.service_providers:
            try:
                # 在這裡實現2captcha API調用
                return False  # 暫未實現
            except Exception as e:
                self.logger.error(f"使用2captcha處理hCaptcha失敗: {str(e)}")
        
        # 提示手動處理
        self.logger.warning("無法自動處理hCaptcha，請手動處理")
        return self._wait_for_detection_to_clear(CaptchaType.HCAPTCHA)
    
    def _handle_image_captcha(self) -> bool:
        """處理傳統圖片驗證碼"""
        self.logger.info("正在處理圖片驗證碼")
        
        # 嘗試找到驗證碼圖片和輸入框
        try:
            img_elements = self.driver.find_elements(
                By.XPATH, "//img[contains(@src, 'captcha') or contains(@alt, 'captcha')]"
            )
            input_elements = self.driver.find_elements(
                By.XPATH, "//input[@id='captcha' or contains(@name, 'captcha')]"
            )
            
            if not img_elements or not input_elements:
                self.logger.warning("找不到完整的圖片驗證碼元素")
                return False
            
            img_element = img_elements[0]
            input_element = input_elements[0]
            
            # 獲取圖片URL
            img_src = img_element.get_attribute("src")
            if not img_src:
                self.logger.warning("無法獲取驗證碼圖片URL")
                return False
                
            # 使用第三方服�務識別驗證碼
            if "2captcha" in self.service_providers:
                try:
                    # 在這裡實現2captcha API調用
                    # 假設獲取到了驗證碼文本
                    captcha_text = "sample_text"  # 替換為實際識別結果
                    
                    # 輸入驗證碼
                    input_element.clear()
                    input_element.send_keys(captcha_text)
                    
                    # 查找提交按鈕並點擊
                    submit_buttons = self.driver.find_elements(
                        By.XPATH, 
                        "//input[@type='submit'] | //button[@type='submit'] | " +
                        "//button[contains(.,'提交') or contains(.,'確定') or " +
                        "contains(.,'Submit') or contains(.,'Confirm')]"
                    )
                    
                    if submit_buttons:
                        submit_buttons[0].click()
                        time.sleep(2)  # 等待提交結果
                        
                        # 驗證是否成功
                        return not self._detect_image_captcha(check_text=False)
                    else:
                        self.logger.warning("找不到驗證碼提交按鈕")
                        return False
                    
                except Exception as e:
                    self.logger.error(f"使用2captcha處理圖片驗證碼失敗: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"處理圖片驗證碼時出錯: {str(e)}")
        
        # 提示手動處理
        self.logger.warning("無法自動處理圖片驗證碼，請手動處理")
        return self._wait_for_detection_to_clear(CaptchaType.IMAGE_CAPTCHA)
    
    def _handle_slider_captcha(self) -> bool:
        """處理滑塊驗證碼"""
        self.logger.info("正在處理滑塊驗證碼")
        
        # 嘗試找到滑塊元素
        try:
            slider_elements = self.driver.find_elements(
                By.XPATH, 
                "//div[contains(@class, 'slider') or contains(@class, 'drag')]"
            )
            
            if not slider_elements:
                self.logger.warning("找不到滑塊元素")
                return False
                
            slider = slider_elements[0]
            
            # 模擬拖動滑塊
            # 此處需要引入ActionChains來實現拖拽操作
            from selenium.webdriver.common.action_chains import ActionChains
            
            actions = ActionChains(self.driver)
            actions.click_and_hold(slider)
            actions.move_by_offset(200, 0)  # 水平移動200px
            actions.release()
            actions.perform()
            
            time.sleep(2)  # 等待驗證結果
            
            # 檢查是否還存在驗證碼
            return not self._detect_slider_captcha(check_text=False)
            
        except Exception as e:
            self.logger.error(f"處理滑塊驗證碼時出錯: {str(e)}")
        
        # 提示手動處理
        self.logger.warning("無法自動處理滑塊驗證碼，請手動處理")
        return self._wait_for_detection_to_clear(CaptchaType.SLIDER_CAPTCHA)
    
    def _handle_rotate_captcha(self) -> bool:
        """處理旋轉驗證碼"""
        self.logger.info("正在處理旋轉驗證碼")
        self.logger.warning("無法自動處理旋轉驗證碼，請手動處理")
        return self._wait_for_detection_to_clear(CaptchaType.ROTATE_CAPTCHA)
    
    def _handle_click_captcha(self) -> bool:
        """處理點擊驗證碼"""
        self.logger.info("正在處理點擊驗證碼")
        self.logger.warning("無法自動處理點擊驗證碼，請手動處理")
        return self._wait_for_detection_to_clear(CaptchaType.CLICK_CAPTCHA)
    
    def _handle_text_captcha(self) -> bool:
        """處理文字問答驗證碼"""
        self.logger.info("正在處理文字問答驗證碼")
        self.logger.warning("無法自動處理文字問答驗證碼，請手動處理")
        return self._wait_for_detection_to_clear(CaptchaType.TEXT_CAPTCHA)
    
    def _handle_manual_captcha(self) -> bool:
        """處理需要手動介入的驗證碼"""
        self.logger.info("需要手動處理驗證碼，請在瀏覽器中完成驗證")
        
        # 等待驗證完成
        wait_time = 0
        interval = 2
        while wait_time < self.max_wait_time:
            # 檢查驗證碼是否已解決
            if not self.detect_captcha(check_text=False).detected:
                self.logger.info("驗證碼已成功解決")
                return True
                
            time.sleep(interval)
            wait_time += interval
            
            if wait_time % 10 == 0:
                self.logger.info(f"已等待 {wait_time} 秒，請完成驗證...")
        
        self.logger.warning(f"等待時間超過 {self.max_wait_time} 秒，驗證未完成")
        return False
    
    def _wait_for_detection_to_clear(self, captcha_type: CaptchaType) -> bool:
        """
        等待指定類型的驗證碼消失
        
        Args:
            captcha_type: 驗證碼類型
            
        Returns:
            是否成功清除
        """
        wait_time = 0
        interval = 2
        detection_method = None
        
        # 選擇對應的檢測方法
        if captcha_type == CaptchaType.RECAPTCHA:
            detection_method = self._detect_recaptcha
        elif captcha_type == CaptchaType.HCAPTCHA:
            detection_method = self._detect_hcaptcha
        elif captcha_type == CaptchaType.IMAGE_CAPTCHA:
            detection_method = self._detect_image_captcha
        elif captcha_type == CaptchaType.SLIDER_CAPTCHA:
            detection_method = self._detect_slider_captcha
        elif captcha_type == CaptchaType.ROTATE_CAPTCHA:
            detection_method = self._detect_rotate_captcha
        elif captcha_type == CaptchaType.CLICK_CAPTCHA:
            detection_method = self._detect_click_captcha
        elif captcha_type == CaptchaType.TEXT_CAPTCHA:
            detection_method = self._detect_text_captcha
        else:
            # 默認使用通用檢測
            detection_method = lambda x: self._detect_general_captcha(x)
        
        # 等待驗證碼消失
        while wait_time < self.max_wait_time:
            # 檢查驗證碼是否已解決
            if not detection_method(check_text=False):
                self.logger.info(f"{captcha_type.value} 驗證碼已成功解決")
                time.sleep(1)  # 短暫等待，確保頁面加載
                return True
                
            time.sleep(interval)
            wait_time += interval
            
            if wait_time % 10 == 0:
                self.logger.info(f"已等待 {wait_time} 秒，請完成 {captcha_type.value} 驗證...")
        
        self.logger.warning(f"等待時間超過 {self.max_wait_time} 秒，{captcha_type.value} 驗證未完成")
        return False
    
    def is_captcha_page(self) -> bool:
        """
        檢查是否是單獨的驗證碼頁面
        
        Returns:
            是否是驗證碼頁面
        """
        detection = self.detect_captcha()
        if not detection.detected:
            return False
            
        # 檢查頁面是否主要是驗證頁面
        try:
            # 檢查頁面標題
            title = self.driver.title.lower()
            captcha_titles = ["captcha", "驗證碼", "verify", "verification", "security check"]
            for t in captcha_titles:
                if t in title:
                    return True
            
            # 檢查頁面主要內容
            body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            word_count = len(body_text.split())
            
            # 如果頁面文字很少且包含驗證相關詞語，可能是驗證頁面
            if word_count < 100:
                captcha_phrases = [
                    "verify you are human", "人機驗證", "安全檢查",
                    "please verify", "請完成驗證", "安全驗證"
                ]
                for phrase in captcha_phrases:
                    if phrase in body_text:
                        return True
                
        except Exception as e:
            self.logger.error(f"檢查驗證碼頁面時出錯: {str(e)}")
        
        return False

    def add_detection_pattern(
        self, 
        captcha_type: CaptchaType, 
        element_xpath: Optional[str] = None,
        text_pattern: Optional[str] = None
    ) -> None:
        """
        添加自定義驗證碼檢測模式
        
        Args:
            captcha_type: 驗證碼類型
            element_xpath: 元素XPath
            text_pattern: 文本模式
        """
        pattern_map = {
            CaptchaType.RECAPTCHA: self.recaptcha_patterns,
            CaptchaType.HCAPTCHA: self.hcaptcha_patterns,
            CaptchaType.IMAGE_CAPTCHA: self.image_captcha_patterns,
            CaptchaType.SLIDER_CAPTCHA: self.slider_captcha_patterns,
            CaptchaType.ROTATE_CAPTCHA: self.rotate_captcha_patterns,
            CaptchaType.CLICK_CAPTCHA: self.click_captcha_patterns,
            CaptchaType.TEXT_CAPTCHA: self.text_captcha_patterns,
            CaptchaType.UNKNOWN: self.general_captcha_patterns
        }
        
        patterns = pattern_map.get(captcha_type)
        if not patterns:
            self.logger.warning(f"未知的驗證碼類型: {captcha_type}")
            return
        
        if element_xpath:
            patterns["elements"].append(element_xpath)
            self.logger.debug(f"已添加 {captcha_type.value} 元素檢測模式: {element_xpath}")
            
        if text_pattern:
            patterns["text_patterns"].append(text_pattern)
            self.logger.debug(f"已添加 {captcha_type.value} 文本檢測模式: {text_pattern}")
    
    def register_custom_handler(
        self, 
        captcha_type: CaptchaType, 
        handler_func: Callable
    ) -> None:
        """
        註冊自定義驗證碼處理器
        
        Args:
            captcha_type: 驗證碼類型
            handler_func: 處理函數，接受driver和detection_result參數
        """
        self.custom_strategies[captcha_type] = handler_func
        self.logger.info(f"已註冊 {captcha_type.value} 類型的自定義處理器")

# 建立便捷函數以在其他模組中使用
def is_captcha_present(driver: webdriver.Remote) -> bool:
    """
    快速檢查頁面是否含有驗證碼
    
    Args:
        driver: WebDriver實例
        
    Returns:
        是否存在驗證碼
    """
    handler = CaptchaHandler(driver)
    return handler.detect_captcha().detected
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文本驗證碼處理模組

提供文本驗證碼的處理功能，包括：
1. 文本驗證碼檢測
2. 文本驗證碼識別
3. 文本驗證碼驗證
"""

import re
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base.base_scraper import BaseScraper
from .base.base_error import CaptchaError, handle_error
from .base.base_config import CaptchaConfig

@dataclass
class TextCaptchaConfig:
    """文本驗證碼配置"""
    input_selector: str = "input[type='text']"
    submit_selector: str = "button[type='submit']"
    error_selector: str = ".error-message"
    success_selector: str = ".success-message"
    max_retries: int = 3
    retry_delay: int = 1
    timeout: int = 10

class TextCaptcha(BaseScraper):
    """文本驗證碼處理類別"""
    
    def __init__(
        self,
        driver: Any,
        config: Union[Dict[str, Any], CaptchaConfig],
        logger: Optional[Any] = None
    ):
        """
        初始化文本驗證碼處理類別
        
        Args:
            driver: 瀏覽器驅動程式
            config: 配置字典或配置對象
            logger: 日誌記錄器
        """
        super().__init__(driver, config, logger)
        self.text_config = TextCaptchaConfig()
        
    def setup(self) -> None:
        """設置爬取環境"""
        super().setup()
        self.logger.info("文本驗證碼處理環境已設置")
        
    def cleanup(self) -> None:
        """清理爬取環境"""
        super().cleanup()
        self.logger.info("文本驗證碼處理環境已清理")
        
    @handle_error()
    def detect_text_captcha(self) -> bool:
        """
        檢測文本驗證碼
        
        Returns:
            是否存在文本驗證碼
        """
        try:
            input_element = self.find_element(By.CSS_SELECTOR, self.text_config.input_selector)
            submit_element = self.find_element(By.CSS_SELECTOR, self.text_config.submit_selector)
            return bool(input_element and submit_element)
        except NoSuchElementException:
            return False
            
    @handle_error()
    def get_text_captcha(self) -> Optional[str]:
        """
        獲取文本驗證碼
        
        Returns:
            文本驗證碼內容
        """
        try:
            input_element = self.find_element(By.CSS_SELECTOR, self.text_config.input_selector)
            return input_element.get_attribute("value")
        except NoSuchElementException:
            return None
            
    @handle_error()
    def solve_text_captcha(self, text: str) -> bool:
        """
        解決文本驗證碼
        
        Args:
            text: 驗證碼文本
            
        Returns:
            是否解決成功
        """
        try:
            input_element = self.find_element(By.CSS_SELECTOR, self.text_config.input_selector)
            submit_element = self.find_element(By.CSS_SELECTOR, self.text_config.submit_selector)
            
            self.input_text(input_element, text)
            self.click(submit_element)
            
            return self.verify_text_captcha()
        except Exception as e:
            self.logger.error(f"解決文本驗證碼失敗：{str(e)}")
            return False
            
    @handle_error()
    def verify_text_captcha(self) -> bool:
        """
        驗證文本驗證碼
        
        Returns:
            是否驗證成功
        """
        try:
            # 等待錯誤或成功消息
            try:
                error_element = self.wait_for_element(
                    By.CSS_SELECTOR,
                    self.text_config.error_selector,
                    timeout=self.text_config.timeout
                )
                if error_element.is_displayed():
                    return False
            except TimeoutException:
                pass
                
            try:
                success_element = self.wait_for_element(
                    By.CSS_SELECTOR,
                    self.text_config.success_selector,
                    timeout=self.text_config.timeout
                )
                return success_element.is_displayed()
            except TimeoutException:
                return False
                
        except Exception as e:
            self.logger.error(f"驗證文本驗證碼失敗：{str(e)}")
            return False
            
    @handle_error()
    def retry_text_captcha(self, max_retries: Optional[int] = None) -> bool:
        """
        重試文本驗證碼
        
        Args:
            max_retries: 最大重試次數
            
        Returns:
            是否解決成功
        """
        max_retries = max_retries or self.text_config.max_retries
        
        for i in range(max_retries):
            self.logger.info(f"第 {i + 1} 次嘗試解決文本驗證碼")
            
            if self.solve_text_captcha("test"):
                return True
                
            if i < max_retries - 1:
                self.logger.info(f"等待 {self.text_config.retry_delay} 秒後重試")
                import time
                time.sleep(self.text_config.retry_delay)
                
        return False
        
    @handle_error()
    def get_text_captcha_error(self) -> Optional[str]:
        """
        獲取文本驗證碼錯誤信息
        
        Returns:
            錯誤信息
        """
        try:
            error_element = self.find_element(By.CSS_SELECTOR, self.text_config.error_selector)
            return error_element.text if error_element.is_displayed() else None
        except NoSuchElementException:
            return None
            
    @handle_error()
    def get_text_captcha_success(self) -> Optional[str]:
        """
        獲取文本驗證碼成功信息
        
        Returns:
            成功信息
        """
        try:
            success_element = self.find_element(By.CSS_SELECTOR, self.text_config.success_selector)
            return success_element.text if success_element.is_displayed() else None
        except NoSuchElementException:
            return None 
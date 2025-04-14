#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
hCaptcha 處理模組

提供 hCaptcha 的處理功能，包括：
1. hCaptcha 檢測
2. hCaptcha 識別
3. hCaptcha 驗證
"""

import os
import time
import json
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base.base_scraper import BaseScraper
from .base.base_error import CaptchaError, handle_error
from .base.base_config import CaptchaConfig

@dataclass
class HCaptchaConfig:
    """hCaptcha 配置"""
    iframe_selector: str = "iframe[title*='hCaptcha']"
    checkbox_selector: str = "#checkbox"
    audio_button_selector: str = "#audio-button"
    audio_source_selector: str = "#audio-source"
    audio_response_selector: str = "#audio-response"
    submit_button_selector: str = "#verify-button"
    error_selector: str = ".error-message"
    success_selector: str = ".success-message"
    max_retries: int = 3
    retry_delay: int = 1
    timeout: int = 10
    audio_save_path: str = "temp/hcaptcha"
    min_audio_duration: float = 1.0  # 最小音頻時長（秒）
    max_audio_duration: float = 30.0  # 最大音頻時長（秒）

class HCaptcha(BaseScraper):
    """hCaptcha 處理類別"""
    
    def __init__(
        self,
        driver: Any,
        config: Union[Dict[str, Any], CaptchaConfig],
        logger: Optional[Any] = None
    ):
        """
        初始化 hCaptcha 處理類別
        
        Args:
            driver: 瀏覽器驅動程式
            config: 配置字典或配置對象
            logger: 日誌記錄器
        """
        super().__init__(driver, config, logger)
        self.hcaptcha_config = HCaptchaConfig()
        self._ensure_audio_dir()
        
    def _ensure_audio_dir(self) -> None:
        """確保音頻保存目錄存在"""
        os.makedirs(self.hcaptcha_config.audio_save_path, exist_ok=True)
        
    def setup(self) -> None:
        """設置爬取環境"""
        super().setup()
        self.logger.info("hCaptcha 處理環境已設置")
        
    def cleanup(self) -> None:
        """清理爬取環境"""
        super().cleanup()
        self.logger.info("hCaptcha 處理環境已清理")
        
    @handle_error()
    def detect_hcaptcha(self) -> bool:
        """
        檢測 hCaptcha
        
        Returns:
            是否存在 hCaptcha
        """
        try:
            iframe = self.find_element(By.CSS_SELECTOR, self.hcaptcha_config.iframe_selector)
            return bool(iframe)
        except NoSuchElementException:
            return False
            
    @handle_error()
    def switch_to_hcaptcha_frame(self) -> bool:
        """
        切換到 hCaptcha iframe
        
        Returns:
            是否切換成功
        """
        try:
            iframe = self.find_element(By.CSS_SELECTOR, self.hcaptcha_config.iframe_selector)
            self.driver.switch_to.frame(iframe)
            return True
        except NoSuchElementException:
            return False
            
    @handle_error()
    def switch_to_default_content(self) -> None:
        """切換回默認內容"""
        self.driver.switch_to.default_content()
        
    @handle_error()
    def click_checkbox(self) -> bool:
        """
        點擊 hCaptcha 複選框
        
        Returns:
            是否點擊成功
        """
        try:
            checkbox = self.find_element(By.CSS_SELECTOR, self.hcaptcha_config.checkbox_selector)
            self.click(checkbox)
            return True
        except NoSuchElementException:
            return False
            
    @handle_error()
    def click_audio_button(self) -> bool:
        """
        點擊音頻按鈕
        
        Returns:
            是否點擊成功
        """
        try:
            audio_button = self.find_element(By.CSS_SELECTOR, self.hcaptcha_config.audio_button_selector)
            self.click(audio_button)
            return True
        except NoSuchElementException:
            return False
            
    @handle_error()
    def get_audio_source(self) -> Optional[str]:
        """
        獲取音頻源
        
        Returns:
            音頻源 URL
        """
        try:
            audio_source = self.find_element(By.CSS_SELECTOR, self.hcaptcha_config.audio_source_selector)
            return audio_source.get_attribute("src")
        except NoSuchElementException:
            return None
            
    @handle_error()
    def download_audio(self, url: str) -> Optional[str]:
        """
        下載音頻
        
        Args:
            url: 音頻 URL
            
        Returns:
            音頻文件路徑
        """
        try:
            # 使用 requests 下載音頻
            import requests
            response = requests.get(url)
            if response.status_code == 200:
                # 生成文件名
                import time
                filename = f"hcaptcha_audio_{int(time.time())}.mp3"
                filepath = os.path.join(self.hcaptcha_config.audio_save_path, filename)
                
                # 保存音頻
                with open(filepath, "wb") as f:
                    f.write(response.content)
                    
                return filepath
            return None
        except Exception as e:
            self.logger.error(f"下載音頻失敗：{str(e)}")
            return None
            
    @handle_error()
    def transcribe_audio(self, filepath: str) -> Optional[str]:
        """
        轉錄音頻
        
        Args:
            filepath: 音頻文件路徑
            
        Returns:
            轉錄文本
        """
        try:
            # TODO: 使用語音識別 API 轉錄音頻
            # 這裡需要實現具體的語音識別邏輯
            return "test"  # 臨時返回測試文本
        except Exception as e:
            self.logger.error(f"轉錄音頻失敗：{str(e)}")
            return None
            
    @handle_error()
    def input_audio_response(self, text: str) -> bool:
        """
        輸入音頻響應
        
        Args:
            text: 響應文本
            
        Returns:
            是否輸入成功
        """
        try:
            audio_response = self.find_element(By.CSS_SELECTOR, self.hcaptcha_config.audio_response_selector)
            self.input_text(audio_response, text)
            return True
        except NoSuchElementException:
            return False
            
    @handle_error()
    def click_verify_button(self) -> bool:
        """
        點擊驗證按鈕
        
        Returns:
            是否點擊成功
        """
        try:
            verify_button = self.find_element(By.CSS_SELECTOR, self.hcaptcha_config.submit_button_selector)
            self.click(verify_button)
            return True
        except NoSuchElementException:
            return False
            
    @handle_error()
    def verify_hcaptcha(self) -> bool:
        """
        驗證 hCaptcha
        
        Returns:
            是否驗證成功
        """
        try:
            # 切換回默認內容
            self.switch_to_default_content()
            
            # 等待錯誤或成功消息
            try:
                error_element = self.wait_for_element(
                    By.CSS_SELECTOR,
                    self.hcaptcha_config.error_selector,
                    timeout=self.hcaptcha_config.timeout
                )
                if error_element.is_displayed():
                    return False
            except TimeoutException:
                pass
                
            try:
                success_element = self.wait_for_element(
                    By.CSS_SELECTOR,
                    self.hcaptcha_config.success_selector,
                    timeout=self.hcaptcha_config.timeout
                )
                return success_element.is_displayed()
            except TimeoutException:
                return False
                
        except Exception as e:
            self.logger.error(f"驗證 hCaptcha 失敗：{str(e)}")
            return False
            
    @handle_error()
    def solve_hcaptcha(self) -> bool:
        """
        解決 hCaptcha
        
        Returns:
            是否解決成功
        """
        try:
            # 切換到 hCaptcha iframe
            if not self.switch_to_hcaptcha_frame():
                return False
                
            # 點擊複選框
            if not self.click_checkbox():
                return False
                
            # 等待音頻按鈕出現
            try:
                audio_button = self.wait_for_element(
                    By.CSS_SELECTOR,
                    self.hcaptcha_config.audio_button_selector,
                    timeout=self.hcaptcha_config.timeout
                )
            except TimeoutException:
                return False
                
            # 點擊音頻按鈕
            if not self.click_audio_button():
                return False
                
            # 獲取音頻源
            audio_url = self.get_audio_source()
            if not audio_url:
                return False
                
            # 下載音頻
            audio_filepath = self.download_audio(audio_url)
            if not audio_filepath:
                return False
                
            # 轉錄音頻
            audio_text = self.transcribe_audio(audio_filepath)
            if not audio_text:
                return False
                
            # 輸入音頻響應
            if not self.input_audio_response(audio_text):
                return False
                
            # 點擊驗證按鈕
            if not self.click_verify_button():
                return False
                
            # 驗證結果
            return self.verify_hcaptcha()
            
        except Exception as e:
            self.logger.error(f"解決 hCaptcha 失敗：{str(e)}")
            return False
            
    @handle_error()
    def retry_hcaptcha(self, max_retries: Optional[int] = None) -> bool:
        """
        重試 hCaptcha
        
        Args:
            max_retries: 最大重試次數
            
        Returns:
            是否解決成功
        """
        max_retries = max_retries or self.hcaptcha_config.max_retries
        
        for i in range(max_retries):
            self.logger.info(f"第 {i + 1} 次嘗試解決 hCaptcha")
            
            if self.solve_hcaptcha():
                return True
                
            if i < max_retries - 1:
                self.logger.info(f"等待 {self.hcaptcha_config.retry_delay} 秒後重試")
                time.sleep(self.hcaptcha_config.retry_delay)
                
        return False
        
    @handle_error()
    def get_hcaptcha_error(self) -> Optional[str]:
        """
        獲取 hCaptcha 錯誤信息
        
        Returns:
            錯誤信息
        """
        try:
            error_element = self.find_element(By.CSS_SELECTOR, self.hcaptcha_config.error_selector)
            return error_element.text if error_element.is_displayed() else None
        except NoSuchElementException:
            return None
            
    @handle_error()
    def get_hcaptcha_success(self) -> Optional[str]:
        """
        獲取 hCaptcha 成功信息
        
        Returns:
            成功信息
        """
        try:
            success_element = self.find_element(By.CSS_SELECTOR, self.hcaptcha_config.success_selector)
            return success_element.text if success_element.is_displayed() else None
        except NoSuchElementException:
            return None 
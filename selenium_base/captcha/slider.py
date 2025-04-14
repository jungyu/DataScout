#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
滑塊驗證碼處理模組

提供滑塊驗證碼的處理功能，包括：
1. 滑塊驗證碼檢測
2. 滑塊驗證碼識別
3. 滑塊驗證碼驗證
"""

import os
import time
import random
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base.base_scraper import BaseScraper
from .base.base_error import CaptchaError, handle_error
from .base.base_config import CaptchaConfig

@dataclass
class SliderCaptchaConfig:
    """滑塊驗證碼配置"""
    slider_selector: str = ".slider-captcha"
    slider_button_selector: str = ".slider-button"
    slider_track_selector: str = ".slider-track"
    slider_image_selector: str = ".slider-image"
    slider_puzzle_selector: str = ".slider-puzzle"
    error_selector: str = ".error-message"
    success_selector: str = ".success-message"
    max_retries: int = 3
    retry_delay: int = 1
    timeout: int = 10
    min_slide_distance: int = 50  # 最小滑動距離（像素）
    max_slide_distance: int = 300  # 最大滑動距離（像素）
    slide_duration: float = 0.5  # 滑動持續時間（秒）
    slide_steps: int = 10  # 滑動步數

class SliderCaptcha(BaseScraper):
    """滑塊驗證碼處理類別"""
    
    def __init__(
        self,
        driver: Any,
        config: Union[Dict[str, Any], CaptchaConfig],
        logger: Optional[Any] = None
    ):
        """
        初始化滑塊驗證碼處理類別
        
        Args:
            driver: 瀏覽器驅動程式
            config: 配置字典或配置對象
            logger: 日誌記錄器
        """
        super().__init__(driver, config, logger)
        self.slider_config = SliderCaptchaConfig()
        
    def setup(self) -> None:
        """設置爬取環境"""
        super().setup()
        self.logger.info("滑塊驗證碼處理環境已設置")
        
    def cleanup(self) -> None:
        """清理爬取環境"""
        super().cleanup()
        self.logger.info("滑塊驗證碼處理環境已清理")
        
    @handle_error()
    def detect_slider_captcha(self) -> bool:
        """
        檢測滑塊驗證碼
        
        Returns:
            是否存在滑塊驗證碼
        """
        try:
            slider_element = self.find_element(By.CSS_SELECTOR, self.slider_config.slider_selector)
            slider_button = self.find_element(By.CSS_SELECTOR, self.slider_config.slider_button_selector)
            slider_track = self.find_element(By.CSS_SELECTOR, self.slider_config.slider_track_selector)
            return bool(slider_element and slider_button and slider_track)
        except NoSuchElementException:
            return False
            
    @handle_error()
    def get_slider_images(self) -> Tuple[Optional[str], Optional[str]]:
        """
        獲取滑塊驗證碼圖片
        
        Returns:
            (背景圖片 base64, 滑塊圖片 base64)
        """
        try:
            slider_image = self.find_element(By.CSS_SELECTOR, self.slider_config.slider_image_selector)
            slider_puzzle = self.find_element(By.CSS_SELECTOR, self.slider_config.slider_puzzle_selector)
            
            # 獲取背景圖片
            image_src = slider_image.get_attribute("src")
            if not image_src:
                return None, None
                
            # 如果是 base64 編碼的圖片
            if image_src.startswith("data:image"):
                image_base64 = image_src.split(",")[1]
            else:
                # 如果是 URL，下載圖片
                image_base64 = self._download_image(image_src)
                
            # 獲取滑塊圖片
            puzzle_src = slider_puzzle.get_attribute("src")
            if not puzzle_src:
                return image_base64, None
                
            # 如果是 base64 編碼的圖片
            if puzzle_src.startswith("data:image"):
                puzzle_base64 = puzzle_src.split(",")[1]
            else:
                # 如果是 URL，下載圖片
                puzzle_base64 = self._download_image(puzzle_src)
                
            return image_base64, puzzle_base64
            
        except NoSuchElementException:
            return None, None
            
    def _download_image(self, url: str) -> Optional[str]:
        """
        下載圖片並轉換為 base64
        
        Args:
            url: 圖片 URL
            
        Returns:
            base64 編碼的圖片
        """
        try:
            # 使用 requests 下載圖片
            import requests
            response = requests.get(url)
            if response.status_code == 200:
                return base64.b64encode(response.content).decode()
            return None
        except Exception as e:
            self.logger.error(f"下載圖片失敗：{str(e)}")
            return None
            
    @handle_error()
    def get_slide_distance(self) -> Optional[int]:
        """
        獲取滑動距離
        
        Returns:
            滑動距離（像素）
        """
        try:
            # TODO: 使用圖像識別算法計算滑動距離
            # 這裡需要實現具體的圖像識別邏輯
            return random.randint(
                self.slider_config.min_slide_distance,
                self.slider_config.max_slide_distance
            )
        except Exception as e:
            self.logger.error(f"計算滑動距離失敗：{str(e)}")
            return None
            
    @handle_error()
    def slide(self, distance: int) -> bool:
        """
        滑動驗證碼
        
        Args:
            distance: 滑動距離（像素）
            
        Returns:
            是否滑動成功
        """
        try:
            slider_button = self.find_element(By.CSS_SELECTOR, self.slider_config.slider_button_selector)
            
            # 計算每一步的距離
            step_distance = distance / self.slider_config.slide_steps
            step_duration = self.slider_config.slide_duration / self.slider_config.slide_steps
            
            # 創建動作鏈
            actions = ActionChains(self.driver)
            actions.click_and_hold(slider_button).perform()
            
            # 分段滑動
            for i in range(self.slider_config.slide_steps):
                # 添加隨機偏移
                offset = random.randint(-2, 2)
                current_distance = step_distance * (i + 1) + offset
                
                # 移動滑塊
                actions.move_by_offset(current_distance, 0).perform()
                time.sleep(step_duration)
                
            # 釋放滑塊
            actions.release().perform()
            
            return True
            
        except Exception as e:
            self.logger.error(f"滑動驗證碼失敗：{str(e)}")
            return False
            
    @handle_error()
    def verify_slider_captcha(self) -> bool:
        """
        驗證滑塊驗證碼
        
        Returns:
            是否驗證成功
        """
        try:
            # 等待錯誤或成功消息
            try:
                error_element = self.wait_for_element(
                    By.CSS_SELECTOR,
                    self.slider_config.error_selector,
                    timeout=self.slider_config.timeout
                )
                if error_element.is_displayed():
                    return False
            except TimeoutException:
                pass
                
            try:
                success_element = self.wait_for_element(
                    By.CSS_SELECTOR,
                    self.slider_config.success_selector,
                    timeout=self.slider_config.timeout
                )
                return success_element.is_displayed()
            except TimeoutException:
                return False
                
        except Exception as e:
            self.logger.error(f"驗證滑塊驗證碼失敗：{str(e)}")
            return False
            
    @handle_error()
    def solve_slider_captcha(self) -> bool:
        """
        解決滑塊驗證碼
        
        Returns:
            是否解決成功
        """
        try:
            # 獲取滑動距離
            distance = self.get_slide_distance()
            if not distance:
                return False
                
            # 滑動驗證碼
            if not self.slide(distance):
                return False
                
            # 驗證結果
            return self.verify_slider_captcha()
            
        except Exception as e:
            self.logger.error(f"解決滑塊驗證碼失敗：{str(e)}")
            return False
            
    @handle_error()
    def retry_slider_captcha(self, max_retries: Optional[int] = None) -> bool:
        """
        重試滑塊驗證碼
        
        Args:
            max_retries: 最大重試次數
            
        Returns:
            是否解決成功
        """
        max_retries = max_retries or self.slider_config.max_retries
        
        for i in range(max_retries):
            self.logger.info(f"第 {i + 1} 次嘗試解決滑塊驗證碼")
            
            if self.solve_slider_captcha():
                return True
                
            if i < max_retries - 1:
                self.logger.info(f"等待 {self.slider_config.retry_delay} 秒後重試")
                time.sleep(self.slider_config.retry_delay)
                
        return False
        
    @handle_error()
    def get_slider_captcha_error(self) -> Optional[str]:
        """
        獲取滑塊驗證碼錯誤信息
        
        Returns:
            錯誤信息
        """
        try:
            error_element = self.find_element(By.CSS_SELECTOR, self.slider_config.error_selector)
            return error_element.text if error_element.is_displayed() else None
        except NoSuchElementException:
            return None
            
    @handle_error()
    def get_slider_captcha_success(self) -> Optional[str]:
        """
        獲取滑塊驗證碼成功信息
        
        Returns:
            成功信息
        """
        try:
            success_element = self.find_element(By.CSS_SELECTOR, self.slider_config.success_selector)
            return success_element.text if success_element.is_displayed() else None
        except NoSuchElementException:
            return None 
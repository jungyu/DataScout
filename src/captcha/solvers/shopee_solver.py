#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
蝦皮網站驗證碼求解器

專門用於處理蝦皮網站的滑動驗證碼。
"""

from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import time
import json
import base64

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)

from .base_solver import BaseSolver
from ..types import CaptchaType, CaptchaConfig, CaptchaResult
from src.core.utils import BrowserUtils, Logger, URLUtils, DataProcessor
from src.core.utils.error_handler import ErrorHandler


class ShopeeSolver(BaseSolver):
    """蝦皮網站驗證碼求解器"""
    
    def __init__(self, config: Optional[CaptchaConfig] = None):
        """
        初始化蝦皮驗證碼求解器
        
        Args:
            config: 驗證碼配置
        """
        super().__init__(config)
        
        # 初始化工具類
        self.browser_utils = BrowserUtils()
        self.logger = Logger(__name__)
        self.url_utils = URLUtils()
        self.data_processor = DataProcessor()
        self.error_handler = ErrorHandler()
        
        # 設置蝦皮特定的配置
        self.shopee_config = {
            'slider_selector': '.shopee-slider__button',
            'slider_track_selector': '.shopee-slider__track',
            'slider_container_selector': '.shopee-slider',
            'success_selector': '.shopee-slider__success',
            'error_selector': '.shopee-slider__error',
            'timeout': 10,  # 等待元素出現的超時時間
            'move_offset': 5,  # 滑動偏移量
            'move_delay': 0.1  # 滑動延遲
        }
    
    def solve(self, driver: WebDriver, element: WebElement) -> CaptchaResult:
        """
        求解蝦皮滑動驗證碼
        
        Args:
            driver: WebDriver實例
            element: 驗證碼元素
            
        Returns:
            CaptchaResult: 驗證碼求解結果
        """
        try:
            # 等待滑塊元素出現
            slider = self.browser_utils.wait_for_element(
                driver,
                By.CSS_SELECTOR,
                self.shopee_config['slider_selector'],
                timeout=self.shopee_config['timeout']
            )
            
            # 獲取滑塊軌道
            track = self.browser_utils.find_element(
                driver,
                By.CSS_SELECTOR,
                self.shopee_config['slider_track_selector']
            )
            
            # 計算滑動距離
            track_width = track.size['width']
            slider_width = slider.size['width']
            distance = track_width - slider_width
            
            # 生成滑動軌跡
            tracks = self._generate_tracks(distance)
            
            # 執行滑動
            success = self._slide(driver, slider, tracks)
            
            if success:
                # 等待成功提示出現
                self.browser_utils.wait_for_element(
                    driver,
                    By.CSS_SELECTOR,
                    self.shopee_config['success_selector'],
                    timeout=self.shopee_config['timeout']
                )
                
                self.logger.info("驗證碼求解成功")
                return CaptchaResult(
                    success=True,
                    message="驗證碼求解成功",
                    solution={"distance": distance, "tracks": tracks}
                )
            else:
                self.logger.error("滑動驗證失敗")
                return CaptchaResult(
                    success=False,
                    message="驗證碼求解失敗",
                    error="滑動驗證失敗"
                )
        
        except TimeoutException:
            self.logger.error("等待元素超時")
            return CaptchaResult(
                success=False,
                message="驗證碼求解失敗",
                error="等待元素超時"
            )
        
        except Exception as e:
            self.error_handler.handle_error(e, "求解驗證碼時發生錯誤")
            return CaptchaResult(
                success=False,
                message="驗證碼求解失敗",
                error=str(e)
            )
    
    def _generate_tracks(self, distance: float) -> list:
        """
        生成滑動軌跡
        
        Args:
            distance: 需要滑動的總距離
            
        Returns:
            list: 滑動軌跡列表
        """
        # 初始化軌跡列表
        tracks = []
        
        # 當前位置
        current = 0
        # 中間位置
        mid = distance * 4 / 5
        # 時間間隔
        t = 0.2
        # 初速度
        v = 0
        
        while current < distance:
            if current < mid:
                # 加速度為正
                a = 2
            else:
                # 加速度為負
                a = -3
            
            # 初速度 v0
            v0 = v
            # 當前速度 v = v0 + at
            v = v0 + a * t
            # 移動距離 x = v0t + 1/2 * a * t^2
            move = v0 * t + 1/2 * a * t * t
            # 當前位置
            current += move
            
            # 加入軌跡
            tracks.append(round(move))
        
        # 返回軌跡列表
        return tracks
    
    def _slide(self, driver: WebDriver, slider: WebElement, tracks: list) -> bool:
        """
        執行滑動操作
        
        Args:
            driver: WebDriver實例
            slider: 滑塊元素
            tracks: 滑動軌跡
            
        Returns:
            bool: 是否滑動成功
        """
        try:
            # 移動到滑塊
            action = driver.action_chains
            action.move_to_element(slider)
            action.click_and_hold().perform()
            
            # 根據軌跡移動
            for track in tracks:
                action.move_by_offset(xoffset=track, yoffset=0).perform()
                time.sleep(self.shopee_config['move_delay'])
            
            # 微調位置
            action.move_by_offset(xoffset=self.shopee_config['move_offset'], yoffset=0).perform()
            action.move_by_offset(xoffset=-self.shopee_config['move_offset'], yoffset=0).perform()
            
            # 釋放滑塊
            time.sleep(0.5)
            action.release().perform()
            
            # 檢查是否成功
            time.sleep(1)
            try:
                success = driver.find_element(By.CSS_SELECTOR, self.shopee_config['success_selector'])
                return True
            except NoSuchElementException:
                return False
        
        except Exception as e:
            self.error_handler.handle_error(e, "執行滑動操作時發生錯誤")
            return False
    
    def _save_screenshot(self, driver: WebDriver, name: str = "captcha") -> Optional[str]:
        """
        保存驗證碼截圖
        
        Args:
            driver: WebDriver實例
            name: 截圖名稱
            
        Returns:
            Optional[str]: 截圖路徑
        """
        try:
            # 獲取驗證碼容器
            container = driver.find_element(By.CSS_SELECTOR, self.shopee_config['slider_container_selector'])
            
            # 生成截圖路徑
            timestamp = int(time.time() * 1000)
            filename = f"{name}_{timestamp}.png"
            filepath = Path(self.solver_config['screenshot_dir']) / filename
            
            # 保存截圖
            container.screenshot(str(filepath))
            
            return str(filepath)
        
        except Exception as e:
            self.error_handler.handle_error(e, "保存驗證碼截圖時發生錯誤")
            return None 
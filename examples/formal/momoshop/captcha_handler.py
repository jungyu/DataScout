#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MomoShop 驗證碼處理器

此模組提供 MomoShop 網站的驗證碼處理功能。
"""

import logging
from typing import Dict, Any, Optional
from playwright.sync_api import Page

from playwright_base import setup_logger

class MomoShopCaptchaHandler:
    """MomoShop 驗證碼處理器"""
    
    def __init__(
        self,
        driver: Page,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化 MomoShop 驗證碼處理器
        
        Args:
            driver: Playwright 頁面實例
            config: 配置字典
            logger: 日誌記錄器
        """
        self.driver = driver
        self.config = config or {}
        self.logger = logger or setup_logger(name=__name__)
        
        self.logger.info("MomoShop 驗證碼處理器已初始化")
        
    def handle_recaptcha(self) -> bool:
        """
        處理 reCAPTCHA 驗證碼
        
        Returns:
            bool: 是否成功
        """
        try:
            self.logger.info("開始處理 reCAPTCHA 驗證碼")
            
            # 檢查是否存在 reCAPTCHA iframe
            recaptcha_frame = self.driver.frame_locator("iframe[title*='reCAPTCHA']")
            if recaptcha_frame.count() == 0:
                self.logger.warning("未找到 reCAPTCHA iframe")
                return False
                
            # 點擊 reCAPTCHA 複選框
            checkbox = recaptcha_frame.locator(".recaptcha-checkbox-border")
            checkbox.click()
            
            # 等待驗證完成
            recaptcha_frame.locator(".recaptcha-checkbox-checked").wait_for(
                timeout=self.config.get("timeout", 30000)
            )
            
            self.logger.info("reCAPTCHA 驗證碼處理成功")
            return True
            
        except Exception as e:
            self.logger.error(f"處理 reCAPTCHA 驗證碼失敗: {str(e)}")
            return False
            
    def handle_image_captcha(self) -> bool:
        """
        處理圖片驗證碼
        
        Returns:
            bool: 是否成功
        """
        try:
            self.logger.info("開始處理圖片驗證碼")
            
            # 檢查是否存在圖片驗證碼
            image_captcha = self.driver.locator("img.captcha-image")
            if image_captcha.count() == 0:
                self.logger.warning("未找到圖片驗證碼")
                return False
                
            # 獲取驗證碼圖片
            image_url = image_captcha.get_attribute("src")
            self.logger.info(f"驗證碼圖片 URL: {image_url}")
            
            # 這裡可以調用驗證碼識別服務
            # 例如：result = self.recognize_captcha(image_url)
            
            # 輸入驗證碼
            input_field = self.driver.locator("input.captcha-input")
            input_field.fill("123456")  # 這裡應該是識別結果
            
            # 提交驗證碼
            submit_button = self.driver.locator("button.captcha-submit")
            submit_button.click()
            
            # 等待驗證結果
            self.driver.wait_for_selector(
                ".captcha-success",
                timeout=self.config.get("timeout", 30000)
            )
            
            self.logger.info("圖片驗證碼處理成功")
            return True
            
        except Exception as e:
            self.logger.error(f"處理圖片驗證碼失敗: {str(e)}")
            return False
            
    def handle_slider_captcha(self) -> bool:
        """
        處理滑塊驗證碼
        
        Returns:
            bool: 是否成功
        """
        try:
            self.logger.info("開始處理滑塊驗證碼")
            
            # 檢查是否存在滑塊驗證碼
            slider = self.driver.locator(".slider-captcha")
            if slider.count() == 0:
                self.logger.warning("未找到滑塊驗證碼")
                return False
                
            # 獲取滑塊和背景圖的位置信息
            slider_box = slider.bounding_box()
            background = self.driver.locator(".slider-background")
            background_box = background.bounding_box()
            
            if not slider_box or not background_box:
                self.logger.error("無法獲取滑塊或背景圖位置信息")
                return False
                
            # 模擬人工滑動
            self.driver.mouse.move(
                slider_box["x"] + slider_box["width"] / 2,
                slider_box["y"] + slider_box["height"] / 2
            )
            self.driver.mouse.down()
            
            # 隨機速度移動到目標位置
            import random
            import time
            
            current_x = slider_box["x"]
            target_x = background_box["x"] + background_box["width"]
            
            while current_x < target_x:
                move_x = min(
                    random.randint(5, 20),
                    target_x - current_x
                )
                current_x += move_x
                
                self.driver.mouse.move(
                    current_x,
                    slider_box["y"] + random.randint(-2, 2)
                )
                time.sleep(random.uniform(0.01, 0.05))
                
            self.driver.mouse.up()
            
            # 等待驗證結果
            self.driver.wait_for_selector(
                ".slider-success",
                timeout=self.config.get("timeout", 30000)
            )
            
            self.logger.info("滑塊驗證碼處理成功")
            return True
            
        except Exception as e:
            self.logger.error(f"處理滑塊驗證碼失敗: {str(e)}")
            return False
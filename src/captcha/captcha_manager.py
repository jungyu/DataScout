#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼管理器模組

提供驗證碼檢測、識別和處理的統一接口。
整合各種驗證碼處理器和第三方服務。
"""

import os
import time
import logging
import base64
import json
import random
from typing import Dict, List, Optional, Any, Union, Tuple, Type, Callable
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..utils.logger import setup_logger
from ..utils.error_handler import retry_on_exception, handle_exception
from .solvers.base_solver import BaseCaptchaSolver
from .third_party.service_client import ThirdPartyServiceClient
from . import CaptchaType
from .detection import CaptchaDetector, CaptchaDetectionResult
from .third_party.config import ThirdPartyServiceConfig
from .solvers import (
    RecaptchaSolver,
    TextSolver,
    SliderSolver,
    RotateSolver,
    ClickSolver
)


class CaptchaManager:
    """
    驗證碼管理器，用於檢測和解決各種類型的驗證碼挑戰。
    支持文本驗證碼、滑塊驗證碼、點擊驗證碼和ReCAPTCHA等。
    """
    
    def __init__(
        self,
        driver: webdriver.Remote,
        logger: Optional[logging.Logger] = None,
        timeout: int = 10,
        screenshot_dir: str = "captcha_screenshots",
        third_party_service: Optional[Union[Dict[str, Any], ThirdPartyServiceConfig]] = None,
        manual_verification: Optional[Callable[[Any], bool]] = None
    ):
        """
        初始化驗證碼管理器
        
        Args:
            driver: Selenium WebDriver實例
            logger: 日誌記錄器
            timeout: 等待超時時間（秒）
            screenshot_dir: 截圖保存目錄
            third_party_service: 第三方驗證服務配置
            manual_verification: 手動驗證函數
        """
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        self.timeout = timeout
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化檢測器
        self.detector = CaptchaDetector(
            driver=driver,
            logger=logger,
            timeout=timeout,
            screenshot_dir=screenshot_dir
        )
        
        # 初始化第三方服務
        if third_party_service:
            if isinstance(third_party_service, dict):
                self.third_party_service = ThirdPartyServiceConfig(**third_party_service)
            else:
                self.third_party_service = third_party_service
        else:
            self.third_party_service = None
        
        # 初始化手動驗證
        self.manual_verification = manual_verification
        
        # 初始化求解器
        self.solvers = {
            CaptchaType.RECAPTCHA: RecaptchaSolver(driver, logger),
            CaptchaType.TEXT_CAPTCHA: TextSolver(driver, logger),
            CaptchaType.SLIDER_CAPTCHA: SliderSolver(driver, logger),
            CaptchaType.ROTATE_CAPTCHA: RotateSolver(driver, logger),
            CaptchaType.CLICK_CAPTCHA: ClickSolver(driver, logger)
        }
        
        # 初始化統計資訊
        self.stats = {
            "total_attempts": 0,
            "successful_solves": 0,
            "failed_solves": 0,
            "manual_solves": 0,
            "third_party_solves": 0
        }
        
        self.logger.info("驗證碼管理器初始化完成")
    
    def detect_captcha(self, check_text: bool = True) -> CaptchaDetectionResult:
        """
        檢測頁面上是否存在驗證碼
        
        Args:
            check_text: 是否檢查頁面文本
            
        Returns:
            驗證碼檢測結果
        """
        return self.detector.detect(check_text)
    
    def solve_captcha(self, detection_result: Optional[CaptchaDetectionResult] = None) -> bool:
        """
        解決驗證碼
        
        Args:
            detection_result: 驗證碼檢測結果，如果為None則自動檢測
            
        Returns:
            是否成功解決驗證碼
        """
        # 更新統計
        self.stats["total_attempts"] += 1
        
        # 如果沒有提供檢測結果，則進行檢測
        if not detection_result:
            detection_result = self.detect_captcha()
        
        # 如果未檢測到驗證碼，返回True
        if not detection_result:
            return True
        
        try:
            # 根據驗證碼類型選擇處理方法
            if detection_result.captcha_type in self.solvers:
                # 使用對應的求解器
                solver = self.solvers[detection_result.captcha_type]
                result = solver.solve(detection_result)
                if result:
                    self.stats["successful_solves"] += 1
                else:
                    self.stats["failed_solves"] += 1
                return result
            
            elif self.third_party_service:
                # 使用第三方服務
                result = self._solve_with_third_party(detection_result)
                if result:
                    self.stats["third_party_solves"] += 1
                else:
                    self.stats["failed_solves"] += 1
                return result
            
            elif self.manual_verification:
                # 使用手動驗證
                result = self.manual_verification(detection_result)
                if result:
                    self.stats["manual_solves"] += 1
                else:
                    self.stats["failed_solves"] += 1
                return result
            
            else:
                self.logger.warning(f"無法處理驗證碼類型: {detection_result.captcha_type}")
                self.stats["failed_solves"] += 1
                return False
            
        except Exception as e:
            self.logger.error(f"解決驗證碼時發生錯誤: {str(e)}")
            self.stats["failed_solves"] += 1
            return False
    
    def _solve_with_third_party(self, detection_result: CaptchaDetectionResult) -> bool:
        """使用第三方服務解決驗證碼"""
        try:
            if not self.third_party_service:
                return False
            
            # 根據驗證碼類型選擇處理方法
            if detection_result.captcha_type == CaptchaType.RECAPTCHA:
                return self._solve_recaptcha_with_third_party(detection_result)
            elif detection_result.captcha_type == CaptchaType.HCAPTCHA:
                return self._solve_hcaptcha_with_third_party(detection_result)
            elif detection_result.captcha_type == CaptchaType.IMAGE_CAPTCHA:
                return self._solve_image_captcha_with_third_party(detection_result)
            else:
                self.logger.warning(f"第三方服務不支持此驗證碼類型: {detection_result.captcha_type}")
                return False
            
        except Exception as e:
            self.logger.error(f"使用第三方服務解決驗證碼時發生錯誤: {str(e)}")
            return False
    
    def _solve_recaptcha_with_third_party(self, detection_result: CaptchaDetectionResult) -> bool:
        """使用第三方服務解決 reCAPTCHA"""
        try:
            if not self.third_party_service or not self.third_party_service.site_key:
                return False
            
            # 使用第三方服務解決 reCAPTCHA
            solver = RecaptchaSolver(self.driver, self.logger)
            return solver.solve_with_third_party(
                detection_result,
                self.third_party_service
            )
            
        except Exception as e:
            self.logger.error(f"使用第三方服務解決 reCAPTCHA 時發生錯誤: {str(e)}")
            return False
    
    def _solve_hcaptcha_with_third_party(self, detection_result: CaptchaDetectionResult) -> bool:
        """使用第三方服務解決 hCaptcha"""
        try:
            if not self.third_party_service or not self.third_party_service.site_key:
                return False
            
            # 使用第三方服務解決 hCaptcha
            solver = RecaptchaSolver(self.driver, self.logger)  # 可以重用 RecaptchaSolver
            return solver.solve_with_third_party(
                detection_result,
                self.third_party_service
            )
            
        except Exception as e:
            self.logger.error(f"使用第三方服務解決 hCaptcha 時發生錯誤: {str(e)}")
            return False
    
    def _solve_image_captcha_with_third_party(self, detection_result: CaptchaDetectionResult) -> bool:
        """使用第三方服務解決圖片驗證碼"""
        try:
            if not self.third_party_service:
                return False
            
            # 使用第三方服務解決圖片驗證碼
            solver = TextSolver(self.driver, self.logger)
            return solver.solve_with_third_party(
                detection_result,
                self.third_party_service
            )
            
        except Exception as e:
            self.logger.error(f"使用第三方服務解決圖片驗證碼時發生錯誤: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """獲取統計信息"""
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """重置統計信息"""
        self.stats = {
            "total_attempts": 0,
            "successful_solves": 0,
            "failed_solves": 0,
            "manual_solves": 0,
            "third_party_solves": 0
        }
    
    def _load_solvers(self):
        """載入驗證碼解決器"""
        # 動態載入解決器
        solver_types = {
            "text": self._load_solver_class(".solvers.text_solver", "TextCaptchaSolver"),
            "slider": self._load_solver_class(".solvers.slider_solver", "SliderCaptchaSolver"),
            "click": self._load_solver_class(".solvers.click_solver", "ClickCaptchaSolver"),
            "recaptcha": self._load_solver_class(".solvers.recaptcha_solver", "ReCaptchaSolver")
        }
        
        # 初始化解決器
        for solver_type, solver_class in solver_types.items():
            if solver_class:
                solver_config = self.config.get(f"{solver_type}_solver_config", {})
                self.solvers[solver_type] = solver_class(solver_config)
                self.logger.info(f"已載入 {solver_type} 驗證碼解決器")
    
    def _load_solver_class(self, module_path: str, class_name: str) -> Optional[Type[BaseCaptchaSolver]]:
        """
        動態載入驗證碼解決器類
        
        Args:
            module_path: 模塊路徑
            class_name: 類名
            
        Returns:
            解決器類或None
        """
        try:
            import importlib
            
            # 完整的模塊路徑
            full_module_path = f"{__package__}{module_path}"
            
            # 導入模塊
            module = importlib.import_module(full_module_path)
            
            # 獲取類
            solver_class = getattr(module, class_name)
            
            return solver_class
        
        except (ImportError, AttributeError) as e:
            self.logger.warning(f"載入驗證碼解決器類 {class_name} 失敗: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"載入驗證碼解決器類時發生錯誤: {str(e)}")
            return None
    
    def _save_captcha_sample(self, driver: webdriver.Remote, captcha_type: str):
        """
        保存驗證碼樣本
        
        Args:
            driver: WebDriver實例
            captcha_type: 驗證碼類型
        """
        try:
            # 創建樣本目錄
            sample_type_dir = os.path.join(self.sample_dir, captcha_type)
            os.makedirs(sample_type_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = int(time.time())
            sample_file = os.path.join(sample_type_dir, f"{captcha_type}_{timestamp}")
            
            if captcha_type == "text":
                # 查找驗證碼圖片
                img_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'captcha')]")
                if not img_elements:
                    return
                
                img_element = img_elements[0]
                img_url = img_element.get_attribute("src")
                
                # 保存圖片
                if img_url.startswith('data:image'):
                    # Base64圖片
                    base64_data = img_url.split(',')[1]
                    with open(f"{sample_file}.png", "wb") as f:
                        f.write(base64.b64decode(base64_data))
                else:
                    # URL圖片
                    import requests
                    response = requests.get(img_url)
                    with open(f"{sample_file}.png", "wb") as f:
                        f.write(response.content)
                
                self.logger.debug(f"已保存文本驗證碼樣本: {sample_file}.png")
            
            elif captcha_type == "slider":
                # 保存背景圖片和滑塊圖片
                background_img = driver.find_element(By.XPATH, "//div[contains(@class, 'slider')]/img")
                bg_url = background_img.get_attribute("src")
                
                if bg_url.startswith('data:image'):
                    # Base64圖片
                    base64_data = bg_url.split(',')[1]
                    with open(f"{sample_file}_bg.png", "wb") as f:
                        f.write(base64.b64decode(base64_data))
                else:
                    # URL圖片
                    import requests
                    response = requests.get(bg_url)
                    with open(f"{sample_file}_bg.png", "wb") as f:
                        f.write(response.content)
                
                # 保存整個驗證碼區域的截圖
                slider_container = driver.find_element(By.XPATH, "//div[contains(@class, 'slider')]")
                slider_container.screenshot(f"{sample_file}_full.png")
                
                self.logger.debug(f"已保存滑塊驗證碼樣本: {sample_file}_bg.png, {sample_file}_full.png")
            
            elif captcha_type == "click":
                # 保存點擊驗證碼圖片
                img_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'imgCaptcha')]/img")
                if not img_elements:
                    return
                
                img_element = img_elements[0]
                img_url = img_element.get_attribute("src")
                
                # 保存圖片
                if img_url.startswith('data:image'):
                    # Base64圖片
                    base64_data = img_url.split(',')[1]
                    with open(f"{sample_file}.png", "wb") as f:
                        f.write(base64.b64decode(base64_data))
                else:
                    # URL圖片
                    import requests
                    response = requests.get(img_url)
                    with open(f"{sample_file}.png", "wb") as f:
                        f.write(response.content)
                
                # 保存提示文本
                hint_elements = driver.find_elements(By.XPATH, "//div[contains(text(), '點擊圖片中的')]")
                if hint_elements:
                    hint_text = hint_elements[0].text
                    with open(f"{sample_file}.txt", "w", encoding="utf-8") as f:
                        f.write(hint_text)
                
                self.logger.debug(f"已保存點擊驗證碼樣本: {sample_file}.png")
            
            elif captcha_type == "recaptcha":
                # 保存ReCAPTCHA信息
                recaptcha_elements = driver.find_elements(By.XPATH, "//div[@class='g-recaptcha']")
                if not recaptcha_elements:
                    return
                
                # 獲取site-key
                site_key = recaptcha_elements[0].get_attribute("data-sitekey")
                page_url = driver.current_url
                
                # 保存信息
                info = {
                    "site_key": site_key,
                    "page_url": page_url,
                    "timestamp": timestamp
                }
                
                with open(f"{sample_file}.json", "w", encoding="utf-8") as f:
                    json.dump(info, f, indent=2)
                
                # 保存截圖
                recaptcha_elements[0].screenshot(f"{sample_file}.png")
                
                self.logger.debug(f"已保存ReCAPTCHA樣本: {sample_file}.json, {sample_file}.png")
        
        except Exception as e:
            self.logger.error(f"保存驗證碼樣本失敗: {str(e)}")
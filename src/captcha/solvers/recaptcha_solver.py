#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
reCAPTCHA 驗證碼解決器模組

提供 reCAPTCHA 驗證碼的解決功能，支持：
1. reCAPTCHA v2 勾選框
2. reCAPTCHA v2 隱形
3. reCAPTCHA v3
"""

import time
import os
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from pathlib import Path

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

from src.core.utils import (
    BrowserUtils,
    Logger,
    URLUtils,
    DataProcessor,
    ErrorHandler,
    ConfigUtils,
    ImageUtils,
    AudioUtils,
    TextUtils,
    CookieManager
)

from .base_solver import BaseSolver
from ..types import CaptchaResult


class RecaptchaSolver(BaseSolver):
    """reCAPTCHA 驗證碼解決器"""
    
    def __init__(self, browser: WebDriver, config: Dict[str, Any]):
        """
        初始化 reCAPTCHA 解決器
        
        Args:
            browser: WebDriver 實例
            config: 配置字典
        """
        super().__init__(browser, config)
        
        # 初始化特定配置
        self._init_recaptcha()
        
    def _init_recaptcha(self):
        """初始化 reCAPTCHA 特定配置"""
        try:
            # 設置超時和重試
            self.timeout = self.config.get('timeout', 30)
            self.retry_count = self.config.get('retry_count', 3)
            self.retry_delay = self.config.get('retry_delay', 1.0)
            
            # 設置目錄
            self.temp_dir = self.config.get('temp_dir', 'temp')
            self.result_dir = self.config.get('result_dir', 'results')
            self.audio_dir = self.config.get('audio_dir', 'audio')
            
            # 創建目錄
            for dir_path in [self.temp_dir, self.result_dir, self.audio_dir]:
                os.makedirs(dir_path, exist_ok=True)
                
            # 設置選擇器
            self.selectors = {
                'v2_checkbox': [
                    "iframe[src*='google.com/recaptcha']",
                    "div.g-recaptcha",
                    "div[class*='recaptcha']",
                    "iframe[title='reCAPTCHA']"
                ],
                'v2_invisible': [
                    "div.g-recaptcha[data-size='invisible']",
                    "div[class*='recaptcha'][data-size='invisible']"
                ],
                'v3': [
                    "script[src*='google.com/recaptcha/api.js']"
                ]
            }
            
            # 初始化狀態
            self.solver_status = {
                'current_version': None,
                'retry_count': 0,
                'success_count': 0,
                'failure_count': 0,
                'start_time': None,
                'end_time': None,
                'duration': None
            }
            
        except Exception as e:
            self.logger.error(f"初始化 reCAPTCHA 失敗: {str(e)}")
            raise
            
    def solve(self, element: WebElement) -> CaptchaResult:
        """
        解決 reCAPTCHA 驗證碼
        
        Args:
            element: 驗證碼元素
            
        Returns:
            CaptchaResult: 驗證碼結果
        """
        try:
            # 更新狀態
            self.solver_status['start_time'] = datetime.now()
            
            # 檢測版本
            version = self._detect_version(element)
            self.solver_status['current_version'] = version
            self.logger.info(f"檢測到 reCAPTCHA 版本: {version}")
            
            # 根據版本解決
            if version == 'v2_checkbox':
                result = self._solve_v2_checkbox(element)
            elif version == 'v2_invisible':
                result = self._solve_v2_invisible(element)
            elif version == 'v3':
                result = self._solve_v3(element)
            else:
                raise Exception(f"不支持的 reCAPTCHA 版本: {version}")
                
            # 更新狀態
            self.solver_status['end_time'] = datetime.now()
            self.solver_status['duration'] = (
                self.solver_status['end_time'] - 
                self.solver_status['start_time']
            ).total_seconds()
            
            if result.success:
                self.solver_status['success_count'] += 1
            else:
                self.solver_status['failure_count'] += 1
                
            return result
            
        except Exception as e:
            self.logger.error(f"解決 reCAPTCHA 失敗: {str(e)}")
            return CaptchaResult(
                success=False,
                error=str(e)
            )
            
    def _detect_version(self, element: WebElement) -> str:
        """
        檢測 reCAPTCHA 版本
        
        Args:
            element: 驗證碼元素
            
        Returns:
            str: 版本類型
        """
        try:
            # 檢查元素屬性
            if element.get_attribute('data-size') == 'invisible':
                return 'v2_invisible'
                
            # 檢查是否有 checkbox
            iframes = self.browser_utils.find_elements(
                self.browser,
                By.CSS_SELECTOR,
                "iframe[src*='google.com/recaptcha']"
            )
            
            if iframes:
                # 未處於 iframe 內
                main_frame = self.browser.current_window_handle
                for iframe in iframes:
                    try:
                        self.browser.switch_to.frame(iframe)
                        checkbox = self.browser_utils.find_elements(
                            self.browser,
                            By.CSS_SELECTOR,
                            ".recaptcha-checkbox-border"
                        )
                        if checkbox:
                            self.browser.switch_to.window(main_frame)
                            return 'v2_checkbox'
                    except:
                        pass
                    finally:
                        self.browser.switch_to.window(main_frame)
                        
            # 檢查是否為 v3
            scripts = self.browser_utils.find_elements(
                self.browser,
                By.CSS_SELECTOR,
                "script[src*='google.com/recaptcha/api.js']"
            )
            
            for script in scripts:
                src = script.get_attribute('src')
                if 'render=' in src:
                    return 'v3'
                    
            # 預設為 v2 checkbox
            return 'v2_checkbox'
            
        except Exception as e:
            self.logger.error(f"檢測 reCAPTCHA 版本失敗: {str(e)}")
            return 'v2_checkbox'
            
    def _solve_v2_checkbox(self, element: WebElement) -> CaptchaResult:
        """
        解決 reCAPTCHA v2 勾選框版本
        
        Args:
            element: 驗證碼元素
            
        Returns:
            CaptchaResult: 驗證碼結果
        """
        try:
            # 獲取網站密鑰
            site_key = element.get_attribute('data-sitekey')
            if not site_key:
                raise Exception("無法獲取網站密鑰")
                
            # 獲取 iframe
            iframe = self.browser_utils.find_element(
                self.browser,
                By.CSS_SELECTOR,
                "iframe[src*='google.com/recaptcha']"
            )
            if not iframe:
                raise Exception("無法找到 reCAPTCHA iframe")
                
            # 切換到 iframe
            self.browser.switch_to.frame(iframe)
            
            # 點擊勾選框
            checkbox = self.browser_utils.find_element(
                self.browser,
                By.CSS_SELECTOR,
                ".recaptcha-checkbox-border"
            )
            if not checkbox:
                raise Exception("無法找到勾選框")
                
            checkbox.click()
            
            # 切換回主框架
            self.browser.switch_to.default_content()
            
            # 等待驗證完成
            for _ in range(self.retry_count):
                time.sleep(self.retry_delay)
                
                # 檢查是否驗證成功
                if self._check_success(element):
                    return CaptchaResult(
                        success=True,
                        solution="v2_checkbox_solved",
                        duration=time.time() - self.solver_status['start_time'].timestamp()
                    )
                    
            raise Exception("驗證超時")
            
        except Exception as e:
            self.logger.error(f"解決 reCAPTCHA v2 勾選框失敗: {str(e)}")
            return CaptchaResult(
                success=False,
                error=str(e)
            )
            
    def _solve_v2_invisible(self, element: WebElement) -> CaptchaResult:
        """
        解決 reCAPTCHA v2 隱形版本
        
        Args:
            element: 驗證碼元素
            
        Returns:
            CaptchaResult: 驗證碼結果
        """
        try:
            # 獲取網站密鑰
            site_key = element.get_attribute('data-sitekey')
            if not site_key:
                raise Exception("無法獲取網站密鑰")
                
            # 觸發驗證
            self.browser.execute_script(
                "document.querySelector('[data-sitekey]').click()"
            )
            
            # 等待驗證完成
            for _ in range(self.retry_count):
                time.sleep(self.retry_delay)
                
                # 檢查是否驗證成功
                if self._check_success(element):
                    return CaptchaResult(
                        success=True,
                        solution="v2_invisible_solved",
                        duration=time.time() - self.solver_status['start_time'].timestamp()
                    )
                    
            raise Exception("驗證超時")
            
        except Exception as e:
            self.logger.error(f"解決 reCAPTCHA v2 隱形失敗: {str(e)}")
            return CaptchaResult(
                success=False,
                error=str(e)
            )
            
    def _solve_v3(self, element: WebElement) -> CaptchaResult:
        """
        解決 reCAPTCHA v3
        
        Args:
            element: 驗證碼元素
            
        Returns:
            CaptchaResult: 驗證碼結果
        """
        try:
            # 獲取網站密鑰
            site_key = element.get_attribute('data-sitekey')
            if not site_key:
                raise Exception("無法獲取網站密鑰")
                
            # 觸發驗證
            self.browser.execute_script(
                "grecaptcha.execute(arguments[0], {action: 'verify'})",
                site_key
            )
            
            # 等待驗證完成
            for _ in range(self.retry_count):
                time.sleep(self.retry_delay)
                
                # 檢查是否驗證成功
                if self._check_success(element):
                    return CaptchaResult(
                        success=True,
                        solution="v3_solved",
                        duration=time.time() - self.solver_status['start_time'].timestamp()
                    )
                    
            raise Exception("驗證超時")
            
        except Exception as e:
            self.logger.error(f"解決 reCAPTCHA v3 失敗: {str(e)}")
            return CaptchaResult(
                success=False,
                error=str(e)
            )
            
    def _check_success(self, element: WebElement) -> bool:
        """
        檢查驗證是否成功
        
        Args:
            element: 驗證碼元素
            
        Returns:
            bool: 是否成功
        """
        try:
            # 檢查是否有成功標記
            if element.get_attribute('data-success'):
                return True
                
            # 檢查是否有 token
            if self.browser.execute_script(
                "return grecaptcha.getResponse(arguments[0])",
                element.get_attribute('data-sitekey')
            ):
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"檢查驗證結果失敗: {str(e)}")
            return False
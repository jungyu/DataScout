#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼管理模組

提供驗證碼處理的統一管理介面。
包括：
1. 驗證碼檢測和處理
2. 驗證碼求解器管理
3. 驗證碼處理結果管理
4. 驗證碼處理策略管理
"""

from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path
import time
import json
import base64
from dataclasses import dataclass, field
import os
from datetime import datetime

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)

# 從 src.core.utils 導入工具類
from src.core.utils import (
    BrowserUtils,
    Logger,
    URLUtils,
    DataProcessor,
    ErrorHandler,
    ConfigUtils,
    PathUtils,
    ImageUtils,
    AudioUtils,
    TextUtils,
    CookieManager
)

from .types import CaptchaType, CaptchaConfig, CaptchaResult
from .detection import CaptchaDetector
from .solvers import (
    RecaptchaSolver,
    HcaptchaSolver,
    ImageCaptchaSolver,
    SliderCaptchaSolver,
    RotateCaptchaSolver,
    ClickCaptchaSolver,
    TextCaptchaSolver,
    ShopeeSolver
)


class CaptchaManager:
    """驗證碼管理器"""
    
    def __init__(self, browser: WebDriver, config: Dict[str, Any]):
        """
        初始化驗證碼管理器
        
        Args:
            browser: WebDriver 實例
            config: 配置字典
        """
        self.browser = browser
        self.config = config
        
        # 初始化工具類
        self.logger = Logger(__name__)
        self.error_handler = ErrorHandler()
        self.config_utils = ConfigUtils()
        self.browser_utils = BrowserUtils(self.browser)
        self.url_utils = URLUtils()
        self.data_processor = DataProcessor()
        self.image_utils = ImageUtils()
        self.audio_utils = AudioUtils()
        self.text_utils = TextUtils()
        self.cookie_manager = CookieManager()
        
        # 初始化檢測器
        self.detector = CaptchaDetector(self.browser, self.config)
        
        # 初始化配置
        self._init_manager()
        
    def _init_manager(self):
        """初始化管理器配置"""
        try:
            # 設置超時和重試
            self.timeout = self.config.get('timeout', 30)
            self.retry_count = self.config.get('retry_count', 3)
            
            # 設置目錄
            self.screenshot_dir = self.config.get('screenshot_dir', 'screenshots')
            self.log_dir = self.config.get('log_dir', 'logs')
            self.temp_dir = self.config.get('temp_dir', 'temp')
            self.cookie_dir = self.config.get('cookie_dir', 'cookies')
            
            # 創建目錄
            for dir_path in [self.screenshot_dir, self.log_dir, self.temp_dir, self.cookie_dir]:
                os.makedirs(dir_path, exist_ok=True)
                
            # 初始化狀態
            self.processing_status = {
                'current_type': None,
                'retry_count': 0,
                'success_count': 0,
                'failure_count': 0
            }
            
            # 初始化緩存
            self.result_cache = {}
            self.screenshot_cache = {}
            self.solution_cache = {}
            self.cookie_cache = {}
            
        except Exception as e:
            self.logger.error(f"初始化管理器失敗: {str(e)}")
            raise
            
    def _save_captcha_screenshot(self, element: WebElement, captcha_type: str) -> str:
        """
        保存驗證碼截圖
        
        Args:
            element: 驗證碼元素
            captcha_type: 驗證碼類型
            
        Returns:
            截圖路徑
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{captcha_type}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            # 使用 ImageUtils 保存截圖
            self.image_utils.save_screenshot(element, filepath)
            
            self.logger.info(f"已保存驗證碼截圖: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"保存驗證碼截圖失敗: {str(e)}")
            raise
            
    def _save_captcha_cookie(self, captcha_type: str) -> None:
        """
        保存驗證碼相關的 Cookie
        
        Args:
            captcha_type: 驗證碼類型
        """
        try:
            cookies = self.browser.get_cookies()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{captcha_type}_{timestamp}.json"
            filepath = os.path.join(self.cookie_dir, filename)
            
            # 使用 CookieManager 保存 Cookie
            self.cookie_manager.save_cookies(cookies, filepath)
            
            self.logger.info(f"已保存驗證碼 Cookie: {filepath}")
            
        except Exception as e:
            self.logger.error(f"保存驗證碼 Cookie 失敗: {str(e)}")
            raise
    
    def process_captcha(self, driver: WebDriver) -> CaptchaResult:
        """
        處理驗證碼
        
        Args:
            driver: WebDriver實例
            
        Returns:
            CaptchaResult: 驗證碼處理結果
        """
        try:
            # 檢查管理器狀態
            if self.processing_status['current_type']:
                return CaptchaResult(
                    success=False,
                    captcha_type=CaptchaType.UNKNOWN,
                    error="管理器正在處理其他驗證碼"
                )
            
            # 更新管理器狀態
            self.processing_status['current_type'] = self.config['type']
            self.processing_status['retry_count'] += 1
            
            # 檢測驗證碼
            has_captcha, captcha_type = self.detector.detect_captcha(driver)
            if not has_captcha:
                self.processing_status['current_type'] = None
                return CaptchaResult(
                    success=True,
                    captcha_type=CaptchaType.UNKNOWN,
                    details={"message": "未檢測到驗證碼"}
                )
            
            # 定位驗證碼元素
            element = self.detector.locate_captcha_element(driver, captcha_type)
            if not element:
                self.processing_status['current_type'] = None
                return CaptchaResult(
                    success=False,
                    captcha_type=captcha_type,
                    error="無法定位驗證碼元素"
                )
            
            # 檢查驗證碼狀態
            if not self.detector.check_captcha_status(driver, captcha_type):
                self.processing_status['current_type'] = None
                return CaptchaResult(
                    success=False,
                    captcha_type=captcha_type,
                    error="驗證碼元素狀態無效"
                )
            
            # 處理驗證碼
            result = self._handle_captcha(driver, element, captcha_type)
            
            # 驗證處理結果
            if not self.detector.validate_result(result):
                self.processing_status['current_type'] = None
                self.processing_status['failure_count'] += 1
                return CaptchaResult(
                    success=False,
                    captcha_type=captcha_type,
                    error="驗證碼處理結果無效"
                )
            
            # 更新管理器狀態
            self.processing_status['current_type'] = None
            if result.success:
                self.processing_status['success_count'] += 1
            else:
                self.processing_status['failure_count'] += 1
            
            return result
        except Exception as e:
            self.error_handler.handle_error(e, "處理驗證碼失敗")
            self.processing_status['current_type'] = None
            self.processing_status['failure_count'] += 1
            return CaptchaResult(
                success=False,
                captcha_type=CaptchaType.UNKNOWN,
                error=str(e)
            )
    
    def _handle_captcha(
        self,
        driver: WebDriver,
        element: WebElement,
        captcha_type: CaptchaType
    ) -> CaptchaResult:
        """
        處理特定類型的驗證碼
        
        Args:
            driver: WebDriver實例
            element: 驗證碼元素
            captcha_type: 驗證碼類型
            
        Returns:
            CaptchaResult: 驗證碼處理結果
        """
        try:
            # 獲取對應的求解器
            solver = self.solvers.get(captcha_type)
            if not solver:
                self.logger.error(f"未找到 {captcha_type.value} 的求解器")
                return CaptchaResult(
                    success=False,
                    captcha_type=captcha_type,
                    error=f"未找到 {captcha_type.value} 的求解器"
                )
            
            # 保存驗證碼截圖
            screenshot_path = self._save_captcha_screenshot(element, captcha_type)
            
            # 保存驗證碼 Cookie
            self._save_captcha_cookie(captcha_type)
            
            # 求解驗證碼
            result = solver.solve(driver, element)
            
            # 更新緩存
            self.result_cache[f"{captcha_type.value}_{driver.current_url}"] = result
            if screenshot_path:
                self.screenshot_cache[f"{captcha_type.value}_{driver.current_url}"] = screenshot_path
            
            return result
        except Exception as e:
            self.error_handler.handle_error(e, f"處理 {captcha_type.value} 失敗")
            return CaptchaResult(
                success=False,
                captcha_type=captcha_type,
                error=str(e)
            )
    
    def take_screenshot(
        self,
        driver: WebDriver,
        element: Optional[Any] = None,
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        截取驗證碼圖片
        
        Args:
            driver: WebDriver實例
            element: 要截圖的元素
            filename: 文件名
            
        Returns:
            Optional[str]: 截圖文件路徑
        """
        try:
            if not filename:
                timestamp = int(time.time() * 1000)
                filename = f"captcha_{timestamp}.png"
            
            filepath = Path(self.screenshot_dir) / filename
            
            if element:
                element.screenshot(str(filepath))
            else:
                driver.save_screenshot(str(filepath))
            
            self.logger.info(f"驗證碼截圖已保存: {filepath}")
            return str(filepath)
        except Exception as e:
            self.error_handler.handle_error(e, "截取驗證碼圖片失敗")
            return None
    
    def save_result(self, result: CaptchaResult) -> bool:
        """
        保存處理結果
        
        Args:
            result: 驗證碼處理結果
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 生成結果文件名
            timestamp = int(time.time() * 1000)
            filename = f"result_{timestamp}.json"
            filepath = Path(self.log_dir) / filename
            
            # 序列化結果
            result_dict = {
                'success': result.success,
                'captcha_type': result.captcha_type.value,
                'solution': result.solution,
                'confidence': result.confidence,
                'error': result.error,
                'details': result.details,
                'timestamp': timestamp
            }
            
            # 保存結果
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"驗證碼處理結果已保存: {filepath}")
            return True
        except Exception as e:
            self.error_handler.handle_error(e, "保存驗證碼處理結果失敗")
            return False
    
    def load_result(self, filepath: Union[str, Path]) -> Optional[CaptchaResult]:
        """
        加載處理結果
        
        Args:
            filepath: 結果文件路徑
            
        Returns:
            Optional[CaptchaResult]: 驗證碼處理結果
        """
        try:
            # 讀取結果文件
            with open(filepath, 'r', encoding='utf-8') as f:
                result_dict = json.load(f)
            
            # 反序列化結果
            return CaptchaResult(
                success=result_dict['success'],
                captcha_type=CaptchaType(result_dict['captcha_type']),
                solution=result_dict.get('solution'),
                confidence=result_dict.get('confidence', 0.0),
                error=result_dict.get('error'),
                details=result_dict.get('details', {})
            )
        except Exception as e:
            self.error_handler.handle_error(e, "加載驗證碼處理結果失敗")
            return None
    
    def clear_cache(self):
        """清理緩存"""
        try:
            self.result_cache = {}
            self.screenshot_cache = {}
            self.logger.info("驗證碼管理器緩存已清理")
        except Exception as e:
            self.error_handler.handle_error(e, "清理驗證碼管理器緩存失敗")
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼檢測模組

提供驗證碼檢測相關功能。
包括：
1. 驗證碼類型檢測
2. 驗證碼元素定位
3. 驗證碼狀態檢查
4. 驗證碼處理結果驗證
"""

from typing import Dict, Any, Optional, List, Union, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
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
    ImageUtils
)

from .types import CaptchaType, CaptchaConfig, CaptchaResult


class CaptchaDetector:
    """驗證碼檢測器"""
    
    def __init__(self, browser: WebDriver, config: Dict[str, Any]):
        """
        初始化驗證碼檢測器
        
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
        
        # 初始化配置
        self._init_detector()
        
    def _init_detector(self):
        """初始化檢測器配置"""
        try:
            # 設置超時和重試
            self.timeout = self.config.get('timeout', 30)
            self.retry_count = self.config.get('retry_count', 3)
            
            # 設置檢測配置
            self.detection_config = {
                'recaptcha': {
                    'iframe_selector': 'iframe[src*="recaptcha"]',
                    'checkbox_selector': '.recaptcha-checkbox-border'
                },
                'hcaptcha': {
                    'iframe_selector': 'iframe[src*="hcaptcha"]',
                    'checkbox_selector': '#checkbox'
                },
                'image_captcha': {
                    'image_selector': 'img[alt*="captcha"]'
                },
                'slider_captcha': {
                    'slider_selector': '.slider-captcha'
                },
                'rotate_captcha': {
                    'rotate_selector': '.rotate-captcha'
                },
                'click_captcha': {
                    'click_selector': '.click-captcha'
                },
                'text_captcha': {
                    'input_selector': 'input[name*="captcha"]'
                },
                'shopee': {
                    'slider_selector': '.shopee-captcha'
                }
            }
            
            # 初始化狀態
            self.detection_status = {
                'current_type': None,
                'retry_count': 0,
                'success_count': 0,
                'failure_count': 0
            }
            
        except Exception as e:
            self.logger.error(f"初始化檢測器失敗: {str(e)}")
            raise
            
    def detect_captcha(self, driver: WebDriver) -> Tuple[bool, Optional[str]]:
        """
        檢測頁面中的驗證碼
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            Tuple[bool, Optional[str]]: (是否存在驗證碼, 驗證碼類型)
        """
        try:
            # 檢查 reCAPTCHA
            if self._detect_recaptcha(driver):
                return True, 'recaptcha'
                
            # 檢查 hCaptcha
            if self._detect_hcaptcha(driver):
                return True, 'hcaptcha'
                
            # 檢查圖片驗證碼
            if self._detect_image_captcha(driver):
                return True, 'image_captcha'
                
            # 檢查滑塊驗證碼
            if self._detect_slider_captcha(driver):
                return True, 'slider_captcha'
                
            # 檢查旋轉驗證碼
            if self._detect_rotate_captcha(driver):
                return True, 'rotate_captcha'
                
            # 檢查點擊驗證碼
            if self._detect_click_captcha(driver):
                return True, 'click_captcha'
                
            # 檢查文本驗證碼
            if self._detect_text_captcha(driver):
                return True, 'text_captcha'
                
            # 檢查 Shopee 驗證碼
            if self._detect_shopee_slider(driver):
                return True, 'shopee'
                
            return False, None
            
        except Exception as e:
            self.logger.error(f"檢測驗證碼失敗: {str(e)}")
            return False, None
            
    def _detect_recaptcha(self, driver: WebDriver) -> bool:
        """
        檢測 reCAPTCHA
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            bool: 是否存在 reCAPTCHA
        """
        try:
            config = self.detection_config['recaptcha']
            iframe = self.browser_utils.find_element(
                driver,
                By.CSS_SELECTOR,
                config['iframe_selector']
            )
            
            if not iframe:
                return False
                
            driver.switch_to.frame(iframe)
            checkbox = self.browser_utils.find_element(
                driver,
                By.CSS_SELECTOR,
                config['checkbox_selector']
            )
            driver.switch_to.default_content()
            
            return bool(checkbox)
            
        except Exception as e:
            self.logger.error(f"檢測 reCAPTCHA 失敗: {str(e)}")
            driver.switch_to.default_content()
            return False
            
    def _detect_hcaptcha(self, driver: WebDriver) -> bool:
        """
        檢測 hCaptcha
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            bool: 是否存在 hCaptcha
        """
        try:
            config = self.detection_config['hcaptcha']
            iframe = self.browser_utils.find_element(
                driver,
                By.CSS_SELECTOR,
                config['iframe_selector']
            )
            
            if not iframe:
                return False
                
            driver.switch_to.frame(iframe)
            checkbox = self.browser_utils.find_element(
                driver,
                By.CSS_SELECTOR,
                config['checkbox_selector']
            )
            driver.switch_to.default_content()
            
            return bool(checkbox)
            
        except Exception as e:
            self.logger.error(f"檢測 hCaptcha 失敗: {str(e)}")
            driver.switch_to.default_content()
            return False
            
    def _detect_image_captcha(self, driver: WebDriver) -> bool:
        """
        檢測圖片驗證碼
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            bool: 是否存在圖片驗證碼
        """
        try:
            config = self.detection_config['image_captcha']
            image = self.browser_utils.find_element(
                driver,
                By.CSS_SELECTOR,
                config['image_selector']
            )
            
            return bool(image)
            
        except Exception as e:
            self.logger.error(f"檢測圖片驗證碼失敗: {str(e)}")
            return False
            
    def _detect_slider_captcha(self, driver: WebDriver) -> bool:
        """
        檢測滑塊驗證碼
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            bool: 是否存在滑塊驗證碼
        """
        try:
            config = self.detection_config['slider_captcha']
            slider = self.browser_utils.find_element(
                driver,
                By.CSS_SELECTOR,
                config['slider_selector']
            )
            
            return bool(slider)
            
        except Exception as e:
            self.logger.error(f"檢測滑塊驗證碼失敗: {str(e)}")
            return False
            
    def _detect_rotate_captcha(self, driver: WebDriver) -> bool:
        """
        檢測旋轉驗證碼
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            bool: 是否存在旋轉驗證碼
        """
        try:
            config = self.detection_config['rotate_captcha']
            rotate = self.browser_utils.find_element(
                driver,
                By.CSS_SELECTOR,
                config['rotate_selector']
            )
            
            return bool(rotate)
            
        except Exception as e:
            self.logger.error(f"檢測旋轉驗證碼失敗: {str(e)}")
            return False
            
    def _detect_click_captcha(self, driver: WebDriver) -> bool:
        """
        檢測點擊驗證碼
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            bool: 是否存在點擊驗證碼
        """
        try:
            config = self.detection_config['click_captcha']
            click = self.browser_utils.find_element(
                driver,
                By.CSS_SELECTOR,
                config['click_selector']
            )
            
            return bool(click)
            
        except Exception as e:
            self.logger.error(f"檢測點擊驗證碼失敗: {str(e)}")
            return False
            
    def _detect_text_captcha(self, driver: WebDriver) -> bool:
        """
        檢測文本驗證碼
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            bool: 是否存在文本驗證碼
        """
        try:
            config = self.detection_config['text_captcha']
            text = self.browser_utils.find_element(
                driver,
                By.CSS_SELECTOR,
                config['input_selector']
            )
            
            return bool(text)
            
        except Exception as e:
            self.logger.error(f"檢測文本驗證碼失敗: {str(e)}")
            return False
            
    def _detect_shopee_slider(self, driver: WebDriver) -> bool:
        """
        檢測 Shopee 滑塊驗證碼
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            bool: 是否存在 Shopee 滑塊驗證碼
        """
        try:
            config = self.detection_config['shopee']
            slider = self.browser_utils.find_element(
                driver,
                By.CSS_SELECTOR,
                config['slider_selector']
            )
            
            return bool(slider)
            
        except Exception as e:
            self.logger.error(f"檢測 Shopee 滑塊驗證碼失敗: {str(e)}")
            return False
    
    def locate_captcha_element(self, driver: Any, captcha_type: CaptchaType) -> Optional[WebElement]:
        """
        定位驗證碼元素
        
        Args:
            driver: WebDriver實例
            captcha_type: 驗證碼類型
            
        Returns:
            Optional[WebElement]: 驗證碼元素
        """
        try:
            # 檢查緩存
            cache_key = f"{captcha_type.value}_{driver.current_url}"
            if cache_key in self.detection_cache['elements']:
                return self.detection_cache['elements'][cache_key]
            
            # 根據驗證碼類型定位元素
            element = None
            if captcha_type == CaptchaType.RECAPTCHA:
                element = self._locate_recaptcha_element(driver)
            elif captcha_type == CaptchaType.HCAPTCHA:
                element = self._locate_hcaptcha_element(driver)
            elif captcha_type == CaptchaType.IMAGE_CAPTCHA:
                element = self._locate_image_captcha_element(driver)
            elif captcha_type == CaptchaType.SLIDER_CAPTCHA:
                element = self._locate_slider_captcha_element(driver)
            elif captcha_type == CaptchaType.ROTATE_CAPTCHA:
                element = self._locate_rotate_captcha_element(driver)
            elif captcha_type == CaptchaType.CLICK_CAPTCHA:
                element = self._locate_click_captcha_element(driver)
            elif captcha_type == CaptchaType.TEXT_CAPTCHA:
                element = self._locate_text_captcha_element(driver)
            
            # 更新緩存
            if element:
                self.detection_cache['elements'][cache_key] = element
            
            return element
        except Exception as e:
            self.error_handler.handle_error(e, "定位驗證碼元素失敗")
            return None
    
    def _locate_recaptcha_element(self, driver: Any) -> Optional[WebElement]:
        """定位 reCAPTCHA 元素"""
        try:
            # 查找 reCAPTCHA iframe
            iframes = driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha']")
            if iframes:
                return iframes[0]
            
            # 查找 reCAPTCHA 元素
            elements = driver.find_elements(By.CSS_SELECTOR, ".g-recaptcha")
            if elements:
                return elements[0]
            
            return None
        except Exception:
            return None
    
    def _locate_hcaptcha_element(self, driver: Any) -> Optional[WebElement]:
        """定位 hCaptcha 元素"""
        try:
            # 查找 hCaptcha iframe
            iframes = driver.find_elements(By.CSS_SELECTOR, "iframe[src*='hcaptcha']")
            if iframes:
                return iframes[0]
            
            # 查找 hCaptcha 元素
            elements = driver.find_elements(By.CSS_SELECTOR, ".h-captcha")
            if elements:
                return elements[0]
            
            return None
        except Exception:
            return None
    
    def _locate_image_captcha_element(self, driver: Any) -> Optional[WebElement]:
        """定位圖片驗證碼元素"""
        try:
            # 查找圖片驗證碼元素
            elements = driver.find_elements(By.CSS_SELECTOR, "img[src*='captcha']")
            if elements:
                return elements[0]
            
            # 查找驗證碼輸入框
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[name*='captcha']")
            if inputs:
                return inputs[0]
            
            return None
        except Exception:
            return None
    
    def _locate_slider_captcha_element(self, driver: Any) -> Optional[WebElement]:
        """定位滑塊驗證碼元素"""
        try:
            # 查找滑塊元素
            elements = driver.find_elements(By.CSS_SELECTOR, ".slider-captcha")
            if elements:
                return elements[0]
            
            # 查找滑塊按鈕
            buttons = driver.find_elements(By.CSS_SELECTOR, ".slider-button")
            if buttons:
                return buttons[0]
            
            return None
        except Exception:
            return None
    
    def _locate_rotate_captcha_element(self, driver: WebDriver) -> Optional[WebElement]:
        """定位旋轉驗證碼元素"""
        try:
            # 查找旋轉驗證碼元素
            elements = self.browser_utils.find_elements(
                driver,
                By.CSS_SELECTOR,
                ".rotate-captcha"
            )
            if elements:
                self.logger.info("已定位到旋轉驗證碼元素")
                return elements[0]
            
            # 查找旋轉按鈕
            buttons = self.browser_utils.find_elements(
                driver,
                By.CSS_SELECTOR,
                ".rotate-button"
            )
            if buttons:
                self.logger.info("已定位到旋轉按鈕")
                return buttons[0]
            
            return None
        except Exception as e:
            self.error_handler.handle_error(e, "定位旋轉驗證碼元素失敗")
            return None
    
    def _locate_click_captcha_element(self, driver: WebDriver) -> Optional[WebElement]:
        """定位點擊驗證碼元素"""
        try:
            # 查找點擊驗證碼元素
            elements = self.browser_utils.find_elements(
                driver,
                By.CSS_SELECTOR,
                ".click-captcha"
            )
            if elements:
                self.logger.info("已定位到點擊驗證碼元素")
                return elements[0]
            
            # 查找點擊區域
            areas = self.browser_utils.find_elements(
                driver,
                By.CSS_SELECTOR,
                ".click-area"
            )
            if areas:
                self.logger.info("已定位到點擊區域")
                return areas[0]
            
            return None
        except Exception as e:
            self.error_handler.handle_error(e, "定位點擊驗證碼元素失敗")
            return None
    
    def _locate_text_captcha_element(self, driver: WebDriver) -> Optional[WebElement]:
        """定位文字驗證碼元素"""
        try:
            # 查找文字驗證碼元素
            elements = self.browser_utils.find_elements(
                driver,
                By.CSS_SELECTOR,
                ".text-captcha"
            )
            if elements:
                self.logger.info("已定位到文字驗證碼元素")
                return elements[0]
            
            # 查找問題文本
            questions = self.browser_utils.find_elements(
                driver,
                By.CSS_SELECTOR,
                ".captcha-question"
            )
            if questions:
                self.logger.info("已定位到驗證碼問題文本")
                return questions[0]
            
            return None
        except Exception as e:
            self.error_handler.handle_error(e, "定位文字驗證碼元素失敗")
            return None
    
    def check_captcha_status(self, driver: WebDriver, captcha_type: CaptchaType) -> bool:
        """
        檢查驗證碼狀態
        
        Args:
            driver: WebDriver實例
            captcha_type: 驗證碼類型
            
        Returns:
            bool: 驗證碼是否有效
        """
        try:
            # 檢查緩存
            cache_key = f"{captcha_type.value}_{driver.current_url}"
            if cache_key in self.detection_cache['results']:
                return self.detection_cache['results'][cache_key]
            
            # 定位驗證碼元素
            element = self.locate_captcha_element(driver, captcha_type)
            if not element:
                self.logger.warning("未找到驗證碼元素")
                return False
            
            # 檢查元素狀態
            is_valid = self._check_element_status(element)
            
            # 更新緩存
            self.detection_cache['results'][cache_key] = is_valid
            
            # 更新統計信息
            if is_valid:
                self.detection_status['success_count'] += 1
            else:
                self.detection_status['failure_count'] += 1
            
            return is_valid
        except Exception as e:
            self.error_handler.handle_error(e, "檢查驗證碼狀態失敗")
            return False
    
    def _check_element_status(self, element: WebElement) -> bool:
        """
        檢查元素狀態
        
        Args:
            element: WebElement實例
            
        Returns:
            bool: 元素是否有效
        """
        try:
            # 檢查元素是否可見
            if not element.is_displayed():
                self.logger.warning("元素不可見")
                return False
            
            # 檢查元素是否啟用
            if not element.is_enabled():
                self.logger.warning("元素未啟用")
                return False
            
            # 檢查元素是否可交互
            if not self.browser_utils.is_element_interactable(element):
                self.logger.warning("元素不可交互")
                return False
            
            return True
        except Exception as e:
            self.error_handler.handle_error(e, "檢查元素狀態失敗")
            return False
    
    def validate_result(self, result: CaptchaResult) -> bool:
        """
        驗證處理結果
        
        Args:
            result: 驗證碼處理結果
            
        Returns:
            bool: 結果是否有效
        """
        try:
            # 檢查結果是否為空
            if not result:
                self.logger.warning("驗證碼結果為空")
                return False
            
            # 檢查結果類型
            if not isinstance(result, CaptchaResult):
                self.logger.warning("驗證碼結果類型錯誤")
                return False
            
            # 檢查必要字段
            if not hasattr(result, 'success') or not hasattr(result, 'captcha_type'):
                self.logger.warning("驗證碼結果缺少必要字段")
                return False
            
            # 檢查結果狀態
            if not result.success:
                self.logger.warning("驗證碼處理失敗")
                return False
            
            # 檢查結果詳情
            if not result.details:
                self.logger.warning("驗證碼結果缺少詳情")
                return False
            
            self.logger.info("驗證碼結果驗證通過")
            return True
        except Exception as e:
            self.error_handler.handle_error(e, "驗證處理結果失敗")
            return False 
"""
蝦皮反指紋檢測模組
"""

import logging
from typing import Dict, Any, Optional, Union

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from ..browser_anti_fingerprint import BrowserAntiFingerprint
from ..configs.anti_fingerprint_config import AntiFingerprintConfig

class ShopeeAntiFingerprint(BrowserAntiFingerprint):
    """蝦皮反指紋檢測類"""
    
    def __init__(self, config: Union[Dict[str, Any], AntiFingerprintConfig], logger=None):
        """
        初始化蝦皮反指紋檢測
        
        Args:
            config: 反指紋檢測配置
            logger: 日誌記錄器
        """
        super().__init__(config, logger)
        self.shopee_config = self._get_shopee_config()
    
    def _get_shopee_config(self) -> Dict[str, Any]:
        """獲取蝦皮特定的配置"""
        return {
            "browser_type": "chrome",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "headless": False,
            "window_size": {"width": 1920, "height": 1080},
            "enable_stealth": True,
            "timeout": 30,
            "disable_webgl": True,
            "disable_canvas": True,
            "experimental_options": {
                "excludeSwitches": ["enable-automation"],
                "useAutomationExtension": False
            }
        }
    
    def _init_from_anti_fingerprint_config(self, config: AntiFingerprintConfig):
        """從反指紋檢測配置初始化"""
        super()._init_from_anti_fingerprint_config(config)
        # 合併蝦皮特定配置
        for key, value in self.shopee_config.items():
            if not hasattr(self, key) or getattr(self, key) is None:
                setattr(self, key, value)
    
    def _init_from_dict_config(self, config: Dict[str, Any]):
        """從字典配置初始化"""
        super()._init_from_dict_config(config)
        # 合併蝦皮特定配置
        for key, value in self.shopee_config.items():
            if key not in config:
                config[key] = value
    
    def navigate_to_shopee(self, url: str = "https://www.shopee.tw") -> bool:
        """
        導航到蝦皮網站
        
        Args:
            url: 蝦皮網站URL
            
        Returns:
            是否成功導航
        """
        try:
            driver = self.create_driver()
            driver.get(url)
            
            # 等待頁面加載完成
            WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            return True
        except TimeoutException:
            self.logger.error("導航到蝦皮網站超時")
            return False
        except Exception as e:
            self.logger.error(f"導航到蝦皮網站失敗: {str(e)}")
            return False
    
    def check_anti_bot(self) -> bool:
        """
        檢查是否觸發反爬蟲機制
        
        Returns:
            是否觸發反爬蟲機制
        """
        try:
            driver = self.create_driver()
            
            # 檢查常見的反爬蟲元素
            anti_bot_selectors = [
                "//div[contains(@class, 'captcha')]",
                "//div[contains(@class, 'verify')]",
                "//div[contains(@class, 'security-check')]",
                "//iframe[contains(@src, 'recaptcha')]",
                "//div[contains(@class, 'g-recaptcha')]"
            ]
            
            for selector in anti_bot_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements and elements[0].is_displayed():
                    self.logger.warning(f"檢測到反爬蟲機制: {selector}")
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"檢查反爬蟲機制失敗: {str(e)}")
            return False
    
    def handle_anti_bot(self) -> bool:
        """
        處理反爬蟲機制
        
        Returns:
            是否成功處理
        """
        try:
            driver = self.create_driver()
            
            # 檢查並處理驗證碼
            if self._handle_captcha(driver):
                return True
            
            # 檢查並處理滑塊驗證
            if self._handle_slider(driver):
                return True
            
            # 檢查並處理 reCAPTCHA
            if self._handle_recaptcha(driver):
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"處理反爬蟲機制失敗: {str(e)}")
            return False
    
    def _handle_captcha(self, driver: webdriver.Remote) -> bool:
        """處理圖片驗證碼"""
        try:
            # 檢查是否存在驗證碼
            captcha_selectors = [
                "//img[contains(@src, 'captcha')]",
                "//div[contains(@class, 'captcha')]//img"
            ]
            
            for selector in captcha_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements and elements[0].is_displayed():
                    # TODO: 實現驗證碼識別和處理
                    self.logger.warning("檢測到圖片驗證碼，需要手動處理")
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"處理圖片驗證碼失敗: {str(e)}")
            return False
    
    def _handle_slider(self, driver: webdriver.Remote) -> bool:
        """處理滑塊驗證"""
        try:
            # 檢查是否存在滑塊
            slider_selectors = [
                "//div[contains(@class, 'slider')]",
                "//div[contains(@class, 'verify-slider')]"
            ]
            
            for selector in slider_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements and elements[0].is_displayed():
                    # TODO: 實現滑塊驗證處理
                    self.logger.warning("檢測到滑塊驗證，需要手動處理")
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"處理滑塊驗證失敗: {str(e)}")
            return False
    
    def _handle_recaptcha(self, driver: webdriver.Remote) -> bool:
        """處理 reCAPTCHA"""
        try:
            # 檢查是否存在 reCAPTCHA
            recaptcha_selectors = [
                "//iframe[contains(@src, 'recaptcha')]",
                "//div[contains(@class, 'g-recaptcha')]"
            ]
            
            for selector in recaptcha_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements and elements[0].is_displayed():
                    # TODO: 實現 reCAPTCHA 處理
                    self.logger.warning("檢測到 reCAPTCHA，需要手動處理")
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"處理 reCAPTCHA 失敗: {str(e)}")
            return False 
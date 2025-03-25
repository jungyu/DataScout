def _locate_elements(self, driver: webdriver.Remote) -> Tuple[Optional[webdriver.remote.webelement.WebElement], Optional[webdriver.remote.webelement.WebElement]]:
        """
        定位驗證碼圖片和輸入框元素
        
        Args:
            driver: WebDriver實例
            
        Returns:
            驗證碼元素和輸入框元素
        """
        try:
            # 查找驗證碼圖片
            captcha_selectors = [
                "//img[contains(@src, 'captcha')]",
                "//img[contains(@src, 'verify')]",
                "//img[contains(@src, 'vcode')]",
                "//img[contains(@id, 'captcha')]",
                "//img[contains(@class, 'captcha')]"
            ]
            
            captcha_element = None
            
            for selector in captcha_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    captcha_element = elements[0]
                    break
            
            if not captcha_element:
                self.logger.warning("未找到驗證碼圖片元素")
                return None, None
            
            # 查找驗證碼輸入框
            input_selectors = [
                "//input[contains(@placeholder, '驗證碼')]",
                "//input[contains(@placeholder, 'captcha')]",
                "//input[contains(@id, 'captcha')]",
                "//input[contains(@name, 'captcha')]",
                "//input[contains(@class, 'captcha')]",
                "//label[contains(text(), '驗證碼')]/following::input",
                "//div[contains(text(), '驗證碼')]/following::input"
            ]
            
            input_element = None
            
            for selector in input_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    input_element = elements[0]
                    break
            
            if not input_element:
                self.logger.warning("未找到驗證碼輸入框元素")
                return captcha_element, None
            
            return captcha_element, input_element
        
        except Exception as e:
            self.logger.error(f"定位驗證碼元素失敗: {str(e)}")
            return None, None
    
    def _locate_captcha_element(self, driver: webdriver.Remote) -> Optional[webdriver.remote.webelement.WebElement]:
        """
        定位驗證碼元素
        
        Args:
            driver: WebDriver實例
            
        Returns:
            驗證碼元素或None
        """
        captcha_element, _ = self._locate_elements(driver)
        return captcha_element
    
    def _locate_submit_button(self, driver: webdriver.Remote) -> Optional[webdriver.remote.webelement.WebElement]:
        """
        定位提交按鈕
        
        Args:
            driver: WebDriver實例
            
        Returns:
            提交按鈕元素或None
        """
        try:
            # 查找提交按鈕
            submit_selectors = [
                "//button[contains(@type, 'submit')]",
                "//input[contains(@type, 'submit')]",
                "//button[contains(text(), '登入')]",
                "//button[contains(text(), '登錄')]",
                "//button[contains(text(), '確定')]",
                "//button[contains(text(), '確認')]",
                "//button[contains(text(), '提交')]",
                "//a[contains(text(), '登入')]",
                "//a[contains(text(), '登錄')]",
                "//a[contains(text(), '確定')]",
                "//a[contains(text(), '確認')]",
                "//a[contains(text(), '提交')]"
            ]
            
            for selector in submit_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    return elements[0]
            
            self.logger.warning("未找到提交按鈕元素")
            return None
        
        except Exception as e:
            self.logger.error(f"定位提交按鈕失敗: {str(e)}")
            return None
    
    def _download_image(self, image_url: str, save_path: str) -> bool:
        """
        下載驗證碼圖片
        
        Args:
            image_url: 圖片URL
            save_path: 保存路徑
            
        Returns:
            是否成功下載
        """
        try:
            # 如果是Base64圖片
            if image_url.startswith('data:image'):
                # 解析Base64數據
                base64_data = image_url.split(',')[1]
                image_data = base64.b64decode(base64_data)
                
                # 保存圖片
                with open(save_path, "wb") as f:
                    f.write(image_data)
                
                return True
            
            # 如果是普通URL
            else:
                import requests
                
                # 下載圖片
                response = requests.get(image_url, timeout=10)
                
                if response.status_code == 200:
                    # 保存圖片
                    with open(save_path, "wb") as f:
                        f.write(response.content)
                    
                    return True
                else:
                    self.logger.error(f"下載圖片失敗，狀態碼: {response.status_code}")
                    return False
        
        except Exception as e:
            self.logger.error(f"下載圖片失敗: {str(e)}")
            return False
    
    def _solve_with_external_service(self, driver: webdriver.Remote, captcha_url: str) -> Dict:
        """
        使用外部服務解決驗證碼
        
        Args:
            driver: WebDriver實例
            captcha_url: 驗證碼圖片URL
            
        Returns:
            服務結果字典
        """
        # 獲取服務配置
        service_type = self.service_config.get("type", "2captcha")
        service_api = self.service_config.get("api", "")
        service_key = self.service_config.get("key", "")
        
        if not service_api or not service_key:
            self.logger.warning("外部服務配置不完整")
            return {"success": False, "error": "配置不完整"}
        
        try:
            # 準備請求數據
            data = {}
            
            if captcha_url.startswith('data:image'):
                # 提取Base64數據
                base64_data = captcha_url.split(',')[1]
                
                data = {
                    "key": service_key,
                    "method": "base64",
                    "body": base64_data,
                    "json": 1
                }
            else:
                data = {
                    "key": service_key,
                    "method": "post",
                    "url": captcha_url,
                    "json": 1
                }
            
            # 調用外部服務
            return self._call_external_service(service_type, service_api, service_key, data)
        
        except Exception as e:
            self.logger.error(f"使用外部服務解決驗證碼失敗: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _manual_input(self) -> str:
        """
        請求人工輸入驗證碼
        
        Returns:
            人工輸入的驗證碼文本
        """
        print("\n=== 請查看瀏覽器中的驗證碼圖片 ===")
        captcha_text = input("請輸入驗證碼: ")
        
        if not self.case_sensitive:
            captcha_text = captcha_text.lower()
        
        return captcha_text
    
    def _refresh_captcha(self, driver: webdriver.Remote) -> bool:
        """
        刷新驗證碼
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否成功刷新
        """
        try:
            # 查找刷新按鈕或鏈接
            refresh_selectors = [
                "//a[contains(@class, 'captcha-refresh')]",
                "//img[contains(@class, 'captcha-refresh')]",
                "//a[contains(@onclick, 'refresh')]",
                "//a[contains(text(), '刷新')]",
                "//span[contains(text(), '刷新')]"
            ]
            
            for selector in refresh_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    elements[0].click()
                    time.sleep(1)
                    return True
            
            # 如果沒有找到刷新按鈕，嘗試點擊驗證碼圖片本身
            captcha_element = self._locate_captcha_element(driver)
            if captcha_element:
                captcha_element.click()
                time.sleep(1)
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"刷新驗證碼失敗: {str(e)}")
            return False
    
    def _check_success(self, driver: webdriver.Remote) -> bool:
        """
        檢查驗證碼是否成功提交
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否成功提交
        """
        try:
            # 檢查是否仍存在驗證碼錯誤提示
            error_selectors = [
                "//div[contains(text(), '驗證碼錯誤')]",
                "//span[contains(text(), '驗證碼錯誤')]",
                "//div[contains(text(), '驗證碼不正確')]",
                "//span[contains(text(), '驗證碼不正確')]",
                "//div[contains(@class, 'error')]"
            ]
            
            for selector in error_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    return False
            
            # 檢查是否仍顯示驗證碼輸入框
            _, input_element = self._locate_elements(driver)
            
            # 如果驗證碼輸入框已經不可見，可能表示成功
            if input_element is None:
                return True
            
            # 檢查是否成功進入下一頁
            # 此處需要根據具體網站進行調整
            
            # 默認情況下，如果沒有明確的錯誤提示，認為提交成功
            return True
        
        except Exception as e:
            self.logger.error(f"檢查驗證碼提交結果失敗: {str(e)}")
            return False#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import base64
import logging
from typing import Dict, Any, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_solver import BaseCaptchaSolver
from ...utils.logger import setup_logger
from ...utils.error_handler import retry_on_exception, handle_exception


class TextCaptchaSolver(BaseCaptchaSolver):
    """
    文本驗證碼解決器，用於解決常見的字符驗證碼
    """
    
    def _init_solver(self):
        """初始化文本驗證碼解決器"""
        # 文本驗證碼特有配置
        self.captcha_length = self.config.get("captcha_length", 4)
        self.case_sensitive = self.config.get("case_sensitive", False)
        
        # 模型路徑
        self.model_path = self.model_config.get("model_path", "")
        
        # 載入模型（如果有）
        self.model = None
        if self.model_path and os.path.exists(self.model_path):
            self.model = self._load_model(self.model_path)
            if self.model:
                self.logger.info(f"已載入文本驗證碼模型: {self.model_path}")
            else:
                self.logger.warning(f"載入文本驗證碼模型失敗: {self.model_path}")
    
    def _get_captcha_type(self) -> str:
        """獲取驗證碼類型"""
        return "text"
    
    def solve(self, driver: webdriver.Remote) -> bool:
        """
        解決文本驗證碼
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否成功解決
        """
        try:
            # 定位驗證碼元素和輸入框
            captcha_element, input_element = self._locate_elements(driver)
            
            if not captcha_element or not input_element:
                self.logger.warning("未找到驗證碼元素或輸入框")
                return False
            
            # 保存驗證碼樣本
            sample_path = self._save_sample(driver)
            
            # 獲取驗證碼圖片
            captcha_url = captcha_element.get_attribute("src")
            
            # 解決驗證碼
            captcha_text = ""
            
            # 優先使用模型識別
            if self.model:
                # 從URL下載圖片
                image_path = f"{sample_path}.png"
                self._download_image(captcha_url, image_path)
                
                # 預處理圖片
                preprocessed_image = self._preprocess_image(image_path)
                
                if preprocessed_image is not None:
                    # 使用模型預測
                    captcha_text = self._predict(self.model, preprocessed_image)
                    self.logger.info(f"模型識別結果: {captcha_text}")
            
            # 如果模型識別失敗或沒有模型，使用外部服務
            if not captcha_text and self.use_external_service:
                service_result = self._solve_with_external_service(driver, captcha_url)
                if service_result["success"]:
                    captcha_text = service_result["result"]
                    self.logger.info(f"外部服務識別結果: {captcha_text}")
            
            # 如果還是沒有結果，請求人工輸入
            if not captcha_text:
                captcha_text = self._manual_input()
            
            # 輸入驗證碼
            if captcha_text:
                # 清空輸入框
                input_element.clear()
                
                # 輸入驗證碼
                input_element.send_keys(captcha_text)
                
                # 提交表單
                submit_button = self._locate_submit_button(driver)
                if submit_button:
                    submit_button.click()
                    time.sleep(2)  # 等待提交結果
                
                # 檢查是否成功
                if self._check_success(driver):
                    self.logger.info("驗證碼提交成功")
                    return True
                else:
                    self.logger.warning("驗證碼提交失敗")
                    # 嘗試刷新驗證碼
                    self._refresh_captcha(driver)
                    return False
            
            return False
        
        except Exception as e:
            self.logger.error(f"解決文本驗證碼失敗: {str(e)}")
            return False
    
    def _locate_elements(self, driver: webdriver.Remote) ->
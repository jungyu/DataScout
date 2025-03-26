#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import base64
import logging
import requests
import numpy as np
from typing import Dict, Any, Optional, Tuple, Union
from io import BytesIO
from PIL import Image

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

from .base_solver import BaseCaptchaSolver


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
                
        # 配置Tesseract (如果使用OCR)
        self.tesseract_config = self.config.get('tesseract_config', {})
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_config.get(
                'cmd_path', pytesseract.pytesseract.tesseract_cmd
            )
            self.use_tesseract = True
        except ImportError:
            self.use_tesseract = False
            self.logger.warning("未安裝pytesseract，將不使用OCR功能")
        
        # 預處理配置
        self.preprocessing = self.config.get('preprocessing', {
            'grayscale': True,
            'threshold': True,
            'noise_reduction': True,
            'deskew': True,
            'contrast_enhancement': True
        })
        
        # 字符白名單和黑名單
        self.char_whitelist = self.config.get('character_whitelist', '')
        self.char_blacklist = self.config.get('character_blacklist', '')
        
        # 最小置信度
        self.min_confidence = self.config.get('min_confidence', 0.8)
    
    def _get_captcha_type(self) -> str:
        """獲取驗證碼類型"""
        return "text"
    
    def detect(self) -> bool:
        """檢測頁面上是否存在文字驗證碼"""
        try:
            if not self.driver:
                self.logger.error("未提供WebDriver實例")
                return False
                
            captcha_selectors = [
                "img[alt*='captcha']",
                "img[src*='captcha']",
                "img[id*='captcha']",
                "img[class*='captcha']",
                "img[name*='captcha']"
            ]
            
            for selector in captcha_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    self.captcha_element = elements[0]
                    return True
            
            # 找不到驗證碼圖像
            return False
            
        except Exception as e:
            self.logger.error(f"檢測文字驗證碼時出錯: {str(e)}")
            return False
    
    def solve(self, driver: webdriver.Remote = None) -> bool:
        """
        解決文本驗證碼
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否成功解決
        """
        driver = driver or self.driver
        if not driver:
            self.logger.error("未提供WebDriver實例")
            return False
            
        try:
            # 定位驗證碼元素和輸入框
            captcha_element, input_element = self._locate_elements(driver)
            
            if not captcha_element or not input_element:
                self.logger.warning("未找到驗證碼元素或輸入框")
                return False
                
            # 保存驗證碼元素的引用
            self.captcha_element = captcha_element
            
            # 獲取驗證碼圖像
            captcha_image = self._get_captcha_image()
            if captcha_image is None:
                return False
                
            # 保存驗證碼樣本
            sample_path = self._save_sample(driver)
            
            # 解決驗證碼
            captcha_text = ""
            
            # 優先使用模型識別
            if self.model:
                # 從URL下載圖片
                image_path = f"{sample_path}.png"
                if hasattr(captcha_image, 'save'):
                    captcha_image.save(image_path)
                else:
                    captcha_url = captcha_element.get_attribute("src")
                    self._download_image(captcha_url, image_path)
                
                # 預處理圖片
                preprocessed_image = self._preprocess_image(image_path)
                
                if preprocessed_image is not None:
                    # 使用模型預測
                    captcha_text = self._predict(self.model, preprocessed_image)
                    self.logger.info(f"模型識別結果: {captcha_text}")
            
            # 如果模型識別失敗且安裝了 Tesseract，使用 OCR
            if not captcha_text and self.use_tesseract:
                processed_image = self._preprocess_image_for_ocr(captcha_image)
                text, confidence = self._recognize_text(processed_image)
                
                if confidence >= self.min_confidence:
                    captcha_text = text
                    self.logger.info(f"OCR識別結果: {captcha_text} (置信度: {confidence:.2f})")
            
            # 如果仍然失敗，使用外部服務
            if not captcha_text and self.use_external_service:
                captcha_url = captcha_element.get_attribute("src")
                service_result = self._solve_with_external_service(driver, captcha_url)
                if service_result.get("success"):
                    captcha_text = service_result.get("result")
                    self.logger.info(f"外部服務識別結果: {captcha_text}")
            
            # 如果還是沒有結果，請求人工輸入
            if not captcha_text:
                captcha_text = self._manual_input()
            
            # 輸入驗證碼
            if captcha_text:
                # 清空輸入框
                input_element.clear()
                
                # 模擬人工輸入
                if self.config.get('simulate_human_typing', True):
                    # 聚焦元素
                    input_element.click()
                    
                    # 人工輸入
                    for char in captcha_text:
                        ActionChains(driver).send_keys(char).perform()
                        time.sleep(0.05 + 0.15 * np.random.random())  # 隨機輸入延遲
                else:
                    # 直接輸入
                    input_element.send_keys(captcha_text)
                
                # 提交表單
                submit_button = self._locate_submit_button(driver)
                if submit_button:
                    submit_button.click()
                    time.sleep(2)  # 等待提交結果
                else:
                    # 如果找不到提交按鈕，嘗試按回車鍵
                    input_element.send_keys(Keys.RETURN)
                    time.sleep(2)
                
                # 檢查是否成功
                success = self._check_success(driver)
                if success:
                    self.logger.info("驗證碼提交成功")
                    self.save_sample(captcha_image, True)
                    self.report_result(True)
                    return True
                else:
                    self.logger.warning("驗證碼提交失敗")
                    self.save_sample(captcha_image, False)
                    self.report_result(False)
                    # 嘗試刷新驗證碼
                    self._refresh_captcha(driver)
                    return False
            
            self.report_result(False)
            return False
            
        except Exception as e:
            self.logger.error(f"解決文本驗證碼失敗: {str(e)}")
            self.report_result(False)
            return False
    
    def _get_captcha_image(self) -> Optional[Image.Image]:
        """獲取驗證碼圖像"""
        try:
            if not hasattr(self, 'captcha_element') or not self.captcha_element:
                return None
                
            # 先嘗試獲取src屬性
            src = self.captcha_element.get_attribute('src')
            
            # 如果是Base64編碼的圖像
            if src and src.startswith('data:image'):
                img_data = src.split(',')[1]
                img = Image.open(BytesIO(base64.b64decode(img_data)))
                return img
                
            # 如果是URL
            elif src and (src.startswith('http') or src.startswith('/')):
                import requests
                from PIL import Image
                from io import BytesIO
                
                if src.startswith('/'):
                    # 相對URL，需要獲取當前頁面的基本URL
                    current_url = self.driver.current_url
                    base_url = current_url.split('://', 1)[0] + '://' + current_url.split('://', 1)[1].split('/', 1)[0]
                    src = base_url + src
                
                response = requests.get(src)
                img = Image.open(BytesIO(response.content))
                return img
                
            # 無法獲取src或格式不支持，嘗試截圖
            else:
                # 截取驗證碼元素的截圖
                png_data = self.captcha_element.screenshot_as_png
                img = Image.open(BytesIO(png_data))
                return img
                
        except Exception as e:
            self.logger.error(f"獲取驗證碼圖像時出錯: {str(e)}")
            return None
    
    def _preprocess_image_for_ocr(self, img: Image.Image) -> Image.Image:
        """預處理圖像以提高OCR準確性"""
        try:
            import cv2
            
            # 轉換為OpenCV格式
            img_array = np.array(img)
            
            # 檢查是否為RGB圖像
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            else:
                img_cv = img_array.copy()
            
            # 灰度轉換
            if self.preprocessing.get('grayscale', True):
                if len(img_cv.shape) == 3:
                    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # 對比度增強
            if self.preprocessing.get('contrast_enhancement', True):
                img_cv = cv2.equalizeHist(img_cv)
            
            # 二值化
            if self.preprocessing.get('threshold', True):
                _, img_cv = cv2.threshold(
                    img_cv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )
            
            # 噪點移除
            if self.preprocessing.get('noise_reduction', True):
                kernel = np.ones((1, 1), np.uint8)
                img_cv = cv2.morphologyEx(img_cv, cv2.MORPH_OPEN, kernel)
                img_cv = cv2.medianBlur(img_cv, 3)
            
            # 轉回PIL格式
            processed_image = Image.fromarray(img_cv)
            return processed_image
            
        except ImportError:
            self.logger.warning("未安裝OpenCV，將使用原始圖像")
            return img
        except Exception as e:
            self.logger.error(f"預處理圖像時出錯: {str(e)}")
            return img
    
    def _recognize_text(self, img: Image.Image) -> Tuple[str, float]:
        """使用OCR引擎識別文字"""
        # 構建OCR配置
        if not self.use_tesseract:
            return "", 0.0
            
        try:
            import pytesseract
            
            config = f"-l {self.tesseract_config.get('lang', 'eng')} {self.tesseract_config.get('config', '--psm 7')}"
            
            # 添加字符白名單和黑名單
            if self.char_whitelist:
                config += f" -c tessedit_char_whitelist={self.char_whitelist}"
            if self.char_blacklist:
                config += f" -c tessedit_char_blacklist={self.char_blacklist}"
            
            # 執行OCR
            result = pytesseract.image_to_data(
                img, config=config, output_type=pytesseract.Output.DICT
            )
            
            # 提取結果和置信度
            text_parts = []
            confidence_sum = 0
            word_count = 0
            
            for i in range(len(result['text'])):
                if not result['text'][i].strip():
                    continue
                
                text_parts.append(result['text'][i])
                confidence_sum += float(result['conf'][i])
                word_count += 1
            
            if not word_count:
                return "", 0.0
                
            complete_text = ''.join(text_parts)
            avg_confidence = confidence_sum / word_count / 100  # Tesseract的置信度是0-100，轉換為0-1
            
            return complete_text, avg_confidence
            
        except Exception as e:
            self.logger.error(f"OCR識別出錯: {str(e)}")
            return "", 0.0
    
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
                "//div[contains(@class, 'error')]",
                "//div[contains(@class, 'alert')]",
                "//span[contains(@class, 'error')]"
            ]
            
            for selector in error_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements and elements[0].is_displayed():
                    return False
            
            # 檢查是否仍顯示驗證碼輸入框
            _, input_element = self._locate_elements(driver)
            
            # 如果驗證碼輸入框已經不可見，可能表示成功
            if input_element is None or not input_element.is_displayed():
                return True
            
            # 檢查是否仍能檢測到驗證碼
            old_driver = self.driver
            self.driver = driver
            captcha_still_present = self.detect()
            self.driver = old_driver
            
            if not captcha_still_present:
                return True
                
            # 默認情況下，如果沒有明確的錯誤提示，認為提交成功
            return True
            
        except Exception as e:
            self.logger.error(f"檢查驗證碼提交結果失敗: {str(e)}")
            return False

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
                "//div[contains(@class, 'error')]",
                "//div[contains(@class, 'alert')]",
                "//span[contains(@class, 'error')]"
            ]
            
            for selector in error_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements and elements[0].is_displayed():
                    return False
            
            # 檢查是否仍顯示驗證碼輸入框
            _, input_element = self._locate_elements(driver)
            
            # 如果驗證碼輸入框已經不可見，可能表示成功
            if input_element is None or not input_element.is_displayed():
                return True
            
            # 檢查是否仍能檢測到驗證碼
            old_driver = self.driver
            self.driver = driver
            captcha_still_present = self.detect()
            self.driver = old_driver
            
            if not captcha_still_present:
                return True
                
            # 默認情況下，如果沒有明確的錯誤提示，認為提交成功
            return True
            
        except Exception as e:
            self.logger.error(f"檢查驗證碼提交結果失敗: {str(e)}")
            return False

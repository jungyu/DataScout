import cv2
import numpy as np
import pytesseract
from PIL import Image
from io import BytesIO
import base64
from typing import Optional, Tuple, Dict, Any

from .base_solver import BaseCaptchaSolver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TextCaptchaSolver(BaseCaptchaSolver):
    """文字驗證碼解決器"""
    
    def setup(self):
        """設置OCR引擎和預處理參數"""
        # 配置Tesseract
        self.tesseract_config = self.config.get('tesseract_config', {})
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_config.get(
            'cmd_path', pytesseract.pytesseract.tesseract_cmd
        )
        
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
    
    def detect(self) -> bool:
        """檢測頁面上是否存在文字驗證碼"""
        try:
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
    
    def solve(self) -> bool:
        """解決文字驗證碼"""
        try:
            # 獲取驗證碼圖像
            captcha_image = self._get_captcha_image()
            if captcha_image is None:
                return False
                
            # 預處理圖像
            processed_image = self._preprocess_image(captcha_image)
            
            # OCR識別
            text, confidence = self._recognize_text(processed_image)
            
            if confidence < self.min_confidence:
                self.logger.warning(
                    f"驗證碼識別置信度過低 ({confidence:.2f} < {self.min_confidence})"
                )
                self.save_sample(captcha_image, False)
                
                # 嘗試第三方服務解決
                if self.config.get('fallback_to_service', False):
                    return self._solve_with_service()
                return False
                
            # 填寫驗證碼
            self._input_captcha_text(text)
            
            # 提交驗證碼
            success = self._submit_captcha()
            self.report_result(success)
            
            # 如果成功，保存正確樣本
            if success:
                self.save_sample(captcha_image, True)
                
            return success
            
        except Exception as e:
            self.logger.error(f"解決文字驗證碼時出錯: {str(e)}")
            self.report_result(False)
            return False
    
    def _get_captcha_image(self) -> Optional[Image.Image]:
        """獲取驗證碼圖像"""
        try:
            # 先嘗試獲取src屬性
            src = self.captcha_element.get_attribute('src')
            
            # 如果是Base64編碼的圖像
            if src.startswith('data:image'):
                img_data = src.split(',')[1]
                img = Image.open(BytesIO(base64.b64decode(img_data)))
                return img
                
            # 如果是URL
            elif src.startswith('http'):
                import requests
                from PIL import Image
                from io import BytesIO
                
                response = requests.get(src)
                img = Image.open(BytesIO(response.content))
                return img
                
            # 無法獲取src或格式不支持，嘗試截圖
            else:
                img = self._take_captcha_screenshot()
                return img
                
        except Exception as e:
            self.logger.error(f"獲取驗證碼圖像時出錯: {str(e)}")
            return None
    
    def _preprocess_image(self, img: Image.Image) -> Image.Image:
        """預處理圖像以提高OCR準確性"""
        # 轉換為OpenCV格式
        img_array = np.array(img)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # 灰度轉換
        if self.preprocessing.get('grayscale', True):
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
    
    def _recognize_text(self, img: Image.Image) -> Tuple[str, float]:
        """使用OCR引擎識別文字"""
        # 構建OCR配置
        config = f"-l {self.tesseract_config.get('lang', 'eng')} {self.tesseract_config.get('config', '--psm 7')}"
        
        # 添加字符白名單和黑名單
        if self.char_whitelist:
            config += f" -c tessedit_char_whitelist={self.char_whitelist}"
        if self.char_blacklist:
            config += f" -c tessedit_char_blacklist={self.char_blacklist}"
        
        # 執行OCR
        try:
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
    
    def _input_captcha_text(self, text: str):
        """將識別的文字輸入到驗證碼輸入框"""
        try:
            # 尋找輸入框
            input_selectors = [
                "input[id*='captcha']",
                "input[name*='captcha']",
                "input[placeholder*='captcha']",
                "input[placeholder*='驗證碼']",
                "input[aria-label*='captcha']",
                "input[class*='captcha']",
                # 在驗證碼圖片附近的輸入框
                "//img[contains(@id, 'captcha') or contains(@src, 'captcha')]/following::input[1]",
                "//img[contains(@id, 'captcha') or contains(@src, 'captcha')]/preceding::input[1]",
                "//img[contains(@id, 'captcha') or contains(@src, 'captcha')]/parent::*/following::input[1]",
                "//img[contains(@id, 'captcha') or contains(@src, 'captcha')]/parent::*/preceding::input[1]"
            ]
            
            input_element = None
            
            # 嘗試CSS選擇器
            for selector in input_selectors[:5]:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    input_element = elements[0]
                    break
            
            # 嘗試XPath選擇器
            if input_element is None:
                for selector in input_selectors[5:]:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        input_element = elements[0]
                        break
            
            if input_element is None:
                self.logger.error("找不到驗證碼輸入框")
                return False
            
            # 清除輸入框
            input_element.clear()
            
            # 模擬人工輸入
            if self.config.get('simulate_human_typing', True):
                from selenium.webdriver.common.action_chains import ActionChains
                import random
                import time
                
                # 聚焦元素
                input_element.click()
                
                # 人工輸入
                for char in text:
                    ActionChains(self.driver).send_keys(char).perform()
                    time.sleep(random.uniform(0.05, 0.2))  # 隨機輸入延遲
            else:
                # 直接輸入
                input_element.send_keys(text)
                
            return True
            
        except Exception as e:
            self.logger.error(f"輸入驗證碼文字時出錯: {str(e)}")
            return False
    
    def _submit_captcha(self) -> bool:
        """提交驗證碼並檢查結果"""
        try:
            # 尋找提交按鈕
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('確認')",
                "button:contains('提交')",
                "button:contains('Submit')",
                "button:contains('Verify')",
                "//button[contains(text(), '確認') or contains(text(), '提交') or contains(text(), 'Submit') or contains(text(), 'Verify')]",
                "//input[@value='確認' or @value='提交' or @value='Submit' or @value='Verify']"
            ]
            
            submit_button = None
            
            # 嘗試CSS選擇器
            for selector in submit_selectors[:5]:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    submit_button = elements[0]
                    break
            
            # 嘗試XPath選擇器
            if submit_button is None:
                for selector in submit_selectors[5:]:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        submit_button = elements[0]
                        break
            
            # 如果找不到提交按鈕，嘗試按回車鍵
            if submit_button is None:
                self.logger.warning("找不到提交按鈕，嘗試按回車鍵")
                from selenium.webdriver.common.keys import Keys
                
                # 找到輸入框按回車
                input_selectors = [
                    "input[id*='captcha']",
                    "input[name*='captcha']"
                ]
                
                for selector in input_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        elements[0].send_keys(Keys.RETURN)
                        break
            else:
                # 點擊提交按鈕
                submit_button.click()
            
            # 等待頁面變化
            import time
            time.sleep(2)  # 簡單等待
            
            # 檢查是否成功（通過檢查驗證碼是否還在頁面上）
            if self.detect():
                # 檢查是否有錯誤消息
                error_selectors = [
                    ".error",
                    ".alert",
                    ".captcha-error",
                    "//div[contains(text(), '驗證碼錯誤') or contains(text(), '驗證碼不正確') or contains(text(), 'Incorrect captcha')]"
                ]
                
                for selector in error_selectors:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                    if elements:
                        self.logger.warning(f"驗證碼提交失敗: {elements[0].text}")
                        return False
                
                # 驗證碼還在但沒有錯誤消息，可能是尚未提交成功
                self.logger.warning("驗證碼仍然存在，但未檢測到錯誤消息")
                return False
            else:
                # 驗證碼不存在了，可能提交成功
                self.logger.info("驗證碼已不存在，可能提交成功")
                return True
                
        except Exception as e:
            self.logger.error(f"提交驗證碼時出錯: {str(e)}")
            return False
    
    def _solve_with_service(self) -> bool:
        """使用第三方服務解決驗證碼"""
        # 檢查是否配置了第三方服務
        if not self.config.get('service_providers', {}).get('enabled', False):
            self.logger.warning("未配置第三方服務")
            return False
            
        try:
            # 獲取驗證碼圖像
            captcha_image = self._get_captcha_image()
            if captcha_image is None:
                return False
                
            # 準備圖像數據
            img_byte_arr = BytesIO()
            captcha_image.save(img_byte_arr, format='PNG')
            image_data = img_byte_arr.getvalue()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 調用第三方服務
            service_name = self.config.get('service_providers', {}).get('default_service', '2captcha')
            
            if service_name == '2captcha':
                result = self._solve_with_2captcha(image_base64)
            elif service_name == 'anti_captcha':
                result = self._solve_with_anticaptcha(image_base64)
            else:
                self.logger.error(f"不支持的第三方服務: {service_name}")
                return False
                
            if not result:
                return False
                
            # 輸入結果
            self._input_captcha_text(result)
            
            # 提交驗證碼
            success = self._submit_captcha()
            self.report_result(success)
            
            return success
            
        except Exception as e:
            self.logger.error(f"使用第三方服務解決驗證碼時出錯: {str(e)}")
            return False
    
    def _solve_with_2captcha(self, image_base64: str) -> Optional[str]:
        """使用2captcha服務解決驗證碼"""
        try:
            import requests
            import time
            
            # 獲取API密鑰
            api_key = self.config.get('service_providers', {}).get('2captcha', {}).get('api_key')
            if not api_key:
                self.logger.error("未配置2captcha API密鑰")
                return None
                
            # 發送圖像到2captcha
            url = "https://2captcha.com/in.php"
            data = {
                "key": api_key,
                "method": "base64",
                "body": image_base64,
                "json": 1
            }
            
            # 添加字符白名單和黑名單
            if self.char_whitelist:
                data["textinstructions"] = f"Whitelist: {self.char_whitelist}"
            
            response = requests.post(url, data=data)
            json_response = response.json()
            
            if json_response['status'] != 1:
                self.logger.error(f"2captcha提交驗證碼失敗: {json_response['request']}")
                return None
                
            # 獲取結果ID
            captcha_id = json_response['request']
            
            # 等待結果
            url = f"https://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}&json=1"
            max_attempts = 30  # 最多等待30次，每次5秒
            
            for _ in range(max_attempts):
                time.sleep(5)  # 每5秒檢查一次結果
                
                response = requests.get(url)
                json_response = response.json()
                
                if json_response['status'] == 1:
                    # 成功獲取結果
                    return json_response['request']
                    
                if json_response['request'] != 'CAPCHA_NOT_READY':
                    # 出現錯誤
                    self.logger.error(f"2captcha獲取結果失敗: {json_response['request']}")
                    return None
            
            self.logger.error("2captcha解決驗證碼超時")
            return None
            
        except Exception as e:
            self.logger.error(f"使用2captcha解決驗證碼時出錯: {str(e)}")
            return None
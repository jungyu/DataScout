#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼模組測試

此模組提供所有驗證碼相關功能的測試用例，包括：
1. 驗證碼類型測試
2. 驗證碼處理器測試
3. 驗證碼識別測試
4. 驗證碼錯誤處理測試
"""

import unittest
from unittest.mock import Mock, patch
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.captcha.types import CaptchaType
from src.captcha.handlers import (
    TextCaptchaHandler,
    ImageCaptchaHandler,
    AudioCaptchaHandler,
    SliderCaptchaHandler
)
from src.captcha.utils.error_handler import CaptchaError
from src.core.utils.browser_utils import BrowserUtils

class TestCaptchaType(unittest.TestCase):
    """驗證碼類型測試"""
    
    def test_captcha_type_enum(self):
        """測試驗證碼類型枚舉"""
        # 測試所有驗證碼類型
        self.assertEqual(CaptchaType.TEXT.value, "text")
        self.assertEqual(CaptchaType.IMAGE.value, "image")
        self.assertEqual(CaptchaType.AUDIO.value, "audio")
        self.assertEqual(CaptchaType.SLIDER.value, "slider")
        
        # 測試從字符串獲取類型
        self.assertEqual(CaptchaType.from_string("text"), CaptchaType.TEXT)
        self.assertEqual(CaptchaType.from_string("image"), CaptchaType.IMAGE)
        self.assertEqual(CaptchaType.from_string("audio"), CaptchaType.AUDIO)
        self.assertEqual(CaptchaType.from_string("slider"), CaptchaType.SLIDER)
        
        # 測試無效類型
        with self.assertRaises(ValueError):
            CaptchaType.from_string("invalid_type")

class TestTextCaptchaHandler(unittest.TestCase):
    """文本驗證碼處理器測試"""
    
    def setUp(self):
        self.driver = Mock(spec=webdriver.Remote)
        self.browser_utils = BrowserUtils(self.driver)
        self.handler = TextCaptchaHandler(self.driver, self.browser_utils)
    
    def test_detect_captcha(self):
        """測試驗證碼檢測"""
        # 模擬驗證碼元素
        captcha_element = Mock()
        captcha_element.is_displayed.return_value = True
        captcha_element.text = "請輸入驗證碼"
        
        self.driver.find_element.return_value = captcha_element
        
        # 測試檢測
        result = self.handler.detect_captcha()
        self.assertTrue(result)
        
        # 測試無驗證碼情況
        self.driver.find_element.side_effect = Exception("元素未找到")
        result = self.handler.detect_captcha()
        self.assertFalse(result)
    
    def test_solve_captcha(self):
        """測試驗證碼解決"""
        # 模擬驗證碼元素和輸入框
        captcha_element = Mock()
        input_element = Mock()
        
        self.driver.find_elements.return_value = [captcha_element, input_element]
        
        # 模擬驗證碼文本
        captcha_element.text = "1234"
        
        # 測試解決
        result = self.handler.solve_captcha()
        self.assertTrue(result)
        
        # 驗證輸入
        input_element.send_keys.assert_called_once_with("1234")
        
        # 測試無效驗證碼
        captcha_element.text = ""
        with self.assertRaises(CaptchaError):
            self.handler.solve_captcha()

class TestImageCaptchaHandler(unittest.TestCase):
    """圖片驗證碼處理器測試"""
    
    def setUp(self):
        self.driver = Mock(spec=webdriver.Remote)
        self.browser_utils = BrowserUtils(self.driver)
        self.handler = ImageCaptchaHandler(self.driver, self.browser_utils)
    
    @patch('src.captcha.utils.image_processor.ImageProcessor')
    def test_detect_captcha(self, mock_image_processor):
        """測試驗證碼檢測"""
        # 模擬驗證碼圖片元素
        image_element = Mock()
        image_element.is_displayed.return_value = True
        image_element.screenshot_as_png = b"fake_image_data"
        
        self.driver.find_element.return_value = image_element
        
        # 測試檢測
        result = self.handler.detect_captcha()
        self.assertTrue(result)
        
        # 測試無驗證碼情況
        self.driver.find_element.side_effect = Exception("元素未找到")
        result = self.handler.detect_captcha()
        self.assertFalse(result)
    
    @patch('src.captcha.utils.image_processor.ImageProcessor')
    def test_solve_captcha(self, mock_image_processor):
        """測試驗證碼解決"""
        # 模擬驗證碼圖片元素和輸入框
        image_element = Mock()
        input_element = Mock()
        
        self.driver.find_elements.return_value = [image_element, input_element]
        image_element.screenshot_as_png = b"fake_image_data"
        
        # 模擬圖片處理結果
        mock_processor = mock_image_processor.return_value
        mock_processor.process_image.return_value = "1234"
        
        # 測試解決
        result = self.handler.solve_captcha()
        self.assertTrue(result)
        
        # 驗證輸入
        input_element.send_keys.assert_called_once_with("1234")
        
        # 測試處理失敗
        mock_processor.process_image.side_effect = Exception("處理失敗")
        with self.assertRaises(CaptchaError):
            self.handler.solve_captcha()

class TestAudioCaptchaHandler(unittest.TestCase):
    """音頻驗證碼處理器測試"""
    
    def setUp(self):
        self.driver = Mock(spec=webdriver.Remote)
        self.browser_utils = BrowserUtils(self.driver)
        self.handler = AudioCaptchaHandler(self.driver, self.browser_utils)
    
    @patch('src.captcha.utils.audio_processor.AudioProcessor')
    def test_detect_captcha(self, mock_audio_processor):
        """測試驗證碼檢測"""
        # 模擬音頻元素
        audio_element = Mock()
        audio_element.is_displayed.return_value = True
        audio_element.get_attribute.return_value = "fake_audio_url"
        
        self.driver.find_element.return_value = audio_element
        
        # 測試檢測
        result = self.handler.detect_captcha()
        self.assertTrue(result)
        
        # 測試無驗證碼情況
        self.driver.find_element.side_effect = Exception("元素未找到")
        result = self.handler.detect_captcha()
        self.assertFalse(result)
    
    @patch('src.captcha.utils.audio_processor.AudioProcessor')
    def test_solve_captcha(self, mock_audio_processor):
        """測試驗證碼解決"""
        # 模擬音頻元素和輸入框
        audio_element = Mock()
        input_element = Mock()
        
        self.driver.find_elements.return_value = [audio_element, input_element]
        audio_element.get_attribute.return_value = "fake_audio_url"
        
        # 模擬音頻處理結果
        mock_processor = mock_audio_processor.return_value
        mock_processor.process_audio.return_value = "1234"
        
        # 測試解決
        result = self.handler.solve_captcha()
        self.assertTrue(result)
        
        # 驗證輸入
        input_element.send_keys.assert_called_once_with("1234")
        
        # 測試處理失敗
        mock_processor.process_audio.side_effect = Exception("處理失敗")
        with self.assertRaises(CaptchaError):
            self.handler.solve_captcha()

class TestSliderCaptchaHandler(unittest.TestCase):
    """滑塊驗證碼處理器測試"""
    
    def setUp(self):
        self.driver = Mock(spec=webdriver.Remote)
        self.browser_utils = BrowserUtils(self.driver)
        self.handler = SliderCaptchaHandler(self.driver, self.browser_utils)
    
    def test_detect_captcha(self):
        """測試驗證碼檢測"""
        # 模擬滑塊元素
        slider_element = Mock()
        slider_element.is_displayed.return_value = True
        
        self.driver.find_element.return_value = slider_element
        
        # 測試檢測
        result = self.handler.detect_captcha()
        self.assertTrue(result)
        
        # 測試無驗證碼情況
        self.driver.find_element.side_effect = Exception("元素未找到")
        result = self.handler.detect_captcha()
        self.assertFalse(result)
    
    def test_solve_captcha(self):
        """測試驗證碼解決"""
        # 模擬滑塊元素
        slider_element = Mock()
        slider_element.size = {"width": 100, "height": 40}
        slider_element.location = {"x": 0, "y": 0}
        
        self.driver.find_element.return_value = slider_element
        
        # 測試解決
        result = self.handler.solve_captcha()
        self.assertTrue(result)
        
        # 驗證滑動
        self.driver.execute_script.assert_called()
        
        # 測試滑動失敗
        self.driver.execute_script.side_effect = Exception("滑動失敗")
        with self.assertRaises(CaptchaError):
            self.handler.solve_captcha()

if __name__ == '__main__':
    unittest.main()

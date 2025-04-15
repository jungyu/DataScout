#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文本提取器測試模組

提供文本提取器的單元測試，包括：
1. 配置驗證
2. 文本定位
3. 文本提取
4. 文本清理
5. 文本驗證
"""

import unittest
from unittest.mock import Mock, patch
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..handlers.text import TextExtractor, TextExtractorConfig
from ..core.error import ExtractorError

class TestTextExtractor(unittest.TestCase):
    """文本提取器測試類別"""
    
    def setUp(self):
        """設置測試環境"""
        self.config = TextExtractorConfig(
            text_selector="p",
            wait_timeout=1.0,
            strip_whitespace=True,
            remove_special_chars=True,
            remove_extra_spaces=True,
            remove_html_tags=True,
            extract_links=True,
            extract_emails=True,
            extract_phones=True,
            extract_dates=True,
            extract_numbers=True,
            min_length=0,
            max_length=None,
            error_on_empty=True,
            error_on_invalid=True,
            error_on_timeout=True,
            retry_on_error=True,
            retry_count=3,
            retry_delay=0.1
        )
        self.extractor = TextExtractor(config=self.config)
        self.driver = Mock()
        
    def test_validate_config(self):
        """測試配置驗證"""
        # 測試有效配置
        self.assertTrue(self.extractor._validate_config())
        
        # 測試無效選擇器
        self.config.text_selector = ""
        self.assertFalse(self.extractor._validate_config())
        self.config.text_selector = "p"
        
        # 測試無效超時時間
        self.config.wait_timeout = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.wait_timeout = 1.0
        
        # 測試無效長度限制
        self.config.min_length = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.min_length = 0
        
        self.config.max_length = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.max_length = None
        
        # 測試無效重試次數
        self.config.retry_count = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.retry_count = 3
        
    def test_find_text_elements(self):
        """測試查找文本元素"""
        # 模擬成功查找
        mock_elements = [Mock(), Mock()]
        self.driver.find_elements.return_value = mock_elements
        WebDriverWait.until.return_value = mock_elements
        
        elements = self.extractor.find_text_elements(self.driver)
        self.assertEqual(elements, mock_elements)
        
        # 模擬超時
        WebDriverWait.until.side_effect = TimeoutException()
        elements = self.extractor.find_text_elements(self.driver)
        self.assertEqual(elements, [])
        
        # 模擬錯誤
        self.config.error_on_timeout = True
        with self.assertRaises(ExtractorError):
            self.extractor.find_text_elements(self.driver)
            
    def test_clean_text(self):
        """測試文本清理"""
        # 測試空白字符處理
        text = "  Hello  World  "
        cleaned = self.extractor.clean_text(text)
        self.assertEqual(cleaned, "Hello World")
        
        # 測試特殊字符處理
        text = "Hello! @#$%^&*() World"
        cleaned = self.extractor.clean_text(text)
        self.assertEqual(cleaned, "Hello World")
        
        # 測試HTML標籤處理
        text = "<p>Hello <b>World</b></p>"
        cleaned = self.extractor.clean_text(text)
        self.assertEqual(cleaned, "Hello World")
        
        # 測試多餘空格處理
        text = "Hello    World"
        cleaned = self.extractor.clean_text(text)
        self.assertEqual(cleaned, "Hello World")
        
    def test_extract_links(self):
        """測試提取鏈接"""
        # 測試有效鏈接
        text = "Visit https://example.com and http://test.com"
        links = self.extractor.extract_links(text)
        self.assertEqual(links, ["https://example.com", "http://test.com"])
        
        # 測試無效鏈接
        text = "Visit example.com and test.com"
        links = self.extractor.extract_links(text)
        self.assertEqual(links, [])
        
        # 測試空文本
        text = ""
        links = self.extractor.extract_links(text)
        self.assertEqual(links, [])
        
    def test_extract_emails(self):
        """測試提取郵箱"""
        # 測試有效郵箱
        text = "Contact us at test@example.com and support@test.com"
        emails = self.extractor.extract_emails(text)
        self.assertEqual(emails, ["test@example.com", "support@test.com"])
        
        # 測試無效郵箱
        text = "Contact us at test@ and support@test"
        emails = self.extractor.extract_emails(text)
        self.assertEqual(emails, [])
        
        # 測試空文本
        text = ""
        emails = self.extractor.extract_emails(text)
        self.assertEqual(emails, [])
        
    def test_extract_phones(self):
        """測試提取電話"""
        # 測試有效電話
        text = "Call us at 123-456-7890 and (987) 654-3210"
        phones = self.extractor.extract_phones(text)
        self.assertEqual(phones, ["123-456-7890", "(987) 654-3210"])
        
        # 測試無效電話
        text = "Call us at 123 and 987"
        phones = self.extractor.extract_phones(text)
        self.assertEqual(phones, [])
        
        # 測試空文本
        text = ""
        phones = self.extractor.extract_phones(text)
        self.assertEqual(phones, [])
        
    def test_extract_dates(self):
        """測試提取日期"""
        # 測試有效日期
        text = "Date: 2023-01-01 and 01/01/2023"
        dates = self.extractor.extract_dates(text)
        self.assertEqual(dates, ["2023-01-01", "01/01/2023"])
        
        # 測試無效日期
        text = "Date: 2023-13-01 and 01/13/2023"
        dates = self.extractor.extract_dates(text)
        self.assertEqual(dates, [])
        
        # 測試空文本
        text = ""
        dates = self.extractor.extract_dates(text)
        self.assertEqual(dates, [])
        
    def test_extract_numbers(self):
        """測試提取數字"""
        # 測試有效數字
        text = "Numbers: 123, 456.78, -90"
        numbers = self.extractor.extract_numbers(text)
        self.assertEqual(numbers, ["123", "456.78", "-90"])
        
        # 測試無效數字
        text = "Numbers: abc, def, ghi"
        numbers = self.extractor.extract_numbers(text)
        self.assertEqual(numbers, [])
        
        # 測試空文本
        text = ""
        numbers = self.extractor.extract_numbers(text)
        self.assertEqual(numbers, [])
        
    def test_validate_text(self):
        """測試文本驗證"""
        # 測試有效文本
        text = "Hello World"
        self.assertTrue(self.extractor.validate_text(text))
        
        # 測試空文本
        text = ""
        self.assertFalse(self.extractor.validate_text(text))
        
        # 測試長度限制
        self.config.min_length = 10
        text = "Hello"
        self.assertFalse(self.extractor.validate_text(text))
        
        self.config.max_length = 5
        text = "Hello World"
        self.assertFalse(self.extractor.validate_text(text))
        
    def test_extract(self):
        """測試文本提取"""
        # 模擬成功提取
        mock_elements = [Mock(), Mock()]
        mock_elements[0].text = "Hello World"
        mock_elements[1].text = "Visit https://example.com"
        
        self.driver.find_elements.return_value = mock_elements
        WebDriverWait.until.return_value = mock_elements
        
        result = self.extractor.extract(self.driver)
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.data[0]["text"], "Hello World")
        self.assertEqual(result.data[1]["text"], "Visit https://example.com")
        self.assertEqual(result.data[1]["links"], ["https://example.com"])
        
        # 模擬提取失敗
        WebDriverWait.until.side_effect = TimeoutException()
        result = self.extractor.extract(self.driver)
        self.assertFalse(result.success)
        self.assertIsNone(result.data)
        self.assertIsNotNone(result.error)
        
if __name__ == "__main__":
    unittest.main() 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
鏈接提取器測試模組

提供鏈接提取器的單元測試，包括：
1. 配置驗證
2. 鏈接提取
3. URL處理
4. 錯誤處理
"""

import unittest
from unittest.mock import Mock, patch
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests

from ..handlers.link import LinkExtractor, LinkExtractorConfig
from ..core.error import ExtractorError

class TestLinkExtractor(unittest.TestCase):
    """鏈接提取器測試類別"""
    
    def setUp(self):
        """設置測試環境"""
        self.config = LinkExtractorConfig(
            link_selector="a",
            wait_timeout=1.0,
            base_url="https://example.com",
            normalize_urls=True,
            remove_fragments=True,
            remove_duplicates=True,
            validate_urls=True,
            check_status=False,
            follow_redirects=True,
            max_redirects=5,
            timeout=1.0,
            allowed_schemes=["http", "https"],
            allowed_domains=["example.com"],
            excluded_domains=["bad.com"],
            allowed_paths=["/path"],
            excluded_paths=["/bad"],
            allowed_extensions=[".html"],
            excluded_extensions=[".jpg"],
            extract_text=True,
            extract_title=True,
            extract_rel=True,
            extract_target=True,
            extract_href=True,
            extract_id=True,
            extract_class=True,
            extract_attributes=["data-*"],
            error_on_empty=True,
            error_on_invalid=True,
            error_on_timeout=True,
            retry_on_error=True,
            retry_count=3,
            retry_delay=0.1
        )
        self.extractor = LinkExtractor(config=self.config)
        self.driver = Mock()
        
    def test_validate_config(self):
        """測試配置驗證"""
        # 測試有效配置
        self.assertTrue(self.extractor._validate_config())
        
        # 測試無效選擇器
        self.config.link_selector = ""
        self.assertFalse(self.extractor._validate_config())
        self.config.link_selector = "a"
        
        # 測試無效重定向次數
        self.config.max_redirects = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.max_redirects = 5
        
        # 測試無效超時時間
        self.config.timeout = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.timeout = 1.0
        
        # 測試無效協議
        self.config.allowed_schemes = ["invalid"]
        self.assertFalse(self.extractor._validate_config())
        self.config.allowed_schemes = ["http", "https"]
        
    def test_find_link_elements(self):
        """測試查找鏈接元素"""
        # 模擬成功查找
        mock_elements = [Mock(), Mock()]
        self.driver.find_elements.return_value = mock_elements
        WebDriverWait.until.return_value = mock_elements
        
        elements = self.extractor.find_link_elements(self.driver)
        self.assertEqual(elements, mock_elements)
        
        # 模擬超時
        WebDriverWait.until.side_effect = TimeoutException()
        elements = self.extractor.find_link_elements(self.driver)
        self.assertEqual(elements, [])
        
        # 模擬錯誤
        self.config.error_on_timeout = True
        with self.assertRaises(ExtractorError):
            self.extractor.find_link_elements(self.driver)
            
    def test_get_link_info(self):
        """測試獲取鏈接信息"""
        # 創建模擬元素
        element = Mock()
        element.text = "Link Text"
        element.get_attribute.side_effect = lambda attr: {
            "title": "Link Title",
            "rel": "nofollow",
            "target": "_blank",
            "href": "https://example.com/path",
            "id": "link1",
            "class": "link-class"
        }.get(attr, "")
        element.get_property.return_value = {
            "attributes": {
                "data-test": "value",
                "aria-label": "Label"
            }
        }
        
        info = self.extractor._get_link_info(element)
        self.assertEqual(info["text"], "Link Text")
        self.assertEqual(info["title"], "Link Title")
        self.assertEqual(info["rel"], "nofollow")
        self.assertEqual(info["target"], "_blank")
        self.assertEqual(info["href"], "https://example.com/path")
        self.assertEqual(info["id"], "link1")
        self.assertEqual(info["class"], "link-class")
        self.assertEqual(info["data-test"], "value")
        self.assertEqual(info["aria-label"], "Label")
        
    def test_normalize_url(self):
        """測試URL標準化"""
        # 測試空URL
        self.assertEqual(self.extractor._normalize_url(""), "")
        
        # 測試相對URL
        url = "/path"
        normalized = self.extractor._normalize_url(url)
        self.assertEqual(normalized, "https://example.com/path")
        
        # 測試帶片段的URL
        url = "https://example.com/path#fragment"
        normalized = self.extractor._normalize_url(url)
        self.assertEqual(normalized, "https://example.com/path")
        
        # 測試空白字符
        url = "  https://example.com/path  "
        normalized = self.extractor._normalize_url(url)
        self.assertEqual(normalized, "https://example.com/path")
        
    def test_validate_url(self):
        """測試URL驗證"""
        # 測試空URL
        self.assertFalse(self.extractor._validate_url(""))
        
        # 測試有效URL
        url = "https://example.com/path.html"
        self.assertTrue(self.extractor._validate_url(url))
        
        # 測試無效協議
        url = "ftp://example.com/path.html"
        self.assertFalse(self.extractor._validate_url(url))
        
        # 測試無效域名
        url = "https://bad.com/path.html"
        self.assertFalse(self.extractor._validate_url(url))
        
        # 測試無效路徑
        url = "https://example.com/bad/path.html"
        self.assertFalse(self.extractor._validate_url(url))
        
        # 測試無效擴展名
        url = "https://example.com/path.jpg"
        self.assertFalse(self.extractor._validate_url(url))
        
    @patch("requests.head")
    def test_check_url_status(self, mock_head):
        """測試URL狀態檢查"""
        # 模擬成功響應
        mock_response = Mock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response
        
        status = self.extractor._check_url_status("https://example.com")
        self.assertEqual(status, 200)
        
        # 模擬錯誤響應
        mock_head.side_effect = requests.RequestException()
        with self.assertRaises(ExtractorError):
            self.extractor._check_url_status("https://example.com")
            
    def test_extract(self):
        """測試鏈接提取"""
        # 模擬成功提取
        mock_elements = [Mock(), Mock()]
        self.driver.find_elements.return_value = mock_elements
        WebDriverWait.until.return_value = mock_elements
        
        # 設置元素屬性
        for i, element in enumerate(mock_elements):
            element.text = f"Link {i}"
            element.get_attribute.side_effect = lambda attr: {
                "title": f"Title {i}",
                "rel": "nofollow",
                "target": "_blank",
                "href": f"https://example.com/path{i}.html",
                "id": f"link{i}",
                "class": "link-class"
            }.get(attr, "")
            
        result = self.extractor.extract(self.driver)
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)
        
        # 模擬提取失敗
        WebDriverWait.until.side_effect = TimeoutException()
        result = self.extractor.extract(self.driver)
        self.assertFalse(result.success)
        self.assertIsNone(result.data)
        self.assertIsNotNone(result.error)
        
if __name__ == "__main__":
    unittest.main() 
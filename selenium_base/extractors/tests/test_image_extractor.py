#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
圖像提取器測試模組

提供圖像提取器的單元測試，包括：
1. 配置驗證
2. 圖像定位
3. 圖像提取
4. 圖像驗證
5. 圖像處理
"""

import unittest
import os
from unittest.mock import Mock, patch, MagicMock
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from PIL import Image
import io

from ..handlers.image import ImageExtractor, ImageExtractorConfig
from ..core.error import ExtractorError

class TestImageExtractor(unittest.TestCase):
    """圖像提取器測試類別"""
    
    def setUp(self):
        """設置測試環境"""
        self.config = ImageExtractorConfig(
            image_selector="img",
            wait_timeout=1.0,
            download_dir="test_downloads",
            validate_size=True,
            min_width=100,
            min_height=100,
            max_width=1000,
            max_height=1000,
            validate_format=True,
            allowed_formats=["jpg", "jpeg", "png", "gif"],
            validate_integrity=True,
            resize=False,
            max_width_resize=800,
            max_height_resize=600,
            quality=85,
            extract_alt=True,
            extract_title=True,
            extract_src=True,
            extract_width=True,
            extract_height=True,
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
        self.extractor = ImageExtractor(config=self.config)
        self.driver = Mock()
        
        # 創建測試目錄
        os.makedirs(self.config.download_dir, exist_ok=True)
        
    def tearDown(self):
        """清理測試環境"""
        # 刪除測試目錄及其內容
        if os.path.exists(self.config.download_dir):
            for file in os.listdir(self.config.download_dir):
                os.remove(os.path.join(self.config.download_dir, file))
            os.rmdir(self.config.download_dir)
        
    def test_validate_config(self):
        """測試配置驗證"""
        # 測試有效配置
        self.assertTrue(self.extractor._validate_config())
        
        # 測試無效選擇器
        self.config.image_selector = ""
        self.assertFalse(self.extractor._validate_config())
        self.config.image_selector = "img"
        
        # 測試無效超時時間
        self.config.wait_timeout = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.wait_timeout = 1.0
        
        # 測試無效尺寸限制
        self.config.min_width = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.min_width = 100
        
        self.config.min_height = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.min_height = 100
        
        self.config.max_width = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.max_width = 1000
        
        self.config.max_height = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.max_height = 1000
        
        # 測試無效格式
        self.config.allowed_formats = ["invalid"]
        self.assertFalse(self.extractor._validate_config())
        self.config.allowed_formats = ["jpg", "jpeg", "png", "gif"]
        
        # 測試無效重試次數
        self.config.retry_count = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.retry_count = 3
        
    def test_find_image_elements(self):
        """測試查找圖像元素"""
        # 模擬成功查找
        mock_elements = [Mock(), Mock()]
        self.driver.find_elements.return_value = mock_elements
        WebDriverWait.until.return_value = mock_elements
        
        elements = self.extractor.find_image_elements(self.driver)
        self.assertEqual(elements, mock_elements)
        
        # 模擬超時
        WebDriverWait.until.side_effect = TimeoutException()
        elements = self.extractor.find_image_elements(self.driver)
        self.assertEqual(elements, [])
        
        # 模擬錯誤
        self.config.error_on_timeout = True
        with self.assertRaises(ExtractorError):
            self.extractor.find_image_elements(self.driver)
            
    def test_get_image_info(self):
        """測試獲取圖像信息"""
        # 創建模擬元素
        element = Mock()
        element.get_attribute.side_effect = lambda attr: {
            "alt": "Image Alt",
            "title": "Image Title",
            "src": "https://example.com/image.jpg",
            "width": "200",
            "height": "150",
            "id": "image1",
            "class": "image-class"
        }.get(attr, "")
        element.get_property.return_value = {
            "attributes": {
                "data-test": "value",
                "aria-label": "Label"
            }
        }
        
        info = self.extractor._get_image_info(element)
        self.assertEqual(info["alt"], "Image Alt")
        self.assertEqual(info["title"], "Image Title")
        self.assertEqual(info["src"], "https://example.com/image.jpg")
        self.assertEqual(info["width"], "200")
        self.assertEqual(info["height"], "150")
        self.assertEqual(info["id"], "image1")
        self.assertEqual(info["class"], "image-class")
        self.assertEqual(info["data-test"], "value")
        self.assertEqual(info["aria-label"], "Label")
        
    def test_download_image(self):
        """測試下載圖像"""
        # 創建測試圖像
        img = Image.new('RGB', (200, 150), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # 模擬請求響應
        mock_response = Mock()
        mock_response.content = img_byte_arr
        mock_response.status_code = 200
        
        with patch('requests.get', return_value=mock_response):
            # 測試成功下載
            file_path = self.extractor.download_image("https://example.com/image.jpg")
            self.assertTrue(os.path.exists(file_path))
            self.assertTrue(file_path.endswith(".jpg"))
            
            # 測試無效URL
            with self.assertRaises(ExtractorError):
                self.extractor.download_image("")
                
            # 測試請求失敗
            mock_response.status_code = 404
            with self.assertRaises(ExtractorError):
                self.extractor.download_image("https://example.com/notfound.jpg")
                
            # 測試請求異常
            with patch('requests.get', side_effect=requests.RequestException):
                with self.assertRaises(ExtractorError):
                    self.extractor.download_image("https://example.com/error.jpg")
                    
    def test_validate_image(self):
        """測試圖像驗證"""
        # 創建測試圖像
        img = Image.new('RGB', (200, 150), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # 測試有效圖像
        self.assertTrue(self.extractor.validate_image(img_byte_arr))
        
        # 測試無效圖像
        self.assertFalse(self.extractor.validate_image(b"invalid"))
        
        # 測試尺寸限制
        img = Image.new('RGB', (50, 50), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        self.assertFalse(self.extractor.validate_image(img_byte_arr))
        
        # 測試格式限制
        self.config.allowed_formats = ["png"]
        img = Image.new('RGB', (200, 150), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        self.assertFalse(self.extractor.validate_image(img_byte_arr))
        
    def test_process_image(self):
        """測試圖像處理"""
        # 創建測試圖像
        img = Image.new('RGB', (1000, 800), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=100)
        img_byte_arr = img_byte_arr.getvalue()
        
        # 測試調整大小
        self.config.resize = True
        processed = self.extractor.process_image(img_byte_arr)
        processed_img = Image.open(io.BytesIO(processed))
        self.assertLessEqual(processed_img.width, self.config.max_width_resize)
        self.assertLessEqual(processed_img.height, self.config.max_height_resize)
        
        # 測試質量調整
        self.config.resize = False
        processed = self.extractor.process_image(img_byte_arr)
        processed_size = len(processed)
        original_size = len(img_byte_arr)
        self.assertLess(processed_size, original_size)
        
    def test_save_image(self):
        """測試保存圖像"""
        # 創建測試圖像
        img = Image.new('RGB', (200, 150), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # 測試成功保存
        file_path = self.extractor.save_image(img_byte_arr, "test.jpg")
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(file_path.endswith(".jpg"))
        
        # 測試無效數據
        with self.assertRaises(ExtractorError):
            self.extractor.save_image(b"invalid", "test.jpg")
            
    def test_extract(self):
        """測試圖像提取"""
        # 創建測試圖像
        img = Image.new('RGB', (200, 150), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # 模擬成功提取
        mock_elements = [Mock(), Mock()]
        for i, element in enumerate(mock_elements):
            element.get_attribute.side_effect = lambda attr: {
                "alt": f"Image {i}",
                "title": f"Title {i}",
                "src": f"https://example.com/image{i}.jpg",
                "width": "200",
                "height": "150",
                "id": f"image{i}",
                "class": "image-class"
            }.get(attr, "")
            
        self.driver.find_elements.return_value = mock_elements
        WebDriverWait.until.return_value = mock_elements
        
        # 模擬請求響應
        mock_response = Mock()
        mock_response.content = img_byte_arr
        mock_response.status_code = 200
        
        with patch('requests.get', return_value=mock_response):
            result = self.extractor.extract(self.driver)
            self.assertTrue(result.success)
            self.assertEqual(len(result.data), 2)
            self.assertEqual(result.data[0]["alt"], "Image 0")
            self.assertEqual(result.data[0]["title"], "Title 0")
            self.assertEqual(result.data[0]["src"], "https://example.com/image0.jpg")
            self.assertTrue(os.path.exists(result.data[0]["file_path"]))
            
        # 模擬提取失敗
        WebDriverWait.until.side_effect = TimeoutException()
        result = self.extractor.extract(self.driver)
        self.assertFalse(result.success)
        self.assertIsNone(result.data)
        self.assertIsNotNone(result.error)
        
if __name__ == "__main__":
    unittest.main() 
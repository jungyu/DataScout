#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
表單提取器測試模組

提供表單提取器的單元測試，包括：
1. 配置驗證
2. 表單定位
3. 表單提取
4. 表單驗證
5. 表單處理
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement

from ..handlers.form import FormExtractor, FormExtractorConfig
from ..core.error import ExtractorError

class TestFormExtractor(unittest.TestCase):
    """表單提取器測試類別"""
    
    def setUp(self):
        """設置測試環境"""
        self.config = FormExtractorConfig(
            form_selector="form",
            wait_timeout=1.0,
            extract_action=True,
            extract_method=True,
            extract_enctype=True,
            extract_name=True,
            extract_id=True,
            extract_class=True,
            extract_attributes=["data-*"],
            extract_inputs=True,
            extract_selects=True,
            extract_textareas=True,
            extract_buttons=True,
            extract_labels=True,
            extract_validation=True,
            extract_required=True,
            extract_disabled=True,
            extract_readonly=True,
            extract_placeholder=True,
            extract_value=True,
            extract_default_value=True,
            extract_options=True,
            extract_selected=True,
            extract_multiple=True,
            extract_size=True,
            extract_maxlength=True,
            extract_pattern=True,
            extract_min=True,
            extract_max=True,
            extract_step=True,
            extract_autocomplete=True,
            extract_autofocus=True,
            extract_formnovalidate=True,
            extract_formaction=True,
            extract_formenctype=True,
            extract_formmethod=True,
            extract_formtarget=True,
            error_on_empty=True,
            error_on_invalid=True,
            error_on_timeout=True,
            retry_on_error=True,
            retry_count=3,
            retry_delay=0.1
        )
        self.extractor = FormExtractor(config=self.config)
        self.driver = Mock()
        
    def test_validate_config(self):
        """測試配置驗證"""
        # 測試有效配置
        self.assertTrue(self.extractor._validate_config())
        
        # 測試無效選擇器
        self.config.form_selector = ""
        self.assertFalse(self.extractor._validate_config())
        self.config.form_selector = "form"
        
        # 測試無效超時時間
        self.config.wait_timeout = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.wait_timeout = 1.0
        
        # 測試無效重試次數
        self.config.retry_count = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.retry_count = 3
        
    def test_find_form_elements(self):
        """測試查找表單元素"""
        # 模擬成功查找
        mock_elements = [Mock(), Mock()]
        self.driver.find_elements.return_value = mock_elements
        WebDriverWait.until.return_value = mock_elements
        
        elements = self.extractor.find_form_elements(self.driver)
        self.assertEqual(elements, mock_elements)
        
        # 模擬超時
        WebDriverWait.until.side_effect = TimeoutException()
        elements = self.extractor.find_form_elements(self.driver)
        self.assertEqual(elements, [])
        
        # 模擬錯誤
        self.config.error_on_timeout = True
        with self.assertRaises(ExtractorError):
            self.extractor.find_form_elements(self.driver)
            
    def test_get_form_info(self):
        """測試獲取表單信息"""
        # 創建模擬元素
        element = Mock()
        element.get_attribute.side_effect = lambda attr: {
            "action": "/submit",
            "method": "post",
            "enctype": "multipart/form-data",
            "name": "test-form",
            "id": "form1",
            "class": "form-class",
            "data-test": "value"
        }.get(attr, "")
        
        info = self.extractor._get_form_info(element)
        self.assertEqual(info["action"], "/submit")
        self.assertEqual(info["method"], "post")
        self.assertEqual(info["enctype"], "multipart/form-data")
        self.assertEqual(info["name"], "test-form")
        self.assertEqual(info["id"], "form1")
        self.assertEqual(info["class"], "form-class")
        self.assertEqual(info["data-test"], "value")
        
    def test_get_input_info(self):
        """測試獲取輸入框信息"""
        # 創建模擬元素
        element = Mock()
        element.get_attribute.side_effect = lambda attr: {
            "type": "text",
            "name": "username",
            "id": "user1",
            "class": "input-class",
            "value": "test",
            "placeholder": "Enter username",
            "required": "required",
            "disabled": "disabled",
            "readonly": "readonly",
            "maxlength": "50",
            "pattern": "[A-Za-z0-9]+",
            "min": "0",
            "max": "100",
            "step": "1",
            "autocomplete": "username",
            "autofocus": "autofocus",
            "formnovalidate": "formnovalidate",
            "data-test": "value"
        }.get(attr, "")
        
        info = self.extractor._get_input_info(element)
        self.assertEqual(info["type"], "text")
        self.assertEqual(info["name"], "username")
        self.assertEqual(info["id"], "user1")
        self.assertEqual(info["class"], "input-class")
        self.assertEqual(info["value"], "test")
        self.assertEqual(info["placeholder"], "Enter username")
        self.assertTrue(info["required"])
        self.assertTrue(info["disabled"])
        self.assertTrue(info["readonly"])
        self.assertEqual(info["maxlength"], "50")
        self.assertEqual(info["pattern"], "[A-Za-z0-9]+")
        self.assertEqual(info["min"], "0")
        self.assertEqual(info["max"], "100")
        self.assertEqual(info["step"], "1")
        self.assertEqual(info["autocomplete"], "username")
        self.assertTrue(info["autofocus"])
        self.assertTrue(info["formnovalidate"])
        self.assertEqual(info["data-test"], "value")
        
    def test_get_select_info(self):
        """測試獲取選擇框信息"""
        # 創建模擬元素
        element = Mock()
        element.get_attribute.side_effect = lambda attr: {
            "name": "country",
            "id": "country1",
            "class": "select-class",
            "multiple": "multiple",
            "size": "5",
            "required": "required",
            "disabled": "disabled",
            "formnovalidate": "formnovalidate",
            "data-test": "value"
        }.get(attr, "")
        
        # 創建模擬選項
        option1 = Mock()
        option1.get_attribute.side_effect = lambda attr: {
            "value": "us",
            "text": "United States",
            "selected": "selected",
            "disabled": "disabled"
        }.get(attr, "")
        
        option2 = Mock()
        option2.get_attribute.side_effect = lambda attr: {
            "value": "uk",
            "text": "United Kingdom",
            "selected": None,
            "disabled": None
        }.get(attr, "")
        
        element.find_elements.return_value = [option1, option2]
        
        info = self.extractor._get_select_info(element)
        self.assertEqual(info["name"], "country")
        self.assertEqual(info["id"], "country1")
        self.assertEqual(info["class"], "select-class")
        self.assertTrue(info["multiple"])
        self.assertEqual(info["size"], "5")
        self.assertTrue(info["required"])
        self.assertTrue(info["disabled"])
        self.assertTrue(info["formnovalidate"])
        self.assertEqual(info["data-test"], "value")
        self.assertEqual(len(info["options"]), 2)
        self.assertEqual(info["options"][0]["value"], "us")
        self.assertEqual(info["options"][0]["text"], "United States")
        self.assertTrue(info["options"][0]["selected"])
        self.assertTrue(info["options"][0]["disabled"])
        self.assertEqual(info["options"][1]["value"], "uk")
        self.assertEqual(info["options"][1]["text"], "United Kingdom")
        self.assertFalse(info["options"][1]["selected"])
        self.assertFalse(info["options"][1]["disabled"])
        
    def test_get_textarea_info(self):
        """測試獲取文本區域信息"""
        # 創建模擬元素
        element = Mock()
        element.get_attribute.side_effect = lambda attr: {
            "name": "comment",
            "id": "comment1",
            "class": "textarea-class",
            "value": "Hello World",
            "placeholder": "Enter comment",
            "required": "required",
            "disabled": "disabled",
            "readonly": "readonly",
            "maxlength": "500",
            "rows": "5",
            "cols": "50",
            "wrap": "soft",
            "autocomplete": "off",
            "autofocus": "autofocus",
            "formnovalidate": "formnovalidate",
            "data-test": "value"
        }.get(attr, "")
        
        info = self.extractor._get_textarea_info(element)
        self.assertEqual(info["name"], "comment")
        self.assertEqual(info["id"], "comment1")
        self.assertEqual(info["class"], "textarea-class")
        self.assertEqual(info["value"], "Hello World")
        self.assertEqual(info["placeholder"], "Enter comment")
        self.assertTrue(info["required"])
        self.assertTrue(info["disabled"])
        self.assertTrue(info["readonly"])
        self.assertEqual(info["maxlength"], "500")
        self.assertEqual(info["rows"], "5")
        self.assertEqual(info["cols"], "50")
        self.assertEqual(info["wrap"], "soft")
        self.assertEqual(info["autocomplete"], "off")
        self.assertTrue(info["autofocus"])
        self.assertTrue(info["formnovalidate"])
        self.assertEqual(info["data-test"], "value")
        
    def test_get_button_info(self):
        """測試獲取按鈕信息"""
        # 創建模擬元素
        element = Mock()
        element.get_attribute.side_effect = lambda attr: {
            "type": "submit",
            "name": "submit-btn",
            "id": "btn1",
            "class": "button-class",
            "value": "Submit",
            "disabled": "disabled",
            "formnovalidate": "formnovalidate",
            "formaction": "/custom-submit",
            "formenctype": "multipart/form-data",
            "formmethod": "post",
            "formtarget": "_blank",
            "data-test": "value"
        }.get(attr, "")
        
        info = self.extractor._get_button_info(element)
        self.assertEqual(info["type"], "submit")
        self.assertEqual(info["name"], "submit-btn")
        self.assertEqual(info["id"], "btn1")
        self.assertEqual(info["class"], "button-class")
        self.assertEqual(info["value"], "Submit")
        self.assertTrue(info["disabled"])
        self.assertTrue(info["formnovalidate"])
        self.assertEqual(info["formaction"], "/custom-submit")
        self.assertEqual(info["formenctype"], "multipart/form-data")
        self.assertEqual(info["formmethod"], "post")
        self.assertEqual(info["formtarget"], "_blank")
        self.assertEqual(info["data-test"], "value")
        
    def test_get_label_info(self):
        """測試獲取標籤信息"""
        # 創建模擬元素
        element = Mock()
        element.get_attribute.side_effect = lambda attr: {
            "for": "username",
            "id": "label1",
            "class": "label-class",
            "data-test": "value"
        }.get(attr, "")
        element.text = "Username:"
        
        info = self.extractor._get_label_info(element)
        self.assertEqual(info["for"], "username")
        self.assertEqual(info["id"], "label1")
        self.assertEqual(info["class"], "label-class")
        self.assertEqual(info["data-test"], "value")
        self.assertEqual(info["text"], "Username:")
        
    def test_extract(self):
        """測試表單提取"""
        # 創建模擬表單元素
        form = Mock()
        form.get_attribute.side_effect = lambda attr: {
            "action": "/submit",
            "method": "post",
            "enctype": "multipart/form-data",
            "name": "test-form",
            "id": "form1",
            "class": "form-class"
        }.get(attr, "")
        
        # 創建模擬輸入框
        input_element = Mock()
        input_element.get_attribute.side_effect = lambda attr: {
            "type": "text",
            "name": "username",
            "id": "user1",
            "value": "test"
        }.get(attr, "")
        
        # 創建模擬選擇框
        select_element = Mock()
        select_element.get_attribute.side_effect = lambda attr: {
            "name": "country",
            "id": "country1"
        }.get(attr, "")
        
        # 創建模擬選項
        option = Mock()
        option.get_attribute.side_effect = lambda attr: {
            "value": "us",
            "text": "United States",
            "selected": "selected"
        }.get(attr, "")
        select_element.find_elements.return_value = [option]
        
        # 創建模擬文本區域
        textarea_element = Mock()
        textarea_element.get_attribute.side_effect = lambda attr: {
            "name": "comment",
            "id": "comment1",
            "value": "Hello World"
        }.get(attr, "")
        
        # 創建模擬按鈕
        button_element = Mock()
        button_element.get_attribute.side_effect = lambda attr: {
            "type": "submit",
            "name": "submit-btn",
            "id": "btn1",
            "value": "Submit"
        }.get(attr, "")
        
        # 創建模擬標籤
        label_element = Mock()
        label_element.get_attribute.side_effect = lambda attr: {
            "for": "username",
            "id": "label1"
        }.get(attr, "")
        label_element.text = "Username:"
        
        # 設置表單子元素
        form.find_elements.side_effect = lambda by, value: {
            (By.TAG_NAME, "input"): [input_element],
            (By.TAG_NAME, "select"): [select_element],
            (By.TAG_NAME, "textarea"): [textarea_element],
            (By.TAG_NAME, "button"): [button_element],
            (By.TAG_NAME, "label"): [label_element]
        }.get((by, value), [])
        
        # 設置驅動程序返回值
        self.driver.find_elements.return_value = [form]
        WebDriverWait.until.return_value = [form]
        
        # 執行提取
        result = self.extractor.extract(self.driver)
        
        # 驗證結果
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data), 1)
        form_data = result.data[0]
        
        # 驗證表單基本信息
        self.assertEqual(form_data["action"], "/submit")
        self.assertEqual(form_data["method"], "post")
        self.assertEqual(form_data["enctype"], "multipart/form-data")
        self.assertEqual(form_data["name"], "test-form")
        self.assertEqual(form_data["id"], "form1")
        self.assertEqual(form_data["class"], "form-class")
        
        # 驗證輸入框
        self.assertEqual(len(form_data["inputs"]), 1)
        input_data = form_data["inputs"][0]
        self.assertEqual(input_data["type"], "text")
        self.assertEqual(input_data["name"], "username")
        self.assertEqual(input_data["id"], "user1")
        self.assertEqual(input_data["value"], "test")
        
        # 驗證選擇框
        self.assertEqual(len(form_data["selects"]), 1)
        select_data = form_data["selects"][0]
        self.assertEqual(select_data["name"], "country")
        self.assertEqual(select_data["id"], "country1")
        self.assertEqual(len(select_data["options"]), 1)
        option_data = select_data["options"][0]
        self.assertEqual(option_data["value"], "us")
        self.assertEqual(option_data["text"], "United States")
        self.assertTrue(option_data["selected"])
        
        # 驗證文本區域
        self.assertEqual(len(form_data["textareas"]), 1)
        textarea_data = form_data["textareas"][0]
        self.assertEqual(textarea_data["name"], "comment")
        self.assertEqual(textarea_data["id"], "comment1")
        self.assertEqual(textarea_data["value"], "Hello World")
        
        # 驗證按鈕
        self.assertEqual(len(form_data["buttons"]), 1)
        button_data = form_data["buttons"][0]
        self.assertEqual(button_data["type"], "submit")
        self.assertEqual(button_data["name"], "submit-btn")
        self.assertEqual(button_data["id"], "btn1")
        self.assertEqual(button_data["value"], "Submit")
        
        # 驗證標籤
        self.assertEqual(len(form_data["labels"]), 1)
        label_data = form_data["labels"][0]
        self.assertEqual(label_data["for"], "username")
        self.assertEqual(label_data["id"], "label1")
        self.assertEqual(label_data["text"], "Username:")
        
        # 測試提取失敗
        WebDriverWait.until.side_effect = TimeoutException()
        result = self.extractor.extract(self.driver)
        self.assertFalse(result.success)
        self.assertIsNone(result.data)
        self.assertIsNotNone(result.error)
        
if __name__ == "__main__":
    unittest.main() 
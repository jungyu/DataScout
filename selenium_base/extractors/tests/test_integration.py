#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提取器集成測試模組

提供提取器的集成測試，包括：
1. 多提取器協同工作
2. 實際網頁環境測試
3. 錯誤處理和恢復
4. 性能測試
"""

import unittest
import os
import time
from unittest.mock import Mock, patch, MagicMock
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..handlers.table import TableExtractor, TableExtractorConfig
from ..handlers.text import TextExtractor, TextExtractorConfig
from ..handlers.image import ImageExtractor, ImageExtractorConfig
from ..handlers.link import LinkExtractor, LinkExtractorConfig
from ..handlers.form import FormExtractor, FormExtractorConfig
from ..core.error import ExtractorError

class TestExtractorIntegration(unittest.TestCase):
    """提取器集成測試類別"""
    
    @classmethod
    def setUpClass(cls):
        """設置測試環境"""
        # 設置 Chrome 選項
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # 初始化 WebDriver
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)
        
        # 創建測試目錄
        cls.test_dir = os.path.join(os.path.dirname(__file__), "test_data")
        os.makedirs(cls.test_dir, exist_ok=True)
        
        # 創建測試 HTML 文件
        cls.test_html = os.path.join(cls.test_dir, "test.html")
        with open(cls.test_html, "w", encoding="utf-8") as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>測試頁面</title>
                <style>
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid black; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    img { max-width: 200px; }
                    form { margin: 20px 0; }
                    input, select, textarea, button { margin: 5px 0; }
                </style>
            </head>
            <body>
                <h1>測試頁面</h1>
                
                <h2>表格測試</h2>
                <table id="test-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>名稱</th>
                            <th>描述</th>
                            <th>價格</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>1</td>
                            <td>產品 A</td>
                            <td>這是產品 A 的描述</td>
                            <td>100</td>
                        </tr>
                        <tr>
                            <td>2</td>
                            <td>產品 B</td>
                            <td>這是產品 B 的描述</td>
                            <td>200</td>
                        </tr>
                        <tr>
                            <td>3</td>
                            <td>產品 C</td>
                            <td>這是產品 C 的描述</td>
                            <td>300</td>
                        </tr>
                    </tbody>
                </table>
                
                <h2>文本測試</h2>
                <div id="text-content">
                    <p>這是一段普通文本。</p>
                    <p>這是一個<a href="https://example.com">鏈接</a>。</p>
                    <p>這是一個<a href="mailto:test@example.com">郵箱</a>。</p>
                    <p>這是一個電話號碼：<a href="tel:+86123456789">+86 123 4567 89</a>。</p>
                    <p>這是一個日期：2023-01-01。</p>
                    <p>這是一個數字：123.45。</p>
                </div>
                
                <h2>圖像測試</h2>
                <div id="image-content">
                    <img src="https://via.placeholder.com/150" alt="測試圖像 1" title="圖像標題 1" id="img1" class="test-img">
                    <img src="https://via.placeholder.com/200" alt="測試圖像 2" title="圖像標題 2" id="img2" class="test-img">
                    <img src="https://via.placeholder.com/250" alt="測試圖像 3" title="圖像標題 3" id="img3" class="test-img">
                </div>
                
                <h2>鏈接測試</h2>
                <div id="link-content">
                    <a href="https://example.com" id="link1" class="test-link">示例網站</a>
                    <a href="https://example.org" id="link2" class="test-link">另一個示例網站</a>
                    <a href="https://example.net" id="link3" class="test-link">第三個示例網站</a>
                    <a href="https://example.com/page1" id="link4" class="test-link">頁面 1</a>
                    <a href="https://example.com/page2" id="link5" class="test-link">頁面 2</a>
                </div>
                
                <h2>表單測試</h2>
                <form id="test-form" action="/submit" method="post" enctype="multipart/form-data">
                    <div>
                        <label for="username">用戶名：</label>
                        <input type="text" id="username" name="username" value="testuser" placeholder="請輸入用戶名" required>
                    </div>
                    <div>
                        <label for="email">郵箱：</label>
                        <input type="email" id="email" name="email" value="test@example.com" placeholder="請輸入郵箱" required>
                    </div>
                    <div>
                        <label for="country">國家：</label>
                        <select id="country" name="country" required>
                            <option value="cn" selected>中國</option>
                            <option value="us">美國</option>
                            <option value="uk">英國</option>
                        </select>
                    </div>
                    <div>
                        <label for="comment">評論：</label>
                        <textarea id="comment" name="comment" rows="5" cols="50" placeholder="請輸入評論">這是一個測試評論。</textarea>
                    </div>
                    <div>
                        <button type="submit" id="submit-btn" name="submit-btn" value="提交">提交</button>
                        <button type="reset" id="reset-btn" name="reset-btn" value="重置">重置</button>
                    </div>
                </form>
            </body>
            </html>
            """)
        
        # 加載測試頁面
        cls.driver.get(f"file://{cls.test_html}")
        
    @classmethod
    def tearDownClass(cls):
        """清理測試環境"""
        # 關閉 WebDriver
        cls.driver.quit()
        
        # 刪除測試文件
        if os.path.exists(cls.test_html):
            os.remove(cls.test_html)
        
        # 刪除測試目錄
        if os.path.exists(cls.test_dir):
            os.rmdir(cls.test_dir)
    
    def test_table_extraction(self):
        """測試表格提取"""
        # 配置表格提取器
        config = TableExtractorConfig(
            table_selector="#test-table",
            header_selector="thead tr th",
            row_selector="tbody tr",
            cell_selector="td",
            normalize_headers=True,
            remove_empty_rows=True,
            validate_structure=True,
            validate_data=True,
            error_on_empty=True,
            error_on_invalid=True,
            error_on_timeout=True,
            retry_on_error=True,
            retry_count=3,
            retry_delay=0.1
        )
        extractor = TableExtractor(config=config)
        
        # 執行提取
        result = extractor.extract(self.driver)
        
        # 驗證結果
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data), 1)
        table_data = result.data[0]
        
        # 驗證表頭
        self.assertEqual(len(table_data["headers"]), 4)
        self.assertEqual(table_data["headers"][0], "id")
        self.assertEqual(table_data["headers"][1], "名稱")
        self.assertEqual(table_data["headers"][2], "描述")
        self.assertEqual(table_data["headers"][3], "價格")
        
        # 驗證行數據
        self.assertEqual(len(table_data["rows"]), 3)
        self.assertEqual(table_data["rows"][0][0], "1")
        self.assertEqual(table_data["rows"][0][1], "產品 A")
        self.assertEqual(table_data["rows"][0][2], "這是產品 A 的描述")
        self.assertEqual(table_data["rows"][0][3], "100")
        
        self.assertEqual(table_data["rows"][1][0], "2")
        self.assertEqual(table_data["rows"][1][1], "產品 B")
        self.assertEqual(table_data["rows"][1][2], "這是產品 B 的描述")
        self.assertEqual(table_data["rows"][1][3], "200")
        
        self.assertEqual(table_data["rows"][2][0], "3")
        self.assertEqual(table_data["rows"][2][1], "產品 C")
        self.assertEqual(table_data["rows"][2][2], "這是產品 C 的描述")
        self.assertEqual(table_data["rows"][2][3], "300")
    
    def test_text_extraction(self):
        """測試文本提取"""
        # 配置文本提取器
        config = TextExtractorConfig(
            text_selector="#text-content",
            wait_timeout=1.0,
            strip_whitespace=True,
            remove_special_chars=False,
            remove_html_tags=True,
            extract_links=True,
            extract_emails=True,
            extract_phones=True,
            extract_dates=True,
            extract_numbers=True,
            validate_text=True,
            min_length=1,
            max_length=1000,
            error_on_empty=True,
            error_on_invalid=True,
            error_on_timeout=True,
            retry_on_error=True,
            retry_count=3,
            retry_delay=0.1
        )
        extractor = TextExtractor(config=config)
        
        # 執行提取
        result = extractor.extract(self.driver)
        
        # 驗證結果
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data), 1)
        text_data = result.data[0]
        
        # 驗證文本內容
        self.assertIn("這是一段普通文本", text_data["text"])
        self.assertIn("這是一個鏈接", text_data["text"])
        self.assertIn("這是一個郵箱", text_data["text"])
        self.assertIn("這是一個電話號碼", text_data["text"])
        self.assertIn("這是一個日期", text_data["text"])
        self.assertIn("這是一個數字", text_data["text"])
        
        # 驗證提取的鏈接
        self.assertEqual(len(text_data["links"]), 1)
        self.assertEqual(text_data["links"][0]["text"], "鏈接")
        self.assertEqual(text_data["links"][0]["url"], "https://example.com")
        
        # 驗證提取的郵箱
        self.assertEqual(len(text_data["emails"]), 1)
        self.assertEqual(text_data["emails"][0]["text"], "test@example.com")
        self.assertEqual(text_data["emails"][0]["email"], "test@example.com")
        
        # 驗證提取的電話
        self.assertEqual(len(text_data["phones"]), 1)
        self.assertEqual(text_data["phones"][0]["text"], "+86 123 4567 89")
        self.assertEqual(text_data["phones"][0]["phone"], "+86123456789")
        
        # 驗證提取的日期
        self.assertEqual(len(text_data["dates"]), 1)
        self.assertEqual(text_data["dates"][0]["text"], "2023-01-01")
        self.assertEqual(text_data["dates"][0]["date"], "2023-01-01")
        
        # 驗證提取的數字
        self.assertEqual(len(text_data["numbers"]), 1)
        self.assertEqual(text_data["numbers"][0]["text"], "123.45")
        self.assertEqual(text_data["numbers"][0]["number"], 123.45)
    
    def test_image_extraction(self):
        """測試圖像提取"""
        # 配置圖像提取器
        config = ImageExtractorConfig(
            image_selector="#image-content img",
            wait_timeout=1.0,
            download_dir=os.path.join(self.test_dir, "images"),
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
        extractor = ImageExtractor(config=config)
        
        # 執行提取
        result = extractor.extract(self.driver)
        
        # 驗證結果
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data), 3)
        
        # 驗證第一張圖像
        image1 = result.data[0]
        self.assertEqual(image1["alt"], "測試圖像 1")
        self.assertEqual(image1["title"], "圖像標題 1")
        self.assertEqual(image1["id"], "img1")
        self.assertEqual(image1["class"], "test-img")
        self.assertTrue(os.path.exists(image1["file_path"]))
        
        # 驗證第二張圖像
        image2 = result.data[1]
        self.assertEqual(image2["alt"], "測試圖像 2")
        self.assertEqual(image2["title"], "圖像標題 2")
        self.assertEqual(image2["id"], "img2")
        self.assertEqual(image2["class"], "test-img")
        self.assertTrue(os.path.exists(image2["file_path"]))
        
        # 驗證第三張圖像
        image3 = result.data[2]
        self.assertEqual(image3["alt"], "測試圖像 3")
        self.assertEqual(image3["title"], "圖像標題 3")
        self.assertEqual(image3["id"], "img3")
        self.assertEqual(image3["class"], "test-img")
        self.assertTrue(os.path.exists(image3["file_path"]))
    
    def test_link_extraction(self):
        """測試鏈接提取"""
        # 配置鏈接提取器
        config = LinkExtractorConfig(
            link_selector="#link-content a",
            wait_timeout=1.0,
            base_url="https://example.com",
            validate_url=True,
            check_status=True,
            extract_text=True,
            extract_href=True,
            extract_title=True,
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
        extractor = LinkExtractor(config=config)
        
        # 執行提取
        result = extractor.extract(self.driver)
        
        # 驗證結果
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data), 5)
        
        # 驗證第一個鏈接
        link1 = result.data[0]
        self.assertEqual(link1["text"], "示例網站")
        self.assertEqual(link1["href"], "https://example.com")
        self.assertEqual(link1["id"], "link1")
        self.assertEqual(link1["class"], "test-link")
        
        # 驗證第二個鏈接
        link2 = result.data[1]
        self.assertEqual(link2["text"], "另一個示例網站")
        self.assertEqual(link2["href"], "https://example.org")
        self.assertEqual(link2["id"], "link2")
        self.assertEqual(link2["class"], "test-link")
        
        # 驗證第三個鏈接
        link3 = result.data[2]
        self.assertEqual(link3["text"], "第三個示例網站")
        self.assertEqual(link3["href"], "https://example.net")
        self.assertEqual(link3["id"], "link3")
        self.assertEqual(link3["class"], "test-link")
        
        # 驗證第四個鏈接
        link4 = result.data[3]
        self.assertEqual(link4["text"], "頁面 1")
        self.assertEqual(link4["href"], "https://example.com/page1")
        self.assertEqual(link4["id"], "link4")
        self.assertEqual(link4["class"], "test-link")
        
        # 驗證第五個鏈接
        link5 = result.data[4]
        self.assertEqual(link5["text"], "頁面 2")
        self.assertEqual(link5["href"], "https://example.com/page2")
        self.assertEqual(link5["id"], "link5")
        self.assertEqual(link5["class"], "test-link")
    
    def test_form_extraction(self):
        """測試表單提取"""
        # 配置表單提取器
        config = FormExtractorConfig(
            form_selector="#test-form",
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
        extractor = FormExtractor(config=config)
        
        # 執行提取
        result = extractor.extract(self.driver)
        
        # 驗證結果
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data), 1)
        form_data = result.data[0]
        
        # 驗證表單基本信息
        self.assertEqual(form_data["action"], "/submit")
        self.assertEqual(form_data["method"], "post")
        self.assertEqual(form_data["enctype"], "multipart/form-data")
        self.assertEqual(form_data["id"], "test-form")
        
        # 驗證輸入框
        self.assertEqual(len(form_data["inputs"]), 2)
        
        # 驗證用戶名輸入框
        username_input = next((input for input in form_data["inputs"] if input["name"] == "username"), None)
        self.assertIsNotNone(username_input)
        self.assertEqual(username_input["type"], "text")
        self.assertEqual(username_input["id"], "username")
        self.assertEqual(username_input["value"], "testuser")
        self.assertEqual(username_input["placeholder"], "請輸入用戶名")
        self.assertTrue(username_input["required"])
        
        # 驗證郵箱輸入框
        email_input = next((input for input in form_data["inputs"] if input["name"] == "email"), None)
        self.assertIsNotNone(email_input)
        self.assertEqual(email_input["type"], "email")
        self.assertEqual(email_input["id"], "email")
        self.assertEqual(email_input["value"], "test@example.com")
        self.assertEqual(email_input["placeholder"], "請輸入郵箱")
        self.assertTrue(email_input["required"])
        
        # 驗證選擇框
        self.assertEqual(len(form_data["selects"]), 1)
        country_select = form_data["selects"][0]
        self.assertEqual(country_select["name"], "country")
        self.assertEqual(country_select["id"], "country")
        self.assertTrue(country_select["required"])
        self.assertEqual(len(country_select["options"]), 3)
        
        # 驗證選項
        cn_option = next((option for option in country_select["options"] if option["value"] == "cn"), None)
        self.assertIsNotNone(cn_option)
        self.assertEqual(cn_option["text"], "中國")
        self.assertTrue(cn_option["selected"])
        
        us_option = next((option for option in country_select["options"] if option["value"] == "us"), None)
        self.assertIsNotNone(us_option)
        self.assertEqual(us_option["text"], "美國")
        self.assertFalse(us_option["selected"])
        
        uk_option = next((option for option in country_select["options"] if option["value"] == "uk"), None)
        self.assertIsNotNone(uk_option)
        self.assertEqual(uk_option["text"], "英國")
        self.assertFalse(uk_option["selected"])
        
        # 驗證文本區域
        self.assertEqual(len(form_data["textareas"]), 1)
        comment_textarea = form_data["textareas"][0]
        self.assertEqual(comment_textarea["name"], "comment")
        self.assertEqual(comment_textarea["id"], "comment")
        self.assertEqual(comment_textarea["value"], "這是一個測試評論。")
        self.assertEqual(comment_textarea["placeholder"], "請輸入評論")
        self.assertEqual(comment_textarea["rows"], "5")
        self.assertEqual(comment_textarea["cols"], "50")
        
        # 驗證按鈕
        self.assertEqual(len(form_data["buttons"]), 2)
        
        # 驗證提交按鈕
        submit_button = next((button for button in form_data["buttons"] if button["type"] == "submit"), None)
        self.assertIsNotNone(submit_button)
        self.assertEqual(submit_button["name"], "submit-btn")
        self.assertEqual(submit_button["id"], "submit-btn")
        self.assertEqual(submit_button["value"], "提交")
        
        # 驗證重置按鈕
        reset_button = next((button for button in form_data["buttons"] if button["type"] == "reset"), None)
        self.assertIsNotNone(reset_button)
        self.assertEqual(reset_button["name"], "reset-btn")
        self.assertEqual(reset_button["id"], "reset-btn")
        self.assertEqual(reset_button["value"], "重置")
        
        # 驗證標籤
        self.assertEqual(len(form_data["labels"]), 4)
        
        # 驗證用戶名標籤
        username_label = next((label for label in form_data["labels"] if label["for"] == "username"), None)
        self.assertIsNotNone(username_label)
        self.assertEqual(username_label["text"], "用戶名：")
        
        # 驗證郵箱標籤
        email_label = next((label for label in form_data["labels"] if label["for"] == "email"), None)
        self.assertIsNotNone(email_label)
        self.assertEqual(email_label["text"], "郵箱：")
        
        # 驗證國家標籤
        country_label = next((label for label in form_data["labels"] if label["for"] == "country"), None)
        self.assertIsNotNone(country_label)
        self.assertEqual(country_label["text"], "國家：")
        
        # 驗證評論標籤
        comment_label = next((label for label in form_data["labels"] if label["for"] == "comment"), None)
        self.assertIsNotNone(comment_label)
        self.assertEqual(comment_label["text"], "評論：")
    
    def test_multiple_extractors(self):
        """測試多個提取器協同工作"""
        # 配置表格提取器
        table_config = TableExtractorConfig(
            table_selector="#test-table",
            header_selector="thead tr th",
            row_selector="tbody tr",
            cell_selector="td",
            normalize_headers=True,
            remove_empty_rows=True,
            validate_structure=True,
            validate_data=True,
            error_on_empty=True,
            error_on_invalid=True,
            error_on_timeout=True,
            retry_on_error=True,
            retry_count=3,
            retry_delay=0.1
        )
        table_extractor = TableExtractor(config=table_config)
        
        # 配置文本提取器
        text_config = TextExtractorConfig(
            text_selector="#text-content",
            wait_timeout=1.0,
            strip_whitespace=True,
            remove_special_chars=False,
            remove_html_tags=True,
            extract_links=True,
            extract_emails=True,
            extract_phones=True,
            extract_dates=True,
            extract_numbers=True,
            validate_text=True,
            min_length=1,
            max_length=1000,
            error_on_empty=True,
            error_on_invalid=True,
            error_on_timeout=True,
            retry_on_error=True,
            retry_count=3,
            retry_delay=0.1
        )
        text_extractor = TextExtractor(config=text_config)
        
        # 配置圖像提取器
        image_config = ImageExtractorConfig(
            image_selector="#image-content img",
            wait_timeout=1.0,
            download_dir=os.path.join(self.test_dir, "images"),
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
        image_extractor = ImageExtractor(config=image_config)
        
        # 配置鏈接提取器
        link_config = LinkExtractorConfig(
            link_selector="#link-content a",
            wait_timeout=1.0,
            base_url="https://example.com",
            validate_url=True,
            check_status=True,
            extract_text=True,
            extract_href=True,
            extract_title=True,
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
        link_extractor = LinkExtractor(config=link_config)
        
        # 配置表單提取器
        form_config = FormExtractorConfig(
            form_selector="#test-form",
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
        form_extractor = FormExtractor(config=form_config)
        
        # 執行提取
        table_result = table_extractor.extract(self.driver)
        text_result = text_extractor.extract(self.driver)
        image_result = image_extractor.extract(self.driver)
        link_result = link_extractor.extract(self.driver)
        form_result = form_extractor.extract(self.driver)
        
        # 驗證結果
        self.assertTrue(table_result.success)
        self.assertTrue(text_result.success)
        self.assertTrue(image_result.success)
        self.assertTrue(link_result.success)
        self.assertTrue(form_result.success)
        
        # 驗證表格數據
        self.assertIsNotNone(table_result.data)
        self.assertEqual(len(table_result.data), 1)
        table_data = table_result.data[0]
        self.assertEqual(len(table_data["headers"]), 4)
        self.assertEqual(len(table_data["rows"]), 3)
        
        # 驗證文本數據
        self.assertIsNotNone(text_result.data)
        self.assertEqual(len(text_result.data), 1)
        text_data = text_result.data[0]
        self.assertIn("這是一段普通文本", text_data["text"])
        self.assertEqual(len(text_data["links"]), 1)
        self.assertEqual(len(text_data["emails"]), 1)
        self.assertEqual(len(text_data["phones"]), 1)
        self.assertEqual(len(text_data["dates"]), 1)
        self.assertEqual(len(text_data["numbers"]), 1)
        
        # 驗證圖像數據
        self.assertIsNotNone(image_result.data)
        self.assertEqual(len(image_result.data), 3)
        
        # 驗證鏈接數據
        self.assertIsNotNone(link_result.data)
        self.assertEqual(len(link_result.data), 5)
        
        # 驗證表單數據
        self.assertIsNotNone(form_result.data)
        self.assertEqual(len(form_result.data), 1)
        form_data = form_result.data[0]
        self.assertEqual(form_data["action"], "/submit")
        self.assertEqual(form_data["method"], "post")
        self.assertEqual(len(form_data["inputs"]), 2)
        self.assertEqual(len(form_data["selects"]), 1)
        self.assertEqual(len(form_data["textareas"]), 1)
        self.assertEqual(len(form_data["buttons"]), 2)
        self.assertEqual(len(form_data["labels"]), 4)
    
    def test_error_handling(self):
        """測試錯誤處理"""
        # 配置表格提取器（使用無效選擇器）
        table_config = TableExtractorConfig(
            table_selector="#non-existent-table",
            header_selector="thead tr th",
            row_selector="tbody tr",
            cell_selector="td",
            normalize_headers=True,
            remove_empty_rows=True,
            validate_structure=True,
            validate_data=True,
            error_on_empty=True,
            error_on_invalid=True,
            error_on_timeout=True,
            retry_on_error=True,
            retry_count=3,
            retry_delay=0.1
        )
        table_extractor = TableExtractor(config=table_config)
        
        # 執行提取
        result = table_extractor.extract(self.driver)
        
        # 驗證結果
        self.assertFalse(result.success)
        self.assertIsNone(result.data)
        self.assertIsNotNone(result.error)
        
        # 配置表格提取器（不拋出錯誤）
        table_config = TableExtractorConfig(
            table_selector="#non-existent-table",
            header_selector="thead tr th",
            row_selector="tbody tr",
            cell_selector="td",
            normalize_headers=True,
            remove_empty_rows=True,
            validate_structure=True,
            validate_data=True,
            error_on_empty=False,
            error_on_invalid=True,
            error_on_timeout=True,
            retry_on_error=True,
            retry_count=3,
            retry_delay=0.1
        )
        table_extractor = TableExtractor(config=table_config)
        
        # 執行提取
        result = table_extractor.extract(self.driver)
        
        # 驗證結果
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data), 0)
    
    def test_performance(self):
        """測試性能"""
        # 配置表格提取器
        table_config = TableExtractorConfig(
            table_selector="#test-table",
            header_selector="thead tr th",
            row_selector="tbody tr",
            cell_selector="td",
            normalize_headers=True,
            remove_empty_rows=True,
            validate_structure=True,
            validate_data=True,
            error_on_empty=True,
            error_on_invalid=True,
            error_on_timeout=True,
            retry_on_error=True,
            retry_count=3,
            retry_delay=0.1
        )
        table_extractor = TableExtractor(config=table_config)
        
        # 測量提取時間
        start_time = time.time()
        result = table_extractor.extract(self.driver)
        end_time = time.time()
        
        # 驗證結果
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data), 1)
        
        # 驗證性能
        extraction_time = end_time - start_time
        self.assertLess(extraction_time, 1.0)  # 提取時間應小於 1 秒
        
        # 配置文本提取器
        text_config = TextExtractorConfig(
            text_selector="#text-content",
            wait_timeout=1.0,
            strip_whitespace=True,
            remove_special_chars=False,
            remove_html_tags=True,
            extract_links=True,
            extract_emails=True,
            extract_phones=True,
            extract_dates=True,
            extract_numbers=True,
            validate_text=True,
            min_length=1,
            max_length=1000,
            error_on_empty=True,
            error_on_invalid=True,
            error_on_timeout=True,
            retry_on_error=True,
            retry_count=3,
            retry_delay=0.1
        )
        text_extractor = TextExtractor(config=text_config)
        
        # 測量提取時間
        start_time = time.time()
        result = text_extractor.extract(self.driver)
        end_time = time.time()
        
        # 驗證結果
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data), 1)
        
        # 驗證性能
        extraction_time = end_time - start_time
        self.assertLess(extraction_time, 1.0)  # 提取時間應小於 1 秒
        
        # 配置圖像提取器
        image_config = ImageExtractorConfig(
            image_selector="#image-content img",
            wait_timeout=1.0,
            download_dir=os.path.join(self.test_dir, "images"),
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
        image_extractor = ImageExtractor(config=image_config)
        
        # 測量提取時間
        start_time = time.time()
        result = image_extractor.extract(self.driver)
        end_time = time.time()
        
        # 驗證結果
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data), 3)
        
        # 驗證性能
        extraction_time = end_time - start_time
        self.assertLess(extraction_time, 5.0)  # 圖像提取時間應小於 5 秒（包括下載）
        
        # 配置鏈接提取器
        link_config = LinkExtractorConfig(
            link_selector="#link-content a",
            wait_timeout=1.0,
            base_url="https://example.com",
            validate_url=True,
            check_status=True,
            extract_text=True,
            extract_href=True,
            extract_title=True,
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
        link_extractor = LinkExtractor(config=link_config)
        
        # 測量提取時間
        start_time = time.time()
        result = link_extractor.extract(self.driver)
        end_time = time.time()
        
        # 驗證結果
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data), 5)
        
        # 驗證性能
        extraction_time = end_time - start_time
        self.assertLess(extraction_time, 5.0)  # 鏈接提取時間應小於 5 秒（包括檢查狀態）
        
        # 配置表單提取器
        form_config = FormExtractorConfig(
            form_selector="#test-form",
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
        form_extractor = FormExtractor(config=form_config)
        
        # 測量提取時間
        start_time = time.time()
        result = form_extractor.extract(self.driver)
        end_time = time.time()
        
        # 驗證結果
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data), 1)
        
        # 驗證性能
        extraction_time = end_time - start_time
        self.assertLess(extraction_time, 1.0)  # 提取時間應小於 1 秒

if __name__ == "__main__":
    unittest.main() 
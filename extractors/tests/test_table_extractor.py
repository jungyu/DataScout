#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
表格提取器測試模組

提供表格提取器的單元測試，包括：
1. 配置驗證
2. 表格定位
3. 表頭提取
4. 數據提取
5. 數據驗證
"""

import unittest
from unittest.mock import Mock, patch
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..handlers.table import TableExtractor, TableExtractorConfig
from ..core.error import ExtractorError

class TestTableExtractor(unittest.TestCase):
    """表格提取器測試類別"""
    
    def setUp(self):
        """設置測試環境"""
        self.config = TableExtractorConfig(
            table_selector="table",
            header_selector="th",
            row_selector="tr",
            cell_selector="td",
            wait_timeout=1.0,
            validate_structure=True,
            validate_data=True,
            normalize_headers=True,
            remove_empty_rows=True,
            remove_duplicate_rows=True,
            trim_cell_values=True,
            convert_numbers=True,
            convert_dates=True,
            error_on_empty=True,
            error_on_invalid=True,
            error_on_timeout=True,
            retry_on_error=True,
            retry_count=3,
            retry_delay=0.1
        )
        self.extractor = TableExtractor(config=self.config)
        self.driver = Mock()
        
    def test_validate_config(self):
        """測試配置驗證"""
        # 測試有效配置
        self.assertTrue(self.extractor._validate_config())
        
        # 測試無效選擇器
        self.config.table_selector = ""
        self.assertFalse(self.extractor._validate_config())
        self.config.table_selector = "table"
        
        # 測試無效超時時間
        self.config.wait_timeout = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.wait_timeout = 1.0
        
        # 測試無效重試次數
        self.config.retry_count = -1
        self.assertFalse(self.extractor._validate_config())
        self.config.retry_count = 3
        
    def test_find_table_elements(self):
        """測試查找表格元素"""
        # 模擬成功查找
        mock_elements = [Mock(), Mock()]
        self.driver.find_elements.return_value = mock_elements
        WebDriverWait.until.return_value = mock_elements
        
        elements = self.extractor.find_table_elements(self.driver)
        self.assertEqual(elements, mock_elements)
        
        # 模擬超時
        WebDriverWait.until.side_effect = TimeoutException()
        elements = self.extractor.find_table_elements(self.driver)
        self.assertEqual(elements, [])
        
        # 模擬錯誤
        self.config.error_on_timeout = True
        with self.assertRaises(ExtractorError):
            self.extractor.find_table_elements(self.driver)
            
    def test_extract_headers(self):
        """測試提取表頭"""
        # 創建模擬表頭元素
        header_elements = [Mock(), Mock()]
        for i, element in enumerate(header_elements):
            element.text = f"Header {i}"
            
        headers = self.extractor.extract_headers(header_elements)
        self.assertEqual(headers, ["Header 0", "Header 1"])
        
        # 測試空表頭
        headers = self.extractor.extract_headers([])
        self.assertEqual(headers, [])
        
        # 測試標準化表頭
        header_elements = [Mock(), Mock()]
        header_elements[0].text = "  Header 0  "
        header_elements[1].text = "header 1"
        headers = self.extractor.extract_headers(header_elements)
        self.assertEqual(headers, ["Header 0", "Header 1"])
        
    def test_extract_rows(self):
        """測試提取行數據"""
        # 創建模擬行元素
        row_elements = [Mock(), Mock()]
        for i, row in enumerate(row_elements):
            cell_elements = [Mock(), Mock()]
            for j, cell in enumerate(cell_elements):
                cell.text = f"Cell {i}-{j}"
            row.find_elements.return_value = cell_elements
            
        rows = self.extractor.extract_rows(row_elements)
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(rows[0]), 2)
        self.assertEqual(rows[0][0], "Cell 0-0")
        self.assertEqual(rows[0][1], "Cell 0-1")
        self.assertEqual(rows[1][0], "Cell 1-0")
        self.assertEqual(rows[1][1], "Cell 1-1")
        
        # 測試空行
        rows = self.extractor.extract_rows([])
        self.assertEqual(rows, [])
        
        # 測試移除空行
        row_elements = [Mock(), Mock(), Mock()]
        row_elements[0].find_elements.return_value = [Mock()]
        row_elements[0].find_elements.return_value[0].text = "Cell 0-0"
        row_elements[1].find_elements.return_value = []
        row_elements[2].find_elements.return_value = [Mock()]
        row_elements[2].find_elements.return_value[0].text = "Cell 2-0"
        
        rows = self.extractor.extract_rows(row_elements)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0], "Cell 0-0")
        self.assertEqual(rows[1][0], "Cell 2-0")
        
    def test_validate_structure(self):
        """測試結構驗證"""
        # 測試有效結構
        headers = ["Header 1", "Header 2"]
        rows = [
            ["Cell 1-1", "Cell 1-2"],
            ["Cell 2-1", "Cell 2-2"]
        ]
        self.assertTrue(self.extractor.validate_structure(headers, rows))
        
        # 測試無效結構（空表頭）
        headers = []
        rows = [["Cell 1-1", "Cell 1-2"]]
        self.assertFalse(self.extractor.validate_structure(headers, rows))
        
        # 測試無效結構（空行）
        headers = ["Header 1", "Header 2"]
        rows = []
        self.assertFalse(self.extractor.validate_structure(headers, rows))
        
        # 測試無效結構（列數不一致）
        headers = ["Header 1", "Header 2"]
        rows = [
            ["Cell 1-1", "Cell 1-2"],
            ["Cell 2-1"]
        ]
        self.assertFalse(self.extractor.validate_structure(headers, rows))
        
    def test_validate_data(self):
        """測試數據驗證"""
        # 測試有效數據
        headers = ["Name", "Age", "Date"]
        rows = [
            ["John", "25", "2023-01-01"],
            ["Jane", "30", "2023-02-01"]
        ]
        self.assertTrue(self.extractor.validate_data(headers, rows))
        
        # 測試無效數據（空值）
        headers = ["Name", "Age"]
        rows = [
            ["John", "25"],
            ["", "30"]
        ]
        self.assertFalse(self.extractor.validate_data(headers, rows))
        
        # 測試無效數據（格式錯誤）
        headers = ["Name", "Age"]
        rows = [
            ["John", "25"],
            ["Jane", "invalid"]
        ]
        self.assertFalse(self.extractor.validate_data(headers, rows))
        
    def test_extract(self):
        """測試表格提取"""
        # 模擬成功提取
        mock_table = Mock()
        mock_headers = [Mock(), Mock()]
        mock_rows = [Mock(), Mock()]
        
        for i, header in enumerate(mock_headers):
            header.text = f"Header {i}"
            
        for i, row in enumerate(mock_rows):
            mock_cells = [Mock(), Mock()]
            for j, cell in enumerate(mock_cells):
                cell.text = f"Cell {i}-{j}"
            row.find_elements.return_value = mock_cells
            
        mock_table.find_elements.side_effect = [mock_headers, mock_rows]
        
        self.driver.find_elements.return_value = [mock_table]
        WebDriverWait.until.return_value = [mock_table]
        
        result = self.extractor.extract(self.driver)
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 1)
        table_data = result.data[0]
        self.assertEqual(table_data["headers"], ["Header 0", "Header 1"])
        self.assertEqual(len(table_data["rows"]), 2)
        self.assertEqual(table_data["rows"][0], ["Cell 0-0", "Cell 0-1"])
        self.assertEqual(table_data["rows"][1], ["Cell 1-0", "Cell 1-1"])
        
        # 模擬提取失敗
        WebDriverWait.until.side_effect = TimeoutException()
        result = self.extractor.extract(self.driver)
        self.assertFalse(result.success)
        self.assertIsNone(result.data)
        self.assertIsNotNone(result.error)
        
if __name__ == "__main__":
    unittest.main() 
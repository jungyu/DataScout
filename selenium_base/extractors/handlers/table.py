#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
表格提取器模組

提供表格數據提取功能，包括：
1. 表格定位
2. 表頭提取
3. 數據提取
4. 數據格式化
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..core.base import BaseExtractor
from ..core.types import ExtractorConfig, ExtractorResult
from ..core.error import ExtractorError, handle_extractor_error

@dataclass
class TableExtractorConfig(ExtractorConfig):
    """表格提取器配置"""
    table_selector: str = "table"
    header_selector: str = "thead tr th"
    row_selector: str = "tbody tr"
    cell_selector: str = "td"
    wait_timeout: float = 10.0
    include_header: bool = True
    strip_whitespace: bool = True
    remove_empty_rows: bool = True
    remove_empty_cells: bool = True
    normalize_headers: bool = True
    header_case: str = "lower"  # lower, upper, title, none
    header_separator: str = "_"
    header_prefix: str = ""
    header_suffix: str = ""
    max_rows: Optional[int] = None
    max_columns: Optional[int] = None
    min_rows: Optional[int] = None
    min_columns: Optional[int] = None
    validate_structure: bool = True
    validate_data: bool = True
    error_on_empty: bool = True
    error_on_invalid: bool = True
    error_on_timeout: bool = True
    retry_on_error: bool = True
    retry_count: int = 3
    retry_delay: float = 1.0

class TableExtractor(BaseExtractor):
    """表格提取器類別"""
    
    def __init__(
        self,
        config: Optional[Union[Dict[str, Any], TableExtractorConfig]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化表格提取器
        
        Args:
            config: 配置字典或配置對象
            logger: 日誌記錄器
        """
        super().__init__(config, logger)
        self.config = config if isinstance(config, TableExtractorConfig) else TableExtractorConfig(**(config or {}))
        
    def _validate_config(self) -> bool:
        """
        驗證配置
        
        Returns:
            bool: 是否有效
        """
        try:
            if not self.config.table_selector:
                raise ExtractorError("表格選擇器不能為空")
                
            if self.config.max_rows is not None and self.config.max_rows < 0:
                raise ExtractorError("最大行數不能為負數")
                
            if self.config.max_columns is not None and self.config.max_columns < 0:
                raise ExtractorError("最大列數不能為負數")
                
            if self.config.min_rows is not None and self.config.min_rows < 0:
                raise ExtractorError("最小行數不能為負數")
                
            if self.config.min_columns is not None and self.config.min_columns < 0:
                raise ExtractorError("最小列數不能為負數")
                
            if self.config.header_case not in ["lower", "upper", "title", "none"]:
                raise ExtractorError("無效的表頭大小寫設置")
                
            return True
            
        except Exception as e:
            self.logger.error(f"配置驗證失敗: {str(e)}")
            return False
            
    def _setup(self) -> None:
        """設置提取器環境"""
        if not self.validate_config():
            raise ExtractorError("配置驗證失敗")
            
    def _cleanup(self) -> None:
        """清理提取器環境"""
        pass
        
    @handle_extractor_error()
    def find_table(self, driver: Any) -> Any:
        """
        查找表格元素
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            Any: 表格元素
        """
        try:
            table = WebDriverWait(driver, self.config.wait_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.config.table_selector))
            )
            return table
        except TimeoutException:
            if self.config.error_on_timeout:
                raise ExtractorError("等待表格元素超時")
            return None
            
    @handle_extractor_error()
    def extract_headers(self, table: Any) -> List[str]:
        """
        提取表頭
        
        Args:
            table: 表格元素
            
        Returns:
            List[str]: 表頭列表
        """
        if not self.config.include_header:
            return []
            
        try:
            headers = []
            header_elements = table.find_elements(By.CSS_SELECTOR, self.config.header_selector)
            
            for element in header_elements:
                header = element.text.strip()
                if self.config.strip_whitespace:
                    header = header.strip()
                    
                if self.config.normalize_headers:
                    header = self._normalize_header(header)
                    
                headers.append(header)
                
            return headers
            
        except NoSuchElementException:
            if self.config.error_on_invalid:
                raise ExtractorError("無法找到表頭元素")
            return []
            
    def _normalize_header(self, header: str) -> str:
        """
        標準化表頭
        
        Args:
            header: 原始表頭
            
        Returns:
            str: 標準化後的表頭
        """
        if self.config.strip_whitespace:
            header = header.strip()
            
        if self.config.header_case == "lower":
            header = header.lower()
        elif self.config.header_case == "upper":
            header = header.upper()
        elif self.config.header_case == "title":
            header = header.title()
            
        header = self.config.header_prefix + header + self.config.header_suffix
        
        return header.replace(" ", self.config.header_separator)
        
    @handle_extractor_error()
    def extract_rows(self, table: Any) -> List[List[str]]:
        """
        提取表格行
        
        Args:
            table: 表格元素
            
        Returns:
            List[List[str]]: 表格數據
        """
        try:
            rows = []
            row_elements = table.find_elements(By.CSS_SELECTOR, self.config.row_selector)
            
            for row_element in row_elements:
                cells = row_element.find_elements(By.CSS_SELECTOR, self.config.cell_selector)
                row_data = []
                
                for cell in cells:
                    cell_text = cell.text
                    if self.config.strip_whitespace:
                        cell_text = cell_text.strip()
                        
                    if not cell_text and self.config.remove_empty_cells:
                        continue
                        
                    row_data.append(cell_text)
                    
                if row_data or not self.config.remove_empty_rows:
                    rows.append(row_data)
                    
            return rows
            
        except NoSuchElementException:
            if self.config.error_on_invalid:
                raise ExtractorError("無法找到表格行元素")
            return []
            
    def _validate_structure(self, headers: List[str], rows: List[List[str]]) -> bool:
        """
        驗證表格結構
        
        Args:
            headers: 表頭列表
            rows: 表格數據
            
        Returns:
            bool: 是否有效
        """
        if not rows:
            if self.config.error_on_empty:
                raise ExtractorError("表格為空")
            return False
            
        if self.config.min_rows is not None and len(rows) < self.config.min_rows:
            raise ExtractorError(f"行數少於最小值 {self.config.min_rows}")
            
        if self.config.max_rows is not None and len(rows) > self.config.max_rows:
            raise ExtractorError(f"行數超過最大值 {self.config.max_rows}")
            
        if self.config.include_header:
            if self.config.min_columns is not None and len(headers) < self.config.min_columns:
                raise ExtractorError(f"列數少於最小值 {self.config.min_columns}")
                
            if self.config.max_columns is not None and len(headers) > self.config.max_columns:
                raise ExtractorError(f"列數超過最大值 {self.config.max_columns}")
                
            for row in rows:
                if len(row) != len(headers):
                    raise ExtractorError("行數據列數與表頭不匹配")
                    
        return True
        
    def _validate_data(self, data: Dict[str, List[str]]) -> bool:
        """
        驗證表格數據
        
        Args:
            data: 表格數據
            
        Returns:
            bool: 是否有效
        """
        if not data:
            if self.config.error_on_empty:
                raise ExtractorError("表格數據為空")
            return False
            
        return True
        
    @handle_extractor_error()
    def _extract(self, driver: Any) -> Dict[str, List[str]]:
        """
        提取表格數據
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            Dict[str, List[str]]: 表格數據
        """
        table = self.find_table(driver)
        if not table:
            return {}
            
        headers = self.extract_headers(table)
        rows = self.extract_rows(table)
        
        if self.config.validate_structure:
            self._validate_structure(headers, rows)
            
        if not headers:
            # 如果沒有表頭，使用數字索引作為鍵
            data = {str(i): [row[i] for row in rows] for i in range(len(rows[0]))}
        else:
            # 使用表頭作為鍵
            data = {header: [row[i] for row in rows] for i, header in enumerate(headers)}
            
        if self.config.validate_data:
            self._validate_data(data)
            
        return data
        
    def extract(self, driver: Any) -> ExtractorResult:
        """
        提取表格數據
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            ExtractorResult: 提取結果
        """
        try:
            data = self._extract(driver)
            return ExtractorResult(success=True, data=data)
        except Exception as e:
            if self.config.retry_on_error:
                self.logger.warning(f"提取失敗，正在重試: {str(e)}")
                for i in range(self.config.retry_count):
                    try:
                        data = self._extract(driver)
                        return ExtractorResult(success=True, data=data)
                    except Exception as retry_e:
                        self.logger.warning(f"第 {i+1} 次重試失敗: {str(retry_e)}")
                        if i < self.config.retry_count - 1:
                            time.sleep(self.config.retry_delay)
                            
            return ExtractorResult(success=False, data=None, error=str(e)) 
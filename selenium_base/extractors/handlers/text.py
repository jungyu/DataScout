#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文本提取器模組

提供文本數據提取功能，包括：
1. 文本定位
2. 文本提取
3. 文本清理
4. 文本格式化
"""

import logging
import re
from typing import Any, Dict, List, Optional, Union, Pattern
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..core.base import BaseExtractor
from ..core.types import ExtractorConfig, ExtractorResult
from ..core.error import ExtractorError, handle_extractor_error

@dataclass
class TextExtractorConfig(ExtractorConfig):
    """文本提取器配置"""
    text_selector: str = "body"
    wait_timeout: float = 10.0
    strip_whitespace: bool = True
    remove_extra_spaces: bool = True
    remove_special_chars: bool = False
    special_chars_pattern: str = r'[^\w\s\u4e00-\u9fff]'
    normalize_unicode: bool = True
    normalize_case: bool = False
    case_type: str = "lower"  # lower, upper, title, none
    remove_html_tags: bool = True
    decode_html_entities: bool = True
    extract_links: bool = False
    extract_emails: bool = False
    extract_phones: bool = False
    extract_dates: bool = False
    extract_numbers: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    validate_content: bool = True
    error_on_empty: bool = True
    error_on_invalid: bool = True
    error_on_timeout: bool = True
    retry_on_error: bool = True
    retry_count: int = 3
    retry_delay: float = 1.0

class TextExtractor(BaseExtractor):
    """文本提取器類別"""
    
    def __init__(
        self,
        config: Optional[Union[Dict[str, Any], TextExtractorConfig]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化文本提取器
        
        Args:
            config: 配置字典或配置對象
            logger: 日誌記錄器
        """
        super().__init__(config, logger)
        self.config = config if isinstance(config, TextExtractorConfig) else TextExtractorConfig(**(config or {}))
        self._special_chars_pattern: Optional[Pattern] = None
        
    def _validate_config(self) -> bool:
        """
        驗證配置
        
        Returns:
            bool: 是否有效
        """
        try:
            if not self.config.text_selector:
                raise ExtractorError("文本選擇器不能為空")
                
            if self.config.min_length is not None and self.config.min_length < 0:
                raise ExtractorError("最小長度不能為負數")
                
            if self.config.max_length is not None and self.config.max_length < 0:
                raise ExtractorError("最大長度不能為負數")
                
            if self.config.case_type not in ["lower", "upper", "title", "none"]:
                raise ExtractorError("無效的大小寫設置")
                
            if self.config.remove_special_chars:
                try:
                    self._special_chars_pattern = re.compile(self.config.special_chars_pattern)
                except re.error as e:
                    raise ExtractorError(f"無效的特殊字符正則表達式: {str(e)}")
                    
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
        self._special_chars_pattern = None
        
    @handle_extractor_error()
    def find_text_element(self, driver: Any) -> Any:
        """
        查找文本元素
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            Any: 文本元素
        """
        try:
            element = WebDriverWait(driver, self.config.wait_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.config.text_selector))
            )
            return element
        except TimeoutException:
            if self.config.error_on_timeout:
                raise ExtractorError("等待文本元素超時")
            return None
            
    def _clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            str: 清理後的文本
        """
        if self.config.strip_whitespace:
            text = text.strip()
            
        if self.config.remove_extra_spaces:
            text = re.sub(r'\s+', ' ', text)
            
        if self.config.remove_special_chars and self._special_chars_pattern:
            text = self._special_chars_pattern.sub('', text)
            
        if self.config.normalize_unicode:
            text = text.encode('utf-8', 'ignore').decode('utf-8')
            
        if self.config.normalize_case:
            if self.config.case_type == "lower":
                text = text.lower()
            elif self.config.case_type == "upper":
                text = text.upper()
            elif self.config.case_type == "title":
                text = text.title()
                
        return text
        
    def _extract_links(self, text: str) -> List[str]:
        """
        提取鏈接
        
        Args:
            text: 文本內容
            
        Returns:
            List[str]: 鏈接列表
        """
        if not self.config.extract_links:
            return []
            
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        return re.findall(url_pattern, text)
        
    def _extract_emails(self, text: str) -> List[str]:
        """
        提取郵箱
        
        Args:
            text: 文本內容
            
        Returns:
            List[str]: 郵箱列表
        """
        if not self.config.extract_emails:
            return []
            
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        return re.findall(email_pattern, text)
        
    def _extract_phones(self, text: str) -> List[str]:
        """
        提取電話號碼
        
        Args:
            text: 文本內容
            
        Returns:
            List[str]: 電話號碼列表
        """
        if not self.config.extract_phones:
            return []
            
        phone_pattern = r'\b\d{3}[-.]?\d{3,4}[-.]?\d{4}\b'
        return re.findall(phone_pattern, text)
        
    def _extract_dates(self, text: str) -> List[str]:
        """
        提取日期
        
        Args:
            text: 文本內容
            
        Returns:
            List[str]: 日期列表
        """
        if not self.config.extract_dates:
            return []
            
        date_pattern = r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?'
        return re.findall(date_pattern, text)
        
    def _extract_numbers(self, text: str) -> List[str]:
        """
        提取數字
        
        Args:
            text: 文本內容
            
        Returns:
            List[str]: 數字列表
        """
        if not self.config.extract_numbers:
            return []
            
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        return re.findall(number_pattern, text)
        
    def _validate_text(self, text: str) -> bool:
        """
        驗證文本
        
        Args:
            text: 文本內容
            
        Returns:
            bool: 是否有效
        """
        if not text:
            if self.config.error_on_empty:
                raise ExtractorError("文本為空")
            return False
            
        if self.config.min_length is not None and len(text) < self.config.min_length:
            raise ExtractorError(f"文本長度少於最小值 {self.config.min_length}")
            
        if self.config.max_length is not None and len(text) > self.config.max_length:
            raise ExtractorError(f"文本長度超過最大值 {self.config.max_length}")
            
        return True
        
    @handle_extractor_error()
    def _extract(self, driver: Any) -> Dict[str, Any]:
        """
        提取文本數據
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            Dict[str, Any]: 文本數據
        """
        element = self.find_text_element(driver)
        if not element:
            return {}
            
        text = element.text
        if self.config.remove_html_tags:
            text = re.sub(r'<[^>]+>', '', text)
            
        if self.config.decode_html_entities:
            text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
            
        text = self._clean_text(text)
        
        if self.config.validate_content:
            self._validate_text(text)
            
        result = {
            'text': text,
            'length': len(text),
            'links': self._extract_links(text),
            'emails': self._extract_emails(text),
            'phones': self._extract_phones(text),
            'dates': self._extract_dates(text),
            'numbers': self._extract_numbers(text)
        }
        
        return result
        
    def extract(self, driver: Any) -> ExtractorResult:
        """
        提取文本數據
        
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
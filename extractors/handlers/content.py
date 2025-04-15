#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
內容提取器模組

提供網頁內容提取功能，包括：
1. 標題提取
2. 正文提取
3. 元數據提取
4. 鏈接提取
"""

import logging
from typing import Any, Dict, List, Optional, Union
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from ..core.base import BaseExtractor
from ..core.error import ExtractorError, handle_extractor_error
from .web import WebExtractor

class ContentExtractor(WebExtractor):
    """內容提取器類別"""
    
    def __init__(
        self,
        driver: WebDriver,
        config: Optional[Union[Dict[str, Any], BaseConfig]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化內容提取器
        
        Args:
            driver: WebDriver 實例
            config: 配置字典或配置對象
            logger: 日誌記錄器
        """
        super().__init__(driver, config, logger)
        self.config.setdefault('selectors', {
            'title': '//h1',
            'content': '//article',
            'metadata': {
                'author': '//meta[@name="author"]/@content',
                'description': '//meta[@name="description"]/@content',
                'keywords': '//meta[@name="keywords"]/@content'
            },
            'links': '//a[@href]'
        })
        
    def _validate_config(self) -> bool:
        """
        驗證配置
        
        Returns:
            是否驗證通過
        """
        if not super()._validate_config():
            return False
            
        required_fields = ['selectors']
        return all(field in self.config for field in required_fields)
        
    @handle_extractor_error()
    def extract_title(self) -> str:
        """
        提取標題
        
        Returns:
            頁面標題
        """
        try:
            return self.get_text(By.XPATH, self.config['selectors']['title'])
        except ExtractorError:
            return self.driver.title
            
    @handle_extractor_error()
    def extract_content(self) -> str:
        """
        提取正文
        
        Returns:
            頁面正文
        """
        content = self.get_text(By.XPATH, self.config['selectors']['content'])
        return content.strip()
        
    @handle_extractor_error()
    def extract_metadata(self) -> Dict[str, str]:
        """
        提取元數據
        
        Returns:
            元數據字典
        """
        metadata = {}
        for key, selector in self.config['selectors']['metadata'].items():
            try:
                value = self.get_attribute(By.XPATH, selector, 'content')
                metadata[key] = value
            except ExtractorError:
                continue
        return metadata
        
    @handle_extractor_error()
    def extract_links(self) -> List[Dict[str, str]]:
        """
        提取鏈接
        
        Returns:
            鏈接列表
        """
        links = []
        elements = self.find_elements(By.XPATH, self.config['selectors']['links'])
        for element in elements:
            try:
                href = element.get_attribute('href')
                text = element.text.strip()
                if href and text:
                    links.append({
                        'url': href,
                        'text': text
                    })
            except ExtractorError:
                continue
        return links
        
    def _extract(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        執行提取
        
        Args:
            *args: 位置參數
            **kwargs: 關鍵字參數
            
        Returns:
            提取結果
        """
        return {
            'title': self.extract_title(),
            'content': self.extract_content(),
            'metadata': self.extract_metadata(),
            'links': self.extract_links()
        } 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
鏈接提取器模組

提供鏈接數據提取功能，包括：
1. 鏈接定位
2. 鏈接驗證
3. 鏈接分類
4. 鏈接處理
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional, Union, Pattern, Set
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests

from ..core.base import BaseExtractor
from ..core.types import ExtractorConfig, ExtractorResult
from ..core.error import ExtractorError, handle_extractor_error

@dataclass
class LinkExtractorConfig(ExtractorConfig):
    """鏈接提取器配置"""
    link_selector: str = "a"
    wait_timeout: float = 10.0
    base_url: Optional[str] = None
    normalize_urls: bool = True
    remove_fragments: bool = True
    remove_duplicates: bool = True
    validate_urls: bool = True
    check_status: bool = False
    follow_redirects: bool = True
    max_redirects: int = 5
    timeout: float = 10.0
    allowed_schemes: List[str] = None
    allowed_domains: List[str] = None
    excluded_domains: List[str] = None
    allowed_paths: List[str] = None
    excluded_paths: List[str] = None
    allowed_extensions: List[str] = None
    excluded_extensions: List[str] = None
    extract_text: bool = True
    extract_title: bool = True
    extract_rel: bool = True
    extract_target: bool = True
    extract_href: bool = True
    extract_id: bool = True
    extract_class: bool = True
    extract_attributes: List[str] = None
    error_on_empty: bool = True
    error_on_invalid: bool = True
    error_on_timeout: bool = True
    retry_on_error: bool = True
    retry_count: int = 3
    retry_delay: float = 1.0

class LinkExtractor(BaseExtractor):
    """鏈接提取器類別"""
    
    def __init__(
        self,
        config: Optional[Union[Dict[str, Any], LinkExtractorConfig]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化鏈接提取器
        
        Args:
            config: 配置字典或配置對象
            logger: 日誌記錄器
        """
        super().__init__(config, logger)
        self.config = config if isinstance(config, LinkExtractorConfig) else LinkExtractorConfig(**(config or {}))
        if self.config.allowed_schemes is None:
            self.config.allowed_schemes = ["http", "https"]
        if self.config.allowed_extensions is None:
            self.config.allowed_extensions = [".html", ".htm", ".php", ".asp", ".aspx", ".jsp"]
        if self.config.excluded_extensions is None:
            self.config.excluded_extensions = [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx"]
        if self.config.extract_attributes is None:
            self.config.extract_attributes = ["data-*", "aria-*"]
            
    def _validate_config(self) -> bool:
        """
        驗證配置
        
        Returns:
            bool: 是否有效
        """
        try:
            if not self.config.link_selector:
                raise ExtractorError("鏈接選擇器不能為空")
                
            if self.config.max_redirects < 0:
                raise ExtractorError("最大重定向次數不能為負數")
                
            if self.config.timeout < 0:
                raise ExtractorError("超時時間不能為負數")
                
            if self.config.allowed_schemes and not all(s in ["http", "https", "ftp", "mailto", "tel"] for s in self.config.allowed_schemes):
                raise ExtractorError("不支持的協議")
                
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
    def find_link_elements(self, driver: Any) -> List[Any]:
        """
        查找鏈接元素
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            List[Any]: 鏈接元素列表
        """
        try:
            elements = WebDriverWait(driver, self.config.wait_timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.config.link_selector))
            )
            return elements
        except TimeoutException:
            if self.config.error_on_timeout:
                raise ExtractorError("等待鏈接元素超時")
            return []
            
    def _get_link_info(self, element: Any) -> Dict[str, Any]:
        """
        獲取鏈接信息
        
        Args:
            element: 鏈接元素
            
        Returns:
            Dict[str, Any]: 鏈接信息
        """
        info = {}
        
        if self.config.extract_text:
            info['text'] = element.text.strip()
            
        if self.config.extract_title:
            info['title'] = element.get_attribute('title') or ''
            
        if self.config.extract_rel:
            info['rel'] = element.get_attribute('rel') or ''
            
        if self.config.extract_target:
            info['target'] = element.get_attribute('target') or ''
            
        if self.config.extract_href:
            info['href'] = element.get_attribute('href') or ''
            
        if self.config.extract_id:
            info['id'] = element.get_attribute('id') or ''
            
        if self.config.extract_class:
            info['class'] = element.get_attribute('class') or ''
            
        if self.config.extract_attributes:
            for attr in self.config.extract_attributes:
                if attr.endswith('*'):
                    prefix = attr[:-1]
                    for name, value in element.get_property('attributes').items():
                        if name.startswith(prefix):
                            info[name] = value
                else:
                    value = element.get_attribute(attr)
                    if value:
                        info[attr] = value
                        
        return info
        
    def _normalize_url(self, url: str) -> str:
        """
        標準化URL
        
        Args:
            url: 原始URL
            
        Returns:
            str: 標準化後的URL
        """
        if not url:
            return ''
            
        # 移除空白字符
        url = url.strip()
        
        # 處理相對URL
        if self.config.base_url and not urlparse(url).netloc:
            url = urljoin(self.config.base_url, url)
            
        # 移除URL片段
        if self.config.remove_fragments:
            url = url.split('#')[0]
            
        return url
        
    def _validate_url(self, url: str) -> bool:
        """
        驗證URL
        
        Args:
            url: URL
        
        Returns:
            bool: 是否有效
        """
        try:
            if not url:
                if self.config.error_on_empty:
                    raise ExtractorError("URL為空")
                return False
                
            parsed = urlparse(url)
            
            # 驗證協議
            if self.config.allowed_schemes and parsed.scheme not in self.config.allowed_schemes:
                raise ExtractorError(f"不支持的協議: {parsed.scheme}")
                
            # 驗證域名
            if self.config.allowed_domains and not any(parsed.netloc.endswith(d) for d in self.config.allowed_domains):
                raise ExtractorError(f"不允許的域名: {parsed.netloc}")
                
            if self.config.excluded_domains and any(parsed.netloc.endswith(d) for d in self.config.excluded_domains):
                raise ExtractorError(f"排除的域名: {parsed.netloc}")
                
            # 驗證路徑
            if self.config.allowed_paths and not any(parsed.path.startswith(p) for p in self.config.allowed_paths):
                raise ExtractorError(f"不允許的路徑: {parsed.path}")
                
            if self.config.excluded_paths and any(parsed.path.startswith(p) for p in self.config.excluded_paths):
                raise ExtractorError(f"排除的路徑: {parsed.path}")
                
            # 驗證擴展名
            ext = os.path.splitext(parsed.path)[1].lower()
            if self.config.allowed_extensions and ext not in self.config.allowed_extensions:
                raise ExtractorError(f"不允許的擴展名: {ext}")
                
            if self.config.excluded_extensions and ext in self.config.excluded_extensions:
                raise ExtractorError(f"排除的擴展名: {ext}")
                
            return True
            
        except Exception as e:
            if self.config.error_on_invalid:
                raise ExtractorError(f"URL驗證失敗: {str(e)}")
            return False
            
    def _check_url_status(self, url: str) -> int:
        """
        檢查URL狀態
        
        Args:
            url: URL
            
        Returns:
            int: HTTP狀態碼
        """
        try:
            response = requests.head(
                url,
                allow_redirects=self.config.follow_redirects,
                timeout=self.config.timeout
            )
            return response.status_code
        except Exception as e:
            raise ExtractorError(f"檢查URL狀態失敗: {str(e)}")
            
    @handle_extractor_error()
    def _extract(self, driver: Any) -> List[Dict[str, Any]]:
        """
        提取鏈接數據
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            List[Dict[str, Any]]: 鏈接數據列表
        """
        elements = self.find_link_elements(driver)
        if not elements:
            return []
            
        results = []
        seen_urls = set()
        
        for element in elements:
            try:
                # 獲取鏈接信息
                info = self._get_link_info(element)
                if not info.get('href'):
                    continue
                    
                # 標準化URL
                url = self._normalize_url(info['href'])
                if not url:
                    continue
                    
                # 驗證URL
                if self.config.validate_urls and not self._validate_url(url):
                    continue
                    
                # 檢查URL狀態
                if self.config.check_status:
                    try:
                        status = self._check_url_status(url)
                        info['status'] = status
                    except Exception as e:
                        self.logger.warning(f"檢查URL狀態失敗: {str(e)}")
                        continue
                        
                # 移除重複URL
                if self.config.remove_duplicates:
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    
                # 更新信息
                info['url'] = url
                results.append(info)
                
            except Exception as e:
                self.logger.warning(f"處理鏈接失敗: {str(e)}")
                continue
                
        return results
        
    def extract(self, driver: Any) -> ExtractorResult:
        """
        提取鏈接數據
        
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
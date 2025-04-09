#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTML清理工具模組

提供處理和清理HTML內容的工具類和函數
"""

import re
import logging
from typing import Optional, Dict, List, Union, Any

from ..config import HtmlCleaningOptions
from .url_normalizer import URLNormalizer, normalize_url, URLNormalizerConfig

# 檢查BeautifulSoup是否可用
try:
    from bs4 import BeautifulSoup
    SOUP_AVAILABLE = True
except ImportError:
    SOUP_AVAILABLE = False
    

class HTMLCleaner:
    """HTML清理和處理工具類"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        初始化HTML清理器
        
        Args:
            base_url: 基礎URL，用於處理相對路徑
        """
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
    
    def set_base_url(self, base_url: str) -> None:
        """
        設置基礎URL
        
        Args:
            base_url: 基礎URL
        """
        self.base_url = base_url
    
    def remove_scripts(self, html: str) -> str:
        """
        移除HTML中的腳本和樣式
        
        Args:
            html: HTML內容
            
        Returns:
            清理後的HTML
        """
        if not html:
            return html
            
        if not SOUP_AVAILABLE:
            # 簡單的腳本和樣式移除
            html = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
            html = re.sub(r'<style.*?</style>', '', html, flags=re.DOTALL)
            return html
            
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 移除script和style標籤
            for tag in soup(['script', 'style']):
                tag.decompose()
                
            return str(soup)
        except Exception as e:
            self.logger.warning(f"移除HTML腳本時出錯: {str(e)}")
            return html
    
    def remove_ads(self, html: str, ad_selectors: Optional[List[str]] = None) -> str:
        """
        移除HTML中的廣告元素
        
        Args:
            html: HTML內容
            ad_selectors: 額外的廣告選擇器
            
        Returns:
            清理後的HTML
        """
        if not html or not SOUP_AVAILABLE:
            return html
            
        if ad_selectors is None:
            ad_selectors = []
            
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 移除常見廣告類和ID
            ad_classes = ['ad', 'ads', 'banner', 'advertisement', 'popup']
            ad_ids = ['ad', 'ads', 'banner', 'advertisement']
            
            # 類名匹配
            for ad_class in ad_classes:
                for el in soup.find_all(class_=re.compile(ad_class, re.IGNORECASE)):
                    el.decompose()
            
            # ID匹配
            for ad_id in ad_ids:
                for el in soup.find_all(id=re.compile(ad_id, re.IGNORECASE)):
                    el.decompose()
                    
            # 額外選擇器
            for selector in ad_selectors:
                for el in soup.select(selector):
                    el.decompose()
            
            return str(soup)
        except Exception as e:
            self.logger.warning(f"移除HTML廣告時出錯: {str(e)}")
            return html
    
    def html_to_text(self, html: str, separator: str = ' ') -> str:
        """
        將HTML轉換為純文本
        
        Args:
            html: HTML內容
            separator: 文本分隔符
            
        Returns:
            純文本內容
        """
        if not html:
            return ""
            
        if not SOUP_AVAILABLE:
            # 簡單的HTML標籤清理
            return re.sub(r'<[^>]+>', '', html)
            
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(separator=separator, strip=True)
        except Exception as e:
            self.logger.warning(f"HTML轉文本時出錯: {str(e)}")
            return re.sub(r'<[^>]+>', '', html)
            
    def extract_images(self, html: str) -> List[Dict[str, str]]:
        """
        從HTML中提取圖片信息
        
        Args:
            html: HTML內容
            
        Returns:
            圖片信息列表，包含url、alt等屬性
        """
        if not html or not SOUP_AVAILABLE:
            return []
            
        try:
            soup = BeautifulSoup(html, 'html.parser')
            images = []
            
            for img in soup.find_all('img'):
                # 獲取src屬性，可能在src或data-src中
                src = img.get('src') or img.get('data-src', '')
                if src:
                    normalized_url = normalize_url(src, self.base_url)
                    images.append({
                        'url': normalized_url,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', ''),
                        'width': img.get('width', ''),
                        'height': img.get('height', '')
                    })
            
            return images
        except Exception as e:
            self.logger.warning(f"提取HTML圖片時出錯: {str(e)}")
            return []
    
    def extract_links(self, html: str) -> List[Dict[str, str]]:
        """
        從HTML中提取鏈接信息
        
        Args:
            html: HTML內容
            
        Returns:
            鏈接信息列表，包含url、text等屬性
        """
        if not html or not SOUP_AVAILABLE:
            return []
            
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            for a in soup.find_all('a'):
                href = a.get('href', '')
                if href:
                    normalized_url = normalize_url(href, self.base_url)
                    links.append({
                        'url': normalized_url,
                        'text': a.get_text().strip(),
                        'title': a.get('title', ''),
                        'rel': a.get('rel', ''),
                        'target': a.get('target', '')
                    })
            
            return links
        except Exception as e:
            self.logger.warning(f"提取HTML鏈接時出錯: {str(e)}")
            return []
    
    def clean_html(self, html: str, options: Optional[HtmlCleaningOptions] = None) -> str:
        """
        清理HTML內容
        
        Args:
            html: HTML內容
            options: 清理選項
            
        Returns:
            清理後的HTML
        """
        if not html:
            return html
            
        options = options or HtmlCleaningOptions()
        
        try:
            # 移除腳本和樣式
            if options.remove_scripts:
                html = self.remove_scripts(html)
            
            # 移除註釋
            if options.remove_comments:
                html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
            
            # 移除廣告
            if options.remove_ads:
                html = self.remove_ads(html, options.ad_selectors)
            
            return html
        except Exception as e:
            self.logger.warning(f"清理HTML時出錯: {str(e)}")
            return html
    
    def process_html(self, html: str, options: Optional[HtmlCleaningOptions] = None) -> Dict[str, Any]:
        """
        處理HTML內容，提取文本和資源
        
        Args:
            html: HTML內容
            options: 處理選項
            
        Returns:
            處理結果字典，包含text、cleaned_html、images、links等
        """
        options = options or HtmlCleaningOptions()
        result = {
            'original_html': html,
            'text': '',
            'cleaned_html': '',
            'images': [],
            'links': []
        }
        
        if not html:
            return result
            
        try:
            # 清理HTML
            cleaned_html = self.clean_html(html, options)
            result['cleaned_html'] = cleaned_html
            
            # 提取純文本
            result['text'] = self.html_to_text(cleaned_html)
            
            # 提取圖片
            if options.extract_images:
                result['images'] = self.extract_images(cleaned_html)
            
            # 提取鏈接
            if options.extract_links:
                result['links'] = self.extract_links(cleaned_html)
            
            return result
        except Exception as e:
            self.logger.warning(f"處理HTML時出錯: {str(e)}")
            return result


# 單例模式，提供一個全局實例
default_cleaner = HTMLCleaner()


def clean_html(html: str, options: Optional[HtmlCleaningOptions] = None) -> str:
    """
    清理HTML的便捷函數
    
    Args:
        html: HTML內容
        options: 清理選項
        
    Returns:
        清理後的HTML
    """
    return default_cleaner.clean_html(html, options)


def html_to_text(html: str, separator: str = ' ') -> str:
    """
    HTML轉文本的便捷函數
    
    Args:
        html: HTML內容
        separator: 文本分隔符
        
    Returns:
        純文本內容
    """
    return default_cleaner.html_to_text(html, separator)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文本清理工具模組

提供清理和格式化文本的工具類和函數
"""

import re
import logging
from typing import Optional, Dict, List

from ..config import TextCleaningOptions


class TextCleaner:
    """文本清理工具類"""
    
    def __init__(self, default_options: Optional[TextCleaningOptions] = None):
        """
        初始化文本清理器
        
        Args:
            default_options: 默認清理選項，如果不提供則使用默認配置
        """
        self.default_options = default_options or TextCleaningOptions()
        self.logger = logging.getLogger(__name__)
    
    def clean_text(self, text: str, options: Optional[TextCleaningOptions] = None) -> str:
        """
        清理文本，移除多餘空白、換行等
        
        Args:
            text: 原始文本
            options: 清理選項，如果不提供則使用默認配置
            
        Returns:
            清理後的文本
        """
        return self._clean_text(text, options or self.default_options)
    
    @staticmethod
    def _clean_text(text: str, options: TextCleaningOptions) -> str:
        """
        執行文本清理
        
        Args:
            text: 原始文本
            options: 清理選項
            
        Returns:
            清理後的文本
        """
        if not text:
            return ""
            
        # 移除空白和換行
        if options.remove_whitespace:
            text = re.sub(r'\s+', ' ', text)
        
        if options.remove_newlines:
            text = text.replace('\n', ' ')
        
        # 大小寫轉換
        if options.lowercase:
            text = text.lower()
        elif options.uppercase:
            text = text.upper()
        
        # 自定義替換
        for old, new in options.custom_replacements.items():
            text = text.replace(old, new)
        
        # 修剪頭尾空白
        if options.trim:
            text = text.strip()
        
        return text
    
    def clean_html_text(self, html_text: str, options: Optional[TextCleaningOptions] = None) -> str:
        """
        清理HTML文本，移除HTML標籤
        
        Args:
            html_text: HTML文本
            options: 清理選項，如果不提供則使用默認配置
            
        Returns:
            清理後的純文本
        """
        if not html_text:
            return ""
        
        # 移除HTML標籤
        text = re.sub(r'<[^>]+>', '', html_text)
        
        # 清理文本
        return self.clean_text(text, options)
    
    def truncate_text(self, text: str, max_length: int, suffix: str = '...') -> str:
        """
        截斷文本到指定長度
        
        Args:
            text: 原始文本
            max_length: 最大長度
            suffix: 截斷後添加的後綴
            
        Returns:
            截斷後的文本
        """
        if not text or len(text) <= max_length:
            return text
        
        # 截斷文本，保留完整單詞
        truncated = text[:max_length]
        
        # 嘗試在單詞邊界截斷
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:  # 只有在靠近末尾時才在單詞邊界截斷
            truncated = truncated[:last_space]
        
        return truncated + suffix
    
    def apply_regex(self, text: str, pattern: str, group: int = 1) -> Optional[str]:
        """
        應用正則表達式提取文本
        
        Args:
            text: 原始文本
            pattern: 正則表達式模式
            group: 要提取的匹配組
            
        Returns:
            提取的文本，如果沒有匹配則返回None
        """
        try:
            match = re.search(pattern, text)
            return match.group(group) if match else None
        except Exception as e:
            self.logger.warning(f"正則提取失敗: {e}")
            return None
    
    def remove_symbols(self, text: str, keep_list: Optional[List[str]] = None) -> str:
        """
        移除標點符號
        
        Args:
            text: 原始文本
            keep_list: 要保留的符號列表
            
        Returns:
            處理後的文本
        """
        if not text:
            return ""
            
        # 預設保留的符號
        keep_list = keep_list or [' ']
        keep_chars = ''.join(keep_list)
        
        # 構建模式，排除保留的符號
        pattern = r'[^\w\s' + re.escape(keep_chars) + r']' if keep_chars else r'[^\w\s]'
        
        # 移除標點符號
        return re.sub(pattern, '', text)


# 單例模式，提供一個全局實例
default_cleaner = TextCleaner()


def clean_text(text: str, options: Optional[TextCleaningOptions] = None) -> str:
    """
    清理文本的便捷函數
    
    Args:
        text: 原始文本
        options: 清理選項
        
    Returns:
        清理後的文本
    """
    return default_cleaner.clean_text(text, options)


def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    """
    截斷文本的便捷函數
    
    Args:
        text: 原始文本
        max_length: 最大長度
        suffix: 截斷後添加的後綴
        
    Returns:
        截斷後的文本
    """
    return default_cleaner.truncate_text(text, max_length, suffix)
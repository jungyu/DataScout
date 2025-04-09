#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文本清理工具模組

提供清理和格式化文本的工具類和函數，包括：
- 文本清理和格式化
- HTML 文本處理
- 文本截斷
- 正則表達式提取
- 符號處理
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Union, Pattern

@dataclass
class TextCleanerConfig:
    """文本清理器配置類"""
    
    # 基本清理選項
    remove_whitespace: bool = True
    remove_newlines: bool = True
    trim: bool = True
    lowercase: bool = False
    uppercase: bool = False
    
    # 自定義替換
    custom_replacements: Dict[str, str] = field(default_factory=dict)
    
    # 正則表達式模式
    regex_patterns: Dict[str, Union[str, Pattern]] = field(default_factory=dict)
    
    # 符號處理
    keep_symbols: List[str] = field(default_factory=lambda: [' '])
    remove_emojis: bool = True
    remove_urls: bool = True
    
    # 截斷設置
    max_length: int = 0
    truncate_suffix: str = '...'
    
    def __post_init__(self):
        """初始化後處理"""
        # 編譯正則表達式模式
        self.compiled_patterns = {
            name: re.compile(pattern) if isinstance(pattern, str) else pattern
            for name, pattern in self.regex_patterns.items()
        }


class TextCleaner:
    """文本清理工具類"""
    
    def __init__(self, config: Optional[TextCleanerConfig] = None):
        """
        初始化文本清理器
        
        Args:
            config: 清理器配置，如果不提供則使用默認配置
        """
        self.config = config or TextCleanerConfig()
        self.logger = logging.getLogger(__name__)
        
        # 預編譯常用正則表達式
        self._url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        self._emoji_pattern = re.compile(
            r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]'
        )
    
    def clean_text(self, text: str, config: Optional[TextCleanerConfig] = None) -> str:
        """
        清理文本，移除多餘空白、換行等
        
        Args:
            text: 原始文本
            config: 清理配置，如果不提供則使用實例配置
            
        Returns:
            清理後的文本
        """
        if not text:
            return ""
            
        config = config or self.config
        text = self._clean_text(text, config)
        
        # 應用自定義正則表達式
        for pattern in config.compiled_patterns.values():
            text = pattern.sub('', text)
        
        # 移除 URL
        if config.remove_urls:
            text = self._url_pattern.sub('', text)
        
        # 移除表情符號
        if config.remove_emojis:
            text = self._emoji_pattern.sub('', text)
        
        # 截斷文本
        if config.max_length > 0:
            text = self.truncate_text(text, config.max_length, config.truncate_suffix)
        
        return text
    
    @staticmethod
    def _clean_text(text: str, config: TextCleanerConfig) -> str:
        """
        執行基本文本清理
        
        Args:
            text: 原始文本
            config: 清理配置
            
        Returns:
            清理後的文本
        """
        # 移除空白和換行
        if config.remove_whitespace:
            text = re.sub(r'\s+', ' ', text)
        
        if config.remove_newlines:
            text = text.replace('\n', ' ')
        
        # 大小寫轉換
        if config.lowercase:
            text = text.lower()
        elif config.uppercase:
            text = text.upper()
        
        # 自定義替換
        for old, new in config.custom_replacements.items():
            text = text.replace(old, new)
        
        # 修剪頭尾空白
        if config.trim:
            text = text.strip()
        
        return text
    
    def clean_html_text(self, html_text: str, config: Optional[TextCleanerConfig] = None) -> str:
        """
        清理HTML文本，移除HTML標籤
        
        Args:
            html_text: HTML文本
            config: 清理配置，如果不提供則使用實例配置
            
        Returns:
            清理後的純文本
        """
        if not html_text:
            return ""
        
        # 移除HTML標籤
        text = re.sub(r'<[^>]+>', '', html_text)
        
        # 清理文本
        return self.clean_text(text, config)
    
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
    
    def apply_regex(self, text: str, pattern: Union[str, Pattern], group: int = 1) -> Optional[str]:
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
            if isinstance(pattern, str):
                pattern = re.compile(pattern)
            match = pattern.search(text)
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
            
        keep_list = keep_list or self.config.keep_symbols
        keep_chars = ''.join(keep_list)
        
        # 構建模式，排除保留的符號
        pattern = r'[^\w\s' + re.escape(keep_chars) + r']' if keep_chars else r'[^\w\s]'
        
        # 移除標點符號
        return re.sub(pattern, '', text)


# 創建默認實例
default_cleaner = TextCleaner()


def clean_text(text: str, config: Optional[TextCleanerConfig] = None) -> str:
    """
    清理文本的便捷函數
    
    Args:
        text: 原始文本
        config: 清理配置
        
    Returns:
        清理後的文本
    """
    return default_cleaner.clean_text(text, config)


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
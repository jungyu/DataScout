#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提取器工具模組

此模組提供各種數據處理和轉換的工具類，包括：
- 文本清理和處理
- URL 規範化
- HTML 清理和解析
- 日期解析和格式化
- 數字解析和格式化
"""

# 文本處理工具
from .text_cleaner import TextCleaner, TextCleanerConfig
from .html_cleaner import HTMLCleaner, HTMLCleanerConfig

# URL 處理工具
from .url_normalizer import URLNormalizer, URLNormalizerConfig

# 數據解析工具
from .date_parser import DateParser, DateParserConfig
from .number_parser import NumberParser, NumberParserConfig

# 導出所有工具類和配置類
__all__ = [
    # 文本處理
    'TextCleaner',
    'TextCleanerConfig',
    'HTMLCleaner',
    'HTMLCleanerConfig',
    
    # URL 處理
    'URLNormalizer',
    'URLNormalizerConfig',
    
    # 數據解析
    'DateParser',
    'DateParserConfig',
    'NumberParser',
    'NumberParserConfig'
]

# 工具類工廠函數
def create_text_cleaner(**kwargs) -> TextCleaner:
    """
    創建文本清理器
    
    Args:
        **kwargs: 配置參數
        
    Returns:
        TextCleaner: 文本清理器實例
    """
    return TextCleaner(**kwargs)

def create_html_cleaner(**kwargs) -> HTMLCleaner:
    """
    創建 HTML 清理器
    
    Args:
        **kwargs: 配置參數
        
    Returns:
        HTMLCleaner: HTML 清理器實例
    """
    return HTMLCleaner(**kwargs)

def create_url_normalizer(**kwargs) -> URLNormalizer:
    """
    創建 URL 規範化器
    
    Args:
        **kwargs: 配置參數
        
    Returns:
        URLNormalizer: URL 規範化器實例
    """
    return URLNormalizer(**kwargs)

def create_date_parser(**kwargs) -> DateParser:
    """
    創建日期解析器
    
    Args:
        **kwargs: 配置參數
        
    Returns:
        DateParser: 日期解析器實例
    """
    return DateParser(**kwargs)

def create_number_parser(**kwargs) -> NumberParser:
    """
    創建數字解析器
    
    Args:
        **kwargs: 配置參數
        
    Returns:
        NumberParser: 數字解析器實例
    """
    return NumberParser(**kwargs)

# 版本信息
__version__ = '0.1.0'
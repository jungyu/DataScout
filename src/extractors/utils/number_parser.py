#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數字解析工具模組

提供解析各種格式數字的工具類和函數，包括：
- 中文數字解析
- 貨幣金額解析
- 百分比解析
- 科學計數法解析
- 數字提取
"""

import re
import logging
from typing import Optional, Dict, List, Union, Pattern, Any
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class NumberParserConfig:
    """數字解析器配置類"""
    
    # 輸出格式
    decimal_places: int = 2
    rounding_mode: str = ROUND_HALF_UP
    
    # 中文數字映射
    cn_numbers: Dict[str, int] = field(default_factory=lambda: {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
        '壹': 1, '貳': 2, '參': 3, '肆': 4, '伍': 5,
        '陸': 6, '柒': 7, '捌': 8, '玖': 9
    })
    
    # 中文單位映射
    cn_units: Dict[str, int] = field(default_factory=lambda: {
        '十': 10, '拾': 10,
        '百': 100, '佰': 100,
        '千': 1000, '仟': 1000,
        '萬': 10000, '萬': 10000,
        '億': 100000000, '億': 100000000
    })
    
    # 貨幣符號映射
    currency_symbols: Dict[str, str] = field(default_factory=lambda: {
        '$': 'USD',
        '€': 'EUR',
        '£': 'GBP',
        '¥': 'CNY',
        'NT$': 'TWD',
        'HK$': 'HKD',
        'JP¥': 'JPY',
        '₩': 'KRW',
        '₹': 'INR',
        '₽': 'RUB'
    })
    
    # 正則表達式模式
    number_patterns: Dict[str, Union[str, Pattern]] = field(default_factory=lambda: {
        'integer': r'-?\d+',
        'decimal': r'-?\d+\.\d+',
        'scientific': r'-?\d+(?:\.\d+)?[eE][+-]?\d+',
        'percentage': r'-?\d+(?:\.\d+)?%',
        'currency': r'(?:[\$€£¥]|NT\$|HK\$|JP¥|₩|₹|₽)\s*-?\d+(?:,\d{3})*(?:\.\d+)?',
        'cn_number': r'[零一二三四五六七八九壹貳參肆伍陸柒捌玖]+(?:[十拾百佰千仟萬億]+[零一二三四五六七八九壹貳參肆伍陸柒捌玖]*)*'
    })
    
    def __post_init__(self):
        """初始化後處理"""
        # 編譯正則表達式模式
        self.compiled_patterns = {
            name: re.compile(pattern) if isinstance(pattern, str) else pattern
            for name, pattern in self.number_patterns.items()
        }


class NumberParser:
    """數字解析工具類"""
    
    def __init__(self, config: Optional[NumberParserConfig] = None):
        """
        初始化數字解析器
        
        Args:
            config: 解析器配置，如果不提供則使用默認配置
        """
        self.config = config or NumberParserConfig()
        self.logger = logging.getLogger(__name__)
    
    def parse_number(self, number_str: str) -> Optional[Decimal]:
        """
        解析各種格式的數字字符串
        
        Args:
            number_str: 數字字符串
            
        Returns:
            解析後的Decimal對象，如果無法解析則返回None
        """
        if not number_str:
            return None
        
        number_str = number_str.strip()
        
        try:
            # 1. 嘗試解析中文數字
            if self.config.compiled_patterns['cn_number'].match(number_str):
                return self._parse_cn_number(number_str)
            
            # 2. 嘗試解析科學計數法
            if self.config.compiled_patterns['scientific'].match(number_str):
                return Decimal(number_str)
            
            # 3. 嘗試解析小數
            if self.config.compiled_patterns['decimal'].match(number_str):
                return Decimal(number_str)
            
            # 4. 嘗試解析整數
            if self.config.compiled_patterns['integer'].match(number_str):
                return Decimal(number_str)
            
            # 5. 嘗試解析百分比
            if self.config.compiled_patterns['percentage'].match(number_str):
                return self._parse_percentage(number_str)
            
            # 6. 嘗試解析貨幣
            if self.config.compiled_patterns['currency'].match(number_str):
                return self._parse_currency(number_str)
            
            self.logger.warning(f"無法解析數字字符串: {number_str}")
            return None
            
        except Exception as e:
            self.logger.error(f"數字解析失敗: {e}")
            return None
    
    def _parse_cn_number(self, cn_str: str) -> Decimal:
        """
        解析中文數字
        
        Args:
            cn_str: 中文數字字符串
            
        Returns:
            解析後的Decimal對象
        """
        result = 0
        temp = 0
        unit = 1
        
        for char in reversed(cn_str):
            if char in self.config.cn_numbers:
                temp = self.config.cn_numbers[char]
                result += temp * unit
                temp = 0
            elif char in self.config.cn_units:
                unit = self.config.cn_units[char]
                if temp == 0:
                    temp = 1
        
        return Decimal(str(result))
    
    def _parse_percentage(self, percent_str: str) -> Decimal:
        """
        解析百分比
        
        Args:
            percent_str: 百分比字符串
            
        Returns:
            解析後的Decimal對象
        """
        number_str = percent_str.rstrip('%')
        return Decimal(number_str) / 100
    
    def _parse_currency(self, currency_str: str) -> Decimal:
        """
        解析貨幣金額
        
        Args:
            currency_str: 貨幣金額字符串
            
        Returns:
            解析後的Decimal對象
        """
        # 移除貨幣符號和空格
        for symbol in self.config.currency_symbols:
            if currency_str.startswith(symbol):
                number_str = currency_str[len(symbol):].strip()
                break
        else:
            number_str = currency_str
        
        # 移除千位分隔符
        number_str = number_str.replace(',', '')
        
        return Decimal(number_str)
    
    def format_number(self, number: Decimal, decimal_places: Optional[int] = None) -> str:
        """
        格式化數字
        
        Args:
            number: 要格式化的數字
            decimal_places: 小數位數
            
        Returns:
            格式化後的字符串
        """
        if decimal_places is None:
            decimal_places = self.config.decimal_places
        
        return str(number.quantize(
            Decimal(f'0.{"0" * decimal_places}'),
            rounding=self.config.rounding_mode
        ))
    
    def extract_numbers(self, text: str) -> List[Decimal]:
        """
        從文本中提取數字
        
        Args:
            text: 文本內容
            
        Returns:
            提取的數字列表
        """
        if not text:
            return []
        
        numbers = []
        
        # 嘗試所有數字模式
        for pattern in self.config.compiled_patterns.values():
            for match in pattern.finditer(text):
                number = self.parse_number(match.group(0))
                if number is not None:
                    numbers.append(number)
        
        return numbers


# 創建默認實例
default_parser = NumberParser()


def parse_number(number_str: str) -> Optional[Decimal]:
    """
    解析數字的便捷函數
    
    Args:
        number_str: 數字字符串
        
    Returns:
        解析後的Decimal對象
    """
    return default_parser.parse_number(number_str)


def format_number(number: Decimal, decimal_places: Optional[int] = None) -> str:
    """
    格式化數字的便捷函數
    
    Args:
        number: 要格式化的數字
        decimal_places: 小數位數
        
    Returns:
        格式化後的字符串
    """
    return default_parser.format_number(number, decimal_places)


def extract_numbers(text: str) -> List[Decimal]:
    """
    提取數字的便捷函數
    
    Args:
        text: 文本內容
        
    Returns:
        提取的數字列表
    """
    return default_parser.extract_numbers(text)
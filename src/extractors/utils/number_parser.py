#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數字解析工具模組

提供解析各種格式數字的工具類和函數
"""

import re
import logging
from typing import Optional, Union, List


class NumberParser:
    """數字解析工具類"""
    
    def __init__(self):
        """初始化數字解析器"""
        self.logger = logging.getLogger(__name__)
        
        # 數字正則表達式
        self.number_patterns = {
            'integer': re.compile(r'(?<!\d)[-+]?\d+(?!\d)'),
            'decimal': re.compile(r'(?<!\d)[-+]?\d+[.,]\d+(?!\d)'),
            'numeric': re.compile(r'(?<!\d)[-+]?\d+(?:[.,]\d+)?(?!\d)'),
            'percentage': re.compile(r'(?<!\d)[-+]?\d+(?:[.,]\d+)?%'),
            'price': re.compile(r'(?:[$€£¥₩₹]|NT\$)\s*\d+(?:[.,]\d+)?|\d+(?:[.,]\d+)?\s*(?:[$€£¥₩₹]|NT\$)')
        }
        
        # 中文數字映射
        self.cn_num_map = {
            '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '百': 100, '千': 1000, '萬': 10000, '億': 100000000
        }
    
    def parse_number(self, number_str: str) -> Union[int, float, str]:
        """
        從字符串中解析數字
        
        Args:
            number_str: 包含數字的字符串
            
        Returns:
            解析出的數字，無法解析時返回原字符串
        """
        if not number_str:
            return 0
            
        try:
            # 移除非數字相關字符，保留數字、小數點、正負號
            clean_str = self._clean_number_string(number_str)
            
            # 嘗試轉換
            if '.' in clean_str:
                return float(clean_str)
            else:
                return int(clean_str)
                
        except Exception as e:
            self.logger.debug(f"數字解析失敗: {e}")
            return number_str
    
    def _clean_number_string(self, number_str: str) -> str:
        """
        清理數字字符串
        
        Args:
            number_str: 原始字符串
            
        Returns:
            清理後的數字字符串
        """
        # 替換逗號和其他非數字字符
        clean_str = re.sub(r'[^\d.,\-+]', '', number_str)
        
        # 替換逗號為小數點
        clean_str = clean_str.replace(',', '.')
        
        # 處理多個小數點的情況
        if clean_str.count('.') > 1:
            parts = clean_str.split('.')
            clean_str = parts[0] + '.' + ''.join(parts[1:])
        
        return clean_str
    
    def extract_numbers(self, text: str, pattern_type: str = 'numeric') -> List[Union[int, float]]:
        """
        從文本中提取所有數字
        
        Args:
            text: 文本內容
            pattern_type: 模式類型，可選值: 'integer', 'decimal', 'numeric', 'percentage', 'price'
            
        Returns:
            提取的數字列表
        """
        if not text:
            return []
            
        pattern = self.number_patterns.get(pattern_type, self.number_patterns['numeric'])
        matches = pattern.findall(text)
        
        result = []
        for match in matches:
            try:
                # 對於百分比和價格，需要特殊處理
                if pattern_type == 'percentage':
                    # 移除百分號並轉換
                    num_str = re.sub(r'%', '', match)
                    num = self.parse_number(num_str)
                    result.append(num)
                elif pattern_type == 'price':
                    # 移除貨幣符號並轉換
                    num_str = re.sub(r'[$€£¥₩₹]|NT\$', '', match)
                    num = self.parse_number(num_str)
                    result.append(num)
                else:
                    num = self.parse_number(match)
                    result.append(num)
            except Exception as e:
                self.logger.debug(f"提取數字失敗: {e}")
        
        return result
    
    def parse_cn_number(self, cn_number: str) -> Optional[int]:
        """
        解析中文數字
        
        Args:
            cn_number: 中文數字字符串
            
        Returns:
            解析後的數字，無法解析時返回None
        """
        if not cn_number:
            return None
            
        try:
            result = 0
            temp = 0
            
            for char in cn_number:
                if char in self.cn_num_map:
                    if self.cn_num_map[char] < 10:
                        temp = self.cn_num_map[char]
                    elif char == '十' and temp == 0:  # 處理"十"開頭的情況
                        temp = 1
                        result += temp * self.cn_num_map[char]
                        temp = 0
                    else:
                        result += temp * self.cn_num_map[char]
                        temp = 0
            
            # 處理最後一位數字
            if temp > 0:
                result += temp
                
            return result
        except Exception as e:
            self.logger.debug(f"中文數字解析失敗: {e}")
            return None
    
    def format_number(self, number: Union[int, float], decimal_places: int = 2,
                     thousands_separator: bool = False, percentage: bool = False) -> str:
        """
        格式化數字
        
        Args:
            number: 要格式化的數字
            decimal_places: 小數位數
            thousands_separator: 是否添加千位分隔符
            percentage: 是否格式化為百分比
            
        Returns:
            格式化後的數字字符串
        """
        try:
            if percentage:
                # 百分比格式
                formatted = f"{number:.{decimal_places}f}%"
            else:
                # 普通數字格式
                if thousands_separator:
                    # 添加千位分隔符
                    if isinstance(number, int):
                        formatted = f"{number:,}"
                    else:
                        formatted = f"{number:,.{decimal_places}f}"
                else:
                    # 不添加千位分隔符
                    if isinstance(number, int):
                        formatted = str(number)
                    else:
                        formatted = f"{number:.{decimal_places}f}"
            
            return formatted
        except Exception as e:
            self.logger.warning(f"數字格式化失敗: {e}")
            return str(number)


# 單例模式，提供一個全局實例
default_parser = NumberParser()


def parse_number(number_str: str) -> Union[int, float, str]:
    """
    解析數字的便捷函數
    
    Args:
        number_str: 包含數字的字符串
        
    Returns:
        解析出的數字
    """
    return default_parser.parse_number(number_str)


def extract_numbers(text: str, pattern_type: str = 'numeric') -> List[Union[int, float]]:
    """
    提取數字的便捷函數
    
    Args:
        text: 文本內容
        pattern_type: 模式類型
        
    Returns:
        提取的數字列表
    """
    return default_parser.extract_numbers(text, pattern_type)


def format_number(number: Union[int, float], decimal_places: int = 2,
                thousands_separator: bool = False, percentage: bool = False) -> str:
    """
    格式化數字的便捷函數
    
    Args:
        number: 要格式化的數字
        decimal_places: 小數位數
        thousands_separator: 是否添加千位分隔符
        percentage: 是否格式化為百分比
        
    Returns:
        格式化後的數字字符串
    """
    return default_parser.format_number(number, decimal_places, thousands_separator, percentage)
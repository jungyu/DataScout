#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日期解析工具模組

提供解析各種格式日期字符串的工具類和函數
"""

import re
import logging
from datetime import datetime
from typing import Optional, Dict, List, Union, Any

# 檢查dateparser是否可用
try:
    import dateparser
    DATEPARSER_AVAILABLE = True
except ImportError:
    DATEPARSER_AVAILABLE = False


class DateParser:
    """日期解析工具類"""
    
    def __init__(self):
        """初始化日期解析器"""
        self.logger = logging.getLogger(__name__)
        
        # 常見日期格式
        self.common_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%Y/%m/%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
            "%Y年%m月%d日 %H:%M:%S",
            "%Y年%m月%d日 %H:%M",
            "%Y年%m月%d日",
            "%d.%m.%Y %H:%M:%S",
            "%d.%m.%Y %H:%M",
            "%d.%m.%Y",
            "%b %d, %Y %H:%M:%S",
            "%b %d, %Y %H:%M",
            "%b %d, %Y",
            "%d %b %Y %H:%M:%S",
            "%d %b %Y %H:%M",
            "%d %b %Y"
        ]
        
        # 中文日期正則
        self.cn_date_pattern = re.compile(r"(\d{2,4})[年\-/\.](\d{1,2})[月\-/\.](\d{1,2})日?")
        
        # 相對時間正則
        self.relative_patterns = {
            "cn": {
                "days_ago": re.compile(r"(\d+)天前"),
                "hours_ago": re.compile(r"(\d+)小時前"),
                "minutes_ago": re.compile(r"(\d+)分鐘前"),
                "just_now": re.compile(r"剛剛|剛才")
            },
            "en": {
                "days_ago": re.compile(r"(\d+) days? ago"),
                "hours_ago": re.compile(r"(\d+) hours? ago"),
                "minutes_ago": re.compile(r"(\d+) minutes? ago"),
                "just_now": re.compile(r"just now|moments ago")
            }
        }
    
    def parse_date(self, date_str: str, output_format: Optional[str] = None, 
                  default_timezone: Optional[str] = None) -> Optional[str]:
        """
        解析各種格式的日期字符串
        
        Args:
            date_str: 日期字符串
            output_format: 輸出格式
            default_timezone: 默認時區
            
        Returns:
            格式化後的日期字符串，如果無法解析則返回None
        """
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        # 1. 嘗試使用dateparser庫(如果可用)
        if DATEPARSER_AVAILABLE:
            try:
                settings = {}
                if default_timezone:
                    settings['TIMEZONE'] = default_timezone
                
                parsed_date = dateparser.parse(date_str, settings=settings)
                if parsed_date:
                    return self._format_date(parsed_date, output_format)
            except Exception as e:
                self.logger.debug(f"dateparser解析失敗: {e}")
        
        # 2. 嘗試使用常見日期格式
        for fmt in self.common_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return self._format_date(parsed_date, output_format)
            except ValueError:
                continue
        
        # 3. 嘗試解析中文日期
        match = self.cn_date_pattern.search(date_str)
        if match:
            try:
                year, month, day = match.groups()
                # 處理兩位數年份
                if len(year) == 2:
                    year = f"20{year}"
                parsed_date = datetime(int(year), int(month), int(day))
                return self._format_date(parsed_date, output_format)
            except Exception:
                pass
        
        # 4. 嘗試解析相對時間
        parsed_date = self._parse_relative_time(date_str)
        if parsed_date:
            return self._format_date(parsed_date, output_format)
        
        self.logger.warning(f"無法解析日期字符串: {date_str}")
        return None
    
    def _parse_relative_time(self, date_str: str) -> Optional[datetime]:
        """
        解析相對時間表達式
        
        Args:
            date_str: 相對時間字符串
            
        Returns:
            解析後的datetime對象
        """
        now = datetime.now()
        
        # 檢查中文相對時間
        for pattern_name, pattern in self.relative_patterns["cn"].items():
            match = pattern.search(date_str)
            if match:
                if pattern_name == "just_now":
                    return now
                elif pattern_name == "minutes_ago":
                    return now.replace(minute=now.minute - int(match.group(1)))
                elif pattern_name == "hours_ago":
                    return now.replace(hour=now.hour - int(match.group(1)))
                elif pattern_name == "days_ago":
                    return now.replace(day=now.day - int(match.group(1)))
        
        # 檢查英文相對時間
        for pattern_name, pattern in self.relative_patterns["en"].items():
            match = pattern.search(date_str)
            if match:
                if pattern_name == "just_now":
                    return now
                elif pattern_name == "minutes_ago":
                    return now.replace(minute=now.minute - int(match.group(1)))
                elif pattern_name == "hours_ago":
                    return now.replace(hour=now.hour - int(match.group(1)))
                elif pattern_name == "days_ago":
                    return now.replace(day=now.day - int(match.group(1)))
        
        return None
    
    def _format_date(self, date_obj: datetime, output_format: Optional[str] = None) -> str:
        """
        格式化日期對象
        
        Args:
            date_obj: 日期對象
            output_format: 輸出格式
            
        Returns:
            格式化後的日期字符串
        """
        if output_format:
            return date_obj.strftime(output_format)
        else:
            return date_obj.isoformat()
    
    def extract_date_from_text(self, text: str, output_format: Optional[str] = None) -> Optional[str]:
        """
        從文本中提取日期
        
        Args:
            text: 文本內容
            output_format: 輸出格式
            
        Returns:
            提取的日期字符串
        """
        if not text:
            return None
        
        # 嘗試常見日期模式
        date_patterns = [
            # ISO格式
            r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?",
            # 常見日期格式
            r"\d{4}[/\-年]\d{1,2}[/\-月]\d{1,2}日?",
            r"\d{1,2}[/\-]\d{1,2}[/\-]\d{4}",
            r"\d{1,2}\.\d{1,2}\.\d{4}",
            # 英文日期格式
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}",
            r"\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}"
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(0)
                return self.parse_date(date_str, output_format)
        
        return None


# 單例模式，提供一個全局實例
default_parser = DateParser()


def parse_date(date_str: str, output_format: Optional[str] = None) -> Optional[str]:
    """
    解析日期的便捷函數
    
    Args:
        date_str: 日期字符串
        output_format: 輸出格式
        
    Returns:
        格式化後的日期字符串
    """
    return default_parser.parse_date(date_str, output_format)


def extract_date_from_text(text: str, output_format: Optional[str] = None) -> Optional[str]:
    """
    從文本提取日期的便捷函數
    
    Args:
        text: 文本內容
        output_format: 輸出格式
        
    Returns:
        提取的日期字符串
    """
    return default_parser.extract_date_from_text(text, output_format)
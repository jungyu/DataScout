#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日期解析工具模組

提供解析各種格式日期字符串的工具類和函數，包括：
- 常見日期格式解析
- 中文日期解析
- 相對時間解析
- 時區處理
- 日期提取
"""

import re
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Union, Pattern, Any

# 檢查dateparser是否可用
try:
    import dateparser
    DATEPARSER_AVAILABLE = True
except ImportError:
    DATEPARSER_AVAILABLE = False

# 檢查arrow是否可用
try:
    import arrow
    ARROW_AVAILABLE = True
except ImportError:
    ARROW_AVAILABLE = False

@dataclass
class DateParserConfig:
    """日期解析器配置類"""
    
    # 輸出格式
    output_format: Optional[str] = None
    default_timezone: Optional[str] = None
    
    # 日期格式
    common_formats: List[str] = field(default_factory=lambda: [
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
    ])
    
    # 正則表達式模式
    date_patterns: Dict[str, Union[str, Pattern]] = field(default_factory=lambda: {
        "iso": r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?",
        "cn_date": r"(\d{2,4})[年\-/\.](\d{1,2})[月\-/\.](\d{1,2})日?",
        "common_date": r"\d{4}[/\-年]\d{1,2}[/\-月]\d{1,2}日?",
        "slash_date": r"\d{1,2}[/\-]\d{1,2}[/\-]\d{4}",
        "dot_date": r"\d{1,2}\.\d{1,2}\.\d{4}",
        "en_date1": r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}",
        "en_date2": r"\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}"
    })
    
    # 相對時間模式
    relative_patterns: Dict[str, Dict[str, Union[str, Pattern]]] = field(default_factory=lambda: {
        "cn": {
            "days_ago": r"(\d+)天前",
            "hours_ago": r"(\d+)小時前",
            "minutes_ago": r"(\d+)分鐘前",
            "just_now": r"剛剛|剛才"
        },
        "en": {
            "days_ago": r"(\d+) days? ago",
            "hours_ago": r"(\d+) hours? ago",
            "minutes_ago": r"(\d+) minutes? ago",
            "just_now": r"just now|moments ago"
        }
    })
    
    def __post_init__(self):
        """初始化後處理"""
        # 編譯正則表達式模式
        self.compiled_patterns = {
            name: re.compile(pattern) if isinstance(pattern, str) else pattern
            for name, pattern in self.date_patterns.items()
        }
        
        # 編譯相對時間模式
        self.compiled_relative_patterns = {
            lang: {
                name: re.compile(pattern) if isinstance(pattern, str) else pattern
                for name, pattern in patterns.items()
            }
            for lang, patterns in self.relative_patterns.items()
        }


class DateParser:
    """日期解析工具類"""
    
    def __init__(self, config: Optional[DateParserConfig] = None):
        """
        初始化日期解析器
        
        Args:
            config: 解析器配置，如果不提供則使用默認配置
        """
        self.config = config or DateParserConfig()
        self.logger = logging.getLogger(__name__)
    
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
        output_format = output_format or self.config.output_format
        default_timezone = default_timezone or self.config.default_timezone
        
        # 1. 嘗試使用arrow庫(如果可用)
        if ARROW_AVAILABLE:
            try:
                # 設置時區
                if default_timezone:
                    arrow_date = arrow.get(date_str, default_timezone)
                else:
                    arrow_date = arrow.get(date_str)
                
                if arrow_date:
                    if output_format:
                        return arrow_date.format(output_format)
                    return arrow_date.isoformat()
            except Exception as e:
                self.logger.debug(f"arrow解析失敗: {e}")
        
        # 2. 嘗試使用dateparser庫(如果可用)
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
        
        # 3. 嘗試使用常見日期格式
        for fmt in self.config.common_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return self._format_date(parsed_date, output_format)
            except ValueError:
                continue
        
        # 4. 嘗試解析中文日期
        match = self.config.compiled_patterns["cn_date"].search(date_str)
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
        
        # 5. 嘗試解析相對時間
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
        for pattern_name, pattern in self.config.compiled_relative_patterns["cn"].items():
            match = pattern.search(date_str)
            if match:
                if pattern_name == "just_now":
                    return now
                elif pattern_name == "minutes_ago":
                    return now - timedelta(minutes=int(match.group(1)))
                elif pattern_name == "hours_ago":
                    return now - timedelta(hours=int(match.group(1)))
                elif pattern_name == "days_ago":
                    return now - timedelta(days=int(match.group(1)))
        
        # 檢查英文相對時間
        for pattern_name, pattern in self.config.compiled_relative_patterns["en"].items():
            match = pattern.search(date_str)
            if match:
                if pattern_name == "just_now":
                    return now
                elif pattern_name == "minutes_ago":
                    return now - timedelta(minutes=int(match.group(1)))
                elif pattern_name == "hours_ago":
                    return now - timedelta(hours=int(match.group(1)))
                elif pattern_name == "days_ago":
                    return now - timedelta(days=int(match.group(1)))
        
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
        
        # 嘗試所有日期模式
        for pattern in self.config.compiled_patterns.values():
            match = pattern.search(text)
            if match:
                date_str = match.group(0)
                return self.parse_date(date_str, output_format)
        
        return None
    
    def shift(self, date_str: str, **kwargs) -> Optional[str]:
        """
        類似 moment.js 的 shift 功能，用於日期時間的增減
        
        Args:
            date_str: 日期字符串
            **kwargs: 要增減的時間參數，例如 days=3, hours=2, minutes=30
            
        Returns:
            計算後的日期字符串
        """
        if not ARROW_AVAILABLE:
            self.logger.warning("arrow庫未安裝，無法使用shift功能")
            return None
            
        try:
            arrow_date = arrow.get(date_str)
            shifted_date = arrow_date.shift(**kwargs)
            return shifted_date.isoformat()
        except Exception as e:
            self.logger.error(f"shift操作失敗: {e}")
            return None
    
    def format(self, date_str: str, format_str: str) -> Optional[str]:
        """
        類似 moment.js 的 format 功能，用於格式化日期
        
        Args:
            date_str: 日期字符串
            format_str: 格式化字符串
            
        Returns:
            格式化後的日期字符串
        """
        if not ARROW_AVAILABLE:
            self.logger.warning("arrow庫未安裝，無法使用format功能")
            return None
            
        try:
            arrow_date = arrow.get(date_str)
            return arrow_date.format(format_str)
        except Exception as e:
            self.logger.error(f"format操作失敗: {e}")
            return None


# 創建默認實例
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


def shift_date(date_str: str, **kwargs) -> Optional[str]:
    """
    日期時間增減的便捷函數
    
    Args:
        date_str: 日期字符串
        **kwargs: 要增減的時間參數
        
    Returns:
        計算後的日期字符串
    """
    return default_parser.shift(date_str, **kwargs)


def format_date(date_str: str, format_str: str) -> Optional[str]:
    """
    格式化日期的便捷函數
    
    Args:
        date_str: 日期字符串
        format_str: 格式化字符串
        
    Returns:
        格式化後的日期字符串
    """
    return default_parser.format(date_str, format_str)
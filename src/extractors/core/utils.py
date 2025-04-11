"""
提取器工具模組

此模組提供各種數據處理和轉換的工具類。
"""

from dataclasses import dataclass
from typing import Optional, Any, Dict, List, Union, Callable

# 配置類
@dataclass
class TextCleanerConfig:
    """文本清理配置"""
    remove_spaces: bool = True
    remove_newlines: bool = True
    remove_tabs: bool = True
    normalize_unicode: bool = True
    
@dataclass
class HTMLCleanerConfig:
    """HTML清理配置"""
    remove_scripts: bool = True
    remove_styles: bool = True
    remove_comments: bool = True
    remove_tags: List[str] = None
    
@dataclass
class URLNormalizerConfig:
    """URL規範化配置"""
    remove_fragments: bool = True
    remove_query: bool = False
    make_absolute: bool = True
    base_url: Optional[str] = None
    
@dataclass
class DateParserConfig:
    """日期解析配置"""
    format: str = "%Y-%m-%d"
    locale: str = "zh_TW"
    timezone: str = "Asia/Taipei"
    
@dataclass
class NumberParserConfig:
    """數字解析配置"""
    decimal_separator: str = "."
    thousands_separator: str = ","
    remove_currency: bool = True

# 工具類
class TextCleaner:
    """文本清理工具"""
    def __init__(self, config: TextCleanerConfig = None):
        self.config = config or TextCleanerConfig()
        
    def clean(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        result = text
        if self.config.remove_spaces:
            result = " ".join(result.split())
        if self.config.remove_newlines:
            result = result.replace("\n", " ")
        if self.config.remove_tabs:
            result = result.replace("\t", " ")
        if self.config.normalize_unicode:
            import unicodedata
            result = unicodedata.normalize("NFKC", result)
        return result.strip()

class HTMLCleaner:
    """HTML清理工具"""
    def __init__(self, config: HTMLCleanerConfig = None):
        self.config = config or HTMLCleanerConfig()
        
    def clean(self, html: str) -> str:
        """清理HTML"""
        from bs4 import BeautifulSoup
        if not html:
            return ""
        soup = BeautifulSoup(html, "lxml")
        if self.config.remove_scripts:
            for script in soup.find_all("script"):
                script.decompose()
        if self.config.remove_styles:
            for style in soup.find_all("style"):
                style.decompose()
        if self.config.remove_comments:
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
        if self.config.remove_tags:
            for tag in self.config.remove_tags:
                for element in soup.find_all(tag):
                    element.decompose()
        return str(soup)

class URLNormalizer:
    """URL規範化工具"""
    def __init__(self, config: URLNormalizerConfig = None):
        self.config = config or URLNormalizerConfig()
        
    def normalize(self, url: str) -> str:
        """規範化URL"""
        from urllib.parse import urlparse, urlunparse, urljoin
        if not url:
            return ""
        parsed = urlparse(url)
        if self.config.remove_fragments:
            parsed = parsed._replace(fragment="")
        if self.config.remove_query:
            parsed = parsed._replace(query="")
        result = urlunparse(parsed)
        if self.config.make_absolute and self.config.base_url:
            result = urljoin(self.config.base_url, result)
        return result

class DateParser:
    """日期解析工具"""
    def __init__(self, config: DateParserConfig = None):
        self.config = config or DateParserConfig()
        
    def parse(self, date_str: str) -> datetime:
        """解析日期字符串"""
        import datetime
        import locale
        if not date_str:
            return None
        try:
            locale.setlocale(locale.LC_TIME, self.config.locale)
            return datetime.datetime.strptime(date_str, self.config.format)
        except (ValueError, locale.Error):
            return None

class NumberParser:
    """數字解析工具"""
    def __init__(self, config: NumberParserConfig = None):
        self.config = config or NumberParserConfig()
        
    def parse(self, number_str: str) -> Union[int, float, None]:
        """解析數字字符串"""
        if not number_str:
            return None
        try:
            # 移除貨幣符號
            if self.config.remove_currency:
                number_str = re.sub(r'[$¥€£]', '', number_str)
            # 替換分隔符
            number_str = number_str.replace(
                self.config.thousands_separator, 
                ""
            ).replace(
                self.config.decimal_separator, 
                "."
            )
            # 轉換為數字
            number = float(number_str)
            return int(number) if number.is_integer() else number
        except ValueError:
            return None

# 工具類工廠函數
def create_text_cleaner(**kwargs) -> TextCleaner:
    """創建文本清理器"""
    config = TextCleanerConfig(**kwargs)
    return TextCleaner(config)

def create_html_cleaner(**kwargs) -> HTMLCleaner:
    """創建HTML清理器"""
    config = HTMLCleanerConfig(**kwargs)
    return HTMLCleaner(config)

def create_url_normalizer(**kwargs) -> URLNormalizer:
    """創建URL規範化器"""
    config = URLNormalizerConfig(**kwargs)
    return URLNormalizer(config)

def create_date_parser(**kwargs) -> DateParser:
    """創建日期解析器"""
    config = DateParserConfig(**kwargs)
    return DateParser(config)

def create_number_parser(**kwargs) -> NumberParser:
    """創建數字解析器"""
    config = NumberParserConfig(**kwargs)
    return NumberParser(config)

__all__ = [
    # 配置類
    'TextCleanerConfig',
    'HTMLCleanerConfig',
    'URLNormalizerConfig',
    'DateParserConfig',
    'NumberParserConfig',
    
    # 工具類
    'TextCleaner',
    'HTMLCleaner',
    'URLNormalizer',
    'DateParser',
    'NumberParser',
    
    # 工廠函數
    'create_text_cleaner',
    'create_html_cleaner',
    'create_url_normalizer',
    'create_date_parser',
    'create_number_parser'
] 
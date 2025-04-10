"""
URL 工具模組
提供 URL 處理、編碼和解析功能
"""

from typing import Dict, Optional
from urllib.parse import urlparse, urljoin, quote, unquote, parse_qs, urlencode
import re

class URLUtils:
    """URL 工具類"""
    
    @staticmethod
    def normalize_url(url: str, base_domain: str) -> str:
        """
        標準化 URL
        
        Args:
            url: 原始 URL
            base_domain: 基礎域名
            
        Returns:
            標準化的 URL
        """
        if not url:
            return ""
            
        # 移除空白字符
        url = url.strip()
        
        # 如果是相對路徑，添加基礎域名
        if not url.startswith(('http://', 'https://')):
            url = urljoin(f"https://{base_domain}", url)
            
        # 解析 URL
        parsed = urlparse(url)
        
        # 重建 URL，確保使用正確的協議和域名
        normalized = f"{parsed.scheme}://{base_domain}{parsed.path}"
        
        # 添加查詢參數
        if parsed.query:
            normalized += f"?{parsed.query}"
            
        # 添加片段
        if parsed.fragment:
            normalized += f"#{parsed.fragment}"
            
        return normalized
        
    @staticmethod
    def encode_url_parameter(param: str) -> str:
        """
        編碼 URL 參數
        
        Args:
            param: 原始參數
            
        Returns:
            編碼後的參數
        """
        # 保留特殊字符的編碼
        return quote(param, safe='')
        
    @staticmethod
    def decode_url_parameter(param: str) -> str:
        """
        解碼 URL 參數
        
        Args:
            param: 編碼後的參數
            
        Returns:
            解碼後的參數
        """
        return unquote(param)
        
    @staticmethod
    def parse_query_params(url: str) -> Dict[str, list]:
        """
        解析 URL 查詢參數
        
        Args:
            url: URL 字符串
            
        Returns:
            查詢參數字典
        """
        parsed = urlparse(url)
        return parse_qs(parsed.query)
        
    @staticmethod
    def build_query_string(params: Dict[str, str]) -> str:
        """
        構建查詢字符串
        
        Args:
            params: 參數字典
            
        Returns:
            查詢字符串
        """
        return urlencode(params)
        
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        檢查 URL 是否有效
        
        Args:
            url: URL 字符串
            
        Returns:
            是否有效
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
            
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """
        提取域名
        
        Args:
            url: URL 字符串
            
        Returns:
            域名
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return None
            
    @staticmethod
    def clean_url(url: str) -> str:
        """
        清理 URL
        
        Args:
            url: URL 字符串
            
        Returns:
            清理後的 URL
        """
        # 移除多餘的斜杠
        url = re.sub(r'([^:])//+', r'\1/', url)
        
        # 移除末尾的斜杠
        url = url.rstrip('/')
        
        return url 
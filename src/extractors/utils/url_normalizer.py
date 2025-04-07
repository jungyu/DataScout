#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
URL標準化工具模組

提供處理和標準化URL的工具類和函數
"""

import re
import logging
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs, urlencode
from typing import Optional, Dict, Set, List


class URLNormalizer:
    """URL標準化工具類"""
    
    def __init__(self):
        """初始化URL標準化器"""
        self.logger = logging.getLogger(__name__)
        self.visited_urls: Set[str] = set()  # 用於跟踪已訪問的URL
    
    def normalize_url(self, url: str, base_url: Optional[str] = None) -> str:
        """
        標準化URL，處理相對路徑和協議缺失的URL
        
        Args:
            url: 原始URL
            base_url: 基礎URL，用於處理相對路徑
            
        Returns:
            標準化後的URL
        """
        if not url:
            return ""
        
        try:
            # 處理協議相對URL
            if url.startswith('//'):
                return f"https:{url}"
                
            # 處理絕對路徑但缺少域名的URL
            if url.startswith('/') and base_url:
                # 從base_url提取域名部分
                parsed_base = urlparse(base_url)
                domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
                return f"{domain}{url}"
                
            # 處理相對路徑
            if not url.startswith(('http://', 'https://')) and base_url:
                return urljoin(base_url, url)
                
            # 已經是絕對URL
            return url
        except Exception as e:
            self.logger.warning(f"URL標準化失敗: {e}")
            return url
    
    def track_url(self, url: str) -> None:
        """
        跟踪已訪問的URL
        
        Args:
            url: 要跟踪的URL
        """
        self.visited_urls.add(url)
    
    def is_visited(self, url: str) -> bool:
        """
        檢查URL是否已訪問
        
        Args:
            url: 要檢查的URL
            
        Returns:
            是否已訪問
        """
        return url in self.visited_urls
    
    def clear_visited(self) -> None:
        """清空已訪問URL集合"""
        self.visited_urls.clear()
    
    def get_visited_count(self) -> int:
        """
        獲取已訪問URL的數量
        
        Returns:
            已訪問URL數量
        """
        return len(self.visited_urls)
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """
        從URL中提取域名
        
        Args:
            url: 完整URL
            
        Returns:
            域名部分
        """
        if not url:
            return ""
            
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return ""
    
    @staticmethod
    def extract_path(url: str) -> str:
        """
        從URL中提取路徑
        
        Args:
            url: 完整URL
            
        Returns:
            路徑部分
        """
        if not url:
            return ""
            
        try:
            parsed = urlparse(url)
            return parsed.path
        except Exception:
            return ""
    
    @staticmethod
    def extract_query_params(url: str) -> Dict[str, List[str]]:
        """
        從URL中提取查詢參數
        
        Args:
            url: 完整URL
            
        Returns:
            查詢參數字典
        """
        if not url:
            return {}
            
        try:
            parsed = urlparse(url)
            return parse_qs(parsed.query)
        except Exception:
            return {}
    
    @staticmethod
    def build_url(base: str, path: str = "", params: Optional[Dict[str, str]] = None) -> str:
        """
        構建URL
        
        Args:
            base: 基礎URL
            path: 路徑
            params: 查詢參數
            
        Returns:
            構建的URL
        """
        if not base:
            return ""
            
        try:
            # 解析基礎URL
            parsed = urlparse(base)
            
            # 處理路徑
            if path:
                if not path.startswith('/'):
                    path = '/' + path
                new_path = path
            else:
                new_path = parsed.path
            
            # 處理查詢參數
            if params:
                query = urlencode(params)
            else:
                query = parsed.query
            
            # 重建URL
            return urlunparse((
                parsed.scheme,
                parsed.netloc,
                new_path,
                parsed.params,
                query,
                parsed.fragment
            ))
        except Exception:
            return base
    
    @staticmethod
    def add_query_params(url: str, params: Dict[str, str]) -> str:
        """
        向URL添加查詢參數
        
        Args:
            url: 原始URL
            params: 要添加的查詢參數
            
        Returns:
            添加參數後的URL
        """
        if not url:
            return ""
            
        try:
            # 解析URL
            parsed = urlparse(url)
            
            # 解析現有查詢參數
            query_params = parse_qs(parsed.query)
            
            # 添加新參數
            for key, value in params.items():
                query_params[key] = [value]
            
            # 編碼查詢參數
            new_query = urlencode(query_params, doseq=True)
            
            # 重建URL
            return urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
        except Exception:
            return url
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        檢查URL是否有效
        
        Args:
            url: 要檢查的URL
            
        Returns:
            URL是否有效
        """
        if not url:
            return False
            
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def remove_fragments(url: str) -> str:
        """
        移除URL中的片段標識符
        
        Args:
            url: 原始URL
            
        Returns:
            處理後的URL
        """
        if not url:
            return ""
            
        try:
            parsed = urlparse(url)
            return urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                ''  # 清空片段
            ))
        except Exception:
            return url


# 單例模式，提供一個全局實例
default_normalizer = URLNormalizer()


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """
    標準化URL的便捷函數
    
    Args:
        url: 原始URL
        base_url: 基礎URL
        
    Returns:
        標準化後的URL
    """
    return default_normalizer.normalize_url(url, base_url)


def extract_domain(url: str) -> str:
    """
    提取域名的便捷函數
    
    Args:
        url: 原始URL
        
    Returns:
        域名
    """
    return URLNormalizer.extract_domain(url)


def is_valid_url(url: str) -> bool:
    """
    檢查URL是否有效的便捷函數
    
    Args:
        url: 要檢查的URL
        
    Returns:
        URL是否有效
    """
    return URLNormalizer.is_valid_url(url)


def build_url(base: str, path: str = "", params: Optional[Dict[str, str]] = None) -> str:
    """
    構建URL的便捷函數
    
    Args:
        base: 基礎URL
        path: 路徑
        params: 查詢參數
        
    Returns:
        構建的URL
    """
    return URLNormalizer.build_url(base, path, params)
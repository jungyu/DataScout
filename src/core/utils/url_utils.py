"""
URL 工具模組

提供 URL 處理、編碼、解析和標準化功能。
支持 URL 參數的編碼和解碼，以及 URL 的驗證和清理。
"""

import re
import logging
from typing import Dict, Optional, Union, List, Tuple
from urllib.parse import urlparse, urljoin, quote, unquote, parse_qs, urlencode, urlunparse

class URLUtils:
    """URL 工具類"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化 URL 工具類
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # URL 安全檢查相關
        self.unsafe_protocols = {'javascript:', 'data:', 'vbscript:', 'file:'}
        self.unsafe_chars = {'<', '>', '"', "'", ';', '\\', '{', '}', '|', '^', '~', '`'}
        
    def normalize_url(self, url: str, base_url: Optional[str] = None, base_domain: Optional[str] = None) -> str:
        """
        標準化 URL
        
        Args:
            url: 原始 URL
            base_url: 基礎 URL，用於處理相對路徑
            base_domain: 基礎域名，用於強制使用特定域名
            
        Returns:
            標準化的 URL
        """
        if not url:
            return ""
            
        try:
            # 移除空白字符
            url = url.strip()
            
            # 如果是相對路徑，添加基礎 URL
            if not url.startswith(('http://', 'https://')):
                if base_url:
                    url = urljoin(base_url, url)
                elif base_domain:
                    url = urljoin(f"https://{base_domain}", url)
                    
            # 解析 URL
            parsed = urlparse(url)
            
            # 重建 URL
            if base_domain:
                normalized = f"{parsed.scheme}://{base_domain}{parsed.path}"
            else:
                normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                
            # 添加查詢參數
            if parsed.query:
                normalized += f"?{parsed.query}"
                
            # 添加片段
            if parsed.fragment:
                normalized += f"#{parsed.fragment}"
                
            return normalized
            
        except Exception as e:
            self.logger.error(f"標準化 URL 失敗: {str(e)}")
            return url
            
    def encode_url_parameter(self, param: str) -> str:
        """
        編碼 URL 參數
        
        Args:
            param: 原始參數
            
        Returns:
            編碼後的參數
        """
        try:
            return quote(param, safe='')
        except Exception as e:
            self.logger.error(f"編碼 URL 參數失敗: {str(e)}")
            return param
            
    def decode_url_parameter(self, param: str) -> str:
        """
        解碼 URL 參數
        
        Args:
            param: 編碼後的參數
            
        Returns:
            解碼後的參數
        """
        try:
            return unquote(param)
        except Exception as e:
            self.logger.error(f"解碼 URL 參數失敗: {str(e)}")
            return param
            
    def parse_query_params(self, url: str) -> Dict[str, List[str]]:
        """
        解析 URL 查詢參數
        
        Args:
            url: URL 字符串
            
        Returns:
            查詢參數字典
        """
        try:
            parsed = urlparse(url)
            return parse_qs(parsed.query)
        except Exception as e:
            self.logger.error(f"解析查詢參數失敗: {str(e)}")
            return {}
            
    def build_query_string(self, params: Dict[str, Union[str, int, float, bool]]) -> str:
        """
        構建查詢字符串
        
        Args:
            params: 參數字典
            
        Returns:
            查詢字符串
        """
        try:
            # 將所有值轉換為字符串
            str_params = {k: str(v) for k, v in params.items()}
            return urlencode(str_params)
        except Exception as e:
            self.logger.error(f"構建查詢字符串失敗: {str(e)}")
            return ""
            
    def is_valid_url(self, url: str) -> bool:
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
        except Exception as e:
            self.logger.error(f"檢查 URL 有效性失敗: {str(e)}")
            return False
            
    def extract_domain(self, url: str) -> Optional[str]:
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
        except Exception as e:
            self.logger.error(f"提取域名失敗: {str(e)}")
            return None
            
    def clean_url(self, url: str) -> str:
        """
        清理 URL
        
        Args:
            url: URL 字符串
            
        Returns:
            清理後的 URL
        """
        try:
            # 移除多餘的斜杠
            url = re.sub(r'([^:])//+', r'\1/', url)
            
            # 移除末尾的斜杠
            url = url.rstrip('/')
            
            # 解析 URL
            parsed = urlparse(url)
            
            # 重建基本 URL
            cleaned = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            # 如果有查詢參數，添加回去
            if parsed.query:
                cleaned += f"?{parsed.query}"
                
            return cleaned
            
        except Exception as e:
            self.logger.error(f"清理 URL 失敗: {str(e)}")
            return url
            
    def is_safe_url(self, url: str) -> Tuple[bool, str]:
        """
        檢查 URL 是否安全
        
        Args:
            url: URL 字符串
            
        Returns:
            (是否安全, 原因)
        """
        try:
            # 檢查協議
            parsed = urlparse(url)
            if parsed.scheme.lower() in self.unsafe_protocols:
                return False, f"不安全的協議: {parsed.scheme}"
                
            # 檢查特殊字符
            if any(char in url for char in self.unsafe_chars):
                return False, "URL 包含不安全的字符"
                
            # 檢查域名
            if not parsed.netloc:
                return False, "缺少域名"
                
            # 檢查路徑遍歷
            if '..' in parsed.path:
                return False, "路徑包含遍歷字符"
                
            return True, "URL 安全"
            
        except Exception as e:
            self.logger.error(f"檢查 URL 安全性失敗: {str(e)}")
            return False, f"檢查失敗: {str(e)}"
            
    def handle_redirect(self, url: str, max_redirects: int = 5) -> Tuple[str, List[str]]:
        """
        處理 URL 重定向
        
        Args:
            url: 原始 URL
            max_redirects: 最大重定向次數
            
        Returns:
            (最終 URL, 重定向鏈)
        """
        try:
            import requests
            
            redirect_chain = []
            current_url = url
            
            for _ in range(max_redirects):
                response = requests.head(current_url, allow_redirects=False)
                
                if response.status_code in (301, 302, 303, 307, 308):
                    redirect_url = response.headers.get('Location')
                    if not redirect_url:
                        break
                        
                    redirect_chain.append(redirect_url)
                    current_url = redirect_url
                else:
                    break
                    
            return current_url, redirect_chain
            
        except Exception as e:
            self.logger.error(f"處理重定向失敗: {str(e)}")
            return url, []
            
    def validate_query_params(self, url: str, required_params: List[str], optional_params: List[str] = None) -> Tuple[bool, str]:
        """
        驗證 URL 查詢參數
        
        Args:
            url: URL 字符串
            required_params: 必需的參數列表
            optional_params: 可選的參數列表
            
        Returns:
            (是否有效, 原因)
        """
        try:
            params = self.parse_query_params(url)
            
            # 檢查必需參數
            missing_params = [param for param in required_params if param not in params]
            if missing_params:
                return False, f"缺少必需參數: {', '.join(missing_params)}"
                
            # 檢查可選參數
            if optional_params:
                invalid_params = [param for param in params if param not in required_params + optional_params]
                if invalid_params:
                    return False, f"無效的參數: {', '.join(invalid_params)}"
                    
            return True, "參數有效"
            
        except Exception as e:
            self.logger.error(f"驗證查詢參數失敗: {str(e)}")
            return False, f"驗證失敗: {str(e)}"
            
    def join_path(self, *paths: str) -> str:
        """
        連接 URL 路徑
        
        Args:
            *paths: 路徑片段
            
        Returns:
            連接後的路徑
        """
        try:
            # 移除每個路徑片段的首尾斜杠
            cleaned_paths = [path.strip('/') for path in paths]
            
            # 過濾掉空路徑
            cleaned_paths = [path for path in cleaned_paths if path]
            
            # 連接路徑
            return '/'.join(cleaned_paths)
            
        except Exception as e:
            self.logger.error(f"連接路徑失敗: {str(e)}")
            return '/'.join(paths)
            
    def get_path_segments(self, url: str) -> List[str]:
        """
        獲取 URL 路徑片段
        
        Args:
            url: URL 字符串
            
        Returns:
            路徑片段列表
        """
        try:
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            return [segment for segment in path.split('/') if segment]
        except Exception as e:
            self.logger.error(f"獲取路徑片段失敗: {str(e)}")
            return []
            
    def get_file_extension(self, url: str) -> Optional[str]:
        """
        獲取 URL 文件擴展名
        
        Args:
            url: URL 字符串
            
        Returns:
            文件擴展名
        """
        try:
            parsed = urlparse(url)
            path = parsed.path
            
            # 從路徑中提取文件名
            filename = path.split('/')[-1]
            
            # 從文件名中提取擴展名
            if '.' in filename:
                return filename.split('.')[-1].lower()
            return None
            
        except Exception as e:
            self.logger.error(f"獲取文件擴展名失敗: {str(e)}")
            return None
            
    def is_same_domain(self, url1: str, url2: str) -> bool:
        """
        檢查兩個 URL 是否屬於同一域名
        
        Args:
            url1: 第一個 URL
            url2: 第二個 URL
            
        Returns:
            是否屬於同一域名
        """
        try:
            domain1 = self.extract_domain(url1)
            domain2 = self.extract_domain(url2)
            
            if not domain1 or not domain2:
                return False
                
            return domain1.lower() == domain2.lower()
            
        except Exception as e:
            self.logger.error(f"檢查域名是否相同失敗: {str(e)}")
            return False
            
    def get_url_depth(self, url: str) -> int:
        """
        獲取 URL 深度
        
        Args:
            url: URL 字符串
            
        Returns:
            URL 深度（路徑層級數）
        """
        try:
            segments = self.get_path_segments(url)
            return len(segments)
        except Exception as e:
            self.logger.error(f"獲取 URL 深度失敗: {str(e)}")
            return 0 
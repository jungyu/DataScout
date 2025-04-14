"""
請求控制模組

提供請求發送、重試、速率限制等功能
"""

import time
import random
from typing import Dict, List, Optional, Union, Any, Callable
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from selenium_base.core.exceptions import RequestError, RateLimitError, TimeoutError, NetworkError
from selenium_base.core.logger import Logger

class Request:
    """請求控制類別"""
    
    def __init__(self, config: Dict):
        """
        初始化請求控制類別
        
        Args:
            config: 配置字典，包含以下欄位：
                - retry_count: 重試次數
                - retry_delay: 重試延遲（秒）
                - timeout: 請求超時（秒）
                - rate_limit: 速率限制（請求/秒）
                - rate_limit_burst: 突發請求數
                - proxy: 代理設定
                - headers: 請求標頭
                - cookies: 請求 Cookie
                - verify: 是否驗證 SSL 證書
                - allow_redirects: 是否允許重定向
                - max_redirects: 最大重定向次數
        """
        self.config = config
        self.logger = Logger('request')
        self.session = self._create_session()
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_reset_time = 0
    
    def _create_session(self) -> requests.Session:
        """
        建立請求會話
        
        Returns:
            requests.Session: 請求會話物件
        """
        session = requests.Session()
        
        # 設定重試策略
        retry_strategy = Retry(
            total=self.config.get('retry_count', 3),
            backoff_factor=self.config.get('retry_delay', 1),
            status_forcelist=[500, 502, 503, 504]
        )
        
        # 設定適配器
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # 設定代理
        if 'proxy' in self.config:
            session.proxies = self.config['proxy']
        
        # 設定標頭
        if 'headers' in self.config:
            session.headers.update(self.config['headers'])
        
        # 設定 Cookie
        if 'cookies' in self.config:
            session.cookies.update(self.config['cookies'])
        
        return session
    
    def _check_rate_limit(self):
        """
        檢查速率限制
        
        Raises:
            RateLimitError: 超過速率限制時拋出
        """
        current_time = time.time()
        
        # 檢查是否需要重置計數器
        if current_time >= self.rate_limit_reset_time:
            self.request_count = 0
            self.rate_limit_reset_time = current_time + 1
        
        # 檢查是否超過速率限制
        if self.request_count >= self.config.get('rate_limit', 0):
            sleep_time = self.rate_limit_reset_time - current_time
            if sleep_time > 0:
                self.logger.warning(f'達到速率限制，等待 {sleep_time:.2f} 秒')
                time.sleep(sleep_time)
                self.request_count = 0
                self.rate_limit_reset_time = time.time() + 1
        
        # 檢查是否超過突發請求數
        if self.request_count >= self.config.get('rate_limit_burst', 0):
            raise RateLimitError('超過突發請求數限制')
        
        # 更新請求計數
        self.request_count += 1
    
    def _handle_response(self, response: requests.Response) -> Dict:
        """
        處理回應
        
        Args:
            response: 請求回應
            
        Returns:
            Dict: 處理後的回應資料
            
        Raises:
            RequestError: 請求失敗時拋出
            TimeoutError: 請求超時時拋出
            NetworkError: 網路錯誤時拋出
        """
        try:
            response.raise_for_status()
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'cookies': dict(response.cookies),
                'content': response.content,
                'text': response.text,
                'json': response.json() if 'application/json' in response.headers.get('Content-Type', '') else None
            }
        except requests.exceptions.HTTPError as e:
            raise RequestError(f'HTTP 錯誤: {str(e)}')
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f'網路連接錯誤: {str(e)}')
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f'請求超時: {str(e)}')
        except requests.exceptions.RequestException as e:
            raise RequestError(f'請求錯誤: {str(e)}')
    
    def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> Dict:
        """
        發送 GET 請求
        
        Args:
            url: 請求 URL
            params: URL 參數
            **kwargs: 其他請求參數
            
        Returns:
            Dict: 回應資料
        """
        self._check_rate_limit()
        self.logger.info(f'發送 GET 請求: {url}')
        
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.config.get('timeout', 30),
                verify=self.config.get('verify', True),
                allow_redirects=self.config.get('allow_redirects', True),
                **kwargs
            )
            return self._handle_response(response)
        except Exception as e:
            self.logger.error(f'GET 請求失敗: {str(e)}')
            raise
    
    def post(self, url: str, data: Optional[Union[Dict, str]] = None, json: Optional[Dict] = None, **kwargs) -> Dict:
        """
        發送 POST 請求
        
        Args:
            url: 請求 URL
            data: 表單資料
            json: JSON 資料
            **kwargs: 其他請求參數
            
        Returns:
            Dict: 回應資料
        """
        self._check_rate_limit()
        self.logger.info(f'發送 POST 請求: {url}')
        
        try:
            response = self.session.post(
                url,
                data=data,
                json=json,
                timeout=self.config.get('timeout', 30),
                verify=self.config.get('verify', True),
                allow_redirects=self.config.get('allow_redirects', True),
                **kwargs
            )
            return self._handle_response(response)
        except Exception as e:
            self.logger.error(f'POST 請求失敗: {str(e)}')
            raise
    
    def put(self, url: str, data: Optional[Union[Dict, str]] = None, **kwargs) -> Dict:
        """
        發送 PUT 請求
        
        Args:
            url: 請求 URL
            data: 請求資料
            **kwargs: 其他請求參數
            
        Returns:
            Dict: 回應資料
        """
        self._check_rate_limit()
        self.logger.info(f'發送 PUT 請求: {url}')
        
        try:
            response = self.session.put(
                url,
                data=data,
                timeout=self.config.get('timeout', 30),
                verify=self.config.get('verify', True),
                allow_redirects=self.config.get('allow_redirects', True),
                **kwargs
            )
            return self._handle_response(response)
        except Exception as e:
            self.logger.error(f'PUT 請求失敗: {str(e)}')
            raise
    
    def delete(self, url: str, **kwargs) -> Dict:
        """
        發送 DELETE 請求
        
        Args:
            url: 請求 URL
            **kwargs: 其他請求參數
            
        Returns:
            Dict: 回應資料
        """
        self._check_rate_limit()
        self.logger.info(f'發送 DELETE 請求: {url}')
        
        try:
            response = self.session.delete(
                url,
                timeout=self.config.get('timeout', 30),
                verify=self.config.get('verify', True),
                allow_redirects=self.config.get('allow_redirects', True),
                **kwargs
            )
            return self._handle_response(response)
        except Exception as e:
            self.logger.error(f'DELETE 請求失敗: {str(e)}')
            raise
    
    def request(self, method: str, url: str, **kwargs) -> Dict:
        """
        發送自定義請求
        
        Args:
            method: 請求方法
            url: 請求 URL
            **kwargs: 其他請求參數
            
        Returns:
            Dict: 回應資料
        """
        self._check_rate_limit()
        self.logger.info(f'發送 {method} 請求: {url}')
        
        try:
            response = self.session.request(
                method,
                url,
                timeout=self.config.get('timeout', 30),
                verify=self.config.get('verify', True),
                allow_redirects=self.config.get('allow_redirects', True),
                **kwargs
            )
            return self._handle_response(response)
        except Exception as e:
            self.logger.error(f'{method} 請求失敗: {str(e)}')
            raise
    
    def download(self, url: str, file_path: str, chunk_size: int = 8192) -> None:
        """
        下載檔案
        
        Args:
            url: 檔案 URL
            file_path: 儲存路徑
            chunk_size: 區塊大小
            
        Raises:
            RequestError: 下載失敗時拋出
        """
        self._check_rate_limit()
        self.logger.info(f'下載檔案: {url} -> {file_path}')
        
        try:
            response = self.session.get(
                url,
                stream=True,
                timeout=self.config.get('timeout', 30),
                verify=self.config.get('verify', True),
                allow_redirects=self.config.get('allow_redirects', True)
            )
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
        except Exception as e:
            self.logger.error(f'檔案下載失敗: {str(e)}')
            raise RequestError(f'檔案下載失敗: {str(e)}')
    
    def upload(self, url: str, file_path: str, field_name: str = 'file', **kwargs) -> Dict:
        """
        上傳檔案
        
        Args:
            url: 上傳 URL
            file_path: 檔案路徑
            field_name: 欄位名稱
            **kwargs: 其他請求參數
            
        Returns:
            Dict: 回應資料
            
        Raises:
            RequestError: 上傳失敗時拋出
        """
        self._check_rate_limit()
        self.logger.info(f'上傳檔案: {file_path} -> {url}')
        
        try:
            with open(file_path, 'rb') as f:
                files = {field_name: f}
                response = self.session.post(
                    url,
                    files=files,
                    timeout=self.config.get('timeout', 30),
                    verify=self.config.get('verify', True),
                    allow_redirects=self.config.get('allow_redirects', True),
                    **kwargs
                )
                return self._handle_response(response)
        except Exception as e:
            self.logger.error(f'檔案上傳失敗: {str(e)}')
            raise RequestError(f'檔案上傳失敗: {str(e)}')
    
    def set_proxy(self, proxy: Dict[str, str]) -> None:
        """
        設定代理
        
        Args:
            proxy: 代理設定，格式為 {'http': 'http://host:port', 'https': 'https://host:port'}
        """
        self.session.proxies = proxy
        self.config['proxy'] = proxy
    
    def set_headers(self, headers: Dict[str, str]) -> None:
        """
        設定請求標頭
        
        Args:
            headers: 請求標頭
        """
        self.session.headers.update(headers)
        self.config['headers'] = headers
    
    def set_cookies(self, cookies: Dict[str, str]) -> None:
        """
        設定 Cookie
        
        Args:
            cookies: Cookie 設定
        """
        self.session.cookies.update(cookies)
        self.config['cookies'] = cookies
    
    def clear_cookies(self) -> None:
        """清除所有 Cookie"""
        self.session.cookies.clear()
        self.config['cookies'] = {}
    
    def close(self) -> None:
        """關閉請求會話"""
        self.session.close() 
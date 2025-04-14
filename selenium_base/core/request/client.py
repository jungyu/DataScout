"""
請求客戶端類別

提供網路請求發送和重試機制，整合到 selenium_base 架構中
"""

import time
import random
from typing import Dict, Optional, Union, Any, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from selenium_base.core.exceptions import RequestError
from selenium_base.core.logger import Logger
from .rate import RateLimiter

class RequestClient:
    """請求客戶端類別"""
    
    def __init__(self, config: Dict):
        """
        初始化請求客戶端
        
        Args:
            config: 配置字典，包含以下欄位：
                - timeout: 請求超時時間
                - retry: 重試配置
                    - total: 最大重試次數
                    - backoff_factor: 重試間隔係數
                    - status_forcelist: 需要重試的HTTP狀態碼
                - proxy: 代理設定
                - headers: 請求標頭
                - cookies: Cookie設定
                - verify: 是否驗證SSL證書
                - rate_limit: 速率限制配置
                    - max_requests: 時間窗口內最大請求數
                    - time_window: 時間窗口大小（秒）
                - browser: 瀏覽器配置（可選）
                    - user_agent: 瀏覽器標識
                    - language: 瀏覽器語言
                    - platform: 瀏覽器平台
                - anti_detection: 反檢測配置（可選）
                    - random_delay: 隨機延遲範圍
                    - rotate_user_agent: 是否輪換User-Agent
                    - rotate_proxy: 是否輪換代理
                    - user_agents: User-Agent列表
                    - proxies: 代理列表
        """
        self.config = config
        self.logger = Logger('request_client')
        self.session = self._create_session()
        self.rate_limiter = RateLimiter(
            max_requests=config.get('rate_limit', {}).get('max_requests', 0),
            time_window=config.get('rate_limit', {}).get('time_window', 0)
        )
        self._setup_browser_config()
        self._setup_anti_detection()
    
    def _create_session(self) -> requests.Session:
        """
        建立請求會話
        
        Returns:
            requests.Session: 請求會話物件
        """
        session = requests.Session()
        
        # 設定重試機制
        retry_config = self.config.get('retry', {})
        retry = Retry(
            total=retry_config.get('total', 3),
            backoff_factor=retry_config.get('backoff_factor', 0.5),
            status_forcelist=retry_config.get('status_forcelist', [500, 502, 503, 504])
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # 設定代理
        if 'proxy' in self.config:
            session.proxies = self.config['proxy']
        
        # 設定請求標頭
        if 'headers' in self.config:
            session.headers.update(self.config['headers'])
        
        # 設定Cookie
        if 'cookies' in self.config:
            session.cookies.update(self.config['cookies'])
        
        return session
    
    def _setup_browser_config(self) -> None:
        """設置瀏覽器配置"""
        browser_config = self.config.get('browser', {})
        if browser_config:
            headers = self.session.headers
            
            # 設置User-Agent
            if 'user_agent' in browser_config:
                headers['User-Agent'] = browser_config['user_agent']
            
            # 設置語言
            if 'language' in browser_config:
                headers['Accept-Language'] = browser_config['language']
            
            # 設置平台
            if 'platform' in browser_config:
                headers['Sec-Ch-Ua-Platform'] = browser_config['platform']
    
    def _setup_anti_detection(self) -> None:
        """設置反檢測配置"""
        anti_detection = self.config.get('anti_detection', {})
        if anti_detection:
            # 設置隨機延遲
            if 'random_delay' in anti_detection:
                self.random_delay = anti_detection['random_delay']
            else:
                self.random_delay = None
            
            # 設置User-Agent輪換
            if anti_detection.get('rotate_user_agent', False):
                self._setup_user_agent_rotation(anti_detection.get('user_agents', []))
            
            # 設置代理輪換
            if anti_detection.get('rotate_proxy', False):
                self._setup_proxy_rotation(anti_detection.get('proxies', []))
    
    def _setup_user_agent_rotation(self, user_agents: List[str]) -> None:
        """
        設置User-Agent輪換
        
        Args:
            user_agents: User-Agent列表
        """
        if not user_agents:
            self.logger.warning("未提供User-Agent列表，無法啟用輪換")
            return
        
        self.user_agents = user_agents
        self.current_user_agent_index = 0
        self.logger.info(f"已啟用User-Agent輪換，共 {len(user_agents)} 個")
    
    def _setup_proxy_rotation(self, proxies: List[Dict[str, str]]) -> None:
        """
        設置代理輪換
        
        Args:
            proxies: 代理列表，格式為 [{"http": "http://...", "https": "https://..."}]
        """
        if not proxies:
            self.logger.warning("未提供代理列表，無法啟用輪換")
            return
        
        self.proxies = proxies
        self.current_proxy_index = 0
        self.logger.info(f"已啟用代理輪換，共 {len(proxies)} 個")
    
    def _rotate_user_agent(self) -> None:
        """輪換User-Agent"""
        if hasattr(self, 'user_agents'):
            self.current_user_agent_index = (self.current_user_agent_index + 1) % len(self.user_agents)
            self.session.headers['User-Agent'] = self.user_agents[self.current_user_agent_index]
            self.logger.debug(f"已輪換User-Agent: {self.user_agents[self.current_user_agent_index]}")
    
    def _rotate_proxy(self) -> None:
        """輪換代理"""
        if hasattr(self, 'proxies'):
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
            self.session.proxies = self.proxies[self.current_proxy_index]
            self.logger.debug(f"已輪換代理: {self.proxies[self.current_proxy_index]}")
    
    def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> requests.Response:
        """
        發送請求
        
        Args:
            method: 請求方法
            url: 請求URL
            **kwargs: 請求參數
            
        Returns:
            requests.Response: 請求回應物件
            
        Raises:
            RequestError: 請求失敗
        """
        try:
            # 檢查速率限制
            self.rate_limiter.wait()
            
            # 應用隨機延遲
            if self.random_delay:
                delay = random.uniform(*self.random_delay)
                time.sleep(delay)
            
            # 輪換User-Agent和代理
            if hasattr(self, 'user_agents'):
                self._rotate_user_agent()
            if hasattr(self, 'proxies'):
                self._rotate_proxy()
            
            # 設定超時時間
            kwargs['timeout'] = kwargs.get('timeout', self.config.get('timeout', 30))
            
            # 設定SSL驗證
            kwargs['verify'] = kwargs.get('verify', self.config.get('verify', True))
            
            # 發送請求
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f'請求失敗: {str(e)}')
            raise RequestError(f'請求失敗: {str(e)}')
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """
        發送GET請求
        
        Args:
            url: 請求URL
            **kwargs: 請求參數
            
        Returns:
            requests.Response: 請求回應物件
        """
        return self.request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """
        發送POST請求
        
        Args:
            url: 請求URL
            **kwargs: 請求參數
            
        Returns:
            requests.Response: 請求回應物件
        """
        return self.request('POST', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> requests.Response:
        """
        發送PUT請求
        
        Args:
            url: 請求URL
            **kwargs: 請求參數
            
        Returns:
            requests.Response: 請求回應物件
        """
        return self.request('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> requests.Response:
        """
        發送DELETE請求
        
        Args:
            url: 請求URL
            **kwargs: 請求參數
            
        Returns:
            requests.Response: 請求回應物件
        """
        return self.request('DELETE', url, **kwargs)
    
    def close(self) -> None:
        """
        關閉請求會話
        """
        self.session.close()
    
    def __enter__(self) -> 'RequestClient':
        """
        上下文管理器進入
        
        Returns:
            RequestClient: 請求客戶端物件
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        上下文管理器退出
        """
        self.close() 
"""
請求控制服務模組

此模組提供了 HTTP 請求相關的服務，包含以下功能：
- 請求控制
- 請求重試
- 請求速率限制
- 請求記錄
"""

import time
import random
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from collections import defaultdict
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from ..core.config import BaseConfig
from ..core.exceptions import RequestError
from ..utils.request import RequestController as RequestUtils

class RequestController:
    """請求控制服務類別"""
    
    def __init__(self, config: BaseConfig):
        """
        初始化請求控制服務
        
        Args:
            config: 配置物件
        """
        self.config = config
        self.logger = config.logger
        self.utils = RequestUtils(config)
        self.session = self.utils.create_session()
        self.request_records = defaultdict(list)
        
    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        verify: bool = True,
        allow_redirects: bool = True,
        proxies: Optional[Dict[str, str]] = None,
        retry: bool = True,
        retry_count: Optional[int] = None,
        retry_delay: Optional[float] = None,
        retry_backoff: Optional[float] = None,
        retry_status_forcelist: Optional[List[int]] = None
    ) -> requests.Response:
        """
        發送 GET 請求
        
        Args:
            url: 請求網址
            params: 查詢參數
            headers: 請求標頭
            cookies: 請求 Cookie
            timeout: 超時時間
            verify: 是否驗證 SSL 憑證
            allow_redirects: 是否允許重定向
            proxies: 代理伺服器
            retry: 是否重試
            retry_count: 重試次數
            retry_delay: 重試延遲
            retry_backoff: 重試退避
            retry_status_forcelist: 重試狀態碼列表
            
        Returns:
            回應物件
        """
        try:
            # 檢查速率限制
            self._check_rate_limit()
            
            # 發送請求
            response = self.session.get(
                url=url,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout or self.config.request.timeout,
                verify=verify,
                allow_redirects=allow_redirects,
                proxies=proxies
            )
            
            # 記錄請求
            self._record_request("GET", url)
            
            # 檢查回應
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GET 請求失敗: {str(e)}")
            
            # 重試請求
            if retry:
                return self._retry_request(
                    "GET",
                    url,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    timeout=timeout,
                    verify=verify,
                    allow_redirects=allow_redirects,
                    proxies=proxies,
                    retry_count=retry_count,
                    retry_delay=retry_delay,
                    retry_backoff=retry_backoff,
                    retry_status_forcelist=retry_status_forcelist
                )
                
            raise RequestError(f"GET 請求失敗: {str(e)}")
            
    def post(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        verify: bool = True,
        allow_redirects: bool = True,
        proxies: Optional[Dict[str, str]] = None,
        retry: bool = True,
        retry_count: Optional[int] = None,
        retry_delay: Optional[float] = None,
        retry_backoff: Optional[float] = None,
        retry_status_forcelist: Optional[List[int]] = None
    ) -> requests.Response:
        """
        發送 POST 請求
        
        Args:
            url: 請求網址
            data: 表單資料
            json: JSON 資料
            headers: 請求標頭
            cookies: 請求 Cookie
            timeout: 超時時間
            verify: 是否驗證 SSL 憑證
            allow_redirects: 是否允許重定向
            proxies: 代理伺服器
            retry: 是否重試
            retry_count: 重試次數
            retry_delay: 重試延遲
            retry_backoff: 重試退避
            retry_status_forcelist: 重試狀態碼列表
            
        Returns:
            回應物件
        """
        try:
            # 檢查速率限制
            self._check_rate_limit()
            
            # 發送請求
            response = self.session.post(
                url=url,
                data=data,
                json=json,
                headers=headers,
                cookies=cookies,
                timeout=timeout or self.config.request.timeout,
                verify=verify,
                allow_redirects=allow_redirects,
                proxies=proxies
            )
            
            # 記錄請求
            self._record_request("POST", url)
            
            # 檢查回應
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"POST 請求失敗: {str(e)}")
            
            # 重試請求
            if retry:
                return self._retry_request(
                    "POST",
                    url,
                    data=data,
                    json=json,
                    headers=headers,
                    cookies=cookies,
                    timeout=timeout,
                    verify=verify,
                    allow_redirects=allow_redirects,
                    proxies=proxies,
                    retry_count=retry_count,
                    retry_delay=retry_delay,
                    retry_backoff=retry_backoff,
                    retry_status_forcelist=retry_status_forcelist
                )
                
            raise RequestError(f"POST 請求失敗: {str(e)}")
            
    def put(
        this,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        verify: bool = True,
        allow_redirects: bool = True,
        proxies: Optional[Dict[str, str]] = None,
        retry: bool = True,
        retry_count: Optional[int] = None,
        retry_delay: Optional[float] = None,
        retry_backoff: Optional[float] = None,
        retry_status_forcelist: Optional[List[int]] = None
    ) -> requests.Response:
        """
        發送 PUT 請求
        
        Args:
            url: 請求網址
            data: 表單資料
            json: JSON 資料
            headers: 請求標頭
            cookies: 請求 Cookie
            timeout: 超時時間
            verify: 是否驗證 SSL 憑證
            allow_redirects: 是否允許重定向
            proxies: 代理伺服器
            retry: 是否重試
            retry_count: 重試次數
            retry_delay: 重試延遲
            retry_backoff: 重試退避
            retry_status_forcelist: 重試狀態碼列表
            
        Returns:
            回應物件
        """
        try:
            # 檢查速率限制
            this._check_rate_limit()
            
            # 發送請求
            response = this.session.put(
                url=url,
                data=data,
                json=json,
                headers=headers,
                cookies=cookies,
                timeout=timeout or this.config.request.timeout,
                verify=verify,
                allow_redirects=allow_redirects,
                proxies=proxies
            )
            
            # 記錄請求
            this._record_request("PUT", url)
            
            # 檢查回應
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.RequestException as e:
            this.logger.error(f"PUT 請求失敗: {str(e)}")
            
            # 重試請求
            if retry:
                return this._retry_request(
                    "PUT",
                    url,
                    data=data,
                    json=json,
                    headers=headers,
                    cookies=cookies,
                    timeout=timeout,
                    verify=verify,
                    allow_redirects=allow_redirects,
                    proxies=proxies,
                    retry_count=retry_count,
                    retry_delay=retry_delay,
                    retry_backoff=retry_backoff,
                    retry_status_forcelist=retry_status_forcelist
                )
                
            raise RequestError(f"PUT 請求失敗: {str(e)}")
            
    def delete(
        this,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        verify: bool = True,
        allow_redirects: bool = True,
        proxies: Optional[Dict[str, str]] = None,
        retry: bool = True,
        retry_count: Optional[int] = None,
        retry_delay: Optional[float] = None,
        retry_backoff: Optional[float] = None,
        retry_status_forcelist: Optional[List[int]] = None
    ) -> requests.Response:
        """
        發送 DELETE 請求
        
        Args:
            url: 請求網址
            params: 查詢參數
            headers: 請求標頭
            cookies: 請求 Cookie
            timeout: 超時時間
            verify: 是否驗證 SSL 憑證
            allow_redirects: 是否允許重定向
            proxies: 代理伺服器
            retry: 是否重試
            retry_count: 重試次數
            retry_delay: 重試延遲
            retry_backoff: 重試退避
            retry_status_forcelist: 重試狀態碼列表
            
        Returns:
            回應物件
        """
        try:
            # 檢查速率限制
            this._check_rate_limit()
            
            # 發送請求
            response = this.session.delete(
                url=url,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout or this.config.request.timeout,
                verify=verify,
                allow_redirects=allow_redirects,
                proxies=proxies
            )
            
            # 記錄請求
            this._record_request("DELETE", url)
            
            # 檢查回應
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.RequestException as e:
            this.logger.error(f"DELETE 請求失敗: {str(e)}")
            
            # 重試請求
            if retry:
                return this._retry_request(
                    "DELETE",
                    url,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    timeout=timeout,
                    verify=verify,
                    allow_redirects=allow_redirects,
                    proxies=proxies,
                    retry_count=retry_count,
                    retry_delay=retry_delay,
                    retry_backoff=retry_backoff,
                    retry_status_forcelist=retry_status_forcelist
                )
                
            raise RequestError(f"DELETE 請求失敗: {str(e)}")
            
    def head(
        this,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        verify: bool = True,
        allow_redirects: bool = True,
        proxies: Optional[Dict[str, str]] = None,
        retry: bool = True,
        retry_count: Optional[int] = None,
        retry_delay: Optional[float] = None,
        retry_backoff: Optional[float] = None,
        retry_status_forcelist: Optional[List[int]] = None
    ) -> requests.Response:
        """
        發送 HEAD 請求
        
        Args:
            url: 請求網址
            params: 查詢參數
            headers: 請求標頭
            cookies: 請求 Cookie
            timeout: 超時時間
            verify: 是否驗證 SSL 憑證
            allow_redirects: 是否允許重定向
            proxies: 代理伺服器
            retry: 是否重試
            retry_count: 重試次數
            retry_delay: 重試延遲
            retry_backoff: 重試退避
            retry_status_forcelist: 重試狀態碼列表
            
        Returns:
            回應物件
        """
        try:
            # 檢查速率限制
            this._check_rate_limit()
            
            # 發送請求
            response = this.session.head(
                url=url,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout or this.config.request.timeout,
                verify=verify,
                allow_redirects=allow_redirects,
                proxies=proxies
            )
            
            # 記錄請求
            this._record_request("HEAD", url)
            
            # 檢查回應
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.RequestException as e:
            this.logger.error(f"HEAD 請求失敗: {str(e)}")
            
            # 重試請求
            if retry:
                return this._retry_request(
                    "HEAD",
                    url,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    timeout=timeout,
                    verify=verify,
                    allow_redirects=allow_redirects,
                    proxies=proxies,
                    retry_count=retry_count,
                    retry_delay=retry_delay,
                    retry_backoff=retry_backoff,
                    retry_status_forcelist=retry_status_forcelist
                )
                
            raise RequestError(f"HEAD 請求失敗: {str(e)}")
            
    def options(
        this,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        verify: bool = True,
        allow_redirects: bool = True,
        proxies: Optional[Dict[str, str]] = None,
        retry: bool = True,
        retry_count: Optional[int] = None,
        retry_delay: Optional[float] = None,
        retry_backoff: Optional[float] = None,
        retry_status_forcelist: Optional[List[int]] = None
    ) -> requests.Response:
        """
        發送 OPTIONS 請求
        
        Args:
            url: 請求網址
            params: 查詢參數
            headers: 請求標頭
            cookies: 請求 Cookie
            timeout: 超時時間
            verify: 是否驗證 SSL 憑證
            allow_redirects: 是否允許重定向
            proxies: 代理伺服器
            retry: 是否重試
            retry_count: 重試次數
            retry_delay: 重試延遲
            retry_backoff: 重試退避
            retry_status_forcelist: 重試狀態碼列表
            
        Returns:
            回應物件
        """
        try:
            # 檢查速率限制
            this._check_rate_limit()
            
            # 發送請求
            response = this.session.options(
                url=url,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout or this.config.request.timeout,
                verify=verify,
                allow_redirects=allow_redirects,
                proxies=proxies
            )
            
            # 記錄請求
            this._record_request("OPTIONS", url)
            
            # 檢查回應
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.RequestException as e:
            this.logger.error(f"OPTIONS 請求失敗: {str(e)}")
            
            # 重試請求
            if retry:
                return this._retry_request(
                    "OPTIONS",
                    url,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    timeout=timeout,
                    verify=verify,
                    allow_redirects=allow_redirects,
                    proxies=proxies,
                    retry_count=retry_count,
                    retry_delay=retry_delay,
                    retry_backoff=retry_backoff,
                    retry_status_forcelist=retry_status_forcelist
                )
                
            raise RequestError(f"OPTIONS 請求失敗: {str(e)}")
            
    def patch(
        this,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        verify: bool = True,
        allow_redirects: bool = True,
        proxies: Optional[Dict[str, str]] = None,
        retry: bool = True,
        retry_count: Optional[int] = None,
        retry_delay: Optional[float] = None,
        retry_backoff: Optional[float] = None,
        retry_status_forcelist: Optional[List[int]] = None
    ) -> requests.Response:
        """
        發送 PATCH 請求
        
        Args:
            url: 請求網址
            data: 表單資料
            json: JSON 資料
            headers: 請求標頭
            cookies: 請求 Cookie
            timeout: 超時時間
            verify: 是否驗證 SSL 憑證
            allow_redirects: 是否允許重定向
            proxies: 代理伺服器
            retry: 是否重試
            retry_count: 重試次數
            retry_delay: 重試延遲
            retry_backoff: 重試退避
            retry_status_forcelist: 重試狀態碼列表
            
        Returns:
            回應物件
        """
        try:
            # 檢查速率限制
            this._check_rate_limit()
            
            # 發送請求
            response = this.session.patch(
                url=url,
                data=data,
                json=json,
                headers=headers,
                cookies=cookies,
                timeout=timeout or this.config.request.timeout,
                verify=verify,
                allow_redirects=allow_redirects,
                proxies=proxies
            )
            
            # 記錄請求
            this._record_request("PATCH", url)
            
            # 檢查回應
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.RequestException as e:
            this.logger.error(f"PATCH 請求失敗: {str(e)}")
            
            # 重試請求
            if retry:
                return this._retry_request(
                    "PATCH",
                    url,
                    data=data,
                    json=json,
                    headers=headers,
                    cookies=cookies,
                    timeout=timeout,
                    verify=verify,
                    allow_redirects=allow_redirects,
                    proxies=proxies,
                    retry_count=retry_count,
                    retry_delay=retry_delay,
                    retry_backoff=retry_backoff,
                    retry_status_forcelist=retry_status_forcelist
                )
                
            raise RequestError(f"PATCH 請求失敗: {str(e)}")
            
    def _check_rate_limit(self):
        """檢查請求速率限制"""
        try:
            # 檢查分鐘限制
            if this.config.request.rate_limit_minute:
                this._check_rate_limit_by_interval(
                    "minute",
                    this.config.request.rate_limit_minute,
                    timedelta(minutes=1)
                )
                
            # 檢查小時限制
            if this.config.request.rate_limit_hour:
                this._check_rate_limit_by_interval(
                    "hour",
                    this.config.request.rate_limit_hour,
                    timedelta(hours=1)
                )
                
            # 檢查日限制
            if this.config.request.rate_limit_day:
                this._check_rate_limit_by_interval(
                    "day",
                    this.config.request.rate_limit_day,
                    timedelta(days=1)
                )
                
        except Exception as e:
            this.logger.error(f"檢查請求速率限制失敗: {str(e)}")
            raise RequestError(f"檢查請求速率限制失敗: {str(e)}")
            
    def _check_rate_limit_by_interval(
        this,
        interval: str,
        limit: int,
        delta: timedelta
    ):
        """
        檢查指定時間區間的請求速率限制
        
        Args:
            interval: 時間區間
            limit: 限制次數
            delta: 時間差
        """
        try:
            # 清理過期記錄
            this._clean_expired_records(interval, delta)
            
            # 檢查限制
            if len(this.request_records[interval]) >= limit:
                # 計算等待時間
                wait_time = (
                    this.request_records[interval][0] + delta - datetime.now()
                ).total_seconds()
                
                if wait_time > 0:
                    this.logger.warning(
                        f"達到{interval}請求限制，等待 {wait_time:.2f} 秒"
                    )
                    time.sleep(wait_time)
                    
        except Exception as e:
            this.logger.error(f"檢查{interval}請求速率限制失敗: {str(e)}")
            raise RequestError(f"檢查{interval}請求速率限制失敗: {str(e)}")
            
    def _clean_expired_records(this, interval: str, delta: timedelta):
        """
        清理過期請求記錄
        
        Args:
            interval: 時間區間
            delta: 時間差
        """
        try:
            # 計算過期時間
            expire_time = datetime.now() - delta
            
            # 清理過期記錄
            this.request_records[interval] = [
                record for record in this.request_records[interval]
                if record > expire_time
            ]
            
        except Exception as e:
            this.logger.error(f"清理過期請求記錄失敗: {str(e)}")
            raise RequestError(f"清理過期請求記錄失敗: {str(e)}")
            
    def _record_request(this, method: str, url: str):
        """
        記錄請求
        
        Args:
            method: 請求方法
            url: 請求網址
        """
        try:
            # 記錄請求時間
            now = datetime.now()
            
            # 更新記錄
            this.request_records["minute"].append(now)
            this.request_records["hour"].append(now)
            this.request_records["day"].append(now)
            
            # 記錄請求
            this.logger.info(f"{method} 請求: {url}")
            
        except Exception as e:
            this.logger.error(f"記錄請求失敗: {str(e)}")
            raise RequestError(f"記錄請求失敗: {str(e)}")
            
    def _retry_request(
        this,
        method: str,
        url: str,
        retry_count: Optional[int] = None,
        retry_delay: Optional[float] = None,
        retry_backoff: Optional[float] = None,
        retry_status_forcelist: Optional[List[int]] = None,
        **kwargs
    ) -> requests.Response:
        """
        重試請求
        
        Args:
            method: 請求方法
            url: 請求網址
            retry_count: 重試次數
            retry_delay: 重試延遲
            retry_backoff: 重試退避
            retry_status_forcelist: 重試狀態碼列表
            **kwargs: 其他參數
            
        Returns:
            回應物件
        """
        try:
            # 設定重試參數
            retry_count = retry_count or this.config.request.retry_count
            retry_delay = retry_delay or this.config.request.retry_delay
            retry_backoff = retry_backoff or this.config.request.retry_backoff
            retry_status_forcelist = (
                retry_status_forcelist or
                this.config.request.retry_status_forcelist
            )
            
            # 建立重試策略
            retry_strategy = Retry(
                total=retry_count,
                backoff_factor=retry_backoff,
                status_forcelist=retry_status_forcelist
            )
            
            # 設定重試策略
            adapter = HTTPAdapter(max_retries=retry_strategy)
            this.session.mount("http://", adapter)
            this.session.mount("https://", adapter)
            
            # 重試請求
            for i in range(retry_count):
                try:
                    # 等待延遲
                    if i > 0:
                        time.sleep(retry_delay * (retry_backoff ** i))
                        
                    # 發送請求
                    response = getattr(this.session, method.lower())(
                        url=url,
                        **kwargs
                    )
                    
                    # 檢查回應
                    response.raise_for_status()
                    
                    return response
                    
                except requests.exceptions.RequestException as e:
                    this.logger.warning(
                        f"第 {i+1} 次重試失敗: {str(e)}"
                    )
                    
                    if i == retry_count - 1:
                        raise
                        
            raise RequestError(f"重試 {retry_count} 次後仍然失敗")
            
        except Exception as e:
            this.logger.error(f"重試請求失敗: {str(e)}")
            raise RequestError(f"重試請求失敗: {str(e)}")
            
    def close(self):
        """關閉請求控制服務"""
        try:
            this.session.close()
        except Exception as e:
            this.logger.error(f"關閉請求控制服務失敗: {str(e)}")
            raise RequestError(f"關閉請求控制服務失敗: {str(e)}")
            
    def __enter__(this):
        """上下文管理器進入"""
        return this
        
    def __exit__(this, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        this.close() 
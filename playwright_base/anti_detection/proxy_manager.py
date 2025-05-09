"""
代理管理模組

提供代理服務器的管理、輪換和測試功能。
"""

import os
import json
import random
import requests
import time
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urlparse

from playwright_base.utils.logger import setup_logger
from playwright_base.utils.exceptions import ProxyException

# 設置日誌
logger = setup_logger(name=__name__)

class ProxyManager:
    """
    代理服務器管理類。
    
    提供代理的獲取、輪換、測試和管理功能。
    """
    
    def __init__(self, proxies_file: str = None, test_url: str = "https://httpbin.org/ip", timeout: int = 10):
        """
        初始化 ProxyManager 實例。
        
        參數:
            proxies_file (str): 包含代理列表的 JSON 檔案路徑。
            test_url (str): 用於測試代理連通性的 URL。
            timeout (int): 代理測試超時時間（秒）。
        """
        self.proxies = []
        self.current_index = 0
        self.test_url = test_url
        self.timeout = timeout
        
        # 如果提供了代理檔案，則從檔案載入
        if proxies_file and os.path.exists(proxies_file):
            self._load_proxies_from_file(proxies_file)
            
        logger.info(f"代理管理器已初始化，共載入 {len(self.proxies)} 個代理")
    
    def _load_proxies_from_file(self, file_path: str) -> None:
        """
        從檔案載入代理列表。
        
        參數:
            file_path (str): JSON 檔案路徑。
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if isinstance(data, list):
                # 直接列表格式
                for item in data:
                    if isinstance(item, str):
                        self.add_proxy_from_string(item)
                    elif isinstance(item, dict):
                        self.add_proxy(item)
            elif isinstance(data, dict) and 'proxies' in data:
                # 包含 'proxies' 鍵的字典
                for item in data['proxies']:
                    if isinstance(item, str):
                        self.add_proxy_from_string(item)
                    elif isinstance(item, dict):
                        self.add_proxy(item)
            else:
                logger.warning(f"從 {file_path} 載入的代理格式無效")
                return
                
            logger.info(f"已從 {file_path} 載入 {len(self.proxies)} 個代理")
            
        except Exception as e:
            logger.error(f"載入代理檔案時發生錯誤: {str(e)}")
    
    def add_proxy(self, proxy: Dict[str, Any]) -> None:
        """
        添加一個代理到代理列表。
        
        參數:
            proxy (Dict[str, Any]): 代理配置字典，格式如：
                {
                    "server": "http://example.com:8080",
                    "username": "user",  # 可選
                    "password": "pass"   # 可選
                }
        """
        if not proxy.get("server"):
            logger.warning("代理缺少伺服器地址，無法添加")
            return
            
        # 檢查是否已經存在
        for existing in self.proxies:
            if existing["server"] == proxy["server"]:
                logger.debug(f"代理 {proxy['server']} 已存在，跳過添加")
                return
                
        self.proxies.append(proxy)
        logger.debug(f"已添加代理: {proxy['server']}")
    
    def add_proxy_from_string(self, proxy_string: str) -> None:
        """
        從字符串添加代理。
        支持格式：
        - "http://user:pass@host:port"
        - "host:port"
        
        參數:
            proxy_string (str): 代理服務器字符串。
        """
        try:
            proxy = {}
            
            # 檢查是否包含協議
            if "://" not in proxy_string:
                proxy_string = f"http://{proxy_string}"
                
            # 解析 URL
            parsed = urlparse(proxy_string)
            
            # 構建代理配置
            protocol = parsed.scheme or "http"
            host = parsed.hostname
            port = parsed.port or (443 if protocol == "https" else 80)
            
            if not host:
                logger.warning(f"無法從 '{proxy_string}' 解析主機名")
                return
                
            proxy["server"] = f"{protocol}://{host}:{port}"
            
            # 解析認證資訊
            if parsed.username and parsed.password:
                proxy["username"] = parsed.username
                proxy["password"] = parsed.password
                
            self.add_proxy(proxy)
            
        except Exception as e:
            logger.error(f"解析代理字符串 '{proxy_string}' 時發生錯誤: {str(e)}")
    
    def get_random_proxy(self) -> Optional[Dict[str, Any]]:
        """
        隨機獲取一個代理。
        
        返回:
            Optional[Dict[str, Any]]: 隨機代理配置字典，若無代理則返回 None。
        """
        if not self.proxies:
            logger.warning("代理列表為空")
            return None
            
        proxy = random.choice(self.proxies)
        logger.debug(f"隨機選擇代理: {proxy['server']}")
        return proxy
    
    def next_proxy(self) -> Optional[Dict[str, Any]]:
        """
        順序獲取下一個代理。
        
        返回:
            Optional[Dict[str, Any]]: 下一個代理配置字典，若無代理則返回 None。
        """
        if not self.proxies:
            logger.warning("代理列表為空")
            return None
            
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        logger.debug(f"選擇下一個代理: {proxy['server']}")
        return proxy
    
    def test_proxy(self, proxy: Dict[str, Any]) -> Dict[str, Any]:
        """
        測試代理的連通性。
        
        參數:
            proxy (Dict[str, Any]): 要測試的代理配置字典。
            
        返回:
            Dict[str, Any]: 測試結果字典，包含是否成功、響應時間等信息。
        """
        result = {
            "proxy": proxy["server"],
            "success": False,
            "response_time": None,
            "error": None,
            "ip": None
        }
        
        # 構建 requests 使用的代理格式
        req_proxy = {}
        
        protocol = proxy["server"].split("://")[0]
        req_proxy[protocol] = proxy["server"]
        
        # 添加認證信息
        if proxy.get("username") and proxy.get("password"):
            auth = f"{proxy['username']}:{proxy['password']}"
            server = proxy["server"].replace("://", f"://{auth}@")
            req_proxy[protocol] = server
            
        try:
            start_time = time.time()
            response = requests.get(self.test_url, proxies=req_proxy, timeout=self.timeout)
            end_time = time.time()
            
            if response.status_code == 200:
                result["success"] = True
                result["response_time"] = round((end_time - start_time) * 1000)  # 毫秒
                
                # 嘗試從 httpbin.org/ip 獲取 IP
                try:
                    data = response.json()
                    if "origin" in data:
                        result["ip"] = data["origin"]
                except Exception:
                    pass
                    
                logger.info(f"代理 {proxy['server']} 測試成功，響應時間: {result['response_time']}ms，IP: {result['ip']}")
            else:
                result["error"] = f"HTTP 錯誤: {response.status_code}"
                logger.warning(f"代理 {proxy['server']} 返回錯誤狀態碼: {response.status_code}")
                
        except requests.exceptions.Timeout:
            result["error"] = "超時"
            logger.warning(f"代理 {proxy['server']} 連接超時")
        except requests.exceptions.ProxyError as e:
            result["error"] = f"代理錯誤: {str(e)}"
            logger.warning(f"代理 {proxy['server']} 發生錯誤: {str(e)}")
        except Exception as e:
            result["error"] = str(e)
            logger.warning(f"測試代理 {proxy['server']} 時發生錯誤: {str(e)}")
            
        return result
    
    def test_all_proxies(self) -> List[Dict[str, Any]]:
        """
        測試所有代理的連通性。
        
        返回:
            List[Dict[str, Any]]: 所有代理的測試結果列表。
        """
        results = []
        
        if not self.proxies:
            logger.warning("代理列表為空，無法測試")
            return results
            
        logger.info(f"開始測試 {len(self.proxies)} 個代理...")
        
        for proxy in self.proxies:
            result = self.test_proxy(proxy)
            results.append(result)
            # 避免過快測試
            time.sleep(1)
            
        # 統計結果
        success_count = sum(1 for r in results if r["success"])
        logger.info(f"代理測試完成，{success_count}/{len(results)} 個代理可用")
        
        return results
    
    def get_working_proxies(self) -> List[Dict[str, Any]]:
        """
        獲取所有可用的代理。
        
        返回:
            List[Dict[str, Any]]: 可用代理列表。
        """
        if not self.proxies:
            logger.warning("代理列表為空")
            return []
            
        working_proxies = []
        results = self.test_all_proxies()
        
        for result, proxy in zip(results, self.proxies):
            if result["success"]:
                working_proxies.append(proxy)
                
        logger.info(f"找到 {len(working_proxies)} 個可用代理")
        return working_proxies
    
    def save_proxies_to_file(self, file_path: str) -> bool:
        """
        將目前的代理列表保存到檔案。
        
        參數:
            file_path (str): 要保存的檔案路徑。
            
        返回:
            bool: 保存是否成功。
        """
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({'proxies': self.proxies}, f, indent=2)
                
            logger.info(f"已將 {len(self.proxies)} 個代理保存到 {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存代理到檔案時發生錯誤: {str(e)}")
            return False
    
    def get_playwright_proxy(self, proxy: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        獲取 Playwright 格式的代理配置。
        如果不指定代理，則隨機選擇一個。
        
        參數:
            proxy (Optional[Dict[str, Any]]): 代理配置字典，若為 None 則隨機選擇。
            
        返回:
            Optional[Dict[str, Any]]: Playwright 格式的代理配置，若無可用代理則返回 None。
        """
        if proxy is None:
            proxy = self.get_random_proxy()
            
        if not proxy:
            return None
            
        # 轉換為 Playwright 代理格式
        pw_proxy = {
            "server": proxy["server"]
        }
        
        # 添加認證信息
        if proxy.get("username") and proxy.get("password"):
            pw_proxy["username"] = proxy["username"]
            pw_proxy["password"] = proxy["password"]
            
        return pw_proxy
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import pickle
import logging
from typing import Dict, List, Optional, Any, Union

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from .logger import setup_logger
from .error_handler import retry_on_exception, handle_exception


class CookieManager:
    """
    Cookie管理工具，提供Cookie的保存、載入、更新和管理功能。
    支持多種格式的Cookie儲存和不同瀏覽器的Cookie轉換。
    """
    
    def __init__(
        self,
        cookie_dir: str = "cookies",
        cookie_expiry: int = 86400,  # 1天
        auto_save: bool = True,
        log_level: int = logging.INFO
    ):
        """
        初始化Cookie管理器
        
        Args:
            cookie_dir: Cookie儲存目錄
            cookie_expiry: Cookie過期時間（秒）
            auto_save: 是否自動保存Cookie
            log_level: 日誌級別
        """
        self.logger = setup_logger(__name__, log_level)
        self.cookie_dir = cookie_dir
        self.cookie_expiry = cookie_expiry
        self.auto_save = auto_save
        
        # 確保Cookie目錄存在
        os.makedirs(cookie_dir, exist_ok=True)
        
        self.logger.info(f"Cookie管理器初始化，目錄: {cookie_dir}")
    
    def _get_cookie_path(self, domain: str, format: str = "json") -> str:
        """
        獲取Cookie文件路徑
        
        Args:
            domain: 網站域名
            format: 文件格式，支持json, pickle
            
        Returns:
            Cookie文件路徑
        """
        # 處理域名格式
        domain = domain.lstrip(".")
        domain = domain.replace(".", "_")
        
        return os.path.join(self.cookie_dir, f"{domain}.{format}")
    
    def save_cookies(
        self,
        driver: WebDriver,
        domain: str = None,
        format: str = "json",
        metadata: Dict = None
    ) -> bool:
        """
        保存瀏覽器中的Cookie
        
        Args:
            driver: WebDriver實例
            domain: 網站域名，為None時從當前URL中提取
            format: 保存格式，支持json, pickle
            metadata: 額外的元數據
            
        Returns:
            是否成功保存
        """
        try:
            if domain is None:
                # 從當前URL中提取域名
                current_url = driver.current_url
                from urllib.parse import urlparse
                domain = urlparse(current_url).netloc
            
            # 獲取所有Cookie
            cookies = driver.get_cookies()
            
            if not cookies:
                self.logger.warning(f"沒有找到Cookie: {domain}")
                return False
            
            # 添加元數據
            data = {
                "cookies": cookies,
                "timestamp": int(time.time()),
                "expiry": int(time.time()) + self.cookie_expiry,
                "domain": domain,
                "metadata": metadata or {}
            }
            
            # 保存Cookie
            cookie_path = self._get_cookie_path(domain, format)
            
            if format.lower() == "json":
                with open(cookie_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            elif format.lower() == "pickle":
                with open(cookie_path, "wb") as f:
                    pickle.dump(data, f)
            else:
                self.logger.error(f"不支持的格式: {format}")
                return False
            
            self.logger.info(f"已保存 {len(cookies)} 個Cookie到 {cookie_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"保存Cookie失敗: {str(e)}")
            return False
    
    def load_cookies(
        self,
        driver: WebDriver,
        domain: str = None,
        format: str = "json",
        check_expiry: bool = True
    ) -> int:
        """
        載入Cookie到瀏覽器
        
        Args:
            driver: WebDriver實例
            domain: 網站域名，為None時從當前URL中提取
            format: 文件格式
            check_expiry: 是否檢查過期時間
            
        Returns:
            成功載入的Cookie數量，-1表示載入失敗
        """
        try:
            if domain is None:
                # 從當前URL中提取域名
                current_url = driver.current_url
                from urllib.parse import urlparse
                domain = urlparse(current_url).netloc
            
            # 獲取Cookie文件路徑
            cookie_path = self._get_cookie_path(domain, format)
            
            if not os.path.exists(cookie_path):
                self.logger.warning(f"Cookie文件不存在: {cookie_path}")
                return 0
            
            # 載入Cookie
            if format.lower() == "json":
                with open(cookie_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif format.lower() == "pickle":
                with open(cookie_path, "rb") as f:
                    data = pickle.load(f)
            else:
                self.logger.error(f"不支持的格式: {format}")
                return -1
            
            # 檢查過期時間
            if check_expiry and "expiry" in data:
                if data["expiry"] < int(time.time()):
                    self.logger.warning(f"Cookie已過期: {cookie_path}")
                    return 0
            
            # 提取Cookie列表
            cookies = data.get("cookies", [])
            
            if not cookies:
                self.logger.warning(f"Cookie文件中沒有找到Cookie: {cookie_path}")
                return 0
            
            # 清除現有Cookie
            driver.delete_all_cookies()
            
            # 添加Cookie
            loaded_count = 0
            for cookie in cookies:
                try:
                    # 處理過期時間格式
                    if "expiry" in cookie and isinstance(cookie["expiry"], float):
                        cookie["expiry"] = int(cookie["expiry"])
                    
                                        # 添加Cookie
                    driver.add_cookie(cookie)
                    loaded_count += 1
                except Exception as cookie_error:
                    self.logger.warning(f"添加Cookie失敗: {str(cookie_error)}")
            
            self.logger.info(f"已載入 {loaded_count}/{len(cookies)} 個Cookie")
            return loaded_count
        
        except Exception as e:
            self.logger.error(f"載入Cookie失敗: {str(e)}")
            return -1
    
    def delete_cookies(self, domain: str, format: str = "json") -> bool:
        """
        刪除指定域名的Cookie文件
        
        Args:
            domain: 網站域名
            format: 文件格式
            
        Returns:
            是否成功刪除
        """
        try:
            cookie_path = self._get_cookie_path(domain, format)
            
            if os.path.exists(cookie_path):
                os.remove(cookie_path)
                self.logger.info(f"已刪除Cookie文件: {cookie_path}")
                return True
            else:
                self.logger.warning(f"Cookie文件不存在: {cookie_path}")
                return False
        
        except Exception as e:
            self.logger.error(f"刪除Cookie失敗: {str(e)}")
            return False
    
    def update_cookies(
        self, 
        driver: WebDriver,
        domain: str = None,
        format: str = "json",
        merge: bool = True
    ) -> bool:
        """
        更新Cookie文件
        
        Args:
            driver: WebDriver實例
            domain: 網站域名，為None時從當前URL中提取
            format: 文件格式
            merge: 是否合併現有Cookie
            
        Returns:
            是否成功更新
        """
        try:
            if domain is None:
                # 從當前URL中提取域名
                current_url = driver.current_url
                from urllib.parse import urlparse
                domain = urlparse(current_url).netloc
            
            cookie_path = self._get_cookie_path(domain, format)
            
            # 獲取瀏覽器中的Cookie
            new_cookies = driver.get_cookies()
            
            if not new_cookies:
                self.logger.warning(f"瀏覽器中沒有找到Cookie，不進行更新")
                return False
            
            # 如果需要合併且文件存在
            if merge and os.path.exists(cookie_path):
                # 載入現有Cookie
                if format.lower() == "json":
                    with open(cookie_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                elif format.lower() == "pickle":
                    with open(cookie_path, "rb") as f:
                        data = pickle.load(f)
                else:
                    self.logger.error(f"不支持的格式: {format}")
                    return False
                
                # 合併Cookie
                old_cookies = data.get("cookies", [])
                
                # 創建域名到Cookie的映射
                cookie_map = {cookie.get("name"): cookie for cookie in old_cookies}
                
                # 更新或添加新Cookie
                for cookie in new_cookies:
                    cookie_map[cookie.get("name")] = cookie
                
                # 轉換回列表
                merged_cookies = list(cookie_map.values())
                
                # 更新數據
                data["cookies"] = merged_cookies
                data["timestamp"] = int(time.time())
                data["expiry"] = int(time.time()) + self.cookie_expiry
            else:
                # 創建新數據
                data = {
                    "cookies": new_cookies,
                    "timestamp": int(time.time()),
                    "expiry": int(time.time()) + self.cookie_expiry,
                    "domain": domain,
                    "metadata": {}
                }
            
            # 保存更新後的Cookie
            if format.lower() == "json":
                with open(cookie_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            elif format.lower() == "pickle":
                with open(cookie_path, "wb") as f:
                    pickle.dump(data, f)
            else:
                self.logger.error(f"不支持的格式: {format}")
                return False
            
            cookie_count = len(data.get("cookies", []))
            self.logger.info(f"已更新 {cookie_count} 個Cookie到 {cookie_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"更新Cookie失敗: {str(e)}")
            return False
    
    def get_cookies(self, domain: str, format: str = "json") -> List[Dict]:
        """
        獲取指定域名的Cookie
        
        Args:
            domain: 網站域名
            format: 文件格式
            
        Returns:
            Cookie列表，空列表表示獲取失敗
        """
        try:
            cookie_path = self._get_cookie_path(domain, format)
            
            if not os.path.exists(cookie_path):
                self.logger.warning(f"Cookie文件不存在: {cookie_path}")
                return []
            
            # 載入Cookie
            if format.lower() == "json":
                with open(cookie_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif format.lower() == "pickle":
                with open(cookie_path, "rb") as f:
                    data = pickle.load(f)
            else:
                self.logger.error(f"不支持的格式: {format}")
                return []
            
            # 提取Cookie列表
            cookies = data.get("cookies", [])
            
            return cookies
        
        except Exception as e:
            self.logger.error(f"獲取Cookie失敗: {str(e)}")
            return []
    
    def get_cookie_metadata(self, domain: str, format: str = "json") -> Dict:
        """
        獲取Cookie的元數據
        
        Args:
            domain: 網站域名
            format: 文件格式
            
        Returns:
            元數據字典，空字典表示獲取失敗
        """
        try:
            cookie_path = self._get_cookie_path(domain, format)
            
            if not os.path.exists(cookie_path):
                self.logger.warning(f"Cookie文件不存在: {cookie_path}")
                return {}
            
            # 載入Cookie
            if format.lower() == "json":
                with open(cookie_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif format.lower() == "pickle":
                with open(cookie_path, "rb") as f:
                    data = pickle.load(f)
            else:
                self.logger.error(f"不支持的格式: {format}")
                return {}
            
            # 提取元數據
            metadata = data.get("metadata", {})
            metadata["timestamp"] = data.get("timestamp")
            metadata["expiry"] = data.get("expiry")
            metadata["domain"] = data.get("domain")
            metadata["cookie_count"] = len(data.get("cookies", []))
            
            return metadata
        
        except Exception as e:
            self.logger.error(f"獲取Cookie元數據失敗: {str(e)}")
            return {}
    
    def is_cookie_valid(self, domain: str, format: str = "json") -> bool:
        """
        檢查Cookie是否有效（未過期）
        
        Args:
            domain: 網站域名
            format: 文件格式
            
        Returns:
            Cookie是否有效
        """
        try:
            cookie_path = self._get_cookie_path(domain, format)
            
            if not os.path.exists(cookie_path):
                self.logger.debug(f"Cookie文件不存在: {cookie_path}")
                return False
            
            # 載入Cookie
            if format.lower() == "json":
                with open(cookie_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif format.lower() == "pickle":
                with open(cookie_path, "rb") as f:
                    data = pickle.load(f)
            else:
                self.logger.error(f"不支持的格式: {format}")
                return False
            
            # 檢查過期時間
            if "expiry" in data:
                if data["expiry"] < int(time.time()):
                    self.logger.debug(f"Cookie已過期: {cookie_path}")
                    return False
            
            # 檢查Cookie是否存在
            cookies = data.get("cookies", [])
            if not cookies:
                self.logger.debug(f"Cookie文件中沒有Cookie: {cookie_path}")
                return False
            
            return True
        
        except Exception as e:
            self.logger.error(f"檢查Cookie有效性失敗: {str(e)}")
            return False
    
    def list_domains(self, format: str = "json") -> List[str]:
        """
        列出所有保存了Cookie的域名
        
        Args:
            format: 文件格式
            
        Returns:
            域名列表
        """
        try:
            domains = []
            
            # 獲取所有Cookie文件
            cookie_files = [f for f in os.listdir(self.cookie_dir) if f.endswith(f".{format}")]
            
            for cookie_file in cookie_files:
                # 從文件名提取域名
                domain = cookie_file.replace(f".{format}", "")
                domain = domain.replace("_", ".")
                domains.append(domain)
            
            return domains
        
        except Exception as e:
            self.logger.error(f"列出域名失敗: {str(e)}")
            return []
    
    def serialize_cookies_to_string(self, domain: str, format: str = "json") -> str:
        """
        將Cookie序列化為字符串
        
        Args:
            domain: 網站域名
            format: 文件格式
            
        Returns:
            序列化後的字符串，空字符串表示序列化失敗
        """
        try:
            cookies = self.get_cookies(domain, format)
            
            if not cookies:
                return ""
            
            # 轉換為 "name=value; " 格式
            cookie_strings = []
            for cookie in cookies:
                name = cookie.get("name")
                value = cookie.get("value")
                if name and value:
                    cookie_strings.append(f"{name}={value}")
            
            return "; ".join(cookie_strings)
        
        except Exception as e:
            self.logger.error(f"序列化Cookie失敗: {str(e)}")
            return ""
"""
Cookie 管理模組

管理瀏覽器 Cookie，以維持會話狀態
"""

import json
import time
from typing import Dict, List, Optional, Union, Any
from selenium import webdriver
from selenium_base.core.logger import Logger
from selenium_base.anti_detection.base_manager import BaseManager
from selenium_base.anti_detection.base_error import CookieError

class CookieManager(BaseManager):
    """Cookie 管理類別"""
    
    def __init__(self, driver: webdriver.Remote, config: Dict, logger: Optional[Logger] = None):
        """
        初始化 Cookie 管理類別
        
        Args:
            driver: 瀏覽器驅動程式
            config: 配置字典
            logger: 日誌記錄器
        """
        super().__init__(driver, config, logger)
        self.cookies = {}
        
    def setup(self) -> None:
        """設置 Cookie 環境"""
        if not self.is_enabled():
            return
            
        try:
            # 載入 Cookie
            self._load_cookies()
            self.logger.info("Cookie 設置完成")
        except Exception as e:
            self.logger.error(f"Cookie 設置失敗: {str(e)}")
            raise CookieError(f"Cookie 設置失敗: {str(e)}")
            
    def cleanup(self) -> None:
        """清理 Cookie 環境"""
        if not self.is_enabled():
            return
            
        try:
            # 清除 Cookie
            self.driver.delete_all_cookies()
            self.cookies = {}
            self.logger.info("Cookie 清理完成")
        except Exception as e:
            self.logger.error(f"Cookie 清理失敗: {str(e)}")
            
    def _load_cookies(self) -> None:
        """載入 Cookie"""
        try:
            cookie_file = self.config.get("cookie_file")
            if not cookie_file:
                return
                
            # 讀取 Cookie 文件
            with open(cookie_file, "r", encoding="utf-8") as f:
                cookies = json.load(f)
                
            # 添加 Cookie
            for cookie in cookies:
                self.driver.add_cookie(cookie)
                self.cookies[cookie["name"]] = cookie
                
            self.logger.info(f"載入 {len(cookies)} 個 Cookie")
            
        except Exception as e:
            self.logger.error(f"載入 Cookie 失敗: {str(e)}")
            raise CookieError(f"載入 Cookie 失敗: {str(e)}")
            
    def save_cookies(self, file_path: str) -> None:
        """
        保存 Cookie 到文件
        
        Args:
            file_path: 文件路徑
        """
        try:
            cookies = self.driver.get_cookies()
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(cookies, f, indent=2)
            self.logger.info(f"保存 {len(cookies)} 個 Cookie 到 {file_path}")
        except Exception as e:
            self.logger.error(f"保存 Cookie 失敗: {str(e)}")
            raise CookieError(f"保存 Cookie 失敗: {str(e)}")
            
    def get_cookie(self, name: str) -> Optional[Dict]:
        """
        獲取指定名稱的 Cookie
        
        Args:
            name: Cookie 名稱
            
        Returns:
            Cookie 字典
        """
        return self.cookies.get(name)
        
    def set_cookie(self, cookie: Dict) -> None:
        """
        設置 Cookie
        
        Args:
            cookie: Cookie 字典
        """
        try:
            self.driver.add_cookie(cookie)
            self.cookies[cookie["name"]] = cookie
            self.logger.info(f"設置 Cookie: {cookie['name']}")
        except Exception as e:
            self.logger.error(f"設置 Cookie 失敗: {str(e)}")
            raise CookieError(f"設置 Cookie 失敗: {str(e)}")
            
    def delete_cookie(self, name: str) -> None:
        """
        刪除 Cookie
        
        Args:
            name: Cookie 名稱
        """
        try:
            self.driver.delete_cookie(name)
            self.cookies.pop(name, None)
            self.logger.info(f"刪除 Cookie: {name}")
        except Exception as e:
            self.logger.error(f"刪除 Cookie 失敗: {str(e)}")
            raise CookieError(f"刪除 Cookie 失敗: {str(e)}")
            
    def clear_cookies(self) -> None:
        """清除所有 Cookie"""
        try:
            self.driver.delete_all_cookies()
            self.cookies = {}
            self.logger.info("清除所有 Cookie")
        except Exception as e:
            self.logger.error(f"清除 Cookie 失敗: {str(e)}")
            raise CookieError(f"清除 Cookie 失敗: {str(e)}")
            
    def get_all_cookies(self) -> List[Dict]:
        """
        獲取所有 Cookie
        
        Returns:
            Cookie 列表
        """
        return list(self.cookies.values())
        
    def is_cookie_valid(self, name: str) -> bool:
        """
        檢查 Cookie 是否有效
        
        Args:
            name: Cookie 名稱
            
        Returns:
            Cookie 是否有效
        """
        try:
            cookie = self.get_cookie(name)
            if not cookie:
                return False
                
            # 檢查過期時間
            if "expiry" in cookie:
                return cookie["expiry"] > time.time()
                
            return True
        except Exception as e:
            self.logger.error(f"檢查 Cookie 有效性失敗: {str(e)}")
            return False 
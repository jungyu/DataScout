#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cookie 管理模組
提供跨瀏覽器的 cookie 管理功能，支援持久化存儲和加密
"""

import os
import json
import base64
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException

from .utils.encryption import encrypt_data, decrypt_data

class CookieManager:
    """Cookie 管理類"""
    
    def __init__(
        self,
        driver: WebDriver,
        storage_path: str = "data/cookies",
        encryption_key: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化 Cookie 管理器
        
        Args:
            driver: WebDriver 實例
            storage_path: Cookie 存儲路徑
            encryption_key: 加密密鑰
            logger: 日誌記錄器
        """
        self.driver = driver
        self.storage_path = Path(storage_path)
        self.encryption_key = encryption_key
        self.logger = logger or logging.getLogger(__name__)
        
        # 創建存儲目錄
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save_cookies(self, domain: str, cookies: List[Dict]) -> bool:
        """
        保存 cookies 到文件
        
        Args:
            domain: 網站域名
            cookies: cookie 列表
            
        Returns:
            是否保存成功
        """
        try:
            # 創建域名目錄
            domain_dir = self.storage_path / domain
            domain_dir.mkdir(exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cookies_{timestamp}.json"
            filepath = domain_dir / filename
            
            # 準備數據
            cookie_data = {
                "domain": domain,
                "timestamp": timestamp,
                "cookies": cookies
            }
            
            # 加密數據
            if self.encryption_key:
                cookie_data = encrypt_data(json.dumps(cookie_data), self.encryption_key)
            
            # 保存到文件
            with open(filepath, "w", encoding="utf-8") as f:
                if self.encryption_key:
                    f.write(cookie_data)
                else:
                    json.dump(cookie_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Cookies 已保存到: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存 cookies 失敗: {str(e)}")
            return False
    
    def load_cookies(self, domain: str, max_age_hours: int = 24) -> Optional[List[Dict]]:
        """
        從文件加載 cookies
        
        Args:
            domain: 網站域名
            max_age_hours: cookie 最大有效期（小時）
            
        Returns:
            cookie 列表，如果加載失敗則返回 None
        """
        try:
            domain_dir = self.storage_path / domain
            if not domain_dir.exists():
                self.logger.warning(f"未找到域名目錄: {domain}")
                return None
            
            # 獲取最新的 cookie 文件
            cookie_files = list(domain_dir.glob("cookies_*.json"))
            if not cookie_files:
                self.logger.warning(f"未找到 cookie 文件: {domain}")
                return None
            
            latest_file = max(cookie_files, key=lambda x: x.stat().st_mtime)
            
            # 檢查文件年齡
            file_age = datetime.now().timestamp() - latest_file.stat().st_mtime
            if file_age > max_age_hours * 3600:
                self.logger.warning(f"Cookie 文件過期: {latest_file}")
                return None
            
            # 讀取文件
            with open(latest_file, "r", encoding="utf-8") as f:
                if self.encryption_key:
                    content = f.read()
                    cookie_data = json.loads(decrypt_data(content, self.encryption_key))
                else:
                    cookie_data = json.load(f)
            
            self.logger.info(f"已加載 cookies: {latest_file}")
            return cookie_data["cookies"]
            
        except Exception as e:
            self.logger.error(f"加載 cookies 失敗: {str(e)}")
            return None
    
    def add_cookies(self, cookies: List[Dict]) -> bool:
        """
        添加 cookies 到瀏覽器
        
        Args:
            cookies: cookie 列表
            
        Returns:
            是否添加成功
        """
        try:
            for cookie in cookies:
                # 移除不必要的字段
                if "sameSite" in cookie:
                    del cookie["sameSite"]
                if "expiry" in cookie:
                    cookie["expiry"] = int(cookie["expiry"])
                
                self.driver.add_cookie(cookie)
            
            self.logger.info(f"已添加 {len(cookies)} 個 cookies")
            return True
            
        except Exception as e:
            self.logger.error(f"添加 cookies 失敗: {str(e)}")
            return False
    
    def get_cookies(self) -> List[Dict]:
        """
        獲取當前所有 cookies
        
        Returns:
            cookie 列表
        """
        try:
            return self.driver.get_cookies()
        except Exception as e:
            self.logger.error(f"獲取 cookies 失敗: {str(e)}")
            return []
    
    def clear_cookies(self) -> bool:
        """
        清除所有 cookies
        
        Returns:
            是否清除成功
        """
        try:
            self.driver.delete_all_cookies()
            self.logger.info("已清除所有 cookies")
            return True
        except Exception as e:
            self.logger.error(f"清除 cookies 失敗: {str(e)}")
            return False
    
    def wait_for_cookie(self, name: str, timeout: int = 10) -> bool:
        """
        等待特定 cookie 出現
        
        Args:
            name: cookie 名稱
            timeout: 超時時間（秒）
            
        Returns:
            是否找到 cookie
        """
        try:
            def cookie_exists(driver):
                return any(cookie["name"] == name for cookie in driver.get_cookies())
            
            WebDriverWait(self.driver, timeout).until(cookie_exists)
            return True
        except TimeoutException:
            self.logger.warning(f"等待 cookie 超時: {name}")
            return False
        except Exception as e:
            self.logger.error(f"等待 cookie 失敗: {str(e)}")
            return False
    
    def get_cookie_value(self, name: str) -> Optional[str]:
        """
        獲取特定 cookie 的值
        
        Args:
            name: cookie 名稱
            
        Returns:
            cookie 值，如果不存在則返回 None
        """
        try:
            for cookie in self.driver.get_cookies():
                if cookie["name"] == name:
                    return cookie["value"]
            return None
        except Exception as e:
            self.logger.error(f"獲取 cookie 值失敗: {str(e)}")
            return None 
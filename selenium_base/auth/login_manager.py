#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
登入管理模組

提供以下功能：
1. 登入狀態管理
2. 登入驗證
3. 登入信息持久化
4. 登入重試機制
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Union, Any

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .auth_exceptions import LoginError, ValidationError
from .cookie_manager import CookieManager
from .session_manager import SessionManager
from ..core.logger import setup_logger
from ..core.utils import Utils

logger = setup_logger(__name__)

class LoginManager:
    """登入管理類"""
    
    def __init__(self, 
                 driver: Optional[WebDriver] = None,
                 cookie_manager: Optional[CookieManager] = None,
                 session_manager: Optional[SessionManager] = None,
                 login_file: Optional[str] = None):
        """
        初始化登入管理器
        
        Args:
            driver: Selenium WebDriver 實例
            cookie_manager: Cookie管理器實例
            session_manager: 會話管理器實例
            login_file: 登入信息文件路徑，默認為 ~/.datascout/login.json
        """
        self.driver = driver
        self.cookie_manager = cookie_manager or CookieManager()
        self.session_manager = session_manager or SessionManager()
        self.login_file = login_file or os.path.expanduser("~/.datascout/login.json")
        self.login_info: Dict[str, Dict] = {}
        self._load_login_info()
        
    def _load_login_info(self) -> None:
        """從文件加載登入信息"""
        try:
            if os.path.exists(self.login_file):
                with open(self.login_file, "r", encoding="utf-8") as f:
                    self.login_info = json.load(f)
        except Exception as e:
            logger.error(f"加載登入信息失敗: {str(e)}")
            self.login_info = {}
            
    def _save_login_info(self) -> None:
        """保存登入信息到文件"""
        try:
            Utils.ensure_dir(os.path.dirname(self.login_file))
            with open(self.login_file, "w", encoding="utf-8") as f:
                json.dump(self.login_info, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存登入信息失敗: {str(e)}")
            
    def add_login(self, domain: str, username: str, password: str) -> None:
        """
        添加登入信息
        
        Args:
            domain: 域名
            username: 用戶名
            password: 密碼
        """
        if domain not in self.login_info:
            self.login_info[domain] = {}
        self.login_info[domain].update({
            "username": username,
            "password": password,
            "last_login": datetime.now().isoformat()
        })
        self._save_login_info()
        
    def get_login(self, domain: str) -> Dict:
        """
        獲取登入信息
        
        Args:
            domain: 域名
            
        Returns:
            登入信息字典
        """
        return self.login_info.get(domain, {})
        
    def update_login(self, domain: str, username: Optional[str] = None, 
                    password: Optional[str] = None) -> None:
        """
        更新登入信息
        
        Args:
            domain: 域名
            username: 新的用戶名
            password: 新的密碼
        """
        if domain not in self.login_info:
            raise LoginError(f"域名 {domain} 的登入信息不存在")
            
        if username:
            self.login_info[domain]["username"] = username
        if password:
            self.login_info[domain]["password"] = password
            
        self.login_info[domain]["last_login"] = datetime.now().isoformat()
        self._save_login_info()
        
    def delete_login(self, domain: str) -> None:
        """
        刪除登入信息
        
        Args:
            domain: 域名
        """
        if domain in self.login_info:
            del self.login_info[domain]
            self._save_login_info()
            
    def clear_login(self) -> None:
        """清空所有登入信息"""
        self.login_info.clear()
        self._save_login_info()
        
    def is_logged_in(self, domain: str) -> bool:
        """
        檢查是否已登入
        
        Args:
            domain: 域名
            
        Returns:
            是否已登入
        """
        if domain not in self.login_info:
            return False
            
        # 檢查Cookie是否有效
        if not self.cookie_manager.is_cookie_valid(domain):
            return False
            
        # 檢查會話是否有效
        if not self.session_manager.is_session_valid(domain):
            return False
            
        return True
        
    def login(self, domain: str, username: str, password: str, 
             max_retries: int = 3, login_url: Optional[str] = None,
             username_selector: Optional[str] = None,
             password_selector: Optional[str] = None,
             submit_selector: Optional[str] = None,
             success_selector: Optional[str] = None) -> bool:
        """
        執行登入操作
        
        Args:
            domain: 域名
            username: 用戶名
            password: 密碼
            max_retries: 最大重試次數
            login_url: 登入頁面URL
            username_selector: 用戶名輸入框選擇器
            password_selector: 密碼輸入框選擇器
            submit_selector: 提交按鈕選擇器
            success_selector: 登入成功標誌選擇器
            
        Returns:
            登入是否成功
        """
        if not self.driver:
            raise LoginError("WebDriver 未初始化")
            
        retries = 0
        while retries < max_retries:
            try:
                # 訪問登入頁面
                if login_url:
                    self.driver.get(login_url)
                
                # 等待頁面加載
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, username_selector or "input[type='text']"))
                )
                
                # 輸入用戶名
                username_input = self.driver.find_element(By.CSS_SELECTOR, username_selector or "input[type='text']")
                username_input.clear()
                username_input.send_keys(username)
                
                # 輸入密碼
                password_input = self.driver.find_element(By.CSS_SELECTOR, password_selector or "input[type='password']")
                password_input.clear()
                password_input.send_keys(password)
                
                # 點擊提交按鈕
                submit_button = self.driver.find_element(By.CSS_SELECTOR, submit_selector or "button[type='submit']")
                submit_button.click()
                
                # 等待登入成功
                if success_selector:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, success_selector))
                    )
                
                # 保存Cookie
                cookies = self.driver.get_cookies()
                self.cookie_manager.add_cookies(domain, cookies)
                
                # 創建會話
                session_data = {
                    "username": username,
                    "login_time": datetime.now().isoformat(),
                    "expire_time": (datetime.now() + timedelta(days=7)).isoformat()
                }
                self.session_manager.create_session(domain, session_data)
                
                # 保存登入信息
                self.add_login(domain, username, password)
                
                logger.info(f"成功登入 {domain}")
                return True
                
            except Exception as e:
                retries += 1
                logger.error(f"登入失敗 (嘗試 {retries}/{max_retries}): {str(e)}")
                if retries == max_retries:
                    raise LoginError(f"登入失敗: {str(e)}")
                    
        return False
    
    def logout(self, domain: str, logout_url: Optional[str] = None,
              logout_button_selector: Optional[str] = None) -> None:
        """
        執行登出操作
        
        Args:
            domain: 域名
            logout_url: 登出頁面URL
            logout_button_selector: 登出按鈕選擇器
            
        Raises:
            LoginError: 登出失敗
        """
        try:
            if self.driver and logout_url:
                # 訪問登出頁面
                self.driver.get(logout_url)
                
                # 點擊登出按鈕
                if logout_button_selector:
                    logout_button = self.driver.find_element(By.CSS_SELECTOR, logout_button_selector)
                    logout_button.click()
            
            # 清除會話
            self.session_manager.delete_session(domain)
            
            # 清除 Cookie
            self.cookie_manager.delete_cookies(domain)
            
            logger.info(f"已登出 {domain}")
            
        except Exception as e:
            raise LoginError(f"登出失敗: {e}")
    
    def check_login_status(self, domain: str, status_url: Optional[str] = None,
                          status_selector: Optional[str] = None) -> bool:
        """
        檢查登入狀態
        
        Args:
            domain: 域名
            status_url: 狀態檢查頁面URL
            status_selector: 狀態檢查選擇器
            
        Returns:
            是否已登入
        """
        # 檢查會話是否存在且有效
        session = self.session_manager.get_session(domain)
        if not session:
            return False
        
        # 檢查 Cookie 是否存在
        cookies = self.cookie_manager.get_cookies(domain)
        if not cookies:
            return False
        
        # 如果提供了狀態檢查URL和選擇器，則訪問頁面檢查
        if self.driver and status_url and status_selector:
            try:
                self.driver.get(status_url)
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, status_selector))
                )
                return True
            except:
                return False
        
        return True
    
    def get_login_info(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        獲取登入信息
        
        Args:
            domain: 域名
            
        Returns:
            登入信息字典，如果未登入則返回 None
        """
        if not self.check_login_status(domain):
            return None
            
        session = self.session_manager.get_session(domain)
        if not session:
            return None
            
        return {
            "username": session.get("username"),
            "login_time": session.get("login_time"),
            "expire_time": session.get("expire_time")
        } 
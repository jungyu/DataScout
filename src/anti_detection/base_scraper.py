"""
基礎爬蟲模組
提供通用的爬蟲功能，包括 WebDriver 管理、Cookie 管理和截圖功能
"""

import os
import json
import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException

from .cookie_manager import CookieManager
from .browser_anti_fingerprint import BrowserAntiFingerprint

class BaseScraper:
    """基礎爬蟲類"""
    
    def __init__(
        self,
        config_path: str,
        data_dir: str,
        domain: str,
        debug_mode: bool = False,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化爬蟲
        
        Args:
            config_path: 配置文件路徑
            data_dir: 數據目錄
            domain: 目標網站域名
            debug_mode: 是否啟用調試模式
            logger: 日誌記錄器
        """
        self.config_path = config_path
        self.data_dir = Path(data_dir)
        self.domain = domain
        self.debug_mode = debug_mode
        self.logger = logger or logging.getLogger(__name__)
        self.driver = None
        
        # 建立子目錄
        self.cookies_dir = self.data_dir / "cookies"
        self.output_dir = self.data_dir / "output"
        self.screenshots_dir = self.data_dir / "screenshots"
        self.profiles_dir = self.data_dir / "profiles"
        
        for directory in [self.cookies_dir, self.output_dir, self.screenshots_dir, self.profiles_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # 載入配置
        self.config = self._load_config()
        
        # 初始化反指紋組件
        self.anti_fingerprint = BrowserAntiFingerprint(
            config=self.config.get("anti_fingerprint", {})
        )
        
        # 初始化 Cookie 管理器
        self.cookie_manager = CookieManager(
            driver=None,  # 將在 setup 中設置
            storage_path=str(self.cookies_dir),
            encryption_key=self.config.get("cookie", {}).get("encryption_key")
        )
        
        self.logger.info("初始化爬蟲")
        
    def _load_config(self) -> Dict:
        """載入配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            self.logger.info(f"已載入配置文件: {self.config_path}")
            return config
        except Exception as e:
            self.logger.error(f"載入配置文件失敗: {str(e)}")
            # 返回基本配置
            return {
                "site_name": "Default",
                "base_url": f"https://{self.domain}",
                "request": {
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
                    }
                },
                "delays": {
                    "page_load": 3,
                    "between_pages": 2
                }
            }
            
    def setup(self) -> bool:
        """設置爬蟲環境"""
        try:
            self.logger.info("開始設置爬蟲環境")
            
            # 設置 WebDriver
            self.driver = self.anti_fingerprint.create_driver()
            if not self.driver:
                self.logger.error("WebDriver 初始化失敗")
                return False
                
            # 更新 Cookie 管理器的 driver
            self.cookie_manager.driver = self.driver
                
            # 載入最佳 Cookie
            cookies = self.cookie_manager.load_cookies(self.domain)
            if cookies:
                self.logger.info(f"成功載入 {len(cookies)} 個 Cookie")
            else:
                self.logger.warning("未找到有效的 Cookie，將需要手動登入")
                
            # 訪問首頁
            self._visit_homepage()
            
            # 添加 Cookie (如果有)
            if cookies:
                self.cookie_manager.add_cookies(cookies)
                
            # 刷新頁面以應用 Cookie
            self.driver.refresh()
            time.sleep(self.config.get("delays", {}).get("page_load", 3))
            
            # 檢查登入狀態
            logged_in = self._check_login_status()
            
            # 如果未登入但需要登入，執行登入流程
            if not logged_in and self.config.get("login", {}).get("required", True):
                self.logger.info("需要登入")
                return self._perform_login()
                
            return True
            
        except Exception as e:
            self.logger.error(f"設置爬蟲環境失敗: {str(e)}")
            return False
            
    def _visit_homepage(self) -> None:
        """訪問首頁"""
        base_url = self.config.get("base_url", f"https://{self.domain}")
        self.logger.info(f"訪問首頁: {base_url}")
        
        self.driver.get(base_url)
        time.sleep(self.config.get("delays", {}).get("page_load", 3))
        
        # 模擬人類行為
        self.anti_fingerprint.simulate_human_behavior(self.driver)
        
        # 處理可能的驗證碼
        self.anti_fingerprint.handle_captcha(self.driver)
        
        # 截圖
        self._take_screenshot("homepage")
            
    def _check_login_status(self) -> bool:
        """檢查是否已登入"""
        try:
            self.logger.info("檢查登入狀態")
            
            # 方法1: 檢查特定元素是否存在
            login_indicators = self.config.get("login", {}).get("indicators", [])
            
            for indicator in login_indicators:
                elements = self.driver.find_elements(By.XPATH, indicator)
                if elements and elements[0].is_displayed():
                    self.logger.info("檢測到已登入狀態")
                    return True
                    
            # 方法2: 獲取當前 Cookie 並分析
            current_cookies = self.driver.get_cookies()
            if current_cookies:
                # 檢查必要的 Cookie 是否存在
                required_cookies = self.config.get("login", {}).get("required_cookies", [])
                if all(any(c["name"] == name for c in current_cookies) for name in required_cookies):
                    self.logger.info("通過 Cookie 分析確認已登入")
                    return True
                    
            self.logger.info("用戶未登入")
            return False
            
        except Exception as e:
            self.logger.error(f"檢查登入狀態時發生錯誤: {str(e)}")
            return False
            
    def _perform_login(self) -> bool:
        """執行登入流程"""
        try:
            self.logger.info("開始登入流程")
            
            # 獲取登入相關配置
            login_config = self.config.get("login", {})
            login_url = login_config.get("url", f"https://{self.domain}/login")
            
            # 訪問登入頁面
            self.logger.info(f"訪問登入頁面: {login_url}")
            self.driver.get(login_url)
            time.sleep(self.config.get("delays", {}).get("page_load", 3))
            
            # 處理可能的驗證碼
            self.anti_fingerprint.handle_captcha(self.driver)
            
            # 截圖
            self._take_screenshot("login_page")
            
            # 檢查是否需要手動登入
            manual_login = True  # 默認需要手動登入
            
            # 如果配置中有用戶名和密碼，嘗試自動登入
            username = login_config.get("username", "")
            password = login_config.get("password", "")
            
            if username and password:
                self.logger.info("嘗試使用配置中的憑證自動登入")
                manual_login = not self._auto_login(username, password)
            
            # 如果自動登入失敗或未配置，提示手動登入
            if manual_login:
                self.logger.info("需要手動登入")
                print("\n" + "="*50)
                print("請在瀏覽器窗口中手動完成登入")
                print("完成後請不要關閉瀏覽器")
                print("系統將在您完成登入後繼續運行")
                print("="*50 + "\n")
                
                # 等待用戶登入完成
                self._wait_for_login_completion()
            
            # 登入完成後，保存 Cookie
            if self._check_login_status():
                self.logger.info("登入成功，保存 Cookie")
                current_cookies = self.driver.get_cookies()
                self.cookie_manager.save_cookies(self.domain, current_cookies)
                return True
            else:
                self.logger.warning("登入流程完成，但用戶似乎仍未登入")
                return False
                
        except Exception as e:
            self.logger.error(f"登入過程中發生錯誤: {str(e)}")
            return False
            
    def _auto_login(self, username: str, password: str) -> bool:
        """自動填寫登入表單"""
        try:
            login_config = self.config.get("login", {})
            fields = login_config.get("fields", {})
            
            # 獲取表單元素選擇器
            username_selector = fields.get("username_selector", "//input[@name='username']")
            password_selector = fields.get("password_selector", "//input[@name='password']")
            submit_selector = fields.get("submit_selector", "//button[@type='submit']")
            
            # 等待用戶名輸入框
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, username_selector))
            )
            
            # 等待密碼輸入框
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, password_selector))
            )
            
            # 模擬人類輸入
            # 先移動到用戶名輸入框
            ActionChains(self.driver).move_to_element(username_input).perform()
            time.sleep(random.uniform(0.5, 1.0))
            
            # 清空輸入框
            username_input.clear()
            
            # 模擬人類輸入
            for char in username:
                username_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
                
            # 暫停一下
            time.sleep(random.uniform(0.5, 1.0))
            
            # 移動到密碼輸入框
            ActionChains(self.driver).move_to_element(password_input).perform()
            time.sleep(random.uniform(0.5, 1.0))
            
            # 清空輸入框
            password_input.clear()
            
            # 模擬人類輸入
            for char in password:
                password_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
                
            # 暫停一下
            time.sleep(random.uniform(0.5, 1.0))
            
            # 截圖
            self._take_screenshot("before_login_submit")
            
            # 找到提交按鈕
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, submit_selector))
            )
            
            # 移動到提交按鈕
            ActionChains(self.driver).move_to_element(submit_button).perform()
            time.sleep(random.uniform(0.5, 1.0))
            
            # 點擊提交按鈕
            submit_button.click()
            
            # 等待登入過程
            time.sleep(login_config.get("wait_after_login", 5))
            
            # 處理可能的驗證碼
            self.anti_fingerprint.handle_captcha(self.driver)
            
            # 截圖
            self._take_screenshot("after_login_submit")
            
            # 檢查是否登入成功
            return self._check_login_status()
            
        except Exception as e:
            self.logger.error(f"自動登入失敗: {str(e)}")
            return False
            
    def _wait_for_login_completion(self) -> None:
        """等待用戶完成手動登入"""
        self.logger.info("等待用戶手動完成登入")
        
        login_config = self.config.get("login", {})
        success_indicators = login_config.get("success_indicators", {})
        
        # 設定最長等待時間 (2分鐘)
        max_wait_time = 120
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            # 檢查 URL 中是否包含成功登入的指示符
            url_contains = success_indicators.get("url_contains", "")
            if url_contains and url_contains in self.driver.current_url:
                self.logger.info("檢測到成功登入 URL 指示")
                return
                
            # 檢查是否存在登入成功的元素
            element_present = success_indicators.get("element_present", "")
            if element_present:
                try:
                    elements = self.driver.find_elements(By.XPATH, element_present)
                    if elements and elements[0].is_displayed():
                        self.logger.info("檢測到成功登入元素指示")
                        return
                except:
                    pass
                    
            # 檢查是否已登入
            if self._check_login_status():
                self.logger.info("檢測到登入狀態")
                return
                
            # 短暫休息
            time.sleep(1)
            
        self.logger.warning("等待登入超時")
        
    def _take_screenshot(self, name: str) -> Optional[str]:
        """擷取頁面截圖"""
        if not self.driver:
            return None
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            screenshot_path = self.screenshots_dir / filename
            self.driver.save_screenshot(str(screenshot_path))
            self.logger.info(f"已保存截圖：{screenshot_path}")
            return str(screenshot_path)
        except Exception as e:
            self.logger.error(f"截圖失敗：{str(e)}")
            return None
            
    def close(self):
        """關閉爬蟲"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
            self.logger.info("爬蟲已關閉")
        except Exception as e:
            self.logger.error(f"關閉爬蟲時發生錯誤: {str(e)}")
            
    def __enter__(self):
        """上下文管理器入口"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close() 
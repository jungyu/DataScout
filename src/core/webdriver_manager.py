#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WebDriver管理模組

負責管理WebDriver實例，包括：
- 創建和配置WebDriver
- 管理WebDriver資源
- 監控WebDriver狀態
- 處理WebDriver錯誤
- 管理臨時文件
"""

import os
import time
import logging
import threading
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from .utils.logger import Logger, setup_logger
from .utils.path_utils import PathUtils
from .utils.config_utils import ConfigUtils
from .utils.browser_utils import BrowserUtils
from .utils.error_handler import ErrorHandler

@dataclass
class BrowserConfig:
    """瀏覽器配置"""
    headless: bool = False
    proxy: Optional[str] = None
    user_agent: Optional[str] = None
    window_size: tuple = (1920, 1080)
    page_load_timeout: int = 30
    script_timeout: int = 30
    implicit_wait: int = 10
    download_dir: Optional[str] = None
    disable_images: bool = False
    disable_javascript: bool = False
    disable_gpu: bool = True
    no_sandbox: bool = True
    disable_dev_shm_usage: bool = True
    disable_extensions: bool = True
    disable_notifications: bool = True
    disable_popup_blocking: bool = True
    disable_automation: bool = True
    disable_infobars: bool = True
    disable_logging: bool = True
    disable_web_security: bool = False
    allow_running_insecure_content: bool = False
    accept_insecure_certs: bool = False
    accept_language: str = "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    accept_encoding: str = "gzip, deflate, br"
    accept: str = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    dns_prefetch: bool = True
    preload: bool = True
    disk_cache_size: int = 1024 * 1024 * 1024  # 1GB
    memory_cache_size: int = 1024 * 1024 * 1024  # 1GB
    max_connections: int = 100
    max_connections_per_host: int = 10
    max_connections_per_proxy: int = 10
    max_retries: int = 3
    retry_delay: int = 5
    cleanup_interval: int = 3600  # 1小時
    max_drivers: int = 5
    driver_timeout: int = 300  # 5分鐘

class WebDriverManager:
    """WebDriver管理器"""
    
    def __init__(self, config: Dict):
        """
        初始化WebDriver管理器
        
        Args:
            config: 配置字典
        """
        # 初始化工具類
        self.logger = setup_logger(
            name="webdriver_manager",
            level=logging.INFO,
            log_dir="logs",
            console_output=True,
            file_output=True
        )
        self.path_utils = PathUtils(self.logger)
        self.config_utils = ConfigUtils(self.logger)
        self.browser_utils = BrowserUtils(self.logger)
        self.error_handler = ErrorHandler(self.logger)
        
        # 加載配置
        self.config = BrowserConfig(**config)
        
        # 創建臨時目錄
        self.temp_dir = self.path_utils.join_path("temp", "webdriver")
        self.path_utils.ensure_dir(self.temp_dir)
        
        # 初始化WebDriver池
        self.drivers: Dict[str, webdriver.Chrome] = {}
        self.driver_lock = threading.Lock()
        
        # 初始化統計信息
        self.stats = {
            "total_drivers": 0,
            "active_drivers": 0,
            "failed_drivers": 0,
            "total_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0,
            "start_time": datetime.now(),
            "last_update": None
        }
        
        # 啟動清理線程
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True
        )
        self.cleanup_thread.start()
    
    def get_driver(self) -> Optional[webdriver.Chrome]:
        """
        獲取WebDriver實例
        
        Returns:
            WebDriver實例
        """
        try:
            with self.driver_lock:
                # 檢查是否達到最大驅動數
                if len(self.drivers) >= self.config.max_drivers:
                    self.logger.warning("已達到最大WebDriver數量")
                    return None
                
                # 創建WebDriver
                driver = self._create_driver()
                
                if driver:
                    # 添加到驅動池
                    driver_id = str(id(driver))
                    self.drivers[driver_id] = driver
                    
                    # 更新統計信息
                    self.stats["total_drivers"] += 1
                    self.stats["active_drivers"] += 1
                    self.stats["last_update"] = datetime.now()
                    
                    self.logger.info(f"已創建WebDriver: {driver_id}")
                    return driver
                
                return None
                
        except Exception as e:
            self.logger.error(f"獲取WebDriver失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return None
    
    def release_driver(self, driver: webdriver.Chrome) -> bool:
        """
        釋放WebDriver實例
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否釋放成功
        """
        try:
            with self.driver_lock:
                driver_id = str(id(driver))
                
                if driver_id in self.drivers:
                    # 關閉WebDriver
                    driver.quit()
                    
                    # 從驅動池移除
                    del self.drivers[driver_id]
                    
                    # 更新統計信息
                    self.stats["active_drivers"] -= 1
                    self.stats["last_update"] = datetime.now()
                    
                    self.logger.info(f"已釋放WebDriver: {driver_id}")
                    return True
                
                self.logger.warning(f"WebDriver不存在: {driver_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"釋放WebDriver失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return False
    
    def _create_driver(self) -> Optional[webdriver.Chrome]:
        """
        創建WebDriver實例
        
        Returns:
            WebDriver實例
        """
        try:
            # 創建選項
            options = self._create_options()
            
            # 創建服務
            service = Service(ChromeDriverManager().install())
            
            # 創建WebDriver
            driver = webdriver.Chrome(
                service=service,
                options=options
            )
            
            # 設置超時
            driver.set_page_load_timeout(self.config.page_load_timeout)
            driver.set_script_timeout(self.config.script_timeout)
            driver.implicitly_wait(self.config.implicit_wait)
            
            return driver
            
        except Exception as e:
            self.logger.error(f"創建WebDriver失敗: {str(e)}")
            self.error_handler.handle_error(e)
            self.stats["failed_drivers"] += 1
            return None
    
    def _create_options(self) -> Options:
        """
        創建Chrome選項
        
        Returns:
            Chrome選項
        """
        try:
            options = Options()
            
            # 設置無頭模式
            if self.config.headless:
                options.add_argument("--headless")
            
            # 設置代理
            if self.config.proxy:
                options.add_argument(f"--proxy-server={self.config.proxy}")
            
            # 設置用戶代理
            if self.config.user_agent:
                options.add_argument(f"--user-agent={self.config.user_agent}")
            
            # 設置窗口大小
            options.add_argument(f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}")
            
            # 設置下載目錄
            if self.config.download_dir:
                options.add_argument(f"--download.default_directory={self.config.download_dir}")
            
            # 禁用圖片
            if self.config.disable_images:
                options.add_argument("--blink-settings=imagesEnabled=false")
            
            # 禁用JavaScript
            if self.config.disable_javascript:
                options.add_argument("--disable-javascript")
            
            # 禁用GPU
            if self.config.disable_gpu:
                options.add_argument("--disable-gpu")
            
            # 禁用沙箱
            if self.config.no_sandbox:
                options.add_argument("--no-sandbox")
            
            # 禁用/dev/shm使用
            if self.config.disable_dev_shm_usage:
                options.add_argument("--disable-dev-shm-usage")
            
            # 禁用擴展
            if self.config.disable_extensions:
                options.add_argument("--disable-extensions")
            
            # 禁用通知
            if self.config.disable_notifications:
                options.add_argument("--disable-notifications")
            
            # 禁用彈窗攔截
            if self.config.disable_popup_blocking:
                options.add_argument("--disable-popup-blocking")
            
            # 禁用自動化
            if self.config.disable_automation:
                options.add_argument("--disable-automation")
            
            # 禁用信息欄
            if self.config.disable_infobars:
                options.add_argument("--disable-infobars")
            
            # 禁用日誌
            if self.config.disable_logging:
                options.add_argument("--log-level=3")
            
            # 禁用Web安全
            if self.config.disable_web_security:
                options.add_argument("--disable-web-security")
            
            # 允許運行不安全內容
            if self.config.allow_running_insecure_content:
                options.add_argument("--allow-running-insecure-content")
            
            # 接受不安全證書
            if self.config.accept_insecure_certs:
                options.add_argument("--ignore-certificate-errors")
            
            # 設置語言
            options.add_argument(f"--lang={self.config.accept_language}")
            
            # 設置編碼
            options.add_argument(f"--accept-encoding={self.config.accept_encoding}")
            
            # 設置接受類型
            options.add_argument(f"--accept={self.config.accept}")
            
            # 啟用DNS預取
            if self.config.dns_prefetch:
                options.add_argument("--dns-prefetch")
            
            # 啟用預加載
            if self.config.preload:
                options.add_argument("--preload")
            
            # 設置磁盤緩存大小
            options.add_argument(f"--disk-cache-size={self.config.disk_cache_size}")
            
            # 設置內存緩存大小
            options.add_argument(f"--memory-cache-size={self.config.memory_cache_size}")
            
            # 設置最大連接數
            options.add_argument(f"--max-connections={self.config.max_connections}")
            
            # 設置每個主機的最大連接數
            options.add_argument(f"--max-connections-per-host={self.config.max_connections_per_host}")
            
            # 設置每個代理的最大連接數
            options.add_argument(f"--max-connections-per-proxy={self.config.max_connections_per_proxy}")
            
            return options
            
        except Exception as e:
            self.logger.error(f"創建Chrome選項失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return Options()
    
    def _cleanup_loop(self):
        """清理循環"""
        while True:
            try:
                time.sleep(self.config.cleanup_interval)
                
                with self.driver_lock:
                    # 清理過期的WebDriver
                    current_time = time.time()
                    expired_drivers = []
                    
                    for driver_id, driver in self.drivers.items():
                        try:
                            # 檢查WebDriver是否響應
                            driver.current_url
                        except:
                            expired_drivers.append(driver_id)
                    
                    # 關閉過期的WebDriver
                    for driver_id in expired_drivers:
                        try:
                            driver = self.drivers[driver_id]
                            driver.quit()
                            del self.drivers[driver_id]
                            
                            self.stats["active_drivers"] -= 1
                            self.stats["failed_drivers"] += 1
                            
                            self.logger.info(f"已清理過期WebDriver: {driver_id}")
                        except:
                            pass
                    
                    # 清理臨時文件
                    self._cleanup_temp_files()
                    
            except Exception as e:
                self.logger.error(f"清理循環異常: {str(e)}")
                self.error_handler.handle_error(e)
    
    def _cleanup_temp_files(self):
        """清理臨時文件"""
        try:
            # 獲取臨時文件列表
            temp_files = self.path_utils.list_files(self.temp_dir)
            
            # 刪除超過24小時的文件
            current_time = time.time()
            for file in temp_files:
                file_path = self.path_utils.join_path(self.temp_dir, file)
                file_time = self.path_utils.get_file_time(file_path)
                
                if current_time - file_time > 86400:  # 24小時
                    self.path_utils.remove_file(file_path)
                    
                    self.logger.info(f"已清理臨時文件: {file}")
                    
        except Exception as e:
            self.logger.error(f"清理臨時文件失敗: {str(e)}")
            self.error_handler.handle_error(e)
    
    def close_all(self):
        """關閉所有WebDriver"""
        try:
            with self.driver_lock:
                for driver_id, driver in list(self.drivers.items()):
                    try:
                        driver.quit()
                        del self.drivers[driver_id]
                        
                        self.stats["active_drivers"] -= 1
                        
                        self.logger.info(f"已關閉WebDriver: {driver_id}")
                    except:
                        pass
                
                self.stats["last_update"] = datetime.now()
                
        except Exception as e:
            self.logger.error(f"關閉所有WebDriver失敗: {str(e)}")
            self.error_handler.handle_error(e)
    
    def get_stats(self) -> Dict:
        """
        獲取統計信息
        
        Returns:
            統計信息
        """
        try:
            stats = self.stats.copy()
            
            # 計算運行時間
            stats["uptime"] = (datetime.now() - stats["start_time"]).total_seconds()
            
            # 計算成功率
            total_requests = stats["total_requests"]
            if total_requests > 0:
                stats["success_rate"] = (total_requests - stats["failed_requests"]) / total_requests
            else:
                stats["success_rate"] = 0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"獲取統計信息失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return {}
    
    def __del__(self):
        """析構函數"""
        try:
            self.close_all()
        except:
            pass
"""
代理管理模組

管理瀏覽器代理，以隱藏真實 IP
"""

import random
from typing import Dict, List, Optional, Union, Any
from selenium import webdriver
from selenium_base.core.logger import Logger
from selenium_base.anti_detection.base_manager import BaseManager
from selenium_base.anti_detection.base_error import ProxyError

class ProxyManager(BaseManager):
    """代理管理類別"""
    
    def __init__(self, driver: webdriver.Remote, config: Dict, logger: Optional[Logger] = None):
        """
        初始化代理管理類別
        
        Args:
            driver: 瀏覽器驅動程式
            config: 配置字典
            logger: 日誌記錄器
        """
        super().__init__(driver, config, logger)
        self.proxies = []
        self.current_proxy = None
        
    def setup(self) -> None:
        """設置代理環境"""
        if not self.is_enabled():
            return
            
        try:
            # 載入代理列表
            self._load_proxies()
            
            # 設置代理
            if self.config.get("rotate_proxy", False):
                self._rotate_proxy()
            else:
                self._set_proxy(self.config.get("proxy"))
                
            self.logger.info("代理設置完成")
        except Exception as e:
            self.logger.error(f"代理設置失敗: {str(e)}")
            raise ProxyError(f"代理設置失敗: {str(e)}")
            
    def cleanup(self) -> None:
        """清理代理環境"""
        if not self.is_enabled():
            return
            
        try:
            # 清除代理設置
            self._clear_proxy()
            self.logger.info("代理清理完成")
        except Exception as e:
            self.logger.error(f"代理清理失敗: {str(e)}")
            
    def _load_proxies(self) -> None:
        """載入代理列表"""
        try:
            proxy_list = self.config.get("proxy_list", [])
            if not proxy_list:
                return
                
            self.proxies = proxy_list
            self.logger.info(f"載入 {len(proxy_list)} 個代理")
            
        except Exception as e:
            self.logger.error(f"載入代理列表失敗: {str(e)}")
            raise ProxyError(f"載入代理列表失敗: {str(e)}")
            
    def _set_proxy(self, proxy: str) -> None:
        """
        設置代理
        
        Args:
            proxy: 代理地址
        """
        try:
            if not proxy:
                return
                
            # 設置代理
            self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {
                "userAgent": self.driver.execute_script("return navigator.userAgent")
            })
            
            self.driver.execute_cdp_cmd("Network.enable", {})
            self.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
                "headers": {"Proxy-Authorization": f"Basic {proxy}"}
            })
            
            self.current_proxy = proxy
            self.logger.info(f"設置代理: {proxy}")
            
        except Exception as e:
            self.logger.error(f"設置代理失敗: {str(e)}")
            raise ProxyError(f"設置代理失敗: {str(e)}")
            
    def _rotate_proxy(self) -> None:
        """輪換代理"""
        try:
            if not self.proxies:
                return
                
            # 隨機選擇代理
            proxy = random.choice(self.proxies)
            self._set_proxy(proxy)
            
        except Exception as e:
            self.logger.error(f"輪換代理失敗: {str(e)}")
            raise ProxyError(f"輪換代理失敗: {str(e)}")
            
    def _clear_proxy(self) -> None:
        """清除代理設置"""
        try:
            self.driver.execute_cdp_cmd("Network.disable", {})
            self.current_proxy = None
            self.logger.info("清除代理設置")
        except Exception as e:
            self.logger.error(f"清除代理設置失敗: {str(e)}")
            
    def get_current_proxy(self) -> Optional[str]:
        """
        獲取當前代理
        
        Returns:
            當前代理地址
        """
        return self.current_proxy
        
    def add_proxy(self, proxy: str) -> None:
        """
        添加代理
        
        Args:
            proxy: 代理地址
        """
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            self.logger.info(f"添加代理: {proxy}")
            
    def remove_proxy(self, proxy: str) -> None:
        """
        移除代理
        
        Args:
            proxy: 代理地址
        """
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            self.logger.info(f"移除代理: {proxy}")
            
    def clear_proxies(self) -> None:
        """清除所有代理"""
        self.proxies = []
        self.logger.info("清除所有代理")
        
    def test_proxy(self, proxy: str) -> bool:
        """
        測試代理是否可用
        
        Args:
            proxy: 代理地址
            
        Returns:
            代理是否可用
        """
        try:
            # 設置臨時代理
            self._set_proxy(proxy)
            
            # 訪問測試網站
            self.driver.get("https://api.ipify.org?format=json")
            
            # 檢查響應
            response = self.driver.find_element_by_tag_name("pre").text
            return "ip" in response
            
        except Exception as e:
            self.logger.error(f"測試代理失敗: {str(e)}")
            return False
        finally:
            # 恢復原代理
            self._set_proxy(self.current_proxy) 
"""
瀏覽器隱身管理模組
"""

import logging
from typing import Dict, Any, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

class StealthManager:
    """瀏覽器隱身管理器"""
    
    def __init__(self, logger=None):
        """
        初始化隱身管理器
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def apply_stealth_options(self, options: Union[ChromeOptions, FirefoxOptions, EdgeOptions], config: Dict[str, Any]):
        """
        應用隱身選項到瀏覽器選項中
        
        Args:
            options: 瀏覽器選項對象
            config: 隱身配置
        """
        if isinstance(options, ChromeOptions):
            self._apply_chrome_stealth_options(options, config)
        elif isinstance(options, FirefoxOptions):
            self._apply_firefox_stealth_options(options, config)
        elif isinstance(options, EdgeOptions):
            self._apply_edge_stealth_options(options, config)
    
    def _apply_chrome_stealth_options(self, options: ChromeOptions, config: Dict[str, Any]):
        """應用 Chrome 隱身選項"""
        # 禁用自動化控制特徵
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 移除自動化標記
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # 添加其他隱身選項
        if config.get("disable_webgl", False):
            options.add_argument("--disable-webgl")
        
        if config.get("disable_canvas", False):
            options.add_argument("--disable-canvas-aa")
            options.add_argument("--disable-2d-canvas-clip-aa")
            options.add_argument("--disable-gl-drawing-for-tests")
    
    def _apply_firefox_stealth_options(self, options: FirefoxOptions, config: Dict[str, Any]):
        """應用 Firefox 隱身選項"""
        # 禁用 WebDriver 標記
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        
        # 添加其他隱身選項
        if config.get("disable_webgl", False):
            options.set_preference("webgl.disabled", True)
        
        if config.get("disable_canvas", False):
            options.set_preference("canvas.capturestream.enabled", False)
    
    def _apply_edge_stealth_options(self, options: EdgeOptions, config: Dict[str, Any]):
        """應用 Edge 隱身選項"""
        # 禁用自動化控制特徵
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 移除自動化標記
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # 添加其他隱身選項
        if config.get("disable_webgl", False):
            options.add_argument("--disable-webgl")
        
        if config.get("disable_canvas", False):
            options.add_argument("--disable-canvas-aa")
            options.add_argument("--disable-2d-canvas-clip-aa")
            options.add_argument("--disable-gl-drawing-for-tests")
    
    def apply_stealth_scripts(self, driver: webdriver.Remote):
        """
        應用隱身 JavaScript 腳本
        
        Args:
            driver: WebDriver 實例
        """
        try:
            # 通用的 WebDriver 隱藏腳本
            stealth_script = """
            // 覆蓋 WebDriver 屬性
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
            
            // 移除 Automation 標記
            const originalHasAttribute = Element.prototype.hasAttribute;
            Element.prototype.hasAttribute = function(name) {
                if (name === 'webdriver') {
                    return false;
                }
                return originalHasAttribute.apply(this, arguments);
            };
            
            // 添加 Chrome 特有對象
            if (!window.chrome) {
                window.chrome = {};
            }
            
            // 添加 Plugins API
            if (!window.chrome.runtime) {
                window.chrome.runtime = {};
                window.chrome.runtime.sendMessage = function() {};
            }
            
            // 模擬Chrome插件
            if (!window.chrome.webstore) {
                window.chrome.webstore = {};
            }
            
            // 覆蓋 permissions API
            if (navigator.permissions) {
                const originalQuery = navigator.permissions.query;
                navigator.permissions.query = function(parameters) {
                    if (parameters.name === 'notifications') {
                        return Promise.resolve({state: Notification.permission, onchange: null});
                    }
                    return originalQuery.apply(navigator.permissions, arguments);
                };
            }
            """
            
            driver.execute_script(stealth_script)
            self.logger.debug("已應用防檢測腳本")
        except Exception as e:
            self.logger.warning(f"應用防檢測腳本失敗: {str(e)}") 
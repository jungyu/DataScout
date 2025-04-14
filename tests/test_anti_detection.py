"""
反檢測模組測試

測試反檢測相關功能，包括：
1. 瀏覽器指紋
2. 人類行為模擬
3. 代理管理
4. 請求控制
"""

import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.anti_detection.fingerprint import BrowserFingerprint
from src.anti_detection.human_behavior import HumanBehavior
from src.anti_detection.proxy_manager import ProxyManager
from src.anti_detection.request_controller import RequestController
from src.core.utils.browser_utils import BrowserUtils
from src.anti_detection.configs import (
    BrowserFingerprintConfig,
    HumanBehaviorConfig,
    WebGLConfig,
    CanvasConfig,
    AudioConfig,
    MouseConfig,
    KeyboardConfig,
    ScrollConfig,
    TimingConfig
)
import time

class TestAntiDetection(unittest.TestCase):
    """反檢測功能測試"""
    
    def setUp(self):
        """測試前準備"""
        chrome_options = Options()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # 初始化配置
        self.fingerprint_config = BrowserFingerprintConfig(
            webgl=WebGLConfig(),
            canvas=CanvasConfig(),
            audio=AudioConfig()
        )
        
        self.human_config = HumanBehaviorConfig(
            mouse=MouseConfig(),
            keyboard=KeyboardConfig(),
            scroll=ScrollConfig(),
            timing=TimingConfig()
        )
        
        # 初始化工具類
        self.browser_utils = BrowserUtils(self.driver)
        self.browser_fingerprint = BrowserFingerprint(self.driver, self.fingerprint_config)
        self.human_behavior = HumanBehavior(self.driver, self.human_config)
        self.proxy_manager = ProxyManager()
        self.request_controller = RequestController()

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_navigator_webdriver(self):
        """測試 navigator.webdriver 屬性是否被正確隱藏"""
        self.driver.get('about:blank')
        webdriver_present = self.driver.execute_script('return navigator.webdriver')
        self.assertFalse(webdriver_present, "navigator.webdriver 屬性未被正確隱藏")

    def test_browser_fingerprint(self):
        """測試瀏覽器指紋"""
        fingerprint = self.browser_fingerprint.generate()
        self.assertIsNotNone(fingerprint)
        self.assertTrue(self.browser_fingerprint.validate())

    def test_human_behavior(self):
        """測試人類行為模擬"""
        behavior = self.human_behavior.simulate()
        self.assertIsNotNone(behavior)

    def test_proxy_manager(self):
        """測試代理管理"""
        proxy = self.proxy_manager.get_proxy()
        self.assertIsNotNone(proxy)

    def test_request_controller(self):
        """測試請求控制"""
        self.request_controller.add_request()
        self.assertTrue(self.request_controller.can_request())

    def test_browser_utils(self):
        """測試瀏覽器工具類功能"""
        self.driver.get('https://example.com')
        
        # 測試元素等待
        element = self.browser_utils.wait_for_element(By.TAG_NAME, 'body')
        self.assertIsNotNone(element, "元素等待失敗")
        
        # 測試安全點擊
        try:
            self.browser_utils.safe_click(element)
        except Exception as e:
            self.fail(f"安全點擊失敗: {str(e)}")
        
        # 測試頁面加載等待
        try:
            self.browser_utils.wait_for_page_load()
        except Exception as e:
            self.fail(f"頁面加載等待失敗: {str(e)}")

if __name__ == '__main__':
    unittest.main()

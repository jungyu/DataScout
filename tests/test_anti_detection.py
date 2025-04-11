import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.anti_detection.utils.browser_fingerprint import BrowserFingerprint
from src.anti_detection.utils.human_behavior import HumanBehavior
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
    def setUp(self):
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

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_navigator_webdriver(self):
        """測試 navigator.webdriver 屬性是否被正確隱藏"""
        self.driver.get('about:blank')
        webdriver_present = self.driver.execute_script('return navigator.webdriver')
        self.assertFalse(webdriver_present, "navigator.webdriver 屬性未被正確隱藏")

    def test_browser_fingerprint(self):
        """測試瀏覽器指紋功能"""
        self.driver.get('https://bot.sannysoft.com')
        
        # 測試 WebGL 指紋
        webgl_fingerprint = self.browser_fingerprint.get_webgl_fingerprint()
        self.assertIsNotNone(webgl_fingerprint, "WebGL 指紋獲取失敗")
        self.assertIsInstance(webgl_fingerprint, dict, "WebGL 指紋格式不正確")
        
        # 測試 Canvas 指紋
        canvas_fingerprint = self.browser_fingerprint.get_canvas_fingerprint()
        self.assertIsNotNone(canvas_fingerprint, "Canvas 指紋獲取失敗")
        self.assertIsInstance(canvas_fingerprint, str, "Canvas 指紋格式不正確")
        
        # 測試 Audio 指紋
        audio_fingerprint = self.browser_fingerprint.get_audio_fingerprint()
        self.assertIsNotNone(audio_fingerprint, "Audio 指紋獲取失敗")
        self.assertIsInstance(audio_fingerprint, str, "Audio 指紋格式不正確")

    def test_human_behavior(self):
        """測試人類行為模擬功能"""
        self.driver.get('https://example.com')
        
        # 測試隨機滾動
        initial_scroll = self.driver.execute_script('return window.pageYOffset')
        self.human_behavior.random_scroll()
        final_scroll = self.driver.execute_script('return window.pageYOffset')
        self.assertNotEqual(initial_scroll, final_scroll, "頁面滾動未生效")
        
        # 測試隨機移動
        element = self.browser_utils.wait_for_element(By.TAG_NAME, 'body')
        self.human_behavior.random_mouse_movement(element)
        
        # 測試隨機暫停
        start_time = time.time()
        self.human_behavior.random_pause()
        end_time = time.time()
        self.assertGreater(end_time - start_time, 0, "隨機暫停未生效")

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

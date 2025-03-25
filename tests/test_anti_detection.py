import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestAntiDetection(unittest.TestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_navigator_webdriver(self):
        self.driver.get('about:blank')
        webdriver_present = self.driver.execute_script('return navigator.webdriver')
        self.assertFalse(webdriver_present)

if __name__ == '__main__':
    unittest.main()

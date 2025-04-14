"""
瀏覽器工具測試模組

此模組提供了瀏覽器工具的測試案例，包含以下功能：
- 瀏覽器配置測試
- 瀏覽器操作測試
- 頁面等待測試
- 元素定位測試
"""

import time
import pytest
from unittest.mock import MagicMock, patch

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from selenium_base.core.config import BaseConfig
from selenium_base.utils.browser import BrowserProfile, BrowserUtils

@pytest.fixture
def config():
    """建立測試用的配置物件"""
    config = BaseConfig()
    config.browser.headless = True
    config.browser.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    config.browser.language = "zh-TW"
    config.browser.timezone = "Asia/Taipei"
    config.browser.geolocation = {"latitude": 25.0330, "longitude": 121.5654}
    config.browser.proxy = "http://127.0.0.1:8080"
    config.browser.proxy_username = "user"
    config.browser.proxy_password = "pass"
    config.browser.extensions = ["extension1.crx", "extension2.crx"]
    return config

@pytest.fixture
def profile(config):
    """建立測試用的瀏覽器配置服務"""
    return BrowserProfile(config)

@pytest.fixture
def utils():
    """建立測試用的瀏覽器工具"""
    return BrowserUtils()

@pytest.fixture
def driver():
    """建立測試用的瀏覽器驅動程式"""
    driver = MagicMock()
    driver.execute_script.return_value = None
    driver.get_cookies.return_value = []
    driver.add_cookie.return_value = None
    driver.delete_cookie.return_value = None
    driver.delete_all_cookies.return_value = None
    driver.switch_to.alert.accept.return_value = None
    driver.switch_to.alert.dismiss.return_value = None
    driver.switch_to.alert.text = "test"
    driver.switch_to.alert.send_keys.return_value = None
    return driver

def test_wait_for_element_by_id(utils, driver):
    """測試等待 ID 元素"""
    # 設定元素
    element = MagicMock()
    driver.find_element.return_value = element
    
    # 等待元素
    result = utils.wait_for_element(driver, By.ID, "test", timeout=10)
    
    # 檢查元素
    assert result == element
    driver.find_element.assert_called_once_with(By.ID, "test")

def test_wait_for_element_by_name(utils, driver):
    """測試等待名稱元素"""
    # 設定元素
    element = MagicMock()
    driver.find_element.return_value = element
    
    # 等待元素
    result = utils.wait_for_element(driver, By.NAME, "test", timeout=10)
    
    # 檢查元素
    assert result == element
    driver.find_element.assert_called_once_with(By.NAME, "test")

def test_wait_for_element_by_class(utils, driver):
    """測試等待類別元素"""
    # 設定元素
    element = MagicMock()
    driver.find_element.return_value = element
    
    # 等待元素
    result = utils.wait_for_element(driver, By.CLASS_NAME, "test", timeout=10)
    
    # 檢查元素
    assert result == element
    driver.find_element.assert_called_once_with(By.CLASS_NAME, "test")

def test_wait_for_element_by_tag(utils, driver):
    """測試等待標籤元素"""
    # 設定元素
    element = MagicMock()
    driver.find_element.return_value = element
    
    # 等待元素
    result = utils.wait_for_element(driver, By.TAG_NAME, "test", timeout=10)
    
    # 檢查元素
    assert result == element
    driver.find_element.assert_called_once_with(By.TAG_NAME, "test")

def test_wait_for_element_by_xpath(utils, driver):
    """測試等待 XPath 元素"""
    # 設定元素
    element = MagicMock()
    driver.find_element.return_value = element
    
    # 等待元素
    result = utils.wait_for_element(driver, By.XPATH, "//test", timeout=10)
    
    # 檢查元素
    assert result == element
    driver.find_element.assert_called_once_with(By.XPATH, "//test")

def test_wait_for_element_by_css(utils, driver):
    """測試等待 CSS 元素"""
    # 設定元素
    element = MagicMock()
    driver.find_element.return_value = element
    
    # 等待元素
    result = utils.wait_for_element(driver, By.CSS_SELECTOR, "test", timeout=10)
    
    # 檢查元素
    assert result == element
    driver.find_element.assert_called_once_with(By.CSS_SELECTOR, "test")

def test_wait_for_element_by_link(utils, driver):
    """測試等待連結元素"""
    # 設定元素
    element = MagicMock()
    driver.find_element.return_value = element
    
    # 等待元素
    result = utils.wait_for_element(driver, By.LINK_TEXT, "test", timeout=10)
    
    # 檢查元素
    assert result == element
    driver.find_element.assert_called_once_with(By.LINK_TEXT, "test")

def test_wait_for_element_by_partial_link(utils, driver):
    """測試等待部分連結元素"""
    # 設定元素
    element = MagicMock()
    driver.find_element.return_value = element
    
    # 等待元素
    result = utils.wait_for_element(driver, By.PARTIAL_LINK_TEXT, "test", timeout=10)
    
    # 檢查元素
    assert result == element
    driver.find_element.assert_called_once_with(By.PARTIAL_LINK_TEXT, "test")

def test_wait_for_element_timeout(utils, driver):
    """測試等待元素超時"""
    # 設定元素不存在
    driver.find_element.side_effect = NoSuchElementException()
    
    # 等待元素
    with pytest.raises(TimeoutException):
        utils.wait_for_element(driver, By.ID, "test", timeout=1)

def test_wait_for_elements(utils, driver):
    """測試等待多個元素"""
    # 設定元素
    elements = [MagicMock(), MagicMock()]
    driver.find_elements.return_value = elements
    
    # 等待元素
    result = utils.wait_for_elements(driver, By.CLASS_NAME, "test", timeout=10)
    
    # 檢查元素
    assert result == elements
    driver.find_elements.assert_called_once_with(By.CLASS_NAME, "test")

def test_wait_for_elements_timeout(utils, driver):
    """測試等待多個元素超時"""
    # 設定元素不存在
    driver.find_elements.return_value = []
    
    # 等待元素
    with pytest.raises(TimeoutException):
        utils.wait_for_elements(driver, By.CLASS_NAME, "test", timeout=1)

def test_scroll_to_element(utils, driver):
    """測試捲動到元素"""
    # 設定元素
    element = MagicMock()
    
    # 捲動到元素
    utils.scroll_to_element(driver, element)
    
    # 檢查捲動
    driver.execute_script.assert_called_once()

def test_scroll_to_bottom(utils, driver):
    """測試捲動到底部"""
    # 捲動到底部
    utils.scroll_to_bottom(driver)
    
    # 檢查捲動
    driver.execute_script.assert_called_once()

def test_take_screenshot(utils, driver, tmp_path):
    """測試截圖"""
    # 設定截圖
    driver.get_screenshot_as_png.return_value = b"test"
    
    # 截圖
    path = tmp_path / "test.png"
    utils.take_screenshot(driver, path)
    
    # 檢查截圖
    assert path.exists()
    assert path.read_bytes() == b"test"

def test_get_cookies(utils, driver):
    """測試取得 Cookie"""
    # 設定 Cookie
    cookies = [{"name": "test", "value": "test"}]
    driver.get_cookies.return_value = cookies
    
    # 取得 Cookie
    result = utils.get_cookies(driver)
    
    # 檢查 Cookie
    assert result == cookies
    driver.get_cookies.assert_called_once()

def test_add_cookie(utils, driver):
    """測試新增 Cookie"""
    # 新增 Cookie
    utils.add_cookie(driver, "test", "test")
    
    # 檢查 Cookie
    driver.add_cookie.assert_called_once_with({"name": "test", "value": "test"})

def test_delete_cookie(utils, driver):
    """測試刪除 Cookie"""
    # 刪除 Cookie
    utils.delete_cookie(driver, "test")
    
    # 檢查 Cookie
    driver.delete_cookie.assert_called_once_with("test")

def test_clear_cookies(utils, driver):
    """測試清除 Cookie"""
    # 清除 Cookie
    utils.clear_cookies(driver)
    
    # 檢查 Cookie
    driver.delete_all_cookies.assert_called_once()

def test_handle_alert_accept(utils, driver):
    """測試處理警告接受"""
    # 處理警告
    utils.handle_alert(driver, accept=True)
    
    # 檢查警告
    driver.switch_to.alert.accept.assert_called_once()

def test_handle_alert_dismiss(utils, driver):
    """測試處理警告取消"""
    # 處理警告
    utils.handle_alert(driver, accept=False)
    
    # 檢查警告
    driver.switch_to.alert.dismiss.assert_called_once()

def test_handle_alert_text(utils, driver):
    """測試處理警告文字"""
    # 處理警告
    result = utils.handle_alert(driver, text=True)
    
    # 檢查警告
    assert result == "test"
    driver.switch_to.alert.text.assert_called_once()

def test_handle_alert_input(utils, driver):
    """測試處理警告輸入"""
    # 處理警告
    utils.handle_alert(driver, input_text="test")
    
    # 檢查警告
    driver.switch_to.alert.send_keys.assert_called_once_with("test") 
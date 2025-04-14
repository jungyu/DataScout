"""
瀏覽器配置模組測試

測試瀏覽器配置類別的各項功能
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from datascout_core.core.browser import Browser
from datascout_core.core.exceptions import BrowserError

@pytest.fixture
def chrome_config():
    """Chrome瀏覽器配置"""
    return {
        'type': 'chrome',
        'headless': True,
        'window_size': {'width': 1920, 'height': 1080},
        'proxy': 'http://127.0.0.1:8080',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'language': 'zh-TW',
        'timezone': 'Asia/Taipei',
        'geolocation': {'latitude': 25.0330, 'longitude': 121.5654},
        'options': ['--disable-gpu', '--no-sandbox'],
        'page_load_timeout': 30,
        'implicit_wait': 10
    }

@pytest.fixture
def firefox_config():
    """Firefox瀏覽器配置"""
    return {
        'type': 'firefox',
        'headless': True,
        'window_size': {'width': 1920, 'height': 1080},
        'proxy': 'http://127.0.0.1:8080',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'language': 'zh-TW',
        'timezone': 'Asia/Taipei',
        'geolocation': {'latitude': 25.0330, 'longitude': 121.5654},
        'options': ['--disable-gpu', '--no-sandbox'],
        'page_load_timeout': 30,
        'implicit_wait': 10
    }

@pytest.fixture
def edge_config():
    """Edge瀏覽器配置"""
    return {
        'type': 'edge',
        'headless': True,
        'window_size': {'width': 1920, 'height': 1080},
        'proxy': 'http://127.0.0.1:8080',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        'language': 'zh-TW',
        'timezone': 'Asia/Taipei',
        'geolocation': {'latitude': 25.0330, 'longitude': 121.5654},
        'options': ['--disable-gpu', '--no-sandbox'],
        'page_load_timeout': 30,
        'implicit_wait': 10
    }

@pytest.fixture
def safari_config():
    """Safari瀏覽器配置"""
    return {
        'type': 'safari',
        'headless': True,
        'window_size': {'width': 1920, 'height': 1080},
        'proxy': 'http://127.0.0.1:8080',
        'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'language': 'zh-TW',
        'timezone': 'Asia/Taipei',
        'geolocation': {'latitude': 25.0330, 'longitude': 121.5654},
        'options': ['--disable-gpu', '--no-sandbox'],
        'page_load_timeout': 30,
        'implicit_wait': 10
    }

def test_init_chrome(chrome_config):
    """測試初始化Chrome瀏覽器"""
    browser = Browser(chrome_config)
    assert browser.config == chrome_config
    assert isinstance(browser.options, ChromeOptions)
    assert browser.driver is None

def test_init_firefox(firefox_config):
    """測試初始化Firefox瀏覽器"""
    browser = Browser(firefox_config)
    assert browser.config == firefox_config
    assert isinstance(browser.options, FirefoxOptions)
    assert browser.driver is None

def test_init_edge(edge_config):
    """測試初始化Edge瀏覽器"""
    browser = Browser(edge_config)
    assert browser.config == edge_config
    assert isinstance(browser.options, EdgeOptions)
    assert browser.driver is None

def test_init_safari(safari_config):
    """測試初始化Safari瀏覽器"""
    browser = Browser(safari_config)
    assert browser.config == safari_config
    assert isinstance(browser.options, SafariOptions)
    assert browser.driver is None

def test_init_invalid_browser():
    """測試初始化無效的瀏覽器"""
    config = {'type': 'invalid'}
    with pytest.raises(BrowserError):
        Browser(config)

def test_configure_options(chrome_config):
    """測試設定瀏覽器選項"""
    browser = Browser(chrome_config)
    
    # 檢查無頭模式
    assert '--headless' in browser.options.arguments
    
    # 檢查視窗大小
    assert f'--window-size={chrome_config["window_size"]["width"]},{chrome_config["window_size"]["height"]}' in browser.options.arguments
    
    # 檢查代理
    assert f'--proxy-server={chrome_config["proxy"]}' in browser.options.arguments
    
    # 檢查使用者代理
    assert f'--user-agent={chrome_config["user_agent"]}' in browser.options.arguments
    
    # 檢查語言
    assert f'--lang={chrome_config["language"]}' in browser.options.arguments
    
    # 檢查時區
    assert f'--timezone={chrome_config["timezone"]}' in browser.options.arguments
    
    # 檢查地理位置
    assert f'--geolocation={chrome_config["geolocation"]["latitude"]},{chrome_config["geolocation"]["longitude"]}' in browser.options.arguments
    
    # 檢查其他選項
    for option in chrome_config['options']:
        assert option in browser.options.arguments

@patch('selenium.webdriver.Chrome')
def test_start_chrome(mock_chrome, chrome_config):
    """測試啟動Chrome瀏覽器"""
    browser = Browser(chrome_config)
    browser.start()
    
    # 檢查驅動程式是否建立
    assert browser.driver is not None
    
    # 檢查頁面載入超時設定
    browser.driver.set_page_load_timeout.assert_called_with(chrome_config['page_load_timeout'])
    
    # 檢查隱式等待設定
    browser.driver.implicitly_wait.assert_called_with(chrome_config['implicit_wait'])

@patch('selenium.webdriver.Firefox')
def test_start_firefox(mock_firefox, firefox_config):
    """測試啟動Firefox瀏覽器"""
    browser = Browser(firefox_config)
    browser.start()
    
    # 檢查驅動程式是否建立
    assert browser.driver is not None
    
    # 檢查頁面載入超時設定
    browser.driver.set_page_load_timeout.assert_called_with(firefox_config['page_load_timeout'])
    
    # 檢查隱式等待設定
    browser.driver.implicitly_wait.assert_called_with(firefox_config['implicit_wait'])

@patch('selenium.webdriver.Edge')
def test_start_edge(mock_edge, edge_config):
    """測試啟動Edge瀏覽器"""
    browser = Browser(edge_config)
    browser.start()
    
    # 檢查驅動程式是否建立
    assert browser.driver is not None
    
    # 檢查頁面載入超時設定
    browser.driver.set_page_load_timeout.assert_called_with(edge_config['page_load_timeout'])
    
    # 檢查隱式等待設定
    browser.driver.implicitly_wait.assert_called_with(edge_config['implicit_wait'])

@patch('selenium.webdriver.Safari')
def test_start_safari(mock_safari, safari_config):
    """測試啟動Safari瀏覽器"""
    browser = Browser(safari_config)
    browser.start()
    
    # 檢查驅動程式是否建立
    assert browser.driver is not None
    
    # 檢查頁面載入超時設定
    browser.driver.set_page_load_timeout.assert_called_with(safari_config['page_load_timeout'])
    
    # 檢查隱式等待設定
    browser.driver.implicitly_wait.assert_called_with(safari_config['implicit_wait'])

def test_stop(chrome_config):
    """測試停止瀏覽器"""
    browser = Browser(chrome_config)
    browser.driver = MagicMock()
    browser.stop()
    
    # 檢查驅動程式是否停止
    browser.driver.quit.assert_called_once()
    assert browser.driver is None

def test_get_driver_not_started(chrome_config):
    """測試取得未啟動的瀏覽器驅動程式"""
    browser = Browser(chrome_config)
    
    with pytest.raises(BrowserError):
        browser.get_driver()

def test_get_driver_started(chrome_config):
    """測試取得已啟動的瀏覽器驅動程式"""
    browser = Browser(chrome_config)
    browser.driver = MagicMock()
    
    driver = browser.get_driver()
    assert driver == browser.driver

def test_add_extension(chrome_config, tmp_path):
    """測試添加擴充功能"""
    browser = Browser(chrome_config)
    
    # 建立測試擴充功能檔案
    extension_path = os.path.join(tmp_path, 'test.crx')
    with open(extension_path, 'w') as f:
        f.write('test')
    
    # 測試添加擴充功能
    browser.add_extension(extension_path)
    
    # 檢查擴充功能是否添加
    assert extension_path in browser.options.extensions
    
    # 測試添加不存在的擴充功能
    with pytest.raises(BrowserError):
        browser.add_extension('nonexistent.crx')

def test_add_argument(chrome_config):
    """測試添加瀏覽器參數"""
    browser = Browser(chrome_config)
    
    # 測試添加瀏覽器參數
    browser.add_argument('--test')
    
    # 檢查參數是否添加
    assert '--test' in browser.options.arguments

def test_add_experimental_option(chrome_config):
    """測試添加實驗性選項"""
    browser = Browser(chrome_config)
    
    # 測試添加實驗性選項
    browser.add_experimental_option('test', 'value')
    
    # 檢查選項是否添加
    assert browser.options.experimental_options['test'] == 'value'

def test_set_preference(chrome_config):
    """測試設定偏好設定"""
    browser = Browser(chrome_config)
    
    # 測試設定偏好設定
    browser.set_preference('test', 'value')
    
    # 檢查偏好設定是否設定
    assert browser.options.preferences['test'] == 'value'

def test_context_manager(chrome_config):
    """測試上下文管理器"""
    with patch('selenium.webdriver.Chrome') as mock_chrome:
        with Browser(chrome_config) as browser:
            # 檢查瀏覽器是否啟動
            assert browser.driver is not None
            
            # 檢查驅動程式是否建立
            mock_chrome.assert_called_once()
        
        # 檢查瀏覽器是否停止
        browser.driver.quit.assert_called_once()
        assert browser.driver is None 
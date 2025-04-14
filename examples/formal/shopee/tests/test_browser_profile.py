"""
瀏覽器配置測試模組

此模組提供以下測試：
- 瀏覽器配置初始化測試
- 視窗大小設定測試
- 語言設定測試
- 時區設定測試
- 地理位置模擬測試
- 代理設定測試
- 擴充功能管理測試
"""

import pytest
from unittest.mock import Mock, patch

from core.browser_profile import BrowserProfile
from config import BaseConfig

@pytest.fixture
def config():
    """建立測試用的配置物件"""
    return BaseConfig()

@pytest.fixture
def browser_profile(config):
    """建立測試用的瀏覽器配置物件"""
    return BrowserProfile(config)

def test_init(browser_profile, config):
    """測試瀏覽器配置初始化"""
    assert browser_profile.config == config
    assert browser_profile.options is not None

def test_setup_window_size(browser_profile):
    """測試視窗大小設定"""
    with patch.object(browser_profile, 'options') as mock_options:
        browser_profile._setup_window_size()
        mock_options.add_argument.assert_called_with("--window-size=1920,1080")

def test_setup_language(browser_profile):
    """測試語言設定"""
    with patch.object(browser_profile, 'options') as mock_options:
        browser_profile._setup_language()
        mock_options.add_argument.assert_called_with("--lang=zh-TW")

def test_setup_timezone(browser_profile):
    """測試時區設定"""
    with patch.object(browser_profile, 'options') as mock_options:
        browser_profile._setup_timezone()
        mock_options.add_argument.assert_called_with("--timezone=Asia/Taipei")

def test_setup_geolocation(browser_profile):
    """測試地理位置模擬"""
    with patch.object(browser_profile, 'options') as mock_options:
        browser_profile._setup_geolocation()
        mock_options.add_argument.assert_called_with("--geolocation=25.0330,121.5654")

def test_setup_proxy(browser_profile):
    """測試代理設定"""
    with patch.object(browser_profile, 'options') as mock_options:
        browser_profile._setup_proxy()
        # 預設情況下不應該設定代理
        mock_options.add_argument.assert_not_called()

def test_setup_extensions(browser_profile):
    """測試擴充功能管理"""
    with patch.object(browser_profile, 'options') as mock_options:
        browser_profile._setup_extensions()
        # 預設情況下不應該載入擴充功能
        mock_options.add_extension.assert_not_called()

def test_get_options(browser_profile):
    """測試獲取選項"""
    options = browser_profile.get_options()
    assert options == browser_profile.options 
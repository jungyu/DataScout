"""
瀏覽器配置服務測試模組

此模組提供了瀏覽器配置服務的測試案例，包含以下功能：
- 瀏覽器選項設定測試
- 瀏覽器驅動程式建立測試
- 擴充功能管理測試
- 代理伺服器設定測試
"""

import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver

from selenium_base.core.config import BaseConfig
from selenium_base.services.browser_profile import BrowserProfile

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

def test_create_options(profile):
    """測試建立瀏覽器選項"""
    options = profile.create_options()
    
    # 檢查選項類型
    assert isinstance(options, Options)
    
    # 檢查無頭模式
    assert "--headless" in options.arguments
    
    # 檢查使用者代理
    assert any("--user-agent=Mozilla/5.0" in arg for arg in options.arguments)
    
    # 檢查語言設定
    assert any("--lang=zh-TW" in arg for arg in options.arguments)
    
    # 檢查時區設定
    assert any("--timezone=Asia/Taipei" in arg for arg in options.arguments)
    
    # 檢查地理位置設定
    assert any("--geolocation=25.0330,121.5654" in arg for arg in options.arguments)
    
    # 檢查代理伺服器設定
    assert any("--proxy-server=http://127.0.0.1:8080" in arg for arg in options.arguments)
    assert any("--proxy-auth=user:pass" in arg for arg in options.arguments)

def test_create_driver(profile):
    """測試建立瀏覽器驅動程式"""
    with patch("selenium.webdriver.chrome.webdriver.WebDriver") as mock_driver:
        driver = profile.create_driver()
        
        # 檢查驅動程式類型
        assert isinstance(driver, WebDriver)
        
        # 檢查服務設定
        assert isinstance(driver.service, Service)
        
        # 檢查選項設定
        assert isinstance(driver.options, Options)

def test_add_extensions(profile, tmp_path):
    """測試新增擴充功能"""
    # 建立測試用的擴充功能檔案
    extension1 = tmp_path / "extension1.crx"
    extension2 = tmp_path / "extension2.crx"
    extension1.write_bytes(b"test1")
    extension2.write_bytes(b"test2")
    
    # 設定擴充功能路徑
    profile.config.browser.extensions = [str(extension1), str(extension2)]
    
    # 建立選項
    options = Options()
    
    # 新增擴充功能
    profile.add_extensions(options)
    
    # 檢查擴充功能是否已新增
    assert len(options.extensions) == 2
    assert any(str(extension1) in str(ext) for ext in options.extensions)
    assert any(str(extension2) in str(ext) for ext in options.extensions)

def test_set_proxy(profile):
    """測試設定代理伺服器"""
    # 建立選項
    options = Options()
    
    # 設定代理伺服器
    profile.set_proxy(options)
    
    # 檢查代理伺服器設定
    assert any("--proxy-server=http://127.0.0.1:8080" in arg for arg in options.arguments)
    assert any("--proxy-auth=user:pass" in arg for arg in options.arguments)

def test_set_user_agent(profile):
    """測試設定使用者代理"""
    # 建立選項
    options = Options()
    
    # 設定使用者代理
    profile.set_user_agent(options)
    
    # 檢查使用者代理設定
    assert any("--user-agent=Mozilla/5.0" in arg for arg in options.arguments)

def test_set_language(profile):
    """測試設定語言"""
    # 建立選項
    options = Options()
    
    # 設定語言
    profile.set_language(options)
    
    # 檢查語言設定
    assert any("--lang=zh-TW" in arg for arg in options.arguments)

def test_set_timezone(profile):
    """測試設定時區"""
    # 建立選項
    options = Options()
    
    # 設定時區
    profile.set_timezone(options)
    
    # 檢查時區設定
    assert any("--timezone=Asia/Taipei" in arg for arg in options.arguments)

def test_set_geolocation(profile):
    """測試設定地理位置"""
    # 建立選項
    options = Options()
    
    # 設定地理位置
    profile.set_geolocation(options)
    
    # 檢查地理位置設定
    assert any("--geolocation=25.0330,121.5654" in arg for arg in options.arguments)

def test_set_webgl(profile):
    """測試設定 WebGL"""
    # 建立選項
    options = Options()
    
    # 設定 WebGL
    profile.set_webgl(options)
    
    # 檢查 WebGL 設定
    assert any("--webgl-vendor=Google Inc." in arg for arg in options.arguments)
    assert any("--webgl-renderer=ANGLE" in arg for arg in options.arguments)
    assert any("--webgl-version=WebGL GLSL ES 1.0" in arg for arg in options.arguments)
    assert any("--webgl-shading-language-version=WebGL GLSL ES 1.0" in arg for arg in options.arguments)
    assert any("--webgl-extensions=ANGLE_instanced_arrays" in arg for arg in options.arguments)

def test_set_audio(profile):
    """測試設定音訊"""
    # 建立選項
    options = Options()
    
    # 設定音訊
    profile.set_audio(options)
    
    # 檢查音訊設定
    assert any("--audio-sample-rate=44100" in arg for arg in options.arguments)
    assert any("--audio-channel-count=2" in arg for arg in options.arguments)
    assert any("--audio-buffer-size=4096" in arg for arg in options.arguments)

def test_set_canvas(profile):
    """測試設定 Canvas"""
    # 建立選項
    options = Options()
    
    # 設定 Canvas
    profile.set_canvas(options)
    
    # 檢查 Canvas 設定
    assert any("--canvas-noise=0.1" in arg for arg in options.arguments)
    assert any("--canvas-mode=source-over" in arg for arg in options.arguments)

def test_set_fonts(profile):
    """測試設定字體"""
    # 建立選項
    options = Options()
    
    # 設定字體
    profile.set_fonts(options)
    
    # 檢查字體設定
    assert any("--font-family=Arial" in arg for arg in options.arguments)
    assert any("--font-size=12" in arg for arg in options.arguments)

def test_set_platform(profile):
    """測試設定平台"""
    # 建立選項
    options = Options()
    
    # 設定平台
    profile.set_platform(options)
    
    # 檢查平台設定
    assert any("--platform-os=Windows" in arg for arg in options.arguments)
    assert any("--platform-arch=x64" in arg for arg in options.arguments)
    assert any("--platform-version=10.0.0" in arg for arg in options.arguments)

def test_set_hardware(profile):
    """測試設定硬體"""
    # 建立選項
    options = Options()
    
    # 設定硬體
    profile.set_hardware(options)
    
    # 檢查硬體設定
    assert any("--hardware-cpu-cores=4" in arg for arg in options.arguments)
    assert any("--hardware-memory=8" in arg for arg in options.arguments)
    assert any("--hardware-gpu=enabled" in arg for arg in options.arguments)

def test_set_screen(profile):
    """測試設定螢幕"""
    # 建立選項
    options = Options()
    
    # 設定螢幕
    profile.set_screen(options)
    
    # 檢查螢幕設定
    assert any("--window-size=1920,1080" in arg for arg in options.arguments)
    assert any("--screen-color-depth=24" in arg for arg in options.arguments)
    assert any("--screen-pixel-ratio=1" in arg for arg in options.arguments)

def test_set_touch(profile):
    """測試設定觸控"""
    # 建立選項
    options = Options()
    
    # 設定觸控
    profile.set_touch(options)
    
    # 檢查觸控設定
    assert any("--enable-touch-events" in arg for arg in options.arguments)
    assert any("--touch-points=5" in arg for arg in options.arguments) 
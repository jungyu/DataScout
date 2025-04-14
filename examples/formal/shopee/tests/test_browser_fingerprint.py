"""
瀏覽器指紋測試模組

此模組提供以下測試：
- 瀏覽器指紋初始化測試
- WebGL 參數修改測試
- Canvas 指紋偽裝測試
- 音訊指紋偽裝測試
- 字體列表偽裝測試
- WebRTC 設定測試
- 硬體並行度偽裝測試
- 時區設定測試
- 語言設定測試
"""

import pytest
from unittest.mock import Mock, patch

from core.browser_fingerprint import BrowserFingerprint
from config import BaseConfig

@pytest.fixture
def config():
    """建立測試用的配置物件"""
    return BaseConfig()

@pytest.fixture
def browser_fingerprint(config):
    """建立測試用的瀏覽器指紋物件"""
    return BrowserFingerprint(config)

def test_init(browser_fingerprint, config):
    """測試瀏覽器指紋初始化"""
    assert browser_fingerprint.config == config
    assert browser_fingerprint.webgl_params is not None
    assert browser_fingerprint.canvas_noise is not None
    assert browser_fingerprint.audio_params is not None
    assert browser_fingerprint.font_list is not None
    assert browser_fingerprint.webrtc_config is not None
    assert browser_fingerprint.hardware_config is not None

def test_modify_webgl_params(browser_fingerprint):
    """測試 WebGL 參數修改"""
    # 模擬 WebGL 參數
    browser_fingerprint.webgl_params = {
        "vendor": "Google Inc.",
        "renderer": "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)",
        "webgl_version": "WebGL 1.0",
        "shading_language_version": "WebGL GLSL ES 1.0"
    }
    
    # 修改 WebGL 參數
    script = browser_fingerprint._modify_webgl_params()
    
    # 檢查腳本
    assert "getParameter" in script
    assert "vendor" in script
    assert "renderer" in script
    assert "webgl_version" in script
    assert "shading_language_version" in script

def test_spoof_canvas_fingerprint(browser_fingerprint):
    """測試 Canvas 指紋偽裝"""
    # 模擬 Canvas 雜訊
    browser_fingerprint.canvas_noise = {
        "noise_level": 0.1,
        "pattern": "random"
    }
    
    # 偽裝 Canvas 指紋
    script = browser_fingerprint._spoof_canvas_fingerprint()
    
    # 檢查腳本
    assert "getContext" in script
    assert "toDataURL" in script
    assert "noise_level" in script
    assert "pattern" in script

def test_spoof_audio_fingerprint(browser_fingerprint):
    """測試音訊指紋偽裝"""
    # 模擬音訊參數
    browser_fingerprint.audio_params = {
        "sample_rate": 44100,
        "channel_count": 2,
        "buffer_size": 4096
    }
    
    # 偽裝音訊指紋
    script = browser_fingerprint._spoof_audio_fingerprint()
    
    # 檢查腳本
    assert "AudioContext" in script
    assert "sampleRate" in script
    assert "channelCount" in script
    assert "bufferSize" in script

def test_spoof_font_list(browser_fingerprint):
    """測試字體列表偽裝"""
    # 模擬字體列表
    browser_fingerprint.font_list = [
        "Arial",
        "Helvetica",
        "Times New Roman",
        "Times",
        "Courier New",
        "Courier",
        "Verdana",
        "Georgia",
        "Palatino",
        "Garamond",
        "Bookman",
        "Comic Sans MS",
        "Trebuchet MS",
        "Arial Black"
    ]
    
    # 偽裝字體列表
    script = browser_fingerprint._spoof_font_list()
    
    # 檢查腳本
    assert "font-family" in script
    for font in browser_fingerprint.font_list:
        assert font in script

def test_configure_webrtc(browser_fingerprint):
    """測試 WebRTC 設定"""
    # 模擬 WebRTC 配置
    browser_fingerprint.webrtc_config = {
        "mode": "disable-non-proxied-udp",
        "proxy_only": True,
        "proxy_server": "socks5://127.0.0.1:1080"
    }
    
    # 設定 WebRTC
    script = browser_fingerprint._configure_webrtc()
    
    # 檢查腳本
    assert "RTCPeerConnection" in script
    assert "mode" in script
    assert "proxy_only" in script
    assert "proxy_server" in script

def test_spoof_hardware_concurrency(browser_fingerprint):
    """測試硬體並行度偽裝"""
    # 模擬硬體配置
    browser_fingerprint.hardware_config = {
        "concurrency": 4,
        "device_memory": 8,
        "platform": "Win32"
    }
    
    # 偽裝硬體並行度
    script = browser_fingerprint._spoof_hardware_concurrency()
    
    # 檢查腳本
    assert "navigator.hardwareConcurrency" in script
    assert "navigator.deviceMemory" in script
    assert "navigator.platform" in script

def test_setup_timezone(browser_fingerprint):
    """測試時區設定"""
    # 模擬時區設定
    browser_fingerprint.timezone = "Asia/Taipei"
    
    # 設定時區
    script = browser_fingerprint._setup_timezone()
    
    # 檢查腳本
    assert "Intl.DateTimeFormat" in script
    assert "timeZone" in script
    assert browser_fingerprint.timezone in script

def test_setup_language(browser_fingerprint):
    """測試語言設定"""
    # 模擬語言設定
    browser_fingerprint.language = "zh-TW"
    
    # 設定語言
    script = browser_fingerprint._setup_language()
    
    # 檢查腳本
    assert "navigator.language" in script
    assert browser_fingerprint.language in script

def test_get_fingerprint_scripts(browser_fingerprint):
    """測試獲取指紋腳本"""
    # 獲取所有指紋腳本
    scripts = browser_fingerprint.get_fingerprint_scripts()
    
    # 檢查腳本
    assert isinstance(scripts, list)
    assert len(scripts) > 0
    for script in scripts:
        assert isinstance(script, str)
        assert len(script) > 0 
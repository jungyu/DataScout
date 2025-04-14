"""
瀏覽器指紋服務測試模組

此模組提供了瀏覽器指紋服務的測試案例，包含以下功能：
- 指紋設定測試
- 指紋隨機化測試
- 指紋驗證測試
- 指紋儲存測試
"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from selenium_base.core.config import BaseConfig
from selenium_base.services.browser_fingerprint import BrowserFingerprint

@pytest.fixture
def config():
    """建立測試用的配置物件"""
    config = BaseConfig()
    config.browser.webgl_vendor = "Google Inc."
    config.browser.webgl_renderer = "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"
    config.browser.webgl_version = "WebGL GLSL ES 1.0"
    config.browser.webgl_shading_language_version = "WebGL GLSL ES 1.0"
    config.browser.webgl_extensions = ["ANGLE_instanced_arrays", "EXT_blend_minmax", "EXT_color_buffer_half_float"]
    config.browser.audio_sample_rate = 44100
    config.browser.audio_channel_count = 2
    config.browser.audio_buffer_size = 4096
    config.browser.canvas_noise = 0.1
    config.browser.canvas_mode = "source-over"
    config.browser.font_families = ["Arial", "Helvetica", "sans-serif"]
    config.browser.font_sizes = [12, 14, 16, 18, 20]
    config.browser.platform_os = "Windows"
    config.browser.platform_arch = "x64"
    config.browser.platform_version = "10.0.0"
    config.browser.hardware_cpu_cores = 4
    config.browser.hardware_memory = 8
    config.browser.hardware_gpu = "enabled"
    config.browser.screen_width = 1920
    config.browser.screen_height = 1080
    config.browser.screen_color_depth = 24
    config.browser.screen_pixel_ratio = 1
    config.browser.touch_enabled = True
    config.browser.touch_points = 5
    return config

@pytest.fixture
def fingerprint(config):
    """建立測試用的瀏覽器指紋服務"""
    return BrowserFingerprint(config)

@pytest.fixture
def options():
    """建立測試用的瀏覽器選項"""
    return MagicMock()

def test_setup(fingerprint, options):
    """測試指紋設定"""
    fingerprint.setup(options)
    
    # 檢查 WebGL 參數
    assert options.add_argument.call_count >= 4
    assert any("--webgl-vendor=Google Inc." in str(call) for call in options.add_argument.call_args_list)
    assert any("--webgl-renderer=ANGLE" in str(call) for call in options.add_argument.call_args_list)
    
    # 檢查音訊參數
    assert any("--audio-sample-rate=44100" in str(call) for call in options.add_argument.call_args_list)
    assert any("--audio-channel-count=2" in str(call) for call in options.add_argument.call_args_list)
    
    # 檢查 Canvas 參數
    assert any("--canvas-noise=0.1" in str(call) for call in options.add_argument.call_args_list)
    assert any("--canvas-mode=source-over" in str(call) for call in options.add_argument.call_args_list)
    
    # 檢查字體參數
    assert any("--font-family=Arial" in str(call) for call in options.add_argument.call_args_list)
    assert any("--font-size=12" in str(call) for call in options.add_argument.call_args_list)
    
    # 檢查平台參數
    assert any("--platform-os=Windows" in str(call) for call in options.add_argument.call_args_list)
    assert any("--platform-arch=x64" in str(call) for call in options.add_argument.call_args_list)
    
    # 檢查硬體參數
    assert any("--hardware-cpu-cores=4" in str(call) for call in options.add_argument.call_args_list)
    assert any("--hardware-memory=8" in str(call) for call in options.add_argument.call_args_list)
    
    # 檢查螢幕參數
    assert any("--window-size=1920,1080" in str(call) for call in options.add_argument.call_args_list)
    assert any("--screen-color-depth=24" in str(call) for call in options.add_argument.call_args_list)
    
    # 檢查觸控參數
    assert any("--enable-touch-events" in str(call) for call in options.add_argument.call_args_list)
    assert any("--touch-points=5" in str(call) for call in options.add_argument.call_args_list)

def test_randomize_webgl(fingerprint):
    """測試 WebGL 參數隨機化"""
    params = {
        "vendor": "Google Inc.",
        "renderer": "ANGLE",
        "version": "WebGL GLSL ES 1.0",
        "shading_language_version": "WebGL GLSL ES 1.0",
        "extensions": ["ANGLE_instanced_arrays"]
    }
    
    with patch.object(fingerprint.config.browser, "webgl_vendors", ["Google Inc.", "Mozilla"]):
        with patch.object(fingerprint.config.browser, "webgl_renderers", ["ANGLE", "SwiftShader"]):
            with patch.object(fingerprint.config.browser, "webgl_versions", ["WebGL GLSL ES 1.0", "WebGL GLSL ES 2.0"]):
                with patch.object(fingerprint.config.browser, "webgl_shading_language_versions", ["WebGL GLSL ES 1.0", "WebGL GLSL ES 2.0"]):
                    with patch.object(fingerprint.config.browser, "webgl_extensions", ["ANGLE_instanced_arrays", "EXT_blend_minmax"]):
                        randomized = fingerprint._randomize_webgl_params(params)
                        
                        assert randomized["vendor"] in ["Google Inc.", "Mozilla"]
                        assert randomized["renderer"] in ["ANGLE", "SwiftShader"]
                        assert randomized["version"] in ["WebGL GLSL ES 1.0", "WebGL GLSL ES 2.0"]
                        assert randomized["shading_language_version"] in ["WebGL GLSL ES 1.0", "WebGL GLSL ES 2.0"]
                        assert len(randomized["extensions"]) > 0
                        assert all(ext in ["ANGLE_instanced_arrays", "EXT_blend_minmax"] for ext in randomized["extensions"])

def test_randomize_audio(fingerprint):
    """測試音訊參數隨機化"""
    params = {
        "sample_rate": 44100,
        "channel_count": 2,
        "buffer_size": 4096
    }
    
    with patch.object(fingerprint.config.browser, "audio_sample_rates", [44100, 48000]):
        with patch.object(fingerprint.config.browser, "audio_channel_counts", [2, 4]):
            with patch.object(fingerprint.config.browser, "audio_buffer_sizes", [4096, 8192]):
                randomized = fingerprint._randomize_audio_params(params)
                
                assert randomized["sample_rate"] in [44100, 48000]
                assert randomized["channel_count"] in [2, 4]
                assert randomized["buffer_size"] in [4096, 8192]

def test_randomize_canvas(fingerprint):
    """測試 Canvas 參數隨機化"""
    params = {
        "noise": 0.1,
        "mode": "source-over"
    }
    
    with patch.object(fingerprint.config.browser, "canvas_modes", ["source-over", "source-atop"]):
        randomized = fingerprint._randomize_canvas_params(params)
        
        assert 0 <= randomized["noise"] <= 1
        assert randomized["mode"] in ["source-over", "source-atop"]

def test_randomize_fonts(fingerprint):
    """測試字體參數隨機化"""
    params = {
        "families": ["Arial"],
        "sizes": [12]
    }
    
    with patch.object(fingerprint.config.browser, "font_families", ["Arial", "Helvetica"]):
        with patch.object(fingerprint.config.browser, "font_sizes", [12, 14]):
            randomized = fingerprint._randomize_font_params(params)
            
            assert len(randomized["families"]) > 0
            assert all(family in ["Arial", "Helvetica"] for family in randomized["families"])
            assert len(randomized["sizes"]) > 0
            assert all(size in [12, 14] for size in randomized["sizes"])

def test_randomize_platform(fingerprint):
    """測試平台參數隨機化"""
    params = {
        "os": "Windows",
        "arch": "x64",
        "version": "10.0.0"
    }
    
    with patch.object(fingerprint.config.browser, "platform_oses", ["Windows", "MacOS"]):
        with patch.object(fingerprint.config.browser, "platform_arches", ["x64", "x86"]):
            with patch.object(fingerprint.config.browser, "platform_versions", ["10.0.0", "11.0.0"]):
                randomized = fingerprint._randomize_platform_params(params)
                
                assert randomized["os"] in ["Windows", "MacOS"]
                assert randomized["arch"] in ["x64", "x86"]
                assert randomized["version"] in ["10.0.0", "11.0.0"]

def test_randomize_hardware(fingerprint):
    """測試硬體參數隨機化"""
    params = {
        "cpu_cores": 4,
        "memory": 8,
        "gpu": "enabled"
    }
    
    with patch.object(fingerprint.config.browser, "hardware_gpus", ["enabled", "disabled"]):
        randomized = fingerprint._randomize_hardware_params(params)
        
        assert 1 <= randomized["cpu_cores"] <= 16
        assert 2 <= randomized["memory"] <= 32
        assert randomized["gpu"] in ["enabled", "disabled"]

def test_randomize_screen(fingerprint):
    """測試螢幕參數隨機化"""
    params = {
        "width": 1920,
        "height": 1080,
        "color_depth": 24,
        "pixel_ratio": 1
    }
    
    with patch.object(fingerprint.config.browser, "screen_widths", [1920, 2560]):
        with patch.object(fingerprint.config.browser, "screen_heights", [1080, 1440]):
            with patch.object(fingerprint.config.browser, "screen_color_depths", [24, 32]):
                with patch.object(fingerprint.config.browser, "screen_pixel_ratios", [1, 2]):
                    randomized = fingerprint._randomize_screen_params(params)
                    
                    assert randomized["width"] in [1920, 2560]
                    assert randomized["height"] in [1080, 1440]
                    assert randomized["color_depth"] in [24, 32]
                    assert randomized["pixel_ratio"] in [1, 2]

def test_randomize_touch(fingerprint):
    """測試觸控參數隨機化"""
    params = {
        "enabled": True,
        "points": 5
    }
    
    randomized = fingerprint._randomize_touch_params(params)
    
    assert isinstance(randomized["enabled"], bool)
    assert 1 <= randomized["points"] <= 10

def test_save_fingerprint(fingerprint, tmp_path):
    """測試指紋儲存"""
    # 設定指紋
    fingerprint.fingerprint = {
        "webgl": {
            "vendor": "Google Inc.",
            "renderer": "ANGLE",
            "version": "WebGL GLSL ES 1.0",
            "shading_language_version": "WebGL GLSL ES 1.0",
            "extensions": ["ANGLE_instanced_arrays"]
        }
    }
    
    # 儲存指紋
    path = tmp_path / "fingerprint.json"
    fingerprint.save_fingerprint(path)
    
    # 檢查檔案是否存在
    assert path.exists()
    
    # 檢查檔案內容
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data == fingerprint.fingerprint

def test_load_fingerprint(fingerprint, tmp_path):
    """測試指紋載入"""
    # 準備測試資料
    data = {
        "webgl": {
            "vendor": "Google Inc.",
            "renderer": "ANGLE",
            "version": "WebGL GLSL ES 1.0",
            "shading_language_version": "WebGL GLSL ES 1.0",
            "extensions": ["ANGLE_instanced_arrays"]
        }
    }
    
    path = tmp_path / "fingerprint.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    
    # 載入指紋
    fingerprint.load_fingerprint(path)
    
    # 檢查指紋內容
    assert fingerprint.fingerprint == data

def test_verify_fingerprint(fingerprint):
    """測試指紋驗證"""
    # 準備測試資料
    fingerprint.fingerprint = {
        "webgl": {
            "vendor": "Google Inc.",
            "renderer": "ANGLE",
            "version": "WebGL GLSL ES 1.0",
            "shading_language_version": "WebGL GLSL ES 1.0",
            "extensions": ["ANGLE_instanced_arrays"]
        },
        "audio": {
            "sample_rate": 44100,
            "channel_count": 2,
            "buffer_size": 4096
        },
        "canvas": {
            "noise": 0.1,
            "mode": "source-over"
        },
        "fonts": {
            "families": ["Arial"],
            "sizes": [12]
        },
        "platform": {
            "os": "Windows",
            "arch": "x64",
            "version": "10.0.0"
        },
        "hardware": {
            "cpu_cores": 4,
            "memory": 8,
            "gpu": "enabled"
        },
        "screen": {
            "width": 1920,
            "height": 1080,
            "color_depth": 24,
            "pixel_ratio": 1
        },
        "touch": {
            "enabled": True,
            "points": 5
        }
    }
    
    # 模擬瀏覽器驅動程式
    driver = MagicMock()
    driver.execute_script.side_effect = [
        fingerprint.fingerprint["webgl"],
        fingerprint.fingerprint["audio"],
        fingerprint.fingerprint["canvas"],
        fingerprint.fingerprint["fonts"],
        fingerprint.fingerprint["platform"],
        fingerprint.fingerprint["hardware"],
        fingerprint.fingerprint["screen"],
        fingerprint.fingerprint["touch"]
    ]
    
    # 驗證指紋
    assert fingerprint.verify_fingerprint(driver)
    
    # 檢查呼叫次數
    assert driver.execute_script.call_count == 8 
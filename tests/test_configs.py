#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模組測試

此模組提供所有配置類的測試用例，包括：
1. Cookie 配置測試
2. 瀏覽器指紋配置測試
3. 人類行為配置測試
4. 代理配置測試
"""

import unittest
from datetime import datetime
from anti_detection.configs import (
    # Cookie 配置
    CookieConfig,
    CookiePoolConfig,
    
    # 瀏覽器指紋配置
    WebGLConfig,
    CanvasConfig,
    AudioConfig,
    FontConfig,
    BrowserFingerprintConfig,
    
    # 人類行為配置
    MouseConfig,
    KeyboardConfig,
    ScrollConfig,
    TimingConfig,
    HumanBehaviorConfig,
    
    # 代理配置
    ProxyConfig,
    ProxyPoolConfig
)

class TestCookieConfig(unittest.TestCase):
    """Cookie 配置測試"""
    
    def test_cookie_config(self):
        """測試 CookieConfig"""
        config = CookieConfig(
            domain="example.com",
            path="/",
            name="session",
            value="abc123",
            secure=True,
            http_only=True,
            same_site="Strict"
        )
        
        # 測試基本屬性
        self.assertEqual(config.domain, "example.com")
        self.assertEqual(config.path, "/")
        self.assertEqual(config.name, "session")
        self.assertEqual(config.value, "abc123")
        self.assertTrue(config.secure)
        self.assertTrue(config.http_only)
        self.assertEqual(config.same_site, "Strict")
        
        # 測試統計數據
        self.assertEqual(config.use_count, 0)
        self.assertEqual(config.success_count, 0)
        self.assertEqual(config.fail_count, 0)
        self.assertIsNone(config.last_used)
        
        # 測試更新統計
        config.update_stats(True)
        self.assertEqual(config.use_count, 1)
        self.assertEqual(config.success_count, 1)
        self.assertEqual(config.fail_count, 0)
        self.assertIsNotNone(config.last_used)
        
        # 測試字典轉換
        data = config.to_dict()
        new_config = CookieConfig.from_dict(data)
        self.assertEqual(config.domain, new_config.domain)
        self.assertEqual(config.path, new_config.path)
        self.assertEqual(config.name, new_config.name)
        self.assertEqual(config.value, new_config.value)
    
    def test_cookie_pool_config(self):
        """測試 CookiePoolConfig"""
        config = CookiePoolConfig(
            max_size=100,
            min_size=10,
            cleanup_interval=300,
            max_age=86400,
            min_success_rate=0.8
        )
        
        # 測試基本屬性
        self.assertEqual(config.max_size, 100)
        self.assertEqual(config.min_size, 10)
        self.assertEqual(config.cleanup_interval, 300)
        self.assertEqual(config.max_age, 86400)
        self.assertEqual(config.min_success_rate, 0.8)
        
        # 測試字典轉換
        data = config.to_dict()
        new_config = CookiePoolConfig.from_dict(data)
        self.assertEqual(config.max_size, new_config.max_size)
        self.assertEqual(config.min_size, new_config.min_size)
        self.assertEqual(config.cleanup_interval, new_config.cleanup_interval)
        self.assertEqual(config.max_age, new_config.max_age)
        self.assertEqual(config.min_success_rate, new_config.min_success_rate)

class TestBrowserFingerprintConfig(unittest.TestCase):
    """瀏覽器指紋配置測試"""
    
    def test_webgl_config(self):
        """測試 WebGLConfig"""
        config = WebGLConfig(
            vendor="Google Inc.",
            renderer="ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)",
            version="WebGL GLSL ES 1.0"
        )
        
        # 測試基本屬性
        self.assertEqual(config.vendor, "Google Inc.")
        self.assertEqual(config.renderer, "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)")
        self.assertEqual(config.version, "WebGL GLSL ES 1.0")
        
        # 測試字典轉換
        data = config.to_dict()
        new_config = WebGLConfig.from_dict(data)
        self.assertEqual(config.vendor, new_config.vendor)
        self.assertEqual(config.renderer, new_config.renderer)
        self.assertEqual(config.version, new_config.version)
    
    def test_canvas_config(self):
        """測試 CanvasConfig"""
        config = CanvasConfig(
            noise_level=0.1,
            pattern="default"
        )
        
        # 測試基本屬性
        self.assertEqual(config.noise_level, 0.1)
        self.assertEqual(config.pattern, "default")
        
        # 測試字典轉換
        data = config.to_dict()
        new_config = CanvasConfig.from_dict(data)
        self.assertEqual(config.noise_level, new_config.noise_level)
        self.assertEqual(config.pattern, new_config.pattern)
    
    def test_audio_config(self):
        """測試 AudioConfig"""
        config = AudioConfig(
            noise_level=0.1,
            pattern="default"
        )
        
        # 測試基本屬性
        self.assertEqual(config.noise_level, 0.1)
        self.assertEqual(config.pattern, "default")
        
        # 測試字典轉換
        data = config.to_dict()
        new_config = AudioConfig.from_dict(data)
        self.assertEqual(config.noise_level, new_config.noise_level)
        self.assertEqual(config.pattern, new_config.pattern)
    
    def test_font_config(self):
        """測試 FontConfig"""
        config = FontConfig(
            common_fonts=["Arial", "Times New Roman"],
            chinese_fonts=["Microsoft YaHei", "SimSun"]
        )
        
        # 測試基本屬性
        self.assertEqual(config.common_fonts, ["Arial", "Times New Roman"])
        self.assertEqual(config.chinese_fonts, ["Microsoft YaHei", "SimSun"])
        
        # 測試字典轉換
        data = config.to_dict()
        new_config = FontConfig.from_dict(data)
        self.assertEqual(config.common_fonts, new_config.common_fonts)
        self.assertEqual(config.chinese_fonts, new_config.chinese_fonts)
    
    def test_browser_fingerprint_config(self):
        """測試 BrowserFingerprintConfig"""
        config = BrowserFingerprintConfig(
            webgl=WebGLConfig(),
            canvas=CanvasConfig(),
            audio=AudioConfig(),
            fonts=FontConfig()
        )
        
        # 測試基本屬性
        self.assertIsInstance(config.webgl, WebGLConfig)
        self.assertIsInstance(config.canvas, CanvasConfig)
        self.assertIsInstance(config.audio, AudioConfig)
        self.assertIsInstance(config.fonts, FontConfig)
        
        # 測試字典轉換
        data = config.to_dict()
        new_config = BrowserFingerprintConfig.from_dict(data)
        self.assertIsInstance(new_config.webgl, WebGLConfig)
        self.assertIsInstance(new_config.canvas, CanvasConfig)
        self.assertIsInstance(new_config.audio, AudioConfig)
        self.assertIsInstance(new_config.fonts, FontConfig)

class TestHumanBehaviorConfig(unittest.TestCase):
    """人類行為配置測試"""
    
    def test_mouse_config(self):
        """測試 MouseConfig"""
        config = MouseConfig(
            move_speed_range=(100, 500),
            click_duration_range=(50, 200),
            double_click_interval_range=(300, 500)
        )
        
        # 測試基本屬性
        self.assertEqual(config.move_speed_range, (100, 500))
        self.assertEqual(config.click_duration_range, (50, 200))
        self.assertEqual(config.double_click_interval_range, (300, 500))
        
        # 測試字典轉換
        data = config.to_dict()
        new_config = MouseConfig.from_dict(data)
        self.assertEqual(config.move_speed_range, new_config.move_speed_range)
        self.assertEqual(config.click_duration_range, new_config.click_duration_range)
        self.assertEqual(config.double_click_interval_range, new_config.double_click_interval_range)
    
    def test_keyboard_config(self):
        """測試 KeyboardConfig"""
        config = KeyboardConfig(
            type_speed_range=(100, 300),
            key_press_duration_range=(50, 150)
        )
        
        # 測試基本屬性
        self.assertEqual(config.type_speed_range, (100, 300))
        self.assertEqual(config.key_press_duration_range, (50, 150))
        
        # 測試字典轉換
        data = config.to_dict()
        new_config = KeyboardConfig.from_dict(data)
        self.assertEqual(config.type_speed_range, new_config.type_speed_range)
        self.assertEqual(config.key_press_duration_range, new_config.key_press_duration_range)
    
    def test_scroll_config(self):
        """測試 ScrollConfig"""
        config = ScrollConfig(
            scroll_speed_range=(100, 500),
            scroll_step_range=(50, 200)
        )
        
        # 測試基本屬性
        self.assertEqual(config.scroll_speed_range, (100, 500))
        self.assertEqual(config.scroll_step_range, (50, 200))
        
        # 測試字典轉換
        data = config.to_dict()
        new_config = ScrollConfig.from_dict(data)
        self.assertEqual(config.scroll_speed_range, new_config.scroll_speed_range)
        self.assertEqual(config.scroll_step_range, new_config.scroll_step_range)
    
    def test_timing_config(self):
        """測試 TimingConfig"""
        config = TimingConfig(
            page_load_timeout=30,
            element_wait_timeout=10,
            action_interval_range=(1, 5)
        )
        
        # 測試基本屬性
        self.assertEqual(config.page_load_timeout, 30)
        self.assertEqual(config.element_wait_timeout, 10)
        self.assertEqual(config.action_interval_range, (1, 5))
        
        # 測試字典轉換
        data = config.to_dict()
        new_config = TimingConfig.from_dict(data)
        self.assertEqual(config.page_load_timeout, new_config.page_load_timeout)
        self.assertEqual(config.element_wait_timeout, new_config.element_wait_timeout)
        self.assertEqual(config.action_interval_range, new_config.action_interval_range)
    
    def test_human_behavior_config(self):
        """測試 HumanBehaviorConfig"""
        config = HumanBehaviorConfig(
            mouse=MouseConfig(),
            keyboard=KeyboardConfig(),
            scroll=ScrollConfig(),
            timing=TimingConfig()
        )
        
        # 測試基本屬性
        self.assertIsInstance(config.mouse, MouseConfig)
        self.assertIsInstance(config.keyboard, KeyboardConfig)
        self.assertIsInstance(config.scroll, ScrollConfig)
        self.assertIsInstance(config.timing, TimingConfig)
        
        # 測試字典轉換
        data = config.to_dict()
        new_config = HumanBehaviorConfig.from_dict(data)
        self.assertIsInstance(new_config.mouse, MouseConfig)
        self.assertIsInstance(new_config.keyboard, KeyboardConfig)
        self.assertIsInstance(new_config.scroll, ScrollConfig)
        self.assertIsInstance(new_config.timing, TimingConfig)

class TestProxyConfig(unittest.TestCase):
    """代理配置測試"""
    
    def test_proxy_config(self):
        """測試 ProxyConfig"""
        config = ProxyConfig(
            proxy_type="http",
            host="127.0.0.1",
            port=8080,
            username="user",
            password="pass",
            country="US",
            region="CA",
            city="San Francisco",
            isp="Comcast"
        )
        
        # 測試基本屬性
        self.assertEqual(config.proxy_type, "http")
        self.assertEqual(config.host, "127.0.0.1")
        self.assertEqual(config.port, 8080)
        self.assertEqual(config.username, "user")
        self.assertEqual(config.password, "pass")
        self.assertEqual(config.country, "US")
        self.assertEqual(config.region, "CA")
        self.assertEqual(config.city, "San Francisco")
        self.assertEqual(config.isp, "Comcast")
        
        # 測試 URL 生成
        self.assertEqual(config.url, "http://user:pass@127.0.0.1:8080")
        
        # 測試地理位置
        self.assertEqual(config.location, "San Francisco, CA, US")
        
        # 測試統計數據
        self.assertEqual(config.use_count, 0)
        self.assertEqual(config.success_count, 0)
        self.assertEqual(config.fail_count, 0)
        self.assertIsNone(config.last_used)
        
        # 測試更新統計
        config.update_stats(True)
        self.assertEqual(config.use_count, 1)
        self.assertEqual(config.success_count, 1)
        self.assertEqual(config.fail_count, 0)
        self.assertIsNotNone(config.last_used)
        
        # 測試字典轉換
        data = config.to_dict()
        new_config = ProxyConfig.from_dict(data)
        self.assertEqual(config.proxy_type, new_config.proxy_type)
        self.assertEqual(config.host, new_config.host)
        self.assertEqual(config.port, new_config.port)
        self.assertEqual(config.username, new_config.username)
        self.assertEqual(config.password, new_config.password)
        self.assertEqual(config.country, new_config.country)
        self.assertEqual(config.region, new_config.region)
        self.assertEqual(config.city, new_config.city)
        self.assertEqual(config.isp, new_config.isp)
    
    def test_proxy_pool_config(self):
        """測試 ProxyPoolConfig"""
        config = ProxyPoolConfig(
            max_size=100,
            min_size=10,
            update_interval=300,
            check_interval=60,
            max_age=86400,
            min_success_rate=0.8,
            max_speed=1000.0,
            allowed_countries=["US", "CA"],
            blocked_countries=["CN", "RU"],
            allowed_regions=["CA", "NY"],
            blocked_regions=["TX", "FL"],
            allowed_isps=["Comcast", "Verizon"],
            blocked_isps=["China Telecom", "Russia Telecom"],
            allowed_types=["http", "https"]
        )
        
        # 測試基本屬性
        self.assertEqual(config.max_size, 100)
        self.assertEqual(config.min_size, 10)
        self.assertEqual(config.update_interval, 300)
        self.assertEqual(config.check_interval, 60)
        self.assertEqual(config.max_age, 86400)
        self.assertEqual(config.min_success_rate, 0.8)
        self.assertEqual(config.max_speed, 1000.0)
        self.assertEqual(config.allowed_countries, ["US", "CA"])
        self.assertEqual(config.blocked_countries, ["CN", "RU"])
        self.assertEqual(config.allowed_regions, ["CA", "NY"])
        self.assertEqual(config.blocked_regions, ["TX", "FL"])
        self.assertEqual(config.allowed_isps, ["Comcast", "Verizon"])
        self.assertEqual(config.blocked_isps, ["China Telecom", "Russia Telecom"])
        self.assertEqual(config.allowed_types, ["http", "https"])
        
        # 測試代理驗證
        proxy = ProxyConfig(
            proxy_type="http",
            host="127.0.0.1",
            port=8080,
            country="US",
            region="CA",
            isp="Comcast",
            success_rate=0.9,
            speed=500.0
        )
        self.assertTrue(config.is_proxy_allowed(proxy))
        
        # 測試字典轉換
        data = config.to_dict()
        new_config = ProxyPoolConfig.from_dict(data)
        self.assertEqual(config.max_size, new_config.max_size)
        self.assertEqual(config.min_size, new_config.min_size)
        self.assertEqual(config.update_interval, new_config.update_interval)
        self.assertEqual(config.check_interval, new_config.check_interval)
        self.assertEqual(config.max_age, new_config.max_age)
        self.assertEqual(config.min_success_rate, new_config.min_success_rate)
        self.assertEqual(config.max_speed, new_config.max_speed)
        self.assertEqual(config.allowed_countries, new_config.allowed_countries)
        self.assertEqual(config.blocked_countries, new_config.blocked_countries)
        self.assertEqual(config.allowed_regions, new_config.allowed_regions)
        self.assertEqual(config.blocked_regions, new_config.blocked_regions)
        self.assertEqual(config.allowed_isps, new_config.allowed_isps)
        self.assertEqual(config.blocked_isps, new_config.blocked_isps)
        self.assertEqual(config.allowed_types, new_config.allowed_types)

if __name__ == '__main__':
    unittest.main() 
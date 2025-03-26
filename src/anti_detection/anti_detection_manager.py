#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import random
import logging
from typing import Dict, List, Optional, Union

from selenium import webdriver

from ..core.webdriver_manager import WebDriverManager
from ..utils.logger import setup_logger
from .browser_fingerprint import BrowserFingerprintModifier
from .human_behavior import HumanBehaviorSimulator
from .detection_handler import DetectionHandler
from .honeypot_detector import HoneypotDetector
from .stealth_script_loader import StealthScriptLoader


class AntiDetectionManager:
    """
    反爬蟲管理器，提供全面的反爬蟲策略，
    檢測和應對各種反爬機制，包括WebDriver特徵隱藏、
    行為模擬、代理切換等。
    """
    
    def __init__(self, config: Dict = None, log_level: int = logging.INFO):
        """
        初始化反爬蟲管理器
        
        Args:
            config: 配置字典
            log_level: 日誌級別
        """
        self.logger = setup_logger(__name__, log_level)
        self.logger.info("初始化反爬蟲管理器")
        
        self.config = config or {}
        
        # WebDriver管理器
        self.webdriver_manager = WebDriverManager(
            config=self.config.get("webdriver_config", {}),
            log_level=log_level
        )
        
        # 默認延遲設置
        self.delays = self.config.get("delays", {
            "page_load": {"min": 2, "max": 5},
            "between_actions": {"min": 1, "max": 3},
            "before_click": {"min": 0.5, "max": 2},
            "typing_speed": {"min": 0.05, "max": 0.2}
        })
        
        # 代理設置
        self.proxies = self.config.get("proxies", [])
        self.proxy_index = 0
        
        # 用戶代理設置
        self.user_agents = self.config.get("user_agents", [])
        
        # 檢測計數器
        self.detection_count = 0
        self.max_retries = self.config.get("max_retries", 3)
        
        # 載入隱身腳本
        self.stealth_script_loader = StealthScriptLoader(log_level)
        
        # 初始化各個模組
        self.fingerprint_modifier = BrowserFingerprintModifier(self.logger)
        self.behavior_simulator = HumanBehaviorSimulator(self.delays, self.logger)
        self.detection_handler = DetectionHandler(
            self, self.config, self.logger, self.max_retries
        )
        self.honeypot_detector = HoneypotDetector(self.logger)
        
        self.logger.info("反爬蟲管理器初始化完成")
    
    def create_webdriver(self, headless: bool = True) -> webdriver.Remote:
        """
        創建反爬蟲配置的WebDriver
        
        Args:
            headless: 是否使用無頭模式
            
        Returns:
            配置好的WebDriver實例
        """
        # 更新配置
        webdriver_config = self.config.get("webdriver_config", {}).copy()
        webdriver_config["headless"] = headless
        
        # 設置代理
        if self.proxies and self.config.get("use_proxy", False):
            proxy = self._get_next_proxy()
            if proxy:
                webdriver_config["proxy"] = proxy
        
        # 設置用戶代理
        if self.user_agents and self.config.get("randomize_user_agent", True):
            user_agent = self._get_random_user_agent()
            if user_agent:
                webdriver_config["user_agent"] = user_agent
        
        # 創建WebDriver
        self.webdriver_manager = WebDriverManager(
            config=webdriver_config,
            log_level=self.logger.level
        )
        
        # 獲取WebDriver實例
        driver = self.webdriver_manager.create_driver()
        
        # 應用隱身腳本
        self._apply_stealth_scripts(driver)
        
        # 配置WebDriver
        self._configure_driver(driver)
        
        return driver
    
    def _configure_driver(self, driver: webdriver.Remote):
        """配置WebDriver的額外設置"""
        # 設置頁面加載超時
        driver.set_page_load_timeout(self.config.get("page_load_timeout", 30))
        
        # 設置腳本超時
        driver.set_script_timeout(self.config.get("script_timeout", 30))
        
        # 設置窗口大小
        window_size = self.config.get("window_size", {"width": 1920, "height": 1080})
        driver.set_window_size(window_size["width"], window_size["height"])
    
    def _apply_stealth_scripts(self, driver: webdriver.Remote):
        """應用隱身腳本"""
        self.stealth_script_loader.apply_scripts(driver)
    
    def _get_next_proxy(self) -> Union[str, Dict, None]:
        """獲取下一個代理"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        
        return proxy
    
    def _get_random_user_agent(self) -> Optional[str]:
        """獲取隨機用戶代理"""
        if not self.user_agents:
            return None
        
        return random.choice(self.user_agents)
    
    def random_delay(self, delay_type: str = "between_actions"):
        """
        根據配置的延遲範圍，生成隨機延遲時間並等待
        
        Args:
            delay_type: 延遲類型，可選值：page_load, between_actions, before_click, typing_speed
        """
        delay_config = self.delays.get(delay_type, {"min": 1, "max": 3})
        min_delay = delay_config.get("min", 1)
        max_delay = delay_config.get("max", 3)
        
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def detected_anti_crawling(self, driver: webdriver.Remote) -> bool:
        """
        檢測是否被反爬機制識別
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否被識別
        """
        return self.detection_handler.detect(driver)
    
    def handle_detection(self, driver: webdriver.Remote) -> bool:
        """
        處理被反爬機制識別的情況
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否成功處理
        """
        return self.detection_handler.handle(driver)
    
    def enable_stealth_mode(self, driver: webdriver.Remote):
        """
        啟用隱身模式，綜合應用多種反檢測技術
        
        Args:
            driver: WebDriver實例
        """
        # 應用隱身腳本
        self._apply_stealth_scripts(driver)
        
        # 修改瀏覽器指紋
        self.fingerprint_modifier.modify_browser_fingerprint(driver)
        
        # 添加額外的隱身措施
        try:
            # 偽造鼠標軌跡
            self.fingerprint_modifier.fake_mouse_movements(driver)
            
            # 偽造鍵盤事件
            self.fingerprint_modifier.fake_keyboard_events(driver)
            
            # 修改WebRTC行為
            self.fingerprint_modifier.modify_webrtc_behavior(driver)
            
            self.logger.info("成功啟用隱身模式")
        
        except Exception as e:
            self.logger.error(f"啟用隱身模式失敗: {str(e)}")
    
    def detect_honeypots(self, driver: webdriver.Remote) -> bool:
        """
        檢測頁面中的蜜罐和陷阱
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否檢測到蜜罐
        """
        return self.honeypot_detector.detect(driver)


class BrowserFingerprintModifier:
    """處理瀏覽器指紋修改"""
    
    def __init__(self, logger=None):
        """
        初始化瀏覽器指紋修改器
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def modify_browser_fingerprint(self, driver: webdriver.Remote):
        """
        修改瀏覽器指紋特徵
        
        Args:
            driver: WebDriver實例
        """
        try:
            # 修改瀏覽器指紋的JavaScript代碼
            fingerprint_script = """
            // 修改navigator屬性
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
            
            // 修改plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    // 創建虛擬插件
                    const plugins = [];
                    for (let i = 0; i < 3; i++) {
                        plugins.push({
                            name: `Plugin ${i}`,
                            description: `Fake plugin ${i}`,
                            filename: `plugin${i}.dll`,
                            length: 1
                        });
                    }
                    return plugins;
                }
            });
            
            // 修改語言
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-TW', 'zh', 'en-US', 'en'],
            });
            
            // 修改硬件信息
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8,
            });
            
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8,
            });
            
            // 修改WebGL
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                // 修改一些特定的參數
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel(R) Iris(TM) Graphics 6100';
                }
                return getParameter.apply(this, arguments);
            };
            
            // 修改Canvas行為
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function() {
                const context = originalGetContext.apply(this, arguments);
                if (context && arguments[0] === '2d') {
                    // 修改填充矩形方法，使結果略微不同
                    const originalFillRect = context.fillRect;
                    context.fillRect = function() {
                        arguments[0] += Math.random() * 0.01;
                        arguments[1] += Math.random() * 0.01;
                        return originalFillRect.apply(this, arguments);
                    };
                }
                return context;
            };
            
            // 修改屏幕信息
            Object.defineProperty(screen, 'width', {
                get: () => 1920,
            });
            
            Object.defineProperty(screen, 'height', {
                get: () => 1080,
            });
            
            Object.defineProperty(screen, 'colorDepth', {
                get: () => 24,
            });
            
            // 移除檢測特徵
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            """
            
            driver.execute_script(fingerprint_script)
            self.logger.info("成功修改瀏覽器指紋特徵")
        
        except Exception as e:
            self.logger.error(f"修改瀏覽器指紋特徵失敗: {str(e)}")
    
    def fake_mouse_movements(self, driver: webdriver.Remote):
        """
        生成假的鼠標移動軌跡
        
        Args:
            driver: WebDriver實例
        """
        script = """
        // 創建模擬鼠標軌跡
        const events = [];
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        // 生成隨機點
        let x = 100, y = 100;
        for (let i = 0; i < 20; i++) {
            x += Math.floor(Math.random() * 20) - 10;
            y += Math.floor(Math.random() * 20) - 10;
            
            // 確保在可視區域內
            x = Math.max(0, Math.min(x, viewportWidth));
            y = Math.max(0, Math.min(y, viewportHeight));
            
            events.push({
                type: 'mousemove',
                x: x,
                y: y,
                timestamp: Date.now() + i * 100
            });
        }
        
        // 存儲到window對象中，以備檢測時使用
        window._mouseTrack = events;
        """
        driver.execute_script(script)
    
    def fake_keyboard_events(self, driver: webdriver.Remote):
        """
        生成假的鍵盤事件
        
        Args:
            driver: WebDriver實例
        """
        script = """
        // 創建模擬鍵盤事件
        const keyEvents = [];
        const keys = ['a', 'b', 'c', 'd', 'e'];
        
        for (let i = 0; i < 10; i++) {
            const key = keys[Math.floor(Math.random() * keys.length)];
            keyEvents.push({
                type: 'keydown',
                key: key,
                timestamp: Date.now() + i * 200
            });
            
            keyEvents.push({
                type: 'keyup',
                key: key,
                timestamp: Date.now() + i * 200 + 100
            });
        }
        
        // 存儲到window對象中，以備檢測時使用
        window._keyboardTrack = keyEvents;
        """
        driver.execute_script(script)
    
    def modify_webrtc_behavior(self, driver: webdriver.Remote):
        """
        修改WebRTC行為，防止IP洩露
        
        Args:
            driver: WebDriver實例
        """
        script = """
        // 修改WebRTC行為
        if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
            const originalEnumerateDevices = navigator.mediaDevices.enumerateDevices;
            navigator.mediaDevices.enumerateDevices = function() {
                return originalEnumerateDevices.apply(this, arguments)
                    .then(devices => {
                        // 返回空設備列表或修改的設備列表
                        return [];
                    });
            };
        }
        
        // 修改RTCPeerConnection，防止IP洩露
        if (window.RTCPeerConnection) {
            const originalRTCPeerConnection = window.RTCPeerConnection;
            window.RTCPeerConnection = function() {
                // 禁止創建連接或返回修改後的連接
                return null;
            };
        }
        """
        driver.execute_script(script)
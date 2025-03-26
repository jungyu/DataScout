#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from selenium import webdriver


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
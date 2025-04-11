#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
隱身腳本載入器

此模組提供隱身腳本的載入和管理功能，包括：
1. 腳本載入和注入
2. 腳本版本管理
3. 腳本效果驗證
"""

import os
import json
import logging
from typing import List, Dict, Any
from pathlib import Path
from selenium import webdriver

class StealthScriptLoader:
    """隱身腳本載入器類"""
    
    def __init__(self, log_level: int = logging.INFO):
        """
        初始化隱身腳本載入器
        
        Args:
            log_level: 日誌級別
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # 腳本目錄
        self.script_dir = Path(__file__).parent / "scripts"
        
        # 腳本列表
        self.scripts = {
            "webdriver": self._get_webdriver_script(),
            "navigator": self._get_navigator_script(),
            "plugins": self._get_plugins_script(),
            "canvas": self._get_canvas_script(),
            "webgl": self._get_webgl_script(),
            "media": self._get_media_script(),
            "webrtc": self._get_webrtc_script(),
            "battery": self._get_battery_script(),
            "hardware": self._get_hardware_script()
        }
        
        self.logger.info("隱身腳本載入器初始化完成")
    
    def apply_scripts(self, driver: webdriver.Remote):
        """
        應用所有隱身腳本
        
        Args:
            driver: WebDriver實例
        """
        try:
            for name, script in self.scripts.items():
                self.logger.debug(f"應用腳本: {name}")
                driver.execute_script(script)
            self.logger.info("所有隱身腳本應用完成")
        except Exception as e:
            self.logger.error(f"應用腳本失敗: {str(e)}")
    
    def _get_webdriver_script(self) -> str:
        """獲取WebDriver隱身腳本"""
        return """
        // 隱藏WebDriver特徵
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false
        });
        
        // 刪除自動化相關屬性
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """
    
    def _get_navigator_script(self) -> str:
        """獲取Navigator隱身腳本"""
        return """
        // 修改Navigator屬性
        const _navigator = {};
        for (let i in navigator) {
            _navigator[i] = navigator[i];
        }
        
        // 修改語言設置
        _navigator.languages = ['zh-TW', 'zh', 'en-US', 'en'];
        
        // 修改平台信息
        _navigator.platform = 'MacIntel';
        
        // 應用修改
        Object.defineProperty(window, 'navigator', {
            get: () => _navigator
        });
        """
    
    def _get_plugins_script(self) -> str:
        """獲取Plugins隱身腳本"""
        return """
        // 創建假插件
        const plugins = [
            {
                name: 'Chrome PDF Plugin',
                filename: 'internal-pdf-viewer',
                description: 'Portable Document Format',
                length: 1
            },
            {
                name: 'Chrome PDF Viewer',
                filename: 'chrome-pdf-viewer',
                description: 'Portable Document Format',
                length: 1
            },
            {
                name: 'Native Client',
                filename: 'native-client',
                description: '',
                length: 1
            }
        ];
        
        // 應用假插件
        Object.defineProperty(navigator, 'plugins', {
            get: () => plugins
        });
        """
    
    def _get_canvas_script(self) -> str:
        """獲取Canvas隱身腳本"""
        return """
        // 修改Canvas行為
        const originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function() {
            const context = originalGetContext.apply(this, arguments);
            if (context && arguments[0] === '2d') {
                // 修改填充矩形方法
                const originalFillRect = context.fillRect;
                context.fillRect = function() {
                    arguments[0] += Math.random() * 0.01;
                    arguments[1] += Math.random() * 0.01;
                    return originalFillRect.apply(this, arguments);
                };
                
                // 修改填充文本方法
                const originalFillText = context.fillText;
                context.fillText = function() {
                    arguments[0] = arguments[0].split('').map(c => 
                        Math.random() < 0.1 ? String.fromCharCode(c.charCodeAt(0) + 1) : c
                    ).join('');
                    return originalFillText.apply(this, arguments);
                };
            }
            return context;
        };
        """
    
    def _get_webgl_script(self) -> str:
        """獲取WebGL隱身腳本"""
        return """
        // 修改WebGL行為
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            // 修改特定參數
            if (parameter === 37445) {
                return 'Intel Inc.';
            }
            if (parameter === 37446) {
                return 'Intel(R) Iris(TM) Graphics 6100';
            }
            return getParameter.apply(this, arguments);
        };
        """
    
    def _get_media_script(self) -> str:
        """獲取Media隱身腳本"""
        return """
        // 修改媒體設備行為
        if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
            const originalEnumerateDevices = navigator.mediaDevices.enumerateDevices;
            navigator.mediaDevices.enumerateDevices = function() {
                return originalEnumerateDevices.apply(this, arguments)
                    .then(devices => {
                        return devices.map(device => {
                            device.deviceId = Math.random().toString(36).substring(7);
                            return device;
                        });
                    });
            };
        }
        """
    
    def _get_webrtc_script(self) -> str:
        """獲取WebRTC隱身腳本"""
        return """
        // 禁用WebRTC
        if (window.RTCPeerConnection) {
            window.RTCPeerConnection = function() {
                return null;
            };
        }
        if (window.RTCDataChannel) {
            window.RTCDataChannel = function() {
                return null;
            };
        }
        """
    
    def _get_battery_script(self) -> str:
        """獲取Battery隱身腳本"""
        return """
        // 修改電池API
        if (navigator.getBattery) {
            navigator.getBattery = function() {
                return Promise.resolve({
                    charging: true,
                    chargingTime: Infinity,
                    dischargingTime: Infinity,
                    level: 0.98
                });
            };
        }
        """
    
    def _get_hardware_script(self) -> str:
        """獲取Hardware隱身腳本"""
        return """
        // 修改硬件信息
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });
        
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8
        });
        
        Object.defineProperty(screen, 'width', {
            get: () => 1920
        });
        
        Object.defineProperty(screen, 'height', {
            get: () => 1080
        });
        
        Object.defineProperty(screen, 'colorDepth', {
            get: () => 24
        });
        """ 
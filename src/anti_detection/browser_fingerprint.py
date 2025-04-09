#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
瀏覽器指紋

此模組提供瀏覽器指紋的功能，包括：
1. 指紋生成
2. 指紋驗證
3. 指紋管理
4. 指紋更新
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import random
import hashlib

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from .base_error import BaseError, handle_error, retry_on_error
from .configs.fingerprint_config import FingerprintConfig

class FingerprintError(BaseError):
    """指紋錯誤"""
    pass

class FingerprintResult:
    """指紋結果"""
    
    def __init__(
        self,
        success: bool,
        fingerprint: Dict[str, Any],
        confidence: float,
        details: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ):
        """
        初始化指紋結果
        
        Args:
            success: 是否成功
            fingerprint: 指紋數據
            confidence: 置信度
            details: 詳細信息
            timestamp: 時間戳
        """
        self.success = success
        self.fingerprint = fingerprint
        self.confidence = confidence
        self.details = details
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "success": self.success,
            "fingerprint": self.fingerprint,
            "confidence": self.confidence,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FingerprintResult":
        """從字典創建實例"""
        return cls(
            success=data["success"],
            fingerprint=data["fingerprint"],
            confidence=data["confidence"],
            details=data["details"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )

class BrowserFingerprint:
    """瀏覽器指紋"""
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化瀏覽器指紋
        
        Args:
            config: 配置字典
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.config = FingerprintConfig.from_dict(config or {})
        if not self.config.validate():
            raise FingerprintError("無效的指紋配置")
        
        self.fingerprint_history: List[FingerprintResult] = []
        self.fingerprint_stats: Dict[str, Dict[str, int]] = {}
    
    @handle_error
    def generate_fingerprint(
        self,
        driver: WebDriver
    ) -> FingerprintResult:
        """
        生成瀏覽器指紋
        
        Args:
            driver: WebDriver實例
            
        Returns:
            指紋結果
        """
        # 獲取瀏覽器信息
        browser_info = self._get_browser_info(driver)
        
        # 獲取系統信息
        system_info = self._get_system_info(driver)
        
        # 獲取硬件信息
        hardware_info = self._get_hardware_info(driver)
        
        # 獲取網絡信息
        network_info = self._get_network_info(driver)
        
        # 獲取插件信息
        plugin_info = self._get_plugin_info(driver)
        
        # 獲取字體信息
        font_info = self._get_font_info(driver)
        
        # 獲取Canvas信息
        canvas_info = self._get_canvas_info(driver)
        
        # 獲取WebGL信息
        webgl_info = self._get_webgl_info(driver)
        
        # 獲取音頻信息
        audio_info = self._get_audio_info(driver)
        
        # 合併所有信息
        fingerprint = {
            "browser": browser_info,
            "system": system_info,
            "hardware": hardware_info,
            "network": network_info,
            "plugins": plugin_info,
            "fonts": font_info,
            "canvas": canvas_info,
            "webgl": webgl_info,
            "audio": audio_info
        }
        
        # 計算指紋哈希
        fingerprint_hash = self._calculate_fingerprint_hash(fingerprint)
        
        # 返回結果
        return FingerprintResult(
            success=True,
            fingerprint=fingerprint,
            confidence=1.0,
            details={"hash": fingerprint_hash}
        )
    
    def _get_browser_info(self, driver: WebDriver) -> Dict[str, Any]:
        """獲取瀏覽器信息"""
        script = """
        return {
            userAgent: navigator.userAgent,
            appName: navigator.appName,
            appVersion: navigator.appVersion,
            platform: navigator.platform,
            language: navigator.language,
            languages: navigator.languages,
            vendor: navigator.vendor,
            product: navigator.product,
            productSub: navigator.productSub,
            cookieEnabled: navigator.cookieEnabled,
            doNotTrack: navigator.doNotTrack
        };
        """
        return driver.execute_script(script)
    
    def _get_system_info(self, driver: WebDriver) -> Dict[str, Any]:
        """獲取系統信息"""
        script = """
        return {
            platform: navigator.platform,
            hardwareConcurrency: navigator.hardwareConcurrency,
            deviceMemory: navigator.deviceMemory,
            maxTouchPoints: navigator.maxTouchPoints,
            connection: navigator.connection ? {
                effectiveType: navigator.connection.effectiveType,
                rtt: navigator.connection.rtt,
                downlink: navigator.connection.downlink
            } : null
        };
        """
        return driver.execute_script(script)
    
    def _get_hardware_info(self, driver: WebDriver) -> Dict[str, Any]:
        """獲取硬件信息"""
        script = """
        return {
            screen: {
                width: window.screen.width,
                height: window.screen.height,
                colorDepth: window.screen.colorDepth,
                pixelDepth: window.screen.pixelDepth
            },
            devicePixelRatio: window.devicePixelRatio,
            hardwareConcurrency: navigator.hardwareConcurrency,
            deviceMemory: navigator.deviceMemory
        };
        """
        return driver.execute_script(script)
    
    def _get_network_info(self, driver: WebDriver) -> Dict[str, Any]:
        """獲取網絡信息"""
        script = """
        return {
            connection: navigator.connection ? {
                effectiveType: navigator.connection.effectiveType,
                rtt: navigator.connection.rtt,
                downlink: navigator.connection.downlink
            } : null,
            onLine: navigator.onLine
        };
        """
        return driver.execute_script(script)
    
    def _get_plugin_info(self, driver: WebDriver) -> Dict[str, Any]:
        """獲取插件信息"""
        script = """
        return Array.from(navigator.plugins).map(plugin => ({
            name: plugin.name,
            description: plugin.description,
            filename: plugin.filename,
            version: plugin.version
        }));
        """
        return driver.execute_script(script)
    
    def _get_font_info(self, driver: WebDriver) -> Dict[str, Any]:
        """獲取字體信息"""
        script = """
        const fonts = [
            'Arial', 'Arial Black', 'Arial Narrow', 'Calibri', 'Cambria',
            'Cambria Math', 'Comic Sans MS', 'Courier', 'Courier New',
            'Georgia', 'Helvetica', 'Impact', 'Lucida Console',
            'Lucida Sans Unicode', 'Microsoft Sans Serif', 'Palatino Linotype',
            'Tahoma', 'Times', 'Times New Roman', 'Trebuchet MS',
            'Verdana', 'Wingdings'
        ];
        
        return fonts.map(font => {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            context.font = '12px ' + font;
            return {
                font: font,
                width: context.measureText('mmmmmmmmmm').width
            };
        });
        """
        return driver.execute_script(script)
    
    def _get_canvas_info(self, driver: WebDriver) -> Dict[str, Any]:
        """獲取Canvas信息"""
        script = """
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        // 繪製文本
        context.textBaseline = 'top';
        context.font = '14px Arial';
        context.fillStyle = '#f60';
        context.fillRect(125, 1, 62, 20);
        context.fillStyle = '#069';
        context.fillText('Browser Fingerprint', 2, 15);
        context.fillStyle = 'rgba(102, 204, 0, 0.7)';
        context.fillText('Browser Fingerprint', 4, 17);
        
        return canvas.toDataURL();
        """
        return driver.execute_script(script)
    
    def _get_webgl_info(self, driver: WebDriver) -> Dict[str, Any]:
        """獲取WebGL信息"""
        script = """
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        
        if (!gl) {
            return null;
        }
        
        return {
            vendor: gl.getParameter(gl.VENDOR),
            renderer: gl.getParameter(gl.RENDERER),
            version: gl.getParameter(gl.VERSION),
            shadingLanguageVersion: gl.getParameter(gl.SHADING_LANGUAGE_VERSION)
        };
        """
        return driver.execute_script(script)
    
    def _get_audio_info(self, driver: WebDriver) -> Dict[str, Any]:
        """獲取音頻信息"""
        script = """
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const analyser = audioContext.createAnalyser();
        const gainNode = audioContext.createGain();
        
        gainNode.gain.value = 0;
        oscillator.connect(analyser);
        analyser.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.start(0);
        
        const dataArray = new Float32Array(analyser.frequencyBinCount);
        analyser.getFloatFrequencyData(dataArray);
        
        return Array.from(dataArray);
        """
        return driver.execute_script(script)
    
    def _calculate_fingerprint_hash(self, fingerprint: Dict[str, Any]) -> str:
        """計算指紋哈希"""
        fingerprint_str = json.dumps(fingerprint, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()
    
    @handle_error
    def apply_fingerprint(
        self,
        driver: WebDriver,
        fingerprint: Dict[str, Any]
    ) -> bool:
        """
        應用瀏覽器指紋
        
        Args:
            driver: WebDriver實例
            fingerprint: 指紋數據
            
        Returns:
            是否成功應用
        """
        # 應用瀏覽器信息
        self._apply_browser_info(driver, fingerprint["browser"])
        
        # 應用系統信息
        self._apply_system_info(driver, fingerprint["system"])
        
        # 應用硬件信息
        self._apply_hardware_info(driver, fingerprint["hardware"])
        
        # 應用網絡信息
        self._apply_network_info(driver, fingerprint["network"])
        
        # 應用插件信息
        self._apply_plugin_info(driver, fingerprint["plugins"])
        
        # 應用字體信息
        self._apply_font_info(driver, fingerprint["fonts"])
        
        # 應用Canvas信息
        self._apply_canvas_info(driver, fingerprint["canvas"])
        
        # 應用WebGL信息
        self._apply_webgl_info(driver, fingerprint["webgl"])
        
        # 應用音頻信息
        self._apply_audio_info(driver, fingerprint["audio"])
        
        return True
    
    def _apply_browser_info(self, driver: WebDriver, info: Dict[str, Any]):
        """應用瀏覽器信息"""
        script = """
        Object.defineProperties(navigator, {
            userAgent: { value: arguments[0] },
            appName: { value: arguments[1] },
            appVersion: { value: arguments[2] },
            platform: { value: arguments[3] },
            language: { value: arguments[4] },
            languages: { value: arguments[5] },
            vendor: { value: arguments[6] },
            product: { value: arguments[7] },
            productSub: { value: arguments[8] },
            cookieEnabled: { value: arguments[9] },
            doNotTrack: { value: arguments[10] }
        });
        """
        driver.execute_script(
            script,
            info["userAgent"],
            info["appName"],
            info["appVersion"],
            info["platform"],
            info["language"],
            info["languages"],
            info["vendor"],
            info["product"],
            info["productSub"],
            info["cookieEnabled"],
            info["doNotTrack"]
        )
    
    def _apply_system_info(self, driver: WebDriver, info: Dict[str, Any]):
        """應用系統信息"""
        script = """
        Object.defineProperties(navigator, {
            platform: { value: arguments[0] },
            hardwareConcurrency: { value: arguments[1] },
            deviceMemory: { value: arguments[2] },
            maxTouchPoints: { value: arguments[3] }
        });
        """
        driver.execute_script(
            script,
            info["platform"],
            info["hardwareConcurrency"],
            info["deviceMemory"],
            info["maxTouchPoints"]
        )
    
    def _apply_hardware_info(self, driver: WebDriver, info: Dict[str, Any]):
        """應用硬件信息"""
        script = """
        Object.defineProperties(window.screen, {
            width: { value: arguments[0] },
            height: { value: arguments[1] },
            colorDepth: { value: arguments[2] },
            pixelDepth: { value: arguments[3] }
        });
        Object.defineProperty(window, 'devicePixelRatio', { value: arguments[4] });
        """
        driver.execute_script(
            script,
            info["screen"]["width"],
            info["screen"]["height"],
            info["screen"]["colorDepth"],
            info["screen"]["pixelDepth"],
            info["devicePixelRatio"]
        )
    
    def _apply_network_info(self, driver: WebDriver, info: Dict[str, Any]):
        """應用網絡信息"""
        script = """
        if (navigator.connection) {
            Object.defineProperties(navigator.connection, {
                effectiveType: { value: arguments[0] },
                rtt: { value: arguments[1] },
                downlink: { value: arguments[2] }
            });
        }
        Object.defineProperty(navigator, 'onLine', { value: arguments[3] });
        """
        connection = info["connection"]
        driver.execute_script(
            script,
            connection["effectiveType"] if connection else None,
            connection["rtt"] if connection else None,
            connection["downlink"] if connection else None,
            info["onLine"]
        )
    
    def _apply_plugin_info(self, driver: WebDriver, info: List[Dict[str, Any]]):
        """應用插件信息"""
        script = """
        const plugins = arguments[0];
        const mimeTypes = [];
        
        plugins.forEach(plugin => {
            const mimeType = {
                type: 'application/x-' + plugin.name.toLowerCase(),
                suffixes: '',
                description: plugin.description,
                enabledPlugin: plugin
            };
            mimeTypes.push(mimeType);
        });
        
        Object.defineProperty(navigator, 'plugins', {
            value: plugins,
            configurable: true
        });
        
        Object.defineProperty(navigator, 'mimeTypes', {
            value: mimeTypes,
            configurable: true
        });
        """
        driver.execute_script(script, info)
    
    def _apply_font_info(self, driver: WebDriver, info: List[Dict[str, Any]]):
        """應用字體信息"""
        script = """
        const fonts = arguments[0];
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        fonts.forEach(font => {
            context.font = '12px ' + font.font;
            const width = context.measureText('mmmmmmmmmm').width;
            Object.defineProperty(font, 'width', { value: width });
        });
        """
        driver.execute_script(script, info)
    
    def _apply_canvas_info(self, driver: WebDriver, info: str):
        """應用Canvas信息"""
        script = """
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        const img = new Image();
        img.src = arguments[0];
        context.drawImage(img, 0, 0);
        """
        driver.execute_script(script, info)
    
    def _apply_webgl_info(self, driver: WebDriver, info: Dict[str, Any]):
        """應用WebGL信息"""
        script = """
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        
        if (gl) {
            Object.defineProperties(gl, {
                VENDOR: { value: arguments[0] },
                RENDERER: { value: arguments[1] },
                VERSION: { value: arguments[2] },
                SHADING_LANGUAGE_VERSION: { value: arguments[3] }
            });
        }
        """
        driver.execute_script(
            script,
            info["vendor"],
            info["renderer"],
            info["version"],
            info["shadingLanguageVersion"]
        )
    
    def _apply_audio_info(self, driver: WebDriver, info: List[float]):
        """應用音頻信息"""
        script = """
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const analyser = audioContext.createAnalyser();
        const gainNode = audioContext.createGain();
        
        gainNode.gain.value = 0;
        analyser.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        const dataArray = new Float32Array(arguments[0]);
        analyser.getFloatFrequencyData(dataArray);
        """
        driver.execute_script(script, info)
    
    def get_fingerprint_report(self) -> Dict[str, Any]:
        """獲取指紋報告"""
        return {
            "total_fingerprints": len(self.fingerprint_history),
            "success_rate": sum(1 for r in self.fingerprint_history if r.success) / len(self.fingerprint_history),
            "fingerprint_types": self.fingerprint_stats,
            "recent_fingerprints": [r.to_dict() for r in self.fingerprint_history[-10:]]
        }
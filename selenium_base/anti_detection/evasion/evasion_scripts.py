#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
規避腳本模組

此模組提供各種規避腳本，包括：
1. WebGL 指紋規避
2. Canvas 指紋規避
3. Audio 指紋規避
4. 字體指紋規避
5. 插件指紋規避
6. 時區指紋規避
7. 語言指紋規避
8. 屏幕指紋規避
"""

from typing import Dict, Any, Optional

from .base_error import AntiDetectionError, handle_error

class EvasionScripts:
    """規避腳本類"""
    
    @staticmethod
    @handle_error()
    def get_webgl_evasion() -> str:
        """
        獲取 WebGL 指紋規避腳本
        
        Returns:
            WebGL 指紋規避腳本
        """
        return """
        // 覆蓋 WebGL 參數
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            // 偽裝 WebGL 參數
            if (parameter === 37445) {
                return 'Intel Open Source Technology Center';
            }
            if (parameter === 37446) {
                return 'Mesa DRI Intel(R) HD Graphics (SKL GT2)';
            }
            return getParameter.apply(this, arguments);
        };
        """
        
    @staticmethod
    @handle_error()
    def get_canvas_evasion() -> str:
        """
        獲取 Canvas 指紋規避腳本
        
        Returns:
            Canvas 指紋規避腳本
        """
        return """
        // 覆蓋 Canvas 方法
        const originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, attributes) {
            const context = originalGetContext.apply(this, arguments);
            if (type === '2d') {
                const originalGetImageData = context.getImageData;
                context.getImageData = function() {
                    const imageData = originalGetImageData.apply(this, arguments);
                    // 添加噪聲
                    for (let i = 0; i < imageData.data.length; i += 4) {
                        imageData.data[i] += Math.random() * 10 - 5;
                        imageData.data[i + 1] += Math.random() * 10 - 5;
                        imageData.data[i + 2] += Math.random() * 10 - 5;
                    }
                    return imageData;
                };
            }
            return context;
        };
        """
        
    @staticmethod
    @handle_error()
    def get_audio_evasion() -> str:
        """
        獲取 Audio 指紋規避腳本
        
        Returns:
            Audio 指紋規避腳本
        """
        return """
        // 覆蓋 Audio 方法
        const originalGetChannelData = AudioBuffer.prototype.getChannelData;
        AudioBuffer.prototype.getChannelData = function() {
            const channelData = originalGetChannelData.apply(this, arguments);
            // 添加噪聲
            for (let i = 0; i < channelData.length; i += 100) {
                channelData[i] += Math.random() * 0.01 - 0.005;
            }
            return channelData;
        };
        """
        
    @staticmethod
    @handle_error()
    def get_font_evasion() -> str:
        """
        獲取字體指紋規避腳本
        
        Returns:
            字體指紋規避腳本
        """
        return """
        // 覆蓋字體檢測
        const originalMatch = window.matchMedia;
        window.matchMedia = function(query) {
            if (query.includes('font-family')) {
                return {
                    matches: true,
                    media: query
                };
            }
            return originalMatch.apply(this, arguments);
        };
        """
        
    @staticmethod
    @handle_error()
    def get_plugin_evasion() -> str:
        """
        獲取插件指紋規避腳本
        
        Returns:
            插件指紋規避腳本
        """
        return """
        // 覆蓋插件檢測
        Object.defineProperty(navigator, 'plugins', {
            get: function() {
                return [
                    {
                        0: {
                            type: 'application/x-google-chrome-pdf',
                            suffixes: 'pdf',
                            description: 'Portable Document Format',
                            enabledPlugin: true
                        },
                        name: 'Chrome PDF Plugin',
                        filename: 'internal-pdf-viewer',
                        description: 'Portable Document Format',
                        length: 1
                    }
                ];
            }
        });
        """
        
    @staticmethod
    @handle_error()
    def get_timezone_evasion() -> str:
        """
        獲取時區指紋規避腳本
        
        Returns:
            時區指紋規避腳本
        """
        return """
        // 覆蓋時區檢測
        const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
        Date.prototype.getTimezoneOffset = function() {
            return -480; // 固定為 UTC+8
        };
        """
        
    @staticmethod
    @handle_error()
    def get_language_evasion() -> str:
        """
        獲取語言指紋規避腳本
        
        Returns:
            語言指紋規避腳本
        """
        return """
        // 覆蓋語言檢測
        Object.defineProperty(navigator, 'language', {
            get: function() {
                return 'zh-CN';
            }
        });
        """
        
    @staticmethod
    @handle_error()
    def get_screen_evasion() -> str:
        """
        獲取屏幕指紋規避腳本
        
        Returns:
            屏幕指紋規避腳本
        """
        return """
        // 覆蓋屏幕檢測
        Object.defineProperty(window, 'screen', {
            get: function() {
                return {
                    width: 1920,
                    height: 1080,
                    colorDepth: 24,
                    pixelDepth: 24
                };
            }
        });
        """
        
    @classmethod
    @handle_error()
    def get_all_evasions(cls) -> Dict[str, str]:
        """
        獲取所有規避腳本
        
        Returns:
            規避腳本字典
        """
        return {
            'webgl': cls.get_webgl_evasion(),
            'canvas': cls.get_canvas_evasion(),
            'audio': cls.get_audio_evasion(),
            'font': cls.get_font_evasion(),
            'plugin': cls.get_plugin_evasion(),
            'timezone': cls.get_timezone_evasion(),
            'language': cls.get_language_evasion(),
            'screen': cls.get_screen_evasion()
        } 
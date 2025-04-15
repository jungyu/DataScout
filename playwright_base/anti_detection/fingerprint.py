#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
指紋管理模組

此模組提供指紋管理功能，包括：
1. 指紋生成
2. 指紋注入
3. 指紋驗證
4. 指紋更新
"""

from typing import Dict, Any, Optional, List
import random
from loguru import logger

from ..utils.exceptions import AntiDetectionException
from .webgl_spoofer import WebGLSpoofer
from .canvas_spoofer import CanvasSpoofer
from .audio_spoofer import AudioSpoofer


class FingerprintManager:
    """指紋管理器"""
    
    def __init__(self):
        """初始化指紋管理器"""
        self.webgl_spoofer = WebGLSpoofer()
        self.canvas_spoofer = CanvasSpoofer()
        self.audio_spoofer = AudioSpoofer()
        
        # 指紋配置
        self.fingerprint_config = {
            'webgl': True,
            'canvas': True,
            'audio': True,
            'font': True,
            'screen': True,
            'platform': True
        }
    
    def set_fingerprint_config(self, config: Dict[str, bool]) -> None:
        """
        設置指紋配置
        
        Args:
            config: 指紋配置字典
        """
        self.fingerprint_config.update(config)
    
    def get_random_fingerprint(self) -> Dict[str, Any]:
        """
        獲取隨機指紋
        
        Returns:
            Dict[str, Any]: 指紋信息
        """
        fingerprint = {}
        
        if self.fingerprint_config.get('webgl', True):
            fingerprint['webgl'] = self.webgl_spoofer.get_random_webgl_fingerprint()
        
        if self.fingerprint_config.get('canvas', True):
            fingerprint['canvas'] = self.canvas_spoofer.get_random_canvas_fingerprint()
        
        if self.fingerprint_config.get('audio', True):
            fingerprint['audio'] = self.audio_spoofer.get_random_audio_fingerprint()
        
        if self.fingerprint_config.get('font', True):
            fingerprint['font'] = self._get_random_font_fingerprint()
        
        if self.fingerprint_config.get('screen', True):
            fingerprint['screen'] = self._get_random_screen_fingerprint()
        
        if self.fingerprint_config.get('platform', True):
            fingerprint['platform'] = self._get_random_platform_fingerprint()
        
        return fingerprint
    
    def get_consistent_fingerprint(self) -> Dict[str, Any]:
        """
        獲取一致的指紋（每次調用返回相同的指紋）
        
        Returns:
            Dict[str, Any]: 指紋信息
        """
        fingerprint = {}
        
        if self.fingerprint_config.get('webgl', True):
            fingerprint['webgl'] = self.webgl_spoofer.get_consistent_webgl_fingerprint()
        
        if self.fingerprint_config.get('canvas', True):
            fingerprint['canvas'] = self.canvas_spoofer.get_consistent_canvas_fingerprint()
        
        if self.fingerprint_config.get('audio', True):
            fingerprint['audio'] = self.audio_spoofer.get_consistent_audio_fingerprint()
        
        if self.fingerprint_config.get('font', True):
            fingerprint['font'] = self._get_consistent_font_fingerprint()
        
        if self.fingerprint_config.get('screen', True):
            fingerprint['screen'] = self._get_consistent_screen_fingerprint()
        
        if self.fingerprint_config.get('platform', True):
            fingerprint['platform'] = self._get_consistent_platform_fingerprint()
        
        return fingerprint
    
    def apply_fingerprint(self, page) -> None:
        """
        應用指紋到頁面
        
        Args:
            page: Playwright 頁面對象
        """
        try:
            # 應用 WebGL 指紋偽裝
            if self.fingerprint_config.get('webgl', True):
                self.webgl_spoofer.apply_spoof(page)
            
            # 應用 Canvas 指紋偽裝
            if self.fingerprint_config.get('canvas', True):
                self.canvas_spoofer.apply_spoof(page)
            
            # 應用音頻指紋偽裝
            if self.fingerprint_config.get('audio', True):
                self.audio_spoofer.apply_spoof(page)
            
            # 應用字體指紋偽裝
            if self.fingerprint_config.get('font', True):
                self._apply_font_spoof(page)
            
            # 應用屏幕指紋偽裝
            if self.fingerprint_config.get('screen', True):
                self._apply_screen_spoof(page)
            
            # 應用平台指紋偽裝
            if self.fingerprint_config.get('platform', True):
                self._apply_platform_spoof(page)
            
            logger.info("已應用所有指紋偽裝")
        except Exception as e:
            logger.error(f"應用指紋偽裝時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"應用指紋偽裝失敗: {str(e)}")
    
    def _get_random_font_fingerprint(self) -> Dict[str, Any]:
        """
        獲取隨機字體指紋
        
        Returns:
            Dict[str, Any]: 字體指紋信息
        """
        fonts = [
            "Arial", "Arial Black", "Arial Narrow", "Calibri", "Cambria", "Cambria Math",
            "Comic Sans MS", "Courier", "Courier New", "Georgia", "Helvetica", "Impact",
            "Lucida Console", "Lucida Sans Unicode", "Microsoft Sans Serif", "Palatino Linotype",
            "Tahoma", "Times", "Times New Roman", "Trebuchet MS", "Verdana"
        ]
        
        return {
            "fonts": random.sample(fonts, random.randint(10, 20)),
            "font_size": random.randint(12, 16),
            "font_color": f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}",
            "font_weight": random.choice(["normal", "bold"]),
            "font_style": random.choice(["normal", "italic"])
        }
    
    def _get_consistent_font_fingerprint(self) -> Dict[str, Any]:
        """
        獲取一致的字體指紋
        
        Returns:
            Dict[str, Any]: 字體指紋信息
        """
        fonts = [
            "Arial", "Arial Black", "Arial Narrow", "Calibri", "Cambria", "Cambria Math",
            "Comic Sans MS", "Courier", "Courier New", "Georgia", "Helvetica", "Impact",
            "Lucida Console", "Lucida Sans Unicode", "Microsoft Sans Serif", "Palatino Linotype",
            "Tahoma", "Times", "Times New Roman", "Trebuchet MS", "Verdana"
        ]
        
        return {
            "fonts": fonts[:15],
            "font_size": 14,
            "font_color": "#000000",
            "font_weight": "normal",
            "font_style": "normal"
        }
    
    def _apply_font_spoof(self, page) -> None:
        """
        應用字體指紋偽裝
        
        Args:
            page: Playwright 頁面對象
        """
        try:
            fingerprint = self._get_consistent_font_fingerprint()
            
            script = f"""
            // 修改字體檢測
            const measureText = CanvasRenderingContext2D.prototype.measureText;
            CanvasRenderingContext2D.prototype.measureText = function(text) {{
                const metrics = measureText.apply(this, arguments);
                // 添加隨機寬度偏移
                metrics.width = metrics.width + Math.random() * 2 - 1;
                return metrics;
            }};
            
            // 修改字體列表
            Object.defineProperty(navigator, 'fonts', {{
                get: function() {{
                    return {fingerprint['fonts']};
                }}
            }});
            """
            
            page.add_init_script(script)
            logger.info("已應用字體指紋偽裝")
        except Exception as e:
            logger.error(f"應用字體指紋偽裝時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"應用字體指紋偽裝失敗: {str(e)}")
    
    def _get_random_screen_fingerprint(self) -> Dict[str, Any]:
        """
        獲取隨機屏幕指紋
        
        Returns:
            Dict[str, Any]: 屏幕指紋信息
        """
        widths = [1366, 1440, 1536, 1600, 1680, 1920, 2560]
        heights = [768, 900, 864, 900, 1050, 1080, 1440]
        
        width = random.choice(widths)
        height = random.choice(heights)
        
        return {
            "width": width,
            "height": height,
            "colorDepth": random.choice([24, 32]),
            "pixelDepth": random.choice([24, 32]),
            "availWidth": width,
            "availHeight": height - random.randint(30, 80),
            "devicePixelRatio": random.choice([1, 1.25, 1.5, 2, 2.5, 3])
        }
    
    def _get_consistent_screen_fingerprint(self) -> Dict[str, Any]:
        """
        獲取一致的屏幕指紋
        
        Returns:
            Dict[str, Any]: 屏幕指紋信息
        """
        return {
            "width": 1920,
            "height": 1080,
            "colorDepth": 24,
            "pixelDepth": 24,
            "availWidth": 1920,
            "availHeight": 1040,
            "devicePixelRatio": 1
        }
    
    def _apply_screen_spoof(self, page) -> None:
        """
        應用屏幕指紋偽裝
        
        Args:
            page: Playwright 頁面對象
        """
        try:
            fingerprint = self._get_consistent_screen_fingerprint()
            
            script = f"""
            // 修改屏幕屬性
            Object.defineProperty(window, 'screen', {{
                get: function() {{
                    const screen = {{
                        width: {fingerprint['width']},
                        height: {fingerprint['height']},
                        colorDepth: {fingerprint['colorDepth']},
                        pixelDepth: {fingerprint['pixelDepth']},
                        availWidth: {fingerprint['availWidth']},
                        availHeight: {fingerprint['availHeight']},
                        devicePixelRatio: {fingerprint['devicePixelRatio']}
                    }};
                    return screen;
                }}
            }});
            """
            
            page.add_init_script(script)
            logger.info("已應用屏幕指紋偽裝")
        except Exception as e:
            logger.error(f"應用屏幕指紋偽裝時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"應用屏幕指紋偽裝失敗: {str(e)}")
    
    def _get_random_platform_fingerprint(self) -> Dict[str, Any]:
        """
        獲取隨機平台指紋
        
        Returns:
            Dict[str, Any]: 平台指紋信息
        """
        platforms = ["Win32", "MacIntel", "Linux x86_64"]
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux i686; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        
        languages = ["en-US", "en-GB", "fr-FR", "de-DE", "es-ES", "it-IT", "ja-JP", "zh-CN", "zh-TW"]
        
        return {
            "platform": random.choice(platforms),
            "userAgent": random.choice(user_agents),
            "language": random.choice(languages),
            "languages": random.sample(languages, random.randint(1, 3)),
            "timezone": random.randint(-12, 12)
        }
    
    def _get_consistent_platform_fingerprint(self) -> Dict[str, Any]:
        """
        獲取一致的平台指紋
        
        Returns:
            Dict[str, Any]: 平台指紋信息
        """
        return {
            "platform": "MacIntel",
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "language": "en-US",
            "languages": ["en-US", "en-GB"],
            "timezone": 0
        }
    
    def _apply_platform_spoof(self, page) -> None:
        """
        應用平台指紋偽裝
        
        Args:
            page: Playwright 頁面對象
        """
        try:
            fingerprint = self._get_consistent_platform_fingerprint()
            
            script = f"""
            // 修改平台屬性
            Object.defineProperty(navigator, 'platform', {{
                get: function() {{
                    return '{fingerprint['platform']}';
                }}
            }});
            
            Object.defineProperty(navigator, 'userAgent', {{
                get: function() {{
                    return '{fingerprint['userAgent']}';
                }}
            }});
            
            Object.defineProperty(navigator, 'language', {{
                get: function() {{
                    return '{fingerprint['language']}';
                }}
            }});
            
            Object.defineProperty(navigator, 'languages', {{
                get: function() {{
                    return {fingerprint['languages']};
                }}
            }});
            
            // 修改時區
            Date.prototype.getTimezoneOffset = function() {{
                return {fingerprint['timezone']} * 60;
            }};
            """
            
            page.add_init_script(script)
            logger.info("已應用平台指紋偽裝")
        except Exception as e:
            logger.error(f"應用平台指紋偽裝時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"應用平台指紋偽裝失敗: {str(e)}") 
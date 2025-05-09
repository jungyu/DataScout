#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
螢幕指紋偽裝模組

此模組提供螢幕指紋偽裝功能，包括：
1. 螢幕分辨率偽裝
2. 螢幕方向偽裝
3. 螢幕像素比偽裝
4. 螢幕顏色深度偽裝
"""

from typing import Dict, Any, List
import random
from loguru import logger

from ..utils.exceptions import AntiDetectionException


class ScreenSpoofer:
    """螢幕指紋偽裝器"""
    
    def __init__(self):
        """初始化螢幕指紋偽裝器"""
        # 常見螢幕分辨率
        self.resolutions = [
            (1920, 1080),  # Full HD
            (2560, 1440),  # 2K
            (3840, 2160),  # 4K
            (1366, 768),   # 筆記本
            (1440, 900),   # 筆記本
            (1536, 864),   # 筆記本
            (1680, 1050),  # 筆記本
            (2880, 1800),  # Retina
            (3200, 1800),  # QHD+
            (2560, 1600)   # WQXGA
        ]
        
        # 螢幕方向
        self.orientations = ["portrait-primary", "portrait-secondary", "landscape-primary", "landscape-secondary"]
        
        # 螢幕像素比
        self.pixel_ratios = [1, 1.25, 1.5, 2, 2.5, 3, 4]
        
        # 螢幕顏色深度
        self.color_depths = [24, 30, 32, 48]
        
        # 螢幕刷新率
        self.refresh_rates = [60, 75, 90, 120, 144, 165, 240]
        
        # 螢幕亮度
        self.brightness_levels = {
            "min": 0.3,
            "max": 1.0
        }
        
        # 螢幕對比度
        self.contrast_levels = {
            "min": 0.8,
            "max": 1.2
        }
    
    def get_random_screen_fingerprint(self) -> Dict[str, Any]:
        """
        獲取隨機螢幕指紋
        
        Returns:
            Dict[str, Any]: 螢幕指紋信息
        """
        width, height = random.choice(self.resolutions)
        return {
            "width": width,
            "height": height,
            "orientation": random.choice(self.orientations),
            "pixelRatio": random.choice(self.pixel_ratios),
            "colorDepth": random.choice(self.color_depths),
            "refreshRate": random.choice(self.refresh_rates),
            "brightness": random.uniform(self.brightness_levels["min"], self.brightness_levels["max"]),
            "contrast": random.uniform(self.contrast_levels["min"], self.contrast_levels["max"])
        }
    
    def get_consistent_screen_fingerprint(self) -> Dict[str, Any]:
        """
        獲取一致的螢幕指紋（每次調用返回相同的指紋）
        
        Returns:
            Dict[str, Any]: 螢幕指紋信息
        """
        return {
            "width": 1920,
            "height": 1080,
            "orientation": "landscape-primary",
            "pixelRatio": 1,
            "colorDepth": 24,
            "refreshRate": 60,
            "brightness": 1.0,
            "contrast": 1.0
        }
    
    def apply_spoof(self, page) -> None:
        """
        應用螢幕指紋偽裝
        
        Args:
            page: Playwright 頁面對象
        """
        try:
            fingerprint = self.get_consistent_screen_fingerprint()
            
            script = f"""
            // 修改螢幕屬性
            Object.defineProperties(window.screen, {{
                width: {{
                    get: function() {{
                        return {fingerprint["width"]};
                    }}
                }},
                height: {{
                    get: function() {{
                        return {fingerprint["height"]};
                    }}
                }},
                availWidth: {{
                    get: function() {{
                        return {fingerprint["width"]};
                    }}
                }},
                availHeight: {{
                    get: function() {{
                        return {fingerprint["height"]};
                    }}
                }},
                colorDepth: {{
                    get: function() {{
                        return {fingerprint["colorDepth"]};
                    }}
                }},
                pixelDepth: {{
                    get: function() {{
                        return {fingerprint["colorDepth"]};
                    }}
                }},
                orientation: {{
                    get: function() {{
                        return {{
                            type: '{fingerprint["orientation"]}',
                            angle: 0
                        }};
                    }}
                }}
            }});
            
            // 修改設備像素比
            Object.defineProperty(window, 'devicePixelRatio', {{
                get: function() {{
                    return {fingerprint["pixelRatio"]};
                }}
            }});
            
            // 修改螢幕媒體查詢
            const originalMatchMedia = window.matchMedia;
            window.matchMedia = function(query) {{
                if (query.includes('resolution') || query.includes('aspect-ratio')) {{
                    return {{
                        matches: true,
                        media: query,
                        onchange: null,
                        addListener: function() {{}},
                        removeListener: function() {{}},
                        addEventListener: function() {{}},
                        removeEventListener: function() {{}},
                        dispatchEvent: function() {{ return true; }}
                    }};
                }}
                return originalMatchMedia.apply(this, arguments);
            }};
            
            // 修改螢幕事件
            const originalAddEventListener = window.addEventListener;
            window.addEventListener = function(type, listener, options) {{
                if (type === 'resize' || type === 'orientationchange') {{
                    return;
                }}
                return originalAddEventListener.apply(this, arguments);
            }};
            
            // 修改螢幕 CSS 媒體查詢
            const style = document.createElement('style');
            style.textContent = `
                @media screen {{
                    width: {fingerprint["width"]}px !important;
                    height: {fingerprint["height"]}px !important;
                    aspect-ratio: {fingerprint["width"]}/{fingerprint["height"]} !important;
                    resolution: {fingerprint["pixelRatio"]}dppx !important;
                    color: {fingerprint["colorDepth"]}bit !important;
                }}
            `;
            document.head.appendChild(style);
            """
            
            page.add_init_script(script)
            logger.info("已應用螢幕指紋偽裝")
        except Exception as e:
            logger.error(f"應用螢幕指紋偽裝時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"應用螢幕指紋偽裝失敗: {str(e)}") 
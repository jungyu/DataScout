#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
字體指紋偽裝模組

此模組提供字體指紋偽裝功能，包括：
1. 字體列表偽裝
2. 字體度量偽裝
3. 字體渲染偽裝
"""

from typing import Dict, Any, List
import random
from loguru import logger

from ..utils.exceptions import AntiDetectionException


class FontSpoofer:
    """字體指紋偽裝器"""
    
    def __init__(self):
        """初始化字體指紋偽裝器"""
        # 常用字體列表
        self.common_fonts = [
            "Arial", "Arial Black", "Arial Narrow", "Calibri", "Cambria", "Cambria Math",
            "Comic Sans MS", "Courier", "Courier New", "Georgia", "Helvetica", "Impact",
            "Lucida Console", "Lucida Sans Unicode", "Microsoft Sans Serif", "Palatino Linotype",
            "Tahoma", "Times", "Times New Roman", "Trebuchet MS", "Verdana"
        ]
        
        # 字體樣式
        self.font_styles = ["normal", "italic", "oblique"]
        
        # 字體粗細
        self.font_weights = ["normal", "bold", "100", "200", "300", "400", "500", "600", "700", "800", "900"]
        
        # 字體變體
        self.font_variants = ["normal", "small-caps"]
        
        # 字體拉伸
        self.font_stretches = [
            "normal", "ultra-condensed", "extra-condensed", "condensed", "semi-condensed",
            "semi-expanded", "expanded", "extra-expanded", "ultra-expanded"
        ]
        
        # 字體度量參數
        self.metrics = {
            "ascent": {"min": 0.7, "max": 0.9},
            "descent": {"min": 0.1, "max": 0.3},
            "lineGap": {"min": 0, "max": 0.2},
            "unitsPerEm": {"min": 1000, "max": 2048},
            "xHeight": {"min": 0.4, "max": 0.6},
            "capHeight": {"min": 0.6, "max": 0.8}
        }
    
    def get_random_font_fingerprint(self) -> Dict[str, Any]:
        """
        獲取隨機字體指紋
        
        Returns:
            Dict[str, Any]: 字體指紋信息
        """
        return {
            "fonts": random.sample(self.common_fonts, random.randint(5, 10)),
            "style": random.choice(self.font_styles),
            "weight": random.choice(self.font_weights),
            "variant": random.choice(self.font_variants),
            "stretch": random.choice(self.font_stretches),
            "metrics": {
                "ascent": random.uniform(self.metrics["ascent"]["min"], self.metrics["ascent"]["max"]),
                "descent": random.uniform(self.metrics["descent"]["min"], self.metrics["descent"]["max"]),
                "lineGap": random.uniform(self.metrics["lineGap"]["min"], self.metrics["lineGap"]["max"]),
                "unitsPerEm": random.randint(self.metrics["unitsPerEm"]["min"], self.metrics["unitsPerEm"]["max"]),
                "xHeight": random.uniform(self.metrics["xHeight"]["min"], self.metrics["xHeight"]["max"]),
                "capHeight": random.uniform(self.metrics["capHeight"]["min"], self.metrics["capHeight"]["max"])
            }
        }
    
    def get_consistent_font_fingerprint(self) -> Dict[str, Any]:
        """
        獲取一致的字體指紋（每次調用返回相同的指紋）
        
        Returns:
            Dict[str, Any]: 字體指紋信息
        """
        return {
            "fonts": self.common_fonts[:5],
            "style": "normal",
            "weight": "normal",
            "variant": "normal",
            "stretch": "normal",
            "metrics": {
                "ascent": 0.8,
                "descent": 0.2,
                "lineGap": 0.1,
                "unitsPerEm": 2048,
                "xHeight": 0.5,
                "capHeight": 0.7
            }
        }
    
    def apply_spoof(self, page) -> None:
        """
        應用字體指紋偽裝
        
        Args:
            page: Playwright 頁面對象
        """
        try:
            fingerprint = self.get_consistent_font_fingerprint()
            
            script = f"""
            // 修改字體檢測方法
            const originalMatchMedia = window.matchMedia;
            window.matchMedia = function(query) {{
                if (query.includes('font-family')) {{
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
            
            // 修改字體度量方法
            const originalGetComputedStyle = window.getComputedStyle;
            window.getComputedStyle = function(element, pseudoElt) {{
                const style = originalGetComputedStyle.apply(this, arguments);
                
                // 修改字體相關屬性
                Object.defineProperties(style, {{
                    fontFamily: {{
                        get: function() {{
                            return '{fingerprint["fonts"][0]}';
                        }}
                    }},
                    fontStyle: {{
                        get: function() {{
                            return '{fingerprint["style"]}';
                        }}
                    }},
                    fontWeight: {{
                        get: function() {{
                            return '{fingerprint["weight"]}';
                        }}
                    }},
                    fontVariant: {{
                        get: function() {{
                            return '{fingerprint["variant"]}';
                        }}
                    }},
                    fontStretch: {{
                        get: function() {{
                            return '{fingerprint["stretch"]}';
                        }}
                    }}
                }});
                
                return style;
            }};
            
            // 修改字體度量 API
            if (window.FontFace) {{
                const originalFontFace = window.FontFace;
                window.FontFace = function(family, source, descriptors) {{
                    const font = new originalFontFace(family, source, descriptors);
                    
                    // 修改字體度量
                    Object.defineProperties(font, {{
                        ascent: {{
                            get: function() {{
                                return {fingerprint["metrics"]["ascent"]};
                            }}
                        }},
                        descent: {{
                            get: function() {{
                                return {fingerprint["metrics"]["descent"]};
                            }}
                        }},
                        lineGap: {{
                            get: function() {{
                                return {fingerprint["metrics"]["lineGap"]};
                            }}
                        }},
                        unitsPerEm: {{
                            get: function() {{
                                return {fingerprint["metrics"]["unitsPerEm"]};
                            }}
                        }},
                        xHeight: {{
                            get: function() {{
                                return {fingerprint["metrics"]["xHeight"]};
                            }}
                        }},
                        capHeight: {{
                            get: function() {{
                                return {fingerprint["metrics"]["capHeight"]};
                            }}
                        }}
                    }});
                    
                    return font;
                }};
            }}
            
            // 修改字體列表檢測
            const originalQuerySelectorAll = document.querySelectorAll;
            document.querySelectorAll = function(selectors) {{
                if (selectors.includes('@font-face')) {{
                    return [];
                }}
                return originalQuerySelectorAll.apply(this, arguments);
            }};
            """
            
            page.add_init_script(script)
            logger.info("已應用字體指紋偽裝")
        except Exception as e:
            logger.error(f"應用字體指紋偽裝時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"應用字體指紋偽裝失敗: {str(e)}") 
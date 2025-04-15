#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Canvas 指紋偽裝模組

此模組提供 Canvas 指紋偽裝功能，包括：
1. Canvas 繪圖操作偽裝
2. Canvas 圖像數據偽裝
3. Canvas 字體渲染偽裝
"""

from typing import Dict, Any, List
import random
from loguru import logger

from ..utils.exceptions import AntiDetectionException


class CanvasSpoofer:
    """Canvas 指紋偽裝器"""
    
    def __init__(self):
        """初始化 Canvas 指紋偽裝器"""
        # 字體列表
        self.fonts = [
            "Arial", "Arial Black", "Arial Narrow", "Calibri", "Cambria", "Cambria Math",
            "Comic Sans MS", "Courier", "Courier New", "Georgia", "Helvetica", "Impact",
            "Lucida Console", "Lucida Sans Unicode", "Microsoft Sans Serif", "Palatino Linotype",
            "Tahoma", "Times", "Times New Roman", "Trebuchet MS", "Verdana"
        ]
        
        # 顏色列表
        self.colors = [
            "#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF",
            "#FFFF00", "#00FFFF", "#FF00FF", "#808080", "#800000",
            "#808000", "#008000", "#800080", "#008080", "#000080"
        ]
        
        # 圖案列表
        self.patterns = [
            "rect", "arc", "line", "text", "image",
            "gradient", "shadow", "path", "curve", "circle"
        ]
    
    def get_random_canvas_fingerprint(self) -> Dict[str, Any]:
        """
        獲取隨機 Canvas 指紋
        
        Returns:
            Dict[str, Any]: Canvas 指紋信息
        """
        return {
            "fonts": random.sample(self.fonts, random.randint(5, 10)),
            "colors": random.sample(self.colors, random.randint(3, 7)),
            "patterns": random.sample(self.patterns, random.randint(3, 5)),
            "noise": random.uniform(0.1, 0.5),
            "text_offset": random.uniform(-1, 1),
            "pattern_offset": random.uniform(-2, 2)
        }
    
    def get_consistent_canvas_fingerprint(self) -> Dict[str, Any]:
        """
        獲取一致的 Canvas 指紋（每次調用返回相同的指紋）
        
        Returns:
            Dict[str, Any]: Canvas 指紋信息
        """
        return {
            "fonts": self.fonts[:5],
            "colors": self.colors[:3],
            "patterns": self.patterns[:3],
            "noise": 0.2,
            "text_offset": 0.5,
            "pattern_offset": 1.0
        }
    
    def apply_spoof(self, page) -> None:
        """
        應用 Canvas 指紋偽裝
        
        Args:
            page: Playwright 頁面對象
        """
        try:
            fingerprint = self.get_consistent_canvas_fingerprint()
            
            script = f"""
            // 修改 Canvas 繪圖操作
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(contextType, contextAttributes) {{
                const context = originalGetContext.apply(this, arguments);
                if (contextType === '2d') {{
                    // 修改 fillText 方法
                    const originalFillText = context.fillText;
                    context.fillText = function(text, x, y, maxWidth) {{
                        // 添加隨機偏移
                        x = x + {fingerprint['text_offset']};
                        y = y + {fingerprint['text_offset']};
                        return originalFillText.apply(this, [text, x, y, maxWidth]);
                    }};
                    
                    // 修改 strokeText 方法
                    const originalStrokeText = context.strokeText;
                    context.strokeText = function(text, x, y, maxWidth) {{
                        // 添加隨機偏移
                        x = x + {fingerprint['text_offset']};
                        y = y + {fingerprint['text_offset']};
                        return originalStrokeText.apply(this, [text, x, y, maxWidth]);
                    }};
                    
                    // 修改 measureText 方法
                    const originalMeasureText = context.measureText;
                    context.measureText = function(text) {{
                        const metrics = originalMeasureText.apply(this, arguments);
                        // 添加隨機寬度偏移
                        metrics.width = metrics.width + {fingerprint['text_offset']};
                        return metrics;
                    }};
                    
                    // 修改 fillRect 方法
                    const originalFillRect = context.fillRect;
                    context.fillRect = function(x, y, width, height) {{
                        // 添加隨機偏移
                        x = x + {fingerprint['pattern_offset']};
                        y = y + {fingerprint['pattern_offset']};
                        return originalFillRect.apply(this, [x, y, width, height]);
                    }};
                    
                    // 修改 strokeRect 方法
                    const originalStrokeRect = context.strokeRect;
                    context.strokeRect = function(x, y, width, height) {{
                        // 添加隨機偏移
                        x = x + {fingerprint['pattern_offset']};
                        y = y + {fingerprint['pattern_offset']};
                        return originalStrokeRect.apply(this, [x, y, width, height]);
                    }};
                    
                    // 修改 arc 方法
                    const originalArc = context.arc;
                    context.arc = function(x, y, radius, startAngle, endAngle, counterclockwise) {{
                        // 添加隨機偏移
                        x = x + {fingerprint['pattern_offset']};
                        y = y + {fingerprint['pattern_offset']};
                        return originalArc.apply(this, [x, y, radius, startAngle, endAngle, counterclockwise]);
                    }};
                    
                    // 修改 getImageData 方法
                    const originalGetImageData = context.getImageData;
                    context.getImageData = function(sx, sy, sw, sh) {{
                        const imageData = originalGetImageData.apply(this, arguments);
                        // 添加噪聲
                        for (let i = 0; i < imageData.data.length; i += 4) {{
                            imageData.data[i] = imageData.data[i] + Math.random() * {fingerprint['noise']} * 255;
                            imageData.data[i + 1] = imageData.data[i + 1] + Math.random() * {fingerprint['noise']} * 255;
                            imageData.data[i + 2] = imageData.data[i + 2] + Math.random() * {fingerprint['noise']} * 255;
                        }}
                        return imageData;
                    }};
                }}
                return context;
            }};
            
            // 修改 toDataURL 方法
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type, quality) {{
                const context = this.getContext('2d');
                if (context) {{
                    // 在獲取數據之前添加一些隨機繪圖操作
                    const width = this.width;
                    const height = this.height;
                    
                    // 隨機選擇一個圖案
                    const pattern = {fingerprint['patterns']}[Math.floor(Math.random() * {len(fingerprint['patterns'])}];
                    
                    // 根據圖案類型進行繪圖
                    switch (pattern) {{
                        case 'rect':
                            context.fillRect(
                                Math.random() * width,
                                Math.random() * height,
                                Math.random() * 10,
                                Math.random() * 10
                            );
                            break;
                        case 'arc':
                            context.beginPath();
                            context.arc(
                                Math.random() * width,
                                Math.random() * height,
                                Math.random() * 5,
                                0,
                                Math.PI * 2
                            );
                            context.fill();
                            break;
                        case 'text':
                            context.fillText(
                                'Canvas Fingerprint',
                                Math.random() * width,
                                Math.random() * height
                            );
                            break;
                    }}
                }}
                return originalToDataURL.apply(this, arguments);
            }};
            """
            
            page.add_init_script(script)
            logger.info("已應用 Canvas 指紋偽裝")
        except Exception as e:
            logger.error(f"應用 Canvas 指紋偽裝時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"應用 Canvas 指紋偽裝失敗: {str(e)}") 
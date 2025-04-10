"""
瀏覽器指紋生成器模組
"""

import random
import json
from typing import Dict, Any

from ..configs.anti_fingerprint_config import AntiFingerprintConfig

class FingerprintGenerator:
    """瀏覽器指紋生成器類"""
    
    def __init__(self, config: AntiFingerprintConfig):
        """
        初始化指紋生成器
        
        Args:
            config: 反指紋檢測配置
        """
        self.config = config
    
    def generate_fingerprint(self) -> Dict[str, Any]:
        """
        生成瀏覽器指紋
        
        Returns:
            包含瀏覽器指紋信息的字典
        """
        return {
            'userAgent': self.config.user_agent,
            'webgl': self._generate_webgl_fingerprint(),
            'canvas': self._generate_canvas_fingerprint(),
            'fonts': self._generate_fonts_list(),
            'screen': self._generate_screen_info(),
            'navigator': self._generate_navigator_info()
        }
    
    def _generate_webgl_fingerprint(self) -> Dict[str, Any]:
        """生成 WebGL 指紋"""
        return {
            'vendor': random.choice([
                'Google Inc. (NVIDIA)',
                'Google Inc. (Intel)',
                'Google Inc. (AMD)',
                'Apple GPU'
            ]),
            'renderer': random.choice([
                'ANGLE (NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0)',
                'ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0)',
                'ANGLE (AMD Radeon RX 580 Direct3D11 vs_5_0)',
                'Apple M1'
            ]),
            'noise': self.config.webgl_noise
        }
    
    def _generate_canvas_fingerprint(self) -> Dict[str, Any]:
        """生成 Canvas 指紋"""
        return {
            'noise': self.config.canvas_noise,
            'width': self.config.window_size[0],
            'height': self.config.window_size[1]
        }
    
    def _generate_fonts_list(self) -> list:
        """生成字體列表"""
        common_fonts = [
            'Arial', 'Helvetica', 'Times New Roman', 'Times', 'Courier New',
            'Courier', 'Verdana', 'Georgia', 'Palatino', 'Garamond', 'Bookman',
            'Comic Sans MS', 'Trebuchet MS', 'Arial Black'
        ]
        return random.sample(common_fonts, random.randint(8, 12))
    
    def _generate_screen_info(self) -> Dict[str, int]:
        """生成屏幕信息"""
        return {
            'width': self.config.window_size[0],
            'height': self.config.window_size[1],
            'colorDepth': random.choice([24, 32]),
            'pixelDepth': random.choice([24, 32])
        }
    
    def _generate_navigator_info(self) -> Dict[str, Any]:
        """生成導航器信息"""
        return {
            'platform': random.choice(['Win32', 'MacIntel', 'Linux x86_64']),
            'language': random.choice(['zh-CN', 'en-US', 'ja-JP']),
            'languages': ['zh-CN', 'en-US'],
            'doNotTrack': random.choice(['1', None]),
            'cookieEnabled': True,
            'webdriver': False
        }
    
    def to_json(self) -> str:
        """
        將指紋信息轉換為 JSON 字符串
        
        Returns:
            JSON 格式的指紋信息
        """
        return json.dumps(self.generate_fingerprint(), indent=2) 
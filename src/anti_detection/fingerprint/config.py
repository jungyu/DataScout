"""
瀏覽器指紋生成配置模塊
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class AntiFingerprintConfig:
    """瀏覽器指紋生成配置類"""
    
    # WebGL 配置
    webgl_vendor: str = "Google Inc. (NVIDIA)"
    webgl_renderer: str = "ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 Direct3D11 vs_5_0 ps_5_0, D3D11)"
    webgl_version: str = "WebGL GLSL ES 1.0"
    
    # Canvas 配置
    canvas_noise: float = 0.1  # Canvas 噪聲強度
    canvas_width: int = 800
    canvas_height: int = 600
    
    # 字體配置
    common_fonts: List[str] = None
    custom_fonts: List[str] = None
    
    # 屏幕配置
    screen_width: int = 1920
    screen_height: int = 1080
    color_depth: int = 24
    pixel_ratio: float = 1.0
    
    # 導航器配置
    user_agent: str = None
    platform: str = "Win32"
    language: str = "zh-CN"
    languages: List[str] = None
    hardware_concurrency: int = 8
    device_memory: int = 8
    
    def __post_init__(self):
        """初始化默認值"""
        if self.common_fonts is None:
            self.common_fonts = [
                "Arial", "Helvetica", "Times New Roman", "Times", "Courier New",
                "Courier", "Verdana", "Georgia", "Palatino", "Garamond",
                "Bookman", "Comic Sans MS", "Trebuchet MS", "Arial Black"
            ]
            
        if self.custom_fonts is None:
            self.custom_fonts = []
            
        if self.languages is None:
            self.languages = ["zh-CN", "zh", "en-US", "en"]
            
        if self.user_agent is None:
            self.user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """將配置轉換為字典"""
        return {
            "webgl": {
                "vendor": self.webgl_vendor,
                "renderer": self.webgl_renderer,
                "version": self.webgl_version
            },
            "canvas": {
                "noise": self.canvas_noise,
                "width": self.canvas_width,
                "height": self.canvas_height
            },
            "fonts": {
                "common": self.common_fonts,
                "custom": self.custom_fonts
            },
            "screen": {
                "width": self.screen_width,
                "height": self.screen_height,
                "colorDepth": self.color_depth,
                "pixelRatio": self.pixel_ratio
            },
            "navigator": {
                "userAgent": self.user_agent,
                "platform": self.platform,
                "language": self.language,
                "languages": self.languages,
                "hardwareConcurrency": self.hardware_concurrency,
                "deviceMemory": self.device_memory
            }
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AntiFingerprintConfig':
        """從字典創建配置對象"""
        webgl = config_dict.get("webgl", {})
        canvas = config_dict.get("canvas", {})
        fonts = config_dict.get("fonts", {})
        screen = config_dict.get("screen", {})
        navigator = config_dict.get("navigator", {})
        
        return cls(
            webgl_vendor=webgl.get("vendor"),
            webgl_renderer=webgl.get("renderer"),
            webgl_version=webgl.get("version"),
            canvas_noise=canvas.get("noise"),
            canvas_width=canvas.get("width"),
            canvas_height=canvas.get("height"),
            common_fonts=fonts.get("common"),
            custom_fonts=fonts.get("custom"),
            screen_width=screen.get("width"),
            screen_height=screen.get("height"),
            color_depth=screen.get("colorDepth"),
            pixel_ratio=screen.get("pixelRatio"),
            user_agent=navigator.get("userAgent"),
            platform=navigator.get("platform"),
            language=navigator.get("language"),
            languages=navigator.get("languages"),
            hardware_concurrency=navigator.get("hardwareConcurrency"),
            device_memory=navigator.get("deviceMemory")
        ) 
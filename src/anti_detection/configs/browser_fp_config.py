#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
瀏覽器指紋配置

此模組提供瀏覽器指紋相關的配置類，包括：
1. BrowserFingerprintConfig：瀏覽器指紋主配置
2. WebGLConfig：WebGL 指紋配置
3. CanvasConfig：Canvas 指紋配置
4. AudioConfig：音頻指紋配置
5. FontConfig：字體指紋配置
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class WebGLConfig:
    """WebGL 指紋配置"""
    vendor: str = "Google Inc. (NVIDIA)"  # WebGL 供應商
    renderer: str = "ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 Direct3D11 vs_5_0 ps_5_0, D3D11)"  # WebGL 渲染器
    version: str = "WebGL GLSL ES 1.0"  # WebGL 版本
    shading_language_version: str = "WebGL GLSL ES 1.0"  # 著色器語言版本
    extensions: List[str] = field(default_factory=lambda: [
        "ANGLE_instanced_arrays",
        "EXT_blend_minmax",
        "EXT_color_buffer_half_float",
        "EXT_disjoint_timer_query",
        "EXT_float_blend",
        "EXT_frag_depth",
        "EXT_shader_texture_lod",
        "EXT_texture_compression_bptc",
        "EXT_texture_compression_rgtc",
        "EXT_texture_filter_anisotropic",
        "OES_element_index_uint",
        "OES_fbo_render_mipmap",
        "OES_standard_derivatives",
        "OES_texture_float",
        "OES_texture_float_linear",
        "OES_texture_half_float",
        "OES_texture_half_float_linear",
        "OES_vertex_array_object",
        "WEBGL_color_buffer_float",
        "WEBGL_compressed_texture_s3tc",
        "WEBGL_compressed_texture_s3tc_srgb",
        "WEBGL_debug_renderer_info",
        "WEBGL_debug_shaders",
        "WEBGL_depth_texture",
        "WEBGL_draw_buffers",
        "WEBGL_lose_context",
        "WEBGL_multi_draw"
    ])
    parameters: Dict[str, Any] = field(default_factory=lambda: {
        "MAX_VERTEX_ATTRIBS": 16,
        "MAX_VERTEX_UNIFORM_VECTORS": 4096,
        "MAX_VARYING_VECTORS": 32,
        "MAX_COMBINED_TEXTURE_IMAGE_UNITS": 32,
        "MAX_VERTEX_TEXTURE_IMAGE_UNITS": 16,
        "MAX_TEXTURE_IMAGE_UNITS": 16,
        "MAX_TEXTURE_SIZE": 16384,
        "MAX_CUBE_MAP_TEXTURE_SIZE": 16384,
        "MAX_RENDERBUFFER_SIZE": 16384,
        "MAX_VIEWPORT_DIMS": [32767, 32767],
        "MAX_VERTEX_UNIFORM_BLOCKS": 14,
        "MAX_FRAGMENT_UNIFORM_BLOCKS": 14,
        "MAX_COMBINED_UNIFORM_BLOCKS": 28,
        "MAX_UNIFORM_BUFFER_BINDINGS": 32,
        "MAX_UNIFORM_BLOCK_SIZE": 16384,
        "MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS": 65536,
        "MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS": 65536
    })
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "vendor": self.vendor,
            "renderer": self.renderer,
            "version": self.version,
            "shading_language_version": self.shading_language_version,
            "extensions": self.extensions,
            "parameters": self.parameters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebGLConfig':
        """從字典創建實例"""
        return cls(
            vendor=data.get("vendor", "Google Inc. (NVIDIA)"),
            renderer=data.get("renderer", "ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
            version=data.get("version", "WebGL GLSL ES 1.0"),
            shading_language_version=data.get("shading_language_version", "WebGL GLSL ES 1.0"),
            extensions=data.get("extensions", []),
            parameters=data.get("parameters", {})
        )

@dataclass
class CanvasConfig:
    """Canvas 指紋配置"""
    width: int = 220  # Canvas 寬度
    height: int = 30  # Canvas 高度
    text: str = "Cwm fjordbank glyphs vext quiz 😃"  # 繪製文本
    font: str = "14px 'Arial'"  # 字體
    background_color: str = "#f60"  # 背景顏色
    text_color: str = "#069"  # 文本顏色
    noise_level: float = 0.1  # 噪聲級別
    noise_pattern: str = "gaussian"  # 噪聲模式：gaussian, uniform, perlin
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "width": self.width,
            "height": self.height,
            "text": self.text,
            "font": self.font,
            "background_color": self.background_color,
            "text_color": self.text_color,
            "noise_level": self.noise_level,
            "noise_pattern": self.noise_pattern
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CanvasConfig':
        """從字典創建實例"""
        return cls(
            width=data.get("width", 220),
            height=data.get("height", 30),
            text=data.get("text", "Cwm fjordbank glyphs vext quiz 😃"),
            font=data.get("font", "14px 'Arial'"),
            background_color=data.get("background_color", "#f60"),
            text_color=data.get("text_color", "#069"),
            noise_level=data.get("noise_level", 0.1),
            noise_pattern=data.get("noise_pattern", "gaussian")
        )

@dataclass
class AudioConfig:
    """音頻指紋配置"""
    sample_rate: int = 44100  # 採樣率
    duration: float = 1.0  # 持續時間（秒）
    frequency: float = 440.0  # 頻率（Hz）
    amplitude: float = 0.5  # 振幅
    noise_level: float = 0.1  # 噪聲級別
    noise_pattern: str = "gaussian"  # 噪聲模式：gaussian, uniform, perlin
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "sample_rate": self.sample_rate,
            "duration": self.duration,
            "frequency": self.frequency,
            "amplitude": self.amplitude,
            "noise_level": self.noise_level,
            "noise_pattern": self.noise_pattern
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioConfig':
        """從字典創建實例"""
        return cls(
            sample_rate=data.get("sample_rate", 44100),
            duration=data.get("duration", 1.0),
            frequency=data.get("frequency", 440.0),
            amplitude=data.get("amplitude", 0.5),
            noise_level=data.get("noise_level", 0.1),
            noise_pattern=data.get("noise_pattern", "gaussian")
        )

@dataclass
class FontConfig:
    """字體指紋配置"""
    common_fonts: List[str] = field(default_factory=lambda: [
        "Arial",
        "Arial Black",
        "Arial Narrow",
        "Calibri",
        "Cambria",
        "Cambria Math",
        "Comic Sans MS",
        "Courier",
        "Courier New",
        "Georgia",
        "Helvetica",
        "Impact",
        "Lucida Console",
        "Lucida Sans Unicode",
        "Microsoft Sans Serif",
        "Palatino Linotype",
        "Tahoma",
        "Times",
        "Times New Roman",
        "Trebuchet MS",
        "Verdana"
    ])
    chinese_fonts: List[str] = field(default_factory=lambda: [
        "Microsoft YaHei",
        "Microsoft YaHei UI",
        "Microsoft YaHei UI Light",
        "Microsoft YaHei UI Semibold",
        "Microsoft YaHei UI Bold",
        "Microsoft YaHei Light",
        "Microsoft YaHei Semibold",
        "Microsoft YaHei Bold",
        "SimSun",
        "SimHei",
        "NSimSun",
        "FangSong",
        "KaiTi",
        "Microsoft JhengHei",
        "Microsoft JhengHei UI",
        "Microsoft JhengHei UI Light",
        "Microsoft JhengHei UI Semibold",
        "Microsoft JhengHei UI Bold",
        "Microsoft JhengHei Light",
        "Microsoft JhengHei Semibold",
        "Microsoft JhengHei Bold",
        "DFKai-SB",
        "DFKai-SB-Estd-BF",
        "DFKai-SB-Estd-BF-Estd-BF",
        "DFKai-SB-Estd-BF-Estd-BF-Estd-BF",
        "DFKai-SB-Estd-BF-Estd-BF-Estd-BF-Estd-BF",
        "DFKai-SB-Estd-BF-Estd-BF-Estd-BF-Estd-BF-Estd-BF",
        "DFKai-SB-Estd-BF-Estd-BF-Estd-BF-Estd-BF-Estd-BF-Estd-BF",
        "DFKai-SB-Estd-BF-Estd-BF-Estd-BF-Estd-BF-Estd-BF-Estd-BF-Estd-BF",
        "DFKai-SB-Estd-BF-Estd-BF-Estd-BF-Estd-BF-Estd-BF-Estd-BF-Estd-BF-Estd-BF",
        "DFKai-SB-Estd-BF-Estd-BF-Estd-BF-Estd-BF-Estd-BF-Estd-BF-Estd-BF-Estd-BF-Estd-BF"
    ])
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "common_fonts": self.common_fonts,
            "chinese_fonts": self.chinese_fonts
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FontConfig':
        """從字典創建實例"""
        return cls(
            common_fonts=data.get("common_fonts", []),
            chinese_fonts=data.get("chinese_fonts", [])
        )

@dataclass
class BrowserFingerprintConfig:
    """瀏覽器指紋配置"""
    id: str
    platform: str = "Win32"  # 平台
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"  # User-Agent
    vendor: str = "Google Inc."  # 供應商
    language: str = "zh-TW"  # 語言
    languages: List[str] = field(default_factory=lambda: ["zh-TW", "zh", "en-US", "en"])  # 語言列表
    color_depth: int = 24  # 顏色深度
    pixel_ratio: float = 1.0  # 像素比例
    screen_width: int = 1920  # 屏幕寬度
    screen_height: int = 1080  # 屏幕高度
    webgl_config: WebGLConfig = field(default_factory=WebGLConfig)  # WebGL 配置
    canvas_config: CanvasConfig = field(default_factory=CanvasConfig)  # Canvas 配置
    audio_config: AudioConfig = field(default_factory=AudioConfig)  # 音頻配置
    font_config: FontConfig = field(default_factory=FontConfig)  # 字體配置
    created_at: datetime = field(default_factory=datetime.now)  # 創建時間
    updated_at: datetime = field(default_factory=datetime.now)  # 更新時間
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "platform": self.platform,
            "user_agent": self.user_agent,
            "vendor": self.vendor,
            "language": self.language,
            "languages": self.languages,
            "color_depth": self.color_depth,
            "pixel_ratio": self.pixel_ratio,
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "webgl_config": self.webgl_config.to_dict(),
            "canvas_config": self.canvas_config.to_dict(),
            "audio_config": self.audio_config.to_dict(),
            "font_config": self.font_config.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BrowserFingerprintConfig':
        """從字典創建實例"""
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
            
        return cls(
            id=data.get("id"),
            platform=data.get("platform", "Win32"),
            user_agent=data.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
            vendor=data.get("vendor", "Google Inc."),
            language=data.get("language", "zh-TW"),
            languages=data.get("languages", ["zh-TW", "zh", "en-US", "en"]),
            color_depth=data.get("color_depth", 24),
            pixel_ratio=data.get("pixel_ratio", 1.0),
            screen_width=data.get("screen_width", 1920),
            screen_height=data.get("screen_height", 1080),
            webgl_config=WebGLConfig.from_dict(data.get("webgl_config", {})),
            canvas_config=CanvasConfig.from_dict(data.get("canvas_config", {})),
            audio_config=AudioConfig.from_dict(data.get("audio_config", {})),
            font_config=FontConfig.from_dict(data.get("font_config", {})),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now())
        ) 
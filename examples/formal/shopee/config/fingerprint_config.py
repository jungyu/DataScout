"""
瀏覽器指紋配置模組

提供瀏覽器指紋相關的配置類別，包括：
- WebGL 配置
- Canvas 配置
- 音頻配置
- WebRTC 配置
- 硬件配置
- 指紋配置
"""

from dataclasses import dataclass, field
from typing import List

@dataclass
class WebGLConfig:
    """WebGL 配置"""
    vendor: str = "Google Inc. (NVIDIA)"
    renderer: str = "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0)"
    extensions: List[str] = field(default_factory=lambda: [
        "ANGLE_instanced_arrays",
        "EXT_blend_minmax",
        "EXT_color_buffer_half_float",
        "EXT_disjoint_timer_query",
        "EXT_float_blend",
        "EXT_frag_depth",
        "EXT_shader_framebuffer_fetch",
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

@dataclass
class CanvasConfig:
    """Canvas 配置"""
    noise: float = 0.1
    randomize_colors: bool = True
    width: int = 200
    height: int = 200

@dataclass
class AudioConfig:
    """音頻配置"""
    sample_rate: int = 44100
    channel_count: int = 2
    buffer_size: int = 4096
    noise_level: float = 0.01

@dataclass
class WebRTCConfig:
    """WebRTC 配置"""
    enabled: bool = True
    ip_handling: str = "disable_non_proxied_udp"
    stun_servers: List[str] = field(default_factory=lambda: [
        "stun:stun.l.google.com:19302",
        "stun:stun1.l.google.com:19302"
    ])

@dataclass
class HardwareConfig:
    """硬件配置"""
    concurrency: int = 8
    memory: int = 8
    platform: str = "Win32"
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

@dataclass
class FingerprintConfig:
    """指紋配置"""
    webgl: WebGLConfig = field(default_factory=WebGLConfig)
    canvas: CanvasConfig = field(default_factory=CanvasConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    webrtc: WebRTCConfig = field(default_factory=WebRTCConfig)
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    fonts: List[str] = field(default_factory=lambda: [
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
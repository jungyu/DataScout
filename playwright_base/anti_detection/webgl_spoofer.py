#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WebGL 指紋偽裝模組

此模組提供 WebGL 指紋偽裝功能，包括：
1. WebGL 參數偽裝
2. WebGL 渲染器偽裝
3. WebGL 擴展偽裝
"""

from typing import Dict, Any, List
import random
from loguru import logger

from ..utils.exceptions import AntiDetectionException


class WebGLSpoofer:
    """WebGL 指紋偽裝器"""
    
    def __init__(self):
        """初始化 WebGL 指紋偽裝器"""
        # WebGL 供應商列表
        self.vendors = [
            "Google Inc. (NVIDIA)",
            "Google Inc. (Intel)",
            "Google Inc. (AMD)",
            "Apple GPU",
            "Mesa/X.org",
            "Microsoft Basic Render Driver",
            "Intel Inc.",
            "AMD",
            "NVIDIA Corporation"
        ]
        
        # WebGL 渲染器列表
        self.renderers = [
            "ANGLE (NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0)",
            "Apple M1",
            "Mesa DRI Intel(R) HD Graphics 520 (Skylake GT2)",
            "ANGLE (NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (AMD Radeon RX 6800 XT Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (Microsoft Basic Render Driver Direct3D11 vs_5_0 ps_5_0)"
        ]
        
        # WebGL 版本列表
        self.versions = [
            "WebGL GLSL ES 1.0",
            "WebGL GLSL ES 2.0",
            "WebGL GLSL ES 3.0",
            "WebGL GLSL ES 3.1"
        ]
        
        # WebGL 擴展列表
        self.extensions = [
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
        ]
    
    def get_random_webgl_fingerprint(self) -> Dict[str, Any]:
        """
        獲取隨機 WebGL 指紋
        
        Returns:
            Dict[str, Any]: WebGL 指紋信息
        """
        vendor = random.choice(self.vendors)
        renderer = random.choice(self.renderers)
        version = random.choice(self.versions)
        extensions = random.sample(self.extensions, random.randint(15, 25))
        
        return {
            "vendor": vendor,
            "renderer": renderer,
            "version": version,
            "extensions": extensions,
            "maxTextureSize": random.choice([2048, 4096, 8192, 16384]),
            "maxViewportDims": [random.choice([2048, 4096, 8192]), random.choice([2048, 4096, 8192])],
            "maxRenderbufferSize": random.choice([2048, 4096, 8192, 16384])
        }
    
    def get_consistent_webgl_fingerprint(self) -> Dict[str, Any]:
        """
        獲取一致的 WebGL 指紋（每次調用返回相同的指紋）
        
        Returns:
            Dict[str, Any]: WebGL 指紋信息
        """
        return {
            "vendor": "Google Inc. (NVIDIA)",
            "renderer": "ANGLE (NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0)",
            "version": "WebGL GLSL ES 2.0",
            "extensions": self.extensions[:20],
            "maxTextureSize": 4096,
            "maxViewportDims": [4096, 4096],
            "maxRenderbufferSize": 4096
        }
    
    def apply_spoof(self, page) -> None:
        """
        應用 WebGL 指紋偽裝
        
        Args:
            page: Playwright 頁面對象
        """
        try:
            fingerprint = self.get_consistent_webgl_fingerprint()
            
            script = f"""
            // 修改 WebGL 參數
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                // WebGL 供應商
                if (parameter === 37445) {{
                    return '{fingerprint['vendor']}';
                }}
                // WebGL 渲染器
                if (parameter === 37446) {{
                    return '{fingerprint['renderer']}';
                }}
                // WebGL 版本
                if (parameter === 35724) {{
                    return '{fingerprint['version']}';
                }}
                // 最大紋理大小
                if (parameter === 3379) {{
                    return {fingerprint['maxTextureSize']};
                }}
                // 最大視口尺寸
                if (parameter === 3386) {{
                    return {fingerprint['maxViewportDims']};
                }}
                // 最大渲染緩衝區大小
                if (parameter === 34024) {{
                    return {fingerprint['maxRenderbufferSize']};
                }}
                return getParameter.apply(this, arguments);
            }};
            
            // 修改 WebGL 擴展
            const getExtension = WebGLRenderingContext.prototype.getExtension;
            WebGLRenderingContext.prototype.getExtension = function(name) {{
                if ({fingerprint['extensions']}.includes(name)) {{
                    return getExtension.apply(this, arguments);
                }}
                return null;
            }};
            
            // 修改 WebGL 擴展列表
            const getSupportedExtensions = WebGLRenderingContext.prototype.getSupportedExtensions;
            WebGLRenderingContext.prototype.getSupportedExtensions = function() {{
                return {fingerprint['extensions']};
            }};
            """
            
            page.add_init_script(script)
            logger.info("已應用 WebGL 指紋偽裝")
        except Exception as e:
            logger.error(f"應用 WebGL 指紋偽裝時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"應用 WebGL 指紋偽裝失敗: {str(e)}") 
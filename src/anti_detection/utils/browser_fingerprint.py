"""
瀏覽器指紋模組
提供瀏覽器指紋生成和管理功能
"""

import json
import random
import string
import logging
from typing import Dict, Any, List, Optional, Tuple
from selenium.webdriver import Chrome, Firefox, Edge
from selenium.webdriver.remote.webdriver import WebDriver

from ..base_error import BaseError, handle_error, retry_on_error
from ..configs.browser_fingerprint_config import BrowserFingerprintConfig

class BrowserFingerprintError(BaseError):
    """瀏覽器指紋錯誤"""
    pass

class BrowserFingerprint:
    """瀏覽器指紋類"""
    
    def __init__(
        self,
        driver: WebDriver,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化
        
        Args:
            driver: WebDriver 實例
            config: 配置字典
            logger: 日誌記錄器
        """
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        self.config = BrowserFingerprintConfig.from_dict(config or {})
        if not self.config.validate():
            raise BrowserFingerprintError("無效的瀏覽器指紋配置")
        
        self.fingerprint_history: List[Dict[str, Any]] = []
        self.fingerprint_stats: Dict[str, Dict[str, int]] = {}
    
    @handle_error
    def generate_fingerprint(self) -> Dict[str, Any]:
        """
        生成瀏覽器指紋
        
        Returns:
            指紋字典
        """
        fingerprint = {
            "user_agent": this._generate_user_agent(),
            "screen": this._generate_screen_info(),
            "navigator": this._generate_navigator_info(),
            "webgl": this._generate_webgl_info(),
            "canvas": this._generate_canvas_info(),
            "fonts": this._generate_fonts_info(),
            "audio": this._generate_audio_info(),
            "plugins": this._generate_plugins_info(),
            "timezone": this._generate_timezone_info(),
            "language": this._generate_language_info(),
            "platform": this._generate_platform_info(),
            "hardware": this._generate_hardware_info()
        }
        
        # 記錄指紋
        this.fingerprint_history.append(fingerprint)
        
        # 更新統計信息
        for key in fingerprint:
            if key not in this.fingerprint_stats:
                this.fingerprint_stats[key] = {}
            value = str(fingerprint[key])
            this.fingerprint_stats[key][value] = this.fingerprint_stats[key].get(value, 0) + 1
        
        return fingerprint
    
    @handle_error
    def apply_fingerprint(self, fingerprint: Dict[str, Any]) -> None:
        """
        應用瀏覽器指紋
        
        Args:
            fingerprint: 指紋字典
        """
        # 設置 User-Agent
        this._set_user_agent(fingerprint["user_agent"])
        
        # 設置屏幕信息
        this._set_screen_info(fingerprint["screen"])
        
        # 設置 Navigator 信息
        this._set_navigator_info(fingerprint["navigator"])
        
        # 設置 WebGL 信息
        this._set_webgl_info(fingerprint["webgl"])
        
        # 設置 Canvas 信息
        this._set_canvas_info(fingerprint["canvas"])
        
        # 設置字體信息
        this._set_fonts_info(fingerprint["fonts"])
        
        # 設置音頻信息
        this._set_audio_info(fingerprint["audio"])
        
        # 設置插件信息
        this._set_plugins_info(fingerprint["plugins"])
        
        # 設置時區信息
        this._set_timezone_info(fingerprint["timezone"])
        
        # 設置語言信息
        this._set_language_info(fingerprint["language"])
        
        # 設置平台信息
        this._set_platform_info(fingerprint["platform"])
        
        # 設置硬件信息
        this._set_hardware_info(fingerprint["hardware"])
    
    @handle_error
    def validate_fingerprint(self, fingerprint: Dict[str, Any]) -> bool:
        """
        驗證瀏覽器指紋
        
        Args:
            fingerprint: 指紋字典
            
        Returns:
            是否有效
        """
        try:
            # 檢查必要字段
            required_fields = [
                "user_agent",
                "screen",
                "navigator",
                "webgl",
                "canvas",
                "fonts",
                "audio",
                "plugins",
                "timezone",
                "language",
                "platform",
                "hardware"
            ]
            
            for field in required_fields:
                if field not in fingerprint:
                    this.logger.error(f"缺少必要字段: {field}")
                    return False
            
            # 檢查字段類型
            if not isinstance(fingerprint["user_agent"], str):
                this.logger.error("User-Agent 必須是字符串")
                return False
            
            if not isinstance(fingerprint["screen"], dict):
                this.logger.error("Screen 必須是字典")
                return False
            
            if not isinstance(fingerprint["navigator"], dict):
                this.logger.error("Navigator 必須是字典")
                return False
            
            # 檢查字段值
            if not fingerprint["user_agent"]:
                this.logger.error("User-Agent 不能為空")
                return False
            
            if not fingerprint["screen"].get("width") or not fingerprint["screen"].get("height"):
                this.logger.error("Screen 寬高不能為空")
                return False
            
            if not fingerprint["navigator"].get("platform"):
                this.logger.error("Navigator platform 不能為空")
                return False
            
            return True
            
        except Exception as e:
            this.logger.error(f"驗證指紋時發生錯誤: {str(e)}")
            return False
    
    def get_fingerprint_report(self) -> Dict[str, Any]:
        """獲取指紋報告"""
        return {
            "total_fingerprints": len(this.fingerprint_history),
            "fingerprint_stats": this.fingerprint_stats,
            "recent_fingerprints": this.fingerprint_history[-10:]
        }
    
    def _generate_user_agent(self) -> str:
        """生成 User-Agent"""
        # 根據瀏覽器類型生成不同的 User-Agent
        if isinstance(this.driver, Chrome):
            return this._generate_chrome_user_agent()
        elif isinstance(this.driver, Firefox):
            return this._generate_firefox_user_agent()
        elif isinstance(this.driver, Edge):
            return this._generate_edge_user_agent()
        else:
            return this._generate_default_user_agent()
    
    def _generate_screen_info(self) -> Dict[str, Any]:
        """生成屏幕信息"""
        return {
            "width": random.randint(1024, 2560),
            "height": random.randint(768, 1440),
            "colorDepth": random.choice([24, 32]),
            "pixelDepth": random.choice([24, 32]),
            "devicePixelRatio": random.choice([1, 1.5, 2, 2.5, 3])
        }
    
    def _generate_navigator_info(self) -> Dict[str, Any]:
        """生成 Navigator 信息"""
        return {
            "platform": random.choice(["Win32", "MacIntel", "Linux x86_64"]),
            "vendor": random.choice(["Google Inc.", "Apple Computer, Inc."]),
            "language": random.choice(["zh-CN", "en-US", "ja-JP"]),
            "languages": ["zh-CN", "en-US"],
            "doNotTrack": random.choice(["1", None]),
            "cookieEnabled": True,
            "webdriver": False
        }
    
    def _generate_webgl_info(self) -> Dict[str, Any]:
        """生成 WebGL 信息"""
        return {
            "vendor": random.choice(["Google Inc.", "Apple Inc."]),
            "renderer": random.choice([
                "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)",
                "ANGLE (AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0)",
                "ANGLE (NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0)"
            ]),
            "extensions": [
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
        }
    
    def _generate_canvas_info(self) -> Dict[str, Any]:
        """生成 Canvas 信息"""
        return {
            "noise": random.uniform(0.1, 0.3),
            "geometry": random.uniform(0.1, 0.3),
            "text": random.uniform(0.1, 0.3)
        }
    
    def _generate_fonts_info(self) -> List[str]:
        """生成字體信息"""
        return [
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
        ]
    
    def _generate_audio_info(self) -> Dict[str, Any]:
        """生成音頻信息"""
        return {
            "sampleRate": random.choice([44100, 48000]),
            "channelCount": random.choice([2, 4, 6, 8]),
            "bufferSize": random.choice([256, 512, 1024, 2048, 4096])
        }
    
    def _generate_plugins_info(self) -> List[Dict[str, str]]:
        """生成插件信息"""
        return [
            {
                "name": "Chrome PDF Plugin",
                "filename": "internal-pdf-viewer",
                "description": "Portable Document Format"
            },
            {
                "name": "Chrome PDF Viewer",
                "filename": "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                "description": "Portable Document Format"
            },
            {
                "name": "Native Client",
                "filename": "internal-nacl-plugin",
                "description": "Native Client Executable"
            }
        ]
    
    def _generate_timezone_info(self) -> Dict[str, Any]:
        """生成時區信息"""
        return {
            "offset": random.randint(-720, 720),
            "name": random.choice([
                "Asia/Shanghai",
                "America/New_York",
                "Europe/London",
                "Asia/Tokyo"
            ])
        }
    
    def _generate_language_info(self) -> Dict[str, Any]:
        """生成語言信息"""
        return {
            "language": random.choice(["zh-CN", "en-US", "ja-JP"]),
            "languages": ["zh-CN", "en-US"],
            "acceptLanguage": "zh-CN,zh;q=0.9,en;q=0.8"
        }
    
    def _generate_platform_info(self) -> Dict[str, Any]:
        """生成平台信息"""
        return {
            "platform": random.choice(["Win32", "MacIntel", "Linux x86_64"]),
            "userAgent": this._generate_user_agent(),
            "appVersion": random.choice([
                "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ])
        }
    
    def _generate_hardware_info(self) -> Dict[str, Any]:
        """生成硬件信息"""
        return {
            "deviceMemory": random.choice([4, 8, 16, 32]),
            "hardwareConcurrency": random.choice([2, 4, 8, 16]),
            "maxTouchPoints": random.choice([0, 5, 10])
        }
    
    def _generate_chrome_user_agent(self) -> str:
        """生成 Chrome User-Agent"""
        chrome_versions = ["91.0.4472.124", "92.0.4515.107", "93.0.4577.63"]
        platforms = [
            "(Windows NT 10.0; Win64; x64)",
            "(Macintosh; Intel Mac OS X 10_15_7)",
            "(X11; Linux x86_64)"
        ]
        
        return f"Mozilla/5.0 {random.choice(platforms)} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(chrome_versions)} Safari/537.36"
    
    def _generate_firefox_user_agent(self) -> str:
        """生成 Firefox User-Agent"""
        firefox_versions = ["89.0", "90.0", "91.0"]
        platforms = [
            "(Windows NT 10.0; Win64; x64; rv:89.0)",
            "(Macintosh; Intel Mac OS X 10.15; rv:89.0)",
            "(X11; Linux i686; rv:89.0)"
        ]
        
        return f"Mozilla/5.0 {random.choice(platforms)} Gecko/20100101 Firefox/{random.choice(firefox_versions)}"
    
    def _generate_edge_user_agent(self) -> str:
        """生成 Edge User-Agent"""
        edge_versions = ["91.0.864.59", "92.0.902.84", "93.0.961.52"]
        platforms = [
            "(Windows NT 10.0; Win64; x64)",
            "(Macintosh; Intel Mac OS X 10_15_7)",
            "(X11; Linux x86_64)"
        ]
        
        return f"Mozilla/5.0 {random.choice(platforms)} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(edge_versions)} Safari/537.36 Edg/{random.choice(edge_versions)}"
    
    def _generate_default_user_agent(self) -> str:
        """生成默認 User-Agent"""
        return this._generate_chrome_user_agent()
    
    def _set_user_agent(self, user_agent: str) -> None:
        """設置 User-Agent"""
        this.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})
    
    def _set_screen_info(self, screen_info: Dict[str, Any]) -> None:
        """設置屏幕信息"""
        this.driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
            "width": screen_info["width"],
            "height": screen_info["height"],
            "deviceScaleFactor": screen_info["devicePixelRatio"],
            "mobile": False
        })
    
    def _set_navigator_info(self, navigator_info: Dict[str, Any]) -> None:
        """設置 Navigator 信息"""
        this.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": f"""
                Object.defineProperty(navigator, 'platform', {{
                    get: () => '{navigator_info["platform"]}'
                }});
                Object.defineProperty(navigator, 'vendor', {{
                    get: () => '{navigator_info["vendor"]}'
                }});
                Object.defineProperty(navigator, 'language', {{
                    get: () => '{navigator_info["language"]}'
                }});
                Object.defineProperty(navigator, 'languages', {{
                    get: () => {json.dumps(navigator_info["languages"])}
                }});
                Object.defineProperty(navigator, 'doNotTrack', {{
                    get: () => {json.dumps(navigator_info["doNotTrack"])}
                }});
                Object.defineProperty(navigator, 'cookieEnabled', {{
                    get: () => {json.dumps(navigator_info["cookieEnabled"])}
                }});
                Object.defineProperty(navigator, 'webdriver', {{
                    get: () => {json.dumps(navigator_info["webdriver"])}
                }});
            """
        })
    
    def _set_webgl_info(self, webgl_info: Dict[str, Any]) -> None:
        """設置 WebGL 信息"""
        this.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": f"""
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                    if (parameter === 37445) {{
                        return '{webgl_info["vendor"]}';
                    }}
                    if (parameter === 37446) {{
                        return '{webgl_info["renderer"]}';
                    }}
                    return getParameter.apply(this, arguments);
                }};
                
                const getExtension = WebGLRenderingContext.prototype.getExtension;
                WebGLRenderingContext.prototype.getExtension = function(name) {{
                    if ({json.dumps(webgl_info["extensions"])}.includes(name)) {{
                        return getExtension.apply(this, arguments);
                    }}
                    return null;
                }};
            """
        })
    
    def _set_canvas_info(self, canvas_info: Dict[str, Any]) -> None:
        """設置 Canvas 信息"""
        this.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": f"""
                const originalGetContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(type, attributes) {{
                    const context = originalGetContext.apply(this, arguments);
                    if (type === '2d') {{
                        const originalGetImageData = context.getImageData;
                        context.getImageData = function() {{
                            const imageData = originalGetImageData.apply(this, arguments);
                            const noise = {canvas_info["noise"]};
                            for (let i = 0; i < imageData.data.length; i += 4) {{
                                imageData.data[i] += Math.random() * noise;
                                imageData.data[i + 1] += Math.random() * noise;
                                imageData.data[i + 2] += Math.random() * noise;
                            }}
                            return imageData;
                        }};
                    }}
                    return context;
                }};
            """
        })
    
    def _set_fonts_info(self, fonts: List[str]) -> None:
        """設置字體信息"""
        this.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": f"""
                const originalFontFace = window.FontFace;
                window.FontFace = function(family, source, descriptors) {{
                    if ({json.dumps(fonts)}.includes(family)) {{
                        return new originalFontFace(family, source, descriptors);
                    }}
                    return null;
                }};
            """
        })
    
    def _set_audio_info(self, audio_info: Dict[str, Any]) -> None:
        """設置音頻信息"""
        this.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": f"""
                const originalGetChannelData = AudioBuffer.prototype.getChannelData;
                AudioBuffer.prototype.getChannelData = function(channel) {{
                    const data = originalGetChannelData.apply(this, arguments);
                    const noise = 0.01;
                    for (let i = 0; i < data.length; i++) {{
                        data[i] += Math.random() * noise;
                    }}
                    return data;
                }};
            """
        })
    
    def _set_plugins_info(self, plugins: List[Dict[str, str]]) -> None:
        """設置插件信息"""
        this.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": f"""
                Object.defineProperty(navigator, 'plugins', {{
                    get: () => {{
                        const plugins = {json.dumps(plugins)};
                        return plugins.map(plugin => ({{
                            name: plugin.name,
                            filename: plugin.filename,
                            description: plugin.description,
                            length: 1
                        }}));
                    }}
                }});
            """
        })
    
    def _set_timezone_info(self, timezone_info: Dict[str, Any]) -> None:
        """設置時區信息"""
        this.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": f"""
                Object.defineProperty(Intl, 'DateTimeFormat', {{
                    get: () => function(locale, options) {{
                        const format = new Intl.DateTimeFormat(locale, options);
                        const originalFormat = format.format;
                        format.format = function(date) {{
                            const result = originalFormat.apply(this, arguments);
                            return result.replace(/\+\d{2}:\d{2}/, '{timezone_info["offset"]:+03d}:00');
                        }};
                        return format;
                    }}
                }});
            """
        })
    
    def _set_language_info(self, language_info: Dict[str, Any]) -> None:
        """設置語言信息"""
        this.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": f"""
                Object.defineProperty(navigator, 'language', {{
                    get: () => '{language_info["language"]}'
                }});
                Object.defineProperty(navigator, 'languages', {{
                    get: () => {json.dumps(language_info["languages"])}
                }});
                Object.defineProperty(navigator, 'acceptLanguage', {{
                    get: () => '{language_info["acceptLanguage"]}'
                }});
            """
        })
    
    def _set_platform_info(self, platform_info: Dict[str, Any]) -> None:
        """設置平台信息"""
        this.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": f"""
                Object.defineProperty(navigator, 'platform', {{
                    get: () => '{platform_info["platform"]}'
                }});
                Object.defineProperty(navigator, 'userAgent', {{
                    get: () => '{platform_info["userAgent"]}'
                }});
                Object.defineProperty(navigator, 'appVersion', {{
                    get: () => '{platform_info["appVersion"]}'
                }});
            """
        })
    
    def _set_hardware_info(self, hardware_info: Dict[str, Any]) -> None:
        """設置硬件信息"""
        this.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": f"""
                Object.defineProperty(navigator, 'deviceMemory', {{
                    get: () => {hardware_info["deviceMemory"]}
                }});
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: () => {hardware_info["hardwareConcurrency"]}
                }});
                Object.defineProperty(navigator, 'maxTouchPoints', {{
                    get: () => {hardware_info["maxTouchPoints"]}
                }});
            """
        }) 
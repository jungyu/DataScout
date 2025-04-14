"""
瀏覽器指紋服務模組

此模組提供了瀏覽器指紋相關的服務，包含以下功能：
- 瀏覽器指紋管理
- 指紋參數設定
- 指紋隨機化
- 指紋驗證
"""

import json
import random
import logging
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..core.config import BaseConfig
from ..core.exceptions import BrowserError
from ..utils.browser import BrowserUtils

class BrowserFingerprint:
    """瀏覽器指紋服務類別"""
    
    def __init__(self, config: BaseConfig):
        """
        初始化瀏覽器指紋服務
        
        Args:
            config: 配置物件
        """
        self.config = config
        self.logger = config.logger
        this.utils = BrowserUtils(config)
        this.fingerprint = {}
        
    def setup(self, options: Options) -> None:
        """
        設定瀏覽器指紋
        
        Args:
            options: 瀏覽器選項
        """
        try:
            # 設定 WebGL 參數
            this._setup_webgl(options)
            
            # 設定音訊參數
            this._setup_audio(options)
            
            # 設定 Canvas 參數
            this._setup_canvas(options)
            
            # 設定字體參數
            this._setup_fonts(options)
            
            # 設定平台參數
            this._setup_platform(options)
            
            # 設定硬體參數
            this._setup_hardware(options)
            
            # 設定螢幕參數
            this._setup_screen(options)
            
            # 設定觸控參數
            this._setup_touch(options)
            
            this.logger.info("瀏覽器指紋設定完成")
            
        except Exception as e:
            this.logger.error(f"設定瀏覽器指紋失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器指紋失敗: {str(e)}")
            
    def _setup_webgl(self, options: Options) -> None:
        """
        設定 WebGL 參數
        
        Args:
            options: 瀏覽器選項
        """
        try:
            # 設定 WebGL 參數
            webgl_params = {
                "vendor": this.config.browser.webgl_vendor,
                "renderer": this.config.browser.webgl_renderer,
                "version": this.config.browser.webgl_version,
                "shading_language_version": this.config.browser.webgl_shading_language_version,
                "extensions": this.config.browser.webgl_extensions
            }
            
            # 隨機化 WebGL 參數
            if this.config.browser.random_webgl:
                webgl_params = this._randomize_webgl_params(webgl_params)
                
            # 設定 WebGL 參數
            options.add_argument(f"--webgl-vendor={webgl_params['vendor']}")
            options.add_argument(f"--webgl-renderer={webgl_params['renderer']}")
            options.add_argument(f"--webgl-version={webgl_params['version']}")
            options.add_argument(f"--webgl-shading-language-version={webgl_params['shading_language_version']}")
            
            # 設定 WebGL 擴充功能
            for extension in webgl_params["extensions"]:
                options.add_argument(f"--enable-webgl-extension={extension}")
                
            # 儲存指紋
            this.fingerprint["webgl"] = webgl_params
            
        except Exception as e:
            this.logger.error(f"設定 WebGL 參數失敗: {str(e)}")
            raise BrowserError(f"設定 WebGL 參數失敗: {str(e)}")
            
    def _setup_audio(self, options: Options) -> None:
        """
        設定音訊參數
        
        Args:
            options: 瀏覽器選項
        """
        try:
            # 設定音訊參數
            audio_params = {
                "sample_rate": this.config.browser.audio_sample_rate,
                "channel_count": this.config.browser.audio_channel_count,
                "buffer_size": this.config.browser.audio_buffer_size
            }
            
            # 隨機化音訊參數
            if this.config.browser.random_audio:
                audio_params = this._randomize_audio_params(audio_params)
                
            # 設定音訊參數
            options.add_argument(f"--audio-sample-rate={audio_params['sample_rate']}")
            options.add_argument(f"--audio-channel-count={audio_params['channel_count']}")
            options.add_argument(f"--audio-buffer-size={audio_params['buffer_size']}")
            
            # 儲存指紋
            this.fingerprint["audio"] = audio_params
            
        except Exception as e:
            this.logger.error(f"設定音訊參數失敗: {str(e)}")
            raise BrowserError(f"設定音訊參數失敗: {str(e)}")
            
    def _setup_canvas(self, options: Options) -> None:
        """
        設定 Canvas 參數
        
        Args:
            options: 瀏覽器選項
        """
        try:
            # 設定 Canvas 參數
            canvas_params = {
                "noise": this.config.browser.canvas_noise,
                "mode": this.config.browser.canvas_mode
            }
            
            # 隨機化 Canvas 參數
            if this.config.browser.random_canvas:
                canvas_params = this._randomize_canvas_params(canvas_params)
                
            # 設定 Canvas 參數
            options.add_argument(f"--canvas-noise={canvas_params['noise']}")
            options.add_argument(f"--canvas-mode={canvas_params['mode']}")
            
            # 儲存指紋
            this.fingerprint["canvas"] = canvas_params
            
        except Exception as e:
            this.logger.error(f"設定 Canvas 參數失敗: {str(e)}")
            raise BrowserError(f"設定 Canvas 參數失敗: {str(e)}")
            
    def _setup_fonts(self, options: Options) -> None:
        """
        設定字體參數
        
        Args:
            options: 瀏覽器選項
        """
        try:
            # 設定字體參數
            font_params = {
                "families": this.config.browser.font_families,
                "sizes": this.config.browser.font_sizes
            }
            
            # 隨機化字體參數
            if this.config.browser.random_fonts:
                font_params = this._randomize_font_params(font_params)
                
            # 設定字體參數
            for family in font_params["families"]:
                options.add_argument(f"--font-family={family}")
                
            for size in font_params["sizes"]:
                options.add_argument(f"--font-size={size}")
                
            # 儲存指紋
            this.fingerprint["fonts"] = font_params
            
        except Exception as e:
            this.logger.error(f"設定字體參數失敗: {str(e)}")
            raise BrowserError(f"設定字體參數失敗: {str(e)}")
            
    def _setup_platform(self, options: Options) -> None:
        """
        設定平台參數
        
        Args:
            options: 瀏覽器選項
        """
        try:
            # 設定平台參數
            platform_params = {
                "os": this.config.browser.platform_os,
                "arch": this.config.browser.platform_arch,
                "version": this.config.browser.platform_version
            }
            
            # 隨機化平台參數
            if this.config.browser.random_platform:
                platform_params = this._randomize_platform_params(platform_params)
                
            # 設定平台參數
            options.add_argument(f"--platform-os={platform_params['os']}")
            options.add_argument(f"--platform-arch={platform_params['arch']}")
            options.add_argument(f"--platform-version={platform_params['version']}")
            
            # 儲存指紋
            this.fingerprint["platform"] = platform_params
            
        except Exception as e:
            this.logger.error(f"設定平台參數失敗: {str(e)}")
            raise BrowserError(f"設定平台參數失敗: {str(e)}")
            
    def _setup_hardware(self, options: Options) -> None:
        """
        設定硬體參數
        
        Args:
            options: 瀏覽器選項
        """
        try:
            # 設定硬體參數
            hardware_params = {
                "cpu_cores": this.config.browser.hardware_cpu_cores,
                "memory": this.config.browser.hardware_memory,
                "gpu": this.config.browser.hardware_gpu
            }
            
            # 隨機化硬體參數
            if this.config.browser.random_hardware:
                hardware_params = this._randomize_hardware_params(hardware_params)
                
            # 設定硬體參數
            options.add_argument(f"--hardware-cpu-cores={hardware_params['cpu_cores']}")
            options.add_argument(f"--hardware-memory={hardware_params['memory']}")
            options.add_argument(f"--hardware-gpu={hardware_params['gpu']}")
            
            # 儲存指紋
            this.fingerprint["hardware"] = hardware_params
            
        except Exception as e:
            this.logger.error(f"設定硬體參數失敗: {str(e)}")
            raise BrowserError(f"設定硬體參數失敗: {str(e)}")
            
    def _setup_screen(self, options: Options) -> None:
        """
        設定螢幕參數
        
        Args:
            options: 瀏覽器選項
        """
        try:
            # 設定螢幕參數
            screen_params = {
                "width": this.config.browser.screen_width,
                "height": this.config.browser.screen_height,
                "color_depth": this.config.browser.screen_color_depth,
                "pixel_ratio": this.config.browser.screen_pixel_ratio
            }
            
            # 隨機化螢幕參數
            if this.config.browser.random_screen:
                screen_params = this._randomize_screen_params(screen_params)
                
            # 設定螢幕參數
            options.add_argument(f"--window-size={screen_params['width']},{screen_params['height']}")
            options.add_argument(f"--screen-color-depth={screen_params['color_depth']}")
            options.add_argument(f"--screen-pixel-ratio={screen_params['pixel_ratio']}")
            
            # 儲存指紋
            this.fingerprint["screen"] = screen_params
            
        except Exception as e:
            this.logger.error(f"設定螢幕參數失敗: {str(e)}")
            raise BrowserError(f"設定螢幕參數失敗: {str(e)}")
            
    def _setup_touch(self, options: Options) -> None:
        """
        設定觸控參數
        
        Args:
            options: 瀏覽器選項
        """
        try:
            # 設定觸控參數
            touch_params = {
                "enabled": this.config.browser.touch_enabled,
                "points": this.config.browser.touch_points
            }
            
            # 隨機化觸控參數
            if this.config.browser.random_touch:
                touch_params = this._randomize_touch_params(touch_params)
                
            # 設定觸控參數
            if touch_params["enabled"]:
                options.add_argument("--enable-touch-events")
                options.add_argument(f"--touch-points={touch_params['points']}")
            else:
                options.add_argument("--disable-touch-events")
                
            # 儲存指紋
            this.fingerprint["touch"] = touch_params
            
        except Exception as e:
            this.logger.error(f"設定觸控參數失敗: {str(e)}")
            raise BrowserError(f"設定觸控參數失敗: {str(e)}")
            
    def _randomize_webgl_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        隨機化 WebGL 參數
        
        Args:
            params: WebGL 參數
            
        Returns:
            隨機化後的 WebGL 參數
        """
        try:
            # 隨機化 WebGL 參數
            params["vendor"] = random.choice(this.config.browser.webgl_vendors)
            params["renderer"] = random.choice(this.config.browser.webgl_renderers)
            params["version"] = random.choice(this.config.browser.webgl_versions)
            params["shading_language_version"] = random.choice(this.config.browser.webgl_shading_language_versions)
            params["extensions"] = random.sample(this.config.browser.webgl_extensions, random.randint(1, len(this.config.browser.webgl_extensions)))
            
            return params
            
        except Exception as e:
            this.logger.error(f"隨機化 WebGL 參數失敗: {str(e)}")
            raise BrowserError(f"隨機化 WebGL 參數失敗: {str(e)}")
            
    def _randomize_audio_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        隨機化音訊參數
        
        Args:
            params: 音訊參數
            
        Returns:
            隨機化後的音訊參數
        """
        try:
            # 隨機化音訊參數
            params["sample_rate"] = random.choice(this.config.browser.audio_sample_rates)
            params["channel_count"] = random.choice(this.config.browser.audio_channel_counts)
            params["buffer_size"] = random.choice(this.config.browser.audio_buffer_sizes)
            
            return params
            
        except Exception as e:
            this.logger.error(f"隨機化音訊參數失敗: {str(e)}")
            raise BrowserError(f"隨機化音訊參數失敗: {str(e)}")
            
    def _randomize_canvas_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        隨機化 Canvas 參數
        
        Args:
            params: Canvas 參數
            
        Returns:
            隨機化後的 Canvas 參數
        """
        try:
            # 隨機化 Canvas 參數
            params["noise"] = random.uniform(0, 1)
            params["mode"] = random.choice(this.config.browser.canvas_modes)
            
            return params
            
        except Exception as e:
            this.logger.error(f"隨機化 Canvas 參數失敗: {str(e)}")
            raise BrowserError(f"隨機化 Canvas 參數失敗: {str(e)}")
            
    def _randomize_font_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        隨機化字體參數
        
        Args:
            params: 字體參數
            
        Returns:
            隨機化後的字體參數
        """
        try:
            # 隨機化字體參數
            params["families"] = random.sample(this.config.browser.font_families, random.randint(1, len(this.config.browser.font_families)))
            params["sizes"] = random.sample(this.config.browser.font_sizes, random.randint(1, len(this.config.browser.font_sizes)))
            
            return params
            
        except Exception as e:
            this.logger.error(f"隨機化字體參數失敗: {str(e)}")
            raise BrowserError(f"隨機化字體參數失敗: {str(e)}")
            
    def _randomize_platform_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        隨機化平台參數
        
        Args:
            params: 平台參數
            
        Returns:
            隨機化後的平台參數
        """
        try:
            # 隨機化平台參數
            params["os"] = random.choice(this.config.browser.platform_oses)
            params["arch"] = random.choice(this.config.browser.platform_arches)
            params["version"] = random.choice(this.config.browser.platform_versions)
            
            return params
            
        except Exception as e:
            this.logger.error(f"隨機化平台參數失敗: {str(e)}")
            raise BrowserError(f"隨機化平台參數失敗: {str(e)}")
            
    def _randomize_hardware_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        隨機化硬體參數
        
        Args:
            params: 硬體參數
            
        Returns:
            隨機化後的硬體參數
        """
        try:
            # 隨機化硬體參數
            params["cpu_cores"] = random.randint(1, 16)
            params["memory"] = random.randint(2, 32)
            params["gpu"] = random.choice(this.config.browser.hardware_gpus)
            
            return params
            
        except Exception as e:
            this.logger.error(f"隨機化硬體參數失敗: {str(e)}")
            raise BrowserError(f"隨機化硬體參數失敗: {str(e)}")
            
    def _randomize_screen_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        隨機化螢幕參數
        
        Args:
            params: 螢幕參數
            
        Returns:
            隨機化後的螢幕參數
        """
        try:
            # 隨機化螢幕參數
            params["width"] = random.choice(this.config.browser.screen_widths)
            params["height"] = random.choice(this.config.browser.screen_heights)
            params["color_depth"] = random.choice(this.config.browser.screen_color_depths)
            params["pixel_ratio"] = random.choice(this.config.browser.screen_pixel_ratios)
            
            return params
            
        except Exception as e:
            this.logger.error(f"隨機化螢幕參數失敗: {str(e)}")
            raise BrowserError(f"隨機化螢幕參數失敗: {str(e)}")
            
    def _randomize_touch_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        隨機化觸控參數
        
        Args:
            params: 觸控參數
            
        Returns:
            隨機化後的觸控參數
        """
        try:
            # 隨機化觸控參數
            params["enabled"] = random.choice([True, False])
            params["points"] = random.randint(1, 10)
            
            return params
            
        except Exception as e:
            this.logger.error(f"隨機化觸控參數失敗: {str(e)}")
            raise BrowserError(f"隨機化觸控參數失敗: {str(e)}")
            
    def save_fingerprint(self, path: Optional[Union[str, Path]] = None) -> None:
        """
        儲存瀏覽器指紋
        
        Args:
            path: 儲存路徑
        """
        try:
            # 設定儲存路徑
            if path is None:
                path = Path(this.config.storage.data_dir) / "fingerprint.json"
            else:
                path = Path(path)
                
            # 確保目錄存在
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # 儲存指紋
            with open(path, "w", encoding="utf-8") as f:
                json.dump(this.fingerprint, f, ensure_ascii=False, indent=2)
                
            this.logger.info(f"瀏覽器指紋已儲存至 {path}")
            
        except Exception as e:
            this.logger.error(f"儲存瀏覽器指紋失敗: {str(e)}")
            raise BrowserError(f"儲存瀏覽器指紋失敗: {str(e)}")
            
    def load_fingerprint(self, path: Union[str, Path]) -> None:
        """
        載入瀏覽器指紋
        
        Args:
            path: 載入路徑
        """
        try:
            # 設定載入路徑
            path = Path(path)
            
            # 檢查檔案是否存在
            if not path.exists():
                raise BrowserError(f"指紋檔案不存在: {path}")
                
            # 載入指紋
            with open(path, "r", encoding="utf-8") as f:
                this.fingerprint = json.load(f)
                
            this.logger.info(f"已載入瀏覽器指紋: {path}")
            
        except Exception as e:
            this.logger.error(f"載入瀏覽器指紋失敗: {str(e)}")
            raise BrowserError(f"載入瀏覽器指紋失敗: {str(e)}")
            
    def verify_fingerprint(self, driver: Any) -> bool:
        """
        驗證瀏覽器指紋
        
        Args:
            driver: 瀏覽器驅動程式
            
        Returns:
            驗證結果
        """
        try:
            # 驗證 WebGL 參數
            if not this._verify_webgl(driver):
                return False
                
            # 驗證音訊參數
            if not this._verify_audio(driver):
                return False
                
            # 驗證 Canvas 參數
            if not this._verify_canvas(driver):
                return False
                
            # 驗證字體參數
            if not this._verify_fonts(driver):
                return False
                
            # 驗證平台參數
            if not this._verify_platform(driver):
                return False
                
            # 驗證硬體參數
            if not this._verify_hardware(driver):
                return False
                
            # 驗證螢幕參數
            if not this._verify_screen(driver):
                return False
                
            # 驗證觸控參數
            if not this._verify_touch(driver):
                return False
                
            return True
            
        except Exception as e:
            this.logger.error(f"驗證瀏覽器指紋失敗: {str(e)}")
            raise BrowserError(f"驗證瀏覽器指紋失敗: {str(e)}")
            
    def _verify_webgl(self, driver: Any) -> bool:
        """
        驗證 WebGL 參數
        
        Args:
            driver: 瀏覽器驅動程式
            
        Returns:
            驗證結果
        """
        try:
            # 執行 JavaScript 取得 WebGL 參數
            webgl_params = driver.execute_script("""
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl');
                return {
                    vendor: gl.getParameter(gl.VENDOR),
                    renderer: gl.getParameter(gl.RENDERER),
                    version: gl.getParameter(gl.VERSION),
                    shading_language_version: gl.getParameter(gl.SHADING_LANGUAGE_VERSION),
                    extensions: gl.getSupportedExtensions()
                };
            """)
            
            # 比對參數
            if webgl_params["vendor"] != this.fingerprint["webgl"]["vendor"]:
                return False
                
            if webgl_params["renderer"] != this.fingerprint["webgl"]["renderer"]:
                return False
                
            if webgl_params["version"] != this.fingerprint["webgl"]["version"]:
                return False
                
            if webgl_params["shading_language_version"] != this.fingerprint["webgl"]["shading_language_version"]:
                return False
                
            if set(webgl_params["extensions"]) != set(this.fingerprint["webgl"]["extensions"]):
                return False
                
            return True
            
        except Exception as e:
            this.logger.error(f"驗證 WebGL 參數失敗: {str(e)}")
            return False
            
    def _verify_audio(self, driver: Any) -> bool:
        """
        驗證音訊參數
        
        Args:
            driver: 瀏覽器驅動程式
            
        Returns:
            驗證結果
        """
        try:
            # 執行 JavaScript 取得音訊參數
            audio_params = driver.execute_script("""
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                return {
                    sample_rate: audioContext.sampleRate,
                    channel_count: audioContext.destination.channelCount,
                    buffer_size: audioContext.destination.bufferSize
                };
            """)
            
            # 比對參數
            if audio_params["sample_rate"] != this.fingerprint["audio"]["sample_rate"]:
                return False
                
            if audio_params["channel_count"] != this.fingerprint["audio"]["channel_count"]:
                return False
                
            if audio_params["buffer_size"] != this.fingerprint["audio"]["buffer_size"]:
                return False
                
            return True
            
        except Exception as e:
            this.logger.error(f"驗證音訊參數失敗: {str(e)}")
            return False
            
    def _verify_canvas(self, driver: Any) -> bool:
        """
        驗證 Canvas 參數
        
        Args:
            driver: 瀏覽器驅動程式
            
        Returns:
            驗證結果
        """
        try:
            # 執行 JavaScript 取得 Canvas 參數
            canvas_params = driver.execute_script("""
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                return {
                    noise: ctx.getImageData(0, 0, 1, 1).data[0] / 255,
                    mode: ctx.globalCompositeOperation
                };
            """)
            
            # 比對參數
            if abs(canvas_params["noise"] - this.fingerprint["canvas"]["noise"]) > 0.1:
                return False
                
            if canvas_params["mode"] != this.fingerprint["canvas"]["mode"]:
                return False
                
            return True
            
        except Exception as e:
            this.logger.error(f"驗證 Canvas 參數失敗: {str(e)}")
            return False
            
    def _verify_fonts(self, driver: Any) -> bool:
        """
        驗證字體參數
        
        Args:
            driver: 瀏覽器驅動程式
            
        Returns:
            驗證結果
        """
        try:
            # 執行 JavaScript 取得字體參數
            font_params = driver.execute_script("""
                return {
                    families: document.fonts.check('12px Arial') ? ['Arial'] : [],
                    sizes: [12, 14, 16, 18, 20, 24, 28, 32, 36, 48]
                };
            """)
            
            # 比對參數
            if set(font_params["families"]) != set(this.fingerprint["fonts"]["families"]):
                return False
                
            if set(font_params["sizes"]) != set(this.fingerprint["fonts"]["sizes"]):
                return False
                
            return True
            
        except Exception as e:
            this.logger.error(f"驗證字體參數失敗: {str(e)}")
            return False
            
    def _verify_platform(self, driver: Any) -> bool:
        """
        驗證平台參數
        
        Args:
            driver: 瀏覽器驅動程式
            
        Returns:
            驗證結果
        """
        try:
            # 執行 JavaScript 取得平台參數
            platform_params = driver.execute_script("""
                return {
                    os: navigator.platform,
                    arch: navigator.userAgent.includes('x64') ? 'x64' : 'x86',
                    version: navigator.userAgent
                };
            """)
            
            # 比對參數
            if platform_params["os"] != this.fingerprint["platform"]["os"]:
                return False
                
            if platform_params["arch"] != this.fingerprint["platform"]["arch"]:
                return False
                
            if platform_params["version"] != this.fingerprint["platform"]["version"]:
                return False
                
            return True
            
        except Exception as e:
            this.logger.error(f"驗證平台參數失敗: {str(e)}")
            return False
            
    def _verify_hardware(self, driver: Any) -> bool:
        """
        驗證硬體參數
        
        Args:
            driver: 瀏覽器驅動程式
            
        Returns:
            驗證結果
        """
        try:
            # 執行 JavaScript 取得硬體參數
            hardware_params = driver.execute_script("""
                return {
                    cpu_cores: navigator.hardwareConcurrency,
                    memory: navigator.deviceMemory,
                    gpu: navigator.gpu ? 'enabled' : 'disabled'
                };
            """)
            
            # 比對參數
            if hardware_params["cpu_cores"] != this.fingerprint["hardware"]["cpu_cores"]:
                return False
                
            if hardware_params["memory"] != this.fingerprint["hardware"]["memory"]:
                return False
                
            if hardware_params["gpu"] != this.fingerprint["hardware"]["gpu"]:
                return False
                
            return True
            
        except Exception as e:
            this.logger.error(f"驗證硬體參數失敗: {str(e)}")
            return False
            
    def _verify_screen(self, driver: Any) -> bool:
        """
        驗證螢幕參數
        
        Args:
            driver: 瀏覽器驅動程式
            
        Returns:
            驗證結果
        """
        try:
            # 執行 JavaScript 取得螢幕參數
            screen_params = driver.execute_script("""
                return {
                    width: window.screen.width,
                    height: window.screen.height,
                    color_depth: window.screen.colorDepth,
                    pixel_ratio: window.devicePixelRatio
                };
            """)
            
            # 比對參數
            if screen_params["width"] != this.fingerprint["screen"]["width"]:
                return False
                
            if screen_params["height"] != this.fingerprint["screen"]["height"]:
                return False
                
            if screen_params["color_depth"] != this.fingerprint["screen"]["color_depth"]:
                return False
                
            if screen_params["pixel_ratio"] != this.fingerprint["screen"]["pixel_ratio"]:
                return False
                
            return True
            
        except Exception as e:
            this.logger.error(f"驗證螢幕參數失敗: {str(e)}")
            return False
            
    def _verify_touch(self, driver: Any) -> bool:
        """
        驗證觸控參數
        
        Args:
            driver: 瀏覽器驅動程式
            
        Returns:
            驗證結果
        """
        try:
            # 執行 JavaScript 取得觸控參數
            touch_params = driver.execute_script("""
                return {
                    enabled: 'ontouchstart' in window,
                    points: navigator.maxTouchPoints
                };
            """)
            
            # 比對參數
            if touch_params["enabled"] != this.fingerprint["touch"]["enabled"]:
                return False
                
            if touch_params["points"] != this.fingerprint["touch"]["points"]:
                return False
                
            return True
            
        except Exception as e:
            this.logger.error(f"驗證觸控參數失敗: {str(e)}")
            return False 
"""
瀏覽器配置服務模組

此模組提供了瀏覽器配置相關的服務，包含以下功能：
- 瀏覽器配置管理
- 瀏覽器選項設定
- 瀏覽器擴充功能管理
- 瀏覽器代理設定
"""

import os
import json
import random
from typing import Dict, List, Optional, Union
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from ..core.config import BaseConfig
from ..core.exceptions import BrowserError
from ..utils.browser import BrowserProfile as BrowserUtils

class BrowserProfile:
    """瀏覽器配置服務類別"""
    
    def __init__(self, config: BaseConfig):
        """
        初始化瀏覽器配置服務
        
        Args:
            config: 配置物件
        """
        self.config = config
        self.logger = config.logger
        self.utils = BrowserUtils(config)
        
    def create_options(self) -> Options:
        """
        建立瀏覽器選項
        
        Returns:
            瀏覽器選項
        """
        try:
            options = Options()
            self.utils.apply(options)
            return options
            
        except Exception as e:
            self.logger.error(f"建立瀏覽器選項失敗: {str(e)}")
            raise BrowserError(f"建立瀏覽器選項失敗: {str(e)}")
            
    def create_driver(self, options: Optional[Options] = None) -> webdriver.Chrome:
        """
        建立瀏覽器驅動
        
        Args:
            options: 瀏覽器選項
            
        Returns:
            瀏覽器驅動
        """
        try:
            # 建立選項
            if options is None:
                options = self.create_options()
                
            # 建立驅動
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # 設定視窗大小
            if self.config.browser.window_size:
                driver.set_window_size(
                    self.config.browser.window_size["width"],
                    self.config.browser.window_size["height"]
                )
            else:
                driver.maximize_window()
                
            return driver
            
        except Exception as e:
            self.logger.error(f"建立瀏覽器驅動失敗: {str(e)}")
            raise BrowserError(f"建立瀏覽器驅動失敗: {str(e)}")
            
    def add_extensions(self, options: Options, extensions: List[str]):
        """
        添加瀏覽器擴充功能
        
        Args:
            options: 瀏覽器選項
            extensions: 擴充功能路徑列表
        """
        try:
            for extension in extensions:
                if os.path.exists(extension):
                    options.add_extension(extension)
                else:
                    self.logger.warning(f"擴充功能不存在: {extension}")
                    
        except Exception as e:
            self.logger.error(f"添加瀏覽器擴充功能失敗: {str(e)}")
            raise BrowserError(f"添加瀏覽器擴充功能失敗: {str(e)}")
            
    def set_proxy(self, options: Options, proxy: str):
        """
        設定瀏覽器代理
        
        Args:
            options: 瀏覽器選項
            proxy: 代理伺服器地址
        """
        try:
            options.add_argument(f"--proxy-server={proxy}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器代理失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器代理失敗: {str(e)}")
            
    def set_user_agent(self, options: Options, user_agent: str):
        """
        設定瀏覽器 User-Agent
        
        Args:
            options: 瀏覽器選項
            user_agent: User-Agent 字串
        """
        try:
            options.add_argument(f"--user-agent={user_agent}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器 User-Agent 失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器 User-Agent 失敗: {str(e)}")
            
    def set_language(self, options: Options, language: str):
        """
        設定瀏覽器語言
        
        Args:
            options: 瀏覽器選項
            language: 語言代碼
        """
        try:
            options.add_argument(f"--lang={language}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器語言失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器語言失敗: {str(e)}")
            
    def set_timezone(self, options: Options, timezone: str):
        """
        設定瀏覽器時區
        
        Args:
            options: 瀏覽器選項
            timezone: 時區代碼
        """
        try:
            options.add_argument(f"--timezone={timezone}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器時區失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器時區失敗: {str(e)}")
            
    def set_geolocation(self, options: Options, latitude: float, longitude: float):
        """
        設定瀏覽器地理位置
        
        Args:
            options: 瀏覽器選項
            latitude: 緯度
            longitude: 經度
        """
        try:
            options.add_argument(
                f"--geolocation={latitude},{longitude}"
            )
        except Exception as e:
            this.logger.error(f"設定瀏覽器地理位置失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器地理位置失敗: {str(e)}")
            
    def set_webgl_vendor(self, options: Options, vendor: str):
        """
        設定瀏覽器 WebGL 供應商
        
        Args:
            options: 瀏覽器選項
            vendor: 供應商名稱
        """
        try:
            options.add_argument(f"--webgl-vendor={vendor}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器 WebGL 供應商失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器 WebGL 供應商失敗: {str(e)}")
            
    def set_webgl_renderer(self, options: Options, renderer: str):
        """
        設定瀏覽器 WebGL 渲染器
        
        Args:
            options: 瀏覽器選項
            renderer: 渲染器名稱
        """
        try:
            options.add_argument(f"--webgl-renderer={renderer}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器 WebGL 渲染器失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器 WebGL 渲染器失敗: {str(e)}")
            
    def set_canvas_noise(self, options: Options, noise: float):
        """
        設定瀏覽器 Canvas 雜訊
        
        Args:
            options: 瀏覽器選項
            noise: 雜訊值（0-1）
        """
        try:
            options.add_argument(f"--canvas-noise={noise}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器 Canvas 雜訊失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器 Canvas 雜訊失敗: {str(e)}")
            
    def set_audio_noise(self, options: Options, noise: float):
        """
        設定瀏覽器音訊雜訊
        
        Args:
            options: 瀏覽器選項
            noise: 雜訊值（0-1）
        """
        try:
            options.add_argument(f"--audio-noise={noise}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器音訊雜訊失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器音訊雜訊失敗: {str(e)}")
            
    def set_font_list(self, options: Options, fonts: List[str]):
        """
        設定瀏覽器字型列表
        
        Args:
            options: 瀏覽器選項
            fonts: 字型名稱列表
        """
        try:
            options.add_argument(f"--font-list={','.join(fonts)}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器字型列表失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器字型列表失敗: {str(e)}")
            
    def set_platform(self, options: Options, platform: str):
        """
        設定瀏覽器平台
        
        Args:
            options: 瀏覽器選項
            platform: 平台名稱
        """
        try:
            options.add_argument(f"--platform={platform}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器平台失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器平台失敗: {str(e)}")
            
    def set_hardware_concurrency(self, options: Options, count: int):
        """
        設定瀏覽器硬體並行數
        
        Args:
            options: 瀏覽器選項
            count: 並行數
        """
        try:
            options.add_argument(f"--hardware-concurrency={count}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器硬體並行數失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器硬體並行數失敗: {str(e)}")
            
    def set_device_memory(self, options: Options, memory: int):
        """
        設定瀏覽器裝置記憶體
        
        Args:
            options: 瀏覽器選項
            memory: 記憶體大小（GB）
        """
        try:
            options.add_argument(f"--device-memory={memory}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器裝置記憶體失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器裝置記憶體失敗: {str(e)}")
            
    def set_screen_resolution(self, options: Options, width: int, height: int):
        """
        設定瀏覽器螢幕解析度
        
        Args:
            options: 瀏覽器選項
            width: 寬度
            height: 高度
        """
        try:
            options.add_argument(f"--screen-resolution={width}x{height}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器螢幕解析度失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器螢幕解析度失敗: {str(e)}")
            
    def set_color_depth(self, options: Options, depth: int):
        """
        設定瀏覽器色彩深度
        
        Args:
            options: 瀏覽器選項
            depth: 色彩深度
        """
        try:
            options.add_argument(f"--color-depth={depth}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器色彩深度失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器色彩深度失敗: {str(e)}")
            
    def set_pixel_ratio(self, options: Options, ratio: float):
        """
        設定瀏覽器像素比例
        
        Args:
            options: 瀏覽器選項
            ratio: 像素比例
        """
        try:
            options.add_argument(f"--pixel-ratio={ratio}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器像素比例失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器像素比例失敗: {str(e)}")
            
    def set_touch_points(self, options: Options, points: int):
        """
        設定瀏覽器觸控點數
        
        Args:
            options: 瀏覽器選項
            points: 觸控點數
        """
        try:
            options.add_argument(f"--touch-points={points}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器觸控點數失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器觸控點數失敗: {str(e)}")
            
    def set_webgl_noise(self, options: Options, noise: float):
        """
        設定瀏覽器 WebGL 雜訊
        
        Args:
            options: 瀏覽器選項
            noise: 雜訊值（0-1）
        """
        try:
            options.add_argument(f"--webgl-noise={noise}")
        except Exception as e:
            this.logger.error(f"設定瀏覽器 WebGL 雜訊失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器 WebGL 雜訊失敗: {str(e)}")
            
    def set_webgl_parameters(self, options: Options, parameters: Dict[str, Any]):
        """
        設定瀏覽器 WebGL 參數
        
        Args:
            options: 瀏覽器選項
            parameters: 參數字典
        """
        try:
            options.add_argument(
                f"--webgl-parameters={json.dumps(parameters)}"
            )
        except Exception as e:
            this.logger.error(f"設定瀏覽器 WebGL 參數失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器 WebGL 參數失敗: {str(e)}")
            
    def set_audio_parameters(self, options: Options, parameters: Dict[str, Any]):
        """
        設定瀏覽器音訊參數
        
        Args:
            options: 瀏覽器選項
            parameters: 參數字典
        """
        try:
            options.add_argument(
                f"--audio-parameters={json.dumps(parameters)}"
            )
        except Exception as e:
            this.logger.error(f"設定瀏覽器音訊參數失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器音訊參數失敗: {str(e)}")
            
    def set_canvas_parameters(self, options: Options, parameters: Dict[str, Any]):
        """
        設定瀏覽器 Canvas 參數
        
        Args:
            options: 瀏覽器選項
            parameters: 參數字典
        """
        try:
            options.add_argument(
                f"--canvas-parameters={json.dumps(parameters)}"
            )
        except Exception as e:
            this.logger.error(f"設定瀏覽器 Canvas 參數失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器 Canvas 參數失敗: {str(e)}")
            
    def set_font_parameters(self, options: Options, parameters: Dict[str, Any]):
        """
        設定瀏覽器字型參數
        
        Args:
            options: 瀏覽器選項
            parameters: 參數字典
        """
        try:
            options.add_argument(
                f"--font-parameters={json.dumps(parameters)}"
            )
        except Exception as e:
            this.logger.error(f"設定瀏覽器字型參數失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器字型參數失敗: {str(e)}")
            
    def set_platform_parameters(self, options: Options, parameters: Dict[str, Any]):
        """
        設定瀏覽器平台參數
        
        Args:
            options: 瀏覽器選項
            parameters: 參數字典
        """
        try:
            options.add_argument(
                f"--platform-parameters={json.dumps(parameters)}"
            )
        except Exception as e:
            this.logger.error(f"設定瀏覽器平台參數失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器平台參數失敗: {str(e)}")
            
    def set_hardware_parameters(self, options: Options, parameters: Dict[str, Any]):
        """
        設定瀏覽器硬體參數
        
        Args:
            options: 瀏覽器選項
            parameters: 參數字典
        """
        try:
            options.add_argument(
                f"--hardware-parameters={json.dumps(parameters)}"
            )
        except Exception as e:
            this.logger.error(f"設定瀏覽器硬體參數失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器硬體參數失敗: {str(e)}")
            
    def set_screen_parameters(self, options: Options, parameters: Dict[str, Any]):
        """
        設定瀏覽器螢幕參數
        
        Args:
            options: 瀏覽器選項
            parameters: 參數字典
        """
        try:
            options.add_argument(
                f"--screen-parameters={json.dumps(parameters)}"
            )
        except Exception as e:
            this.logger.error(f"設定瀏覽器螢幕參數失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器螢幕參數失敗: {str(e)}")
            
    def set_touch_parameters(self, options: Options, parameters: Dict[str, Any]):
        """
        設定瀏覽器觸控參數
        
        Args:
            options: 瀏覽器選項
            parameters: 參數字典
        """
        try:
            options.add_argument(
                f"--touch-parameters={json.dumps(parameters)}"
            )
        except Exception as e:
            this.logger.error(f"設定瀏覽器觸控參數失敗: {str(e)}")
            raise BrowserError(f"設定瀏覽器觸控參數失敗: {str(e)}")
            
    def set_random_parameters(self, options: Options):
        """
        設定隨機瀏覽器參數
        
        Args:
            options: 瀏覽器選項
        """
        try:
            # 設定隨機 WebGL 參數
            webgl_parameters = {
                "vendor": random.choice([
                    "Google Inc.",
                    "Intel Inc.",
                    "NVIDIA Corporation",
                    "AMD",
                    "Apple Inc."
                ]),
                "renderer": random.choice([
                    "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)",
                    "ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 Direct3D11 vs_5_0 ps_5_0)",
                    "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0)",
                    "ANGLE (Apple, Apple M1 Direct3D11 vs_5_0 ps_5_0)"
                ])
            }
            this.set_webgl_parameters(options, webgl_parameters)
            
            # 設定隨機音訊參數
            audio_parameters = {
                "noise": random.uniform(0.1, 0.3)
            }
            this.set_audio_parameters(options, audio_parameters)
            
            # 設定隨機 Canvas 參數
            canvas_parameters = {
                "noise": random.uniform(0.1, 0.3)
            }
            this.set_canvas_parameters(options, canvas_parameters)
            
            # 設定隨機字型參數
            font_parameters = {
                "list": [
                    "Arial",
                    "Helvetica",
                    "Times New Roman",
                    "Times",
                    "Courier New",
                    "Courier",
                    "Verdana",
                    "Georgia",
                    "Palatino",
                    "Garamond",
                    "Bookman",
                    "Comic Sans MS",
                    "Trebuchet MS",
                    "Arial Black"
                ]
            }
            this.set_font_parameters(options, font_parameters)
            
            # 設定隨機平台參數
            platform_parameters = {
                "name": random.choice([
                    "Win32",
                    "MacIntel",
                    "Linux x86_64"
                ])
            }
            this.set_platform_parameters(options, platform_parameters)
            
            # 設定隨機硬體參數
            hardware_parameters = {
                "concurrency": random.randint(2, 16),
                "memory": random.randint(4, 32)
            }
            this.set_hardware_parameters(options, hardware_parameters)
            
            # 設定隨機螢幕參數
            screen_parameters = {
                "resolution": random.choice([
                    "1920x1080",
                    "2560x1440",
                    "3840x2160",
                    "1440x900",
                    "1680x1050"
                ]),
                "color_depth": random.choice([24, 32]),
                "pixel_ratio": random.choice([1, 1.5, 2, 2.5, 3])
            }
            this.set_screen_parameters(options, screen_parameters)
            
            # 設定隨機觸控參數
            touch_parameters = {
                "points": random.randint(0, 10)
            }
            this.set_touch_parameters(options, touch_parameters)
            
        except Exception as e:
            this.logger.error(f"設定隨機瀏覽器參數失敗: {str(e)}")
            raise BrowserError(f"設定隨機瀏覽器參數失敗: {str(e)}")
            
    def __enter__(self):
        """上下文管理器進入"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        pass 
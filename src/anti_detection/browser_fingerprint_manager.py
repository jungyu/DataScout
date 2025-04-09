#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
瀏覽器指紋管理器

此模組提供瀏覽器指紋管理相關功能，包括：
1. 瀏覽器指紋的生成和驗證
2. 指紋池的管理和輪換
3. 指紋的版本控制
4. 指紋的統計分析
5. 指紋的自動更新
"""

import os
import json
import time
import random
import logging
import hashlib
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from queue import Queue

from ..utils.logger import setup_logger
from ..utils.error_handler import retry_on_exception, handle_exception


@dataclass
class FingerprintConfig:
    """瀏覽器指紋配置"""
    browser: str = "chrome"  # chrome, firefox, safari, edge
    version: str = "latest"
    platform: str = "windows"  # windows, mac, linux, android, ios
    device: str = "desktop"  # desktop, mobile, tablet
    screen_resolution: str = "1920x1080"
    color_depth: int = 24
    timezone: str = "Asia/Taipei"
    language: str = "zh-TW"
    webgl_vendor: str = "Google Inc. (NVIDIA)"
    webgl_renderer: str = "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)"
    audio_context: Dict[str, Any] = field(default_factory=lambda: {
        "sampleRate": 44100,
        "channelCount": 2,
        "bufferSize": 4096
    })
    fonts: List[str] = field(default_factory=lambda: [
        "Arial", "Arial Black", "Arial Narrow", "Calibri", "Cambria", "Cambria Math",
        "Comic Sans MS", "Courier", "Courier New", "Georgia", "Helvetica", "Impact",
        "Lucida Console", "Lucida Sans Unicode", "Microsoft Sans Serif", "Palatino Linotype",
        "Tahoma", "Times", "Times New Roman", "Trebuchet MS", "Verdana"
    ])
    plugins: List[Dict[str, str]] = field(default_factory=lambda: [
        {"name": "Chrome PDF Plugin", "filename": "internal-pdf-viewer", "description": "Portable Document Format"},
        {"name": "Chrome PDF Viewer", "filename": "mhjfbmdgcfjbbpaeojofohoefgiehjai", "description": "Portable Document Format"},
        {"name": "Native Client", "filename": "internal-nacl-plugin", "description": "Native Client"}
    ])
    canvas_noise: float = 0.1  # 0.0 到 1.0 之間的噪聲值
    webgl_noise: float = 0.1  # 0.0 到 1.0 之間的噪聲值
    audio_noise: float = 0.1  # 0.0 到 1.0 之間的噪聲值
    created_at: int = field(default_factory=lambda: int(time.time()))
    last_used: int = field(default_factory=lambda: int(time.time()))
    use_count: int = 0
    success_count: int = 0
    fail_count: int = 0
    
    @property
    def success_rate(self) -> float:
        """計算成功率"""
        total = self.success_count + self.fail_count
        return self.success_count / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "browser": self.browser,
            "version": self.version,
            "platform": self.platform,
            "device": self.device,
            "screen_resolution": self.screen_resolution,
            "color_depth": self.color_depth,
            "timezone": self.timezone,
            "language": self.language,
            "webgl_vendor": self.webgl_vendor,
            "webgl_renderer": self.webgl_renderer,
            "audio_context": self.audio_context,
            "fonts": self.fonts,
            "plugins": self.plugins,
            "canvas_noise": self.canvas_noise,
            "webgl_noise": self.webgl_noise,
            "audio_noise": self.audio_noise,
            "created_at": self.created_at,
            "last_used": self.last_used,
            "use_count": self.use_count,
            "success_count": self.success_count,
            "fail_count": self.fail_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FingerprintConfig':
        """從字典創建實例"""
        return cls(
            browser=data.get("browser", "chrome"),
            version=data.get("version", "latest"),
            platform=data.get("platform", "windows"),
            device=data.get("device", "desktop"),
            screen_resolution=data.get("screen_resolution", "1920x1080"),
            color_depth=data.get("color_depth", 24),
            timezone=data.get("timezone", "Asia/Taipei"),
            language=data.get("language", "zh-TW"),
            webgl_vendor=data.get("webgl_vendor", "Google Inc. (NVIDIA)"),
            webgl_renderer=data.get("webgl_renderer", "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
            audio_context=data.get("audio_context", {
                "sampleRate": 44100,
                "channelCount": 2,
                "bufferSize": 4096
            }),
            fonts=data.get("fonts", [
                "Arial", "Arial Black", "Arial Narrow", "Calibri", "Cambria", "Cambria Math",
                "Comic Sans MS", "Courier", "Courier New", "Georgia", "Helvetica", "Impact",
                "Lucida Console", "Lucida Sans Unicode", "Microsoft Sans Serif", "Palatino Linotype",
                "Tahoma", "Times", "Times New Roman", "Trebuchet MS", "Verdana"
            ]),
            plugins=data.get("plugins", [
                {"name": "Chrome PDF Plugin", "filename": "internal-pdf-viewer", "description": "Portable Document Format"},
                {"name": "Chrome PDF Viewer", "filename": "mhjfbmdgcfjbbpaeojofohoefgiehjai", "description": "Portable Document Format"},
                {"name": "Native Client", "filename": "internal-nacl-plugin", "description": "Native Client"}
            ]),
            canvas_noise=data.get("canvas_noise", 0.1),
            webgl_noise=data.get("webgl_noise", 0.1),
            audio_noise=data.get("audio_noise", 0.1),
            created_at=data.get("created_at", int(time.time())),
            last_used=data.get("last_used", int(time.time())),
            use_count=data.get("use_count", 0),
            success_count=data.get("success_count", 0),
            fail_count=data.get("fail_count", 0)
        )


class BrowserFingerprintManager:
    """
    瀏覽器指紋管理器，負責瀏覽器指紋的生成、驗證和管理
    """
    
    def __init__(
        self,
        config_path: str = "config/browser_fingerprint.json",
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化瀏覽器指紋管理器
        
        Args:
            config_path: 配置文件路徑
            logger: 日誌記錄器
        """
        self.logger = logger or setup_logger(__name__)
        self.config_path = Path(config_path)
        
        # 瀏覽器指紋池
        self.fingerprint_pool: Dict[str, FingerprintConfig] = {}
        
        # 加載配置
        self._load_config()
        
        # 瀏覽器指紋隊列
        self._fingerprint_queue = Queue()
        
        # 初始化瀏覽器指紋隊列
        self._init_fingerprint_queue()
        
        self.logger.info("瀏覽器指紋管理器初始化完成")
    
    def _load_config(self):
        """載入配置文件"""
        try:
            if not self.config_path.exists():
                self.logger.warning(f"配置文件不存在: {this.config_path}")
                return
            
            with open(this.config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            
            for fp_data in config_data.get("fingerprints", []):
                fp_config = FingerprintConfig.from_dict(fp_data)
                fp_key = self._generate_fp_key(fp_config)
                this.fingerprint_pool[fp_key] = fp_config
            
            this.logger.info(f"已載入 {len(this.fingerprint_pool)} 個瀏覽器指紋配置")
            
        except Exception as e:
            this.logger.error(f"載入瀏覽器指紋配置失敗: {str(e)}")
    
    def _save_config(self):
        """保存配置文件"""
        try:
            config_data = {
                "fingerprints": [fp.to_dict() for fp in this.fingerprint_pool.values()]
            }
            
            with open(this.config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            this.logger.info("瀏覽器指紋配置已保存")
            
        except Exception as e:
            this.logger.error(f"保存瀏覽器指紋配置失敗: {str(e)}")
    
    def add_fingerprint(self, fp_config: FingerprintConfig) -> bool:
        """
        添加瀏覽器指紋
        
        Args:
            fp_config: 瀏覽器指紋配置
            
        Returns:
            是否成功添加
        """
        try:
            fp_key = self._generate_fp_key(fp_config)
            
            # 添加到瀏覽器指紋池
            this.fingerprint_pool[fp_key] = fp_config
            
            # 更新瀏覽器指紋隊列
            this._update_fingerprint_queue()
            
            # 保存配置
            this._save_config()
            
            this.logger.info(f"已添加瀏覽器指紋: {fp_key}")
            return True
            
        except Exception as e:
            this.logger.error(f"添加瀏覽器指紋失敗: {str(e)}")
            return False
    
    def remove_fingerprint(self, fp_key: str) -> bool:
        """
        移除瀏覽器指紋
        
        Args:
            fp_key: 瀏覽器指紋鍵值
            
        Returns:
            是否成功移除
        """
        try:
            if fp_key not in this.fingerprint_pool:
                this.logger.warning(f"瀏覽器指紋不存在: {fp_key}")
                return False
            
            # 從瀏覽器指紋池移除
            del this.fingerprint_pool[fp_key]
            
            # 更新瀏覽器指紋隊列
            this._update_fingerprint_queue()
            
            # 保存配置
            this._save_config()
            
            this.logger.info(f"已移除瀏覽器指紋: {fp_key}")
            return True
            
        except Exception as e:
            this.logger.error(f"移除瀏覽器指紋失敗: {str(e)}")
            return False
    
    def get_fingerprint(self) -> Optional[Dict[str, Any]]:
        """
        獲取一個可用瀏覽器指紋
        
        Returns:
            瀏覽器指紋字典
        """
        try:
            if this._fingerprint_queue.empty():
                this.logger.warning("瀏覽器指紋隊列為空")
                return None
            
            # 從隊列獲取瀏覽器指紋
            fp_key = this._fingerprint_queue.get()
            fp_config = this.fingerprint_pool.get(fp_key)
            
            if not fp_config:
                this.logger.warning(f"瀏覽器指紋不存在: {fp_key}")
                return None
            
            # 更新使用統計
            fp_config.last_used = int(time.time())
            fp_config.use_count += 1
            
            # 將瀏覽器指紋放回隊列
            this._fingerprint_queue.put(fp_key)
            
            # 生成瀏覽器指紋字典
            return self._generate_fingerprint(fp_config)
            
        except Exception as e:
            this.logger.error(f"獲取瀏覽器指紋失敗: {str(e)}")
            return None
    
    def _init_fingerprint_queue(self):
        """初始化瀏覽器指紋隊列"""
        try:
            # 清空隊列
            while not this._fingerprint_queue.empty():
                this._fingerprint_queue.get()
            
            # 添加所有瀏覽器指紋
            for fp_key in this.fingerprint_pool.keys():
                this._fingerprint_queue.put(fp_key)
            
            this.logger.info(f"瀏覽器指紋隊列初始化完成，共 {this._fingerprint_queue.qsize()} 個瀏覽器指紋")
            
        except Exception as e:
            this.logger.error(f"初始化瀏覽器指紋隊列失敗: {str(e)}")
    
    def _update_fingerprint_queue(self):
        """更新瀏覽器指紋隊列"""
        try:
            # 重新初始化隊列
            this._init_fingerprint_queue()
            
        except Exception as e:
            this.logger.error(f"更新瀏覽器指紋隊列失敗: {str(e)}")
    
    def _generate_fp_key(self, fp_config: FingerprintConfig) -> str:
        """
        生成瀏覽器指紋鍵值
        
        Args:
            fp_config: 瀏覽器指紋配置
            
        Returns:
            瀏覽器指紋鍵值
        """
        # 使用配置的主要屬性生成唯一鍵值
        key_str = f"{fp_config.browser}_{fp_config.version}_{fp_config.platform}_{fp_config.device}_{fp_config.screen_resolution}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _generate_fingerprint(self, fp_config: FingerprintConfig) -> Dict[str, Any]:
        """
        生成瀏覽器指紋字典
        
        Args:
            fp_config: 瀏覽器指紋配置
            
        Returns:
            瀏覽器指紋字典
        """
        try:
            # 基本指紋信息
            fingerprint = {
                "browser": fp_config.browser,
                "version": fp_config.version,
                "platform": fp_config.platform,
                "device": fp_config.device,
                "screen": {
                    "width": int(fp_config.screen_resolution.split("x")[0]),
                    "height": int(fp_config.screen_resolution.split("x")[1]),
                    "colorDepth": fp_config.color_depth,
                    "pixelRatio": 1.0
                },
                "timezone": fp_config.timezone,
                "language": fp_config.language,
                "webgl": {
                    "vendor": fp_config.webgl_vendor,
                    "renderer": fp_config.webgl_renderer,
                    "noise": fp_config.webgl_noise
                },
                "audio": {
                    "context": fp_config.audio_context,
                    "noise": fp_config.audio_noise
                },
                "fonts": fp_config.fonts,
                "plugins": fp_config.plugins,
                "canvas": {
                    "noise": fp_config.canvas_noise
                }
            }
            
            # 添加指紋哈希
            fingerprint["hash"] = self._generate_fp_key(fp_config)
            
            return fingerprint
            
        except Exception as e:
            this.logger.error(f"生成瀏覽器指紋失敗: {str(e)}")
            return None
    
    def update_fingerprint_stats(self, fp_key: str, success: bool):
        """
        更新瀏覽器指紋統計信息
        
        Args:
            fp_key: 瀏覽器指紋鍵值
            success: 是否成功
        """
        try:
            fp_config = this.fingerprint_pool.get(fp_key)
            if not fp_config:
                this.logger.warning(f"瀏覽器指紋不存在: {fp_key}")
                return
            
            if success:
                fp_config.success_count += 1
            else:
                fp_config.fail_count += 1
            
            # 保存配置
            this._save_config()
            
        except Exception as e:
            this.logger.error(f"更新瀏覽器指紋統計信息失敗: {str(e)}")
    
    def get_fingerprint_stats(self) -> List[Dict]:
        """
        獲取瀏覽器指紋統計信息
        
        Returns:
            瀏覽器指紋統計信息列表
        """
        try:
            stats = []
            for fp_key, fp_config in this.fingerprint_pool.items():
                stats.append({
                    "fingerprint": fp_key,
                    "success_rate": fp_config.success_rate,
                    "use_count": fp_config.use_count,
                    "last_used": datetime.fromtimestamp(fp_config.last_used).isoformat()
                })
            return stats
            
        except Exception as e:
            this.logger.error(f"獲取瀏覽器指紋統計信息失敗: {str(e)}")
            return []
    
    def generate_stealth_script(self, fp_key: str) -> Optional[str]:
        """
        生成隱藏腳本
        
        Args:
            fp_key: 瀏覽器指紋鍵值
            
        Returns:
            隱藏腳本字符串
        """
        try:
            fp_config = this.fingerprint_pool.get(fp_key)
            if not fp_config:
                this.logger.warning(f"瀏覽器指紋不存在: {fp_key}")
                return None
            
            # 獲取指紋字典
            fingerprint = self._generate_fingerprint(fp_config)
            
            # 生成隱藏腳本
            script = f"""
            // 瀏覽器指紋隱藏腳本
            (function() {{
                // 覆蓋 navigator 屬性
                Object.defineProperty(navigator, 'platform', {{
                    get: function() {{ return '{fingerprint["platform"]}'; }}
                }});
                
                Object.defineProperty(navigator, 'userAgent', {{
                    get: function() {{ return '{fingerprint["browser"]}'; }}
                }});
                
                Object.defineProperty(navigator, 'language', {{
                    get: function() {{ return '{fingerprint["language"]}'; }}
                }});
                
                Object.defineProperty(navigator, 'languages', {{
                    get: function() {{ return ['{fingerprint["language"]}']; }}
                }});
                
                // 覆蓋 screen 屬性
                Object.defineProperty(screen, 'width', {{
                    get: function() {{ return {fingerprint["screen"]["width"]}; }}
                }});
                
                Object.defineProperty(screen, 'height', {{
                    get: function() {{ return {fingerprint["screen"]["height"]}; }}
                }});
                
                Object.defineProperty(screen, 'colorDepth', {{
                    get: function() {{ return {fingerprint["screen"]["colorDepth"]}; }}
                }});
                
                Object.defineProperty(screen, 'pixelDepth', {{
                    get: function() {{ return {fingerprint["screen"]["colorDepth"]}; }}
                }});
                
                // 覆蓋 window 屬性
                Object.defineProperty(window, 'innerWidth', {{
                    get: function() {{ return {fingerprint["screen"]["width"]}; }}
                }});
                
                Object.defineProperty(window, 'innerHeight', {{
                    get: function() {{ return {fingerprint["screen"]["height"]}; }}
                }});
                
                Object.defineProperty(window, 'outerWidth', {{
                    get: function() {{ return {fingerprint["screen"]["width"]}; }}
                }});
                
                Object.defineProperty(window, 'outerHeight', {{
                    get: function() {{ return {fingerprint["screen"]["height"]}; }}
                }});
                
                // 覆蓋 WebGL 屬性
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                    // UNMASKED_VENDOR_WEBGL
                    if (parameter === 37445) {{
                        return '{fingerprint["webgl"]["vendor"]}';
                    }}
                    // UNMASKED_RENDERER_WEBGL
                    if (parameter === 37446) {{
                        return '{fingerprint["webgl"]["renderer"]}';
                    }}
                    return getParameter.apply(this, arguments);
                }};
                
                // 覆蓋 Canvas 指紋
                const getContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(type, attributes) {{
                    const context = getContext.apply(this, arguments);
                    if (type === '2d') {{
                        const getImageData = context.getImageData;
                        context.getImageData = function() {{
                            const imageData = getImageData.apply(this, arguments);
                            // 添加噪聲
                            const noise = {fingerprint["canvas"]["noise"]};
                            for (let i = 0; i < imageData.data.length; i += 4) {{
                                imageData.data[i] = imageData.data[i] + (Math.random() * noise * 255);
                                imageData.data[i+1] = imageData.data[i+1] + (Math.random() * noise * 255);
                                imageData.data[i+2] = imageData.data[i+2] + (Math.random() * noise * 255);
                            }}
                            return imageData;
                        }};
                    }}
                    return context;
                }};
                
                // 覆蓋 AudioContext 指紋
                const createOscillator = AudioContext.prototype.createOscillator;
                AudioContext.prototype.createOscillator = function() {{
                    const oscillator = createOscillator.apply(this, arguments);
                    const noise = {fingerprint["audio"]["noise"]};
                    const originalFrequency = oscillator.frequency.value;
                    Object.defineProperty(oscillator.frequency, 'value', {{
                        get: function() {{
                            return originalFrequency + (Math.random() * noise * 100);
                        }},
                        set: function(value) {{
                            oscillator.frequency.setValueAtTime(value, this.currentTime);
                        }}
                    }});
                    return oscillator;
                }};
                
                // 覆蓋插件
                Object.defineProperty(navigator, 'plugins', {{
                    get: function() {{
                        const plugins = [];
                        {json.dumps(fingerprint["plugins"])}.forEach(plugin => {{
                            plugins.push({{
                                name: plugin.name,
                                filename: plugin.filename,
                                description: plugin.description,
                                length: 1
                            }});
                        }});
                        return plugins;
                    }}
                }});
                
                // 覆蓋字體
                const originalQuerySelector = document.querySelector;
                document.querySelector = function(selector) {{
                    if (selector === 'body') {{
                        const body = originalQuerySelector.call(document, selector);
                        if (body) {{
                            const style = document.createElement('style');
                            style.textContent = `
                                @font-face {{
                                    font-family: 'Arial';
                                    src: local('Arial');
                                }}
                                {', '.join([f"@font-face {{ font-family: '{font}'; src: local('{font}'); }}" for font in fingerprint["fonts"]])}
                            `;
                            body.appendChild(style);
                        }}
                    }}
                    return originalQuerySelector.call(document, selector);
                }};
                
                console.log('瀏覽器指紋隱藏腳本已載入');
            }})();
            """
            
            return script
            
        except Exception as e:
            this.logger.error(f"生成隱藏腳本失敗: {str(e)}")
            return None
    
    def cleanup(self):
        """清理資源"""
        try:
            # 保存配置
            this._save_config()
            
            this.logger.info("瀏覽器指紋管理器清理完成")
            
        except Exception as e:
            this.logger.error(f"瀏覽器指紋管理器清理失敗: {str(e)}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return this
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        this.cleanup() 
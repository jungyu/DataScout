#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
指紋管理器模組

此模組提供指紋管理功能，包括：
1. 指紋生成
2. 指紋注入
3. 指紋驗證
4. 指紋更新
"""

import json
import random
import time
from typing import Dict, List, Optional, Union, Any

from selenium.webdriver.remote.webdriver import WebDriver

from ..base_manager import BaseManager
from ..base_error import AntiDetectionError, handle_error

class FingerprintManager(BaseManager):
    """指紋管理器類"""
    
    def __init__(self, driver: WebDriver, config: Optional[Dict] = None):
        """
        初始化指紋管理器
        
        Args:
            driver: WebDriver 實例
            config: 配置字典
        """
        super().__init__(driver, config)
        self.fingerprint = {}
        self.original_fingerprint = {}
        self.fingerprint_history = []
        
    @handle_error()
    def setup(self) -> None:
        """設置指紋管理器"""
        self._load_config()
        self._capture_original_fingerprint()
        self._generate_fingerprint()
        self._inject_fingerprint()
        self._validate_fingerprint()
        
    @handle_error()
    def cleanup(self) -> None:
        """清理指紋管理器"""
        self._restore_original_fingerprint()
        self.fingerprint = {}
        self.original_fingerprint = {}
        
    @handle_error()
    def _load_config(self) -> None:
        """加載配置"""
        if not self.config:
            self.config = {
                'fingerprint_type': 'random',  # random, consistent, custom
                'platform': 'windows',  # windows, mac, linux
                'browser': 'chrome',  # chrome, firefox, safari, edge
                'browser_version': '120.0.0.0',
                'screen_resolution': '1920x1080',
                'color_depth': 24,
                'timezone': 'Asia/Shanghai',
                'language': 'zh-CN',
                'webgl_vendor': 'Google Inc. (NVIDIA)',
                'webgl_renderer': 'ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 Ti Direct3D11 vs_5_0 ps_5_0)',
                'canvas_noise': 0.1,
                'audio_noise': 0.1,
                'font_list': [
                    'Arial', 'Helvetica', 'Times New Roman', 'Times', 'Courier New', 'Courier',
                    'Verdana', 'Georgia', 'Palatino', 'Garamond', 'Bookman', 'Comic Sans MS',
                    'Trebuchet MS', 'Arial Black'
                ],
                'plugins': [
                    {
                        'name': 'Chrome PDF Plugin',
                        'filename': 'internal-pdf-viewer',
                        'description': 'Portable Document Format',
                        'mime_types': [
                            {
                                'type': 'application/x-google-chrome-pdf',
                                'suffixes': 'pdf',
                                'description': 'Portable Document Format',
                                'enabled': True
                            }
                        ]
                    },
                    {
                        'name': 'Chrome PDF Viewer',
                        'filename': 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                        'description': 'Portable Document Format',
                        'mime_types': [
                            {
                                'type': 'application/pdf',
                                'suffixes': 'pdf',
                                'description': 'Portable Document Format',
                                'enabled': True
                            }
                        ]
                    },
                    {
                        'name': 'Native Client',
                        'filename': 'internal-nacl-plugin',
                        'description': '',
                        'mime_types': []
                    }
                ],
                'update_interval': 3600,  # 指紋更新間隔（秒）
                'last_update': 0
            }
            
    @handle_error()
    def _capture_original_fingerprint(self) -> None:
        """捕獲原始指紋"""
        try:
            self.original_fingerprint = {
                'navigator': self.driver.execute_script("""
                    return {
                        userAgent: navigator.userAgent,
                        platform: navigator.platform,
                        language: navigator.language,
                        languages: navigator.languages,
                        plugins: Array.from(navigator.plugins).map(p => ({
                            name: p.name,
                            filename: p.filename,
                            description: p.description,
                            mimeTypes: Array.from(p).map(m => ({
                                type: m.type,
                                suffixes: m.suffixes,
                                description: m.description,
                                enabled: m.enabledPlugin
                            }))
                        })),
                        webdriver: navigator.webdriver,
                        hardwareConcurrency: navigator.hardwareConcurrency,
                        deviceMemory: navigator.deviceMemory,
                        connection: navigator.connection ? {
                            effectiveType: navigator.connection.effectiveType,
                            rtt: navigator.connection.rtt,
                            downlink: navigator.connection.downlink
                        } : null
                    };
                """),
                'screen': self.driver.execute_script("""
                    return {
                        width: screen.width,
                        height: screen.height,
                        colorDepth: screen.colorDepth,
                        pixelDepth: screen.pixelDepth,
                        availWidth: screen.availWidth,
                        availHeight: screen.availHeight
                    };
                """),
                'window': self.driver.execute_script("""
                    return {
                        innerWidth: window.innerWidth,
                        innerHeight: window.innerHeight,
                        outerWidth: window.outerWidth,
                        outerHeight: window.outerHeight,
                        devicePixelRatio: window.devicePixelRatio
                    };
                """),
                'webgl': self.driver.execute_script("""
                    const canvas = document.createElement('canvas');
                    const gl = canvas.getContext('webgl');
                    if (!gl) return null;
                    
                    return {
                        vendor: gl.getParameter(gl.VENDOR),
                        renderer: gl.getParameter(gl.RENDERER),
                        version: gl.getParameter(gl.VERSION),
                        shadingLanguageVersion: gl.getParameter(gl.SHADING_LANGUAGE_VERSION),
                        extensions: gl.getSupportedExtensions()
                    };
                """),
                'canvas': self.driver.execute_script("""
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    if (!ctx) return null;
                    
                    canvas.width = 200;
                    canvas.height = 50;
                    ctx.textBaseline = 'top';
                    ctx.font = '14px Arial';
                    ctx.textBaseline = 'alphabetic';
                    ctx.fillStyle = '#f60';
                    ctx.fillRect(125, 1, 62, 20);
                    ctx.fillStyle = '#069';
                    ctx.fillText('Cwm fjordbank glyphs vext quiz', 2, 15);
                    ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
                    ctx.fillText('Cwm fjordbank glyphs vext quiz', 4, 17);
                    
                    return canvas.toDataURL();
                """),
                'audio': self.driver.execute_script("""
                    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    const oscillator = audioContext.createOscillator();
                    const analyser = audioContext.createAnalyser();
                    const gainNode = audioContext.createGain();
                    const scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
                    
                    gainNode.gain.value = 0;
                    oscillator.type = 'triangle';
                    oscillator.connect(analyser);
                    analyser.connect(gainNode);
                    gainNode.connect(audioContext.destination);
                    oscillator.start(0);
                    
                    const audioData = [];
                    scriptProcessor.onaudioprocess = function(e) {
                        const inputData = e.inputBuffer.getChannelData(0);
                        for (let i = 0; i < inputData.length; i++) {
                            audioData.push(inputData[i]);
                        }
                    };
                    
                    return audioData.slice(0, 100);
                """),
                'fonts': self.driver.execute_script("""
                    const fontList = [
                        'Arial', 'Helvetica', 'Times New Roman', 'Times', 'Courier New', 'Courier',
                        'Verdana', 'Georgia', 'Palatino', 'Garamond', 'Bookman', 'Comic Sans MS',
                        'Trebuchet MS', 'Arial Black'
                    ];
                    
                    const availableFonts = [];
                    for (const font of fontList) {
                        if (document.fonts.check(`12px "${font}"`)) {
                            availableFonts.push(font);
                        }
                    }
                    
                    return availableFonts;
                """),
                'timezone': self.driver.execute_script("""
                    return {
                        offset: new Date().getTimezoneOffset(),
                        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
                    };
                """)
            }
            self.logger.info("成功捕獲原始指紋")
        except Exception as e:
            self.logger.error(f"捕獲原始指紋失敗: {str(e)}")
            raise
            
    @handle_error()
    def _generate_fingerprint(self) -> None:
        """生成指紋"""
        fingerprint_type = self.config.get('fingerprint_type', 'random')
        
        if fingerprint_type == 'random':
            self._generate_random_fingerprint()
        elif fingerprint_type == 'consistent':
            self._generate_consistent_fingerprint()
        elif fingerprint_type == 'custom':
            self._generate_custom_fingerprint()
        else:
            raise AntiDetectionError(f"未知的指紋類型: {fingerprint_type}")
            
        self.fingerprint_history.append({
            'timestamp': time.time(),
            'fingerprint': self.fingerprint.copy()
        })
        
        # 限制歷史記錄大小
        if len(self.fingerprint_history) > 10:
            self.fingerprint_history.pop(0)
            
    @handle_error()
    def _generate_random_fingerprint(self) -> None:
        """生成隨機指紋"""
        platforms = ['Windows', 'MacIntel', 'Linux x86_64']
        browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
        screen_resolutions = ['1920x1080', '1366x768', '1440x900', '1536x864', '2560x1440']
        timezones = ['Asia/Shanghai', 'America/New_York', 'Europe/London', 'Asia/Tokyo']
        languages = ['zh-CN', 'en-US', 'ja-JP', 'ko-KR', 'fr-FR', 'de-DE']
        
        self.fingerprint = {
            'navigator': {
                'platform': random.choice(platforms),
                'language': random.choice(languages),
                'languages': [random.choice(languages), 'en-US'],
                'webdriver': False,
                'hardwareConcurrency': random.randint(2, 16),
                'deviceMemory': random.choice([2, 4, 8, 16, 32]),
                'connection': {
                    'effectiveType': random.choice(['4g', '5g']),
                    'rtt': random.randint(10, 100),
                    'downlink': random.uniform(1.0, 10.0)
                }
            },
            'screen': {
                'width': int(random.choice(screen_resolutions).split('x')[0]),
                'height': int(random.choice(screen_resolutions).split('x')[1]),
                'colorDepth': 24,
                'pixelDepth': 24,
                'availWidth': int(random.choice(screen_resolutions).split('x')[0]),
                'availHeight': int(random.choice(screen_resolutions).split('x')[1])
            },
            'webgl': {
                'vendor': random.choice([
                    'Google Inc. (NVIDIA)',
                    'Google Inc. (Intel)',
                    'Google Inc. (AMD)',
                    'Apple Inc.',
                    'Mozilla'
                ]),
                'renderer': random.choice([
                    'ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 Ti Direct3D11 vs_5_0 ps_5_0)',
                    'ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)',
                    'ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0)',
                    'Apple M1',
                    'Mozilla'
                ])
            },
            'timezone': {
                'offset': random.choice([-480, -420, -360, -300, -240, -120, 0, 60, 120, 180, 240, 360, 480, 540, 600, 660, 720]),
                'timezone': random.choice(timezones)
            }
        }
        
    @handle_error()
    def _generate_consistent_fingerprint(self) -> None:
        """生成一致指紋"""
        # 使用配置中的設置生成一致指紋
        self.fingerprint = {
            'navigator': {
                'platform': self.config.get('platform', 'windows'),
                'language': self.config.get('language', 'zh-CN'),
                'languages': [self.config.get('language', 'zh-CN'), 'en-US'],
                'webdriver': False,
                'hardwareConcurrency': 8,
                'deviceMemory': 8,
                'connection': {
                    'effectiveType': '4g',
                    'rtt': 50,
                    'downlink': 5.0
                }
            },
            'screen': {
                'width': int(self.config.get('screen_resolution', '1920x1080').split('x')[0]),
                'height': int(self.config.get('screen_resolution', '1920x1080').split('x')[1]),
                'colorDepth': self.config.get('color_depth', 24),
                'pixelDepth': self.config.get('color_depth', 24),
                'availWidth': int(self.config.get('screen_resolution', '1920x1080').split('x')[0]),
                'availHeight': int(self.config.get('screen_resolution', '1920x1080').split('x')[1])
            },
            'webgl': {
                'vendor': self.config.get('webgl_vendor', 'Google Inc. (NVIDIA)'),
                'renderer': self.config.get('webgl_renderer', 'ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 Ti Direct3D11 vs_5_0 ps_5_0)')
            },
            'timezone': {
                'offset': -480,  # UTC+8
                'timezone': self.config.get('timezone', 'Asia/Shanghai')
            }
        }
        
    @handle_error()
    def _generate_custom_fingerprint(self) -> None:
        """生成自定義指紋"""
        # 使用配置中的自定義設置生成指紋
        if 'custom_fingerprint' in self.config:
            self.fingerprint = self.config['custom_fingerprint']
        else:
            self._generate_consistent_fingerprint()
            
    @handle_error()
    def _inject_fingerprint(self) -> None:
        """注入指紋"""
        try:
            # 注入 navigator 指紋
            self.driver.execute_script("""
                Object.defineProperties(navigator, {
                    platform: {
                        get: function() { return arguments[0]; }
                    },
                    language: {
                        get: function() { return arguments[0]; }
                    },
                    languages: {
                        get: function() { return arguments[0]; }
                    },
                    webdriver: {
                        get: function() { return arguments[0]; }
                    },
                    hardwareConcurrency: {
                        get: function() { return arguments[0]; }
                    },
                    deviceMemory: {
                        get: function() { return arguments[0]; }
                    }
                });
            """, self.fingerprint['navigator']['platform'],
                self.fingerprint['navigator']['language'],
                self.fingerprint['navigator']['languages'],
                self.fingerprint['navigator']['webdriver'],
                self.fingerprint['navigator']['hardwareConcurrency'],
                self.fingerprint['navigator']['deviceMemory'])
            
            # 注入 screen 指紋
            self.driver.execute_script("""
                Object.defineProperties(screen, {
                    width: {
                        get: function() { return arguments[0]; }
                    },
                    height: {
                        get: function() { return arguments[0]; }
                    },
                    colorDepth: {
                        get: function() { return arguments[0]; }
                    },
                    pixelDepth: {
                        get: function() { return arguments[0]; }
                    },
                    availWidth: {
                        get: function() { return arguments[0]; }
                    },
                    availHeight: {
                        get: function() { return arguments[0]; }
                    }
                });
            """, self.fingerprint['screen']['width'],
                self.fingerprint['screen']['height'],
                self.fingerprint['screen']['colorDepth'],
                self.fingerprint['screen']['pixelDepth'],
                self.fingerprint['screen']['availWidth'],
                self.fingerprint['screen']['availHeight'])
            
            # 注入 webgl 指紋
            self.driver.execute_script("""
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl');
                if (gl) {
                    const getParameter = gl.getParameter.bind(gl);
                    gl.getParameter = function(parameter) {
                        if (parameter === gl.VENDOR) {
                            return arguments[0];
                        }
                        if (parameter === gl.RENDERER) {
                            return arguments[1];
                        }
                        return getParameter(parameter);
                    };
                }
            """, self.fingerprint['webgl']['vendor'],
                self.fingerprint['webgl']['renderer'])
            
            # 注入時區指紋
            self.driver.execute_script("""
                Date.prototype.getTimezoneOffset = function() {
                    return arguments[0];
                };
                
                Intl.DateTimeFormat = function() {
                    return {
                        resolvedOptions: function() {
                            return {
                                timeZone: arguments[0]
                            };
                        }
                    };
                };
            """, self.fingerprint['timezone']['offset'],
                self.fingerprint['timezone']['timezone'])
            
            self.logger.info("成功注入指紋")
        except Exception as e:
            self.logger.error(f"注入指紋失敗: {str(e)}")
            raise
            
    @handle_error()
    def _restore_original_fingerprint(self) -> None:
        """恢復原始指紋"""
        try:
            # 恢復 navigator 指紋
            self.driver.execute_script("""
                Object.defineProperties(navigator, {
                    platform: {
                        get: function() { return arguments[0]; }
                    },
                    language: {
                        get: function() { return arguments[0]; }
                    },
                    languages: {
                        get: function() { return arguments[0]; }
                    },
                    webdriver: {
                        get: function() { return arguments[0]; }
                    },
                    hardwareConcurrency: {
                        get: function() { return arguments[0]; }
                    },
                    deviceMemory: {
                        get: function() { return arguments[0]; }
                    }
                });
            """, self.original_fingerprint['navigator']['platform'],
                self.original_fingerprint['navigator']['language'],
                self.original_fingerprint['navigator']['languages'],
                self.original_fingerprint['navigator']['webdriver'],
                self.original_fingerprint['navigator']['hardwareConcurrency'],
                self.original_fingerprint['navigator']['deviceMemory'])
            
            # 恢復 screen 指紋
            self.driver.execute_script("""
                Object.defineProperties(screen, {
                    width: {
                        get: function() { return arguments[0]; }
                    },
                    height: {
                        get: function() { return arguments[0]; }
                    },
                    colorDepth: {
                        get: function() { return arguments[0]; }
                    },
                    pixelDepth: {
                        get: function() { return arguments[0]; }
                    },
                    availWidth: {
                        get: function() { return arguments[0]; }
                    },
                    availHeight: {
                        get: function() { return arguments[0]; }
                    }
                });
            """, self.original_fingerprint['screen']['width'],
                self.original_fingerprint['screen']['height'],
                self.original_fingerprint['screen']['colorDepth'],
                self.original_fingerprint['screen']['pixelDepth'],
                self.original_fingerprint['screen']['availWidth'],
                self.original_fingerprint['screen']['availHeight'])
            
            # 恢復 webgl 指紋
            self.driver.execute_script("""
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl');
                if (gl) {
                    const getParameter = gl.getParameter.bind(gl);
                    gl.getParameter = function(parameter) {
                        if (parameter === gl.VENDOR) {
                            return arguments[0];
                        }
                        if (parameter === gl.RENDERER) {
                            return arguments[1];
                        }
                        return getParameter(parameter);
                    };
                }
            """, self.original_fingerprint['webgl']['vendor'],
                self.original_fingerprint['webgl']['renderer'])
            
            # 恢復時區指紋
            self.driver.execute_script("""
                Date.prototype.getTimezoneOffset = function() {
                    return arguments[0];
                };
                
                Intl.DateTimeFormat = function() {
                    return {
                        resolvedOptions: function() {
                            return {
                                timeZone: arguments[0]
                            };
                        }
                    };
                };
            """, self.original_fingerprint['timezone']['offset'],
                self.original_fingerprint['timezone']['timezone'])
            
            self.logger.info("成功恢復原始指紋")
        except Exception as e:
            self.logger.error(f"恢復原始指紋失敗: {str(e)}")
            raise
            
    @handle_error()
    def _validate_fingerprint(self) -> None:
        """驗證指紋"""
        try:
            current_fingerprint = self._capture_current_fingerprint()
            
            # 比較當前指紋與注入指紋
            for key, value in self.fingerprint.items():
                if key in current_fingerprint:
                    for subkey, subvalue in value.items():
                        if subkey in current_fingerprint[key]:
                            if current_fingerprint[key][subkey] != subvalue:
                                self.logger.warning(f"指紋驗證失敗: {key}.{subkey} 不匹配")
                                self.logger.warning(f"期望值: {subvalue}, 實際值: {current_fingerprint[key][subkey]}")
                                
            self.logger.info("指紋驗證完成")
        except Exception as e:
            self.logger.error(f"指紋驗證失敗: {str(e)}")
            raise
            
    @handle_error()
    def _capture_current_fingerprint(self) -> Dict[str, Any]:
        """捕獲當前指紋"""
        return self.driver.execute_script("""
            return {
                navigator: {
                    platform: navigator.platform,
                    language: navigator.language,
                    languages: navigator.languages,
                    webdriver: navigator.webdriver,
                    hardwareConcurrency: navigator.hardwareConcurrency,
                    deviceMemory: navigator.deviceMemory
                },
                screen: {
                    width: screen.width,
                    height: screen.height,
                    colorDepth: screen.colorDepth,
                    pixelDepth: screen.pixelDepth,
                    availWidth: screen.availWidth,
                    availHeight: screen.availHeight
                },
                webgl: (function() {
                    const canvas = document.createElement('canvas');
                    const gl = canvas.getContext('webgl');
                    if (!gl) return null;
                    
                    return {
                        vendor: gl.getParameter(gl.VENDOR),
                        renderer: gl.getParameter(gl.RENDERER)
                    };
                })(),
                timezone: {
                    offset: new Date().getTimezoneOffset(),
                    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
                }
            };
        """)
        
    @handle_error()
    def update_fingerprint(self) -> None:
        """更新指紋"""
        current_time = time.time()
        last_update = self.config.get('last_update', 0)
        update_interval = self.config.get('update_interval', 3600)
        
        if current_time - last_update >= update_interval:
            self._generate_fingerprint()
            self._inject_fingerprint()
            self._validate_fingerprint()
            
            self.config['last_update'] = current_time
            self.logger.info(f"指紋已更新，下次更新時間: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time + update_interval))}")
            
    @handle_error()
    def get_fingerprint(self) -> Dict[str, Any]:
        """
        獲取當前指紋
        
        Returns:
            當前指紋
        """
        return self.fingerprint.copy()
        
    @handle_error()
    def get_fingerprint_history(self) -> List[Dict[str, Any]]:
        """
        獲取指紋歷史
        
        Returns:
            指紋歷史
        """
        return self.fingerprint_history.copy()
        
    @handle_error()
    def save_fingerprint(self, file_path: str) -> None:
        """
        保存指紋到文件
        
        Args:
            file_path: 文件路徑
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'fingerprint': self.fingerprint,
                    'original_fingerprint': self.original_fingerprint,
                    'fingerprint_history': self.fingerprint_history,
                    'config': self.config
                }, f, ensure_ascii=False, indent=2)
            self.logger.info(f"指紋已保存到: {file_path}")
        except Exception as e:
            self.logger.error(f"保存指紋失敗: {str(e)}")
            raise
            
    @handle_error()
    def load_fingerprint(self, file_path: str) -> None:
        """
        從文件加載指紋
        
        Args:
            file_path: 文件路徑
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.fingerprint = data.get('fingerprint', {})
            self.original_fingerprint = data.get('original_fingerprint', {})
            self.fingerprint_history = data.get('fingerprint_history', [])
            self.config.update(data.get('config', {}))
            
            self._inject_fingerprint()
            self._validate_fingerprint()
            
            self.logger.info(f"已從 {file_path} 加載指紋")
        except Exception as e:
            self.logger.error(f"加載指紋失敗: {str(e)}")
            raise 
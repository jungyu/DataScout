#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
平台指紋偽裝模組

此模組提供平台指紋偽裝功能，包括：
1. 操作系統偽裝
2. 瀏覽器偽裝
3. 硬件平台偽裝
4. 語言和地區偽裝
"""

from typing import Dict, Any, List
import random
from loguru import logger

from ..utils.exceptions import AntiDetectionException


class PlatformSpoofer:
    """平台指紋偽裝器"""
    
    def __init__(self):
        """初始化平台指紋偽裝器"""
        # 操作系統列表
        self.operating_systems = [
            {
                "name": "Windows",
                "versions": ["10.0", "11.0"],
                "architectures": ["x86_64", "x86"],
                "platform": "Win32"
            },
            {
                "name": "macOS",
                "versions": ["10_15", "11_0", "12_0", "13_0"],
                "architectures": ["x86_64", "arm64"],
                "platform": "MacIntel"
            },
            {
                "name": "Linux",
                "versions": ["x86_64", "i686"],
                "architectures": ["x86_64", "x86"],
                "platform": "Linux x86_64"
            }
        ]
        
        # 瀏覽器列表
        self.browsers = [
            {
                "name": "Chrome",
                "versions": ["110.0.0.0", "111.0.0.0", "112.0.0.0", "113.0.0.0"],
                "userAgent": "Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
            },
            {
                "name": "Firefox",
                "versions": ["110.0", "111.0", "112.0", "113.0"],
                "userAgent": "Mozilla/5.0 ({platform}; rv:{version}) Gecko/20100101 Firefox/{version}"
            },
            {
                "name": "Safari",
                "versions": ["16.0", "16.1", "16.2", "16.3"],
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X {os_version}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15"
            }
        ]
        
        # 硬件平台列表
        self.hardware_platforms = [
            {
                "name": "Desktop",
                "processors": ["Intel", "AMD"],
                "memory": [8, 16, 32],
                "cores": [4, 6, 8, 12, 16]
            },
            {
                "name": "Laptop",
                "processors": ["Intel", "AMD", "Apple"],
                "memory": [8, 16, 32],
                "cores": [4, 6, 8, 10]
            },
            {
                "name": "Mobile",
                "processors": ["Qualcomm", "MediaTek", "Apple"],
                "memory": [4, 6, 8],
                "cores": [4, 6, 8]
            }
        ]
        
        # 語言和地區列表
        self.languages = [
            "en-US",
            "en-GB",
            "zh-CN",
            "zh-TW",
            "ja-JP",
            "ko-KR",
            "fr-FR",
            "de-DE",
            "es-ES",
            "it-IT"
        ]
    
    def get_random_platform_fingerprint(self) -> Dict[str, Any]:
        """
        獲取隨機平台指紋
        
        Returns:
            Dict[str, Any]: 平台指紋信息
        """
        os = random.choice(self.operating_systems)
        browser = random.choice(self.browsers)
        hardware = random.choice(self.hardware_platforms)
        
        return {
            "os": {
                "name": os["name"],
                "version": random.choice(os["versions"]),
                "architecture": random.choice(os["architectures"]),
                "platform": os["platform"]
            },
            "browser": {
                "name": browser["name"],
                "version": random.choice(browser["versions"]),
                "userAgent": browser["userAgent"].format(
                    platform=os["platform"],
                    version=random.choice(browser["versions"]),
                    os_version=random.choice(os["versions"])
                )
            },
            "hardware": {
                "platform": hardware["name"],
                "processor": random.choice(hardware["processors"]),
                "memory": random.choice(hardware["memory"]),
                "cores": random.choice(hardware["cores"])
            },
            "language": random.choice(self.languages)
        }
    
    def get_consistent_platform_fingerprint(self) -> Dict[str, Any]:
        """
        獲取一致的平台指紋（每次調用返回相同的指紋）
        
        Returns:
            Dict[str, Any]: 平台指紋信息
        """
        return {
            "os": {
                "name": "Windows",
                "version": "10.0",
                "architecture": "x86_64",
                "platform": "Win32"
            },
            "browser": {
                "name": "Chrome",
                "version": "110.0.0.0",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
            },
            "hardware": {
                "platform": "Desktop",
                "processor": "Intel",
                "memory": 16,
                "cores": 8
            },
            "language": "en-US"
        }
    
    def apply_spoof(self, page) -> None:
        """
        應用平台指紋偽裝
        
        Args:
            page: Playwright 頁面對象
        """
        try:
            fingerprint = self.get_consistent_platform_fingerprint()
            
            script = f"""
            // 修改 navigator 屬性
            Object.defineProperties(navigator, {{
                platform: {{
                    get: function() {{
                        return '{fingerprint["os"]["platform"]}';
                    }}
                }},
                userAgent: {{
                    get: function() {{
                        return '{fingerprint["browser"]["userAgent"]}';
                    }}
                }},
                language: {{
                    get: function() {{
                        return '{fingerprint["language"]}';
                    }}
                }},
                languages: {{
                    get: function() {{
                        return ['{fingerprint["language"]}'];
                    }}
                }},
                hardwareConcurrency: {{
                    get: function() {{
                        return {fingerprint["hardware"]["cores"]};
                    }}
                }},
                deviceMemory: {{
                    get: function() {{
                        return {fingerprint["hardware"]["memory"]};
                    }}
                }}
            }});
            
            // 修改 window 屬性
            Object.defineProperties(window, {{
                innerWidth: {{
                    get: function() {{
                        return {fingerprint["screen"]["width"]};
                    }}
                }},
                innerHeight: {{
                    get: function() {{
                        return {fingerprint["screen"]["height"]};
                    }}
                }},
                outerWidth: {{
                    get: function() {{
                        return {fingerprint["screen"]["width"]};
                    }}
                }},
                outerHeight: {{
                    get: function() {{
                        return {fingerprint["screen"]["height"]};
                    }}
                }}
            }});
            
            // 修改 document 屬性
            Object.defineProperties(document, {{
                documentElement: {{
                    get: function() {{
                        const element = document.documentElement;
                        element.style.width = '{fingerprint["screen"]["width"]}px';
                        element.style.height = '{fingerprint["screen"]["height"]}px';
                        return element;
                    }}
                }}
            }});
            
            // 修改 screen 屬性
            Object.defineProperties(screen, {{
                width: {{
                    get: function() {{
                        return {fingerprint["screen"]["width"]};
                    }}
                }},
                height: {{
                    get: function() {{
                        return {fingerprint["screen"]["height"]};
                    }}
                }},
                availWidth: {{
                    get: function() {{
                        return {fingerprint["screen"]["width"]};
                    }}
                }},
                availHeight: {{
                    get: function() {{
                        return {fingerprint["screen"]["height"]};
                    }}
                }}
            }});
            """
            
            page.add_init_script(script)
            logger.info("已應用平台指紋偽裝")
        except Exception as e:
            logger.error(f"應用平台指紋偽裝時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"應用平台指紋偽裝失敗: {str(e)}") 
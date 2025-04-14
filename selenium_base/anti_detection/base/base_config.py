#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
反檢測配置模組

提供反檢測的基礎配置
"""

import os
import json
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field

from ...core.config import BaseConfig
from ...core.utils import Utils
from ...core.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class ProxyConfig:
    """代理配置"""
    enabled: bool = False
    proxy_type: str = "http"  # http, https, socks4, socks5
    host: str = ""
    port: int = 0
    username: Optional[str] = None
    password: Optional[str] = None
    rotate: bool = False
    rotation_interval: int = 10  # 分鐘
    proxy_list: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class UserAgentConfig:
    """用戶代理配置"""
    enabled: bool = False
    rotate: bool = False
    rotation_interval: int = 10  # 分鐘
    custom_user_agent: Optional[str] = None
    user_agent_list: List[str] = field(default_factory=list)

@dataclass
class FingerprintConfig:
    """指紋配置"""
    enabled: bool = False
    canvas_noise: bool = True
    webgl_noise: bool = True
    audio_noise: bool = True
    fonts_noise: bool = True
    timezone_noise: bool = True
    language_noise: bool = True
    platform_noise: bool = True
    hardware_concurrency_noise: bool = True
    device_memory_noise: bool = True

@dataclass
class StealthConfig:
    """隱藏身份配置"""
    enabled: bool = False
    webdriver_flags: List[str] = field(default_factory=lambda: [
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--disable-notifications",
        "--disable-popup-blocking",
        "--disable-save-password-bubble",
        "--disable-translate",
        "--disable-zero-browsers-open-for-tests",
        "--no-default-browser-check",
        "--no-first-run",
        "--password-store=basic",
        "--use-mock-keychain",
    ])
    cdp_commands: List[Dict[str, Any]] = field(default_factory=lambda: [
        {"command": "Page.addScriptToEvaluateOnNewDocument", "params": {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        }},
        {"command": "Network.setUserAgentOverride", "params": {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }},
    ])

@dataclass
class HoneypotConfig:
    """蜜罐檢測配置"""
    enabled: bool = False
    check_links: bool = True
    check_forms: bool = True
    check_buttons: bool = True
    check_hidden_elements: bool = True
    check_iframes: bool = True
    check_redirects: bool = True
    check_javascript: bool = True

@dataclass
class BehaviorConfig:
    """行為模擬配置"""
    enabled: bool = False
    random_mouse_movements: bool = True
    random_scrolling: bool = True
    random_typing: bool = True
    random_clicks: bool = True
    random_pauses: bool = True
    human_like_behavior: bool = True
    behavior_patterns: List[str] = field(default_factory=lambda: ["browse", "search", "read"])

@dataclass
class DetectionConfig:
    """檢測配置"""
    enabled: bool = False
    check_webdriver: bool = True
    check_automation: bool = True
    check_plugins: bool = True
    check_languages: bool = True
    check_platform: bool = True
    check_timezone: bool = True
    check_screen: bool = True
    check_canvas: bool = True
    check_webgl: bool = True
    check_audio: bool = True
    check_fonts: bool = True

@dataclass
class EvasionConfig:
    """逃避檢測配置"""
    enabled: bool = False
    use_evasion_scripts: bool = True
    use_evasion_techniques: bool = True
    evasion_scripts: List[str] = field(default_factory=lambda: [
        "webdriver_evasion.js",
        "automation_evasion.js",
        "fingerprint_evasion.js",
    ])
    evasion_techniques: List[str] = field(default_factory=lambda: [
        "random_delays",
        "mouse_movements",
        "keyboard_events",
        "scroll_events",
        "click_events",
    ])

@dataclass
class AntiDetectionConfig(BaseConfig):
    """反檢測配置"""
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    user_agent: UserAgentConfig = field(default_factory=UserAgentConfig)
    fingerprint: FingerprintConfig = field(default_factory=FingerprintConfig)
    stealth: StealthConfig = field(default_factory=StealthConfig)
    honeypot: HoneypotConfig = field(default_factory=HoneypotConfig)
    behavior: BehaviorConfig = field(default_factory=BehaviorConfig)
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    evasion: EvasionConfig = field(default_factory=EvasionConfig)
    
    def save(self, path: str) -> None:
        """
        保存配置到文件
        
        Args:
            path: 文件路徑
        """
        try:
            Utils.ensure_dir(os.path.dirname(path))
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
            logger.info(f"配置已保存到：{path}")
        except Exception as e:
            logger.error(f"保存配置失敗：{str(e)}")
            raise
            
    def load(self, path: str) -> None:
        """
        從文件加載配置
        
        Args:
            path: 文件路徑
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            self.__dict__.update(self.from_dict(config_dict).__dict__)
            logger.info(f"配置已從 {path} 加載")
        except Exception as e:
            logger.error(f"加載配置失敗：{str(e)}")
            raise
            
    def validate(self) -> bool:
        """
        驗證配置
        
        Returns:
            配置是否有效
        """
        try:
            # 驗證代理配置
            if self.proxy.enabled:
                if not self.proxy.host or not self.proxy.port:
                    return False
                    
            # 驗證用戶代理配置
            if self.user_agent.enabled and self.user_agent.rotate:
                if not self.user_agent.user_agent_list:
                    return False
                    
            # 驗證指紋配置
            if self.fingerprint.enabled:
                pass  # 添加指紋相關驗證
                
            # 驗證隱藏配置
            if self.stealth.enabled:
                if not self.stealth.webdriver_flags:
                    return False
                    
            # 驗證行為配置
            if self.behavior.enabled:
                if not self.behavior.behavior_patterns:
                    return False
                    
            # 驗證規避配置
            if self.evasion.enabled:
                if not self.evasion.evasion_scripts:
                    return False
                    
            return True
        except Exception as e:
            logger.error(f"驗證配置失敗：{str(e)}")
            return False
            
    def merge(self, other: Union[Dict, 'AntiDetectionConfig']) -> None:
        """
        合併配置
        
        Args:
            other: 要合併的配置
        """
        if isinstance(other, dict):
            other = self.from_dict(other)
        self.__dict__.update(other.__dict__)
    
    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "proxy": {
                "enabled": self.proxy.enabled,
                "proxy_type": self.proxy.proxy_type,
                "host": self.proxy.host,
                "port": self.proxy.port,
                "username": self.proxy.username,
                "password": self.proxy.password,
                "rotate": self.proxy.rotate,
                "rotation_interval": self.proxy.rotation_interval,
                "proxy_list": self.proxy.proxy_list,
            },
            "user_agent": {
                "enabled": self.user_agent.enabled,
                "rotate": self.user_agent.rotate,
                "rotation_interval": self.user_agent.rotation_interval,
                "custom_user_agent": self.user_agent.custom_user_agent,
                "user_agent_list": self.user_agent.user_agent_list,
            },
            "fingerprint": {
                "enabled": self.fingerprint.enabled,
                "canvas_noise": self.fingerprint.canvas_noise,
                "webgl_noise": self.fingerprint.webgl_noise,
                "audio_noise": self.fingerprint.audio_noise,
                "fonts_noise": self.fingerprint.fonts_noise,
                "timezone_noise": self.fingerprint.timezone_noise,
                "language_noise": self.fingerprint.language_noise,
                "platform_noise": self.fingerprint.platform_noise,
                "hardware_concurrency_noise": self.fingerprint.hardware_concurrency_noise,
                "device_memory_noise": self.fingerprint.device_memory_noise,
            },
            "stealth": {
                "enabled": self.stealth.enabled,
                "webdriver_flags": self.stealth.webdriver_flags,
                "cdp_commands": self.stealth.cdp_commands,
            },
            "honeypot": {
                "enabled": self.honeypot.enabled,
                "check_links": self.honeypot.check_links,
                "check_forms": self.honeypot.check_forms,
                "check_buttons": self.honeypot.check_buttons,
                "check_hidden_elements": self.honeypot.check_hidden_elements,
                "check_iframes": self.honeypot.check_iframes,
                "check_redirects": self.honeypot.check_redirects,
                "check_javascript": self.honeypot.check_javascript,
            },
            "behavior": {
                "enabled": self.behavior.enabled,
                "random_mouse_movements": self.behavior.random_mouse_movements,
                "random_scrolling": self.behavior.random_scrolling,
                "random_typing": self.behavior.random_typing,
                "random_clicks": self.behavior.random_clicks,
                "random_pauses": self.behavior.random_pauses,
                "human_like_behavior": self.behavior.human_like_behavior,
                "behavior_patterns": self.behavior.behavior_patterns,
            },
            "detection": {
                "enabled": self.detection.enabled,
                "check_webdriver": self.detection.check_webdriver,
                "check_automation": self.detection.check_automation,
                "check_plugins": self.detection.check_plugins,
                "check_languages": self.detection.check_languages,
                "check_platform": self.detection.check_platform,
                "check_timezone": self.detection.check_timezone,
                "check_screen": self.detection.check_screen,
                "check_canvas": self.detection.check_canvas,
                "check_webgl": self.detection.check_webgl,
                "check_audio": self.detection.check_audio,
                "check_fonts": self.detection.check_fonts,
            },
            "evasion": {
                "enabled": self.evasion.enabled,
                "use_evasion_scripts": self.evasion.use_evasion_scripts,
                "use_evasion_techniques": self.evasion.use_evasion_techniques,
                "evasion_scripts": self.evasion.evasion_scripts,
                "evasion_techniques": self.evasion.evasion_techniques,
            },
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'AntiDetectionConfig':
        """從字典創建配置"""
        proxy_config = ProxyConfig(**config_dict.get("proxy", {}))
        user_agent_config = UserAgentConfig(**config_dict.get("user_agent", {}))
        fingerprint_config = FingerprintConfig(**config_dict.get("fingerprint", {}))
        stealth_config = StealthConfig(**config_dict.get("stealth", {}))
        honeypot_config = HoneypotConfig(**config_dict.get("honeypot", {}))
        behavior_config = BehaviorConfig(**config_dict.get("behavior", {}))
        detection_config = DetectionConfig(**config_dict.get("detection", {}))
        evasion_config = EvasionConfig(**config_dict.get("evasion", {}))
        
        return cls(
            proxy=proxy_config,
            user_agent=user_agent_config,
            fingerprint=fingerprint_config,
            stealth=stealth_config,
            honeypot=honeypot_config,
            behavior=behavior_config,
            detection=detection_config,
            evasion=evasion_config,
        ) 
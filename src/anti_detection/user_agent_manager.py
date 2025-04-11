#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
User-Agent 管理器

此模組提供 User-Agent 管理相關功能，包括：
1. User-Agent 的生成和驗證
2. User-Agent 池的管理和輪換
3. User-Agent 的版本控制
4. User-Agent 的統計分析
5. User-Agent 的自動更新
"""

import os
import json
import time
import random
import logging
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from queue import Queue

from src.core.utils.logger import setup_logger
from ..utils.error_handler import retry_on_exception, handle_exception


@dataclass
class UserAgentConfig:
    """User-Agent 配置"""
    browser: str = "chrome"  # chrome, firefox, safari, edge
    version: str = "latest"
    platform: str = "windows"  # windows, mac, linux, android, ios
    device: str = "desktop"  # desktop, mobile, tablet
    language: str = "en-US"
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
            "language": self.language,
            "created_at": self.created_at,
            "last_used": self.last_used,
            "use_count": self.use_count,
            "success_count": self.success_count,
            "fail_count": self.fail_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserAgentConfig':
        """從字典創建實例"""
        return cls(
            browser=data.get("browser", "chrome"),
            version=data.get("version", "latest"),
            platform=data.get("platform", "windows"),
            device=data.get("device", "desktop"),
            language=data.get("language", "en-US"),
            created_at=data.get("created_at", int(time.time())),
            last_used=data.get("last_used", int(time.time())),
            use_count=data.get("use_count", 0),
            success_count=data.get("success_count", 0),
            fail_count=data.get("fail_count", 0)
        )


class UserAgentManager:
    """
    User-Agent 管理器，負責 User-Agent 的生成、驗證和管理
    """
    
    def __init__(
        self,
        config_path: str = "config/user_agent.json",
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化 User-Agent 管理器
        
        Args:
            config_path: 配置文件路徑
            logger: 日誌記錄器
        """
        self.logger = logger or setup_logger(__name__)
        self.config_path = Path(config_path)
        
        # User-Agent 池
        self.user_agent_pool: Dict[str, UserAgentConfig] = {}
        
        # 加載配置
        self._load_config()
        
        # User-Agent 隊列
        self._user_agent_queue = Queue()
        
        # 初始化 User-Agent 隊列
        self._init_user_agent_queue()
        
        self.logger.info("User-Agent 管理器初始化完成")
    
    def _load_config(self):
        """載入配置文件"""
        try:
            if not self.config_path.exists():
                self.logger.warning(f"配置文件不存在: {self.config_path}")
                return
            
            with open(self.config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            
            for ua_data in config_data.get("user_agents", []):
                ua_config = UserAgentConfig.from_dict(ua_data)
                ua_key = self._generate_ua_key(ua_config)
                self.user_agent_pool[ua_key] = ua_config
            
            self.logger.info(f"已載入 {len(self.user_agent_pool)} 個 User-Agent 配置")
            
        except Exception as e:
            self.logger.error(f"載入 User-Agent 配置失敗: {str(e)}")
    
    def _save_config(self):
        """保存配置文件"""
        try:
            config_data = {
                "user_agents": [ua.to_dict() for ua in self.user_agent_pool.values()]
            }
            
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("User-Agent 配置已保存")
            
        except Exception as e:
            self.logger.error(f"保存 User-Agent 配置失敗: {str(e)}")
    
    def add_user_agent(self, ua_config: UserAgentConfig) -> bool:
        """
        添加 User-Agent
        
        Args:
            ua_config: User-Agent 配置
            
        Returns:
            是否成功添加
        """
        try:
            ua_key = self._generate_ua_key(ua_config)
            
            # 添加到 User-Agent 池
            self.user_agent_pool[ua_key] = ua_config
            
            # 更新 User-Agent 隊列
            self._update_user_agent_queue()
            
            # 保存配置
            self._save_config()
            
            self.logger.info(f"已添加 User-Agent: {ua_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加 User-Agent 失敗: {str(e)}")
            return False
    
    def remove_user_agent(self, ua_key: str) -> bool:
        """
        移除 User-Agent
        
        Args:
            ua_key: User-Agent 鍵值
            
        Returns:
            是否成功移除
        """
        try:
            if ua_key not in self.user_agent_pool:
                self.logger.warning(f"User-Agent 不存在: {ua_key}")
                return False
            
            # 從 User-Agent 池移除
            del self.user_agent_pool[ua_key]
            
            # 更新 User-Agent 隊列
            self._update_user_agent_queue()
            
            # 保存配置
            self._save_config()
            
            self.logger.info(f"已移除 User-Agent: {ua_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"移除 User-Agent 失敗: {str(e)}")
            return False
    
    def get_user_agent(self) -> Optional[str]:
        """
        獲取一個可用 User-Agent
        
        Returns:
            User-Agent 字符串
        """
        try:
            if self._user_agent_queue.empty():
                self.logger.warning("User-Agent 隊列為空")
                return None
            
            # 從隊列獲取 User-Agent
            ua_key = self._user_agent_queue.get()
            ua_config = self.user_agent_pool.get(ua_key)
            
            if not ua_config:
                self.logger.warning(f"User-Agent 不存在: {ua_key}")
                return None
            
            # 更新使用統計
            ua_config.last_used = int(time.time())
            ua_config.use_count += 1
            
            # 將 User-Agent 放回隊列
            self._user_agent_queue.put(ua_key)
            
            # 生成 User-Agent 字符串
            return self._generate_user_agent(ua_config)
            
        except Exception as e:
            self.logger.error(f"獲取 User-Agent 失敗: {str(e)}")
            return None
    
    def _init_user_agent_queue(self):
        """初始化 User-Agent 隊列"""
        try:
            # 清空隊列
            while not self._user_agent_queue.empty():
                self._user_agent_queue.get()
            
            # 添加所有 User-Agent
            for ua_key in self.user_agent_pool.keys():
                self._user_agent_queue.put(ua_key)
            
            self.logger.info(f"User-Agent 隊列初始化完成，共 {self._user_agent_queue.qsize()} 個 User-Agent")
            
        except Exception as e:
            self.logger.error(f"初始化 User-Agent 隊列失敗: {str(e)}")
    
    def _update_user_agent_queue(self):
        """更新 User-Agent 隊列"""
        try:
            # 重新初始化隊列
            self._init_user_agent_queue()
            
        except Exception as e:
            self.logger.error(f"更新 User-Agent 隊列失敗: {str(e)}")
    
    def _generate_ua_key(self, ua_config: UserAgentConfig) -> str:
        """
        生成 User-Agent 鍵值
        
        Args:
            ua_config: User-Agent 配置
            
        Returns:
            User-Agent 鍵值
        """
        return f"{ua_config.browser}_{ua_config.version}_{ua_config.platform}_{ua_config.device}"
    
    def _generate_user_agent(self, ua_config: UserAgentConfig) -> str:
        """
        生成 User-Agent 字符串
        
        Args:
            ua_config: User-Agent 配置
            
        Returns:
            User-Agent 字符串
        """
        try:
            if ua_config.browser == "chrome":
                return self._generate_chrome_ua(ua_config)
            elif ua_config.browser == "firefox":
                return self._generate_firefox_ua(ua_config)
            elif ua_config.browser == "safari":
                return self._generate_safari_ua(ua_config)
            elif ua_config.browser == "edge":
                return self._generate_edge_ua(ua_config)
            else:
                self.logger.warning(f"不支持的瀏覽器類型: {ua_config.browser}")
                return None
                
        except Exception as e:
            self.logger.error(f"生成 User-Agent 失敗: {str(e)}")
            return None
    
    def _generate_chrome_ua(self, ua_config: UserAgentConfig) -> str:
        """
        生成 Chrome User-Agent
        
        Args:
            ua_config: User-Agent 配置
            
        Returns:
            Chrome User-Agent 字符串
        """
        try:
            # 版本號
            version = ua_config.version if ua_config.version != "latest" else "120.0.0.0"
            
            # 平台信息
            if ua_config.platform == "windows":
                platform = "Windows NT 10.0; Win64; x64"
            elif ua_config.platform == "mac":
                platform = "Macintosh; Intel Mac OS X 10_15_7"
            elif ua_config.platform == "linux":
                platform = "X11; Linux x86_64"
            else:
                platform = "Windows NT 10.0; Win64; x64"
            
            # 設備信息
            if ua_config.device == "mobile":
                platform = "Linux; Android 13; SM-S918B"
                device = "Mobile"
            elif ua_config.device == "tablet":
                platform = "Linux; Android 13; SM-X800"
                device = "Tablet"
            else:
                device = ""
            
            # 語言
            language = ua_config.language
            
            # 構建 User-Agent
            ua = f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
            
            if device:
                ua = ua.replace("Chrome", f"Chrome {device}")
            
            return ua
            
        except Exception as e:
            self.logger.error(f"生成 Chrome User-Agent 失敗: {str(e)}")
            return None
    
    def _generate_firefox_ua(self, ua_config: UserAgentConfig) -> str:
        """
        生成 Firefox User-Agent
        
        Args:
            ua_config: User-Agent 配置
            
        Returns:
            Firefox User-Agent 字符串
        """
        try:
            # 版本號
            version = ua_config.version if ua_config.version != "latest" else "120.0"
            
            # 平台信息
            if ua_config.platform == "windows":
                platform = "Windows NT 10.0; Win64; x64"
            elif ua_config.platform == "mac":
                platform = "Macintosh; Intel Mac OS X 10.15"
            elif ua_config.platform == "linux":
                platform = "X11; Linux i686"
            else:
                platform = "Windows NT 10.0; Win64; x64"
            
            # 設備信息
            if ua_config.device == "mobile":
                platform = "Android"
                device = "Mobile"
            elif ua_config.device == "tablet":
                platform = "Android"
                device = "Tablet"
            else:
                device = ""
            
            # 語言
            language = ua_config.language
            
            # 構建 User-Agent
            ua = f"Mozilla/5.0 ({platform}; rv:{version}) Gecko/20100101 Firefox/{version}"
            
            if device:
                ua = ua.replace("Firefox", f"Firefox {device}")
            
            return ua
            
        except Exception as e:
            self.logger.error(f"生成 Firefox User-Agent 失敗: {str(e)}")
            return None
    
    def _generate_safari_ua(self, ua_config: UserAgentConfig) -> str:
        """
        生成 Safari User-Agent
        
        Args:
            ua_config: User-Agent 配置
            
        Returns:
            Safari User-Agent 字符串
        """
        try:
            # 版本號
            version = ua_config.version if ua_config.version != "latest" else "17.0"
            
            # 平台信息
            if ua_config.platform == "mac":
                platform = "Macintosh; Intel Mac OS X 10_15_7"
            elif ua_config.platform == "ios":
                platform = "iPhone; CPU iPhone OS 17_0 like Mac OS X"
            else:
                platform = "Macintosh; Intel Mac OS X 10_15_7"
            
            # 設備信息
            if ua_config.device == "mobile":
                platform = "iPhone; CPU iPhone OS 17_0 like Mac OS X"
                device = "Mobile"
            elif ua_config.device == "tablet":
                platform = "iPad; CPU OS 17_0 like Mac OS X"
                device = "Tablet"
            else:
                device = ""
            
            # 語言
            language = ua_config.language
            
            # 構建 User-Agent
            ua = f"Mozilla/5.0 ({platform}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15"
            
            if device:
                ua = ua.replace("Safari", f"Safari {device}")
            
            return ua
            
        except Exception as e:
            self.logger.error(f"生成 Safari User-Agent 失敗: {str(e)}")
            return None
    
    def _generate_edge_ua(self, ua_config: UserAgentConfig) -> str:
        """
        生成 Edge User-Agent
        
        Args:
            ua_config: User-Agent 配置
            
        Returns:
            Edge User-Agent 字符串
        """
        try:
            # 版本號
            version = ua_config.version if ua_config.version != "latest" else "120.0.0.0"
            
            # 平台信息
            if ua_config.platform == "windows":
                platform = "Windows NT 10.0; Win64; x64"
            elif ua_config.platform == "mac":
                platform = "Macintosh; Intel Mac OS X 10_15_7"
            elif ua_config.platform == "linux":
                platform = "X11; Linux x86_64"
            else:
                platform = "Windows NT 10.0; Win64; x64"
            
            # 設備信息
            if ua_config.device == "mobile":
                platform = "Linux; Android 13; SM-S918B"
                device = "Mobile"
            elif ua_config.device == "tablet":
                platform = "Linux; Android 13; SM-X800"
                device = "Tablet"
            else:
                device = ""
            
            # 語言
            language = ua_config.language
            
            # 構建 User-Agent
            ua = f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36 Edg/{version}"
            
            if device:
                ua = ua.replace("Edg", f"Edg {device}")
            
            return ua
            
        except Exception as e:
            self.logger.error(f"生成 Edge User-Agent 失敗: {str(e)}")
            return None
    
    def update_user_agent_stats(self, ua_key: str, success: bool):
        """
        更新 User-Agent 統計信息
        
        Args:
            ua_key: User-Agent 鍵值
            success: 是否成功
        """
        try:
            ua_config = self.user_agent_pool.get(ua_key)
            if not ua_config:
                self.logger.warning(f"User-Agent 不存在: {ua_key}")
                return
            
            if success:
                ua_config.success_count += 1
            else:
                ua_config.fail_count += 1
            
            # 保存配置
            self._save_config()
            
        except Exception as e:
            self.logger.error(f"更新 User-Agent 統計信息失敗: {str(e)}")
    
    def get_user_agent_stats(self) -> List[Dict]:
        """
        獲取 User-Agent 統計信息
        
        Returns:
            User-Agent 統計信息列表
        """
        try:
            stats = []
            for ua_key, ua_config in self.user_agent_pool.items():
                stats.append({
                    "user_agent": ua_key,
                    "success_rate": ua_config.success_rate,
                    "use_count": ua_config.use_count,
                    "last_used": datetime.fromtimestamp(ua_config.last_used).isoformat()
                })
            return stats
            
        except Exception as e:
            self.logger.error(f"獲取 User-Agent 統計信息失敗: {str(e)}")
            return []
    
    def cleanup(self):
        """清理資源"""
        try:
            # 保存配置
            self._save_config()
            
            self.logger.info("User-Agent 管理器清理完成")
            
        except Exception as e:
            self.logger.error(f"User-Agent 管理器清理失敗: {str(e)}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup() 